"""AnimationBible — query facade for the Phase 4 Animation Bible.

Provides programmatic access to every quantitative standard defined in the
`Animation/` markdown bibles, plus bible-aware validation of animation plans
and resolution of a plan into a concrete :class:`MotionBrief`.
"""

from __future__ import annotations

import math
import os
import re
from typing import Optional, Union

from . import libraries as lib
from .models import (
    BlinkType, CameraShot, ClothElement, DanceLoop, DocConsistencyReport,
    DocFact, ExpressionLevel, FacialExpression, Gesture, IdleLayer,
    Interaction, JumpCycle, LocomotionVariant, MotionBrief, MotionCycle,
    MouthAction, PacingStandard, PhysicsRule, ReactionStandard,
    SceneTransition, ShotHold,
)
from .prompts import ANIMATION_NEGATIVE_BASE


class AnimationBible:
    def __init__(self) -> None:
        self.master_frame_rate = lib.MASTER_FRAME_RATE
        self.export_frame_rate = lib.EXPORT_FRAME_RATE
        self.valid_frame_rates = lib.VALID_FRAME_RATES

        self._cycles = {c.motion: c for c in lib.MOTION_CYCLES}
        self._walks = {v.name: v for v in lib.WALK_VARIANTS}
        self._runs = {v.name: v for v in lib.RUN_VARIANTS}
        self._jumps = {j.name: j for j in lib.JUMP_CYCLES}
        self._dances = {d.name: d for d in lib.DANCE_LOOPS}
        self._idle = {i.name: i for i in lib.IDLE_LAYERS}
        self._expressions = {e.emotion: e for e in lib.FACIAL_EXPRESSIONS}
        self._blinks = {b.name: b for b in lib.BLINK_TYPES}
        self._mouth_actions = {m.name: m for m in lib.MOUTH_ACTIONS}
        self._gestures = {g.name: g for g in lib.GESTURES}
        self._interactions = {i.name: i for i in lib.INTERACTIONS}
        self._camera_shots = {s.name: s for s in lib.CAMERA_SHOTS}
        self._transitions = {t.name: t for t in lib.SCENE_TRANSITIONS}
        self._physics = {p.name: p for p in lib.PHYSICS_RULES}
        self._cloth = {c.name: c for c in lib.CLOTH_ELEMENTS}
        self._pacing = {p.age: p for p in lib.PACING_STANDARDS}
        self._shot_holds = {h.shot: h for h in lib.SHOT_HOLDS}
        self._reactions = {r.event: r for r in lib.REACTION_STANDARDS}
        self._action_timings = {a.action: a for a in lib.ACTION_TIMINGS}

    # ------------------------------------------------------------------
    # Lists
    # ------------------------------------------------------------------

    def list_motions(self) -> list[str]:
        return [c.motion for c in lib.MOTION_CYCLES]

    def list_walk_variants(self) -> list[str]:
        return list(self._walks)

    def list_run_variants(self) -> list[str]:
        return list(self._runs)

    def list_jumps(self) -> list[str]:
        return list(self._jumps)

    def list_dances(self) -> list[str]:
        return list(self._dances)

    def list_idle_layers(self) -> list[str]:
        return list(self._idle)

    def list_expressions(self) -> list[str]:
        return list(self._expressions)

    def list_gestures(self) -> list[str]:
        return list(self._gestures)

    def list_interactions(self) -> list[str]:
        return list(self._interactions)

    def list_camera_shots(self) -> list[str]:
        return list(self._camera_shots)

    def list_transitions(self) -> list[str]:
        return list(self._transitions)

    def list_cloth_elements(self) -> list[str]:
        return list(self._cloth)

    # ------------------------------------------------------------------
    # Queries (fall back to a stable default when unknown)
    # ------------------------------------------------------------------

    def motion_cycle(self, motion: str) -> MotionCycle:
        return self._cycles.get(motion, self._cycles["idle"])

    def walk_variant(self, name: str = "normal_walk") -> Optional[LocomotionVariant]:
        return self._walks.get(name)

    def run_variant(self, name: str = "normal_run") -> Optional[LocomotionVariant]:
        return self._runs.get(name)

    def jump(self, name: str = "standing_jump") -> Optional[JumpCycle]:
        return self._jumps.get(name)

    def dance(self, name: str = "side_to_side") -> Optional[DanceLoop]:
        return self._dances.get(name)

    def idle_layer(self, name: str = "breathing") -> Optional[IdleLayer]:
        return self._idle.get(name)

    def expression(self, emotion: str) -> Optional[FacialExpression]:
        return self._expressions.get(emotion)

    def expression_level(self, emotion: str, intensity: int = 3) -> Optional[ExpressionLevel]:
        expr = self._expressions.get(emotion)
        if not expr:
            return None
        for level in expr.levels:
            if level.intensity == intensity:
                return level
        return expr.levels[-1]

    def blink(self, name: str = "normal") -> Optional[BlinkType]:
        return self._blinks.get(name)

    def mouth_action(self, name: str = "talking") -> Optional[MouthAction]:
        return self._mouth_actions.get(name)

    def gesture(self, name: str) -> Optional[Gesture]:
        return self._gestures.get(name)

    def interaction(self, name: str) -> Optional[Interaction]:
        return self._interactions.get(name)

    def camera_shot(self, name: str) -> Optional[CameraShot]:
        return self._camera_shots.get(name)

    def transition(self, name: str) -> Optional[SceneTransition]:
        return self._transitions.get(name)

    def physics(self, name: str) -> Optional[PhysicsRule]:
        return self._physics.get(name)

    def cloth(self, name: str) -> Optional[ClothElement]:
        return self._cloth.get(name)

    def pacing(self, age: str = "4yr") -> Optional[PacingStandard]:
        return self._pacing.get(age)

    def shot_hold(self, shot: str) -> Optional[ShotHold]:
        return self._shot_holds.get(shot)

    def reaction(self, event: str) -> Optional[ReactionStandard]:
        return self._reactions.get(event)

    def action_timing(self, action: str) -> Optional[ActionTiming]:
        return self._action_timings.get(action)

    # ------------------------------------------------------------------
    # Expression / enum helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_value(x) -> str:
        return x.value if hasattr(x, "value") else str(x)

    def expression_for_enum(self, enum_value) -> str:
        mapping = {
            "happy": "happiness", "excited": "excitement",
            "curious": "curiosity", "surprised": "surprise",
            "confused": "confusion", "proud": "pride",
            "sleepy": "sleepiness", "laughing": "happiness",
            "gentle_sadness": "sadness", "neutral": "happiness",
            "thoughtful": "curiosity",
        }
        value = self._to_value(enum_value)
        return mapping.get(value, value)

    def camera_shot_for_motion(self, camera_motion) -> str:
        return lib.CAMERA_MOTION_TO_SHOT.get(
            self._to_value(camera_motion), "medium"
        )

    def transition_for_enum(self, transition) -> str:
        mapping = {
            "crossfade": "cross_dissolve", "fade": "cross_dissolve",
            "page_turn": "page_turn", "slide": "gentle_slide",
            "wipe": "wipe", "soft_zoom": "cross_dissolve",
            "dissolve": "cross_dissolve",
        }
        return mapping.get(self._to_value(transition), "cross_dissolve")

    def physics_notes_for_material(self, material) -> str:
        mapping = {
            "bouncy": lib.PHYSICS_RULES[6].value,
            "soft": lib.PHYSICS_RULES[3].value,
            "floating": lib.PHYSICS_RULES[2].value,
            "heavy": "Heavy objects fall at 80% of realistic acceleration",
            "light": "Light objects (paper, leaves) fall at 60% of realistic acceleration",
        }
        return mapping.get(self._to_value(material), lib.PHYSICS_RULES[3].value)

    # ------------------------------------------------------------------
    # Motion brief resolution
    # ------------------------------------------------------------------

    def build_motion_brief(
        self,
        motion: str = "idle",
        expression: str = "happy",
        expression_level: int = 3,
        camera_motion: str = "static",
        transition_in: str = "fade",
        transition_out: str = "fade",
        physics: str = "soft",
        duration_seconds: float = 3.0,
        fps: int = 24,
        dialogue: str = "",
        character: str = "",
        environment: str = "",
        weather: str = "",
    ) -> MotionBrief:
        motion = self._to_value(motion)
        cycle = self.motion_cycle(motion)
        fps = fps or self.master_frame_rate

        frames_per_cycle = max(cycle.base_frames, 1)
        if cycle.looping:
            cycles = max(1, math.ceil(duration_seconds * fps / frames_per_cycle))
        else:
            cycles = 1

        cycle_notes = self._cycle_notes(motion, cycle, character)

        expression = self.expression_for_enum(expression) if not isinstance(expression, str) else expression
        expr_level = self.expression_level(expression, expression_level)
        if expr_level is None:
            expression, expr_level = "happiness", self.expression_level("happiness", expression_level)

        blink = "normal"
        if motion in ("sleep", "idle"):
            blink = "slow"
        elif expression in ("surprise", "excitement"):
            blink = "double"
        blink_spec = self.blink(blink)

        camera_shot_name = self.camera_shot_for_motion(camera_motion)
        camera = self.camera_shot(camera_shot_name)

        transition_in = self.transition_for_enum(transition_in) if not isinstance(transition_in, str) else (transition_in or "cross_dissolve")
        transition_out = self.transition_for_enum(transition_out) if not isinstance(transition_out, str) else (transition_out or "cross_dissolve")
        tr_in = self.transition(transition_in) or self.transition("cross_dissolve")
        tr_out = self.transition(transition_out) or self.transition("cross_dissolve")

        physics_notes = self.physics_notes_for_material(physics)

        secondary = self._secondary_elements(character, motion)

        mouth = "talking" if dialogue else "breathing"
        mouth_action = self.mouth_action(mouth)

        pacing_note = (
            f"Master {self.master_frame_rate}fps, export {self.export_frame_rate}fps; "
            f"hold each shot 30-50% longer than adult content; reaction pause 8-16 frames"
        )
        if dialogue and mouth_action:
            pacing_note += f"; mouth: {mouth_action.timing}"

        return MotionBrief(
            motion=motion,
            frames_per_cycle=frames_per_cycle,
            loopable=cycle.looping,
            cycles=cycles,
            duration_seconds=round(duration_seconds, 3),
            fps=fps,
            cycle_notes=cycle_notes,
            expression=expression,
            expression_level=expr_level.intensity,
            blink=blink,
            blink_frames=blink_spec.frames if blink_spec else "2-3",
            camera_shot=camera_shot_name,
            transition_in=transition_in,
            transition_out=transition_out,
            physics=physics,
            physics_notes=physics_notes,
            secondary_elements=secondary,
            pacing_note=pacing_note,
            negative_prompt=ANIMATION_NEGATIVE_BASE,
        )

    def _cycle_notes(self, motion: str, cycle: MotionCycle, character: str) -> str:
        if motion in ("walk", "run"):
            pool = self._walks if motion == "walk" else self._runs
            variant_name = "normal_walk" if motion == "walk" else "normal_run"
            variant = pool.get(variant_name)
            if variant:
                return (
                    f"{variant.description} — {variant.frames_per_stride} frames per "
                    f"stride at {variant.speed_percent}% max speed, {variant.easing}."
                )
        if motion == "jump":
            jump = self.jump("standing_jump")
            if jump:
                return (
                    f"{jump.description} — {jump.total_frames} frames, "
                    f"reaches {jump.height_percent}% of character height."
                )
        if motion == "dance":
            dance = self.dance("side_to_side")
            if dance:
                return (
                    f"{dance.description} — {dance.frames}-frame loop at "
                    f"{dance.bpm} BPM (24 frames per beat)."
                )
        if motion == "idle":
            layers = ", ".join(self._idle.keys())
            return f"Never frozen: {layers} all active at low amplitude."
        return cycle.description

    def _secondary_elements(self, character: str, motion: str) -> list[str]:
        exclude: set[str] = set()
        if motion in ("sleep", "sit"):
            exclude.add("balloons")
        elements = [c.name for c in lib.CLOTH_ELEMENTS if c.name not in exclude]
        return elements

    # ------------------------------------------------------------------
    # Bible-aware validation
    # ------------------------------------------------------------------

    def validate_motion(self, motion: str) -> list[str]:
        violations = []
        motion = self._to_value(motion)
        if motion not in self._cycles:
            violations.append(f"Unknown motion '{motion}' — not in the animation cycle library")
        return violations

    def validate_expression(self, expression: str) -> list[str]:
        violations = []
        name = self.expression_for_enum(expression)
        if name not in self._expressions:
            violations.append(f"Unknown expression '{name}' — not in the facial library")
        return violations

    def validate_plan(self, plan) -> dict:
        """Validate an AnimationPlan against bible standards.

        Returns a dict with `passed`, `violations`, `warnings`, and `score`.
        """
        violations: list[str] = []
        warnings: list[str] = []

        if plan is None:
            return {"passed": False, "violations": ["No plan provided"],
                    "warnings": [], "score": 0.0}

        motion = getattr(plan, "motion", None)
        if motion is None:
            violations.append("Plan has no motion")
        else:
            violations.extend(self.validate_motion(self._to_value(motion)))

        expression = getattr(plan, "expression", None)
        if expression is not None:
            violations.extend(self.validate_expression(self._to_value(expression)))

        duration = getattr(plan, "duration_seconds", 0.0) or 0.0
        if duration <= 0:
            violations.append("Plan duration must be positive")
        elif duration < 0.5:
            violations.append("Plan duration below the 0.5 second minimum")
        elif duration < 1.5:
            warnings.append(
                "Duration under 1.5 seconds — no cuts should be faster than 1.5s"
            )

        camera = getattr(plan, "camera_motion", None)
        if camera is not None and self.camera_shot_for_motion(camera) not in self._camera_shots:
            warnings.append(f"Camera motion '{self._to_value(camera)}' maps to an unknown shot")

        lip_sync = getattr(plan, "lip_sync", None)
        if lip_sync is not None and getattr(lip_sync, "dialogue", ""):
            words = len(str(lip_sync.dialogue).split())
            expected_seconds = (words * 0.8) + 1.5  # reading-speed formula
            if duration and duration < expected_seconds - 1.0:
                warnings.append(
                    f"Dialogue ({words} words) needs ~{expected_seconds:.1f}s for reading, "
                    f"plan holds {duration:.1f}s"
                )

        check_count = 4
        score = round(
            (1.0 - (len(violations) / check_count if violations else 0.0)) * 100.0, 1
        )
        return {
            "passed": not violations,
            "violations": violations,
            "warnings": warnings,
            "score": score,
        }

    def validate_clip(self, clip) -> dict:
        """Validate an AnimationClip against bible standards."""
        violations: list[str] = []
        warnings: list[str] = []

        frame_rate = getattr(clip, "frame_rate", None)
        if frame_rate is not None and frame_rate not in self.valid_frame_rates:
            violations.append(
                f"Frame rate {frame_rate} invalid — use {self.valid_frame_rates}"
            )

        animation_type = getattr(clip, "animation_type", None)
        if animation_type is not None:
            violations.extend(self.validate_motion(self._to_value(animation_type)))

        duration = getattr(clip, "duration_seconds", 0.0) or 0.0
        if duration <= 0:
            violations.append("Clip duration must be positive")

        passed = not violations
        return {
            "passed": passed,
            "violations": violations,
            "warnings": warnings,
            "score": 100.0 if passed else round(100.0 - len(violations) * 20.0, 1),
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
            DocFact("Animation/STYLE_GUIDE.md", "blink rate", "4–6 seconds"),
            DocFact("Animation/Motion/WALK_CYCLES.md", "Normal walk frames", "8 frames per step"),
            DocFact("Animation/Motion/WALK_CYCLES.md", "Happy skip frames", "6 frames per step"),
            DocFact("Animation/Motion/RUN_CYCLES.md", "Normal run frames", "5 frames per stride"),
            DocFact("Animation/Motion/JUMP_CYCLES.md", "Standing jump total", "12 frames"),
            DocFact("Animation/Motion/JUMP_CYCLES.md", "Jump for joy height", "45%"),
            DocFact("Animation/Motion/DANCE_LIBRARY.md", "Dance BPM", "120 BPM"),
            DocFact("Animation/Motion/DANCE_LIBRARY.md", "Side-to-side loop", "8 frames"),
            DocFact("Animation/Motion/IDLE.md", "Breathing rate", "12 cycles per minute"),
            DocFact("Animation/Motion/IDLE.md", "Weight shift loop", "144 frames"),
            DocFact("Animation/Facial/FACIAL_LIBRARY.md", "Intensity scale", "1–5"),
            DocFact("Animation/Facial/EYE_ANIMATION.md", "Blinks per minute", "6–15"),
            DocFact("Animation/Facial/MOUTH_ANIMATION.md", "Phoneme frames", "4–6"),
            DocFact("Animation/Gestures/GESTURE_LIBRARY.md", "Wave cycle", "12 frames"),
            DocFact("Animation/Interactions/INTERACTION_LIBRARY.md", "Tie shoelaces", "60 frames"),
            DocFact("Animation/Interactions/INTERACTION_LIBRARY.md", "Wash hands", "30 frames"),
            DocFact("Animation/Camera/CAMERA_LANGUAGE.md", "Close-up duration", "24-96 frames"),
            DocFact("Animation/Camera/TRANSITIONS.md", "Cross dissolve", "12-16 frames"),
            DocFact("Animation/Physics/PHYSICS.md", "Gravity strength", "85%"),
            DocFact("Animation/Physics/CLOTH_MOTION.md", "Secondary amplitude", "10-20%"),
            DocFact("Animation/Timing/TIMING.md", "Reaction pause", "8-16"),
            DocFact("Animation/Timing/TIMING.md", "2-4 year multiplier", "1.5x"),
            DocFact("Animation/PromptTemplates/animation-prompts.md", "Placeholder", "[character]"),
            DocFact("Animation/NegativePrompts/animation-negatives.md", "Base negative", "watermark"),
        ]

        report = DocConsistencyReport()
        base = os.path.abspath(docs_dir)
        strip_animation_prefix = os.path.basename(base) == "Animation"

        for fact in facts:
            rel = fact.file
            if strip_animation_prefix and rel.startswith("Animation/"):
                rel = rel[len("Animation/"):]
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
