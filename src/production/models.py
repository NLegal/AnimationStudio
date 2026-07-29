from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, List


@dataclass
class Camera:
    shot_type: str = "medium"
    movement: str = "static"
    position: str = "front"

    def to_prompt_suffix(self) -> str:
        parts = []
        if self.movement and self.movement != "static":
            parts.append(f"{self.movement} camera")
        parts.append(f"{self.shot_type} shot")
        parts.append(f"{self.position} view")
        return ", ".join(parts)


@dataclass
class CharacterAssignment:
    character_id: str = ""
    visible: bool = True
    speaking: bool = False
    singing: bool = False
    animation: str = "idle"
    emotion: str = "neutral"
    clothing: Optional[str] = None
    accessories: List[str] = field(default_factory=list)


@dataclass
class TimelineEvent:
    timestamp: float = 0.0
    event_type: str = "narration"
    description: str = ""
    duration: float = 2.0


@dataclass
class DialogueEvent:
    character: str = ""
    line: str = ""
    start_time: float = 0.0
    end_time: float = 2.0
    emotion: str = "neutral"


@dataclass
class MusicEvent:
    track_id: str = ""
    start_time: float = 0.0
    end_time: float = 30.0
    music_type: str = "background"


@dataclass
class AnimationEvent:
    character: str = ""
    animation_type: str = "idle"
    start_time: float = 0.0
    duration: float = 2.0
    loop: bool = True


@dataclass
class AssetReference:
    asset_id: str = ""
    category: str = ""
    placement: Optional[str] = None
    variant: Optional[str] = None


@dataclass
class RenderTask:
    shot_id: str = ""
    task_type: str = "image"
    status: str = "queued"
    priority: int = 5
    dependencies: List[str] = field(default_factory=list)


@dataclass
class QCReport:
    shot_id: str = ""
    checks: Dict[str, bool] = field(default_factory=dict)
    notes: Optional[str] = None
    approved: bool = False


@dataclass
class ProductionTokens:
    character: Optional[str] = None
    location: Optional[str] = None
    camera: Optional[str] = None
    lighting: Optional[str] = None
    emotion: Optional[str] = None
    animation: Optional[str] = None
    weather: Optional[str] = None
    season: Optional[str] = None

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "Character": self.character,
            "Location": self.location,
            "Camera": self.camera,
            "Lighting": self.lighting,
            "Emotion": self.emotion,
            "Animation": self.animation,
            "Weather": self.weather,
            "Season": self.season,
        }


@dataclass
class Shot:
    id: str = ""
    scene_id: str = ""
    duration_seconds: float = 3.0
    camera: Camera = field(default_factory=Camera)
    characters: List[CharacterAssignment] = field(default_factory=list)
    assets: List[str] = field(default_factory=list)
    environment: str = ""
    animation: str = "idle"
    lighting: str = "natural"
    weather: str = "clear"
    dialogue: Optional[str] = None
    song_timestamp: Optional[float] = None
    emotion: str = "neutral"
    movement: str = "static"
    transition: str = "cut"
    prompt_id: Optional[str] = None
    negative_prompt_id: Optional[str] = None
    tokens: Optional[ProductionTokens] = None

    @property
    def frame_count(self) -> int:
        return int(self.duration_seconds * 24)


@dataclass
class Scene:
    id: str = ""
    episode_id: str = ""
    title: str = ""
    purpose: str = ""
    duration_seconds: float = 30.0
    characters: List[str] = field(default_factory=list)
    location: str = ""
    learning_objective: Optional[str] = None
    has_dialogue: bool = False
    has_song: bool = False
    mood: str = "happy"
    transition: str = "cross_dissolve"
    shots: List[Shot] = field(default_factory=list)
    dialogue: List[DialogueEvent] = field(default_factory=list)
    music: List[MusicEvent] = field(default_factory=list)
    assets: List[str] = field(default_factory=list)
    animation_notes: Optional[str] = None
    camera_notes: Optional[str] = None


@dataclass
class EpisodeManifest:
    episode_id: str = ""
    title: str = ""
    duration_seconds: float = 180.0
    target_age: str = "2-5"
    learning_goal: str = ""
    has_song: bool = False
    has_narration: bool = True
    characters: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    assets: List[str] = field(default_factory=list)
    scene_count: int = 0
    shot_count: int = 0
    estimated_video_clips: int = 0
    estimated_images: int = 0


@dataclass
class Episode:
    id: str = ""
    title: str = ""
    manifest: Optional[EpisodeManifest] = None
    duration_seconds: float = 180.0
    timeline: List[TimelineEvent] = field(default_factory=list)
    scenes: List[Scene] = field(default_factory=list)

    @property
    def scene_count(self) -> int:
        return len(self.scenes)

    @property
    def shot_count(self) -> int:
        return sum(len(s.shots) for s in self.scenes)

    def total_estimated_images(self) -> int:
        return sum(len(s.shots) for s in self.scenes)


@dataclass
class Season:
    id: str = ""
    series_id: str = ""
    episodes: List[Episode] = field(default_factory=list)


@dataclass
class Series:
    id: str = ""
    title: str = ""
    seasons: List[Season] = field(default_factory=list)
