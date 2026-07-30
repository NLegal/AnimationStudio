from __future__ import annotations
from typing import Dict, List, Optional

from src.story_engine.models import ContinuityRecord, EpisodeBlueprint


class ContinuityTracker:
    def __init__(self):
        self._records: Dict[str, ContinuityRecord] = {}

    def record_episode(self, blueprint: EpisodeBlueprint) -> None:
        for char_id in [blueprint.main_character] + blueprint.supporting_characters:
            if char_id not in self._records:
                self._records[char_id] = ContinuityRecord(
                    character_id=char_id,
                    last_episode_id=blueprint.episode_id,
                    last_location=blueprint.location,
                    last_mood="happy",
                    episodes_appeared=0,
                )
            record = self._records[char_id]
            record.last_episode_id = blueprint.episode_id
            record.last_location = blueprint.location
            record.episodes_appeared += 1

    def get_last_location(self, char_id: str) -> Optional[str]:
        record = self._records.get(char_id)
        if record:
            return record.last_location
        return None

    def get_episode_count(self, char_id: str) -> int:
        record = self._records.get(char_id)
        if record:
            return record.episodes_appeared
        return 0

    def check_consistency(self, blueprint: EpisodeBlueprint) -> List[str]:
        issues: List[str] = []
        for char_id in [blueprint.main_character] + blueprint.supporting_characters:
            record = self._records.get(char_id)
            if record and record.last_location:
                if record.last_location != blueprint.location and record.episodes_appeared > 0:
                    issues.append(
                        f"Continuity: '{char_id}' was at '{record.last_location}' "
                        f"in episode '{record.last_episode_id}' but is now at '{blueprint.location}'"
                    )
        return issues

    def get_record(self, char_id: str) -> Optional[ContinuityRecord]:
        return self._records.get(char_id)
