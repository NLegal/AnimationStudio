from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from PIL import Image


REFERENCE_CATEGORIES = {
    "characters", "environments", "assets",
    "poses", "expressions", "color_palettes", "style_sheets",
}


@dataclass
class ReferenceImage:
    name: str
    category: str
    path: Optional[Path] = None
    image: Optional[Image.Image] = None
    source: str = ""
    tags: list[str] = field(default_factory=list)


class ReferenceImageManager:
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path("ImageGeneration/References")
        self._cache: dict[str, ReferenceImage] = {}

    def register(self, reference: ReferenceImage) -> None:
        if reference.category not in REFERENCE_CATEGORIES:
            raise ValueError(
                f"Unknown category '{reference.category}'. "
                f"Choose from {REFERENCE_CATEGORIES}"
            )
        key = f"{reference.category}:{reference.name}"
        self._cache[key] = reference

    def get(self, category: str, name: str) -> Optional[ReferenceImage]:
        return self._cache.get(f"{category}:{name}")

    def get_by_category(self, category: str) -> list[ReferenceImage]:
        return [
            ref for key, ref in self._cache.items()
            if key.startswith(f"{category}:")
        ]

    def get_by_tags(self, tags: list[str]) -> list[ReferenceImage]:
        return [
            ref for ref in self._cache.values()
            if any(t in ref.tags for t in tags)
        ]

    def load_image(self, reference: ReferenceImage) -> Optional[Image.Image]:
        if reference.image is not None:
            return reference.image
        if reference.path is not None and reference.path.exists():
            img = Image.open(reference.path)
            reference.image = img
            return img
        return None

    def get_character_reference(self, name: str) -> Optional[ReferenceImage]:
        return self.get("characters", name)

    def get_environment_reference(self, name: str) -> Optional[ReferenceImage]:
        return self.get("environments", name)

    def get_pose_reference(self, name: str) -> Optional[ReferenceImage]:
        return self.get("poses", name)

    def get_expression_reference(self, name: str) -> Optional[ReferenceImage]:
        return self.get("expressions", name)

    def list_categories(self) -> set[str]:
        return REFERENCE_CATEGORIES

    def count(self) -> int:
        return len(self._cache)
