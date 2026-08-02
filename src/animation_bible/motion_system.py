"""Motion System — ties the Phase 4 Animation Bible to the Phase 9 pipeline.

Given an :class:`~src.animation.models.AnimationPlan`, the MotionSystem
resolves it against the bible standards into a :class:`MotionBrief`, attaches
the Phase 9 engine descriptions, validates it against both the bible and the
pipeline validator, and produces the render-ready prompt + negative prompt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from src.animation import (
    AnimationPlan, AnimationPlanner, AnimationValidator,
    CameraMotionEngine, FacialAnimationEngine, MotionEngine,
    PhysicsEngine, TransitionEngine,
)

from .bible import AnimationBible
from .models import MotionBrief
from .prompts import build_animation_prompt, category_negative, quality_checklist


@dataclass
class MotionSystemResult:
    plan: AnimationPlan
    brief: MotionBrief
    engine_notes: dict = field(default_factory=dict)
    bible_validation: dict = field(default_factory=dict)
    pipeline_validation: Optional[object] = None
    prompt: str = ""
    negative_prompt: str = ""
    quality_checks: list[str] = field(default_factory=list)

    @property
    def ready(self) -> bool:
        return (
            self.bible_validation.get("passed", False)
            and self.pipeline_validation is not None
            and self.pipeline_validation.passed
        )


class MotionSystem:
    def __init__(self) -> None:
        self.bible = AnimationBible()
        self.planner = AnimationPlanner()
        self.validator = AnimationValidator()
        self._motion_engine = MotionEngine()
        self._facial_engine = FacialAnimationEngine()
        self._camera_engine = CameraMotionEngine()
        self._transition_engine = TransitionEngine()
        self._physics_engine = PhysicsEngine()

    def plan_from_shot_data(self, **kwargs) -> AnimationPlan:
        """Build a plan from story/shot data (strings), like the pipeline does."""
        return self.planner.plan_from_shot_data(**kwargs)

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def resolve(self, plan: AnimationPlan, character: str = "", environment: str = "") -> MotionSystemResult:
        brief = self.bible.build_motion_brief(
            motion=plan.motion,
            expression=plan.expression,
            camera_motion=plan.camera_motion,
            transition_in=plan.transition_in,
            transition_out=plan.transition_out,
            physics=plan.physics_material,
            duration_seconds=plan.duration_seconds,
            dialogue=plan.lip_sync.dialogue if plan.has_lip_sync() else "",
        )

        engine_notes = self._engine_notes(plan)

        bible_validation = self.bible.validate_plan(plan)
        pipeline_validation = self.validator.validate_plan(plan)

        prompt = self._build_prompt(plan, brief, character, environment)
        negative = category_negative(self._negative_category(plan))

        return MotionSystemResult(
            plan=plan,
            brief=brief,
            engine_notes=engine_notes,
            bible_validation=bible_validation,
            pipeline_validation=pipeline_validation,
            prompt=prompt,
            negative_prompt=negative,
            quality_checks=quality_checklist(),
        )

    def resolve_many(
        self, plans: list[AnimationPlan], character: str = "", environment: str = ""
    ) -> list[MotionSystemResult]:
        return [self.resolve(p, character, environment) for p in plans]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _engine_notes(self, plan: AnimationPlan) -> dict:
        notes: dict = {}
        try:
            notes["motion"] = self._motion_engine.describe(plan.motion)
        except Exception:
            pass
        try:
            notes["facial"] = self._facial_engine.describe_expression(plan.expression)
        except Exception:
            pass
        try:
            notes["camera"] = self._camera_engine.describe(plan.camera_motion)
        except Exception:
            pass
        try:
            notes["transition_in"] = self._transition_engine.describe(plan.transition_in)
        except Exception:
            pass
        try:
            notes["physics"] = self._physics_engine.describe(plan.physics_material)
        except Exception:
            pass
        return notes

    def _build_prompt(self, plan: AnimationPlan, brief: MotionBrief,
                      character: str, environment: str) -> str:
        template = "walk"
        if plan.motion.value in ("idle", "walk", "run", "jump", "dance",
                                 "wave", "clap", "hug", "sleep", "read", "celebrate"):
            template = plan.motion.value
        emotion = brief.expression
        dialogue_hint = ""
        if plan.has_lip_sync():
            dialogue_hint = "while speaking"
        details = tuple(d for d in (dialogue_hint,) if d)
        return build_animation_prompt(
            character=character or "the character",
            action=plan.motion.value,
            emotion=emotion,
            environment=environment,
            camera_shot=brief.camera_shot,
            details=details,
            template=template,
        )

    def _negative_category(self, plan: AnimationPlan) -> str:
        motion = plan.motion.value
        if motion in ("walk", "run", "skip"):
            return "walk_run"
        if motion == "dance":
            return "dance"
        if motion in ("jump",):
            return "jump"
        if motion in ("eat", "drink", "read", "write", "play"):
            return "interaction"
        if plan.has_lip_sync():
            return "singing"
        if motion in ("laugh", "cry", "celebrate"):
            return "facial"
        return "base"
