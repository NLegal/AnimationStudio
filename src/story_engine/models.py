from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set


@dataclass
class CurriculumArea:
    id: str = ""
    name: str = ""
    description: str = ""
    age_range: str = "2-5"
    topics: List[str] = field(default_factory=list)


@dataclass
class LearningObjective:
    id: str = ""
    curriculum_area: str = ""
    name: str = ""
    description: str = ""
    difficulty: int = 1
    age_range: str = "2-5"
    keywords: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)


@dataclass
class Theme:
    id: str = ""
    name: str = ""
    description: str = ""
    season: Optional[str] = None
    holiday: Optional[str] = None
    requires_song: bool = False
    suggested_assets: List[str] = field(default_factory=list)
    suggested_locations: List[str] = field(default_factory=list)


@dataclass
class StoryGrammar:
    id: str = ""
    name: str = ""
    description: str = ""
    structure: List[str] = field(default_factory=list)
    conflict_types: List[str] = field(default_factory=list)
    resolution_types: List[str] = field(default_factory=list)


@dataclass
class CharacterInfo:
    character_id: str = ""
    name: str = ""
    role: str = "student"
    age_group: str = "child"
    personality: List[str] = field(default_factory=list)
    catchphrases: List[str] = field(default_factory=list)
    favorite_things: List[str] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)
    home: str = ""
    preferred_locations: List[str] = field(default_factory=list)


@dataclass
class DialogueLine:
    speaker: str = ""
    text: str = ""
    emotion: str = "neutral"
    interaction: bool = False
    pause_after: float = 0.5


@dataclass
class InteractiveMoment:
    prompt: str = ""
    expected_reaction: str = ""
    pause_duration: float = 2.0
    moment_type: str = "question"


@dataclass
class SongPlacement:
    position: str = ""  # opening, middle, ending, transition
    song_type: str = ""  # educational, dance, lullaby
    topic: str = ""
    duration_seconds: int = 60


@dataclass
class EpisodeBlueprint:
    episode_id: str = ""
    season: int = 1
    episode_number: int = 1
    title: str = ""
    subtitle: str = ""
    curriculum_area: str = ""
    learning_objective: str = ""
    theme: str = ""
    target_age: str = "2-5"
    difficulty: int = 1
    duration_minutes: int = 3
    has_song: bool = False
    song: Optional[SongPlacement] = None
    main_character: str = ""
    supporting_characters: List[str] = field(default_factory=list)
    location: str = ""
    weather: str = "clear"
    season_name: str = "spring"
    holiday: Optional[str] = None
    assets: List[str] = field(default_factory=list)
    story_grammar: str = ""
    narrative_structure: List[str] = field(default_factory=list)
    conflict: str = ""
    resolution: str = ""
    dialogue: List[DialogueLine] = field(default_factory=list)
    interactive_moments: List[InteractiveMoment] = field(default_factory=list)
    emotional_arc: List[str] = field(default_factory=list)
    humor_moments: List[str] = field(default_factory=list)
    reinforcement_count: int = 3
    vocabulary_level: str = "simple"
    keywords: List[str] = field(default_factory=list)
    curriculum_tags: List[str] = field(default_factory=list)
    language: str = "en"

    def validate(self) -> List[str]:
        issues = []
        if not self.learning_objective:
            issues.append("Missing learning objective")
        if not self.main_character:
            issues.append("Missing main character")
        if not self.location:
            issues.append("Missing location")
        if not self.conflict:
            issues.append("Missing conflict")
        if not self.resolution:
            issues.append("Missing resolution")
        return issues


@dataclass
class SeasonPlan:
    season_number: int = 1
    title: str = ""
    description: str = ""
    episodes: List[EpisodeBlueprint] = field(default_factory=list)
    curriculum_focus: List[str] = field(default_factory=list)


@dataclass
class SeriesPlan:
    title: str = "Little Learning Town"
    seasons: List[SeasonPlan] = field(default_factory=list)


@dataclass
class ContinuityRecord:
    character_id: str = ""
    last_episode_id: str = ""
    last_location: str = ""
    last_mood: str = "happy"
    episodes_appeared: int = 0
    relationships_used: Set[str] = field(default_factory=set)


@dataclass
class DiversityTracker:
    recent_locations: List[str] = field(default_factory=list)
    recent_characters: List[str] = field(default_factory=list)
    recent_themes: List[str] = field(default_factory=list)
    recent_lessons: List[str] = field(default_factory=list)
    location_usage: Dict[str, int] = field(default_factory=dict)
    character_usage: Dict[str, int] = field(default_factory=dict)
    theme_usage: Dict[str, int] = field(default_factory=dict)
    lesson_usage: Dict[str, int] = field(default_factory=dict)
    max_recent: int = 5

    def would_be_repetitive(self, blueprint: EpisodeBlueprint) -> List[str]:
        warnings = []
        if blueprint.location in self.recent_locations:
            warnings.append(f"Location '{blueprint.location}' used recently")
        for c in [blueprint.main_character] + blueprint.supporting_characters:
            if c in self.recent_characters:
                warnings.append(f"Character '{c}' used recently")
        if blueprint.theme in self.recent_themes:
            warnings.append(f"Theme '{blueprint.theme}' used recently")
        if blueprint.learning_objective in self.recent_lessons:
            warnings.append(f"Lesson '{blueprint.learning_objective}' used recently")
        return warnings

    def record(self, blueprint: EpisodeBlueprint):
        self.recent_locations = self._push(self.recent_locations, blueprint.location)
        for c in [blueprint.main_character] + blueprint.supporting_characters:
            self.recent_characters = self._push(self.recent_characters, c)
        self.recent_themes = self._push(self.recent_themes, blueprint.theme)
        self.recent_lessons = self._push(self.recent_lessons, blueprint.learning_objective)

        self.location_usage[blueprint.location] = self.location_usage.get(blueprint.location, 0) + 1
        for c in [blueprint.main_character] + blueprint.supporting_characters:
            self.character_usage[c] = self.character_usage.get(c, 0) + 1
        self.theme_usage[blueprint.theme] = self.theme_usage.get(blueprint.theme, 0) + 1
        self.lesson_usage[blueprint.learning_objective] = self.lesson_usage.get(blueprint.learning_objective, 0) + 1

    def _push(self, lst: List[str], item: str) -> List[str]:
        lst = [x for x in lst if x != item]
        lst.append(item)
        if len(lst) > self.max_recent:
            lst = lst[-self.max_recent:]
        return lst

    def get_least_used_location(self, locations: List[str]) -> str:
        return min(locations, key=lambda l: self.location_usage.get(l, 0))

    def get_least_used_character(self, characters: List[str]) -> str:
        return min(characters, key=lambda c: self.character_usage.get(c, 0))


# ---------------------------------------------------------------------------
# Doc consistency check
# ---------------------------------------------------------------------------

@dataclass
class DocFact:
    file: str
    token: str
    expected: str
    found: bool = False
    detail: str = ""


@dataclass
class DocConsistencyReport:
    facts: List[DocFact] = field(default_factory=list)
    missing_files: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.missing_files and all(f.found for f in self.facts)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "facts_checked": len(self.facts),
            "facts_passed": sum(1 for f in self.facts if f.found),
            "facts_failed": [f.file + " -> " + f.token for f in self.facts if not f.found],
            "missing_files": self.missing_files,
        }
