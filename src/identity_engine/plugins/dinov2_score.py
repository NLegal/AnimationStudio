"""DINOv2 scoring plugin — cosine similarity between image embeddings.

Weight: 40% (D-06)
Uses facebookresearch/dinov2_vits14 for embedding extraction.
Lazy-loads model on first use; falls back to 0.0 on load failure.
All heavy imports (torch, torchvision) are deferred to avoid
import-time crashes when dependencies are missing.
"""

import warnings
from typing import Optional

from PIL import Image


class DINOv2ScoringPlugin:
    """DINOv2-based identity scoring via embedding cosine similarity.

    Compares test image embedding against a reference embedding.
    Without a reference, returns 0.0 (no identity signal).
    """

    name: str = "character_consistency"
    weight: float = 0.40

    def __init__(self, weight: float = 0.40, device: str = "cpu"):
        self.weight = weight
        self.device = device
        self._model = None
        self._transform = None

    def _ensure_model(self):
        """Lazy-load torch, transforms, and the DINOv2 model on first use."""
        if self._model is not None:
            return
        try:
            import torch
            import torch.nn.functional as F
            from torchvision import transforms

            self._torch = torch
            self._F = F
            self._transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ])

            self._model = torch.hub.load(
                "facebookresearch/dinov2", "dinov2_vits14"
            ).to(self.device)
            self._model.eval()
        except Exception as exc:
            warnings.warn(
                f"DINOv2 model loading failed: {exc}. "
                f"Falling back to placeholder score 0.0."
            )
            self._model = None

    def embed(self, image: Image.Image):
        """Extract a DINOv2 embedding from an image.

        Args:
            image: PIL Image (RGB).

        Returns:
            1D array-like of shape (384,) — torch.Tensor if model loaded,
            numpy.ndarray fallback if model unavailable.
        """
        self._ensure_model()
        if self._model is None:
            import numpy as np
            return np.zeros(384)

        tensor = self._transform(image.convert("RGB")).unsqueeze(0).to(self.device)
        with self._torch.no_grad():
            embedding = self._model(tensor)
        return embedding.squeeze().cpu()

    def score(
        self,
        image: Image.Image,
        reference: Optional[Image.Image] = None,
        **kwargs,
    ) -> float:
        """Compute cosine similarity between image and reference embeddings.

        Args:
            image: Test image.
            reference: Reference image for comparison. If None, returns 0.0.

        Returns:
            Float in [0.0, 1.0] — cosine similarity clamped to non-negative.
        """
        if reference is None:
            return 0.0

        self._ensure_model()
        if self._model is None:
            return 0.0

        emb_a = self.embed(image)
        emb_b = self.embed(reference)

        cos = self._F.cosine_similarity(
            emb_a.unsqueeze(0), emb_b.unsqueeze(0)
        )
        return float(max(0.0, cos.item()))
