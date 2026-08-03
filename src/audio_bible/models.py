"""Data models for the Phase 5 Audio Bible & Music Production System.

These frozen dataclasses encode the quantitative and qualitative standards
from the `Audio/` markdown bibles so the audio pipeline can query them
programmatically instead of hard-coding BPM ranges, durations, and rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Songs
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SongCategory:
    name: str
    description: str
    prompt_keyword: str
    use: str


@dataclass(frozen=True)
class SongSection:
    name: str
    position: int
    purpose: str
    optional: bool = False


@dataclass(frozen=True)
class SongDuration:
    label: str
    seconds: int
    use: str


@dataclass(frozen=True)
class MusicStyle:
    tempo_min: int
    tempo_max: int
    moods: tuple[str, ...]
    keys: tuple[str, ...]
    melody: str
    arrangement: str
    instrumentation: tuple[str, ...]
    vocals: tuple[str, ...]


# ---------------------------------------------------------------------------
# Voices / dialogue
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class VoiceProfile:
    character: str
    age: str
    pitch: str
    energy: str
    speech_speed: str
    accent: str
    laugh_style: str
    singing_style: str
    favorite_expressions: tuple[str, ...]
    tts_engine: str = "XTTS v2"
    role: str = "character"
    notes: str = ""


@dataclass(frozen=True)
class DialogueRule:
    rule: str
    standard: str
    notes: str = ""


@dataclass(frozen=True)
class PronunciationEntry:
    word: str
    phonetic: str
    notes: str = ""
    language: str = "English"


# ---------------------------------------------------------------------------
# Sound libraries
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SoundEffect:
    name: str
    description: str
    notes: str = ""


@dataclass(frozen=True)
class FoleySound:
    name: str
    description: str
    notes: str = ""


@dataclass(frozen=True)
class AmbientSound:
    name: str
    description: str
    level: str = "Low"


# ---------------------------------------------------------------------------
# Mix / master / lipsync / localization standards
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MixingRule:
    rule: str
    standard: str


@dataclass(frozen=True)
class MasteringRule:
    rule: str
    standard: str


@dataclass(frozen=True)
class LipSyncStandard:
    rule: str
    standard: str


@dataclass(frozen=True)
class LocalizationStandard:
    rule: str
    standard: str


# ---------------------------------------------------------------------------
# Resolved briefs
# ---------------------------------------------------------------------------

@dataclass
class MusicBrief:
    category: str
    topic: str
    structure: tuple[str, ...]
    duration_label: str
    duration_seconds: int
    tempo: int
    mood: str
    key: str
    vocals: str
    instrumentation: tuple[str, ...]
    style_notes: str
    prompt: str
    negative_prompt: str
    quality_checks: list[str] = field(default_factory=list)
    stems: bool = True
    lipsync_note: str = ""
    localization_note: str = ""

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "topic": self.topic,
            "structure": list(self.structure),
            "duration_label": self.duration_label,
            "duration_seconds": self.duration_seconds,
            "tempo": self.tempo,
            "mood": self.mood,
            "key": self.key,
            "vocals": self.vocals,
            "instrumentation": list(self.instrumentation),
            "style_notes": self.style_notes,
            "stems": self.stems,
        }


@dataclass
class VoiceBrief:
    character: str
    role: str
    age: str
    pitch: str
    energy: str
    speech_speed: str
    accent: str
    laugh_style: str
    singing_style: str
    tts_engine: str
    prompt: str
    negative_prompt: str
    quality_checks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "character": self.character,
            "role": self.role,
            "age": self.age,
            "pitch": self.pitch,
            "energy": self.energy,
            "speech_speed": self.speech_speed,
            "accent": self.accent,
            "laugh_style": self.laugh_style,
            "singing_style": self.singing_style,
            "tts_engine": self.tts_engine,
        }


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
    facts: list[DocFact] = field(default_factory=list)
    missing_files: list[str] = field(default_factory=list)

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
