"""CLIP scoring plugin — image-text semantic alignment.

Weight: 20% (D-06)
Uses openai/clip-vit-base-patch16 via transformers.
Lazy-loads model on first use; falls back to 0.0 on load failure.
"""

import warnings
from typing import Optional

from PIL import Image


class CLIPScoringPlugin:
    """CLIP-based prompt-image alignment scoring.

    Evaluates how well an image matches a text prompt.
    Requires the ``prompt`` kwarg; returns 0.0 if absent.
    """

    name: str = "prompt_accuracy"
    weight: float = 0.20

    def __init__(self, weight: float = 0.20, device: str = "cpu"):
        self.weight = weight
        self.device = device
        self._model = None
        self._processor = None

    def _load_model(self):
        """Lazy-load CLIP model and processor on first use."""
        if self._model is not None:
            return
        try:
            import torch
            from transformers import CLIPModel, CLIPProcessor

            model_id = "openai/clip-vit-base-patch16"
            self._torch = torch
            self._model = CLIPModel.from_pretrained(model_id).to(self.device)
            self._model.eval()
            self._processor = CLIPProcessor.from_pretrained(model_id)
        except Exception as exc:
            warnings.warn(
                f"CLIP model loading failed: {exc}. "
                f"Falling back to placeholder score 0.0."
            )
            self._model = None

    def score(
        self,
        image: Image.Image,
        reference: Optional[Image.Image] = None,
        **kwargs,
    ) -> float:
        """Compute image-text alignment score.

        Args:
            image: Test image.
            reference: Ignored for CLIP scoring (uses prompt instead).
            **kwargs: Must include ``prompt`` (str) for meaningful scoring.

        Returns:
            Float in [0.0, 1.0] — sigmoid-scaled logit. Returns 0.0
            if no prompt provided or model load fails.
        """
        prompt = kwargs.get("prompt")
        if not prompt:
            return 0.0

        self._load_model()
        if self._model is None or self._processor is None:
            return 0.0

        inputs = self._processor(
            text=prompt,
            images=image.convert("RGB"),
            return_tensors="pt",
            padding=True,
        ).to(self.device)

        with self._torch.no_grad():
            outputs = self._model(**inputs)
            logits_per_image = outputs.logits_per_image  # shape (1, 1)
            # Sigmoid-scale to [0, 1]
            score = self._torch.sigmoid(logits_per_image).item()

        return float(score)
