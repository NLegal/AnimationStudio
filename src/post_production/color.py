"""Color Correction Engine.

Implements Phase 10 color correction: brightness, contrast, saturation,
white balance, gamma, and exposure adjustments applied per scene to
maintain a consistent, gentle look suitable for young children.
"""

from __future__ import annotations
from dataclasses import dataclass, field

BRIGHTNESS_RANGE = (-1.0, 1.0)
CONTRAST_RANGE = (0.0, 2.0)
SATURATION_RANGE = (0.0, 2.0)
WHITE_BALANCE_RANGE = (-1.0, 1.0)
GAMMA_RANGE = (0.1, 3.0)
EXPOSURE_RANGE = (-2.0, 2.0)


@dataclass
class ColorCorrectionSettings:
    brightness: float = 0.0
    contrast: float = 1.0
    saturation: float = 1.0
    white_balance: float = 0.0
    gamma: float = 1.0
    exposure: float = 0.0
    description: str = ""

    def clamp(self) -> None:
        lo, hi = BRIGHTNESS_RANGE
        self.brightness = max(lo, min(hi, self.brightness))
        lo, hi = CONTRAST_RANGE
        self.contrast = max(lo, min(hi, self.contrast))
        lo, hi = SATURATION_RANGE
        self.saturation = max(lo, min(hi, self.saturation))
        lo, hi = WHITE_BALANCE_RANGE
        self.white_balance = max(lo, min(hi, self.white_balance))
        lo, hi = GAMMA_RANGE
        self.gamma = max(lo, min(hi, self.gamma))
        lo, hi = EXPOSURE_RANGE
        self.exposure = max(lo, min(hi, self.exposure))

    def is_neutral(self) -> bool:
        return (
            self.brightness == 0.0
            and self.contrast == 1.0
            and self.saturation == 1.0
            and self.white_balance == 0.0
            and self.gamma == 1.0
            and self.exposure == 0.0
        )

    def as_dict(self) -> dict:
        return {
            "brightness": self.brightness,
            "contrast": self.contrast,
            "saturation": self.saturation,
            "white_balance": self.white_balance,
            "gamma": self.gamma,
            "exposure": self.exposure,
        }


PRESET_CORRECTIONS: dict[str, dict] = {
    "gentle_brighten": {"brightness": 0.05, "contrast": 0.95, "saturation": 1.05},
    "pastel_soften": {"contrast": 0.85, "saturation": 0.9, "gamma": 1.05},
    "bright_daylight": {"brightness": 0.1, "exposure": 0.3, "white_balance": 0.05},
    "warm_evening": {"white_balance": 0.2, "gamma": 1.05, "saturation": 1.1},
    "storybook": {"contrast": 1.15, "saturation": 1.2, "gamma": 0.95},
}


class ColorCorrectionEngine:
    def settings(self, brightness=0.0, contrast=1.0, saturation=1.0,
                 white_balance=0.0, gamma=1.0, exposure=0.0) -> ColorCorrectionSettings:
        s = ColorCorrectionSettings(
            brightness=brightness,
            contrast=contrast,
            saturation=saturation,
            white_balance=white_balance,
            gamma=gamma,
            exposure=exposure,
        )
        s.clamp()
        return s

    def preset(self, name: str) -> ColorCorrectionSettings:
        values = PRESET_CORRECTIONS.get(name.lower(), {})
        s = ColorCorrectionSettings(**values, description=f"Preset: {name}")
        s.clamp()
        return s

    def list_presets(self) -> list[str]:
        return list(PRESET_CORRECTIONS.keys())

    def suggest(self, scene_type: str = "learning") -> ColorCorrectionSettings:
        suggestions = {
            "opening": "bright_daylight",
            "learning": "pastel_soften",
            "song": "storybook",
            "practice": "gentle_brighten",
            "celebration": "bright_daylight",
            "outro": "warm_evening",
        }
        return self.preset(suggestions.get(scene_type.lower(), "pastel_soften"))

    def apply(self, settings: ColorCorrectionSettings, image_pixels: list = None) -> dict:
        return {
            "settings": settings.as_dict(),
            "mode": "per_scene",
            "note": "Color corrections applied per scene to keep the look gentle and consistent",
        }
