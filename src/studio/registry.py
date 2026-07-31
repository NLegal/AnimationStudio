from __future__ import annotations

from .models import RegistryEntry


class ModelRegistry:
    def __init__(self):
        self._models: dict[str, RegistryEntry] = {}

    def register(
        self,
        model_name: str,
        version: str = "1.0",
        purpose: str = "",
        input_type: str = "",
        output_type: str = "",
        hardware: str = "gpu",
        status: str = "active",
        metadata: dict | None = None,
    ) -> RegistryEntry:
        entry = RegistryEntry(
            entry_id=f"MODEL_{model_name}",
            name=model_name,
            version=version,
            category="model",
            status=status,
            metadata={
                "purpose": purpose,
                "input_type": input_type,
                "output_type": output_type,
                "hardware": hardware,
                "performance": metadata.get("performance", "") if metadata else "",
                "quality_score": metadata.get("quality_score", 0.0) if metadata else 0.0,
                "approved_use_cases": metadata.get("approved_use_cases", []) if metadata else [],
            },
        )
        self._models[entry.entry_id] = entry
        return entry

    def get(self, model_name: str) -> RegistryEntry:
        return self._models.get(f"MODEL_{model_name}", RegistryEntry())

    def list_models(self) -> list[RegistryEntry]:
        return list(self._models.values())

    def active_models(self) -> list[RegistryEntry]:
        return [m for m in self._models.values() if m.status == "active"]

    def models_for_purpose(self, purpose: str) -> list[RegistryEntry]:
        return [m for m in self._models.values() if m.metadata.get("purpose") == purpose]

    def set_status(self, model_name: str, status: str) -> bool:
        entry = self._models.get(f"MODEL_{model_name}")
        if entry is None:
            return False
        entry.status = status
        return True

    def count(self) -> int:
        return len(self._models)

    def swap_model(self, model_name: str, new_version: str) -> bool:
        entry = self._models.get(f"MODEL_{model_name}")
        if entry is None:
            return False
        entry.version = new_version
        return True


class PromptRegistry:
    def __init__(self):
        self._prompts: dict[str, list[RegistryEntry]] = {}

    def register_prompt(
        self,
        prompt_id: str,
        prompt_text: str,
        version: str = "1.0",
        author: str = "",
        approved: bool = False,
    ) -> RegistryEntry:
        if prompt_id not in self._prompts:
            self._prompts[prompt_id] = []
        entry = RegistryEntry(
            entry_id=f"PROMPT_{prompt_id}_{version}",
            name=prompt_id,
            version=version,
            category="prompt",
            status="approved" if approved else "draft",
            metadata={
                "text": prompt_text,
                "author": author,
                "revision": len(self._prompts[prompt_id]),
            },
        )
        self._prompts[prompt_id].append(entry)
        return entry

    def get_version(self, prompt_id: str, version: str) -> RegistryEntry:
        for entry in self._prompts.get(prompt_id, []):
            if entry.version == version:
                return entry
        return RegistryEntry()

    def latest(self, prompt_id: str) -> RegistryEntry:
        versions = self._prompts.get(prompt_id, [])
        if not versions:
            return RegistryEntry()
        return versions[-1]

    def revision_history(self, prompt_id: str) -> list[RegistryEntry]:
        return list(self._prompts.get(prompt_id, []))

    def list_prompt_ids(self) -> list[str]:
        return list(self._prompts.keys())

    def count(self) -> int:
        return sum(len(v) for v in self._prompts.values())


class AssetRegistry:
    CATEGORIES = [
        "character", "prop", "background", "music", "voice",
        "effect", "animation", "subtitle", "thumbnail",
    ]

    def __init__(self):
        self._assets: dict[str, RegistryEntry] = {}
        self._counter = 0

    def register(self, name: str, category: str, metadata: dict | None = None) -> RegistryEntry | None:
        if category not in self.CATEGORIES:
            return None
        self._counter += 1
        entry = RegistryEntry(
            entry_id=f"ASSET_{self._counter}",
            name=name,
            version="1.0",
            category=category,
            status="active",
            metadata=metadata or {},
        )
        self._assets[entry.entry_id] = entry
        return entry

    def get(self, asset_id: str) -> RegistryEntry:
        return self._assets.get(asset_id, RegistryEntry())

    def by_category(self, category: str) -> list[RegistryEntry]:
        return [a for a in self._assets.values() if a.category == category]

    def all_assets(self) -> list[RegistryEntry]:
        return list(self._assets.values())

    def count(self) -> int:
        return len(self._assets)

    def list_categories(self) -> list[str]:
        return list(self.CATEGORIES)
