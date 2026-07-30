from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class MetricSnapshot:
    timestamp: str = ""
    render_time_seconds: float = 0.0
    gpu_utilization: float = 0.0
    failed_generations: int = 0
    character_consistency_score: float = 0.0
    animation_quality_score: float = 0.0
    scene_completion_rate: float = 0.0
    cost_per_minute: float = 0.0
    render_retries: int = 0


class AnimationMonitor:
    def __init__(self):
        self._snapshots: list[MetricSnapshot] = []
        self._total_renders = 0
        self._failed_renders = 0
        self._total_retries = 0

    def record_render(self, duration: float, success: bool) -> None:
        self._total_renders += 1
        if not success:
            self._failed_renders += 1

    def record_retry(self) -> None:
        self._total_retries += 1

    def snapshot(
        self,
        gpu_utilization: float = 0.0,
        character_score: float = 0.0,
        quality_score: float = 0.0,
        cost_per_min: float = 0.0,
    ) -> MetricSnapshot:
        snap = MetricSnapshot(
            timestamp=datetime.now().isoformat(),
            render_time_seconds=self.average_render_time(),
            gpu_utilization=gpu_utilization,
            failed_generations=self._failed_renders,
            character_consistency_score=character_score,
            animation_quality_score=quality_score,
            scene_completion_rate=self.completion_rate(),
            cost_per_minute=cost_per_min,
            render_retries=self._total_retries,
        )
        self._snapshots.append(snap)
        return snap

    def average_render_time(self) -> float:
        if not self._snapshots:
            return 0.0
        total = sum(s.render_time_seconds for s in self._snapshots)
        return round(total / len(self._snapshots), 2)

    def completion_rate(self) -> float:
        if self._total_renders == 0:
            return 1.0
        success = self._total_renders - self._failed_renders
        return round(success / self._total_renders, 3)

    def total_renders(self) -> int:
        return self._total_renders

    def failed_renders(self) -> int:
        return self._failed_renders

    def retry_count(self) -> int:
        return self._total_retries

    def history(self) -> list[MetricSnapshot]:
        return list(self._snapshots)

    def latest(self) -> Optional[MetricSnapshot]:
        return self._snapshots[-1] if self._snapshots else None

    def clear(self) -> None:
        self._snapshots.clear()
        self._total_renders = 0
        self._failed_renders = 0
        self._total_retries = 0
