from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class ImageMetadata:
    image_id: str = ""
    episode: str = ""
    scene: str = ""
    shot: str = ""
    character_ids: list[str] = field(default_factory=list)
    environment_id: str = ""
    asset_ids: list[str] = field(default_factory=list)
    prompt_version: str = ""
    negative_prompt_version: str = ""
    model: str = ""
    seed: int = 0
    sampler: str = ""
    steps: int = 0
    cfg: float = 0.0
    width: int = 0
    height: int = 0
    aspect_ratio: str = ""
    generation_date: str = ""
    revision: int = 1
    approval_status: str = "pending"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> ImageMetadata:
        return cls(**data)

    def fill_defaults(self) -> ImageMetadata:
        if not self.generation_date:
            self.generation_date = datetime.now().isoformat()
        if self.width and self.height and not self.aspect_ratio:
            ratio = self.width / self.height
            if abs(ratio - 1.0) < 0.01:
                self.aspect_ratio = "1:1"
            elif abs(ratio - 1.5) < 0.01:
                self.aspect_ratio = "3:2"
            elif abs(ratio - 1.78) < 0.05:
                self.aspect_ratio = "16:9"
            elif abs(ratio - 0.67) < 0.01:
                self.aspect_ratio = "2:3"
            elif abs(ratio - 0.56) < 0.01:
                self.aspect_ratio = "9:16"
            else:
                self.aspect_ratio = f"{self.width}:{self.height}"
        return self

    def is_complete(self) -> bool:
        required = [self.image_id, self.model, self.generation_date]
        return all(required)
