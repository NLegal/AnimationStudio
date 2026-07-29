"""Production Pipeline API Specification.

This module defines the FastAPI-style endpoints for the production pipeline.
Implementation requires FastAPI, uvicorn, and Pydantic.

Endpoints:
    POST /api/episodes          - Create episode
    GET  /api/episodes          - List episodes
    GET  /api/episodes/{id}     - Get episode
    POST /api/episodes/{id}/scenes     - Add scene
    POST /api/episodes/{id}/shots      - Add shot
    POST /api/episodes/{id}/manifest   - Build manifest
    POST /api/episodes/{id}/prompts    - Generate prompts
    POST /api/episodes/{id}/continuity - Validate continuity
    POST /api/render-queue      - Queue render tasks
    GET  /api/render-queue      - List render queue
    POST /api/quality-check     - Run quality gates
    GET  /api/quality-check/{shot_id} - Get QC report
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum


class ShotType(str, Enum):
    ESTABLISHING = "establishing"
    WIDE = "wide"
    MEDIUM = "medium"
    CLOSE_UP = "close-up"
    EXTREME_CLOSE_UP = "extreme_close-up"
    OVERHEAD = "overhead"
    SIDE = "side"
    TRACKING = "tracking"
    FOLLOW = "follow"
    POV = "pov"
    REACTION = "reaction"
    CUTAWAY = "cutaway"
    TRANSITION = "transition"


class CameraMovement(str, Enum):
    STATIC = "static"
    PAN_LEFT = "pan_left"
    PAN_RIGHT = "pan_right"
    TILT = "tilt"
    PUSH_IN = "push_in"
    PULL_OUT = "pull_out"
    ORBIT = "orbit"
    TRACK = "track"
    FOLLOW = "follow"
    CRANE = "crane"
    ZOOM = "zoom"


class TaskType(str, Enum):
    IMAGE = "image"
    ANIMATION = "animation"
    LIP_SYNC = "lip_sync"
    COMPOSITE = "composite"
    RENDER = "render"
    UPSCALE = "upscale"


class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# --- Request/Response Models ---

@dataclass
class CreateEpisodeRequest:
    episode_id: str
    title: str
    duration_seconds: float = 180.0
    target_age: str = "2-5"
    learning_goal: str = ""
    has_song: bool = False
    has_narration: bool = True
    characters: List[str] = None
    locations: List[str] = None

    def __post_init__(self):
        self.characters = self.characters or []
        self.locations = self.locations or []


@dataclass
class AddSceneRequest:
    scene_id: str
    title: str
    purpose: str
    location: str
    duration_seconds: float = 30.0
    mood: str = "happy"
    characters: List[str] = None

    def __post_init__(self):
        self.characters = self.characters or []


@dataclass
class AddShotRequest:
    shot_id: str
    duration_seconds: float = 3.0
    shot_type: ShotType = ShotType.MEDIUM
    camera_movement: CameraMovement = CameraMovement.STATIC
    camera_position: str = "front"
    environment: str = ""
    animation: str = "idle"
    emotion: str = "neutral"
    weather: str = "clear"
    lighting: str = "natural"
    characters: List[Dict] = None
    assets: List[str] = None

    def __post_init__(self):
        self.characters = self.characters or []
        self.assets = self.assets or []


@dataclass
class QueueRenderRequest:
    shot_ids: List[str]


@dataclass
class QualityCheckRequest:
    shot_id: str


@dataclass
class ApiResponse:
    success: bool
    data: Optional[Dict] = None
    errors: Optional[List[str]] = None
    message: Optional[str] = None


ROUTES = {
    "POST /api/episodes": {
        "description": "Create a new episode",
        "request": CreateEpisodeRequest,
        "response": ApiResponse,
        "example": {
            "episode_id": "S01E001",
            "title": "Five Colorful Ducks",
            "duration_seconds": 192,
            "learning_goal": "Primary Colors",
            "has_song": True,
        },
    },
    "POST /api/episodes/{id}/scenes": {
        "description": "Add a scene to an episode",
        "request": AddSceneRequest,
        "response": ApiResponse,
    },
    "POST /api/episodes/{id}/shots": {
        "description": "Add a shot to a scene",
        "request": AddShotRequest,
        "response": ApiResponse,
    },
    "POST /api/episodes/{id}/manifest": {
        "description": "Build episode manifest",
        "response": ApiResponse,
    },
    "POST /api/episodes/{id}/prompts": {
        "description": "Generate prompts for all shots",
        "response": ApiResponse,
    },
    "POST /api/episodes/{id}/continuity": {
        "description": "Validate continuity across all shots",
        "response": ApiResponse,
    },
    "POST /api/render-queue": {
        "description": "Add shots to render queue",
        "request": QueueRenderRequest,
        "response": ApiResponse,
    },
    "GET /api/render-queue": {
        "description": "List all tasks in render queue",
        "response": ApiResponse,
    },
    "POST /api/quality-check": {
        "description": "Run quality gates on a shot",
        "request": QualityCheckRequest,
        "response": ApiResponse,
    },
}
