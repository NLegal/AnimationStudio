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
        test.winner = winner
        return test


class EducationalAnalyticsEngine:
    """Educational design metrics correlated with audience engagement."""

    def __init__(self):
        self._records: list[dict] = []

    def record(
        self,
        episode_id: str,
        learning_topic: str,
        target_age: str = "2-5",
        episode_length: float = 0.0,
        song_count: int = 0,
        question_count: int = 0,
        interactive_moments: int = 0,
        completion_rate: float = 0.0,
        replay_rate: float = 0.0,
    ) -> dict:
        record = {
            "episode_id": episode_id,
            "learning_topic": learning_topic,
            "target_age": target_age,
            "episode_length": episode_length,
            "song_count": song_count,
            "question_count": question_count,
            "interactive_moments": interactive_moments,
            "completion_rate": completion_rate,
            "replay_rate": replay_rate,
        }
        self._records.append(record)
        return record

    def for_episode(self, episode_id: str) -> dict:
        for record in reversed(self._records):
            if record["episode_id"] == episode_id:
                return record
        return {}

    def topic_performance(self, learning_topic: str) -> dict:
        topic_records = [r for r in self._records if r["learning_topic"] == learning_topic]
        if not topic_records:
            return {"learning_topic": learning_topic, "episode_count": 0}
        return {
            "learning_topic": learning_topic,
            "episode_count": len(topic_records),
            "average_completion_rate": round(
                sum(r["completion_rate"] for r in topic_records) / len(topic_records), 4
            ),
            "average_replay_rate": round(
                sum(r["replay_rate"] for r in topic_records) / len(topic_records), 4
            ),
            "total_songs": sum(r["song_count"] for r in topic_records),
            "total_questions": sum(r["question_count"] for r in topic_records),
        }

    def list_topics(self) -> list[str]:
        topics: list[str] = []
        for r in self._records:
            if r["learning_topic"] not in topics:
                topics.append(r["learning_topic"])
        return topics

    def popular_topics(self, limit: int = 5) -> list[dict]:
        ranked = sorted(
            (self.topic_performance(t) for t in self.list_topics()),
            key=lambda t: t["episode_count"],
            reverse=True,
        )
        return ranked[:limit]

    def count(self) -> int:
        return len(self._records)
