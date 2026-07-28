"""Part verification plugin — body part detection presence score.

Weight: 10% (D-06)
Uses OpenCV Haar cascade as a proxy for "has character body parts".
Falls back to neutral 0.5 if opencv not installed.
"""

import warnings
from typing import Optional

import numpy as np
from PIL import Image


class PartVerificationPlugin:
    """Scores whether expected character body parts are detectable.

    Uses OpenCV face detection (Haar cascade) as a simple proxy for
    the presence of character features. Without a reference, returns 0.0
    (no part information available).
    """

    name: str = "facial_appeal"
    weight: float = 0.10

    def __init__(self, weight: float = 0.10):
        self.weight = weight
        self._face_cascade = None

    def _load_cascade(self):
        """Lazy-load the Haar cascade for face detection."""
        if self._face_cascade is not None:
            return
        try:
            import cv2

            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self._face_cascade = cv2.CascadeClassifier(cascade_path)
            if self._face_cascade.empty():
                warnings.warn("OpenCV Haar cascade file not found.")
                self._face_cascade = None
        except ImportError:
            warnings.warn(
                "OpenCV (cv2) not available. "
                "PartVerificationPlugin returning neutral score 0.5."
            )
            self._face_cascade = None
        except Exception as exc:
            warnings.warn(
                f"OpenCV cascade loading failed: {exc}. "
                f"Returning neutral score."
            )
            self._face_cascade = None

    def score(
        self,
        image: Image.Image,
        reference: Optional[Image.Image] = None,
        **kwargs,
    ) -> float:
        """Detect and score body part presence.

        Args:
            image: Test image.
            reference: Optional reference image for comparison.
            **kwargs: Unused.

        Returns:
            Float in [0.0, 1.0]. Without reference, returns 0.0.
        """
        if reference is None:
            return 0.0

        self._load_cascade()
        if self._face_cascade is None:
            return 0.5  # Neutral — can't determine

        try:
            import cv2

            # Convert PIL to OpenCV BGR
            open_cv_image = np.array(image.convert("RGB"))
            open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2GRAY)

            faces = self._face_cascade.detectMultiScale(
                open_cv_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )

            # Score based on face detection confidence
            if len(faces) > 0:
                return 0.8  # Face detected — good part presence
            else:
                return 0.3  # No face detected
        except Exception as exc:
            warnings.warn(f"Part detection failed: {exc}. Returning 0.5.")
            return 0.5
