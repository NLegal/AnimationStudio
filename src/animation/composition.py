"""Scene Composition Engine — dynamic camera and frame composition.

Implements the Phase 9 Scene Composition Engine: dynamic framing,
rule of thirds, depth staging, eye-level movement, and transition-aware
composition so each shot follows animation principles.
"""

from __future__ import annotations
from dataclasses import dataclass, field

COMPOSITION_LAYERS: list[str] = ["background", "midground", "foreground"]

COMPOSITION_PRINCIPLES: dict[str, str] = {
    "rule_of_thirds": "Key subjects align with third-lines and intersections",
    "depth_staging": "Scenes stage across background, midground, and foreground",
    "eye_level": "Camera holds a child-friendly eye level for empathy",
    "dynamic_framing": "Framing shifts during camera moves to keep the subject breathing room",
    "lead_space": "Subject looks into negative space in the direction of action",
}


@dataclass
class CompositionRule:
    name: str = "rule_of_thirds"
    enabled: bool = True
    description: str = ""


@dataclass
class ShotComposition:
    shot_id: str = ""
    subject_position: str = "left_third"
    layers: list[str] = field(default_factory=lambda: list(COMPOSITION_LAYERS))
    camera: str = "eye_level"
    lead_space: str = "right"
    active_rules: list[str] = field(default_factory=list)
    notes: str = ""


class SceneCompositionEngine:
    def evaluate(self, subject_position: str, camera: str = "eye_level") -> ShotComposition:
        position = subject_position if subject_position else "center"
        lead_space = "right" if position in ("left_third", "left") else "left"
        active = [p for p, enabled in self.active_principles(camera).items() if enabled]
        return ShotComposition(
            shot_id=f"SHOT_{len(position)}",
            subject_position=position,
            camera=camera if camera in ("eye_level", "high_angle", "low_angle", "top_down") else "eye_level",
            lead_space=lead_space,
            active_rules=active,
            notes=f"Composition staged across {len(COMPOSITION_LAYERS)} depth layers",
        )

    def active_principles(self, camera: str = "eye_level") -> dict[str, bool]:
        return {
            "rule_of_thirds": True,
            "depth_staging": True,
            "eye_level": camera == "eye_level",
            "dynamic_framing": True,
            "lead_space": True,
        }

    def rule_of_thirds(self, subject_x: float, subject_y: float) -> tuple[float, float]:
        """Snap a subject to the nearest rule-of-thirds anchor (1/3 or 2/3)."""
        xs = [round(1 / 3, 3), round(2 / 3, 3)]
        ys = [round(1 / 3, 3), round(2 / 3, 3)]
        ax = min(xs, key=lambda x: abs(x - subject_x))
        ay = min(ys, key=lambda y: abs(y - subject_y))
        return ax, ay

    def stage_depth(self, subject_layer: str = "midground") -> dict[str, dict[str, str]]:
        index = COMPOSITION_LAYERS.index(subject_layer) if subject_layer in COMPOSITION_LAYERS else 1
        return {
            layer: {"staging": "depth_layer", "order": str(i + 1)}
            for i, layer in enumerate(COMPOSITION_LAYERS)
        }

    def list_principles(self) -> list[str]:
        return list(COMPOSITION_PRINCIPLES.keys())

    def describe_principles(self) -> dict[str, str]:
        return dict(COMPOSITION_PRINCIPLES)
