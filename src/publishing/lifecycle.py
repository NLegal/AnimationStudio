from __future__ import annotations
from datetime import datetime


class LifecycleManager:
    STAGES = [
        "concept",
        "production",
        "editing",
        "approved",
        "scheduled",
        "published",
        "localized",
        "optimized",
        "archived",
    ]

    def __init__(self):
        self._lifecycles: dict[str, dict] = {}

    def start(self, episode_id: str) -> dict:
        lifecycle = {
            "episode_id": episode_id,
            "stage": "concept",
            "history": [
                {"stage": "concept", "timestamp": datetime.now().isoformat()},
            ],
        }
        self._lifecycles[episode_id] = lifecycle
        return lifecycle

    def advance(self, episode_id: str, to_stage: str) -> bool:
        lifecycle = self._lifecycles.get(episode_id)
        if lifecycle is None:
            return False
        if to_stage not in self.STAGES:
            return False
        current_index = self.STAGES.index(lifecycle["stage"])
        target_index = self.STAGES.index(to_stage)
        if target_index <= current_index:
            return False
        lifecycle["stage"] = to_stage
        lifecycle["history"].append({"stage": to_stage, "timestamp": datetime.now().isoformat()})
        return True

    def get_stage(self, episode_id: str) -> str:
        lifecycle = self._lifecycles.get(episode_id)
        if lifecycle is None:
            return ""
        return lifecycle["stage"]

    def get_lifecycle(self, episode_id: str) -> dict:
        return self._lifecycles.get(episode_id, {})

    def list_all(self) -> list[dict]:
        return list(self._lifecycles.values())

    def count(self) -> int:
        return len(self._lifecycles)

    def list_by_stage(self, stage: str) -> list[dict]:
        return [l for l in self._lifecycles.values() if l["stage"] == stage]
