"""Tests for Training Engine — TrainingBackend ABC, TrainingConfig, TrainingResult,
and KohyaAdapter implementation.

Tests cover interface compliance, config defaults, environment validation,
dataset preparation, and command generation (Flux vs SDXL).
"""

import os
import sys
from pathlib import Path
from datetime import datetime

import pytest

from src.training_engine import TrainingBackend, TrainingConfig, TrainingResult, KohyaAdapter


# ---------------------------------------------------------------------------
# TrainingConfig tests
# ---------------------------------------------------------------------------

class TestTrainingConfig:
    """TrainingConfig dataclass defaults and structure."""

    def test_config_defaults(self):
        """Default field values are set correctly."""
        config = TrainingConfig(
            character_id="lily-bunny",
            dataset_path=Path("/tmp/dataset"),
            output_path=Path("/tmp/output"),
        )
        assert config.character_id == "lily-bunny"
        assert config.base_model == "black-forest-labs/FLUX.1-dev"
        assert config.learning_rate == 1e-4
        assert config.num_epochs == 10
        assert config.batch_size == 4
        assert config.resolution == 1024
        assert config.lora_rank == 64
        assert config.lora_alpha == 128
        assert config.optimizer_type == "AdamW8bit"
        assert config.scheduler == "cosine_with_restarts"
        assert config.mixed_precision == "bf16"
        assert config.seed == 42
        assert config.version == "v0.1"

    def test_config_custom_values(self):
        """Custom field values override defaults."""
        config = TrainingConfig(
            character_id="ben-bunny",
            dataset_path=Path("/custom/dataset"),
            output_path=Path("/custom/output"),
            base_model="stabilityai/stable-diffusion-xl-base-1.0",
            learning_rate=5e-5,
            num_epochs=20,
            lora_rank=128,
            version="v0.5",
        )
        assert config.base_model == "stabilityai/stable-diffusion-xl-base-1.0"
        assert config.learning_rate == 5e-5
        assert config.num_epochs == 20
        assert config.lora_rank == 128
        assert config.version == "v0.5"


# ---------------------------------------------------------------------------
# TrainingResult tests
# ---------------------------------------------------------------------------

class TestTrainingResult:
    """TrainingResult dataclass structure."""

    def test_result_structure(self):
        """TrainingResult has expected fields and defaults."""
        result = TrainingResult(
            lora_path=Path("/tmp/lily-v0.1.safetensors"),
            version="v0.1",
            metrics={"train_loss": 0.05, "epochs_completed": 10},
        )
        assert result.lora_path == Path("/tmp/lily-v0.1.safetensors")
        assert result.version == "v0.1"
        assert result.metrics["train_loss"] == 0.05
        assert result.success is True
        assert isinstance(result.trained_at, datetime)

    def test_result_failure(self):
        """TrainingResult can represent a failed training."""
        result = TrainingResult(
            lora_path=Path(),
            version="v0.1",
            metrics={"error": "Environment not ready"},
            success=False,
        )
        assert result.success is False


# ---------------------------------------------------------------------------
# TrainingBackend ABC tests
# ---------------------------------------------------------------------------

class TestTrainingBackendABC:
    """TrainingBackend ABC cannot be instantiated directly."""

    def test_abstract_class_cannot_instantiate(self):
        """TrainingBackend ABC raises TypeError when instantiated."""
        with pytest.raises(TypeError):
            TrainingBackend()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# KohyaAdapter tests
# ---------------------------------------------------------------------------

class TestKohyaAdapterInterface:
    """KohyaAdapter conforms to the TrainingBackend ABC."""

    def test_adapter_is_training_backend(self):
        """KohyaAdapter is a TrainingBackend."""
        from src.training_engine.kohya_adapter import KohyaAdapter as Ka
        assert issubclass(Ka, TrainingBackend)

    def test_adapter_can_instantiate(self):
        """KohyaAdapter can be instantiated."""
        adapter = KohyaAdapter()
        assert isinstance(adapter, TrainingBackend)


class TestKohyaEnvironmentValidation:
    """validate_environment behavior."""

    def test_validate_not_ready_when_path_missing(self):
        """validate_environment returns False when KOHYA_SS_PATH is missing."""
        adapter = KohyaAdapter(kohya_path="")
        result = adapter.validate_environment()
        assert result is False

    def test_validate_not_ready_when_path_does_not_exist(self, tmp_path):
        """validate_environment returns False when KOHYA_SS_PATH doesn't exist."""
        fake_path = str(tmp_path / "nonexistent")
        adapter = KohyaAdapter(kohya_path=fake_path)
        result = adapter.validate_environment()
        assert result is False


class TestKohyaDatasetPreparation:
    """prepare_dataset behavior."""

    def test_prepare_dataset_creates_directory(self, tmp_path):
        """prepare_dataset creates output directory structure."""
        adapter = KohyaAdapter(kohya_path="/tmp/fake_kohya")
        image_paths = [
            tmp_path / "img1.png",
            tmp_path / "img2.png",
        ]
        # Create dummy images
        for p in image_paths:
            p.write_text("dummy-image-data")

        output_dir = tmp_path / "training_data"
        result_path = adapter.prepare_dataset(image_paths, output_dir)

        assert output_dir.exists()
        assert result_path == output_dir

    def test_empty_dataset_path(self, tmp_path):
        """Empty image list creates empty output directory (no crash)."""
        adapter = KohyaAdapter(kohya_path="/tmp/fake_kohya")
        output_dir = tmp_path / "empty_training"
        result_path = adapter.prepare_dataset([], output_dir)
        assert output_dir.exists()
        assert result_path == output_dir


class TestKohyaCommandGeneration:
    """Command-line generation for Flux and SDXL."""

    def test_adapter_flux_vs_sdxl_command(self, tmp_path):
        """KohyaAdapter generates different training script paths for Flux vs SDXL."""
        from src.training_engine.kohya_adapter import KohyaAdapter as Ka

        kohya_path = str(tmp_path / "kohya_ss")
        (tmp_path / "kohya_ss" / "sd-scripts").mkdir(parents=True, exist_ok=True)

        # Flux config
        flux_config = TrainingConfig(
            character_id="lily-bunny",
            dataset_path=tmp_path / "dataset",
            output_path=tmp_path / "output",
            base_model="black-forest-labs/FLUX.1-dev",
        )

        # SDXL config
        sdxl_config = TrainingConfig(
            character_id="lily-bunny",
            dataset_path=tmp_path / "dataset",
            output_path=tmp_path / "output",
            base_model="stabilityai/stable-diffusion-xl-base-1.0",
        )

        adapter = Ka(kohya_path=kohya_path)
        flux_cmd = adapter._build_command(flux_config)
        sdxl_cmd = adapter._build_command(sdxl_config)

        # Find the training script argument (index 2 after [sys.executable, script_path])
        flux_script = [a for a in flux_cmd if "flux_train_network" in a]
        sdxl_script = [a for a in sdxl_cmd if "sdxl_train_network" in a]

        assert len(flux_script) >= 1, "Flux config should reference flux_train_network.py"
        assert len(sdxl_script) >= 1, "SDXL config should reference sdxl_train_network.py"

    def test_command_has_expected_args(self, tmp_path):
        """Generated command contains expected arguments."""
        from src.training_engine.kohya_adapter import KohyaAdapter as Ka

        kohya_path = str(tmp_path / "kohya_ss")
        (tmp_path / "kohya_ss" / "sd-scripts").mkdir(parents=True, exist_ok=True)

        config = TrainingConfig(
            character_id="lily-bunny",
            dataset_path=tmp_path / "dataset",
            output_path=tmp_path / "output",
            learning_rate=1e-4,
            num_epochs=10,
            batch_size=4,
            lora_rank=64,
            lora_alpha=128,
            seed=42,
        )

        adapter = Ka(kohya_path=kohya_path)
        cmd = adapter._build_command(config)

        cmd_str = " ".join(cmd)
        assert "--learning_rate" in cmd_str
        assert "--train_batch_size" in cmd_str
        assert "--max_train_epochs" in cmd_str
        assert "--network_module" in cmd_str
        assert "--network_dim" in cmd_str
        assert "--network_alpha" in cmd_str
        assert "--seed" in cmd_str
        assert "lily-bunny_v0.1" in cmd_str


class TestTrainingIntegration:
    """Full training flow integration (no GPU, validates path construction)."""

    def test_train_returns_error_when_env_not_ready(self):
        """train() returns failure TrainingResult when env not ready."""
        adapter = KohyaAdapter(kohya_path="")
        config = TrainingConfig(
            character_id="test",
            dataset_path=Path("/tmp/test"),
            output_path=Path("/tmp/test_out"),
        )
        result = adapter.train(config)
        assert result.success is False
        assert "error" in result.metrics
