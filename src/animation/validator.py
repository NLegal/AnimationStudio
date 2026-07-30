from .models import AnimationClip, AnimationPlan, AnimationValidationResult


class AnimationValidator:
    MIN_DURATION = 0.5
    MAX_DURATION = 600.0
    VALID_RESOLUTIONS = {(1920, 1080), (3840, 2160), (1280, 720), (1080, 1920)}
    VALID_FRAME_RATES = {24, 30, 60}

    def validate_clip(self, clip: AnimationClip) -> AnimationValidationResult:
        checks: dict[str, bool] = {
            "has_clip_id": bool(clip.clip_id),
            "has_episode": bool(clip.episode),
            "has_animation_type": clip.animation_type is not None,
            "duration_in_range": self.MIN_DURATION <= clip.duration_seconds <= self.MAX_DURATION,
            "valid_resolution": (
                clip.resolution_width > 0 and clip.resolution_height > 0
            ),
            "valid_frame_rate": clip.frame_rate in self.VALID_FRAME_RATES,
            "has_characters": len(clip.characters) > 0,
            "has_environment": bool(clip.environment),
            "has_seed": True,
            "has_prompt_version": bool(clip.prompt_version),
        }
        errors = [k for k, v in checks.items() if not v]

        score = (sum(1 for v in checks.values() if v) / len(checks)) * 100.0 if checks else 0.0

        return AnimationValidationResult(
            passed=len(errors) == 0,
            checks=checks,
            errors=errors,
            score=round(score, 1),
        )

    def validate_plan(self, plan: AnimationPlan) -> AnimationValidationResult:
        checks: dict[str, bool] = {
            "has_shot_id": bool(plan.shot_id),
            "has_motion": plan.motion is not None,
            "has_expression": plan.expression is not None,
            "has_camera_motion": plan.camera_motion is not None,
            "has_lighting": plan.lighting is not None,
            "duration_in_range": self.MIN_DURATION <= plan.duration_seconds <= self.MAX_DURATION,
            "has_transition_in": plan.transition_in is not None,
            "has_transition_out": plan.transition_out is not None,
        }
        errors = [k for k, v in checks.items() if not v]

        score = (sum(1 for v in checks.values() if v) / len(checks)) * 100.0 if checks else 0.0

        return AnimationValidationResult(
            passed=len(errors) == 0,
            checks=checks,
            errors=errors,
            score=round(score, 1),
        )
