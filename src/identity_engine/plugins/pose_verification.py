"""Pose verification plugin — basic pose similarity via edge/HoG features.

Weight: 5% (D-06)
Compares test image to reference using structural similarity features.
Falls back to 0.5 if opencv not installed.
"""

import warnings
from typing import Optional

import numpy as np
from PIL import Image


class PoseVerificationPlugin:
    """Basic pose similarity scoring via edge/HoG-like features.

    Compares low-level structural features (edges, gradients) between
    test image and reference. Without a reference, returns 0.0
    (no pose information).
    """

    name: str = "silhouette_recognizability"
    weight: float = 0.05

    def __init__(self, weight: float = 0.05):
        self.weight = weight

    def score(
        self,
        image: Image.Image,
        reference: Optional[Image.Image] = None,
        **kwargs,
    ) -> float:
        """Compute structural similarity between image and reference.

        Args:
            image: Test image.
            reference: Reference image for pose comparison.
            **kwargs: Unused.

        Returns:
            Float in [0.0, 1.0]. Without reference, returns 0.0.
        """
        if reference is None:
            return 0.0

        try:
            import cv2

            # Convert both to grayscale and resize to same size
            size = (128, 128)
            img_gray = cv2.cvtColor(
                np.array(image.convert("RGB").resize(size, Image.LANCZOS)),
                cv2.COLOR_RGB2GRAY,
            )
            ref_gray = cv2.cvtColor(
                np.array(reference.convert("RGB").resize(size, Image.LANCZOS)),
                cv2.COLOR_RGB2GRAY,
            )

            # Compute edge images
            img_edges = cv2.Canny(img_gray, 50, 150)
            ref_edges = cv2.Canny(ref_gray, 50, 150)

            # Compute HoG-like orientation histograms
            def _hog_features(gray: np.ndarray, cell_size: int = 16) -> np.ndarray:
                """Simple gradient orientation histogram."""
                gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
                gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
                mag, ang = cv2.cartToPolar(gx, gy)
                # Bin orientations into 9 bins (0-180°)
                h, w = gray.shape
                cells_h, cells_w = h // cell_size, w // cell_size
                hist = np.zeros((cells_h, cells_w, 9), dtype=np.float32)
                for i in range(cells_h):
                    for j in range(cells_w):
                        cell_mag = mag[
                            i * cell_size : (i + 1) * cell_size,
                            j * cell_size : (j + 1) * cell_size,
                        ]
                        cell_ang = ang[
                            i * cell_size : (i + 1) * cell_size,
                            j * cell_size : (j + 1) * cell_size,
                        ]
                        bin_idx = (cell_ang / 20.0).astype(int) % 9
                        for b in range(9):
                            hist[i, j, b] = np.sum(cell_mag[bin_idx == b])
                return hist.flatten()

            feat_a = _hog_features(img_gray)
            feat_b = _hog_features(ref_gray)

            # Cosine similarity of feature vectors
            norm_a = np.linalg.norm(feat_a)
            norm_b = np.linalg.norm(feat_b)
            if norm_a == 0 or norm_b == 0:
                return 0.5

            similarity = float(np.dot(feat_a, feat_b) / (norm_a * norm_b))
            return float(max(0.0, min(1.0, similarity)))

        except ImportError:
            warnings.warn(
                "OpenCV (cv2) not available. "
                "PoseVerificationPlugin returning neutral score 0.5."
            )
            return 0.5
        except Exception as exc:
            warnings.warn(f"Pose verification failed: {exc}. Returning 0.5.")
            return 0.5
