"""PonyBackend — GenerationBackend adapter for Pony Diffusion.

An SDXL-based model with pony-specific quality score tags prepended
to the positive prompt per community conventions.
"""

import logging
from typing import Optional

from .base import GenerationBackend, GenerationInput, GenerationOutput, ModelLoadError

logger = logging.getLogger(__name__)

# PonyDiffusion quality score prefix prepended to positive prompts
# per community convention for quality filtering.
PONY_SCORE_TAG = "score_9, score_8_up, score_7_up "


class PonyBackend(GenerationBackend):
    """Generation backend using Pony Diffusion (SDXL-based).

    Pony Diffusion is an SDXL fine-tune that uses score tags for
    community-defined quality filtering. The score tag is prepended
    to the positive prompt automatically.
    """

    def __init__(self, model_id: str = "AstraliteHeart/pony-diffusion-v6-xl"):
        self.model_id = model_id
        self._pipe: Optional[object] = None

    def load_model(self, model_path: str = "") -> None:
        """Load or switch the Pony Diffusion pipeline model.

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
            logger.info("Loading Pony Diffusion model: %s", target)
            self._pipe = StableDiffusionXLPipeline.from_pretrained(
                target,
                torch_dtype=torch.float16,
            )
            self._pipe.enable_model_cpu_offload()
            logger.info("Pony Diffusion model loaded: %s", target)
        except ImportError as exc:
            raise ModelLoadError(
                f"diffusers not installed — cannot load PonyBackend: {exc}"
            ) from exc
        except Exception as exc:
            raise ModelLoadError(
                f"Failed to load Pony model '{model_path or self.model_id}': {exc}"
            ) from exc

    def generate(self, input: GenerationInput) -> GenerationOutput:
        """Generate images using Pony Diffusion with score tag prefix.

        Prepends pony-specific quality score tags to the positive prompt
        per PonyDiffusion community conventions.

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
                    "backend": "PonyBackend",
                    "model_id": self.model_id,
                },
            )

        try:
            import torch

            # Prepend pony quality score tag to positive prompt
            pony_prompt = PONY_SCORE_TAG + input.prompt

            generator = torch.Generator("cpu").manual_seed(input.seed)
            images = self._pipe(
                prompt=pony_prompt,
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
                    "backend": "PonyBackend",
                    "model_id": self.model_id,
                    "num_images": len(images),
                    "prompt_score_tag": PONY_SCORE_TAG.strip(),
                },
            )
        except Exception as exc:
            logger.warning("PonyBackend generation failed: %s", exc)
            return GenerationOutput(
                images=[],
                seed=input.seed,
                metadata={
                    "error": str(exc),
                    "backend": "PonyBackend",
                    "model_id": self.model_id,
                },
            )
