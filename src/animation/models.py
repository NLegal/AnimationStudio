from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class MotionCategory(str, Enum):
    IDLE = "idle"
    WALK = "walk"
    RUN = "run"
    SKIP = "skip"
    DANCE = "dance"
    JUMP = "jump"
    WAVE = "wave"
    POINT = "point"
    CLAP = "clap"
    HUG = "hug"
    SIT = "sit"
    STAND = "stand"
    READ = "read"
    WRITE = "write"
    SLEEP = "sleep"
    EAT = "eat"
    DRINK = "drink"
    PLAY = "play"
    LAUGH = "laugh"
    CRY = "cry"
    CELEBRATE = "celebrate"


class CameraMotion(str, Enum):
    STATIC = "static"
    PAN = "pan"
    TILT = "tilt"
    TRACK = "track"
    FOLLOW = "follow"
    PUSH_IN = "push_in"
    PULL_OUT = "pull_out"
    ORBIT = "orbit"
    CRANE = "crane"
    DOLLY = "dolly"


class FacialExpression(str, Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    EXCITED = "excited"
    CURIOUS = "curious"
    SURPRISED = "surprised"
    CONFUSED = "confused"
    PROUD = "proud"
    THOUGHTFUL = "thoughtful"
    SLEEPY = "sleepy"
    LAUGHING = "laughing"
    GENTLE_SADNESS = "gentle_sadness"


class TransitionType(str, Enum):
    FADE = "fade"
    CROSSFADE = "crossfade"
    PAGE_TURN = "page_turn"
    SLIDE = "slide"
    WIPE = "wipe"
    SOFT_ZOOM = "soft_zoom"
    DISSOLVE = "dissolve"


class LightingCondition(str, Enum):
    SUNRISE = "sunrise"
    MORNING = "morning"
    NOON = "noon"
    GOLDEN_HOUR = "golden_hour"
    SUNSET = "sunset"
    NIGHT = "night"
    CLOUDS = "clouds"
    RAIN = "rain"
    SNOW = "snow"
    INDOOR = "indoor"
    HOLIDAY = "holiday"


class ParticleEffect(str, Enum):
    BUBBLES = "bubbles"
    LEAVES = "leaves"
    SNOW = "snow"
    RAIN = "rain"
    CONFETTI = "confetti"
    SPARKLES = "sparkles"
    DUST = "dust"
    MAGIC = "magic"
    BUTTERFLIES = "butterflies"
    FIREFLIES = "fireflies"


class PhysicsMaterial(str, Enum):
    BOUNCY = "bouncy"
    SOFT = "soft"
    FLOATING = "floating"
    HEAVY = "heavy"
    LIGHT = "light"


class RenderStatus(str, Enum):
    QUEUED = "queued"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class Phoneme:
    phoneme: str = ""
    start_time: float = 0.0
    end_time: float = 0.0
    mouth_shape: str = ""


@dataclass
class LipSyncTrack:
    dialogue: str = ""
    phonemes: list[Phoneme] = field(default_factory=list)
    duration: float = 0.0

    def total_phonemes(self) -> int:
        return len(self.phonemes)


@dataclass
class AnimationPlan:
    shot_id: str = ""
    motion: MotionCategory = MotionCategory.IDLE
    expression: FacialExpression = FacialExpression.NEUTRAL
    expression_transitions: list[tuple[float, FacialExpression]] = field(default_factory=list)
    camera_motion: CameraMotion = CameraMotion.STATIC
    lip_sync: Optional[LipSyncTrack] = None
    lighting: LightingCondition = LightingCondition.MORNING
    transition_in: TransitionType = TransitionType.FADE
    transition_out: TransitionType = TransitionType.FADE
    duration_seconds: float = 3.0
    particle_effects: list[ParticleEffect] = field(default_factory=list)
    physics_material: PhysicsMaterial = PhysicsMaterial.SOFT
    weather: str = "clear"
    seed: int = 42

    def has_lip_sync(self) -> bool:
        return self.lip_sync is not None and bool(self.lip_sync.dialogue)


@dataclass
class AnimationClip:
    clip_id: str = ""
    episode: str = ""
    scene: str = ""
    shot: str = ""
    characters: list[str] = field(default_factory=list)
    environment: str = ""
    animation_type: MotionCategory = MotionCategory.IDLE
    model: str = ""
    seed: int = 0
    prompt_version: str = ""
    duration_seconds: float = 0.0
    resolution_width: int = 1920
    resolution_height: int = 1080
    frame_rate: int = 24
    render_time_seconds: float = 0.0
    revision: int = 1
    approval_status: str = "pending"
    file_path: str = ""
    metadata: dict = field(default_factory=dict)

    @property
    def total_frames(self) -> int:
        return int(self.duration_seconds * self.frame_rate)

    @property
    def aspect_ratio(self) -> str:
        ratio = self.resolution_width / self.resolution_height
        if abs(ratio - 16 / 9) < 0.01:
            return "16:9"
        if abs(ratio - 4 / 3) < 0.01:
            return "4:3"
        if abs(ratio - 1.0) < 0.01:
            return "1:1"
        if abs(ratio - 9 / 16) < 0.01:
            return "9:16"
        return f"{self.resolution_width}:{self.resolution_height}"


@dataclass
class RenderJob:
    job_id: str = ""
    clip_id: str = ""
    status: RenderStatus = RenderStatus.QUEUED
    priority: int = 5
    created_at: str = ""
    completed_at: str = ""
    error: str = ""


@dataclass
class AnimationValidationResult:
    passed: bool = False
    checks: dict[str, bool] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    score: float = 0.0
