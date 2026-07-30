from .models import CameraMotion


CAMERA_MOTION_DESCRIPTIONS: dict[CameraMotion, dict] = {
    CameraMotion.STATIC: {
        "description": "Camera remains fixed in position — stable, no movement",
        "speed": "none",
        "best_for": "dialogue, close-ups, establishing shots",
    },
    CameraMotion.PAN: {
        "description": "Camera rotates horizontally on fixed axis — left or right",
        "speed": "slow",
        "best_for": "revealing environments, following horizontal action",
    },
    CameraMotion.TILT: {
        "description": "Camera rotates vertically on fixed axis — up or down",
        "speed": "slow",
        "best_for": "revealing tall objects, scanning from ground to sky",
    },
    CameraMotion.TRACK: {
        "description": "Camera moves parallel to action — lateral movement",
        "speed": "moderate",
        "best_for": "following walking characters, parallel to subject",
    },
    CameraMotion.FOLLOW: {
        "description": "Camera follows subject from behind or ahead",
        "speed": "moderate",
        "best_for": "walking/exploring sequences, POV-adjacent shots",
    },
    CameraMotion.PUSH_IN: {
        "description": "Camera moves toward subject — increases focus intensity",
        "speed": "slow",
        "best_for": "emotional emphasis, revealing reaction, building tension",
    },
    CameraMotion.PULL_OUT: {
        "description": "Camera moves away from subject — reveals context",
        "speed": "slow",
        "best_for": "revealing environment, ending scenes, transitions",
    },
    CameraMotion.ORBIT: {
        "description": "Camera rotates around subject in circular path",
        "speed": "slow",
        "best_for": "character reveals, product showcases, dramatic intros",
    },
    CameraMotion.CRANE: {
        "description": "Camera moves vertically up or down — boom motion",
        "speed": "slow",
        "best_for": "revealing scale, establishing shots, scene transitions",
    },
    CameraMotion.DOLLY: {
        "description": "Camera moves toward or away from scene on wheeled platform",
        "speed": "moderate",
        "best_for": "smooth scene entry/exit, following character movement",
    },
}


class CameraMotionEngine:
    def describe(self, motion: CameraMotion) -> dict:
        return CAMERA_MOTION_DESCRIPTIONS.get(
            motion,
            CAMERA_MOTION_DESCRIPTIONS[CameraMotion.STATIC],
        )

    def list_motions(self) -> list[CameraMotion]:
        return list(CameraMotion)

    def estimate_duration(self, motion: CameraMotion, shot_duration: float) -> dict:
        speeds = {
            CameraMotion.STATIC: 0,
            CameraMotion.PAN: 0.3,
            CameraMotion.TILT: 0.3,
            CameraMotion.TRACK: 0.4,
            CameraMotion.FOLLOW: 0.4,
            CameraMotion.PUSH_IN: 0.5,
            CameraMotion.PULL_OUT: 0.5,
            CameraMotion.ORBIT: 0.6,
            CameraMotion.CRANE: 0.5,
            CameraMotion.DOLLY: 0.4,
        }
        hold_ratio = 1.0 - speeds[motion]
        return {
            "motion_duration": round(shot_duration * speeds[motion], 2),
            "hold_duration": round(shot_duration * hold_ratio, 2),
            "motion_speed": CAMERA_MOTION_DESCRIPTIONS[motion]["speed"],
        }
