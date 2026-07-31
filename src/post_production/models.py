from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class VideoTrackType(str, Enum):
    ANIMATION = "animation"
    BACKGROUND = "background"
    EFFECTS = "effects"
    OVERLAY = "overlay"
    TITLES = "titles"


class AudioTrackType(str, Enum):
    DIALOGUE = "dialogue"
    NARRATION = "narration"
    SINGING = "singing"
    LEARNING_SOUNDS = "learning_sounds"
    SOUND_EFFECTS = "sound_effects"
    MUSIC = "music"
    AMBIENCE = "ambience"


class TransitionStyle(str, Enum):
    FADE = "fade"
    CROSSFADE = "crossfade"
    SLIDE = "slide"
    ZOOM = "zoom"
    PAGE_TURN = "page_turn"
    SOFT_WIPE = "soft_wipe"
    DISSOLVE = "dissolve"
    QUICK_CUT = "quick_cut"
    NONE = "none"


@dataclass
class TimelineEvent:
    event_id: str = ""
    start_time: float = 0.0
    end_time: float = 0.0
    duration: float = 0.0
    clip_id: str = ""
    video_track: VideoTrackType = VideoTrackType.ANIMATION
    audio_track: AudioTrackType = AudioTrackType.DIALOGUE
    transition_in: TransitionStyle = TransitionStyle.NONE
    transition_out: TransitionStyle = TransitionStyle.NONE
    metadata: dict = field(default_factory=dict)


@dataclass
class TimelineTrack:
    name: str = ""
    events: list[TimelineEvent] = field(default_factory=list)
    order: int = 0

    def total_duration(self) -> float:
        if not self.events:
            return 0.0
        return max(e.end_time for e in self.events)

    def event_count(self) -> int:
        return len(self.events)


@dataclass
class MasterTimeline:
    episode_id: str = ""
    title: str = ""
    duration_seconds: float = 0.0
    tracks: list[TimelineTrack] = field(default_factory=list)
    frame_rate: int = 24
    resolution_width: int = 1920
    resolution_height: int = 1080
    created_at: str = ""
    version: int = 1

    @property
    def total_frames(self) -> int:
        return int(self.duration_seconds * self.frame_rate)


@dataclass
class ClipReference:
    clip_id: str = ""
    episode: str = ""
    scene: str = ""
    shot: str = ""
    duration: float = 0.0
    frame_rate: int = 24
    resolution_width: int = 1920
    resolution_height: int = 1080
    approval_status: str = "pending"
    version: int = 1
    revision: int = 1


@dataclass
class SceneAssembly:
    episode_id: str = ""
    opening: list[ClipReference] = field(default_factory=list)
    introduction: list[ClipReference] = field(default_factory=list)
    learning: list[ClipReference] = field(default_factory=list)
    song: list[ClipReference] = field(default_factory=list)
    practice: list[ClipReference] = field(default_factory=list)
    review: list[ClipReference] = field(default_factory=list)
    celebration: list[ClipReference] = field(default_factory=list)
    outro: list[ClipReference] = field(default_factory=list)

    def total_clips(self) -> int:
        return sum(len(v) for v in self.__dict__.values() if isinstance(v, list))

    def total_duration(self) -> float:
        return sum(
            c.duration for section in [
                self.opening, self.introduction, self.learning, self.song,
                self.practice, self.review, self.celebration, self.outro,
            ] for c in section
        )


@dataclass
class ExportPreset:
    name: str = ""
    resolution_width: int = 1920
    resolution_height: int = 1080
    frame_rate: int = 24
    video_bitrate: str = "8 Mbps"
    audio_bitrate: str = "192 kbps"
    format: str = "mp4"
    description: str = ""


@dataclass
class QCResult:
    passed: bool = False
    checks: dict[str, bool] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    score: float = 0.0
    timestamp: str = ""


@dataclass
class ArchiveRecord:
    project_id: str = ""
    master_video: str = ""
    source_clips: list[str] = field(default_factory=list)
    audio_stems: list[str] = field(default_factory=list)
    subtitles: list[str] = field(default_factory=list)
    thumbnails: list[str] = field(default_factory=list)
    metadata_file: str = ""
    prompt_versions: list[str] = field(default_factory=list)
    render_settings: str = ""
    qc_report: str = ""
    archived_at: str = ""
