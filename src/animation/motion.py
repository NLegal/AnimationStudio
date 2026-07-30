from enum import Enum
from typing import Optional

from .models import MotionCategory


class MotionComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


MOTION_PROPERTIES: dict[MotionCategory, dict] = {
    MotionCategory.IDLE: {"complexity": "simple", "frames": 24, "looping": True},
    MotionCategory.WALK: {"complexity": "moderate", "frames": 8, "looping": True},
    MotionCategory.RUN: {"complexity": "moderate", "frames": 6, "looping": True},
    MotionCategory.SKIP: {"complexity": "moderate", "frames": 12, "looping": True},
    MotionCategory.DANCE: {"complexity": "complex", "frames": 48, "looping": True},
    MotionCategory.JUMP: {"complexity": "moderate", "frames": 16, "looping": False},
    MotionCategory.WAVE: {"complexity": "simple", "frames": 12, "looping": False},
    MotionCategory.POINT: {"complexity": "simple", "frames": 10, "looping": False},
    MotionCategory.CLAP: {"complexity": "simple", "frames": 8, "looping": True},
    MotionCategory.HUG: {"complexity": "moderate", "frames": 20, "looping": False},
    MotionCategory.SIT: {"complexity": "simple", "frames": 14, "looping": False},
    MotionCategory.STAND: {"complexity": "simple", "frames": 14, "looping": False},
    MotionCategory.READ: {"complexity": "simple", "frames": 60, "looping": False},
    MotionCategory.WRITE: {"complexity": "moderate", "frames": 30, "looping": False},
    MotionCategory.SLEEP: {"complexity": "simple", "frames": 40, "looping": True},
    MotionCategory.EAT: {"complexity": "moderate", "frames": 20, "looping": False},
    MotionCategory.DRINK: {"complexity": "moderate", "frames": 18, "looping": False},
    MotionCategory.PLAY: {"complexity": "moderate", "frames": 30, "looping": True},
    MotionCategory.LAUGH: {"complexity": "simple", "frames": 14, "looping": False},
    MotionCategory.CRY: {"complexity": "simple", "frames": 24, "looping": False},
    MotionCategory.CELEBRATE: {"complexity": "complex", "frames": 32, "looping": False},
}


class MotionEngine:
    def describe(self, motion: MotionCategory) -> dict:
        props = MOTION_PROPERTIES.get(motion, MOTION_PROPERTIES[MotionCategory.IDLE])
        return {
            "motion": motion.value,
            "complexity": props["complexity"],
            "base_frame_count": props["frames"],
            "looping": props["looping"],
            "description": self._describe_motion(motion),
        }

    def list_motions(
        self,
        complexity: Optional[str] = None,
        looping: Optional[bool] = None,
    ) -> list[MotionCategory]:
        results: list[MotionCategory] = []
        for motion, props in MOTION_PROPERTIES.items():
            if complexity and props["complexity"] != complexity:
                continue
            if looping is not None and props["looping"] != looping:
                continue
            results.append(motion)
        return results

    def estimate_duration(self, motion: MotionCategory, frame_rate: int = 24) -> float:
        props = MOTION_PROPERTIES.get(motion, MOTION_PROPERTIES[MotionCategory.IDLE])
        return props["frames"] / frame_rate

    def _describe_motion(self, motion: MotionCategory) -> str:
        descriptions = {
            MotionCategory.IDLE: "Character stands relaxed with gentle breathing and subtle weight shifts",
            MotionCategory.WALK: "Natural forward walking motion with arm swing and gentle bounce",
            MotionCategory.RUN: "Bouncy running motion with increased arm swing and faster pace",
            MotionCategory.SKIP: "Playful skipping with alternating hops and arm swings",
            MotionCategory.DANCE: "Rhythmic full-body dance movement with coordinated arm and leg motion",
            MotionCategory.JUMP: "Upward jumping motion with squat anticipation and landing recovery",
            MotionCategory.WAVE: "Hand waving side to side with slight arm movement",
            MotionCategory.POINT: "Arm extends to point at an object with hand gesture",
            MotionCategory.CLAP: "Hands clap together with slight body bounce",
            MotionCategory.HUG: "Arms open wide then close around another character or object",
            MotionCategory.SIT: "Character lowers into seated position with knee bend",
            MotionCategory.STAND: "Character rises from seated to standing position",
            MotionCategory.READ: "Head moves slightly while eyes track text across a page",
            MotionCategory.WRITE: "Hand moves across surface with slight shoulder and head movement",
            MotionCategory.SLEEP: "Gentle rhythmic breathing with slow rise and fall of chest",
            MotionCategory.EAT: "Hand-to-mouth motion with chewing and swallowing",
            MotionCategory.DRINK: "Cup raises to mouth with tilting and swallowing motion",
            MotionCategory.PLAY: "Playful movement with varied gestures and body language",
            MotionCategory.LAUGH: "Body shakes with open mouth and eye crinkle expression",
            MotionCategory.CRY: "Shoulders heave with occasional wiping of eyes",
            MotionCategory.CELEBRATE: "Arms raised in excitement with possible jumping or spinning",
        }
        return descriptions.get(motion, "Custom animation motion")
