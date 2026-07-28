"""SDXLBackend — GenerationBackend adapter for Stable Diffusion XL.

Uses diffusers StableDiffusionXLPipeline for production image generation.
Supports lazy model loading, CPU offloading, and graceful error handling.
"""

import logging
from typing import Optional

from .base import GenerationBackend, GenerationInput, GenerationOutput, ModelLoadError

logger = logging.getLogger(__name__)


class SDXLBackend(GenerationBackend):
    """Generation backend using diffusers StableDiffusionXLPipeline.

    Production adapter for Stability AI's SDXL base model.
    Uses float16 precision and model CPU offloading for memory efficiency.
    """

    def __init__(self, model_id: str = "stabilityai/stable-diffusion-xl-base-1.0"):
        self.model_id = model_id
        self._pipe: Optional[object] = None

    def load_model(self, model_path: str = "") -> None:
        """Load or switch the SDXL pipeline model.

        Args:
            model_path: Optional path to a local checkpoint.
                        If empty, loads the default model_id.

        Raises:
            ModelLoadError: If model loading fails.
        """
        try:
            from diffusers import StableDiffusionXLPipeline
            import torch

            target = model_path or self.model_id
            logger.info("Loading SDXL pipeline model: %s", target)
            self._pipe = StableDiffusionXLPipeline.from_pretrained(
                target,
                torch_dtype=torch.float16,
            )
            self._pipe.enable_model_cpu_offload()
            logger.info("SDXL pipeline model loaded: %s", target)
        except ImportError as exc:
            raise ModelLoadError(
                f"diffusers not installed — cannot load SDXLBackend: {exc}"
            ) from exc
        except Exception as exc:
            raise ModelLoadError(
                f"Failed to load SDXL model '{model_path or self.model_id}': {exc}"
            ) from exc

    def generate(self, input: GenerationInput) -> GenerationOutput:
        """Generate images using the SDXL pipeline.

        Args:
            input: GenerationInput with prompt, seed, dimensions, etc.

        Returns:
            GenerationOutput with generated images (empty list on failure).
        """
        try:
            if self._pipe is None:
                self.load_model()
        except ModelLoadError as exc:
            return GenerationOutput(
                images=[],
                seed=input.seed,
                metadata={
                    "error": str(exc),
                    "backend": "SDXLBackend",
                    "model_id": self.model_id,
                },
            )

        try:
            import torch
            generator = torch.Generator("cpu").manual_seed(input.seed)
            images = self._pipe(
                prompt=input.prompt,
                negative_prompt=input.negative_prompt,
                height=input.height,
                width=input.width,
                guidance_scale=7.5,
                num_inference_steps=30,
                generator=generator,
                num_images_per_prompt=input.num_images,
            ).images

            return GenerationOutput(
                images=images,
                seed=input.seed,
                metadata={
                    "backend": "SDXLBackend",
                    "model_id": self.model_id,
                    "num_images": len(images),
                },
            )
        except Exception as exc:
            logger.warning("SDXLBackend generation failed: %s", exc)
            return GenerationOutput(
                images=[],
                seed=input.seed,
                metadata={
                    "error": str(exc),
                    "backend": "SDXLBackend",
                    "model_id": self.model_id,
                },
            )
