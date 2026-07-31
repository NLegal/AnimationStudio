from __future__ import annotations
from datetime import datetime

from .models import AnalyticsSnapshot, ABTest


class AnalyticsEngine:
    def __init__(self):
        self._snapshots: list[AnalyticsSnapshot] = []
        self._tests: dict[str, ABTest] = {}
        self._counter = 0

    def record(self, snapshot: AnalyticsSnapshot) -> AnalyticsSnapshot:
        snapshot.timestamp = snapshot.timestamp or datetime.now().isoformat()
        self._snapshots.append(snapshot)
        return snapshot

    def snapshots_for(self, episode_id: str) -> list[AnalyticsSnapshot]:
        return [s for s in self._snapshots if s.episode_id == episode_id]

    def latest_for(self, episode_id: str) -> AnalyticsSnapshot | None:
        snapshots = self.snapshots_for(episode_id)
        if not snapshots:
            return None
        return max(snapshots, key=lambda s: s.timestamp)

    def total_views(self) -> int:
        return sum(s.views for s in self._snapshots)

    def average_retention(self) -> float:
        if not self._snapshots:
            return 0.0
        return round(
            sum(s.audience_retention for s in self._snapshots) / len(self._snapshots),
            4,
        )

    def average_ctr(self) -> float:
        if not self._snapshots:
            return 0.0
        return round(sum(s.ctr for s in self._snapshots) / len(self._snapshots), 4)

    def top_episodes(self, limit: int = 5) -> list[AnalyticsSnapshot]:
        by_episode: dict[str, AnalyticsSnapshot] = {}
        for s in self._snapshots:
            if s.episode_id not in by_episode or s.timestamp >= by_episode[s.episode_id].timestamp:
                by_episode[s.episode_id] = s
        ranked = sorted(by_episode.values(), key=lambda s: s.views, reverse=True)
        return ranked[:limit]

    def educational_metrics(self, episode_attributes: dict[str, dict]) -> dict:
        report: dict[str, dict] = {}
        for episode_id, attrs in episode_attributes.items():
            snapshots = self.snapshots_for(episode_id)
            if not snapshots:
                continue
            latest = max(snapshots, key=lambda s: s.timestamp)
            report[episode_id] = {
                **attrs,
                "views": latest.views,
                "completion_rate": latest.audience_retention,
                "replay_estimate": round(latest.engagement_rate, 4),
            }
        return report

    def create_ab_test(
        self,
        episode_id: str,
        attribute: str,
        variant_a: str,
        variant_b: str,
        metric: str = "ctr",
    ) -> ABTest:
        self._counter += 1
        test = ABTest(
            test_id=f"AB_{self._counter}",
            episode_id=episode_id,
            attribute=attribute,
            variant_a=variant_a,
            variant_b=variant_b,
            metric=metric,
        )
        self._tests[test.test_id] = test
        return test

    def list_ab_tests(self) -> list[ABTest]:
        return list(self._tests.values())

    def get_ab_test(self, test_id: str) -> ABTest:
        return self._tests.get(test_id, ABTest())

    def conclude_ab_test(self, test_id: str, winner: str) -> ABTest:
        test = self._tests.get(test_id)
        if test is None:
            return ABTest()
        test.status = "concluded"
        test.variant_a = test.variant_a if winner == "a" else test.variant_a
        return test
