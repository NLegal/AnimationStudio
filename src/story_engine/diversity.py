from __future__ import annotations
from typing import Dict, List

from src.story_engine.models import DiversityTracker, EpisodeBlueprint


class DiversityEngine:
    def __init__(self):
        self.tracker = DiversityTracker()

    def check_diversity(self, blueprint: EpisodeBlueprint) -> List[str]:
        return self.tracker.would_be_repetitive(blueprint)

    def suggest_alternative(self, blueprint: EpisodeBlueprint) -> Dict:
        suggestions: Dict = {}

        if self.tracker.location_usage.get(blueprint.location, 0) > 1:
            all_locations = list(self.tracker.location_usage.keys()) + (
                ["Playground", "Park", "Classroom", "Garden", "Home"]
            )
            least_used = self.tracker.get_least_used_location(all_locations)
            if least_used != blueprint.location:
                suggestions["location"] = least_used

        if self.tracker.character_usage.get(blueprint.main_character, 0) > 2:
            all_chars = list(self.tracker.character_usage.keys()) + (
                ["lily-bunny", "ben-bear", "daisy-duck", "molly-cat", "max-puppy"]
            )
            least_used = self.tracker.get_least_used_character(all_chars)
            if least_used != blueprint.main_character:
                suggestions["main_character"] = least_used

        if self.tracker.theme_usage.get(blueprint.theme, 0) > 1:
            all_themes = list(self.tracker.theme_usage.keys()) + [
                "park-visit", "birthday", "cooking", "gardening", "beach",
            ]
            least_used = min(
                all_themes,
                key=lambda t: self.tracker.theme_usage.get(t, 0),
            )
            if least_used != blueprint.theme:
                suggestions["theme"] = least_used

        if self.tracker.lesson_usage.get(blueprint.learning_objective, 0) > 1:
            all_lessons = list(self.tracker.lesson_usage.keys()) + [
                "Count to 5", "Recognize Blue", "Identify Circle", "Name Farm Animals",
            ]
            least_used = min(
                all_lessons,
                key=lambda l: self.tracker.lesson_usage.get(l, 0),
            )
            if least_used != blueprint.learning_objective:
                suggestions["learning_objective"] = least_used

        return suggestions

    def get_usage_summary(self) -> Dict:
        return {
            "location_usage": dict(self.tracker.location_usage),
            "character_usage": dict(self.tracker.character_usage),
            "theme_usage": dict(self.tracker.theme_usage),
            "lesson_usage": dict(self.tracker.lesson_usage),
            "recent_locations": list(self.tracker.recent_locations),
            "recent_characters": list(self.tracker.recent_characters),
            "recent_themes": list(self.tracker.recent_themes),
            "recent_lessons": list(self.tracker.recent_lessons),
        }
