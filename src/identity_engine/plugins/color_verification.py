"""Color verification plugin — brand palette adherence.

Weight: 10% (D-06)
Extracts dominant colors via K-Means and scores against a reference
brand palette (Cocomelon-inspired pastel primaries).
Falls back to sklearn if external color-palette-extractor is unavailable.
"""

import json
import warnings
from pathlib import Path
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

# Lazily-loaded cache for brand palette from filesystem
_cached_palette: Optional[list[tuple[int, int, int]]] = None


def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    """Convert a hex color string (e.g. '#F0A0C0') to an (R, G, B) tuple."""
    h = hex_str.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def _load_brand_palette_from_file() -> list[tuple[int, int, int]]:
    """Load brand palette from Universe/ColorPalette/brand-palette.json.

    Reads the 'primary' color group from the palette JSON file, converts
    hex values to RGB tuples, and returns the palette. Falls back to
    DEFAULT_BRAND_PALETTE if the file is missing or unparseable.

    Returns:
        List of (R, G, B) tuples representing the brand palette colors.
    """
    # Attempt to resolve the palette file relative to the project root.
    # Walk up from this file's directory to find the repo root.
    palette_path = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "Universe" / "ColorPalette" / "brand-palette.json"
    )

    if not palette_path.exists():
        warnings.warn(
            f"Brand palette file not found at {palette_path}. "
            "Falling back to DEFAULT_BRAND_PALETTE."
        )
        return DEFAULT_BRAND_PALETTE

    try:
        with open(palette_path) as f:
            data = json.load(f)

        colors: list[tuple[int, int, int]] = []
        for name, info in data.get("primary", {}).items():
            hex_val = info.get("hex", "")
            if hex_val:
                colors.append(_hex_to_rgb(hex_val))

        if not colors:
            warnings.warn(
                "Brand palette file has no 'primary' colors. "
                "Falling back to DEFAULT_BRAND_PALETTE."
            )
            return DEFAULT_BRAND_PALETTE

        return colors
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        warnings.warn(
            f"Failed to parse brand palette file: {exc}. "
            "Falling back to DEFAULT_BRAND_PALETTE."
        )
        return DEFAULT_BRAND_PALETTE


def _color_distance(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    """Euclidean distance in RGB space."""
    return np.sqrt(sum((int(a) - int(b)) ** 2 for a, b in zip(c1, c2)))


def _closest_palette_distance(
    color: tuple[int, int, int], palette: list[tuple[int, int, int]]
) -> float:
    """Distance from a color to the nearest palette color."""
    return min(_color_distance(color, pc) for pc in palette)


def _extract_dominant_colors(
    image: Image.Image, n_colors: int = 5, use_kmeans: bool = True
) -> list[tuple[int, int, int]]:
    """Extract dominant colors via K-Means clustering."""
    if not use_kmeans:
        arr = np.array(image.convert("RGB").resize((64, 64)))
        pixels = arr.reshape(-1, 3)
        idx = np.linspace(0, len(pixels) - 1, n_colors, dtype=int)
        return [tuple(pixels[i]) for i in idx]

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

    The brand palette is loaded from Universe/ColorPalette/brand-palette.json
    on first score() call and cached as a class-level attribute so filesystem
    reads happen at most once per process. Falls back to DEFAULT_BRAND_PALETTE
    if the file is not found or unparseable.
    """

    name: str = "color_harmony"
    weight: float = 0.10
    _cached_palette: Optional[list[tuple[int, int, int]]] = None

    def __init__(
        self,
        weight: float = 0.10,
        brand_palette: Optional[list[tuple[int, int, int]]] = None,
        use_kmeans: bool = True,
    ):
        self.weight = weight
        self.brand_palette = brand_palette
        self.use_kmeans = use_kmeans

    def _get_palette(self) -> list[tuple[int, int, int]]:
        """Return the brand palette, loading from filesystem on first call.

        Uses a class-level cache so the file is read at most once per
        process, even across multiple instances.
        """
        if self.brand_palette is not None:
            # Instance-level override (e.g. test injection)
            return self.brand_palette

        if ColorVerificationPlugin._cached_palette is None:
            ColorVerificationPlugin._cached_palette = _load_brand_palette_from_file()
        return ColorVerificationPlugin._cached_palette

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
                       uses filesystem-loaded brand palette).
            **kwargs: Unused.

        Returns:
            Float in [0.0, 1.0] — 1.0 = all dominant colors match palette.
        """
        # Determine target palette
        palette = self._get_palette()
        if reference is not None:
            palette = _extract_dominant_colors(reference, n_colors=5,
                                               use_kmeans=self.use_kmeans)

        try:
            dominant = _extract_dominant_colors(image, n_colors=5,
                                                use_kmeans=self.use_kmeans)
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
