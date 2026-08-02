"""Tests for Phase 4 — Animation Bible & Motion System.

Covers the structured bible library (cycles, facial acting, gestures,
interactions, camera, transitions, physics, cloth, timing), the prompt
builder, bible-aware validation, and the MotionSystem integration.
"""

import os

import pytest

from src.animation import (
    AnimationClip, AnimationPlan, MotionCategory, FacialExpression,
    CameraMotion, TransitionType, LightingCondition, PhysicsMaterial,
)
from src.animation_bible import (
    AnimationBible, ANIMATION_NEGATIVE_BASE, MotionSystem,
    build_animation_prompt, category_negative, emotion_word,
    quality_checklist, MotionBrief,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def bible():
    return AnimationBible()


# ── Library contents ─────────────────────────────────────────────────────

class TestLibraryContents:
    def test_motion_library(self, bible):
        assert len(bible.list_motions()) == 21
        assert "idle" in bible.list_motions()
        assert "celebrate" in bible.list_motions()

    def test_walk_variants(self, bible):
        assert len(bible.list_walk_variants()) == 6
        normal = bible.walk_variant("normal_walk")
        assert normal.frames_per_step == 8
        assert normal.frames_per_stride == 16
        assert normal.speed_percent == 50
        assert normal.loopable

    def test_slow_walk_slower_than_fast_walk(self, bible):
        slow = bible.walk_variant("slow_walk")
        fast = bible.walk_variant("fast_walk")
        assert slow.frames_per_step > fast.frames_per_step
        assert slow.speed_percent < fast.speed_percent

    def test_run_variants_have_air_frames(self, bible):
        assert len(bible.list_run_variants()) == 4
        normal = bible.run_variant("normal_run")
        assert normal.air_frames == 2
        sprint = bible.run_variant("small_sprint")
        assert sprint.speed_percent == 95

    def test_jump_library(self, bible):
        assert len(bible.list_jumps()) == 6
        jump = bible.jump("standing_jump")
        assert jump.total_frames == 12
        assert jump.height_percent == 30
        assert len(jump.phases) == 4
        joy = bible.jump("jump_for_joy")
        assert joy.height_percent == 45

    def test_dance_library(self, bible):
        assert len(bible.list_dances()) == 7
        dance = bible.dance("circle_dance")
        assert dance.frames == 48
        assert dance.bpm == 120
        assert bible.dance("ribbon_dance").frames == 16

    def test_idle_layers(self, bible):
        assert len(bible.list_idle_layers()) == 5
        assert bible.idle_layer("breathing").frames == 120
        assert bible.idle_layer("weight_shift").frames == 144

    def test_expression_library(self, bible):
        assert len(bible.list_expressions()) == 13
        happy = bible.expression("happiness")
        assert len(happy.levels) == 5
        assert happy.levels[0].intensity == 1
        assert happy.levels[4].name == "ecstatic"
        # intensity is bounded 1-5
        for expr in bible.list_expressions():
            for level in bible.expression(expr).levels:
                assert 1 <= level.intensity <= 5

    def test_expression_level_lookup(self, bible):
        level = bible.expression_level("happiness", 3)
        assert level.name == "happy"
        assert bible.expression_level("happiness", 99) is not None  # clamps

    def test_blink_types(self, bible):
        assert bible.blink("normal").frames == "2-3"
        assert bible.blink("exaggerated").frames == "6-8"

    def test_mouth_actions(self, bible):
        talking = bible.mouth_action("talking")
        assert "4-6" in talking.timing
        assert bible.mouth_action("yawning") is not None

    def test_gesture_library(self, bible):
        assert len(bible.list_gestures()) == 23
        wave = bible.gesture("wave")
        assert "12" in wave.frames
        assert bible.gesture("point") is not None

    def test_interaction_library(self, bible):
        assert len(bible.list_interactions()) == 21
        door = bible.interaction("open_door")
        assert door.total_frames == 16
        assert len(door.phases) == 5
        assert bible.interaction("tie_shoelaces").total_frames == 60

    def test_interaction_sequence(self, bible):
        for name in bible.list_interactions():
            interaction = bible.interaction(name)
            phase_sum = sum(p.frames for p in interaction.phases)
            assert phase_sum <= interaction.total_frames or interaction.loopable

    def test_camera_shots(self, bible):
        assert len(bible.list_camera_shots()) == 12
        close = bible.camera_shot("close_up")
        assert close.min_frames == 24
        assert close.max_frames == 96
        assert bible.camera_shot("establishing").min_frames == 72

    def test_transitions(self, bible):
        assert len(bible.list_transitions()) == 11
        cross = bible.transition("cross_dissolve")
        assert cross.min_frames == 12
        assert cross.max_frames == 16
        assert bible.transition("cut").max_frames == 0

    def test_physics_rules(self, bible):
        gravity = bible.physics("gravity_strength")
        assert "85%" in gravity.value
        assert bible.physics("ball_bounce") is not None

    def test_cloth_elements(self, bible):
        assert len(bible.list_cloth_elements()) == 6
        dress = bible.cloth("dresses")
        assert dress.delay_frames == 4
        assert "15%" in dress.amplitude

    def test_pacing_and_holds(self, bible):
        assert bible.pacing("2yr").multiplier == 1.5
        assert bible.pacing("adult").multiplier == 0.4
        assert bible.shot_hold("medium").max_frames == 144
        assert bible.reaction("surprise_event").delay == "8-12 frames"

    def test_quality_checklist(self):
        checks = quality_checklist()
        assert len(checks) == 10
        assert "Natural blinking" in checks
        assert "Stable camera" in checks

    def test_cycle_frames_match_phase9_motion_engine(self, bible):
        from src.animation import MotionEngine
        engine = MotionEngine()
        for motion in bible.list_motions():
            cycle = bible.motion_cycle(motion)
            desc = engine.describe(MotionCategory(motion))
            assert desc["base_frame_count"] == cycle.base_frames
            assert desc["looping"] == cycle.looping


# ── Motion brief ─────────────────────────────────────────────────────────

class TestMotionBrief:
    def test_build_walk_brief(self, bible):
        brief = bible.build_motion_brief(
            motion="walk", duration_seconds=3.0, fps=24,
            expression="happy", camera_motion="track",
        )
        assert brief.motion == "walk"
        assert brief.frames_per_cycle == 8
        assert brief.loopable
        assert brief.cycles >= 1
        assert brief.expression == "happiness"
        assert brief.blink == "normal"
        assert brief.camera_shot == "tracking"
        assert brief.negative_prompt == ANIMATION_NEGATIVE_BASE

    def test_brief_cycle_count_matches_duration(self, bible):
        brief = bible.build_motion_brief(motion="walk", duration_seconds=2.0)
        assert brief.cycles == 6  # 2.0 * 24 / 8
        assert brief.duration_seconds == 2.0

    def test_brief_non_looping_single_cycle(self, bible):
        brief = bible.build_motion_brief(motion="jump", duration_seconds=5.0)
        assert brief.cycles == 1

    def test_brief_sleep_uses_slow_blink(self, bible):
        brief = bible.build_motion_brief(motion="sleep", expression="sleepy")
        assert brief.blink == "slow"

    def test_brief_dialogue_sets_talking(self, bible):
        brief = bible.build_motion_brief(motion="idle", dialogue="hello there")
        assert "mouth" in brief.pacing_note
        assert "4-6" in brief.pacing_note

    def test_brief_camera_mapping(self, bible):
        assert bible.camera_shot_for_motion("push_in") == "slow_push_in"
        assert bible.camera_shot_for_motion(CameraMotion.PAN) == "gentle_pan"

    def test_brief_to_dict(self, bible):
        brief = bible.build_motion_brief(motion="dance", duration_seconds=2.0)
        data = brief.to_dict()
        assert data["motion"] == "dance"
        assert set(data) == {
            "motion", "frames_per_cycle", "loopable", "cycles",
            "duration_seconds", "fps", "cycle_notes", "expression",
            "expression_level", "blink", "blink_frames", "camera_shot",
            "transition_in", "transition_out", "physics", "physics_notes",
            "secondary_elements", "pacing_note", "negative_prompt",
        }


# ── Bible-aware validation ───────────────────────────────────────────────

class TestBibleValidation:
    def test_validate_full_plan_passes(self, bible):
        plan = AnimationPlan(shot_id="S1", motion=MotionCategory.WALK,
                             expression=FacialExpression.HAPPY,
                             camera_motion=CameraMotion.TRACK,
                             transition_in=TransitionType.CROSSFADE,
                             transition_out=TransitionType.CROSSFADE,
                             duration_seconds=3.0)
        result = bible.validate_plan(plan)
        assert result["passed"]
        assert result["violations"] == []

    def test_validate_default_plan_passes(self, bible):
        # AnimationPlan() has valid bible defaults (idle/neutral/static/…)
        result = bible.validate_plan(AnimationPlan())
        assert result["passed"]

    def test_validate_none_plan_fails(self, bible):
        result = bible.validate_plan(None)
        assert not result["passed"]
        assert "No plan" in result["violations"][0]

    def test_validate_unknown_motion(self, bible):
        plan = AnimationPlan(shot_id="S1", motion="moonwalk", duration_seconds=3.0)
        result = bible.validate_plan(plan)
        assert not result["passed"]
        assert any("moonwalk" in v for v in result["violations"])

    def test_validate_unknown_expression(self, bible):
        plan = AnimationPlan(shot_id="S1", expression="rage", duration_seconds=3.0)
        result = bible.validate_plan(plan)
        assert not result["passed"]

    def test_validate_short_duration_warns(self, bible):
        plan = AnimationPlan(shot_id="S1", duration_seconds=0.8)
        result = bible.validate_plan(plan)
        assert result["passed"]
        assert any("1.5" in w for w in result["warnings"])

    def test_validate_too_short_duration_fails(self, bible):
        plan = AnimationPlan(shot_id="S1", duration_seconds=0.2)
        result = bible.validate_plan(plan)
        assert not result["passed"]

    def test_validate_clip_frame_rate(self, bible):
        clip = AnimationClip(clip_id="C1", animation_type=MotionCategory.WALK,
                             duration_seconds=3.0, frame_rate=15)
        result = bible.validate_clip(clip)
        assert not result["passed"]
        assert any("15" in v for v in result["violations"])

    def test_validate_clip_ok(self, bible):
        clip = AnimationClip(clip_id="C1", animation_type=MotionCategory.WALK,
                             duration_seconds=3.0, frame_rate=24)
        result = bible.validate_clip(clip)
        assert result["passed"]


# ── Prompt builder ───────────────────────────────────────────────────────

class TestPromptBuilder:
    def test_build_walk_prompt_structure(self):
        prompt = build_animation_prompt(
            character="Lily Bunny", action="walk", emotion="happiness",
            environment="Sunny Garden Playground", camera_shot="tracking",
            prop="red ball", template="walk",
        )
        assert prompt.startswith("Lily Bunny")
        assert "Sunny Garden Playground" in prompt
        assert "red ball" in prompt
        assert "tracking shot" in prompt
        assert "child-friendly" in prompt

    def test_prompt_placeholder_order(self):
        prompt = build_animation_prompt(
            character="Benny Bear", action="dance", emotion="excitement",
            environment="Music Room", camera_shot="medium",
        )
        char_idx = prompt.index("Benny Bear")
        env_idx = prompt.index("Music Room")
        camera_idx = prompt.index("medium shot")
        assert char_idx < env_idx < camera_idx

    def test_emotion_words(self):
        assert emotion_word("happiness") == "happily"
        assert emotion_word("curiosity") == "curiously"
        assert emotion_word("unknown") == "happily"

    def test_category_negative_layering(self):
        combined = category_negative("walk_run")
        assert ANIMATION_NEGATIVE_BASE in combined
        assert "foot skating" in combined
        alone = category_negative("dance", include_base=False)
        assert "robotic dance" in alone
        assert ANIMATION_NEGATIVE_BASE not in alone

    def test_unknown_category_falls_back_to_base(self):
        assert category_negative("nonsense") == ANIMATION_NEGATIVE_BASE


# ── MotionSystem integration ─────────────────────────────────────────────

class TestMotionSystem:
    def test_resolve_plan_ready(self):
        system = MotionSystem()
        plan = system.planner.plan_shot(
            "SH_001", motion=MotionCategory.WALK,
            expression=FacialExpression.HAPPY,
            camera_motion=CameraMotion.TRACK,
            dialogue="Let's go to the park!",
            duration_seconds=3.0,
        )
        result = system.resolve(plan, character="Lily Bunny",
                                environment="Sunny Garden Playground")
        assert result.ready
        assert isinstance(result.brief, MotionBrief)
        assert result.brief.motion == "walk"
        assert "motion" in result.engine_notes
        assert "facial" in result.engine_notes
        assert "camera" in result.engine_notes
        assert result.prompt.startswith("Lily Bunny")
        assert len(result.quality_checks) == 10

    def test_resolve_from_shot_data(self):
        system = MotionSystem()
        plan = system.plan_from_shot_data(
            shot_id="SH_002", animation="dance", emotion="happy",
            environment="Playground", duration=2.0,
        )
        result = system.resolve(plan)
        assert result.brief.motion == "dance"
        assert result.brief.loopable

    def test_resolve_many(self):
        system = MotionSystem()
        plans = [
            system.planner.plan_shot("A", motion=MotionCategory.WAVE),
            system.planner.plan_shot("B", motion=MotionCategory.SLEEP),
        ]
        results = system.resolve_many(plans)
        assert [r.plan.shot_id for r in results] == ["A", "B"]
        assert results[0].brief.motion == "wave"
        assert results[1].brief.motion == "sleep"

    def test_dialogue_uses_singing_negatives(self):
        system = MotionSystem()
        plan = system.planner.plan_shot("S", motion=MotionCategory.IDLE,
                                        dialogue="la la la")
        result = system.resolve(plan)
        assert "mismatched lip sync" in result.negative_prompt


# ── Doc <-> code consistency ─────────────────────────────────────────────

class TestDocConsistency:
    def test_all_doc_facts_pass(self, bible):
        report = bible.check_docs(os.path.join(ROOT, "Animation"))
        assert report.passed, report.to_dict()
        assert report.to_dict()["facts_checked"] >= 20

    def test_report_tracks_missing_file(self, bible, tmp_path):
        report = bible.check_docs(str(tmp_path))
        assert not report.passed
        assert len(report.missing_files) > 0
