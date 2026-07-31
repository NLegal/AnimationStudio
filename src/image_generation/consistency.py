"""Character, Environment, and Style Locking system.

Every recurring asset must be locked before production so images stay
consistent across thousands of episodes. This implements the Phase 8
locking standards:

- Character Locking: reference images, identity LoRA, face consistency
  methods, character embeddings, approved color palette, approved costumes.
- Environment Locking: master image, layout map, lighting presets, weather
  presets, color palette, camera reference images, object placement rules.
- Style Locking: the Studio Style Guide characteristics every image must
  follow.

Never regenerate a character or environment from scratch.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


STUDIO_STYLE_CHARACTERISTICS: dict[str, str] = {
    "soft_lighting": "Soft lighting with gentle shadows",
    "rounded_geometry": "Rounded geometry and smooth shapes",
    "friendly_proportions": "Friendly, childlike proportions",
    "bright_pastel_colors": "Bright pastel colors",
    "minimal_visual_noise": "Minimal visual noise",
    "large_readable_shapes": "Large, readable shapes",
    "clean_backgrounds": "Clean backgrounds",
}

CONTROLLED_PALETTE: dict[str, list[str]] = {
    "primary_colors": ["red", "blue", "yellow", "green"],
    "pastels": ["pink", "mint", "lavender", "peach", "sky"],
    "warm_neutrals": ["cream", "tan", "soft_brown", "beige"],
    "natural_greens": ["leaf", "sage", "forest_light"],
    "soft_blues": ["powder", "periwinkle", "baby_blue"],
}


@dataclass
class ColorPalette:
    name: str = ""
    colors: list[str] = field(default_factory=list)


@dataclass
class CharacterLock:
    character_id: str = ""
    reference_images: list[str] = field(default_factory=list)
    identity_lora: str = ""
    face_consistency_method: str = ""
    character_embeddings: list[str] = field(default_factory=list)
    approved_color_palette: str = ""
    approved_costumes: list[str] = field(default_factory=list)
    locked: bool = False

    def check(self) -> dict[str, bool]:
        return {
            "has_reference_images": len(self.reference_images) > 0,
            "has_identity_method": bool(
                self.identity_lora
                or self.face_consistency_method
                or self.character_embeddings
            ),
            "has_approved_palette": bool(self.approved_color_palette),
            "has_approved_costumes": len(self.approved_costumes) > 0,
        }

    def is_locked(self) -> bool:
        return self.locked and all(self.check().values())


@dataclass
class EnvironmentProfile:
    environment_id: str = ""
    name: str = ""
    master_image: str = ""
    layout_map: str = ""
    lighting_presets: list[str] = field(default_factory=list)
    weather_presets: list[str] = field(default_factory=list)
    color_palette: str = ""
    camera_reference_images: list[str] = field(default_factory=list)
    object_placement_rules: list[str] = field(default_factory=list)

    def check(self) -> dict[str, bool]:
        return {
            "has_master_image": bool(self.master_image),
            "has_layout_map": bool(self.layout_map),
            "has_lighting_presets": len(self.lighting_presets) > 0,
            "has_weather_presets": len(self.weather_presets) > 0,
            "has_color_palette": bool(self.color_palette),
            "has_object_placement_rules": len(self.object_placement_rules) > 0,
        }

    def is_complete(self) -> bool:
        return all(self.check().values())


@dataclass
class StyleGuide:
    name: str = "Studio Style Guide"
    characteristics: dict[str, str] = field(
        default_factory=lambda: dict(STUDIO_STYLE_CHARACTERISTICS)
    )
    controlled_palette: dict[str, list[str]] = field(
        default_factory=lambda: {k: list(v) for k, v in CONTROLLED_PALETTE.items()}
    )

    def characteristic_keys(self) -> list[str]:
        return list(self.characteristics.keys())

    def contains_characteristic(self, key: str) -> bool:
        return key in self.characteristics


class ConsistencyManager:
    """Central registry enforcing character, environment, and style locking."""

    def __init__(self):
        self._character_locks: dict[str, CharacterLock] = {}
        self._environments: dict[str, EnvironmentProfile] = {}
        self._style_guide: StyleGuide = StyleGuide()

    # Character Locking
    def lock_character(self, lock: CharacterLock) -> CharacterLock:
        lock.locked = True
        self._character_locks[lock.character_id] = lock
        return lock

    def get_character_lock(self, character_id: str) -> Optional[CharacterLock]:
        return self._character_locks.get(character_id)

    def unlock_character(self, character_id: str) -> bool:
        lock = self._character_locks.get(character_id)
        if lock is None:
            return False
        lock.locked = False
        return True

    def validate_character(self, character_id: str) -> dict[str, bool]:
        lock = self.get_character_lock(character_id)
        if lock is None:
            return {"locked": False, "registered": False}
        checks = lock.check()
        checks["locked"] = lock.locked
        return checks

    def locked_character_count(self) -> int:
        return sum(1 for l in self._character_locks.values() if l.locked)

    # Environment Locking
    def register_environment(self, profile: EnvironmentProfile) -> EnvironmentProfile:
        self._environments[profile.environment_id] = profile
        return profile

    def get_environment(self, environment_id: str) -> Optional[EnvironmentProfile]:
        return self._environments.get(environment_id)

    def validate_environment(self, environment_id: str) -> dict[str, bool]:
        profile = self.get_environment(environment_id)
        if profile is None:
            return {"registered": False}
        checks = profile.check()
        checks["registered"] = True
        return checks

    def environment_count(self) -> int:
        return len(self._environments)

    # Style Locking
    def set_style_guide(self, guide: StyleGuide) -> None:
        self._style_guide = guide

    def style_guide(self) -> StyleGuide:
        return self._style_guide

    def validate_style(self, satisfied: dict[str, bool]) -> dict[str, bool]:
        checks = {
            "all_style_characteristics_met": all(
                satisfied.get(key, False) for key in self._style_guide.characteristic_keys()
            ),
            "uses_controlled_palette": satisfied.get("controlled_palette", False),
            "avoids_oversaturation": satisfied.get("no_oversaturation", False),
        }
        return checks

    def enforce(
        self,
        character_id: Optional[str] = None,
        environment_id: Optional[str] = None,
        style_satisfied: Optional[dict[str, bool]] = None,
    ) -> dict[str, bool]:
        results: dict[str, bool] = {}
        if character_id is not None:
            for key, value in self.validate_character(character_id).items():
                results[f"character_{key}"] = value
        if environment_id is not None:
            for key, value in self.validate_environment(environment_id).items():
                results[f"environment_{key}"] = value
        if style_satisfied is not None:
            for key, value in self.validate_style(style_satisfied).items():
                results[f"style_{key}"] = value
        results["all_locked"] = all(results.values())
        return results
