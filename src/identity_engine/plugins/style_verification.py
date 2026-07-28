"""Style verification plugin — style consistency scoring.

Weight: 10% (D-06)
Compares low-level image statistics (color distribution, contrast,
brightness, saturation histogram) between image and reference.
Without a reference, returns 0.5 (neutral — no style information).
"""

import warnings
from typing import Optional

import numpy as np
from PIL import Image


class StyleVerificationPlugin:
    """Scores style consistency between two images using low-level stats.

    Compares:
    - Brightness distribution (mean, std)
    - Saturation histogram
    - Contrast (RMS)
    - Color channel correlation
    """

    name: str = "style_consistency"
    weight: float = 0.10

    def __init__(self, weight: float = 0.10):
        self.weight = weight

    def score(
        self,
        image: Image.Image,
        reference: Optional[Image.Image] = None,
        **kwargs,
    ) -> float:
        """Compute style consistency score.

        Args:
            image: Test image.
            reference: Reference image for style comparison.
            **kwargs: Unused.

        Returns:
            Float in [0.0, 1.0]. Without reference, returns 0.5 (neutral).
        """
        if reference is None:
            return 0.5

        try:
            arr = np.array(image.convert("RGB"))
            ref_arr = np.array(reference.convert("RGB"))

            # Convert to float
            arr_f = arr.astype(np.float32)
            ref_f = ref_arr.astype(np.float32)

            # 1. Brightness comparison (mean and std)
            gray = np.mean(arr_f, axis=2)
            ref_gray = np.mean(ref_f, axis=2)

            brightness_sim = 1.0 - min(
                1.0, abs(np.mean(gray) - np.mean(ref_gray)) / 255.0
            )
            contrast_sim = 1.0 - min(
                1.0, abs(np.std(gray) - np.std(ref_gray)) / 128.0
            )

            # 2. Saturation comparison
            def _saturation(rgb: np.ndarray) -> np.ndarray:
                """Compute per-pixel saturation (max - min)."""
                r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
                mx = np.maximum(np.maximum(r, g), b)
                mn = np.minimum(np.minimum(r, g), b)
                return mx - mn

            sat = _saturation(arr_f)
            ref_sat = _saturation(ref_f)

            sat_hist_sim = _histogram_intersection(sat, ref_sat, bins=32)

            # 3. Color channel correlation
            def _channel_correlation(img: np.ndarray) -> float:
                """Mean correlation between RGB channels."""
                r, g, b = img[:, :, 0].flatten(), img[:, :, 1].flatten(), img[:, :, 2].flatten()
                rg = np.corrcoef(r, g)[0, 1] if np.std(r) > 0 and np.std(g) > 0 else 0
                rb = np.corrcoef(r, b)[0, 1] if np.std(r) > 0 and np.std(b) > 0 else 0
                gb = np.corrcoef(g, b)[0, 1] if np.std(g) > 0 and np.std(b) > 0 else 0
                return float((abs(rg) + abs(rb) + abs(gb)) / 3.0)

            corr_a = _channel_correlation(arr_f)
            corr_b = _channel_correlation(ref_f)
            corr_sim = 1.0 - min(1.0, abs(corr_a - corr_b))

            # Weighted combination
            score = (
                0.25 * brightness_sim
                + 0.25 * contrast_sim
                + 0.30 * sat_hist_sim
                + 0.20 * corr_sim
            )

            return float(max(0.0, min(1.0, score)))

        except Exception as exc:
            warnings.warn(f"Style verification failed: {exc}. Returning 0.5.")
            return 0.5


def _histogram_intersection(
    a: np.ndarray, b: np.ndarray, bins: int = 32
) -> float:
    """Normalized histogram intersection between two arrays."""
    hist_a, _ = np.histogram(a.flatten(), bins=bins, range=(0, 255))
    hist_b, _ = np.histogram(b.flatten(), bins=bins, range=(0, 255))
    hist_a = hist_a.astype(float) / max(hist_a.sum(), 1)
    hist_b = hist_b.astype(float) / max(hist_b.sum(), 1)
    return float(np.minimum(hist_a, hist_b).sum())
