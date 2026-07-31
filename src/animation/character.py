"""Character Animation Engine — eye, body, and secondary motion.

Implements the Phase 9 character-performance systems:

- Eye Animation: blink frequency, eye tracking, focus target, reading
  movement, looking at speaker, looking at object.
- Body Animation: natural weight shifts, breathing, secondary motion,
  arm swing, foot placement, head movement. Avoid robotic movement.
- Secondary Motion: hair, bows, clothing, scarves, tails, backpacks,
  balloons, leaves, grass — subtle movements that make scenes feel alive.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ── Eye Animation ───────────────────────────────────────────────────────

EYE_BEHAVIORS: list[str] = [
    "blink_frequency",
    "eye_tracking",
    "focus_target",
    "reading_movement",
    "look_at_speaker",
    "look_at_object",
]

DEFAULT_BLINK_INTERVAL = (4.0, 10.0)


@dataclass
class EyeAnimationPattern:
    behavior: str = "blink_frequency"
    target: str = ""
    blink_interval: tuple[float, float] = DEFAULT_BLINK_INTERVAL
    duration_seconds: float = 0.0
    description: str = ""


class EyeAnimationEngine:
    def list_behaviors(self) -> list[str]:
        return list(EYE_BEHAVIORS)

    def describe(self, behavior: str) -> dict:
        descriptions = {
            "blink_frequency": "Natural blinking with randomized intervals to avoid staring",
            "eye_tracking": "Eyes smoothly track a moving subject",
            "focus_target": "Eyes lock onto a clear focus point in the scene",
            "reading_movement": "Eyes sweep left-to-right across a page",
            "look_at_speaker": "Eyes shift to the speaking character",
            "look_at_object": "Eyes shift to a referenced object",
        }
        return {
            "behavior": behavior,
            "description": descriptions.get(behavior, "Custom eye behavior"),
        }

    def suggest_pattern(
        self, behavior: str, target: str = "", duration: float = 0.0
    ) -> EyeAnimationPattern:
        if behavior not in EYE_BEHAVIORS:
            behavior = "blink_frequency"
        return EyeAnimationPattern(
            behavior=behavior,
            target=target,
            duration_seconds=duration,
            description=self.describe(behavior)["description"],
        )

    def blink_schedule(self, duration: float, interval: tuple[float, float] = DEFAULT_BLINK_INTERVAL) -> list[tuple[float, float]]:
        """Returns (start, end) blink windows across the duration."""
        blinks: list[tuple[float, float]] = []
        t = interval[0]
        while t < duration:
            blinks.append((round(t, 3), round(min(t + 0.1, duration), 3)))
            t += interval[0] + (interval[1] - interval[0]) / 2
        return blinks

    def focus_target(self, target: str) -> EyeAnimationPattern:
        return self.suggest_pattern("focus_target", target)

    def look_at(self, subject: str, kind: str = "object") -> EyeAnimationPattern:
        behavior = "look_at_speaker" if kind == "speaker" else "look_at_object"
        return self.suggest_pattern(behavior, subject)

    def reading_movement(self, page_duration: float, lines: int = 3) -> list[tuple[float, str]]:
        """Returns (timestamp, gaze_position) sweep points across a page."""
        line_time = page_duration / max(lines, 1)
        positions = ["left", "center", "right"]
        sweeps: list[tuple[float, str]] = []
        for i in range(lines):
            base = i * line_time
            for j, pos in enumerate(positions):
                sweeps.append((round(base + j * (line_time / len(positions)), 3), pos))
        return sweeps


# ── Body Animation ──────────────────────────────────────────────────────

BODY_COMPONENTS: list[str] = [
    "weight_shifts",
    "breathing",
    "secondary_motion",
    "arm_swing",
    "foot_placement",
    "head_movement",
]


@dataclass
class BodyAnimationProfile:
    motion: str = "idle"
    weight_shifts: str = "gentle"
    breathing: bool = True
    secondary_motion: bool = True
    arm_swing: str = "relaxed"
    foot_placement: str = "grounded"
    head_movement: str = "subtle"
    description: str = ""


class BodyAnimationEngine:
    def profile(self, motion: str = "idle") -> BodyAnimationProfile:
        profiles = {
            "walk": BodyAnimationProfile(
                motion="walk", weight_shifts="rhythmic", breathing=True,
                secondary_motion=True, arm_swing="opposite_phase",
                foot_placement="heel_toe", head_movement="natural_bob",
                description="Natural forward motion with weight transfer and opposite arm swing",
            ),
            "run": BodyAnimationProfile(
                motion="run", weight_shifts="dynamic", breathing=True,
                secondary_motion=True, arm_swing="high_energy",
                foot_placement="ball_of_foot", head_movement="stable",
                description="Bouncy forward motion with strong arm drive and forward lean",
            ),
            "idle": BodyAnimationProfile(
                motion="idle", weight_shifts="gentle", breathing=True,
                secondary_motion=True, arm_swing="relaxed",
                foot_placement="grounded", head_movement="subtle",
                description="Relaxed standing with gentle weight shifts and breathing",
            ),
            "dance": BodyAnimationProfile(
                motion="dance", weight_shifts="expressive", breathing=True,
                secondary_motion=True, arm_swing="choreographed",
                foot_placement="stepping", head_movement="rhythmic",
                description="Full-body coordinated motion with expressive weight shifts",
            ),
            "sit": BodyAnimationProfile(
                motion="sit", weight_shifts="none", breathing=True,
                secondary_motion=False, arm_swing="resting",
                foot_placement="planted", head_movement="occasional",
                description="Seated posture with breathing and occasional head movement",
            ),
        }
        return profiles.get(motion, profiles["idle"])

    def list_components(self) -> list[str]:
        return list(BODY_COMPONENTS)

    def describe(self, motion: str = "idle") -> dict:
        profile = self.profile(motion)
        return {
            "motion": profile.motion,
            "components": {
                "weight_shifts": profile.weight_shifts,
                "breathing": profile.breathing,
                "secondary_motion": profile.secondary_motion,
                "arm_swing": profile.arm_swing,
                "foot_placement": profile.foot_placement,
                "head_movement": profile.head_movement,
            },
            "description": profile.description,
        }

    def avoid_robotic(self) -> list[str]:
        return [
            "jitter_subtle_weight_shift",
            "asymmetrical_arm_phases",
            "micro_head_tilt",
            "breathing_offset",
            "occasional_weight_transfer",
        ]


# ── Secondary Motion ────────────────────────────────────────────────────

SECONDARY_ELEMENTS: list[str] = [
    "hair", "bows", "clothing", "scarves", "tails",
    "backpacks", "balloons", "leaves", "grass",
]


@dataclass
class SecondaryMotionElement:
    element: str = ""
    intensity: float = 0.3
    delay: float = 0.1
    motion_type: str = "follow_through"
    description: str = ""


class SecondaryMotionEngine:
    def list_elements(self) -> list[str]:
        return list(SECONDARY_ELEMENTS)

    def describe_element(self, element: str) -> dict:
        descriptions = {
            "hair": "Hair follows head movement with delayed settle",
            "bows": "Bows bob gently with head and body motion",
            "clothing": "Cloth settles after movement with soft folds",
            "scarves": "Scarf trails behind motion with gentle waves",
            "tails": "Tails sway with delayed follow-through",
            "backpacks": "Backpack bounces slightly with steps",
            "balloons": "Balloons drift and tug with a slight bob",
            "leaves": "Leaves rustle and drift in air currents",
            "grass": "Grass sways gently in response to movement",
        }
        return {
            "element": element,
            "description": descriptions.get(element, "Secondary motion element"),
        }

    def suggest_elements(self, context: str = "") -> list[str]:
        context_map = {
            "outdoor": ["hair", "leaves", "grass"],
            "indoor": ["hair", "clothing"],
            "winter": ["scarves", "hair"],
            "playground": ["backpack", "balloon", "hair"],
            "celebration": ["confetti", "balloon"],
        }
        elements = context_map.get(context.lower(), ["hair", "clothing"])
        return [e for e in elements if e in SECONDARY_ELEMENTS]

    def intensity_for_motion(self, motion: str = "idle") -> float:
        intensities = {
            "idle": 0.15,
            "walk": 0.3,
            "run": 0.5,
            "dance": 0.6,
            "jump": 0.7,
            "celebrate": 0.6,
            "wave": 0.4,
        }
        return intensities.get(motion, 0.3)

    def animate(self, element: str, motion: str = "idle") -> Optional[SecondaryMotionElement]:
        if element not in SECONDARY_ELEMENTS:
            return None
        return SecondaryMotionElement(
            element=element,
            intensity=round(self.intensity_for_motion(motion) * 0.6, 2),
            motion_type="follow_through",
            description=self.describe_element(element)["description"],
        )


# ── Character Animation Engine (facade) ─────────────────────────────────

class CharacterAnimationEngine:
    """Coordinates eye, body, and secondary motion into a character performance."""

    def __init__(self):
        self.eyes = EyeAnimationEngine()
        self.body = BodyAnimationEngine()
        self.secondary = SecondaryMotionEngine()

    def build_performance(self, motion: str = "idle", emotion: str = "happy", context: str = "") -> dict:
        body = self.body.profile(motion)
        eye_behavior = "look_at_speaker" if emotion in ("happy", "excited") else "blink_frequency"
        elements = [
            self.secondary.animate(e, motion)
            for e in self.secondary.suggest_elements(context)
            if self.secondary.animate(e, motion) is not None
        ]
        return {
            "motion": body.motion,
            "body": self.body.describe(motion),
            "eyes": self.eyes.suggest_pattern(eye_behavior).__dict__,
            "secondary_elements": [e.__dict__ for e in elements],
            "robotic_avoidance": self.body.avoid_robotic(),
        }

    def list_engines(self) -> list[str]:
        return ["eye_animation", "body_animation", "secondary_motion"]
