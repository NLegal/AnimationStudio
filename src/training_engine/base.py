"""Training Engine abstraction per D-18.

Defines the TrainingBackend abstract base class that all LoRA training
adapters must implement, plus the TrainingConfig and TrainingResult
dataclasses that form the contract between the engine and its adapters.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# TrainingConfig
# ---------------------------------------------------------------------------

@dataclass
class TrainingConfig:
    """All parameters needed to configure a single LoRA training run.

    Defaults are tuned for Flux LoRA training (1024px, rank 64, BF16
    mixed precision).  Override per-character or per-model as needed.
    """

    character_id: str
    dataset_path: Path
    output_path: Path
    base_model: str = "black-forest-labs/FLUX.1-dev"
    learning_rate: float = 1e-4
    num_epochs: int = 10
    batch_size: int = 4
    resolution: int = 1024
    lora_rank: int = 64
    lora_alpha: int = 128
    network_module: str = "networks.lora"
    optimizer_type: str = "AdamW8bit"
    scheduler: str = "cosine_with_restarts"
    seed: int = 42
    mixed_precision: str = "bf16"
    cache_latents: bool = True
    caption_dropout_rate: float = 0.05
    version: str = "v0.1"
    dry_run: bool = False


# ---------------------------------------------------------------------------
# TrainingResult
# ---------------------------------------------------------------------------

@dataclass
class TrainingResult:
    """The outcome of a single training run."""

    lora_path: Path
    version: str
    metrics: dict  # benchmark scores, training loss, epochs completed
    trained_at: datetime = field(default_factory=datetime.now)
    success: bool = True


# ---------------------------------------------------------------------------
# TrainingBackend ABC
# ---------------------------------------------------------------------------

class TrainingBackend(ABC):
    """Abstract base for LoRA training adapters.

    Every concrete training backend (Kohya SS, AI-Toolkit, cloud API, …)
    implements this interface so orchestration code never depends on a
    specific training tool.
    """

    @abstractmethod
    def train(self, config: TrainingConfig) -> TrainingResult:
        """Execute LoRA training and return the path to the trained model.

        Args:
            config: Fully populated training configuration.

        Returns:
            A TrainingResult indicating success/failure and the output path.
        """
        ...

    @abstractmethod
    def validate_environment(self) -> bool:
        """Check whether the training environment is ready.

        Returns:
            True if all prerequisites (GPU, tool installation, environment
            variables) are satisfied, False otherwise.
        """
        ...

    @abstractmethod
    def prepare_dataset(
        self,
        image_paths: list[Path],
        output_dir: Path,
    ) -> Path:
        """Prepare images and captions for training.

        Args:
            image_paths: List of paths to source images.
            output_dir: Directory to write prepared dataset into.

        Returns:
            Path to the prepared dataset configuration (directory or JSON).
        """
        ...
