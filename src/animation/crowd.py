"""Crowd Engine — background character animation.

Implements the Phase 9 Crowd Engine: background characters walk, talk
silently, play, wave, read, sit, run, and dance. Crowd animation must
remain subtle and never distract from the main characters.
"""

from __future__ import annotations
from dataclasses import dataclass, field

CROWD_ACTIVITIES: list[str] = [
    "walk", "talk_silently", "play", "wave", "read", "sit", "run", "dance",
]

CROWD_ACTIVITY_DESCRIPTIONS: dict[str, str] = {
    "walk": "Background character walks at a relaxed pace",
    "talk_silently": "Background character mouths a silent conversation",
    "play": "Background character plays quietly in the distance",
    "wave": "Background character waves gently",
    "read": "Background character reads a book",
    "sit": "Background character sits calmly",
    "run": "Background character runs across the background",
    "dance": "Background character dances softly in place",
}


@dataclass
class CrowdMember:
    member_id: str = ""
    activity: str = "walk"
    background_level: float = 0.3
    description: str = ""


class CrowdEngine:
    SUBTLETY_LEVEL = 0.3

    def build_crowd(self, size: int = 5, primary_motion: str = "walk") -> list[CrowdMember]:
        size = max(0, size)
        members: list[CrowdMember] = []
        for i in range(size):
            activity = self._suggest_activity(primary_motion, i)
            members.append(CrowdMember(
                member_id=f"CROWD_{i + 1}",
                activity=activity,
                background_level=self.SUBTLETY_LEVEL,
                description=CROWD_ACTIVITY_DESCRIPTIONS.get(activity, "Background activity"),
            ))
        return members

    def suggest_activities(self, scene_type: str = "") -> list[str]:
        scene_map = {
            "park": ["walk", "play", "wave", "sit"],
            "classroom": ["read", "sit", "talk_silently", "wave"],
            "playground": ["play", "run", "dance", "wave"],
            "street": ["walk", "talk_silently", "run", "sit"],
            "celebration": ["dance", "wave", "play", "talk_silently"],
        }
        return scene_map.get(scene_type.lower(), list(CROWD_ACTIVITIES))

    def _suggest_activity(self, primary_motion: str, index: int) -> str:
        rotations = ["walk", "talk_silently", "play", "wave", "read", "sit", "run", "dance"]
        if primary_motion in CROWD_ACTIVITIES:
            rotations = [a for a in rotations if a != primary_motion]
        return rotations[index % len(rotations)]

    def list_activities(self) -> list[str]:
        return list(CROWD_ACTIVITIES)

    def describe(self) -> dict:
        return {
            "subtlety_level": self.SUBTLETY_LEVEL,
            "principle": "Crowd animation remains subtle and never distracts from the main characters",
            "activities": list(CROWD_ACTIVITIES),
        }
