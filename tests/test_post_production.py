"""Tests for Phase 10 — Post-Production, Video Editing & Mastering System.

Covers all 13 engine modules and supporting dataclasses.
"""

import pytest

from src.post_production import (
    TimelineTrack, TimelineEvent, MasterTimeline, ClipReference,
    SceneAssembly, ExportPreset, QCResult, ArchiveRecord,
    VideoTrackType, AudioTrackType, TransitionStyle,
    TimelineEngine, EditingEngine, PacingEngine,
    TransitionLibrary, AudioSyncEngine,
    SubtitleEngine, SubtitleEntry,
    GraphicsEngine, GraphicOverlay,
    IntroOutroEngine, IntroTemplate, OutroTemplate,
    ThumbnailSelector,
    ExportEngine,
    LocalizationEngine, LocalizationPackage,
    PostProductionQC, ArchiveEngine,
    ColorCorrectionEngine, ColorCorrectionSettings,
    EnhancementEngine, EnhancementSettings,
    PostProductionAnalytics, AnalyticsReport,
    InteractiveElementEngine,
)


# ── Model Tests ─────────────────────────────────────────────────────────

class TestTimelineTrack:
    def test_defaults(self):
        t = TimelineTrack()
        assert t.name == ""
        assert t.events == []
        assert t.order == 0

    def test_total_duration_empty(self):
        t = TimelineTrack()
        assert t.total_duration() == 0.0

    def test_total_duration_with_events(self):
        t = TimelineTrack(events=[
            TimelineEvent(start_time=0.0, end_time=5.0),
            TimelineEvent(start_time=2.0, end_time=10.0),
        ])
        assert t.total_duration() == 10.0

    def test_event_count(self):
        t = TimelineTrack(events=[TimelineEvent(), TimelineEvent()])
        assert t.event_count() == 2

    def test_event_count_empty(self):
        t = TimelineTrack()
        assert t.event_count() == 0


class TestTimelineEvent:
    def test_defaults(self):
        e = TimelineEvent()
        assert e.event_id == ""
        assert e.start_time == 0.0
        assert e.video_track == VideoTrackType.ANIMATION

    def test_duration_requires_explicit_set(self):
        e = TimelineEvent(start_time=1.0, end_time=4.0, duration=3.0)
        assert e.duration == 3.0

    def test_negative_duration_explicit(self):
        e = TimelineEvent(start_time=5.0, end_time=2.0, duration=-3.0)
        assert e.duration == -3.0


class TestMasterTimeline:
    def test_defaults(self):
        m = MasterTimeline()
        assert m.episode_id == ""
        assert m.frame_rate == 24
        assert m.resolution_width == 1920

    def test_total_frames(self):
        m = MasterTimeline(duration_seconds=5.0, frame_rate=24)
        assert m.total_frames == 120

    def test_total_frames_zero(self):
        m = MasterTimeline()
        assert m.total_frames == 0


class TestClipReference:
    def test_defaults(self):
        c = ClipReference()
        assert c.clip_id == ""
        assert c.frame_rate == 24
        assert c.resolution_width == 1920
        assert c.approval_status == "pending"

    def test_full_init(self):
        c = ClipReference(clip_id="CLIP_001", episode="S01E01", scene="learning", duration=5.0)
        assert c.clip_id == "CLIP_001"
        assert c.duration == 5.0


class TestSceneAssembly:
    def test_defaults(self):
        s = SceneAssembly()
        assert s.total_clips() == 0
        assert s.total_duration() == 0.0

    def test_total_clips(self):
        s = SceneAssembly(
            opening=[ClipReference(), ClipReference()],
            learning=[ClipReference()],
        )
        assert s.total_clips() == 3

    def test_total_duration(self):
        s = SceneAssembly(
            opening=[ClipReference(duration=2.0)],
            song=[ClipReference(duration=3.0)],
        )
        assert s.total_duration() == 5.0

    def test_all_sections(self):
        s = SceneAssembly(
            opening=[ClipReference()],
            introduction=[ClipReference()],
            learning=[ClipReference()],
            song=[ClipReference()],
            practice=[ClipReference()],
            review=[ClipReference()],
            celebration=[ClipReference()],
            outro=[ClipReference()],
        )
        assert s.total_clips() == 8


class TestExportPreset:
    def test_defaults(self):
        p = ExportPreset()
        assert p.resolution_width == 1920
        assert p.resolution_height == 1080
        assert p.frame_rate == 24
        assert p.format == "mp4"


class TestQCResult:
    def test_defaults(self):
        q = QCResult()
        assert q.passed is False
        assert q.score == 0.0

    def test_full_init(self):
        q = QCResult(passed=True, checks={"ok": True}, score=100.0, timestamp="now")
        assert q.passed
        assert q.score == 100.0


class TestArchiveRecord:
    def test_defaults(self):
        a = ArchiveRecord()
        assert a.project_id == ""
        assert a.source_clips == []
        assert a.audio_stems == []


# ── Enum Value Tests ────────────────────────────────────────────────────

class TestEnumValues:
    def test_video_track_types(self):
        assert len(VideoTrackType) == 5

    def test_audio_track_types(self):
        assert len(AudioTrackType) == 7

    def test_transition_styles(self):
        assert len(TransitionStyle) == 9


# ── TimelineEngine Tests ────────────────────────────────────────────────

class TestTimelineEngine:
    def test_create(self):
        engine = TimelineEngine()
        tl = engine.create("EP_001", "Colors")
        assert tl.episode_id == "EP_001"
        assert tl.title == "Colors"
        assert tl.created_at != ""

    def test_create_default_title(self):
        engine = TimelineEngine()
        tl = engine.create("EP_001")
        assert tl.title == "EP_001"

    def test_add_track(self):
        engine = TimelineEngine()
        tl = engine.create("EP_001")
        track = engine.add_track(tl, "Video", 0)
        assert track.name == "Video"
        assert track.order == 0
        assert len(tl.tracks) == 1

    def test_add_event(self):
        engine = TimelineEngine()
        tl = engine.create("EP_001")
        track = engine.add_track(tl, "Video")
        event = engine.add_event(
            track, "EVT_001", start_time=0.0, end_time=5.0,
            clip_id="CLIP_001",
        )
        assert event.event_id == "EVT_001"
        assert event.duration == 5.0
        assert event.clip_id == "CLIP_001"
        assert len(track.events) == 1

    def test_add_event_custom_transitions(self):
        engine = TimelineEngine()
        tl = engine.create("EP_001")
        track = engine.add_track(tl, "Video")
        event = engine.add_event(
            track, "EVT_001", transition_in=TransitionStyle.FADE,
            transition_out=TransitionStyle.CROSSFADE,
        )
        assert event.transition_in == TransitionStyle.FADE
        assert event.transition_out == TransitionStyle.CROSSFADE

    def test_calculate_duration_empty(self):
        engine = TimelineEngine()
        tl = engine.create("EP_001")
        assert engine.calculate_duration(tl) == 0.0
        assert tl.duration_seconds == 0.0

    def test_calculate_duration(self):
        engine = TimelineEngine()
        tl = engine.create("EP_001")
        track = engine.add_track(tl, "Video")
        engine.add_event(track, "E1", end_time=10.0)
        assert engine.calculate_duration(tl) == 10.0

    def test_calculate_duration_multiple_tracks(self):
        engine = TimelineEngine()
        tl = engine.create("EP_001")
        t1 = engine.add_track(tl, "Video")
        t2 = engine.add_track(tl, "Audio")
        engine.add_event(t1, "E1", end_time=10.0)
        engine.add_event(t2, "E2", end_time=15.0)
        assert engine.calculate_duration(tl) == 15.0

    def test_find_gaps_empty(self):
        engine = TimelineEngine()
        track = TimelineTrack()
        assert engine.find_gaps(track) == [(0.0, 0.0)]

    def test_find_gaps_no_gaps(self):
        engine = TimelineEngine()
        track = TimelineTrack(events=[
            TimelineEvent(start_time=0.0, end_time=5.0),
            TimelineEvent(start_time=5.0, end_time=10.0),
        ])
        assert engine.find_gaps(track) == []

    def test_find_gaps_with_gap(self):
        engine = TimelineEngine()
        track = TimelineTrack(events=[
            TimelineEvent(start_time=0.0, end_time=3.0),
            TimelineEvent(start_time=7.0, end_time=10.0),
        ])
        gaps = engine.find_gaps(track)
        assert len(gaps) == 1
        assert abs(gaps[0][0] - 3.0) < 0.01
        assert abs(gaps[0][1] - 7.0) < 0.01

    def test_find_gaps_sorted(self):
        engine = TimelineEngine()
        track = TimelineTrack(events=[
            TimelineEvent(start_time=5.0, end_time=10.0),
            TimelineEvent(start_time=0.0, end_time=3.0),
        ])
        gaps = engine.find_gaps(track)
        assert len(gaps) == 1

    def test_find_overlaps_none(self):
        engine = TimelineEngine()
        track = TimelineTrack(events=[
            TimelineEvent(event_id="A", start_time=0.0, end_time=3.0),
            TimelineEvent(event_id="B", start_time=3.0, end_time=6.0),
        ])
        assert engine.find_overlaps(track) == []

    def test_find_overlaps_with_overlap(self):
        engine = TimelineEngine()
        track = TimelineTrack(events=[
            TimelineEvent(event_id="A", start_time=0.0, end_time=5.0),
            TimelineEvent(event_id="B", start_time=3.0, end_time=8.0),
        ])
        overlaps = engine.find_overlaps(track)
        assert len(overlaps) == 1
        assert overlaps[0][0] == "A"
        assert overlaps[0][1] == "B"

    def test_timeline_to_dict(self):
        engine = TimelineEngine()
        tl = engine.create("EP_001")
        track = engine.add_track(tl, "Video")
        engine.add_event(track, "E1", start_time=0.0, end_time=5.0)
        engine.calculate_duration(tl)
        d = engine.timeline_to_dict(tl)
        assert d["episode_id"] == "EP_001"
        assert d["duration_seconds"] == 5.0
        assert d["resolution"] == "1920x1080"
        assert len(d["tracks"]) == 1
        assert d["tracks"][0]["events"][0]["event_id"] == "E1"


# ── PacingEngine Tests ──────────────────────────────────────────────────

class TestPacingEngine:
    def test_suggest_shot_duration_default(self):
        p = PacingEngine()
        assert p.suggest_shot_duration("unknown_type") == 4.0

    def test_suggest_shot_duration_dialogue(self):
        p = PacingEngine()
        assert p.suggest_shot_duration("dialogue") == 4.0

    def test_suggest_shot_duration_song(self):
        p = PacingEngine()
        assert p.suggest_shot_duration("song") == 6.0

    def test_suggest_shot_duration_minimum(self):
        p = PacingEngine()
        assert p.suggest_shot_duration("transition") == 2.0

    def test_educational_pause_question(self):
        p = PacingEngine()
        assert p.educational_pause("question") == 2.0

    def test_educational_pause_count(self):
        p = PacingEngine()
        assert p.educational_pause("count") == 0.8

    def test_educational_pause_unknown(self):
        p = PacingEngine()
        assert p.educational_pause("unknown") == 1.0

    def test_estimate_scene_duration(self):
        p = PacingEngine()
        assert p.estimate_scene_duration("opening") == 8.0
        assert p.estimate_scene_duration("song") == 45.0
        assert p.estimate_scene_duration("learning") == 30.0

    def test_estimate_scene_duration_unknown(self):
        p = PacingEngine()
        assert p.estimate_scene_duration("unknown") == 20.0

    def test_total_episode_estimate_with_song(self):
        p = PacingEngine()
        total = p.total_episode_estimate(has_song=True)
        assert total == pytest.approx(8 + 15 + 30 + 45 + 25 + 20 + 15 + 15)

    def test_total_episode_estimate_without_song(self):
        p = PacingEngine()
        total = p.total_episode_estimate(has_song=False)
        assert total == pytest.approx(8 + 15 + 30 + 25 + 20 + 15 + 15)


# ── EditingEngine Tests ─────────────────────────────────────────────────

class TestEditingEngine:
    def test_assemble_scenes_empty(self):
        engine = EditingEngine()
        assembly = SceneAssembly(episode_id="EP_001")
        tl = engine.assemble_scenes("EP_001", assembly)
        assert tl.episode_id == "EP_001"
        assert tl.duration_seconds == 0.0

    def test_assemble_scenes_with_clips(self):
        engine = EditingEngine()
        assembly = SceneAssembly(
            opening=[ClipReference(clip_id="C1", duration=3.0)],
            learning=[ClipReference(clip_id="C2", duration=5.0)],
        )
        tl = engine.assemble_scenes("EP_001", assembly, "Learning Colors")
        assert tl.title == "Learning Colors"
        assert tl.duration_seconds == pytest.approx(8.0)
        assert len(tl.tracks) == 3

    def test_assemble_scenes_all_sections(self):
        engine = EditingEngine()
        assembly = SceneAssembly(
            opening=[ClipReference(clip_id="O1", duration=2.0)],
            introduction=[ClipReference(clip_id="I1", duration=2.0)],
            learning=[ClipReference(clip_id="L1", duration=2.0)],
            song=[ClipReference(clip_id="S1", duration=2.0)],
            practice=[ClipReference(clip_id="P1", duration=2.0)],
            review=[ClipReference(clip_id="R1", duration=2.0)],
            celebration=[ClipReference(clip_id="CE1", duration=2.0)],
            outro=[ClipReference(clip_id="OU1", duration=2.0)],
        )
        tl = engine.assemble_scenes("EP_001", assembly)
        assert tl.duration_seconds == pytest.approx(16.0)

    def test_assemble_scenes_creates_three_tracks(self):
        engine = EditingEngine()
        tl = engine.assemble_scenes("EP_001", SceneAssembly())
        assert len(tl.tracks) == 3
        assert tl.tracks[0].name == "Video"
        assert tl.tracks[1].name == "Audio"
        assert tl.tracks[2].name == "Subtitles"


# ── EditingEngine insert_pause Tests ────────────────────────────────────

class TestInsertPause:
    def test_insert_pause_shifts_future_events(self):
        engine = EditingEngine()
        assembly = SceneAssembly(
            learning=[ClipReference(clip_id="C1", duration=3.0)],
            practice=[ClipReference(clip_id="C2", duration=2.0)],
        )
        tl = engine.assemble_scenes("EP_001", assembly)
        video = tl.tracks[0]
        audio = tl.tracks[1]
        engine.insert_pause(video, audio, at_time=3.0, duration=0.5)
        first, second = video.events
        assert first.start_time == pytest.approx(0.0)
        assert first.end_time == pytest.approx(3.0)
        assert second.start_time == pytest.approx(3.5)
        assert second.end_time == pytest.approx(5.5)

    def test_insert_pause_straddling_event(self):
        engine = EditingEngine()
        tl = engine.assemble_scenes(
            "EP_001",
            SceneAssembly(learning=[ClipReference(clip_id="C1", duration=3.0)]),
        )
        video = tl.tracks[0]
        engine.insert_pause(video, None, at_time=1.0, duration=0.5)
        assert video.events[0].start_time == pytest.approx(0.0)
        assert video.events[0].end_time == pytest.approx(3.5)

    def test_insert_pause_clamps_duration(self):
        engine = EditingEngine()
        tl = engine.assemble_scenes(
            "EP_001",
            SceneAssembly(learning=[ClipReference(clip_id="C1", duration=3.0)]),
        )
        engine.insert_pause(tl.tracks[0], tl.tracks[1], at_time=1.0, duration=-1.0)
        assert tl.tracks[0].events[0].end_time == pytest.approx(3.1)


# ── InteractiveElementEngine Tests ──────────────────────────────────────

class TestInteractiveElementEngine:
    def test_add_and_list(self):
        engine = InteractiveElementEngine()
        engine.add_element("E1", "question", 0.0, 2.0, "count_bunny")
        engine.add_element("E2", "celebration", 5.0, 6.0)
        assert len(engine.list_elements()) == 2

    def test_remove(self):
        engine = InteractiveElementEngine()
        engine.add_element("E1", "question", 0.0, 2.0)
        assert engine.remove_element("E1") is True
        assert engine.remove_element("MISSING") is False

    def test_elements_in_range(self):
        engine = InteractiveElementEngine()
        engine.add_element("E1", "question", 1.0, 3.0)
        engine.add_element("E2", "clap", 10.0, 12.0)
        found = engine.elements_in_range(2.0, 4.0)
        assert [e["id"] for e in found] == ["E1"]


# ── ColorCorrectionEngine Tests ─────────────────────────────────────────

class TestColorCorrectionEngine:
    def test_neutral_defaults(self):
        s = ColorCorrectionEngine().settings()
        assert s.is_neutral()

    def test_clamping(self):
        s = ColorCorrectionEngine().settings(brightness=5.0, contrast=5.0, saturation=-1.0)
        assert s.brightness == 1.0
        assert s.contrast == 2.0
        assert s.saturation == 0.0

    def test_preset(self):
        s = ColorCorrectionEngine().preset("storybook")
        assert s.contrast == pytest.approx(1.15)
        assert s.saturation == pytest.approx(1.2)

    def test_list_presets(self):
        presets = ColorCorrectionEngine().list_presets()
        assert "storybook" in presets

    def test_suggest(self):
        s = ColorCorrectionEngine().suggest("song")
        assert s.description

    def test_apply(self):
        result = ColorCorrectionEngine().apply(ColorCorrectionEngine().preset("gentle_brighten"))
        assert result["settings"]["brightness"] == pytest.approx(0.05)


# ── EnhancementEngine Tests ─────────────────────────────────────────────

class TestEnhancementEngine:
    def test_recommend_interpolation(self):
        engine = EnhancementEngine()
        settings = engine.recommend(12, 24)
        assert settings.frame_interpolation is True

    def test_recommend_no_interpolation(self):
        engine = EnhancementEngine()
        settings = engine.recommend(24, 24)
        assert settings.frame_interpolation is False

    def test_pipeline_steps(self):
        engine = EnhancementEngine()
        steps = engine.pipeline()
        assert [s["step"] for s in steps] == [
            "sharpening", "noise_reduction", "frame_interpolation",
            "artifact_cleanup", "edge_refinement",
        ]

    def test_list_steps(self):
        steps = EnhancementEngine().list_steps()
        assert len(steps) == 5


# ── PostProductionAnalytics Tests ───────────────────────────────────────

class TestPostProductionAnalytics:
    def test_build_report(self):
        report = PostProductionAnalytics().build_report(
            episode_id="EP_001", question_count=4, subtitle_count=10,
            qc_score=95.0, render_time_seconds=120.0,
        )
        assert report.episode_id == "EP_001"
        assert report.question_count == 4
        assert report.subtitle_count == 10
        assert report.qc_score == 95.0

    def test_compression_ratio(self):
        engine = PostProductionAnalytics()
        assert engine.compression_ratio(100.0, 20.0) == pytest.approx(5.0)
        assert engine.compression_ratio(0.0, 20.0) == 0.0

    def test_duration_breakdown(self):
        engine = PostProductionAnalytics()
        breakdown = engine.duration_breakdown({"learning": 30.0, "song": 30.0})
        assert breakdown["learning"]["seconds"] == 30.0
        assert breakdown["learning"]["percent"] == pytest.approx(50.0)

    def test_as_dict(self):
        report = PostProductionAnalytics().build_report(episode_id="EP_001")
        assert report.as_dict()["episode_id"] == "EP_001"


# ── TransitionLibrary Tests ─────────────────────────────────────────────

class TestTransitionLibrary:
    def test_describe(self):
        lib = TransitionLibrary()
        desc = lib.describe(TransitionStyle.FADE)
        assert desc["duration"] == 0.5
        assert "description" in desc

    def test_describe_unknown_falls_back_to_fade(self):
        lib = TransitionLibrary()
        desc = lib.describe(TransitionStyle.NONE)
        assert desc["duration"] == 0.0

    def test_list_styles(self):
        lib = TransitionLibrary()
        assert len(lib.list_styles()) == 9

    def test_suggest_for_mood(self):
        lib = TransitionLibrary()
        assert lib.suggest_for_mood("happy") == TransitionStyle.CROSSFADE
        assert lib.suggest_for_mood("magical") == TransitionStyle.DISSOLVE
        assert lib.suggest_for_mood("fast") == TransitionStyle.QUICK_CUT

    def test_suggest_for_mood_unknown(self):
        lib = TransitionLibrary()
        assert lib.suggest_for_mood("unknown_mood") == TransitionStyle.FADE

    def test_estimate_duration(self):
        lib = TransitionLibrary()
        assert lib.estimate_duration(TransitionStyle.PAGE_TURN) == 1.2
        assert lib.estimate_duration(TransitionStyle.QUICK_CUT) == 0.1

    def test_estimate_duration_unknown(self):
        lib = TransitionLibrary()
        assert lib.estimate_duration(TransitionStyle.NONE) == 0.0


# ── AudioSyncEngine Tests ───────────────────────────────────────────────

class TestAudioSyncEngine:
    def test_mix_levels(self):
        engine = AudioSyncEngine()
        levels = engine.mix_levels([AudioTrackType.DIALOGUE, AudioTrackType.MUSIC])
        assert levels["dialogue"] == 0.0
        assert levels["music"] == -12.0

    def test_mix_levels_priority_order(self):
        engine = AudioSyncEngine()
        levels = engine.mix_levels(list(AudioTrackType))
        assert len(levels) == 7

    def test_mix_levels_new_tracks(self):
        engine = AudioSyncEngine()
        levels = engine.mix_levels([AudioTrackType.SINGING, AudioTrackType.LEARNING_SOUNDS])
        assert levels["singing"] == -3.0
        assert levels["learning_sounds"] == -6.0

    def test_estimate_dialogue_duration(self):
        engine = AudioSyncEngine()
        dur = engine.estimate_dialogue_duration("hello world", 150)
        assert dur == pytest.approx((2 / 150) * 60)

    def test_estimate_dialogue_duration_empty(self):
        engine = AudioSyncEngine()
        assert engine.estimate_dialogue_duration("") == 0.0

    def test_estimate_dialogue_duration_long(self):
        engine = AudioSyncEngine()
        dur = engine.estimate_dialogue_duration("one two three four five", 150)
        assert dur == pytest.approx((5 / 150) * 60)

    def test_check_sync_in_sync(self):
        engine = AudioSyncEngine()
        result = engine.check_sync(5.0, 5.02, tolerance=0.1)
        assert result["in_sync"] is True

    def test_check_sync_out_of_sync(self):
        engine = AudioSyncEngine()
        result = engine.check_sync(5.0, 6.0, tolerance=0.1)
        assert result["in_sync"] is False

    def test_suggest_music_fade_short(self):
        engine = AudioSyncEngine()
        fade = engine.suggest_music_fade(3.0)
        assert fade["fade_in"] == 0.3
        assert fade["fade_out"] == 0.3

    def test_suggest_music_fade_long(self):
        engine = AudioSyncEngine()
        fade = engine.suggest_music_fade(30.0)
        assert fade["fade_in"] == 2.0
        assert fade["fade_out"] == 2.0


# ── SubtitleEngine Tests ────────────────────────────────────────────────

class TestSubtitleEngine:
    def test_generate_from_text_empty(self):
        engine = SubtitleEngine()
        assert engine.generate_from_text("", 0.0, 5.0) == []

    def test_generate_from_text_single(self):
        engine = SubtitleEngine()
        entries = engine.generate_from_text("Hello world", 0.0, 4.0)
        assert len(entries) == 1
        assert entries[0].text == "Hello world"
        assert entries[0].start_time == 0.0

    def test_generate_from_text_long_line_splits(self):
        engine = SubtitleEngine()
        long_text = "a " * 50
        entries = engine.generate_from_text(long_text, 0.0, 10.0)
        assert len(entries) >= 1

    def test_generate_from_dialogue(self):
        engine = SubtitleEngine()
        entries = engine.generate_from_dialogue("Hello!", "Lily", 0.0, 3.0)
        assert len(entries) == 1
        assert "Lily:" in entries[0].text

    def test_generate_from_dialogue_no_character(self):
        engine = SubtitleEngine()
        entries = engine.generate_from_dialogue("Hello!", "", 0.0, 3.0)
        assert entries[0].text == "Hello!"

    def test_generate_from_lyrics(self):
        engine = SubtitleEngine()
        entries = engine.generate_from_lyrics("Twinkle twinkle\nLittle star", 0.0, 4.0)
        assert len(entries) == 2

    def test_generate_from_lyrics_empty(self):
        engine = SubtitleEngine()
        assert engine.generate_from_lyrics("", 0.0, 4.0) == []

    def test_to_srt(self):
        engine = SubtitleEngine()
        entries = [SubtitleEntry(text="Hello", start_time=0.0, end_time=2.0)]
        srt = engine.to_srt(entries)
        assert "1" in srt
        assert "00:00:00.000" in srt
        assert "Hello" in srt

    def test_to_srt_multiple(self):
        engine = SubtitleEngine()
        entries = [
            SubtitleEntry(text="First", start_time=0.0, end_time=2.0),
            SubtitleEntry(text="Second", start_time=2.0, end_time=4.0),
        ]
        srt = engine.to_srt(entries)
        assert srt.count("\n\n") >= 1

    def test_to_vtt(self):
        engine = SubtitleEngine()
        entries = [SubtitleEntry(text="Hello", start_time=0.0, end_time=2.0)]
        vtt = engine.to_vtt(entries)
        assert vtt.startswith("WEBVTT")
        assert "Hello" in vtt

    def test_total_duration(self):
        engine = SubtitleEngine()
        entries = [SubtitleEntry(end_time=5.0), SubtitleEntry(end_time=10.0)]
        assert engine.total_duration(entries) == 10.0

    def test_total_duration_empty(self):
        engine = SubtitleEngine()
        assert engine.total_duration([]) == 0.0

    def test_word_timings(self):
        engine = SubtitleEngine()
        entries = engine.generate_from_text("hello world", 0.0, 2.0)
        assert len(entries[0].word_timings) == 2

    def test_split_long_line(self):
        engine = SubtitleEngine()
        text = "a" * 60
        result = engine._split_long_line(text)
        assert "\n" in result

    def test_split_long_line_short(self):
        engine = SubtitleEngine()
        assert engine._split_long_line("short") == "short"

    def test_format_time(self):
        engine = SubtitleEngine()
        assert engine._format_time(0.0) == "00:00:00.000"
        assert engine._format_time(3661.5) == "01:01:01.500"

    def test_generate_highlight(self):
        engine = SubtitleEngine()
        entries = engine.generate_from_text("Hello", 0.0, 2.0, is_highlight=True)
        assert entries[0].is_highlight is True


# ── GraphicsEngine Tests ────────────────────────────────────────────────

class TestGraphicsEngine:
    def test_create_overlay(self):
        engine = GraphicsEngine()
        overlay = engine.create_overlay("episode_title", "Colors", 0.0)
        assert overlay is not None
        assert overlay.type == "title"
        assert overlay.text == "Colors"
        assert overlay.position == "center"
        assert overlay.style == "large_playful"

    def test_create_overlay_unknown_template(self):
        engine = GraphicsEngine()
        assert engine.create_overlay("nonexistent", "Text", 0.0) is None

    def test_create_overlay_custom_duration(self):
        engine = GraphicsEngine()
        overlay = engine.create_overlay("episode_title", "Hello", 0.0, custom_duration=6.0)
        assert overlay.end_time - overlay.start_time == 6.0

    def test_get_templates(self):
        engine = GraphicsEngine()
        templates = engine.get_templates()
        assert len(templates) == 11

    def test_list_template_keys(self):
        engine = GraphicsEngine()
        keys = engine.list_template_keys()
        assert "episode_title" in keys
        assert "celebration_stars" in keys
        assert len(keys) == 11


class TestGraphicOverlay:
    def test_defaults(self):
        g = GraphicOverlay()
        assert g.overlay_id == ""
        assert g.position == "center"

    def test_full_init(self):
        g = GraphicOverlay(overlay_id="G1", text="Hello", start_time=0.0, end_time=3.0)
        assert g.text == "Hello"
        assert g.end_time == 3.0


# ── IntroOutroEngine Tests ──────────────────────────────────────────────

class TestIntroTemplate:
    def test_defaults(self):
        t = IntroTemplate()
        assert t.total_duration == pytest.approx(1.5 + 1.0 + 3.5 + 2.0 + 2.0)

    def test_default_within_standard(self):
        t = IntroTemplate()
        assert t.is_within_standard()

    def test_custom_values(self):
        t = IntroTemplate(theme_music_duration=3.0, episode_title_duration=2.0)
        assert t.total_duration == pytest.approx(1.5 + 1.0 + 3.0 + 2.0 + 2.0)


class TestOutroTemplate:
    def test_defaults(self):
        t = OutroTemplate()
        assert t.total_duration == pytest.approx(4.0 + 2.0 + 2.0 + 3.0 + 2.0 + 5.0)

    def test_custom_values(self):
        t = OutroTemplate(goodbye_duration=3.0, end_screen_duration=4.0)
        assert t.total_duration == pytest.approx(4.0 + 3.0 + 2.0 + 3.0 + 2.0 + 4.0)


class TestIntroOutroEngine:
    def test_create_intro_default(self):
        engine = IntroOutroEngine()
        intro = engine.create_intro()
        assert isinstance(intro, IntroTemplate)
        assert intro.total_duration > 0

    def test_create_intro_with_title(self):
        engine = IntroOutroEngine()
        intro = engine.create_intro(episode_title="Colors")
        assert intro.total_duration > 0

    def test_create_intro_overrides(self):
        engine = IntroOutroEngine()
        intro = engine.create_intro(studio_logo_duration=3.0, theme_music_duration=4.0)
        assert intro.studio_logo_duration == 3.0
        assert intro.theme_music_duration == 4.0

    def test_create_outro_default(self):
        engine = IntroOutroEngine()
        outro = engine.create_outro()
        assert isinstance(outro, OutroTemplate)
        assert outro.total_duration > 0

    def test_create_outro_with_next_episode(self):
        engine = IntroOutroEngine()
        outro = engine.create_outro(next_episode="EP_002")
        assert outro.total_duration > 0

    def test_create_outro_overrides(self):
        engine = IntroOutroEngine()
        outro = engine.create_outro(lesson_recap_duration=5.0, subscribe_reminder_duration=3.0)
        assert outro.lesson_recap_duration == 5.0
        assert outro.subscribe_reminder_duration == 3.0

    def test_end_screen_templates(self):
        engine = IntroOutroEngine()
        templates = engine.end_screen_templates()
        assert "youtube_end_screen" in templates
        assert "basic_end_screen" in templates
        assert "subscribe" in templates["youtube_end_screen"]["elements"]


# ── ThumbnailSelector Tests ─────────────────────────────────────────────

class TestThumbnailSelector:
    def test_evaluate_candidate_default(self):
        sel = ThumbnailSelector()
        c = sel.evaluate_candidate()
        assert c.eye_contact_score == 0.5
        assert c.total_score == pytest.approx(0.5 * 0.25 + 0.5 * 0.20 + 0.5 * 0.20 + 0.5 * 0.15 + 0.5 * 0.10 + 0.5 * 0.10)

    def test_evaluate_candidate_high_scores(self):
        sel = ThumbnailSelector()
        c = sel.evaluate_candidate(eye_contact=1.0, brightness=1.0, emotion_clarity=1.0,
                                     contrast=1.0, educational_relevance=1.0, clutter=0.0)
        assert c.total_score == pytest.approx(1.0)

    def test_evaluate_candidate_low_scores(self):
        sel = ThumbnailSelector()
        c = sel.evaluate_candidate(eye_contact=0.0, brightness=0.0, emotion_clarity=0.0,
                                     contrast=0.0, educational_relevance=0.0, clutter=1.0)
        assert c.total_score == 0.0

    def test_select_best(self):
        sel = ThumbnailSelector()
        candidates = [
            sel.evaluate_candidate(eye_contact=0.3),
            sel.evaluate_candidate(eye_contact=0.9),
        ]
        best = sel.select_best(candidates)
        assert best.eye_contact_score == 0.9

    def test_select_best_empty(self):
        sel = ThumbnailSelector()
        assert sel.select_best([]) is None

    def test_rank_candidates(self):
        sel = ThumbnailSelector()
        candidates = [
            sel.evaluate_candidate(eye_contact=0.3),
            sel.evaluate_candidate(eye_contact=0.9),
            sel.evaluate_candidate(eye_contact=0.6),
        ]
        ranked = sel.rank_candidates(candidates)
        assert ranked[0].eye_contact_score == 0.9
        assert ranked[-1].eye_contact_score == 0.3


# ── ExportEngine Tests ──────────────────────────────────────────────────

class TestExportEngine:
    def test_list_presets(self):
        engine = ExportEngine()
        presets = engine.list_presets()
        assert len(presets) == 8

    def test_list_presets_has_master(self):
        engine = ExportEngine()
        presets = engine.list_presets()
        assert "master_archive" in presets

    def test_get_preset(self):
        engine = ExportEngine()
        preset = engine.get_preset("youtube")
        assert preset.resolution_width == 1920
        assert preset.resolution_height == 1080

    def test_get_preset_shorts(self):
        engine = ExportEngine()
        preset = engine.get_preset("shorts")
        assert preset.resolution_width == 1080
        assert preset.resolution_height == 1920

    def test_get_preset_unknown_falls_back(self):
        engine = ExportEngine()
        preset = engine.get_preset("nonexistent")
        assert preset.name == "YouTube"

    def test_add_preset(self):
        engine = ExportEngine()
        preset = ExportPreset(name="Test", resolution_width=640, resolution_height=480)
        engine.add_preset("test", preset)
        assert engine.get_preset("test").resolution_width == 640


# ── LocalizationEngine Tests ────────────────────────────────────────────

class TestLocalizationEngine:
    def test_list_languages(self):
        engine = LocalizationEngine()
        langs = engine.list_languages()
        assert "en" in langs
        assert "es" in langs
        assert len(langs) == 10

    def test_is_supported_true(self):
        engine = LocalizationEngine()
        assert engine.is_supported("en")
        assert engine.is_supported("fr")

    def test_is_supported_false(self):
        engine = LocalizationEngine()
        assert not engine.is_supported("xx")

    def test_create_package(self):
        engine = LocalizationEngine()
        pkg = engine.create_package("es", "Colores")
        assert pkg is not None
        assert pkg.language == "es"
        assert pkg.title == "Colores"
        assert pkg.audio_track == "audio_es"

    def test_create_package_unsupported(self):
        engine = LocalizationEngine()
        assert engine.create_package("xx", "Title") is None

    def test_create_package_default_title(self):
        engine = LocalizationEngine()
        pkg = engine.create_package("en")
        assert pkg.title == ""

    def test_localize_text(self):
        engine = LocalizationEngine()
        assert engine.localize_text("Hello", "es") == "[es] Hello"

    def test_localize_text_unsupported(self):
        engine = LocalizationEngine()
        assert engine.localize_text("Hello", "xx") == "Hello"


class TestLocalizationPackage:
    def test_defaults(self):
        p = LocalizationPackage()
        assert p.language == ""
        assert p.graphics == {}

    def test_full_init(self):
        p = LocalizationPackage(language="fr", title="Les Couleurs", subtitle_file="subtitles_fr")
        assert p.subtitle_file == "subtitles_fr"


# ── PostProductionQC Tests ──────────────────────────────────────────────

class TestPostProductionQC:
    def test_validate_timeline_invalid(self):
        qc = PostProductionQC()
        tl = MasterTimeline()
        result = qc.validate_timeline(tl)
        assert not result.passed
        assert len(result.errors) > 0

    def test_validate_timeline_valid(self):
        qc = PostProductionQC()
        tl = MasterTimeline(episode_id="EP_001", duration_seconds=30.0, frame_rate=24)
        tl.tracks.append(TimelineTrack(name="Video", events=[TimelineEvent()]))
        tl.tracks.append(TimelineTrack(name="Audio"))
        result = qc.validate_timeline(tl)
        assert result.passed, result.errors
        assert result.score == 100.0

    def test_validate_timeline_partial(self):
        qc = PostProductionQC()
        tl = MasterTimeline(episode_id="EP_001")
        result = qc.validate_timeline(tl)
        assert not result.passed
        assert result.score < 100.0

    def test_validate_exports_empty(self):
        qc = PostProductionQC()
        result = qc.validate_exports([])
        assert result.passed

    def test_validate_exports_valid(self):
        qc = PostProductionQC()
        presets = [ExportPreset(name="Test", resolution_width=1920, resolution_height=1080, frame_rate=24, format="mp4")]
        result = qc.validate_exports(presets)
        assert result.passed

    def test_validate_exports_invalid(self):
        qc = PostProductionQC()
        presets = [ExportPreset(name="Bad", resolution_width=0, resolution_height=0)]
        result = qc.validate_exports(presets)
        assert not result.passed

    def test_check_missing_clips_none(self):
        qc = PostProductionQC()
        tl = MasterTimeline()
        track = TimelineTrack(events=[TimelineEvent(clip_id="C1")])
        tl.tracks.append(track)
        assert qc.check_missing_clips(tl) == []

    def test_check_missing_clips_present(self):
        qc = PostProductionQC()
        tl = MasterTimeline()
        track = TimelineTrack(events=[TimelineEvent(clip_id=""), TimelineEvent(clip_id="C2")])
        tl.tracks.append(track)
        missing = qc.check_missing_clips(tl)
        assert len(missing) == 1

    def test_check_missing_clips_empty_track(self):
        qc = PostProductionQC()
        tl = MasterTimeline()
        tl.tracks.append(TimelineTrack())
        assert qc.check_missing_clips(tl) == []

    def test_check_transitions(self):
        qc = PostProductionQC()
        tl = MasterTimeline()
        track = TimelineTrack(events=[
            TimelineEvent(start_time=0.0, end_time=3.0),
            TimelineEvent(start_time=3.0, end_time=6.0),
        ])
        tl.tracks.append(track)
        issues = qc.check_transitions(tl)
        assert isinstance(issues, list)

    def test_validate_accessibility_safe_flashes(self):
        qc = PostProductionQC()
        result = qc.validate_accessibility(flash_events=[(0.0, 0.5)])
        assert result.passed is True
        assert result.checks["flashes_within_limits"] is True

    def test_validate_accessibility_excessive_flashes(self):
        qc = PostProductionQC()
        result = qc.validate_accessibility(flash_events=[(0.0, 0.05)])
        assert result.passed is False
        assert result.checks["flashes_within_limits"] is False
        assert len(result.errors) == 1

    def test_validate_accessibility_empty(self):
        qc = PostProductionQC()
        result = qc.validate_accessibility()
        assert result.passed is True


# ── ArchiveEngine Tests ─────────────────────────────────────────────────

class TestArchiveEngine:
    def test_create_record(self):
        engine = ArchiveEngine()
        record = engine.create_record(
            project_id="EP_001",
            master_video="masters/ep001.mp4",
            source_clips=["clip1.mp4", "clip2.mp4"],
        )
        assert record.project_id == "EP_001"
        assert record.master_video == "masters/ep001.mp4"
        assert len(record.source_clips) == 2
        assert record.archived_at != ""

    def test_create_record_minimal(self):
        engine = ArchiveEngine()
        record = engine.create_record(project_id="EP_001")
        assert record.project_id == "EP_001"
        assert record.source_clips == []

    def test_generate_metadata(self):
        engine = ArchiveEngine()
        meta = engine.generate_metadata(
            episode_id="EP_001",
            title="Colors",
            description="Learn about colors",
            keywords=["colors", "learning"],
            learning_objective="Identify colors",
            characters=["lily"],
            duration=120.0,
        )
        assert meta["episode_id"] == "EP_001"
        assert meta["title"] == "Colors"
        assert len(meta["keywords"]) == 2
        assert meta["duration_seconds"] == 120.0

    def test_generate_metadata_defaults(self):
        engine = ArchiveEngine()
        meta = engine.generate_metadata(episode_id="EP_001", title="Colors")
        assert meta["keywords"] == []
        assert meta["characters"] == []
        assert meta["version"] == 1

    def test_reproducibility_checklist_empty(self):
        engine = ArchiveEngine()
        record = ArchiveEngine().create_record(project_id="")
        checklist = engine.reproducibility_checklist(record)
        assert checklist["has_project_id"] is False
        assert checklist["has_master_video"] is False
        assert checklist["has_source_clips"] is False

    def test_reproducibility_checklist_full(self):
        engine = ArchiveEngine()
        record = engine.create_record(
            project_id="EP_001",
            master_video="master.mp4",
            source_clips=["c1.mp4"],
            audio_stems=["a1.wav"],
            subtitles=["subs.srt"],
            thumbnails=["thumb.jpg"],
            qc_report="qc.json",
        )
        checklist = engine.reproducibility_checklist(record)
        assert all(v for v in checklist.values())
