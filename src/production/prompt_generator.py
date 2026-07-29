from typing import Dict, Optional
from src.production.models import Shot, CharacterAssignment, Camera


class PromptGenerator:
    def __init__(self):
        self._templates: Dict[str, str] = {}

    def register_template(self, key: str, template: str):
        self._templates[key] = template

    def register_templates(self, templates: Dict[str, str]):
        self._templates.update(templates)

    def get_template(self, key: str) -> Optional[str]:
        return self._templates.get(key)

    def _resolve_character_prompt(self, char: CharacterAssignment) -> str:
        parts = [char.character_id]
        if char.emotion:
            parts.append(f"emotion:{char.emotion}")
        if char.animation:
            parts.append(f"anim:{char.animation}")
        if char.clothing:
            parts.append(f"clothing:{char.clothing}")
        if char.accessories:
            parts.append(f"accessories:{','.join(char.accessories)}")
        return " | ".join(parts)

    def _resolve_camera_prompt(self, camera: Camera) -> str:
        return camera.to_prompt_suffix()

    def generate_shot_prompt(
        self, shot: Shot, template_key: Optional[str] = None
    ) -> str:
        base_template = "Generate {shot_type} of {character_description} in {environment}, {lighting}, {weather}, {camera_description}"

        if template_key and template_key in self._templates:
            base_template = self._templates[template_key]

        char_desc = "; ".join(
            self._resolve_character_prompt(c) for c in shot.characters
        )
        cam_desc = self._resolve_camera_prompt(shot.camera)

        return base_template.format(
            shot_type=shot.camera.shot_type,
            character_description=char_desc or "scene",
            environment=shot.environment or "default environment",
            lighting=shot.lighting or "natural lighting",
            weather=shot.weather or "clear weather",
            camera_description=cam_desc,
        )

    def generate_prompt_package(self, shot: Shot) -> Dict[str, str]:
        return {
            "character": self._resolve_character_prompt(shot.characters[0])
            if shot.characters
            else "",
            "environment": shot.environment,
            "camera": self._resolve_camera_prompt(shot.camera),
            "lighting": shot.lighting,
            "animation": shot.animation,
            "weather": shot.weather,
        }

    def compose_full_prompt(
        self,
        character_prompt: str,
        environment_prompt: str,
        animation_prompt: str,
        camera_prompt: str,
        lighting_prompt: str,
        quality_suffix: str = "Pixar-quality, Cocomelon-inspired, highly detailed, cinematic lighting, 8k",
    ) -> str:
        parts = [
            character_prompt,
            environment_prompt,
            animation_prompt,
            camera_prompt,
            lighting_prompt,
            quality_suffix,
        ]
        return ", ".join(p for p in parts if p)
