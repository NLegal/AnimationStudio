from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class IntroTemplate:
    studio_logo_duration: float = 2.0
    series_logo_duration: float = 1.5
    theme_music_duration: float = 5.0
    character_greeting_duration: float = 3.0
    episode_title_duration: float = 3.0
    total_duration: float = 0.0

    def __post_init__(self):
        self.total_duration = (
            self.studio_logo_duration
            + self.series_logo_duration
            + self.theme_music_duration
            + self.character_greeting_duration
            + self.episode_title_duration
        )


@dataclass
class OutroTemplate:
    lesson_recap_duration: float = 4.0
    goodbye_duration: float = 2.0
    subscribe_reminder_duration: float = 2.0
    next_episode_teaser_duration: float = 3.0
    studio_logo_duration: float = 2.0
    end_screen_duration: float = 5.0
    total_duration: float = 0.0

    def __post_init__(self):
        self.total_duration = (
            self.lesson_recap_duration
            + self.goodbye_duration
            + self.subscribe_reminder_duration
            + self.next_episode_teaser_duration
            + self.studio_logo_duration
            + self.end_screen_duration
        )


class IntroOutroEngine:
    DEFAULT_INTRO = IntroTemplate()
    DEFAULT_OUTRO = OutroTemplate()

    def create_intro(
        self,
        episode_title: str = "",
        studio_name: str = "AI Nursery Studio",
        **overrides,
    ) -> IntroTemplate:
        params = {
            k: overrides.get(k, getattr(self.DEFAULT_INTRO, k))
            for k in ["studio_logo_duration", "series_logo_duration",
                       "theme_music_duration", "character_greeting_duration",
                       "episode_title_duration"]
        }
        return IntroTemplate(**params)

    def create_outro(
        self,
        next_episode: str = "",
        **overrides,
    ) -> OutroTemplate:
        params = {
            k: overrides.get(k, getattr(self.DEFAULT_OUTRO, k))
            for k in ["lesson_recap_duration", "goodbye_duration",
                       "subscribe_reminder_duration", "next_episode_teaser_duration",
                       "studio_logo_duration", "end_screen_duration"]
        }
        return OutroTemplate(**params)

    def end_screen_templates(self) -> dict[str, dict]:
        return {
            "youtube_end_screen": {
                "elements": ["suggested_video", "playlist", "subscribe", "channel_logo"],
                "layout": "grid_4",
            },
            "basic_end_screen": {
                "elements": ["subscribe", "channel_logo"],
                "layout": "simple_2",
            },
        }
