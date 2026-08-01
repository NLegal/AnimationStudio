"""MockBackend — deterministic placeholder generation backend.

Produces solid-color (or simple gradient) test images so the full pipeline
(prompt → generate → score → diversity filter → save) can run without a
GPU, ComfyUI server, or cloud API key.  Used by the batch generator and the
Review UI's default "mock" backend option.
"""

import hashlib

from PIL import Image, ImageDraw

from .base import GenerationBackend, GenerationInput, GenerationOutput


class MockBackend(GenerationBackend):
    """Generation backend that returns deterministic placeholder images.

    The colour is derived from the seed and prompt so re-running a job with
    the same seeds reproduces the same output (useful for regression tests).

    Usage:
        backend = MockBackend()
        out = backend.generate(GenerationInput(prompt="a cat", seed=42))
        assert out.images
    """

    def __init__(self, base_size: int = 512, draw_pattern: bool = True):
        self.base_size = base_size
        self.draw_pattern = draw_pattern

    def load_model(self, model_path: str = "") -> None:
        """No model to load — this backend is a placeholder."""

    def generate(self, input: GenerationInput) -> GenerationOutput:
        """Generate one placeholder image per requested output."""
        images = []
        for offset in range(max(1, input.num_images)):
            seed = (input.seed + offset) % (2**31)
            colour = self._seed_to_color(seed, input.prompt)
            img = Image.new("RGB", (input.width, input.height), colour)
            if self.draw_pattern:
                self._draw_label(img, seed, input.prompt)
            images.append(img)

        return GenerationOutput(
            images=images,
            seed=input.seed,
            metadata={
                "backend": "mock",
                "model": "MockBackend",
                "num_images": len(images),
            },
        )

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    def _seed_to_color(self, seed: int, prompt: str) -> tuple[int, int, int]:
        """Derive a stable RGB colour from seed + prompt hash."""
        digest = hashlib.sha256(f"{seed}:{prompt}".encode()).hexdigest()
        return tuple(int(digest[i:i + 2], 16) for i in (0, 2, 4))

    def _draw_label(self, img: Image.Image, seed: int, prompt: str) -> None:
        """Draw a small seed marker in the corner for visual distinction."""
        draw = ImageDraw.Draw(img)
        label = f"mock:{seed}"
        x = max(img.width - 90, 0)
        draw.rectangle([x, img.height - 20, img.width, img.height], fill=(0, 0, 0))
        draw.text((x + 6, img.height - 16), label, fill=(255, 255, 255))
