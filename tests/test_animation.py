"""Tests for Phase 9 — AI Animation Pipeline & Motion Generation System.

Covers all 13 engine modules and supporting dataclasses.
"""

import pytest

from src.animation import (
    AnimationClip, AnimationPlan, MotionCategory, CameraMotion,
    FacialExpression, LipSyncTrack, Phoneme, TransitionType,
    LightingCondition, ParticleEffect, PhysicsMaterial,
    RenderJob, RenderStatus, AnimationValidationResult,
    AnimationPlanner, MotionEngine, FacialAnimationEngine,
    LipSyncEngine, CameraMotionEngine, PhysicsEngine,
    ParticleEngine, TransitionEngine, LightingAnimationEngine,
    RenderQueue, RenderPipeline, AnimationValidator,
    AnimationMonitor, MetricSnapshot,
    CharacterAnimationEngine, EyeAnimationEngine, BodyAnimationEngine,
    SecondaryMotionEngine, CrowdEngine, CrowdMember,
    SceneCompositionEngine, ShotComposition,
    ClipRegenerationEngine, ClipRegenerationRequest, ClipRegenerationResult,
)


# ── Model Tests ─────────────────────────────────────────────────────────

class TestAnimationClip:
    def test_defaults(self):
        clip = AnimationClip()
        assert clip.clip_id == ""
        assert clip.resolution_width == 1920
        assert clip.resolution_height == 1080
        assert clip.frame_rate == 24
        assert clip.approval_status == "pending"

    def test_total_frames(self):
        clip = AnimationClip(duration_seconds=3.0, frame_rate=24)
        assert clip.total_frames == 72

    def test_total_frames_zero(self):
        clip = AnimationClip()
        assert clip.total_frames == 0

    def test_aspect_ratio_16_9(self):
        clip = AnimationClip(resolution_width=1920, resolution_height=1080)
        assert clip.aspect_ratio == "16:9"

    def test_aspect_ratio_4_3(self):
        clip = AnimationClip(resolution_width=1024, resolution_height=768)
        assert clip.aspect_ratio == "4:3"

    def test_aspect_ratio_1_1(self):
        clip = AnimationClip(resolution_width=1024, resolution_height=1024)
        assert clip.aspect_ratio == "1:1"

    def test_aspect_ratio_9_16(self):
        clip = AnimationClip(resolution_width=1080, resolution_height=1920)
        assert clip.aspect_ratio == "9:16"


class TestAnimationPlan:
    def test_defaults(self):
        plan = AnimationPlan()
        assert plan.motion == MotionCategory.IDLE
        assert plan.expression == FacialExpression.NEUTRAL
        assert plan.camera_motion == CameraMotion.STATIC

    def test_has_lip_sync_true(self):
        plan = AnimationPlan(lip_sync=LipSyncTrack(dialogue="hello"))
        assert plan.has_lip_sync()

    def test_has_lip_sync_false(self):
        plan = AnimationPlan()
        assert not plan.has_lip_sync()

    def test_has_lip_sync_empty_dialogue(self):
        plan = AnimationPlan(lip_sync=LipSyncTrack(dialogue=""))
        assert not plan.has_lip_sync()


class TestLipSyncTrack:
    def test_total_phonemes(self):
        track = LipSyncTrack(phonemes=[Phoneme(), Phoneme()])
        assert track.total_phonemes() == 2

    def test_total_phonemes_empty(self):
        track = LipSyncTrack()
        assert track.total_phonemes() == 0


class TestEnumValues:
    def test_motion_categories(self):
        assert len(MotionCategory) == 21

    def test_camera_motions(self):
        assert len(CameraMotion) == 10

    def test_facial_expressions(self):
        assert len(FacialExpression) == 11

    def test_transition_types(self):
        assert len(TransitionType) == 7

    def test_lighting_conditions(self):
        assert len(LightingCondition) == 11

    def test_particle_effects(self):
        assert len(ParticleEffect) == 10

    def test_physics_materials(self):
        assert len(PhysicsMaterial) == 5

    def test_render_status(self):
        assert len(RenderStatus) == 6


# ── AnimationPlanner Tests ──────────────────────────────────────────────

class TestAnimationPlanner:
    def test_plan_shot_defaults(self):
        planner = AnimationPlanner()
        plan = planner.plan_shot(shot_id="SH_001")
        assert plan.shot_id == "SH_001"
        assert plan.motion == MotionCategory.IDLE
        assert plan.expression == FacialExpression.HAPPY
        assert plan.duration_seconds == 3.0

    def test_plan_shot_with_dialogue(self):
        planner = AnimationPlanner()
        plan = planner.plan_shot(shot_id="SH_001", dialogue="Hello!")
        assert plan.has_lip_sync()
        assert plan.lip_sync.dialogue == "Hello!"

    def test_plan_shot_with_weather_snow(self):
        planner = AnimationPlanner()
        plan = planner.plan_shot(shot_id="SH_001", weather="snow")
        assert ParticleEffect.SNOW in plan.particle_effects

    def test_plan_from_shot_data(self):
        planner = AnimationPlanner()
        plan = planner.plan_from_shot_data(
            shot_id="SH_001", animation="walk", emotion="happy",
            movement="track", lighting="golden_hour", duration=5.0,
            dialogue="Let's go!",
        )
        assert plan.shot_id == "SH_001"
        assert plan.motion == MotionCategory.WALK
        assert plan.expression == FacialExpression.HAPPY
        assert plan.camera_motion == CameraMotion.TRACK
        assert plan.duration_seconds == 5.0
        assert plan.has_lip_sync()

    def test_plan_from_shot_data_no_dialogue(self):
        planner = AnimationPlanner()
        plan = planner.plan_from_shot_data(shot_id="SH_001", animation="idle")
        assert not plan.has_lip_sync()

    def test_resolve_motion_unknown(self):
        planner = AnimationPlanner()
        plan = planner.plan_from_shot_data(shot_id="SH_001", animation="unknown_motion")
        assert plan.motion == MotionCategory.IDLE

    def test_resolve_emotion_unknown(self):
        planner = AnimationPlanner()
        plan = planner.plan_from_shot_data(shot_id="SH_001", emotion="unknown")
        assert plan.expression == FacialExpression.NEUTRAL

    def test_suggest_transitions(self):
        planner = AnimationPlanner()
        plan = planner.plan_shot(shot_id="SH_001")
        assert len(plan.expression_transitions) == 3

    def test_night_lighting_suggests_fireflies(self):
        planner = AnimationPlanner()
        plan = planner.plan_shot(shot_id="SH_001")
        plan.lighting = LightingCondition.NIGHT
        effects = planner._suggest_particles("clear", LightingCondition.NIGHT)
        assert ParticleEffect.FIREFLIES in effects


# ── MotionEngine Tests ──────────────────────────────────────────────────

class TestMotionEngine:
    def test_describe(self):
        engine = MotionEngine()
        desc = engine.describe(MotionCategory.WALK)
        assert desc["motion"] == "walk"
        assert desc["complexity"] == "moderate"
        assert desc["looping"] is True

    def test_describe_unknown_returns_idle_defaults(self):
        engine = MotionEngine()
        desc = engine.describe(MotionCategory.IDLE)
        assert desc["motion"] == "idle"

    def test_list_motions_all(self):
        engine = MotionEngine()
        all_motions = engine.list_motions()
        assert len(all_motions) == 21

    def test_list_motions_by_complexity(self):
        engine = MotionEngine()
        simple = engine.list_motions(complexity="simple")
        assert all(MotionEngine().describe(m)["complexity"] == "simple" for m in simple)

    def test_list_motions_looping(self):
        engine = MotionEngine()
        looping = engine.list_motions(looping=True)
        assert len(looping) > 0

    def test_estimate_duration(self):
        engine = MotionEngine()
        dur = engine.estimate_duration(MotionCategory.WALK, 24)
        assert dur == 8 / 24


# ── FacialAnimationEngine Tests ─────────────────────────────────────────

class TestFacialAnimationEngine:
    def test_describe_expression(self):
        engine = FacialAnimationEngine()
        desc = engine.describe_expression(FacialExpression.HAPPY)
        assert "eyes" in desc
        assert "mouth" in desc
        assert "squinted" in desc["eyes"]

    def test_describe_unknown_returns_neutral(self):
        engine = FacialAnimationEngine()
        desc = engine.describe_expression(FacialExpression.NEUTRAL)
        assert desc["eyes"] == "open, relaxed"

    def test_list_expressions(self):
        engine = FacialAnimationEngine()
        assert len(engine.list_expressions()) == 11

    def test_blink_interval_default(self):
        engine = FacialAnimationEngine()
        interval = engine.suggest_blink_interval(FacialExpression.HAPPY)
        assert interval[0] > 0
        assert interval[1] > interval[0]

    def test_blink_interval_excited(self):
        engine = FacialAnimationEngine()
        interval = engine.suggest_blink_interval(FacialExpression.EXCITED)
        assert interval[0] >= 6.0

    def test_blend_expressions(self):
        engine = FacialAnimationEngine()
        blend = engine.blend_expressions(FacialExpression.HAPPY, FacialExpression.GENTLE_SADNESS, 0.3)
        assert isinstance(blend, dict)


# ── LipSyncEngine Tests ─────────────────────────────────────────────────

class TestLipSyncEngine:
    def test_generate_simple_word(self):
        engine = LipSyncEngine()
        track = engine.generate("hello", 2.0)
        assert track.dialogue == "hello"
        assert track.duration == 2.0
        assert len(track.phonemes) == 5

    def test_generate_empty(self):
        engine = LipSyncEngine()
        track = engine.generate("", 1.0)
        assert track.duration == 1.0
        assert track.total_phonemes() == 0

    def test_generate_multiple_words(self):
        engine = LipSyncEngine()
        track = engine.generate("hello world", 4.0)
        assert track.total_phonemes() == 10  # hello=5 + world=5

    def test_generate_phoneme_timing(self):
        engine = LipSyncEngine()
        track = engine.generate("hi", 2.0)
        assert len(track.phonemes) == 2
        assert track.phonemes[0].start_time >= 0
        assert track.phonemes[-1].end_time <= 2.0

    def test_generate_mouth_shapes(self):
        engine = LipSyncEngine()
        track = engine.generate("a", 1.0)
        assert track.phonemes[0].mouth_shape == "open_wide"

    def test_estimate_duration(self):
        engine = LipSyncEngine()
        dur = engine.estimate_duration("hello world", 2.5)
        assert dur == 2.0 / 2.5

    def test_estimate_duration_empty(self):
        engine = LipSyncEngine()
        assert engine.estimate_duration("") == 0.0


# ── CameraMotionEngine Tests ────────────────────────────────────────────

class TestCameraMotionEngine:
    def test_describe(self):
        engine = CameraMotionEngine()
        desc = engine.describe(CameraMotion.PAN)
        assert "description" in desc
        assert "rotates horizontally" in desc["description"]

    def test_describe_unknown(self):
        engine = CameraMotionEngine()
        desc = engine.describe(CameraMotion.STATIC)
        assert desc["speed"] == "none"

    def test_list_motions(self):
        engine = CameraMotionEngine()
        assert len(engine.list_motions()) == 10

    def test_estimate_duration(self):
        engine = CameraMotionEngine()
        est = engine.estimate_duration(CameraMotion.PUSH_IN, 10.0)
        assert est["motion_duration"] == 5.0
        assert est["hold_duration"] == 5.0


# ── PhysicsEngine Tests ─────────────────────────────────────────────────

class TestPhysicsEngine:
    def test_describe(self):
        engine = PhysicsEngine()
        desc = engine.describe(PhysicsMaterial.BOUNCY)
        assert desc["bounce_factor"] == 0.8

    def test_describe_unknown(self):
        engine = PhysicsEngine()
        desc = engine.describe(PhysicsMaterial.SOFT)
        assert desc["bounce_factor"] == 0.3

    def test_list_materials(self):
        engine = PhysicsEngine()
        assert len(engine.list_materials()) == 5

    def test_simulate_impact(self):
        engine = PhysicsEngine()
        result = engine.simulate_impact(PhysicsMaterial.BOUNCY, 2.0)
        assert result["bounce_height"] == 1.6
        assert result["bounces_to_rest"] > 0

    def test_simulate_impact_heavy(self):
        engine = PhysicsEngine()
        result = engine.simulate_impact(PhysicsMaterial.HEAVY, 2.0)
        assert result["bounce_height"] < 0.5


# ── ParticleEngine Tests ────────────────────────────────────────────────

class TestParticleEngine:
    def test_describe(self):
        engine = ParticleEngine()
        desc = engine.describe(ParticleEffect.SNOW)
        assert desc["count"] == 40
        assert desc["motion"] == "gentle_fall"

    def test_describe_unknown(self):
        engine = ParticleEngine()
        desc = engine.describe(ParticleEffect.SPARKLES)
        assert desc["count"] == 12

    def test_list_effects(self):
        engine = ParticleEngine()
        assert len(engine.list_effects()) == 10

    def test_suggest_for_mood(self):
        engine = ParticleEngine()
        effects = engine.suggest_for_mood("celebratory")
        assert ParticleEffect.CONFETTI in effects

    def test_suggest_for_mood_unknown(self):
        engine = ParticleEngine()
        effects = engine.suggest_for_mood("unknown_mood")
        assert len(effects) > 0


# ── TransitionEngine Tests ──────────────────────────────────────────────

class TestTransitionEngine:
    def test_describe(self):
        engine = TransitionEngine()
        desc = engine.describe(TransitionType.CROSSFADE)
        assert "duration" in desc
        assert desc["duration"] == 0.8

    def test_describe_unknown(self):
        engine = TransitionEngine()
        desc = engine.describe(TransitionType.FADE)
        assert desc["duration"] == 0.5

    def test_list_transitions(self):
        engine = TransitionEngine()
        assert len(engine.list_transitions()) == 7

    def test_suggest_for_mood(self):
        engine = TransitionEngine()
        assert engine.suggest_for_mood("magical") == TransitionType.DISSOLVE
        assert engine.suggest_for_mood("happy") == TransitionType.CROSSFADE

    def test_estimate_duration(self):
        engine = TransitionEngine()
        assert engine.estimate_duration(TransitionType.PAGE_TURN) == 1.2


# ── LightingAnimationEngine Tests ───────────────────────────────────────

class TestLightingAnimationEngine:
    def test_describe(self):
        engine = LightingAnimationEngine()
        desc = engine.describe(LightingCondition.GOLDEN_HOUR)
        assert desc["color_temperature"] == "warm_3500K"
        assert desc["brightness"] == 0.7

    def test_describe_unknown(self):
        engine = LightingAnimationEngine()
        desc = engine.describe(LightingCondition.MORNING)
        assert desc["color_temperature"] == "warm_4500K"

    def test_list_conditions(self):
        engine = LightingAnimationEngine()
        assert len(engine.list_conditions()) == 11

    def test_transition_time_same(self):
        engine = LightingAnimationEngine()
        assert engine.transition_time(LightingCondition.MORNING, LightingCondition.MORNING) == 0.0

    def test_transition_time_rapid(self):
        engine = LightingAnimationEngine()
        assert engine.transition_time(LightingCondition.MORNING, LightingCondition.NOON) == 1.0

    def test_transition_time_slow(self):
        engine = LightingAnimationEngine()
        assert engine.transition_time(LightingCondition.MORNING, LightingCondition.NIGHT) == 2.5


# ── RenderQueue Tests ───────────────────────────────────────────────────

class TestRenderQueue:
    def test_enqueue(self):
        queue = RenderQueue()
        job = queue.enqueue("clip_001", priority=5)
        assert job.clip_id == "clip_001"
        assert job.priority == 5
        assert job.status == RenderStatus.QUEUED
        assert job.job_id.startswith("RENDER_clip_001")

    def test_dequeue(self):
        queue = RenderQueue()
        queue.enqueue("clip_001", priority=1)
        queue.enqueue("clip_002", priority=10)
        job = queue.dequeue()
        assert job.clip_id == "clip_002"  # Higher priority first

    def test_dequeue_empty(self):
        queue = RenderQueue()
        assert queue.dequeue() is None

    def test_complete(self):
        queue = RenderQueue()
        job = queue.enqueue("clip_001")
        queue.dequeue()
        assert queue.complete(job.job_id)
        assert queue.get_job(job.job_id).status == RenderStatus.COMPLETED

    def test_complete_nonexistent(self):
        queue = RenderQueue()
        assert not queue.complete("nonexistent")

    def test_fail(self):
        queue = RenderQueue()
        job = queue.enqueue("clip_001")
        queue.fail(job.job_id, "error occurred")
        assert queue.get_job(job.job_id).status == RenderStatus.FAILED

    def test_approve(self):
        queue = RenderQueue()
        job = queue.enqueue("clip_001")
        queue.dequeue()
        queue.complete(job.job_id)
        assert queue.approve(job.job_id)

    def test_approve_not_completed(self):
        queue = RenderQueue()
        job = queue.enqueue("clip_001")
        assert not queue.approve(job.job_id)

    def test_reject(self):
        queue = RenderQueue()
        job = queue.enqueue("clip_001")
        assert queue.reject(job.job_id)

    def test_pending_count(self):
        queue = RenderQueue()
        assert queue.pending_count() == 0
        queue.enqueue("clip_001")
        queue.enqueue("clip_002")
        assert queue.pending_count() == 2

    def test_total_count(self):
        queue = RenderQueue()
        queue.enqueue("clip_001")
        queue.enqueue("clip_002")
        assert queue.total_count() == 2

    def test_list_by_status(self):
        queue = RenderQueue()
        queue.enqueue("clip_001")
        assert len(queue.list_by_status(RenderStatus.QUEUED)) == 1
        assert len(queue.list_by_status(RenderStatus.COMPLETED)) == 0

    def test_get_job(self):
        queue = RenderQueue()
        job = queue.enqueue("clip_001")
        assert queue.get_job(job.job_id) is job

    def test_get_job_nonexistent(self):
        queue = RenderQueue()
        assert queue.get_job("nonexistent") is None


# ── RenderPipeline Tests ────────────────────────────────────────────────

class TestRenderPipeline:
    def test_submit_shot(self):
        pipeline = RenderPipeline()
        job = pipeline.submit_shot("clip_001")
        assert job.clip_id == "clip_001"

    def test_submit_batch(self):
        pipeline = RenderPipeline()
        jobs = pipeline.submit_batch(["clip_001", "clip_002"])
        assert len(jobs) == 2

    def test_process_next(self):
        pipeline = RenderPipeline()
        pipeline.submit_shot("clip_001")
        job = pipeline.process_next()
        assert job is not None
        assert job.status == RenderStatus.RENDERING
        assert pipeline.active_count() == 1

    def test_process_next_empty(self):
        pipeline = RenderPipeline()
        assert pipeline.process_next() is None

    def test_complete_job(self):
        pipeline = RenderPipeline()
        job = pipeline.submit_shot("clip_001")
        pipeline.process_next()
        assert pipeline.complete_job(job.job_id)
        assert pipeline.active_count() == 0

    def test_fail_job(self):
        pipeline = RenderPipeline()
        job = pipeline.submit_shot("clip_001")
        pipeline.process_next()
        assert pipeline.fail_job(job.job_id, "error")
        assert pipeline.active_count() == 0


# ── AnimationValidator Tests ────────────────────────────────────────────

class TestAnimationValidator:
    def test_validate_clip_full(self):
        validator = AnimationValidator()
        clip = AnimationClip(
            clip_id="CLIP_001", episode="S01E01", duration_seconds=5.0,
            characters=["lily"], environment="park",
            prompt_version="V1", seed=42,
            animation_type=MotionCategory.WALK,
        )
        result = validator.validate_clip(clip)
        assert result.passed, result.errors
        assert result.score == 100.0

    def test_validate_clip_missing_fields(self):
        validator = AnimationValidator()
        clip = AnimationClip()
        result = validator.validate_clip(clip)
        assert not result.passed
        assert len(result.errors) > 0

    def test_validate_clip_bad_frame_rate(self):
        validator = AnimationValidator()
        clip = AnimationClip(
            clip_id="X", episode="S01", duration_seconds=3.0,
            characters=["lily"], environment="park",
            prompt_version="V1", seed=42,
            frame_rate=15,
        )
        result = validator.validate_clip(clip)
        assert not result.passed

    def test_validate_plan_full(self):
        validator = AnimationValidator()
        plan = AnimationPlan(shot_id="SH_001", duration_seconds=3.0)
        result = validator.validate_plan(plan)
        assert result.passed

    def test_validate_plan_empty(self):
        validator = AnimationValidator()
        plan = AnimationPlan()
        result = validator.validate_plan(plan)
        assert not result.passed

    def test_validation_checks_structure(self):
        validator = AnimationValidator()
        result = validator.validate_clip(AnimationClip())
        assert isinstance(result.checks, dict)
        assert isinstance(result.errors, list)
        assert isinstance(result.score, float)


# ── AnimationMonitor Tests ──────────────────────────────────────────────

class TestAnimationMonitor:
    def test_record_render(self):
        monitor = AnimationMonitor()
        monitor.record_render(5.0, True)
        assert monitor.total_renders() == 1
        assert monitor.failed_renders() == 0

    def test_record_render_failure(self):
        monitor = AnimationMonitor()
        monitor.record_render(5.0, False)
        assert monitor.total_renders() == 1
        assert monitor.failed_renders() == 1

    def test_record_retry(self):
        monitor = AnimationMonitor()
        monitor.record_retry()
        assert monitor.retry_count() == 1

    def test_snapshot(self):
        monitor = AnimationMonitor()
        snap = monitor.snapshot(gpu_utilization=0.75, character_score=0.92)
        assert snap.gpu_utilization == 0.75
        assert snap.character_consistency_score == 0.92
        assert snap.timestamp != ""

    def test_snapshot_tracks_metrics(self):
        monitor = AnimationMonitor()
        monitor.record_render(10.0, True)
        monitor.record_render(5.0, False)
        snap = monitor.snapshot()
        assert snap.failed_generations == 1

    def test_average_render_time(self):
        monitor = AnimationMonitor()
        monitor.record_render(10.0, True)
        monitor.record_render(20.0, True)
        snap1 = monitor.snapshot()
        snap2 = monitor.snapshot()
        assert monitor.average_render_time() >= 0

    def test_completion_rate(self):
        monitor = AnimationMonitor()
        assert monitor.completion_rate() == 1.0
        monitor.record_render(5.0, True)
        monitor.record_render(5.0, False)
        assert monitor.completion_rate() == 0.5

    def test_history(self):
        monitor = AnimationMonitor()
        monitor.snapshot()
        monitor.snapshot()
        assert len(monitor.history()) == 2

    def test_latest(self):
        monitor = AnimationMonitor()
        assert monitor.latest() is None
        monitor.snapshot(quality_score=0.85)
        assert monitor.latest().animation_quality_score == 0.85

    def test_clear(self):
        monitor = AnimationMonitor()
        monitor.record_render(5.0, False)
        monitor.snapshot()
        monitor.clear()
        assert monitor.total_renders() == 0
        assert monitor.failed_renders() == 0
        assert monitor.history() == []


# ── Eye Animation Tests ─────────────────────────────────────────────────

class TestEyeAnimationEngine:
    def test_list_behaviors(self):
        engine = EyeAnimationEngine()
        behaviors = engine.list_behaviors()
        assert "blink_frequency" in behaviors
        assert "look_at_speaker" in behaviors
        assert "reading_movement" in behaviors

    def test_describe(self):
        engine = EyeAnimationEngine()
        info = engine.describe("eye_tracking")
        assert "smoothly track" in info["description"]

    def test_suggest_pattern(self):
        engine = EyeAnimationEngine()
        pattern = engine.suggest_pattern("focus_target", "apple")
        assert pattern.behavior == "focus_target"
        assert pattern.target == "apple"

    def test_suggest_pattern_unknown_falls_back(self):
        engine = EyeAnimationEngine()
        pattern = engine.suggest_pattern("unknown")
        assert pattern.behavior == "blink_frequency"

    def test_blink_schedule(self):
        engine = EyeAnimationEngine()
        blinks = engine.blink_schedule(20.0)
        assert len(blinks) > 0
        assert blinks[0][0] < blinks[0][1]

    def test_focus_target(self):
        engine = EyeAnimationEngine()
        pattern = engine.focus_target("balloon")
        assert pattern.target == "balloon"

    def test_look_at_speaker(self):
        engine = EyeAnimationEngine()
        pattern = engine.look_at("lily", kind="speaker")
        assert pattern.behavior == "look_at_speaker"

    def test_look_at_object(self):
        engine = EyeAnimationEngine()
        pattern = engine.look_at("clock")
        assert pattern.behavior == "look_at_object"

    def test_reading_movement(self):
        engine = EyeAnimationEngine()
        sweeps = engine.reading_movement(6.0, lines=2)
        assert len(sweeps) == 6
        assert sweeps[0][1] == "left"


# ── Body Animation Tests ────────────────────────────────────────────────

class TestBodyAnimationEngine:
    def test_profile_walk(self):
        engine = BodyAnimationEngine()
        profile = engine.profile("walk")
        assert profile.motion == "walk"
        assert profile.arm_swing == "opposite_phase"
        assert profile.foot_placement == "heel_toe"

    def test_profile_unknown_defaults_to_idle(self):
        engine = BodyAnimationEngine()
        assert engine.profile("unknown").motion == "idle"

    def test_list_components(self):
        engine = BodyAnimationEngine()
        components = engine.list_components()
        assert "breathing" in components
        assert "weight_shifts" in components

    def test_describe(self):
        engine = BodyAnimationEngine()
        info = engine.describe("run")
        assert info["motion"] == "run"
        assert info["components"]["arm_swing"] == "high_energy"

    def test_avoid_robotic(self):
        engine = BodyAnimationEngine()
        tips = engine.avoid_robotic()
        assert "breathing_offset" in tips


# ── Secondary Motion Tests ──────────────────────────────────────────────

class TestSecondaryMotionEngine:
    def test_list_elements(self):
        engine = SecondaryMotionEngine()
        elements = engine.list_elements()
        assert "hair" in elements
        assert "scarves" in elements
        assert "balloons" in elements

    def test_describe_element(self):
        engine = SecondaryMotionEngine()
        info = engine.describe_element("hair")
        assert "follows head movement" in info["description"]

    def test_suggest_elements_context(self):
        engine = SecondaryMotionEngine()
        elements = engine.suggest_elements("winter")
        assert "scarves" in elements

    def test_intensity_for_motion(self):
        engine = SecondaryMotionEngine()
        assert engine.intensity_for_motion("run") > engine.intensity_for_motion("idle")

    def test_animate(self):
        engine = SecondaryMotionEngine()
        element = engine.animate("tails", "walk")
        assert element.element == "tails"
        assert element.motion_type == "follow_through"

    def test_animate_unknown(self):
        engine = SecondaryMotionEngine()
        assert engine.animate("rocket") is None


# ── Character Animation Engine Tests ────────────────────────────────────

class TestCharacterAnimationEngine:
    def test_build_performance(self):
        engine = CharacterAnimationEngine()
        perf = engine.build_performance("walk", "happy", "park")
        assert perf["motion"] == "walk"
        assert perf["body"]["motion"] == "walk"
        assert "eyes" in perf
        assert len(perf["secondary_elements"]) > 0

    def test_list_engines(self):
        engine = CharacterAnimationEngine()
        assert engine.list_engines() == ["eye_animation", "body_animation", "secondary_motion"]


# ── Crowd Engine Tests ──────────────────────────────────────────────────

class TestCrowdEngine:
    def test_build_crowd(self):
        engine = CrowdEngine()
        crowd = engine.build_crowd(4)
        assert len(crowd) == 4
        assert all(isinstance(m, CrowdMember) for m in crowd)

    def test_build_crowd_zero(self):
        engine = CrowdEngine()
        assert engine.build_crowd(0) == []

    def test_members_subtle(self):
        engine = CrowdEngine()
        crowd = engine.build_crowd(5)
        assert all(m.background_level <= engine.SUBTLETY_LEVEL for m in crowd)

    def test_suggest_activities(self):
        engine = CrowdEngine()
        activities = engine.suggest_activities("park")
        assert "play" in activities

    def test_list_activities(self):
        engine = CrowdEngine()
        activities = engine.list_activities()
        assert "talk_silently" in activities
        assert len(activities) == 8

    def test_describe(self):
        engine = CrowdEngine()
        info = engine.describe()
        assert info["subtlety_level"] == engine.SUBTLETY_LEVEL
        assert "subtle" in info["principle"]


# ── Scene Composition Engine Tests ──────────────────────────────────────

class TestSceneCompositionEngine:
    def test_evaluate(self):
        engine = SceneCompositionEngine()
        shot = engine.evaluate("left_third")
        assert isinstance(shot, ShotComposition)
        assert shot.subject_position == "left_third"
        assert shot.camera == "eye_level"

    def test_evaluate_lead_space(self):
        engine = SceneCompositionEngine()
        shot = engine.evaluate("left_third")
        assert shot.lead_space == "right"
        shot = engine.evaluate("right_third")
        assert shot.lead_space == "left"

    def test_active_principles(self):
        engine = SceneCompositionEngine()
        principles = engine.active_principles("eye_level")
        assert principles["rule_of_thirds"] is True
        assert principles["eye_level"] is True

    def test_rule_of_thirds(self):
        engine = SceneCompositionEngine()
        x, y = engine.rule_of_thirds(0.2, 0.8)
        assert x == pytest.approx(round(1 / 3, 3))
        assert y == pytest.approx(round(2 / 3, 3))

    def test_stage_depth(self):
        engine = SceneCompositionEngine()
        layers = engine.stage_depth("midground")
        assert len(layers) == 3
        assert "background" in layers

    def test_list_principles(self):
        engine = SceneCompositionEngine()
        assert "depth_staging" in engine.list_principles()


# ── Clip Regeneration Tests ─────────────────────────────────────────────

class TestClipRegenerationEngine:
    def test_list_reasons(self):
        engine = ClipRegenerationEngine()
        reasons = engine.list_reasons()
        assert "jarring_motion" in reasons
        assert "style_mismatch" in reasons

    def test_reason_description(self):
        engine = ClipRegenerationEngine()
        assert "easing naturally" in engine.reason_description("jarring_motion")

    def test_request_regeneration(self):
        engine = ClipRegenerationEngine()
        request = engine.request_regeneration("C1", "timing_off", "too fast")
        assert request.clip_id == "C1"
        assert request.reason == "timing_off"
        assert request.notes == "too fast"

    def test_request_unknown_reason(self):
        engine = ClipRegenerationEngine()
        request = engine.request_regeneration("C1", "unknown")
        assert request.reason == "jarring_motion"

    def test_regenerate(self):
        engine = ClipRegenerationEngine()
        request = ClipRegenerationRequest(clip_id="C1", reason="poor_expression")
        result = engine.regenerate(request)
        assert result.regenerated is True
        assert result.timeline_intact is True
        assert result.clip_id == "C1"

    def test_regenerate_exhausted_attempts(self):
        engine = ClipRegenerationEngine()
        request = ClipRegenerationRequest(clip_id="C1", reason="poor_expression")
        result = engine.regenerate(request, attempt=engine.MAX_ATTEMPTS + 1)
        assert result.regenerated is False
        assert "failed" in result.message

    def test_summarize(self):
        engine = ClipRegenerationEngine()
        summary = engine.summarize("C1", "style_mismatch", "wrong palette")
        assert summary["clip_id"] == "C1"
        assert summary["notes"] == "wrong palette"
