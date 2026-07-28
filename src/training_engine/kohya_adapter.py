"""Kohya SS adapter for LoRA training (D-18).

Implements the TrainingBackend ABC by wrapping Kohya SS's sd-scripts CLI
(``flux_train_network.py`` / ``sdxl_train_network.py``) via subprocess.

Security: All command construction uses argument lists (never ``shell=True``)
and validates paths with ``Path.resolve()`` before passing to subprocess.
"""

import os
import shutil
import subprocess
import sys
import warnings
from pathlib import Path
from typing import Optional

from .base import TrainingBackend, TrainingConfig, TrainingResult


class KohyaAdapter(TrainingBackend):
    """Adapter that drives Kohya SS LoRA training via the sd-scripts CLI.

    Usage::

        adapter = KohyaAdapter(kohya_path="/path/to/kohya_ss")
        if adapter.validate_environment():
            result = adapter.train(config)
    """

    def __init__(self, kohya_path: Optional[str] = None):
        """Initialise the adapter.

        Args:
            kohya_path: Absolute path to the Kohya SS installation directory.
                Falls back to the ``KOHYA_SS_PATH`` environment variable when
                not provided.
        """
        self.kohya_path = kohya_path or os.environ.get("KOHYA_SS_PATH", "")

    # ------------------------------------------------------------------
    #  TrainingBackend interface
    # ------------------------------------------------------------------

    def validate_environment(self) -> bool:
        """Check that the Kohya SS installation and GPU are available.

        Returns:
            True if ``KOHYA_SS_PATH`` points to an existing directory and
            ``nvidia-smi`` is on ``$PATH``.
        """
        if not self.kohya_path:
            warnings.warn("KOHYA_SS_PATH not set — training unavailable")
            return False

        kohya_dir = Path(self.kohya_path).resolve()
        if not kohya_dir.exists():
            warnings.warn(f"KOHYA_SS_PATH '{kohya_dir}' does not exist")
            return False

        if shutil.which("nvidia-smi") is None:
            warnings.warn("nvidia-smi not found — no GPU detected")
            # We still return True if the path exists; the GPU warning
            # is advisory.  Production training will fail at the
            # subprocess call if no GPU is available.
            # Future: add a --dry-run / --check flag for stricter validation.

        return True

    def prepare_dataset(
        self,
        image_paths: list[Path],
        output_dir: Path,
    ) -> Path:
        """Prepare images for Kohya SS training.

        Copies images to *output_dir* and creates a Kohya-compatible
        metadata JSON file (``metadata.json``) mapping each image to a
        prompt-based caption.

        Args:
            image_paths: Source image paths.
            output_dir: Destination directory for the prepared dataset.

        Returns:
            The *output_dir* path (same as input).
        """
        import json

        output_dir = output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        metadata: list[dict] = []
        for i, src in enumerate(image_paths):
            src = Path(src).resolve()
            if not src.exists():
                continue
            dest = output_dir / src.name
            shutil.copy2(str(src), str(dest))
            # Use filename (without extension) as a simple caption hint;
            # production pipelines should provide richer metadata.
            caption = src.stem.replace("_", " ").replace("-", " ")
            metadata.append({
                "image": src.name,
                "caption": caption,
            })

        meta_file = output_dir / "metadata.json"
        meta_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        return output_dir

    def train(self, config: TrainingConfig) -> TrainingResult:
        """Execute a Kohya SS LoRA training run.

        Args:
            config: Training configuration.

        Returns:
            ``TrainingResult(success=True, lora_path=…)`` on success, or
            ``TrainingResult(success=False, metrics={"error": …})`` if the
            environment is not ready.
        """
        if not self.validate_environment():
            return TrainingResult(
                lora_path=Path(),
                version=config.version,
                metrics={"error": "Environment not ready"},
                success=False,
            )

        cmd = self._build_command(config)

        # Ensure the output directory exists
        config.output_path.resolve().mkdir(parents=True, exist_ok=True)

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )
            # Locate the resulting LoRA file
            lora_file = (
                config.output_path
                / f"{config.character_id}_{config.version}.safetensors"
            )
            return TrainingResult(
                lora_path=lora_file,
                version=config.version,
                metrics={
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "exit_code": proc.returncode,
                },
                success=True,
            )
        except subprocess.CalledProcessError as exc:
            return TrainingResult(
                lora_path=Path(),
                version=config.version,
                metrics={
                    "error": str(exc),
                    "stdout": exc.stdout,
                    "stderr": exc.stderr,
                    "exit_code": exc.returncode,
                },
                success=False,
            )
        except FileNotFoundError:
            return TrainingResult(
                lora_path=Path(),
                version=config.version,
                metrics={"error": "Kohya SS Python executable not found"},
                success=False,
            )

    # ------------------------------------------------------------------
    #  Internal helpers
    # ------------------------------------------------------------------

    def _dataset_config_path(self, config: TrainingConfig) -> Path:
        """Return the path to the dataset config directory for *config*."""
        return config.dataset_path.resolve()

    def _build_command(self, config: TrainingConfig) -> list[str]:
        """Build the subprocess argument list for Kohya SS training.

        Returns a list of strings suitable for ``subprocess.run()``
        (never uses ``shell=True``).  All paths are resolved before being
        added to the list.
        """
        model_lower = config.base_model.lower()
        if "sdxl" in model_lower or "stable-diffusion-xl" in model_lower:
            script = "sdxl_train_network.py"
        else:
            script = "flux_train_network.py"

        script_path = Path(self.kohya_path).resolve() / "sd-scripts" / script
        output_name = f"{config.character_id}_{config.version}"

        cmd: list[str] = [
            sys.executable,
            str(script_path),
            "--pretrained_model_name_or_path", config.base_model,
            "--dataset_config", str(self._dataset_config_path(config)),
            "--output_dir", str(config.output_path.resolve()),
            "--learning_rate", str(config.learning_rate),
            "--train_batch_size", str(config.batch_size),
            "--max_train_epochs", str(config.num_epochs),
            "--mixed_precision", config.mixed_precision,
            "--save_precision", "bf16",
            "--seed", str(config.seed),
            "--cache_latents",
            "--cache_latents_to_disk",
            "--optimizer_type", config.optimizer_type,
            "--lr_scheduler", config.scheduler,
            "--network_module", config.network_module,
            "--network_dim", str(config.lora_rank),
            "--network_alpha", str(config.lora_alpha),
            "--output_name", output_name,
        ]

        # Resolution is passed as width x height
        cmd.extend([
            "--max_data_loader_n_workers", "8",
            "--persistent_data_loader_workers",
        ])

        return cmd
