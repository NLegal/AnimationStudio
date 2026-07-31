from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class LearningItem:
    item_id: str = ""
    category: str = ""
    source: str = ""
    content: dict = field(default_factory=dict)
    created_at: str = ""
    weight: float = 1.0


class LearningLoop:
    def __init__(self):
        self._items: list[LearningItem] = []
        self._counter = 0

    def record(self, category: str, source: str, content: dict) -> LearningItem:
        self._counter += 1
        item = LearningItem(
            item_id=f"LEARN_{self._counter}",
            category=category,
            source=source,
            content=content,
            created_at=datetime.now().isoformat(),
        )
        self._items.append(item)
        return item

    def record_success(self, source: str, content: dict) -> LearningItem:
        return self.record("success", source, content)

    def record_failure(self, source: str, content: dict) -> LearningItem:
        return self.record("failure", source, content)

    def items(self) -> list[LearningItem]:
        return list(self._items)

    def by_category(self, category: str) -> list[LearningItem]:
        return [i for i in self._items if i.category == category]

    def success_rate(self) -> float:
        successes = len(self.by_category("success"))
        failures = len(self.by_category("failure"))
        total = successes + failures
        if total == 0:
            return 1.0
        return round(successes / total, 4)

    def top_sources(self, limit: int = 5) -> list[str]:
        from collections import Counter

        counter = Counter(i.source for i in self._items)
        return [source for source, _ in counter.most_common(limit)]

    def count(self) -> int:
        return len(self._items)

    def apply_feedback(self, prompt_id: str, weight_delta: float) -> bool:
        for item in self._items:
            if item.content.get("prompt_id") == prompt_id:
                item.weight = max(0.1, item.weight + weight_delta)
                return True
        return False
