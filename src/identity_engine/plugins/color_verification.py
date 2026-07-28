"""Color verification plugin — brand palette adherence.

Weight: 10% (D-06)
Extracts dominant colors via K-Means and scores against a reference
brand palette (Cocomelon-inspired pastel primaries).
Falls back to sklearn if external color-palette-extractor is unavailable.
"""

import warnings
from typing import Optional

import numpy as np
from PIL import Image


# Default Cocomelon-inspired brand palette (pastel primary colors)
DEFAULT_BRAND_PALETTE: list[tuple[int, int, int]] = [
    (255, 182, 193),  # pastel pink
    (173, 216, 230),  # pastel blue
    (255, 255, 153),  # pastel yellow
    (144, 238, 144),  # pastel green
    (255, 204, 153),  # pastel orange
]


def _color_distance(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    """Euclidean distance in RGB space."""
    return np.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))


def _closest_palette_distance(
    color: tuple[int, int, int], palette: list[tuple[int, int, int]]
) -> float:
    """Distance from a color to the nearest palette color."""
    return min(_color_distance(color, pc) for pc in palette)


def _extract_dominant_colors(
    image: Image.Image, n_colors: int = 5
) -> list[tuple[int, int, int]]:
    """Extract dominant colors via K-Means clustering."""
    try:
        from sklearn.cluster import KMeans
    except ImportError as exc:
        warnings.warn(
            f"sklearn.cluster.KMeans not available ({exc}). "
            f"Using simple pixel sampling as fallback."
        )
        # Fallback: uniform sampling
        arr = np.array(image.convert("RGB").resize((64, 64)))
        pixels = arr.reshape(-1, 3)
        idx = np.linspace(0, len(pixels) - 1, n_colors, dtype=int)
        return [tuple(pixels[i]) for i in idx]

    arr = np.array(image.convert("RGB").resize((128, 128)))
    pixels = arr.reshape(-1, 3)

    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init="auto")
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_.astype(int)
    return [tuple(c) for c in colors]


class ColorVerificationPlugin:
    """Scores how well image colors match the brand palette.

    Extracts dominant colors, measures distance to the reference palette,
    and returns a normalized score.
    """

    name: str = "color_harmony"
    weight: float = 0.10

    def __init__(
        self,
        weight: float = 0.10,
        brand_palette: Optional[list[tuple[int, int, int]]] = None,
    ):
        self.weight = weight
        self.brand_palette = brand_palette or DEFAULT_BRAND_PALETTE

    def score(
        self,
        image: Image.Image,
        reference: Optional[Image.Image] = None,
        **kwargs,
    ) -> float:
        """Compute brand palette adherence score.

        Args:
            image: Test image.
            reference: Reference image (palette compared; if None,
                       uses DEFAULT_BRAND_PALETTE).
            **kwargs: Unused.

        Returns:
            Float in [0.0, 1.0] — 1.0 = all dominant colors match palette.
        """
        # Determine target palette
        palette = DEFAULT_BRAND_PALETTE
        if reference is not None:
            palette = _extract_dominant_colors(reference, n_colors=5)

        try:
            dominant = _extract_dominant_colors(image, n_colors=5)
        except Exception as exc:
            warnings.warn(f"Color extraction failed: {exc}. Returning 0.0.")
            return 0.0

        # For grayscale images (single channel or all channels equal)
        arr = np.array(image.convert("RGB"))
        if arr.std() < 10:
            return 0.1  # Very low score for grayscale

        # Compute score: average proximity to palette
        # Max distance in RGB is ~441 (sqrt(3*255^2))
        max_dist = 441.0
        distances = [
            _closest_palette_distance(c, palette) for c in dominant
        ]
        avg_distance = np.mean(distances)
        score = max(0.0, 1.0 - avg_distance / max_dist)
        return round(float(score), 4)
