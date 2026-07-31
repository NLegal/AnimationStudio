from __future__ import annotations
from datetime import datetime

from .models import (
    PublicationRecord, PublishStatus, Visibility,
)
from .metadata import MetadataEngine, TitleGenerator, DescriptionEngine, KeywordEngine


class PublishingEngine:
    def __init__(self):
        self._records: dict[str, PublicationRecord] = {}
        self._counter = 0
        self.metadata = MetadataEngine()
        self.titles = TitleGenerator()
        self.descriptions = DescriptionEngine()
        self.keywords = KeywordEngine()

    def create_record(
        self,
        episode_id: str,
        channel_id: str,
        platform: str = "youtube",
        title: str = "",
    ) -> PublicationRecord:
        self._counter += 1
        record = PublicationRecord(
            record_id=f"PUB_{self._counter}",
            episode_id=episode_id,
            channel_id=channel_id,
            platform=platform,
            status=PublishStatus.DRAFT,
            title=title,
        )
        self._records[record.record_id] = record
        return record

    def get(self, record_id: str) -> PublicationRecord:
        return self._records.get(record_id, PublicationRecord())

    def records_for_episode(self, episode_id: str) -> list[PublicationRecord]:
        return [r for r in self._records.values() if r.episode_id == episode_id]

    def approve(self, record_id: str) -> bool:
        record = self._records.get(record_id)
        if record is None:
            return False
        record.status = PublishStatus.APPROVED
        return True

    def schedule(self, record_id: str, scheduled_at: str) -> bool:
        record = self._records.get(record_id)
        if record is None:
            return False
        record.scheduled_at = scheduled_at
        record.status = PublishStatus.SCHEDULED
        return True

    def publish(self, record_id: str, video_url: str = "") -> bool:
        record = self._records.get(record_id)
        if record is None:
            return False
        if record.status not in (PublishStatus.APPROVED, PublishStatus.SCHEDULED):
            return False
        record.status = PublishStatus.PUBLISHED
        record.published_at = datetime.now().isoformat()
        record.video_url = video_url
        return True

    def update(self, record_id: str) -> bool:
        record = self._records.get(record_id)
        if record is None:
            return False
        if record.status != PublishStatus.PUBLISHED:
            return False
        record.status = PublishStatus.UPDATED
        record.version += 1
        return True

    def archive(self, record_id: str) -> bool:
        record = self._records.get(record_id)
        if record is None:
            return False
        record.status = PublishStatus.ARCHIVED
        return True

    def set_visibility(self, record_id: str, visibility: Visibility) -> bool:
        record = self._records.get(record_id)
        if record is None:
            return False
        record.visibility = visibility
        return True

    def prepare_publish_package(
        self,
        episode_id: str,
        topic: str,
        character: str,
        objective: str,
        series: str,
        age_group: str = "2-5",
        keywords: list[str] | None = None,
    ) -> dict:
        titles = self.titles.generate_titles(topic, character, age_group, objective)
        best = self.titles.select_best(titles)
        metadata = self.metadata.generate(
            episode_id=episode_id,
            title=best.title,
            series=series,
            learning_objective=objective,
            age_group=age_group,
            characters=[character],
            curriculum_tags=[topic],
            keywords=keywords,
        )
        description = self.descriptions.build_description(
            summary=f"Join {character} to {objective.lower()} in {series}!",
            objective=objective,
            age_group=age_group,
            series=series,
        )
        return {
            "episode_id": episode_id,
            "titles": [{"kind": t.kind, "title": t.title, "score": t.score} for t in titles],
            "selected_title": best.title,
            "metadata": metadata,
            "description": description,
        }
