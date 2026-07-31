"""Visual Enhancement Engine.

Implements Phase 10 visual enhancement: sharpening, noise reduction,
frame interpolation, artifact cleanup, and edge refinement applied after
color correction to polish the final image quality.
"""

from __future__ import annotations
from dataclasses import dataclass, field

ENHANCEMENT_STEPS: list[str] = [
    "sharpening",
    "noise_reduction",
    "frame_interpolation",
    "artifact_cleanup",
    "edge_refinement",
]

ENHANCEMENT_DESCRIPTIONS: dict[str, str] = {
    "sharpening": "Restore fine detail lost during upscaling and interpolation",
    "noise_reduction": "Remove grain while preserving soft shading",
    "frame_interpolation": "Smooth motion between low frame-rate keyframes",
    "artifact_cleanup": "Remove compression and interpolation artifacts",
    "edge_refinement": "Clean and define edges for a crisp animated look",
}


@dataclass
class EnhancementSettings:
    sharpening: float = 0.5
    noise_reduction: float = 0.3
    frame_interpolation: bool = True
    artifact_cleanup: bool = True
    edge_refinement: float = 0.5

    def clamp(self) -> None:
        self.sharpening = max(0.0, min(1.0, self.sharpening))
        self.noise_reduction = max(0.0, min(1.0, self.noise_reduction))
        self.edge_refinement = max(0.0, min(1.0, self.edge_refinement))


class EnhancementEngine:
    def recommend(self, source_fps: int, target_fps: int) -> EnhancementSettings:
        needs_interpolation = target_fps > source_fps
        return EnhancementSettings(
            sharpening=0.6,
            noise_reduction=0.4,
            frame_interpolation=needs_interpolation,
            artifact_cleanup=True,
            edge_refinement=0.5,
        )

    def pipeline(self, settings: EnhancementSettings | None = None) -> list[dict]:
        s = settings or EnhancementSettings()
        s.clamp()
        steps = [
            {"step": "sharpening", "enabled": True, "strength": s.sharpening},
            {"step": "noise_reduction", "enabled": True, "strength": s.noise_reduction},
            {"step": "frame_interpolation", "enabled": s.frame_interpolation},
            {"step": "artifact_cleanup", "enabled": s.artifact_cleanup},
            {"step": "edge_refinement", "enabled": True, "strength": s.edge_refinement},
        ]
        return steps

    def describe_step(self, step: str) -> str:
        return ENHANCEMENT_DESCRIPTIONS.get(step, step)

    def list_steps(self) -> list[str]:
        return list(ENHANCEMENT_STEPS)
