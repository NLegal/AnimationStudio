"""Phase 5 Audio Bible & Music Production System.

Machine-readable encoding of the Audio bible standards (`Audio/` markdown
docs): song categories/structure/durations, music style, voice profiles,
dialogue rules, pronunciation dictionary, SFX/foley/ambience libraries,
mixing/mastering guidelines, lip-sync and localization standards, plus a
production system that assembles and validates a full episode audio plan.
"""

from .bible import AudioBible
from .models import (
    AmbientSound, DialogueRule, DocConsistencyReport, DocFact,
    FoleySound, LipSyncStandard, LocalizationStandard, MasteringRule, MixingRule,
    MusicBrief, MusicStyle, PronunciationEntry, SongCategory, SongDuration,
    SongSection, SoundEffect, VoiceBrief, VoiceProfile,
)
from .production import AudioPlan, AudioProductionSystem, DialogueClip, SongEntry
from .prompts import (
    AUDIO_NEGATIVE_BASE, build_music_prompt, build_voice_prompt,
    category_negative, duration_word, quality_checklist,
)

__all__ = [
    "AudioBible", "AudioPlan", "AudioProductionSystem", "DialogueClip",
    "SongEntry", "MusicBrief", "VoiceBrief", "SongCategory", "SongDuration",
    "SongSection", "MusicStyle", "VoiceProfile", "DialogueRule",
    "PronunciationEntry", "SoundEffect", "FoleySound", "AmbientSound",
    "MixingRule", "MasteringRule", "LipSyncStandard", "LocalizationStandard",
    "DocFact", "DocConsistencyReport", "AUDIO_NEGATIVE_BASE",
    "build_music_prompt", "build_voice_prompt", "category_negative",
    "duration_word", "quality_checklist",
]
