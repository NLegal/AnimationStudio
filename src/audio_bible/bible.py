"""AudioBible — query facade for the Phase 5 Audio Bible.

Provides programmatic access to every standard defined in the `Audio/`
markdown bibles, plus bible-aware validation of audio plans and resolution
of a song/voice request into a concrete :class:`MusicBrief` / :class:`VoiceBrief`.
"""

from __future__ import annotations

import os
import re
from typing import Optional

from . import libraries as lib
from .models import (
    AmbientSound, DocConsistencyReport, DocFact, FoleySound, LipSyncStandard,
    LocalizationStandard, MasteringRule, MixingRule, MusicBrief,
    PronunciationEntry, SongCategory, SongDuration, SongSection, SoundEffect,
    VoiceBrief, VoiceProfile,
)
from .prompts import (
    AUDIO_NEGATIVE_BASE, category_negative, build_music_prompt,
    build_voice_prompt, quality_checklist,
)


class AudioBible:
    def __init__(self) -> None:
        self.tempo_range = lib.TEMP_RANGE
        self.master_loudness_lufs = lib.MASTER_LOUDNESS_LUFS
        self.true_peak_dbtp = lib.TRUE_PEAK_DBTP
        self.master_sample_rate = lib.MASTER_SAMPLE_RATE
        self.speaking_rate_wps = lib.SPEAKING_RATE_WPS
        self.primary_platform = lib.PRIMARY_MUSIC_PLATFORM
        self.secondary_platform = lib.SECONDARY_MUSIC_PLATFORM
        self.supported_languages = lib.SUPPORTED_LANGUAGES

        self._categories = {c.name: c for c in lib.SONG_CATEGORIES}
        self._durations = {d.label: d for d in lib.SONG_DURATIONS}
        self._tempo = lib.CATEGORY_TEMPO
        self._profiles = {p.character: p for p in lib.VOICE_PROFILES}
        self._sfx = {s.name: s for s in lib.SOUND_EFFECTS}
        self._foley = {f.name: f for f in lib.FOLEY_SOUNDS}
        self._ambience = {a.name: a for a in lib.AMBIENT_SOUNDS}
        self._pronunciations = {p.word: p for p in lib.PRONUNCIATIONS}

    # ------------------------------------------------------------------
    # Lists
    # ------------------------------------------------------------------

    def list_song_categories(self) -> list[str]:
        return [c.name for c in lib.SONG_CATEGORIES]

    def list_song_sections(self) -> list[str]:
        return [s.name for s in lib.SONG_SECTIONS]

    def list_durations(self) -> list[str]:
        return [d.label for d in lib.SONG_DURATIONS]

    def list_voice_profiles(self) -> list[str]:
        return list(self._profiles)

    def list_sound_effects(self) -> list[str]:
        return list(self._sfx)

    def list_foley_sounds(self) -> list[str]:
        return list(self._foley)

    def list_ambience(self) -> list[str]:
        return list(self._ambience)

    def list_pronunciations(self) -> list[str]:
        return list(self._pronunciations)

    # ------------------------------------------------------------------
    # Queries (fall back to a stable default when unknown)
    # ------------------------------------------------------------------

    def song_category(self, name: str) -> Optional[SongCategory]:
        return self._categories.get(name)

    def song_duration(self, label: str) -> Optional[SongDuration]:
        for duration in lib.SONG_DURATIONS:
            if duration.label.lower() == label.lower():
                return duration
        return None

    def song_structure(self, duration_seconds: int) -> tuple[SongSection, ...]:
        """Structure sections for a duration, per SONG_STRUCTURE.md."""
        if duration_seconds <= 60:
            keep = {"Intro", "Verse", "Chorus", "Outro"}
            sections = [s for s in lib.SONG_SECTIONS if s.name in keep]
            final = next(s for s in sections if s.name == "Chorus")
            sections.append(SongSection("Final Chorus", 8, "Hook repeat with full energy"))
            return tuple(sections)
        if duration_seconds >= 180:
            return lib.SONG_SECTIONS
        return lib.SONG_SECTIONS

    def tempo_for_category(self, category: str) -> tuple[int, int]:
        return self._tempo.get(category, lib.TEMP_RANGE)

    def voice_profile(self, character: str) -> Optional[VoiceProfile]:
        return self._profiles.get(character)

    def sound_effect(self, name: str) -> Optional[SoundEffect]:
        return self._sfx.get(name)

    def foley(self, name: str) -> Optional[FoleySound]:
        return self._foley.get(name)

    def ambience(self, name: str) -> Optional[AmbientSound]:
        return self._ambience.get(name)

    def pronunciation(self, word: str) -> Optional[PronunciationEntry]:
        return self._pronunciations.get(word)

    def mixing_rules(self) -> tuple[MixingRule, ...]:
        return lib.MIXING_RULES

    def mastering_rules(self) -> tuple[MasteringRule, ...]:
        return lib.MASTERING_RULES

    def lipsync_standards(self) -> tuple[LipSyncStandard, ...]:
        return lib.LIPSYNC_STANDARDS

    def localization_standards(self) -> tuple[LocalizationStandard, ...]:
        return lib.LOCALIZATION_STANDARDS

    # ------------------------------------------------------------------
    # Brief resolution
    # ------------------------------------------------------------------

    def build_music_brief(
        self,
        category: str = "Alphabet",
        topic: str = "letters and letter sounds",
        duration_label: str = "Standard",
        vocals: str = "female lead vocal, children's choir",
        mood: str = "",
        tempo: Optional[int] = None,
        key: str = lib.DEFAULT_KEY,
    ) -> MusicBrief:
        category = self._canonical_category(category)
        duration = self.song_duration(duration_label) or lib.SONG_DURATIONS[2]
        tempo_min, tempo_max = self.tempo_for_category(category)
        tempo = tempo or ((tempo_min + tempo_max) // 2)
        structure = self.song_structure(duration.seconds)
        mood = mood or self._default_mood(category)

        prompt = build_music_prompt(
            category=category, topic=topic, duration_label=duration.label,
            vocals=vocals, mood=mood,
        )

        return MusicBrief(
            category=category,
            topic=topic,
            structure=tuple(s.name for s in structure),
            duration_label=duration.label,
            duration_seconds=duration.seconds,
            tempo=tempo,
            mood=mood,
            key=key,
            vocals=vocals,
            instrumentation=lib.SIGNATURE_INSTRUMENTATION,
            style_notes=(
                f"Tempo {tempo_min}-{tempo_max} BPM, major key only, simple "
                "repetitive melody, bright instrumentation"
            ),
            prompt=prompt,
            negative_prompt=category_negative(category),
            quality_checks=quality_checklist(),
            stems=True,
            lipsync_note=(
                f"Phoneme timing 4-6 frames per phoneme at {lib.MASTER_FRAME_RATE} fps; "
                "beat grid 24 frames per 2 beats at 120 BPM"
            ),
            localization_note=(
                "Keep music stems so vocals can be replaced per locale; "
                f"supported languages: {', '.join(lib.SUPPORTED_LANGUAGES)}"
            ),
        )

    def build_voice_brief(self, character: str = "Narrator") -> VoiceBrief:
        profile = self._profiles.get(character) or self._profiles["Narrator"]
        return VoiceBrief(
            character=profile.character,
            role=profile.role,
            age=profile.age,
            pitch=profile.pitch,
            energy=profile.energy,
            speech_speed=profile.speech_speed,
            accent=profile.accent,
            laugh_style=profile.laugh_style,
            singing_style=profile.singing_style,
            tts_engine=profile.tts_engine,
            prompt=build_voice_prompt(profile),
            negative_prompt=category_negative("voice"),
            quality_checks=quality_checklist(),
        )

    def _canonical_category(self, category: str) -> str:
        for name in self._categories:
            if name.lower() == category.lower():
                return name
        return category

    def _default_mood(self, category: str) -> str:
        lower = category.lower()
        if "dance" in lower or "exercise" in lower:
            return "bouncy"
        if "bedtime" in lower or "family" in lower or "emotion" in lower:
            return "gentle"
        return lib.DEFAULT_MOOD

    # ------------------------------------------------------------------
    # Bible-aware validation
    # ------------------------------------------------------------------

    def validate_music_brief(self, brief: MusicBrief) -> dict:
        violations: list[str] = []
        warnings: list[str] = []

        if brief.category not in self._categories:
            violations.append(f"Unknown song category '{brief.category}' — not in the 24 approved categories")
        else:
            tempo_min, tempo_max = self.tempo_for_category(brief.category)
            if not (tempo_min <= brief.tempo <= tempo_max):
                violations.append(
                    f"Tempo {brief.tempo} BPM outside the {tempo_min}-{tempo_max} BPM range "
                    f"for '{brief.category}'"
                )
            elif not (self.tempo_range[0] <= brief.tempo <= self.tempo_range[1]):
                warnings.append(f"Tempo {brief.tempo} BPM outside the global 80-130 BPM range")

        duration = self.song_duration(brief.duration_label)
        if duration is None or duration.seconds != brief.duration_seconds:
            violations.append(
                f"Duration '{brief.duration_label}' ({brief.duration_seconds}s) is not an approved duration"
            )
        else:
            sections = {s.name for s in self.song_structure(brief.duration_seconds)}
            if "Final Chorus" not in brief.structure:
                violations.append("Structure missing Final Chorus")
            if set(brief.structure) - sections:
                violations.append(f"Structure contains sections not valid for {brief.duration_label} duration")

        if brief.key and "major" not in brief.key:
            violations.append("Only major keys are allowed")
        if not brief.stems:
            warnings.append("Stems should be archived so vocals can be replaced for localization")

        return {
            "passed": not violations,
            "violations": violations,
            "warnings": warnings,
        }

    def validate_voice_brief(self, brief: VoiceBrief) -> dict:
        violations: list[str] = []
        warnings: list[str] = []

        if brief.character not in self._profiles:
            warnings.append(f"Character '{brief.character}' has no approved voice profile — using Narrator defaults")

        known_engines = {lib.NARRATOR_ENGINE, lib.CHARACTER_ENGINE, lib.OFFLINE_ENGINE}
        if brief.tts_engine not in known_engines:
            warnings.append(f"TTS engine '{brief.tts_engine}' is not an approved engine ({', '.join(known_engines)})")

        if not brief.prompt:
            violations.append("Voice brief has no prompt")

        return {
            "passed": not violations,
            "violations": violations,
            "warnings": warnings,
        }

    def validate_dialogue(self, text: str) -> dict:
        violations: list[str] = []
        warnings: list[str] = []

        words = len(re.findall(r"\S+", text))
        sentences = re.split(r"[.!?]+", text)
        sentences = [s for s in sentences if s.strip()]
        max_words = max((len(s.split()) for s in sentences), default=0)
        if max_words > 12:
            violations.append(f"Sentence too long ({max_words} words) — dialogue uses short sentences")
        if words and (words / max(len(sentences), 1)) > 12:
            warnings.append("Dialogue density high — children respond best to short, repeated lines")

        expected_seconds = words / self.speaking_rate_wps
        return {
            "passed": not violations,
            "violations": violations,
            "warnings": warnings,
            "words": words,
            "expected_seconds": round(expected_seconds, 2),
        }

    # ------------------------------------------------------------------
    # Doc <-> code consistency
    # ------------------------------------------------------------------

    def check_docs(self, docs_dir: str) -> DocConsistencyReport:
        """Verify the markdown bibles still contain the standards we encode.

        Each fact pairs a file with a token that must appear in that file.
        This keeps the code in sync with the human-readable bibles.
        """
        facts = [
            DocFact("Audio/Music/MUSIC_STYLE_GUIDE.md", "Tempo", "80–130 BPM"),
            DocFact("Audio/Music/MUSIC_STYLE_GUIDE.md", "Preferred keys", "C major"),
            DocFact("Audio/Music/SONG_CATEGORIES.md", "Categories", "Alphabet"),
            DocFact("Audio/Music/SONG_CATEGORIES.md", "Last category", "Dance Songs"),
            DocFact("Audio/Music/SONG_STRUCTURE.md", "Final section", "Final Chorus"),
            DocFact("Audio/Music/SONG_STRUCTURE.md", "Animation sync", "24 fps"),
            DocFact("Audio/AUDIO_BIBLE.md", "Primary platform", "Suno"),
            DocFact("Audio/AUDIO_BIBLE.md", "Secondary platform", "ACE-Step Studio"),
            DocFact("Audio/CharacterVoices/VOICE_PROFILES.md", "Narrator engine", "Kokoro"),
            DocFact("Audio/CharacterVoices/VOICE_PROFILES.md", "Multilingual engine", "XTTS v2"),
            DocFact("Audio/CharacterVoices/VOICE_PROFILES.md", "Offline engine", "Piper"),
            DocFact("Audio/CharacterVoices/VOICE_PROFILES.md", "Lily pitch", "Medium-high"),
            DocFact("Audio/CharacterVoices/VOICE_PROFILES.md", "Lily singing", "Bright"),
            DocFact("Audio/Narration/NARRATION_STANDARDS.md", "Narrator decision", "Single narrator"),
            DocFact("Audio/Dialogue/DIALOGUE_STANDARDS.md", "Sentence rule", "Short sentences"),
            DocFact("Audio/PronunciationDictionary/PRONUNCIATION_GUIDE.md",
                    "Town name", "Little Learning Town"),
            DocFact("Audio/SFX/SFX_INDEX.md", "Soft thunder", "Thunder Distant Soft"),
            DocFact("Audio/SFX/SFX_INDEX.md", "Sparkle", "Sparkle"),
            DocFact("Audio/Foley/FOLEY_INDEX.md", "Zipper", "Backpack Zip"),
            DocFact("Audio/Ambience/AMBIENCE_INDEX.md", "Nature bed", "Forest Day"),
            DocFact("Audio/Mixes/MIXING_STANDARDS.md", "Priority rule", "Dialogue (Highest Priority)"),
            DocFact("Audio/Mixes/MASTERING_GUIDE.md", "Loudness target", "-14 LUFS"),
            DocFact("Audio/LipSync/LIPSYNC_STANDARDS.md", "Phoneme timing", "phoneme timing"),
            DocFact("Audio/Localization/LOCALIZATION_GUIDE.md", "Target languages", "Spanish"),
            DocFact("Audio/PromptTemplates/music-prompts.md", "Duration phrase", "approximately two minutes"),
            DocFact("Audio/NegativePrompts/AUDIO_NEGATIVES.md", "Negative block", "harsh"),
        ]

        report = DocConsistencyReport()
        base = os.path.abspath(docs_dir)
        strip_audio_prefix = os.path.basename(base) == "Audio"

        for fact in facts:
            rel = fact.file
            if strip_audio_prefix and rel.startswith("Audio/"):
                rel = rel[len("Audio/"):]
            path = os.path.join(base, rel)
            if not os.path.exists(path):
                report.missing_files.append(fact.file)
                continue
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            norm_content = re.sub(r"\s+", " ", content)
            if fact.expected in norm_content:
                fact.found = True
                fact.detail = f"'{fact.expected}' present in {fact.file}"
            else:
                fact.detail = f"'{fact.expected}' NOT found in {fact.file}"
            report.facts.append(fact)

        return report
