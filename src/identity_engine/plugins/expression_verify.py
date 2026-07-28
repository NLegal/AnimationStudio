"""Expression verification plugin — expression match scoring.

Weight: 5% (D-06)
If expression_name is provided and matches keywords, checks image for
expression-correlated features (brightness, contrast, etc.).
Without a reference, returns 0.5 (neutral).
No external model dependency — uses basic image statistics as proxy.
"""

import math
from typing import Optional

import numpy as np
from PIL import Image


# Expression keywords grouped by emotional valence
POSITIVE_EXPRESSIONS = {
    "happy", "very_happy", "laughing", "giggling", "smiling",
    "excited", "proud", "determined", "whistling", "blowing_kiss",
    "winking", "singing",
}
NEUTRAL_EXPRESSIONS = {
    "neutral", "thinking", "curious", "surprised", "confused",
}
NEGATIVE_EXPRESSIONS = {
    "sad", "crying", "scared", "embarrassed", "sleepy", "yawning",
}


class ExpressionVerificationPlugin:
    """Scores expression match between image and expected expression.

    Uses basic image statistics (brightness, variance, local contrast)
    as a heuristic proxy for expression type.
    """

    name: str = "child_friendliness"
    weight: float = 0.05

    def __init__(self, weight: float = 0.05):
        self.weight = weight

    def score(
        self,
        image: Image.Image,
        reference: Optional[Image.Image] = None,
        **kwargs,
    ) -> float:
        """Compute expression match score.

        Args:
            image: Test image.
            reference: Reference image (ignored if expression_name provided).
            **kwargs: ``expression_name`` (str) for targeted matching.

        Returns:
            Float in [0.0, 1.0]. Without reference, returns 0.5 (neutral).
        """
        expression_name = kwargs.get("expression_name")

        if reference is None and not expression_name:
            return 0.5  # Neutral — no information

        try:
            arr = np.array(image.convert("RGB"))
            gray = np.array(image.convert("L"))

            # Image statistics
            mean_brightness = np.mean(gray) / 255.0
            std_brightness = np.std(gray) / 255.0

            if expression_name:
                return self._score_by_expression_name(
                    expression_name, mean_brightness, std_brightness
                )

            # With reference but no expression name: compare stats
            ref_arr = np.array(reference.convert("RGB"))
            ref_gray = np.array(reference.convert("L"))

            ref_mean = np.mean(ref_gray) / 255.0
            ref_std = np.std(ref_gray) / 255.0

            # Similarity based on brightness and contrast proximity
            brightness_sim = 1.0 - min(1.0, abs(mean_brightness - ref_mean))
            contrast_sim = 1.0 - min(1.0, abs(std_brightness - ref_std))

            # Color distribution similarity (RGB histograms)
            score = 0.0
            for c in range(3):
                hist_a, _ = np.histogram(arr[:, :, c], bins=32, range=(0, 255))
                hist_b, _ = np.histogram(ref_arr[:, :, c], bins=32, range=(0, 255))
                hist_a = hist_a.astype(float) / max(hist_a.sum(), 1)
                hist_b = hist_b.astype(float) / max(hist_b.sum(), 1)
                intersection = np.minimum(hist_a, hist_b).sum()
                score += intersection / 3.0

            combined = 0.3 * brightness_sim + 0.3 * contrast_sim + 0.4 * score
            return float(max(0.0, min(1.0, combined)))

        except Exception as exc:
            import warnings
            warnings.warn(f"Expression verification failed: {exc}. Returning 0.5.")
            return 0.5

    @staticmethod
    def _score_by_expression_name(
        name: str, mean_brightness: float, std_brightness: float
    ) -> float:
        """Heuristic score based on expression name and image statistics.

        Positive expressions tend to be brighter with higher contrast.
        Negative expressions tend to be darker.
        """
        name_lower = name.lower().replace(" ", "_")

        if name_lower in POSITIVE_EXPRESSIONS:
            # Expect higher brightness and contrast
            score = 0.5 + 0.3 * mean_brightness + 0.2 * std_brightness
        elif name_lower in NEGATIVE_EXPRESSIONS:
            # Expect lower brightness
            score = 0.5 - 0.3 * (0.5 - mean_brightness) + 0.1 * std_brightness
        else:
            # Neutral / unknown expression
            score = 0.5

        return float(max(0.0, min(1.0, score)))
