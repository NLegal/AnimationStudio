from __future__ import annotations
from datetime import datetime

from .models import AnalyticsSnapshot, PublicationRecord


class PublishingArchiveEngine:
    def __init__(self):
        self._records: list[dict] = []

    def store(
        self,
        publication: PublicationRecord,
        analytics: AnalyticsSnapshot | None = None,
        extra_metadata: dict | None = None,
        subtitles: list[str] | None = None,
    ) -> dict:
        entry = {
            "record_id": publication.record_id,
            "episode_id": publication.episode_id,
            "channel_id": publication.channel_id,
            "platform": publication.platform,
            "status": publication.status.value,
            "title": publication.title,
            "description": publication.description,
            "tags": list(publication.tags),
            "thumbnail": publication.thumbnail,
            "subtitles": list(subtitles or []),
            "published_at": publication.published_at,
            "version": publication.version,
            "archived_at": datetime.now().isoformat(),
            "analytics": {
                "views": analytics.views if analytics else 0,
                "ctr": analytics.ctr if analytics else 0.0,
                "retention": analytics.audience_retention if analytics else 0.0,
            } if analytics else None,
            "extra": extra_metadata or {},
        }
        self._records.append(entry)
        return entry

    def history_for(self, episode_id: str) -> list[dict]:
        return [r for r in self._records if r["episode_id"] == episode_id]

    def all_archives(self) -> list[dict]:
        return list(self._records)

    def count(self) -> int:
        return len(self._records)

    def list_episode_ids(self) -> list[str]:
        episode_ids: list[str] = []
        for record in self._records:
            if record["episode_id"] not in episode_ids:
                episode_ids.append(record["episode_id"])
        return episode_ids
