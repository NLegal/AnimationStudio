from __future__ import annotations
from datetime import datetime

from .models import (
    EventType,
    Task,
    TaskStatus,
    WorkerType,
    Workflow,
)
from .events import EventBus
from .tasks import TaskQueue
from .agents import AgentRegistry, WorkerPool
from .workflow import WorkflowEngine, EpisodeWorkflowFactory
from .quality import QualityGate
from .registry import ModelRegistry
from .resources import ResourceManager


class PipelineOrchestrator:
    STAGE_ORDER = ["story", "storyboard", "images", "animation", "edit", "qc", "publish"]

    def __init__(self):
        self.workflow_engine = WorkflowEngine()
        self.episode_factory = EpisodeWorkflowFactory()
        self.event_bus = EventBus()
        self.task_queue = TaskQueue()
        self.agent_registry = AgentRegistry()
        self.worker_pool = WorkerPool()
        self.quality_gate = QualityGate()
        self.model_registry = ModelRegistry()
        self.resource_manager = ResourceManager()
        self.agents = self.agent_registry
        self._pipelines: dict[str, Workflow] = {}

    def setup_defaults(self) -> None:
        self.agent_registry.register_defaults()
        self.worker_pool.add_worker("gpu-renderer-1", WorkerType.GPU)
        self.worker_pool.add_worker("cpu-worker-1", WorkerType.CPU)
        self.worker_pool.add_worker("cpu-worker-2", WorkerType.CPU)
        self.quality_gate.register_all_domain_checkers()

    def create_pipeline(self, episode_id: str) -> Workflow:
        pipeline = self.episode_factory.build_episode_workflow(episode_id)
        self._pipelines[episode_id] = pipeline
        return pipeline

    def pipeline(self, episode_id: str) -> Workflow:
        return self._pipelines.get(episode_id, Workflow())

    def ready_steps(self, episode_id: str) -> list:
        pipeline = self.pipeline(episode_id)
        if pipeline.workflow_id:
            return self.workflow_engine.next_ready_steps(pipeline)
        return []

    def enqueue_ready_steps(self, episode_id: str) -> list[Task]:
        pipeline = self.pipeline(episode_id)
        tasks = []
        for step in self.workflow_engine.next_ready_steps(pipeline):
            worker_type = WorkerType.GPU if step.task_type in ("images", "animation") else WorkerType.CPU
            task = self.task_queue.enqueue(
                task_type=step.task_type,
                payload={"episode_id": episode_id, "step_id": step.step_id},
                worker_type=worker_type,
            )
            self.workflow_engine.mark_step(pipeline, step.step_id, TaskStatus.RUNNING)
            tasks.append(task)
        return tasks

    def execute_ready_steps(self, episode_id: str) -> list[Task]:
        tasks = self.enqueue_ready_steps(episode_id)
        for task in tasks:
            worker = self.worker_pool.available_for(task)
            if worker is not None:
                self.worker_pool.assign(worker.worker_id, task)
                self.task_queue.complete(task.task_id)
                self.worker_pool.release(worker.worker_id)
        return tasks

    def mark_step_completed(self, episode_id: str, step_id: str) -> bool:
        pipeline = self.pipeline(episode_id)
        return self.workflow_engine.mark_step(pipeline, step_id, TaskStatus.COMPLETED)

    def process_pipeline(self, episode_id: str, passes: int = 10) -> bool:
        for _ in range(passes):
            tasks = self.execute_ready_steps(episode_id)
            if not tasks:
                break
            for task in tasks:
                self.mark_step_completed(episode_id, task.payload["step_id"])
        return self.workflow_engine.is_complete(self.pipeline(episode_id))

    def publish_event(self, event_type: EventType, source: str, payload: dict | None = None):
        return self.event_bus.publish(event_type, source, payload)
