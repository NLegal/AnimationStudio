from typing import Optional

from .models import (
    AnimationPlan, MotionCategory, FacialExpression,
    CameraMotion, LightingCondition, TransitionType,
    PhysicsMaterial, ParticleEffect, LipSyncTrack,
)


class AnimationPlanner:
    def plan_shot(
        self,
        shot_id: str,
        motion: MotionCategory = MotionCategory.IDLE,
        expression: FacialExpression = FacialExpression.HAPPY,
        camera_motion: CameraMotion = CameraMotion.STATIC,
        lighting: LightingCondition = LightingCondition.MORNING,
        duration_seconds: float = 3.0,
        dialogue: str = "",
        seed: int = 42,
        weather: str = "clear",
    ) -> AnimationPlan:
        lip_sync = None
        if dialogue:
            lip_sync = self._generate_lip_sync_placeholder(dialogue, duration_seconds)

        return AnimationPlan(
            shot_id=shot_id,
            motion=motion,
            expression=expression,
            expression_transitions=self._suggest_transitions(expression, duration_seconds),
            camera_motion=camera_motion,
            lip_sync=lip_sync,
            lighting=lighting,
            transition_in=self._suggest_transition_in(motion),
            transition_out=TransitionType.FADE,
            duration_seconds=duration_seconds,
            particle_effects=self._suggest_particles(weather, lighting),
            physics_material=PhysicsMaterial.SOFT,
            weather=weather,
            seed=seed,
        )

    def plan_from_shot_data(
        self,
        shot_id: str,
        animation: str = "idle",
        emotion: str = "happy",
        movement: str = "static",
        lighting: str = "natural",
        environment: str = "",
        duration: float = 3.0,
        dialogue: Optional[str] = None,
        weather: str = "clear",
        seed: int = 42,
    ) -> AnimationPlan:
        motion = self._resolve_motion(animation)
        expression = self._resolve_expression(emotion)
        camera_motion = self._resolve_camera_motion(movement)
        lighting_cond = self._resolve_lighting(lighting)

        lip_sync = None
        if dialogue:
            lip_sync = self._generate_lip_sync_placeholder(dialogue, duration)

        return AnimationPlan(
            shot_id=shot_id,
            motion=motion,
            expression=expression,
            camera_motion=camera_motion,
            lip_sync=lip_sync,
            lighting=lighting_cond,
            duration_seconds=duration,
            weather=weather,
            seed=seed,
        )

    def _suggest_transitions(
        self, expression: FacialExpression, duration: float
    ) -> list[tuple[float, FacialExpression]]:
        if expression == FacialExpression.NEUTRAL:
            return [(0.0, expression)]
        peaks: list[tuple[float, FacialExpression]] = [(0.0, FacialExpression.NEUTRAL)]
        mid = duration * 0.4
        peaks.append((mid, expression))
        end = duration * 0.9
        peaks.append((end, FacialExpression.NEUTRAL))
        return peaks

    def _suggest_transition_in(self, motion: MotionCategory) -> TransitionType:
        if motion in (MotionCategory.DANCE, MotionCategory.CELEBRATE, MotionCategory.JUMP):
            return TransitionType.SOFT_ZOOM
        if motion in (MotionCategory.WALK, MotionCategory.RUN, MotionCategory.SKIP):
            return TransitionType.SLIDE
        return TransitionType.FADE

    def _suggest_particles(self, weather: str, lighting: LightingCondition) -> list[ParticleEffect]:
        effects: list[ParticleEffect] = []
        if weather == "snow":
            effects.append(ParticleEffect.SNOW)
        elif weather == "rain":
            effects.append(ParticleEffect.RAIN)
        if lighting == LightingCondition.NIGHT:
            effects.append(ParticleEffect.FIREFLIES)
        if lighting == LightingCondition.HOLIDAY:
            effects.append(ParticleEffect.CONFETTI)
        return effects

    def _generate_lip_sync_placeholder(self, dialogue: str, duration: float) -> LipSyncTrack:
        from .lipsync import LipSyncEngine
        engine = LipSyncEngine()
        return engine.generate(dialogue, duration)

    def _resolve_motion(self, animation: str) -> MotionCategory:
        mapping = {
            "idle": MotionCategory.IDLE, "walk": MotionCategory.WALK,
            "run": MotionCategory.RUN, "skip": MotionCategory.SKIP,
            "dance": MotionCategory.DANCE, "jump": MotionCategory.JUMP,
            "wave": MotionCategory.WAVE, "point": MotionCategory.POINT,
            "clap": MotionCategory.CLAP, "hug": MotionCategory.HUG,
            "sit": MotionCategory.SIT, "stand": MotionCategory.STAND,
            "read": MotionCategory.READ, "write": MotionCategory.WRITE,
            "sleep": MotionCategory.SLEEP, "eat": MotionCategory.EAT,
            "drink": MotionCategory.DRINK, "play": MotionCategory.PLAY,
            "laugh": MotionCategory.LAUGH, "cry": MotionCategory.CRY,
            "celebrate": MotionCategory.CELEBRATE,
        }
        return mapping.get(animation, MotionCategory.IDLE)

    def _resolve_expression(self, emotion: str) -> FacialExpression:
        mapping = {
            "neutral": FacialExpression.NEUTRAL, "happy": FacialExpression.HAPPY,
            "excited": FacialExpression.EXCITED, "curious": FacialExpression.CURIOUS,
            "surprised": FacialExpression.SURPRISED, "confused": FacialExpression.CONFUSED,
            "proud": FacialExpression.PROUD, "thoughtful": FacialExpression.THOUGHTFUL,
            "sleepy": FacialExpression.SLEEPY, "laughing": FacialExpression.LAUGHING,
            "sad": FacialExpression.GENTLE_SADNESS,
        }
        return mapping.get(emotion, FacialExpression.NEUTRAL)

    def _resolve_camera_motion(self, movement: str) -> CameraMotion:
        mapping = {
            "static": CameraMotion.STATIC, "pan": CameraMotion.PAN,
            "pan_left": CameraMotion.PAN, "pan_right": CameraMotion.PAN,
            "tilt": CameraMotion.TILT, "track": CameraMotion.TRACK,
            "follow": CameraMotion.FOLLOW, "push_in": CameraMotion.PUSH_IN,
            "pull_out": CameraMotion.PULL_OUT, "orbit": CameraMotion.ORBIT,
            "crane": CameraMotion.CRANE, "dolly": CameraMotion.DOLLY,
        }
        return mapping.get(movement, CameraMotion.STATIC)

    def _resolve_lighting(self, lighting: str) -> LightingCondition:
        mapping = {
            "sunrise": LightingCondition.SUNRISE, "morning": LightingCondition.MORNING,
            "noon": LightingCondition.NOON, "golden_hour": LightingCondition.GOLDEN_HOUR,
            "sunset": LightingCondition.SUNSET, "night": LightingCondition.NIGHT,
            "clouds": LightingCondition.CLOUDS, "rain": LightingCondition.RAIN,
            "snow": LightingCondition.SNOW, "indoor": LightingCondition.INDOOR,
            "holiday": LightingCondition.HOLIDAY, "natural": LightingCondition.MORNING,
        }
        return mapping.get(lighting, LightingCondition.MORNING)
