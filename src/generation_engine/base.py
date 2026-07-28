"""Generation Engine — abstract base class for pluggable model backends.

Defines the adapter interface (D-09) that all concrete generation backends
must implement (Flux, SDXL, Pony, CloudAPI, ComfyUI).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from PIL import Image


@dataclass
class GenerationInput:
    """Input contract for image generation."""

    prompt: str
    negative_prompt: str = ""
    seed: int = 42
    width: int = 1024
    height: int = 1024
    num_images: int = 1


@dataclass
class GenerationOutput:
    """Output contract for image generation."""

    images: list[Image.Image] = field(default_factory=list)
    seed: int = 0
    metadata: dict = field(default_factory=dict)


class GenerationBackend(ABC):
    """Abstract base class for all generation backends."""

    @abstractmethod
    def load_model(self, model_path: str) -> None:
        """Load a model checkpoint or LoRA weights."""
        ...

    @abstractmethod
    def generate(self, input: GenerationInput) -> GenerationOutput:
        """Run inference and return generated images."""
        ...
