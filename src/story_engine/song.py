from __future__ import annotations
import random
from typing import Dict, List, Optional

from src.story_engine.models import LearningObjective, SongPlacement


class SongEngine:
    def __init__(self):
        self._placements = [
            "opening",
            "middle",
            "ending",
            "transition",
            "full_episode",
        ]
        self._song_types = [
            "educational",
            "dance",
            "lullaby",
            "alphabet",
            "counting",
            "color",
            "animal",
            "transition",
        ]
        self._default_duration: Dict[str, int] = {
            "opening": 45,
            "middle": 60,
            "ending": 50,
            "transition": 30,
            "full_episode": 120,
        }
        self._type_duration: Dict[str, int] = {
            "educational": 60,
            "dance": 50,
            "lullaby": 90,
            "alphabet": 55,
            "counting": 50,
            "color": 45,
            "animal": 45,
            "transition": 30,
        }
        self._objective_song_map: Dict[str, List[str]] = {
            "counting": ["counting", "educational", "dance"],
            "numbers": ["counting", "educational"],
            "colors": ["color", "educational", "dance"],
            "color": ["color", "educational"],
            "shapes": ["educational", "dance"],
            "shape": ["educational", "dance"],
            "alphabet": ["alphabet", "educational"],
            "letters": ["alphabet", "educational"],
            "animals": ["animal", "educational", "dance"],
            "animal": ["animal", "educational"],
            "phonics": ["alphabet", "educational"],
            "dance": ["dance", "educational"],
            "music": ["dance", "educational"],
            "bedtime": ["lullaby", "educational"],
            "sleep": ["lullaby"],
            "friendship": ["educational", "dance"],
            "emotions": ["educational", "lullaby"],
            "weather": ["educational", "transition"],
            "seasons": ["educational", "dance"],
            "ocean": ["animal", "educational"],
            "farm": ["animal", "educational"],
            "space": ["educational", "dance"],
            "transportation": ["educational", "transition"],
        }
        self._song_topics: Dict[str, List[str]] = {
            "counting": [
                "counting numbers",
                "counting animals",
                "counting stars",
                "counting toys",
            ],
            "color": [
                "learning colors",
                "color mixing",
                "colors in nature",
                "rainbow colors",
            ],
            "alphabet": [
                "ABC song",
                "letter sounds",
                "vowel song",
                "consonant song",
            ],
            "animal": [
                "animal sounds",
                "animal parade",
                "animal dance",
                "animal friends",
            ],
            "educational": [
                "learning fun",
                "discovery song",
                "wonder world",
                "curiosity song",
            ],
            "dance": [
                "dance together",
                "wiggle and move",
                "happy dance",
                "jump and clap",
            ],
            "lullaby": [
                "gentle dreams",
                "star light",
                "soft sleep",
                "peaceful night",
            ],
            "transition": [
                "moving along",
                "next adventure",
                "change is fun",
                "on we go",
            ],
        }

    def should_include_song(self, themes_require_song: bool = False) -> bool:
        if themes_require_song:
            return True
        return random.random() < 0.6

    def select_placement(self, structure_length: int) -> str:
        if structure_length <= 3:
            return "ending"
        if structure_length <= 5:
            return random.choice(["middle", "ending"])
        if structure_length >= 8:
            return random.choice(
                ["opening", "middle", "ending", "transition", "full_episode"]
            )
        return random.choice(["opening", "middle", "ending", "transition"])

    def select_song_type(self, objective: LearningObjective) -> str:
        kw = objective.name.lower() if objective.name else ""
        curriculum = objective.curriculum_area.lower() if objective.curriculum_area else ""
        candidates: List[str] = []
        if kw in self._objective_song_map:
            candidates = self._objective_song_map[kw]
        elif curriculum in self._objective_song_map:
            candidates = self._objective_song_map[curriculum]
        for key, types in self._objective_song_map.items():
            if key in kw or key in curriculum:
                candidates = types
                break
        if not candidates:
            candidates = ["educational"]
        return random.choice(candidates)

    def plan_song(
        self,
        placement: str,
        song_type: str,
        objective: LearningObjective,
        main_character: str,
    ) -> SongPlacement:
        duration = self._type_duration.get(song_type, 60)
        if placement in self._default_duration:
            duration = max(duration, self._default_duration[placement])
        topic_list = self._song_topics.get(song_type, ["fun song"])
        topic = f"{main_character} {random.choice(topic_list)}"
        return SongPlacement(
            position=placement,
            song_type=song_type,
            topic=topic,
            duration_seconds=duration,
        )

    def get_song_themes_for_objective(self, objective_id: str) -> List[str]:
        oid = objective_id.lower()
        for key, types in self._objective_song_map.items():
            if key in oid:
                return types[:]
        return ["educational"]


class SongThemeLibrary:
    def __init__(self):
        self.theme_songs: Dict[str, List[dict]] = {
            "birthday": [
                {"type": "dance", "topic": "birthday dance"},
                {"type": "counting", "topic": "counting candles"},
            ],
            "bedtime": [
                {"type": "lullaby", "topic": "sleepy time"},
                {"type": "educational", "topic": "night time learning"},
            ],
            "zoo": [
                {"type": "animal", "topic": "zoo animal parade"},
                {"type": "dance", "topic": "animal dance"},
            ],
            "beach": [
                {"type": "educational", "topic": "ocean discovery"},
                {"type": "transition", "topic": "waves and sand"},
            ],
            "space": [
                {"type": "educational", "topic": "space adventure"},
                {"type": "counting", "topic": "counting stars"},
            ],
        }

    def get_songs_for_theme(self, theme_id: str) -> List[dict]:
        return self.theme_songs.get(theme_id.lower(), [])
