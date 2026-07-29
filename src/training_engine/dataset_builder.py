"""LoRA dataset builder — prepares training datasets from approved character assets.

Transforms approved character images into Kohya SS-compatible datasets with
rich captions derived from the original generation prompts, proper image
preprocessing, and train/validation splits.
"""

import json
import shutil
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class DatasetEntry:
    """A single training example with its associated metadata."""

    image_path: Path
    caption: str
    asset_type: str = "expression"
    variant: Optional[str] = None
    brand_score: Optional[float] = None


@dataclass
class DatasetConfig:
    """Configuration for a dataset build operation."""

    output_dir: Path
    resolution: int = 1024
    validation_split: float = 0.1
    repeat_count: int = 1
    shuffle_seed: int = 42
    caption_prefix: str = ""
    caption_suffix: str = ", high quality, detailed, Pixar-style"


@dataclass
class BuildResult:
    """Result of a dataset build operation."""

    output_dir: Path
    num_images: int
    num_val_images: int
    config_file: Path
    metadata_file: Path


class DatasetBuilder:
    """Builds Kohya SS-compatible training datasets from approved assets.

    Usage::

        builder = DatasetBuilder()
        entries = [
            DatasetEntry(
                image_path=Path("/assets/lily-happy-001.png"),
                caption="Lily Bunny, happy expression, portrait, ...",
            ),
        ]
        config = DatasetConfig(output_dir=Path("/training/lily-v1"))
        result = builder.build(entries, config)
    """

    def build(
        self,
        entries: list[DatasetEntry],
        config: DatasetConfig,
    ) -> BuildResult:
        """Build a complete training dataset.

        Args:
            entries: List of dataset entries with images and captions.
            config: Dataset build configuration.

        Returns:
            BuildResult with paths to the prepared dataset.
        """
        output_dir = config.output_dir.resolve()
        train_dir = output_dir / "train"
        val_dir = output_dir / "val"

        train_dir.mkdir(parents=True, exist_ok=True)
        val_dir.mkdir(parents=True, exist_ok=True)

        import random
        random.seed(config.shuffle_seed)
        shuffled = list(entries)
        random.shuffle(shuffled)

        num_val = int(len(shuffled) * config.validation_split)
        if num_val < 1 and config.validation_split > 0:
            num_val = 1
        val_entries = shuffled[:num_val]
        train_entries = shuffled[num_val:]

        train_metadata = self._copy_and_caption(
            train_entries, train_dir, config
        )
        val_metadata = self._copy_and_caption(
            val_entries, val_dir, config
        )

        metadata = {
            "train": train_metadata,
            "val": val_metadata,
        }
        meta_file = output_dir / "metadata.json"
        meta_file.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        config_file = self._write_kohya_config(output_dir, config)

        return BuildResult(
            output_dir=output_dir,
            num_images=len(train_metadata),
            num_val_images=len(val_metadata),
            config_file=config_file,
            metadata_file=meta_file,
        )

    def _copy_and_caption(
        self,
        entries: list[DatasetEntry],
        dest_dir: Path,
        config: DatasetConfig,
    ) -> list[dict]:
        """Copy images and build caption metadata for a split.

        Args:
            entries: Dataset entries to process.
            dest_dir: Destination directory for this split.
            config: Dataset build configuration.

        Returns:
            List of metadata dicts (image, caption pairs) for this split.
        """
        metadata: list[dict] = []
        for i, entry in enumerate(entries):
            src = entry.image_path.resolve()
            if not src.exists():
                warnings.warn(f"Image not found: {src}")
                continue

            dest = dest_dir / f"{i:04d}_{src.stem}{src.suffix}"
            shutil.copy2(str(src), str(dest))

            caption_parts = []
            if config.caption_prefix:
                caption_parts.append(config.caption_prefix)
            caption_parts.append(entry.caption)
            if config.caption_suffix:
                caption_parts.append(config.caption_suffix)

            caption = ", ".join(part for part in caption_parts if part)

            metadata.append({
                "image": dest.name,
                "caption": caption,
                "asset_type": entry.asset_type,
                "original_image": src.name,
            })

        return metadata

    def _write_kohya_config(
        self,
        output_dir: Path,
        config: DatasetConfig,
    ) -> Path:
        """Write a Kohya SS TOML dataset configuration file.

        This config is referenced by the ``--dataset_config`` flag in
        Kohya's training scripts.  It points to the prepared image
        directories and metadata files.

        Args:
            output_dir: Dataset output directory.
            config: Dataset build configuration.

        Returns:
            Path to the written TOML config file.
        """
        config_path = output_dir / "dataset_config.toml"
        lines = [
            "[general]",
            f"resolution = {config.resolution}",
            f"shuffle_caption = true",
            f"keep_tokens = 1",
            "",
            f"[[datasets]]",
            f"batch_size = 4",
            f"caption_metadata_file = \"metadata.json\"",  # noqa: Q003
            "caption_prefix = \"\"",
            "",
            "  [[datasets.subsets]]",
            f"  image_dir = \"train\"",
            f"  num_repeats = {config.repeat_count}",
            "",
            "  [[datasets.subsets]]",
            f"  image_dir = \"val\"",
            f"  num_repeats = 1",
            "",
        ]
        config_path.write_text("\n".join(lines), encoding="utf-8")
        return config_path

    @staticmethod
    def build_entries_from_assets(
        assets: list[dict],
        prompts: Optional[dict[str, str]] = None,
    ) -> list[DatasetEntry]:
        """Build DatasetEntry list from asset repository records.

        Each *asset* dict should contain at minimum:
            - ``file_path`` (str): path to the generated image
            - ``asset_type`` (str): type of asset
            - ``variant`` (str, optional): specific variant name
            - ``brand_score`` (float, optional): identity consistency score
            - ``prompt`` (str, optional): generation prompt used

        The optional *prompts* dict maps ``asset_id → prompt`` so callers
        can supply richer captions than what is stored on the record.

        Args:
            assets: List of asset dicts from the asset repository.
            prompts: Optional mapping of asset ID to full prompt text.

        Returns:
            List of DatasetEntry objects.
        """
        entries: list[DatasetEntry] = []
        for asset in assets:
            image_path = Path(asset.get("file_path", ""))
            if not image_path.exists():
                continue

            prompt = asset.get("prompt", "")
            if prompts and asset.get("id") in prompts:
                prompt = prompts[asset["id"]]

            if not prompt:
                prompt = asset.get("variant", asset.get("asset_type", "character"))

            entries.append(DatasetEntry(
                image_path=image_path,
                caption=prompt,
                asset_type=asset.get("asset_type", ""),
                variant=asset.get("variant"),
                brand_score=asset.get("brand_score"),
            ))

        return entries
