from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class PromptVersion:
    version_id: str = ""
    prompt_text: str = ""
    category: str = ""
    model: str = ""
    negative_prompt: str = ""
    author: str = ""
    created_at: str = ""
    notes: str = ""
    parent_version: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class PromptVersionManager:
    def __init__(self):
        self._versions: dict[str, PromptVersion] = {}
        self._counter: dict[str, int] = {}

    def register(self, version: PromptVersion) -> str:
        version_id = self._next_id(version.category)
        version.version_id = version_id
        if not version.created_at:
            version.created_at = datetime.now().isoformat()
        self._versions[version_id] = version
        return version_id

    def get(self, version_id: str) -> Optional[PromptVersion]:
        return self._versions.get(version_id)

    def get_latest(self, category: str) -> Optional[PromptVersion]:
        versions = self.list_by_category(category)
        return versions[-1] if versions else None

    def list_by_category(self, category: str) -> list[PromptVersion]:
        return sorted(
            [v for v in self._versions.values() if v.category == category],
            key=lambda v: v.created_at,
        )

    def list_all(self) -> list[PromptVersion]:
        return sorted(
            self._versions.values(),
            key=lambda v: v.created_at,
        )

    def create_version(
        self,
        prompt_text: str,
        category: str,
        model: str = "",
        negative_prompt: str = "",
        author: str = "",
        notes: str = "",
        parent_version: Optional[str] = None,
    ) -> str:
        version = PromptVersion(
            prompt_text=prompt_text,
            category=category,
            model=model,
            negative_prompt=negative_prompt,
            author=author,
            notes=notes,
            parent_version=parent_version,
        )
        return self.register(version)

    def _next_id(self, category: str) -> str:
        self._counter[category] = self._counter.get(category, 0) + 1
        num = self._counter[category]
        prefix = category.upper()[:5]
        return f"PROMPT_{prefix}_V{num}"

    def count(self) -> int:
        return len(self._versions)
