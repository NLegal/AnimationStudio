"""Data models for the Phase 4 Animation Bible & Motion System.

These frozen dataclasses encode the quantitative standards from the
`Animation/` markdown bibles so the animation pipeline can query them
programmatically instead of hard-coding frame counts and rules.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Idle / subtle-movement layers
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class IdleLayer:
    name: str
    rate: str
    frames: int
    amplitude: str
    description: str


# ---------------------------------------------------------------------------
# Locomotion (walk / run) variants
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LocomotionVariant:
    name: str
    frames_per_step: int
    frames_per_stride: int
    speed_percent: int
    body: str
    arms: str
    legs: str
    height_variation: str
    easing: str
    description: str
    gait: str = "walk"
    air_frames: int = 0
    loopable: bool = True


# ---------------------------------------------------------------------------
# Jumps
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class JumpPhase:
    name: str
    frames: int
    description: str


@dataclass(frozen=True)
class JumpCycle:
    name: str
    phases: tuple[JumpPhase, ...]
    total_frames: int
    height_percent: int
    description: str
    loopable: bool = False


# ---------------------------------------------------------------------------
# Dance loops
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class DanceLoop:
    name: str
    frames: int
    bpm: int
    description: str
    spacing: str
    difficulty: str
    loopable: bool = True


# ---------------------------------------------------------------------------
# Facial acting
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExpressionLevel:
    intensity: int
    name: str
    face: str


@dataclass(frozen=True)
class FacialExpression:
    emotion: str
    levels: tuple[ExpressionLevel, ...]
    description: str = ""


@dataclass(frozen=True)
class BlinkType:
    name: str
    frames: str
    duration: str
    usage: str


@dataclass(frozen=True)
class MouthAction:
    name: str
    timing: str
    notes: str


# ---------------------------------------------------------------------------
# Gestures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Gesture:
    name: str
    frames: str
    arm: str
    hand: str
    posture: str
    use: str
    note: str = ""


# ---------------------------------------------------------------------------
# Interactions
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class InteractionPhase:
    phase: str
    frames: int
    description: str


@dataclass(frozen=True)
class Interaction:
    name: str
    phases: tuple[InteractionPhase, ...]
    total_frames: int
    description: str
    loopable: bool = False


# ---------------------------------------------------------------------------
# Camera language
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CameraShot:
    name: str
    description: str
    min_frames: int
    max_frames: int
    composition: str
    movement: str
    use: str
    notes: str = ""


@dataclass(frozen=True)
class SceneTransition:
    name: str
    min_frames: int
    max_frames: int
    description: str
    curve: str
    use: str
    rules: str = ""


# ---------------------------------------------------------------------------
# Physics / cloth
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PhysicsRule:
    name: str
    value: str
    notes: str = ""


@dataclass(frozen=True)
class ClothElement:
    name: str
    delay_frames: int
    amplitude: str
    settle_frames: int
    description: str


# ---------------------------------------------------------------------------
# Timing / pacing
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PacingStandard:
    age: str
    multiplier: float
    notes: str = ""


@dataclass(frozen=True)
class ShotHold:
    shot: str
    min_frames: int
    recommended: str
    max_frames: int


@dataclass(frozen=True)
class ReactionStandard:
    event: str
    delay: str
    total_processing: str


@dataclass(frozen=True)
class ActionTiming:
    action: str
    min_frames: int
    recommended: str
    readability: str


@dataclass(frozen=True)
class EmotionalBeat:
    emotion: str
    onset: str
    hold: str
    recovery: str


# ---------------------------------------------------------------------------
# Cycle library
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MotionCycle:
    motion: str
    base_frames: int
    looping: bool
    description: str
    complexity: str


# ---------------------------------------------------------------------------
# Motion brief (the resolved, bible-conformant plan for a shot)
# ---------------------------------------------------------------------------

@dataclass
class MotionBrief:
    motion: str
    frames_per_cycle: int
    loopable: bool
    cycles: int
    duration_seconds: float
    fps: int
    cycle_notes: str
    expression: str
    expression_level: int
    blink: str
    blink_frames: str
    camera_shot: str
    transition_in: str
    transition_out: str
    physics: str
    physics_notes: str
    secondary_elements: list[str] = field(default_factory=list)
    pacing_note: str = ""
    negative_prompt: str = ""

    def to_dict(self) -> dict:
        return {
            "motion": self.motion,
            "frames_per_cycle": self.frames_per_cycle,
            "loopable": self.loopable,
            "cycles": self.cycles,
            "duration_seconds": self.duration_seconds,
            "fps": self.fps,
            "cycle_notes": self.cycle_notes,
            "expression": self.expression,
            "expression_level": self.expression_level,
            "blink": self.blink,
            "blink_frames": self.blink_frames,
            "camera_shot": self.camera_shot,
            "transition_in": self.transition_in,
            "transition_out": self.transition_out,
            "physics": self.physics,
            "physics_notes": self.physics_notes,
            "secondary_elements": list(self.secondary_elements),
            "pacing_note": self.pacing_note,
            "negative_prompt": self.negative_prompt,
        }


# ---------------------------------------------------------------------------
# Doc consistency check
# ---------------------------------------------------------------------------

@dataclass
class DocFact:
    file: str
    token: str
    expected: str
    found: bool = False
    detail: str = ""


@dataclass
class DocConsistencyReport:
    facts: list[DocFact] = field(default_factory=list)
    missing_files: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.missing_files and all(f.found for f in self.facts)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "facts_checked": len(self.facts),
            "facts_passed": sum(1 for f in self.facts if f.found),
            "facts_failed": [f.file + " -> " + f.token for f in self.facts if not f.found],
            "missing_files": self.missing_files,
        }
