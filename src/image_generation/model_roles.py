"""Model responsibility routing for image generation.

Enforces the Phase 8 model responsibilities table:

| Model          | Primary Purpose                          |
| -------------- | ---------------------------------------- |
| FLUX           | Final production-quality images          |
| SDXL           | Batch generation, concepts, environments |
| Pony Diffusion | Stylized expression and pose exploration |

Every model has a clearly defined responsibility.
"""

from __future__ import annotations

MODEL_RESPONSIBILITIES: dict[str, str] = {
    "flux": "Final production-quality images",
    "sdxl": "Batch generation, concepts, environments",
    "pony": "Stylized expression and pose exploration",
}

GENERATION_TYPE_MODEL: dict[str, str] = {
    "character_portrait": "flux",
    "character_turnaround": "flux",
    "expression_sheet": "pony",
    "character_pose": "flux",
    "pose": "flux",
    "expression": "pony",
    "environment": "sdxl",
    "background": "sdxl",
    "environment_variation": "sdxl",
    "asset": "flux",
    "prop": "flux",
    "storyboard_frame": "sdxl",
    "keyframe": "flux",
    "reference_sheet": "flux",
    "promotional_artwork": "flux",
    "thumbnail": "flux",
}


class ModelRoleManager:
    def purpose(self, model: str) -> str:
        return MODEL_RESPONSIBILITIES.get(
            model.lower(), "Unknown model"
        )

    def list_models(self) -> list[str]:
        return list(MODEL_RESPONSIBILITIES.keys())

    def responsibilities(self) -> dict[str, str]:
        return dict(MODEL_RESPONSIBILITIES)

    def recommended_model(self, generation_type: str) -> str:
        return GENERATION_TYPE_MODEL.get(generation_type, "flux")

    def is_responsible(self, model: str, generation_type: str) -> bool:
        return self.recommended_model(generation_type) == model.lower()
