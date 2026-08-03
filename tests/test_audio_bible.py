"""Phase 5 tests — Audio Bible & Music Production System.

Covers library contents, brief resolution, bible validation, prompt
builders, the full production system, and doc <-> code consistency.
"""

import os

import pytest

from src.audio_bible import (
    AUDIO_NEGATIVE_BASE, AudioBible, AudioProductionSystem, MusicBrief,
    VoiceBrief, build_music_prompt, build_voice_prompt, category_negative,
    duration_word, quality_checklist,
)
from src.audio_bible import libraries as lib


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def bible():
    return AudioBible()


@pytest.fixture
def system():
    return AudioProductionSystem()


class TestLibraryContents:
    def test_song_categories(self, bible):
        cats = bible.list_song_categories()
        assert len(cats) == 24
        for expected in ("Alphabet", "Numbers", "Colors", "Animals",
                         "Bedtime", "Dance Songs", "Interactive Learning",
                         "Holiday Specials", "Birthday Songs"):
            assert expected in cats

    def test_song_sections(self, bible):
        sections = bible.list_song_sections()
        assert sections == ["Intro", "Verse", "Pre-Chorus", "Chorus",
                            "Verse", "Chorus", "Bridge", "Final Chorus", "Outro"]

    def test_song_durations(self, bible):
        assert [(d.label, d.seconds) for d in lib.SONG_DURATIONS] == [
            ("Micro", 30), ("Short", 60), ("Standard", 120),
            ("Feature", 180), ("Long", 300),
        ]

    def test_voice_profiles(self, bible):
        profiles = bible.list_voice_profiles()
        assert len(profiles) == 11
        assert "Lily Bunny" in profiles
        assert "Narrator" in profiles
        lily = bible.voice_profile("Lily Bunny")
        assert lily.pitch == "Medium-high"
        assert lily.singing_style == "Bright"
        assert lily.tts_engine == "XTTS v2"
        narrator = bible.voice_profile("Narrator")
        assert narrator.role == "narrator"
        assert narrator.tts_engine == "Kokoro"

    def test_sound_libraries(self, bible):
        sfx = bible.list_sound_effects()
        assert len(sfx) == 27
        assert "Thunder (soft)" in sfx
        assert "Magic Sparkle" in sfx
        assert "Xylophone" in sfx
        assert "Clapping" in sfx
        foley = bible.list_foley_sounds()
        assert len(foley) == 12
        assert "Backpack zipper" in foley
        ambience = bible.list_ambience()
        assert len(ambience) == 12
        assert "Morning Birds" in ambience

    def test_pronunciations(self, bible):
        entries = bible.list_pronunciations()
        assert len(entries) == 19
        town = bible.pronunciation("Little Learning Town")
        assert town.phonetic == "LIT-ul LURN-ing TOWN"

    def test_mixing_and_mastering(self, bible):
        rules = {r.rule: r.standard for r in bible.mixing_rules()}
        assert rules["Dialogue priority"] == "Dialogue always takes priority"
        assert "No spikes" in rules
        master = {r.rule: r.standard for r in bible.mastering_rules()}
        assert master["Consistent loudness"] == "-14 LUFS integrated"
        assert bible.true_peak_dbtp == -1.0
        assert bible.master_sample_rate == 48000

    def test_quality_checklist(self):
        checks = quality_checklist()
        assert len(checks) == 10
        assert checks[0] == "Matches studio identity"
        assert "Localization-ready" in checks

    def test_style_constants(self):
        assert lib.TEMP_RANGE == (80, 130)
        assert lib.MASTER_FRAME_RATE == 24
        assert lib.SPEAKING_RATE_WPS == 2.5
        assert lib.PRIMARY_MUSIC_PLATFORM == "Suno"
        assert lib.SECONDARY_MUSIC_PLATFORM == "ACE-Step Studio"
        assert len(lib.CATEGORY_TEMPO) == 24


class TestMusicBrief:
    def test_build_standard(self, bible):
        brief = bible.build_music_brief(category="Alphabet", topic="letters",
                                        duration_label="Standard")
        assert isinstance(brief, MusicBrief)
        assert brief.category == "Alphabet"
        assert brief.duration_seconds == 120
        assert brief.tempo == 110
        assert brief.key == "C major"
        assert "Final Chorus" in brief.structure
        assert len(brief.structure) == 9
        assert brief.stems is True

    def test_short_structure(self, bible):
        brief = bible.build_music_brief(category="Bedtime", topic="sleepy time",
                                        duration_label="Short")
        assert brief.duration_seconds == 60
        assert "Final Chorus" in brief.structure
        assert "Pre-Chorus" not in brief.structure

    def test_tempo_per_category(self, bible):
        assert bible.tempo_for_category("Bedtime") == (60, 80)
        assert bible.tempo_for_category("Dance Songs") == (110, 130)
        assert bible.tempo_for_category("Alphabet") == (100, 120)

    def test_brief_has_prompt_and_negative(self, bible):
        brief = bible.build_music_brief()
        assert "[character]" not in brief.prompt
        assert "preschool" in brief.prompt
        assert "approximately two minutes" in brief.prompt
        assert brief.negative_prompt
        assert brief.lipsync_note
        assert "stems" in brief.localization_note.lower()

    def test_unknown_category_defaults(self, bible):
        brief = bible.build_music_brief(category="Totally Fake", topic="x",
                                        duration_label="Standard")
        assert brief.category == "Totally Fake"
        validation = bible.validate_music_brief(brief)
        assert not validation["passed"]


class TestVoiceBrief:
    def test_lily(self, bible):
        brief = bible.build_voice_brief("Lily Bunny")
        assert isinstance(brief, VoiceBrief)
        assert brief.character == "Lily Bunny"
        assert brief.role == "character"
        assert brief.pitch == "Medium-high"
        assert brief.tts_engine == "XTTS v2"
        assert "preschool" in brief.prompt
        assert "children ages 2-6" in brief.prompt

    def test_narrator(self, bible):
        brief = bible.build_voice_brief("Narrator")
        assert brief.role == "narrator"
        assert brief.tts_engine == "Kokoro"
        assert "Warm preschool narrator" in brief.prompt

    def test_unknown_character_defaults_to_narrator(self, bible):
        brief = bible.build_voice_brief("Unknown Character")
        assert brief.character == "Narrator"

    def test_all_profiles_resolve(self, bible):
        for name in bible.list_voice_profiles():
            brief = bible.build_voice_brief(name)
            assert brief.prompt


class TestBibleValidation:
    def test_validate_good_music(self, bible):
        brief = bible.build_music_brief()
        assert bible.validate_music_brief(brief)["passed"]

    def test_validate_bad_tempo(self, bible):
        brief = bible.build_music_brief(category="Bedtime", topic="x")
        brief.tempo = 140
        result = bible.validate_music_brief(brief)
        assert not result["passed"]
        assert any("140 BPM" in v for v in result["violations"])

    def test_validate_minor_key(self, bible):
        brief = bible.build_music_brief()
        brief.key = "A minor"
        result = bible.validate_music_brief(brief)
        assert not result["passed"]
        assert any("major keys" in v for v in result["violations"])

    def test_validate_no_stems_warns(self, bible):
        brief = bible.build_music_brief()
        brief.stems = False
        result = bible.validate_music_brief(brief)
        assert result["passed"]
        assert any("stems" in w.lower() for w in result["warnings"])

    def test_validate_dialogue_short(self, bible):
        result = bible.validate_dialogue("Let's learn together!")
        assert result["passed"]
        assert result["expected_seconds"] > 0

    def test_validate_dialogue_too_long_sentence(self, bible):
        text = ("The quick brown fox jumps over the lazy dog and then "
                "continues running through the entire meadow without stopping once, okay?")
        result = bible.validate_dialogue(text)
        assert not result["passed"]


class TestPromptBuilder:
    def test_music_prompt_category_template(self):
        prompt = build_music_prompt("Alphabet", "letters", "Standard")
        assert "alphabet song" in prompt
        assert "approximately two minutes" in prompt

    def test_music_prompt_duration_words(self):
        assert duration_word(30) == "thirty seconds"
        assert duration_word(120) == "two minutes"
        assert duration_word(300) == "five minutes"

    def test_music_prompt_placeholder_order(self):
        # PHASE5.md example prompt
        prompt = build_music_prompt(
            category="Good Manners",
            topic="sharing toys",
            duration_label="Standard",
            vocals="female lead vocal, children's choir",
        )
        assert "preschool" in prompt
        assert "major key" in prompt
        assert "simple repetitive melody" in prompt
        assert "educational" in prompt
        assert "bright instrumentation" in prompt
        assert prompt.index("preschool") < prompt.index("major key")

    def test_voice_prompt(self, bible):
        lily = bible.voice_profile("Lily Bunny")
        prompt = build_voice_prompt(lily)
        assert "medium-high pitch" in prompt
        assert "playful energy" in prompt

    def test_narrator_prompt_exact(self, bible):
        narrator = bible.voice_profile("Narrator")
        assert build_voice_prompt(narrator) == (
            "Warm preschool narrator, calm pace, clear pronunciation, friendly tone, "
            "energetic but gentle, suitable for children ages 2-6."
        )

    def test_category_negative_layering(self):
        base = category_negative("music", include_base=False)
        assert base
        layered = category_negative("music")
        assert layered.startswith(AUDIO_NEGATIVE_BASE)
        assert "harsh" in layered


class TestProductionSystem:
    def test_resolve_music(self, system):
        brief = system.resolve_music("Numbers", "counting to ten", "Short")
        assert brief.category == "Numbers"
        assert brief.duration_seconds == 60

    def test_resolve_voice(self, system):
        assert system.resolve_voice("Daisy Duck").character == "Daisy Duck"

    def test_plan_song_with_engine(self, system):
        entry = system.plan_song_with_engine(
            song_type="lullaby", objective_name="bedtime",
            main_character="Lily Bunny", duration_label="Standard",
        )
        assert entry.category == "Bedtime"
        assert entry.placement == "middle"
        assert entry.brief is not None
        assert entry.validation["passed"]

    def test_plan_episode_full(self, system):
        plan = system.plan_episode(
            episode_id="S01E01",
            title="The Alphabet Garden",
            dialogue_lines=[
                ("Lily Bunny", "A is for apple! B is for ball!", "happy"),
                ("Ben Bear", "Yum yum, apples!", "excited"),
            ],
            songs=[("Alphabet", "letter sounds", "Short"),
                   ("Dance Songs", "moving and dancing", "Standard")],
            scene="Sunny Garden Playground",
        )
        assert plan.passed
        assert plan.narration is not None
        assert len(plan.dialogue) == 2
        assert len(plan.songs) == 2
        assert plan.dialogue[0].lip_sync.total_phonemes() > 0
        assert plan.dialogue[0].voice_brief.character == "Lily Bunny"
        assert plan.dialogue[1].voice_brief.character == "Ben Bear"
        assert "Playground" in plan.ambience
        assert plan.total_song_seconds == 180
        assert plan.mix_rules[0] == "Dialogue always takes priority"

    def test_plan_episode_empty_fails(self, system):
        plan = system.plan_episode(episode_id="E0", title="Empty",
                                   dialogue_lines=[], songs=[])
        assert not plan.passed

    def test_plan_episode_no_narration(self, system):
        plan = system.plan_episode(
            episode_id="E1", title="Silent", narration=False,
            dialogue_lines=[("Lily Bunny", "Hi!", "happy")], songs=[],
        )
        assert plan.passed
        assert plan.narration is None

    def test_scene_sound_mapping(self, system):
        assert "School Bell" in system._pick_sfx("school classroom")
        assert "Cow Moo" in system._pick_sfx("the farm")
        assert "Beach" in system._pick_ambience("ocean beach")
        assert "Rain" in system._pick_sfx("rainy day")
        assert "Night" in system._pick_ambience("night time")


class TestDocConsistency:
    def test_check_docs_passes(self, bible):
        report = bible.check_docs(os.path.join(ROOT, "Audio"))
        d = report.to_dict()
        assert d["passed"], d["facts_failed"]
        assert d["facts_checked"] == 26
        assert d["facts_passed"] == 26
        assert d["missing_files"] == []

    def test_check_docs_prefix_stripping(self, bible):
        # Passing the Audio/ dir itself must still resolve Audio/... facts
        report = bible.check_docs(os.path.join(ROOT, "Audio"))
        assert report.to_dict()["facts_passed"] == 26

    def test_check_docs_missing_dir(self, bible):
        report = bible.check_docs("/tmp/does_not_exist_audio")
        assert not report.to_dict()["passed"]
        assert report.to_dict()["missing_files"]
