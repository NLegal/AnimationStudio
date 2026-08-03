"""Audio Production System — ties the Phase 5 Audio Bible to the audio pipeline.

Given an episode's audio requirements, the AudioProductionSystem:

1. Resolves the narrator + character voice briefs.
2. Generates phoneme lip-sync tracks for every dialogue line (24 fps timing).
3. Resolves every song into a bible-conformant MusicBrief (structure, tempo,
   duration, prompt, negative prompt).
4. Assembles the full episode AudioPlan and validates it end-to-end.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from src.animation.lipsync import LipSyncEngine, LipSyncTrack
from src.story_engine import SongEngine

from .bible import AudioBible
from .models import MusicBrief, VoiceBrief
from .prompts import quality_checklist


@dataclass
class DialogueClip:
    speaker: str
    text: str
    emotion: str = "neutral"
    voice_brief: Optional[VoiceBrief] = None
    lip_sync: Optional[LipSyncTrack] = None
    validation: dict = field(default_factory=dict)


@dataclass
class SongEntry:
    placement: str
    category: str
    topic: str
    brief: Optional[MusicBrief] = None
    validation: dict = field(default_factory=dict)


@dataclass
class AudioPlan:
    episode_id: str
    title: str
    narration: Optional[VoiceBrief] = None
    dialogue: list[DialogueClip] = field(default_factory=list)
    songs: list[SongEntry] = field(default_factory=list)
    sfx: list[str] = field(default_factory=list)
    foley: list[str] = field(default_factory=list)
    ambience: list[str] = field(default_factory=list)
    mix_rules: list[str] = field(default_factory=list)
    master_rules: list[str] = field(default_factory=list)
    localization: list[str] = field(default_factory=list)
    quality_checks: list[str] = field(default_factory=list)
    passed: bool = True

    @property
    def total_dialogue_seconds(self) -> float:
        return sum(c.lip_sync.duration for c in self.dialogue if c.lip_sync)

    @property
    def total_song_seconds(self) -> int:
        return sum(s.brief.duration_seconds for s in self.songs if s.brief)


class AudioProductionSystem:
    _SONG_TYPE_TO_CATEGORY = {
        "alphabet": "Alphabet",
        "counting": "Numbers",
        "color": "Colors",
        "animal": "Animals",
        "dance": "Dance Songs",
        "lullaby": "Bedtime",
        "educational": "Interactive Learning",
        "transition": "Interactive Learning",
    }

    def __init__(self) -> None:
        self.bible = AudioBible()
        self.song_engine = SongEngine()
        self.lipsync = LipSyncEngine()

    # ------------------------------------------------------------------
    # Single resolutions
    # ------------------------------------------------------------------

    def resolve_music(
        self, category: str = "Alphabet", topic: str = "letters and letter sounds",
        duration_label: str = "Standard",
    ) -> MusicBrief:
        return self.bible.build_music_brief(category=category, topic=topic,
                                            duration_label=duration_label)

    def resolve_voice(self, character: str = "Narrator") -> VoiceBrief:
        return self.bible.build_voice_brief(character)

    def plan_song_with_engine(
        self, song_type: str, objective_name: str, main_character: str,
        duration_label: str = "Standard",
    ) -> SongEntry:
        """Plan a song using the story-engine SongEngine for placement/topic."""
        from src.story_engine import LearningObjective

        objective = LearningObjective(name=objective_name)
        placement = self.song_engine.plan_song(
            placement="middle", song_type=song_type,
            objective=objective, main_character=main_character,
        )
        category = self._SONG_TYPE_TO_CATEGORY.get(
            placement.song_type, placement.song_type.capitalize()
        )
        brief = self.resolve_music(
            category=category, topic=placement.topic, duration_label=duration_label,
        )
        validation = self.bible.validate_music_brief(brief)
        return SongEntry(
            placement=placement.position, category=category,
            topic=placement.topic, brief=brief, validation=validation,
        )

    # ------------------------------------------------------------------
    # Episode planning
    # ------------------------------------------------------------------

    def plan_episode(
        self,
        episode_id: str,
        title: str,
        dialogue_lines: list[tuple[str, str, str]] = None,
        songs: list[tuple[str, str, str]] = None,
        scene: str = "Sunny Garden Playground",
        narration: bool = True,
    ) -> AudioPlan:
        """Build a full episode AudioPlan.

        dialogue_lines: list of (speaker, text, emotion)
        songs:          list of (category, topic, duration_label)
        """
        dialogue_lines = dialogue_lines or []
        songs = songs or []

        narrator = self.resolve_voice("Narrator") if narration else None

        dialogue: list[DialogueClip] = []
        for speaker, text, emotion in dialogue_lines:
            voice = self.resolve_voice(speaker)
            duration = self.lipsync.estimate_duration(text, self.bible.speaking_rate_wps)
            track = self.lipsync.generate(text, duration)
            validation = self.bible.validate_dialogue(text)
            dialogue.append(DialogueClip(
                speaker=speaker, text=text, emotion=emotion,
                voice_brief=voice, lip_sync=track, validation=validation,
            ))

        song_entries: list[SongEntry] = []
        for category, topic, duration_label in songs:
            brief = self.resolve_music(category=category, topic=topic,
                                       duration_label=duration_label)
            validation = self.bible.validate_music_brief(brief)
            song_entries.append(SongEntry(
                placement="middle", category=category, topic=topic,
                brief=brief, validation=validation,
            ))

        sfx = self._pick_sfx(scene)
        foley = self._pick_foley(scene)
        ambience = self._pick_ambience(scene)

        plan = AudioPlan(
            episode_id=episode_id,
            title=title,
            narration=narrator,
            dialogue=dialogue,
            songs=song_entries,
            sfx=sfx,
            foley=foley,
            ambience=ambience,
            mix_rules=[m.standard for m in self.bible.mixing_rules()],
            master_rules=[m.standard for m in self.bible.mastering_rules()],
            localization=list(self.bible.supported_languages),
            quality_checks=quality_checklist(),
            passed=True,
        )
        plan.passed = self.validate_episode(plan)["passed"]
        return plan

    def validate_episode(self, plan: AudioPlan) -> dict:
        violations: list[str] = []
        warnings: list[str] = []

        if not plan.dialogue and not plan.songs:
            violations.append("Episode must contain at least one song or dialogue line")

        for clip in plan.dialogue:
            if clip.validation.get("violations"):
                violations.extend(
                    f"{clip.speaker}: {v}" for v in clip.validation["violations"]
                )
            if clip.lip_sync is not None and not clip.lip_sync.phonemes and clip.text:
                warnings.append(f"{clip.speaker}: dialogue generated no phoneme track")
            if clip.voice_brief is None:
                warnings.append(f"{clip.speaker}: no approved voice profile")

        for entry in plan.songs:
            if entry.brief is None:
                violations.append(f"Song '{entry.category}' has no music brief")
            elif entry.validation.get("violations"):
                violations.extend(
                    f"{entry.category}: {v}" for v in entry.validation["violations"]
                )

        if plan.narration is None and not plan.dialogue:
            warnings.append("No narration and no dialogue — episode is silent")

        if "Dialogue always takes priority" not in plan.mix_rules:
            violations.append("Mix must include the dialogue-priority rule")

        passed = not violations
        return {
            "passed": passed,
            "violations": violations,
            "warnings": warnings,
        }

    # ------------------------------------------------------------------
    # Scene-based sound assignment
    # ------------------------------------------------------------------

    def _pick_sfx(self, scene: str) -> list[str]:
        scene = scene.lower()
        if "playground" in scene:
            return ["Footsteps", "Running", "Clapping", "Laughter", "Birds"]
        if "bedroom" in scene or "night" in scene or "sleep" in scene:
            return ["Bell", "Page Turn"]
        if "kitchen" in scene or "food" in scene:
            return ["Bubbles", "Piano", "Laughter"]
        if "beach" in scene or "ocean" in scene or "sea" in scene:
            return ["Water Splash", "Birds", "Bubbles"]
        if "forest" in scene or "garden" in scene or "nature" in scene:
            return ["Birds", "Wind", "Magic Sparkle"]
        if "farm" in scene:
            return ["Cow Moo", "Duck Quack", "Dog Bark"]
        if "school" in scene or "classroom" in scene:
            return ["School Bell", "Blocks", "Xylophone"]
        if "rain" in scene or "storm" in scene:
            return ["Rain", "Thunder (soft)"]
        return ["Birds", "Laughter"]

    def _pick_foley(self, scene: str) -> list[str]:
        scene = scene.lower()
        if "playground" in scene:
            return ["Toy pickup", "Toy drop", "Ball bounce", "Building blocks"]
        if "school" in scene or "library" in scene:
            return ["Book opening", "Book closing", "Pencil writing", "Paper crumple"]
        if "bedroom" in scene:
            return ["Chair movement", "Table tap", "Book opening"]
        if "kitchen" in scene:
            return ["Table tap", "Building blocks"]
        return ["Book opening", "Toy pickup", "Backpack zipper"]

    def _pick_ambience(self, scene: str) -> list[str]:
        scene = scene.lower()
        if "playground" in scene:
            return ["Playground"]
        if "bedroom" in scene or "sleep" in scene:
            return ["Bedroom", "Night"]
        if "beach" in scene or "ocean" in scene:
            return ["Beach"]
        if "forest" in scene or "garden" in scene or "nature" in scene:
            return ["Forest", "Morning Birds"]
        if "farm" in scene:
            return ["Farm"]
        if "school" in scene or "classroom" in scene:
            return ["School", "Library"]
        if "rain" in scene or "storm" in scene:
            return ["Rain"]
        if "snow" in scene or "winter" in scene:
            return ["Snow"]
        if "night" in scene:
            return ["Night"]
        return ["Morning Birds"]
