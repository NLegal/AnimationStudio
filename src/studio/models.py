from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    VALIDATED = "validated"
    ARCHIVED = "archived"
    FAILED = "failed"
    RETRYING = "retrying"


class WorkerType(str, Enum):
    CPU = "cpu"
    GPU = "gpu"
    AUDIO = "audio"
    VIDEO = "video"
    PUBLISHING = "publishing"
    ANALYTICS = "analytics"
    LOCALIZATION = "localization"


class EventType(str, Enum):
    STORY_APPROVED = "story_approved"
    STORYBOARD_STARTED = "storyboard_started"
    STORYBOARD_FINISHED = "storyboard_finished"
    IMAGE_GENERATION_STARTED = "image_generation_started"
    IMAGES_APPROVED = "images_approved"
    ANIMATION_STARTED = "animation_started"
    RENDERING_FINISHED = "rendering_finished"
    PUBLISHING_READY = "publishing_ready"
    PUBLISHED = "published"
    FAILED = "failed"


@dataclass
class Task:
    task_id: str = ""
    task_type: str = ""
    status: TaskStatus = TaskStatus.QUEUED
    priority: int = 0
    payload: dict = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    worker_type: WorkerType = WorkerType.CPU
    attempts: int = 0
    max_retries: int = 3
    created_at: str = ""
    completed_at: str = ""


@dataclass
class WorkflowStep:
    step_id: str = ""
    name: str = ""
    task_type: str = ""
    dependencies: list[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.QUEUED


@dataclass
class Workflow:
    workflow_id: str = ""
    name: str = ""
    steps: list[WorkflowStep] = field(default_factory=list)
    status: TaskStatus = TaskStatus.QUEUED
    created_at: str = ""
    completed_at: str = ""


@dataclass
class StudioEvent:
    event_id: str = ""
    event_type: EventType = EventType.FAILED
    source: str = ""
    payload: dict = field(default_factory=dict)
    timestamp: str = ""


@dataclass
class Agent:
    agent_id: str = ""
    name: str = ""
    role: str = ""
    status: str = "idle"
    capabilities: list[str] = field(default_factory=list)


@dataclass
class Worker:
    worker_id: str = ""
    name: str = ""
    worker_type: WorkerType = WorkerType.CPU
    status: str = "idle"
    current_task: str = ""
    completed_tasks: int = 0


@dataclass
class RegistryEntry:
    entry_id: str = ""
    name: str = ""
    version: str = "1.0"
    category: str = ""
    status: str = "active"
    metadata: dict = field(default_factory=dict)


@dataclass
class QualityReport:
    subject_id: str = ""
    subject_type: str = ""
    passed: bool = False
    checks: dict[str, bool] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    score: float = 0.0
    timestamp: str = ""


@dataclass
class ResourceSnapshot:
    gpu_utilization: float = 0.0
    cpu_utilization: float = 0.0
    ram_used_gb: float = 0.0
    vram_used_gb: float = 0.0
    disk_used_gb: float = 0.0
    bandwidth_mbps: float = 0.0
    power_watts: float = 0.0
    timestamp: str = ""


@dataclass
class StudioMetrics:
    episodes_produced: int = 0
    average_render_time: float = 0.0
    automation_success_rate: float = 1.0
    retry_rate: float = 0.0
    average_quality_score: float = 100.0
    publishing_success_rate: float = 1.0
    time_from_concept: float = 0.0
    gpu_utilization: float = 0.0
    recorded_at: str = ""
