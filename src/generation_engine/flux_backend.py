"""FluxBackend — GenerationBackend adapter for Black Forest Labs FLUX.1.

Uses diffusers FluxPipeline for production image generation (D-08).
Supports lazy model loading, CPU offloading, and graceful error handling
so the pipeline never crashes on model load failures.
"""

import logging
from typing import Optional

from .base import GenerationBackend, GenerationInput, GenerationOutput, ModelLoadError

logger = logging.getLogger(__name__)


class FluxBackend(GenerationBackend):
    """Generation backend using diffusers FluxPipeline (FLUX.1-dev).

    Production adapter for the Black Forest Labs FLUX.1 model family.
    Uses bfloat16 precision and model CPU offloading for memory efficiency.
    """

    def __init__(self, model_id: str = "black-forest-labs/FLUX.1-dev"):
        self.model_id = model_id
        self._pipe: Optional[object] = None

    def load_model(self, model_path: str = "") -> None:
        """Load or switch the FluxPipeline model.

        Args:
            model_path: Optional path to a local checkpoint or LoRA.
                        If empty, loads the default model_id from __init__.

        Raises:
            ModelLoadError: If model loading fails for any reason.
        """
        try:
            from diffusers import FluxPipeline
            import torch

            target = model_path or self.model_id
            logger.info("Loading FluxPipeline model: %s", target)
            self._pipe = FluxPipeline.from_pretrained(
                target,
                torch_dtype=torch.bfloat16,
            )
            self._pipe.enable_model_cpu_offload()
            logger.info("FluxPipeline model loaded: %s", target)
        except ImportError as exc:
            raise ModelLoadError(
                f"diffusers not installed — cannot load FluxBackend: {exc}"
            ) from exc
        except Exception as exc:
            raise ModelLoadError(
                f"Failed to load FluxPipeline model '{model_path or self.model_id}': {exc}"
            ) from exc

    def generate(self, input: GenerationInput) -> GenerationOutput:
        """Generate images using the FluxPipeline.

        Args:
            input: GenerationInput with prompt, seed, dimensions, etc.

        Returns:
            GenerationOutput with generated images (empty list on failure
            with error metadata — never crashes).
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
                    "backend": "FluxBackend",
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
                guidance_scale=3.5,
                num_inference_steps=50,
                max_sequence_length=512,
                generator=generator,
                num_images_per_prompt=input.num_images,
            ).images

            return GenerationOutput(
                images=images,
                seed=input.seed,
                metadata={
                    "backend": "FluxBackend",
                    "model_id": self.model_id,
                    "num_images": len(images),
                },
            )
        except Exception as exc:
            logger.warning("FluxBackend generation failed: %s", exc)
            return GenerationOutput(
                images=[],
                seed=input.seed,
                metadata={
                    "error": str(exc),
                    "backend": "FluxBackend",
                    "model_id": self.model_id,
                },
            )
