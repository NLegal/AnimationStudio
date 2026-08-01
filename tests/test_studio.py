"""Tests for Phase 12 — Studio Automation, AI Orchestration & Autonomous Production Platform.

Covers all 14 studio modules and supporting dataclasses.
"""

import pytest

from src.studio import (
    TaskStatus, WorkerType, EventType,
    Task, WorkflowStep, Workflow, StudioEvent, Agent, Worker,
    RegistryEntry, QualityReport, ResourceSnapshot, StudioMetrics,
    WorkflowEngine, EpisodeWorkflowFactory,
    EventBus,
    TaskQueue,
    AgentRegistry, WorkerPool, AGENT_SPECS,
    StudioScheduler, ScheduleEvent,
    ModelRegistry, PromptRegistry, AssetRegistry,
    MetricsCollector, StudioMonitor, ProductionTracker, Alert,
    QualityGate,
    ResourceManager, RenderFarm, ResourceAllocation,
    LearningLoop,
    StudioAnalytics, AIPerformanceTracker,
    PipelineOrchestrator,
    ErrorRecoveryEngine, Checkpoint, RecoveryRecord,
    AccessControl, AuditLog, SecurityManager,
    BackupManager, BackupJob, DisasterRecovery,
    PluginRegistry, Plugin,
    StudioDashboard,
    StudioAPI,
)


# ── Model Tests ─────────────────────────────────────────────────────────

class TestEnums:
    def test_task_status_values(self):
        assert TaskStatus.QUEUED.value == "queued"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.VALIDATED.value == "validated"
        assert TaskStatus.ARCHIVED.value == "archived"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.RETRYING.value == "retrying"

    def test_worker_type_values(self):
        assert WorkerType.GPU.value == "gpu"
        assert WorkerType.CPU.value == "cpu"
        assert WorkerType.AUDIO.value == "audio"
        assert WorkerType.VIDEO.value == "video"
        assert WorkerType.PUBLISHING.value == "publishing"
        assert WorkerType.ANALYTICS.value == "analytics"
        assert WorkerType.LOCALIZATION.value == "localization"

    def test_event_type_values(self):
        assert EventType.STORY_APPROVED.value == "story_approved"
        assert EventType.PUBLISHED.value == "published"
        assert EventType.RENDERING_FINISHED.value == "rendering_finished"
        assert EventType.PUBLISHING_READY.value == "publishing_ready"


class TestTask:
    def test_defaults(self):
        t = Task()
        assert t.task_id == ""
        assert t.status == TaskStatus.QUEUED
        assert t.priority == 0
        assert t.payload == {}
        assert t.dependencies == []
        assert t.worker_type == WorkerType.CPU
        assert t.attempts == 0
        assert t.max_retries == 3

    def test_full_init(self):
        t = Task(task_id="T", task_type="story", priority=5,
                 payload={"episode": "e1"}, dependencies=["d1"],
                 worker_type=WorkerType.GPU)
        assert t.task_id == "T"
        assert t.priority == 5
        assert t.payload["episode"] == "e1"
        assert t.dependencies == ["d1"]
        assert t.worker_type == WorkerType.GPU


class TestWorkflow:
    def test_defaults(self):
        w = Workflow()
        assert w.workflow_id == ""
        assert w.steps == []
        assert w.status == TaskStatus.QUEUED

    def test_with_steps(self):
        step = WorkflowStep(step_id="s1", task_type="story")
        w = Workflow(workflow_id="W1", name="Episode 1", steps=[step])
        assert len(w.steps) == 1
        assert w.steps[0].task_type == "story"


class TestStudioEvent:
    def test_defaults(self):
        e = StudioEvent()
        assert e.event_type == EventType.FAILED
        assert e.payload == {}

    def test_full_init(self):
        e = StudioEvent(event_id="E1", event_type=EventType.PUBLISHED, source="publishing",
                        payload={"episode": "e1"})
        assert e.event_id == "E1"
        assert e.source == "publishing"


class TestAgent:
    def test_defaults(self):
        a = Agent()
        assert a.status == "idle"
        assert a.capabilities == []

    def test_full_init(self):
        a = Agent(agent_id="A1", name="Story Writer", role="writes", capabilities=["story"])
        assert a.name == "Story Writer"
        assert "story" in a.capabilities


class TestWorker:
    def test_defaults(self):
        w = Worker()
        assert w.status == "idle"
        assert w.current_task == ""
        assert w.completed_tasks == 0

    def test_full_init(self):
        w = Worker(worker_id="W1", worker_type=WorkerType.GPU)
        assert w.worker_id == "W1"
        assert w.worker_type == WorkerType.GPU


class TestRegistryEntry:
    def test_defaults(self):
        r = RegistryEntry()
        assert r.version == "1.0"
        assert r.status == "active"
        assert r.metadata == {}

    def test_full_init(self):
        r = RegistryEntry(entry_id="R1", name="Flux", category="model")
        assert r.name == "Flux"


class TestQualityReport:
    def test_defaults(self):
        r = QualityReport()
        assert r.passed is False
        assert r.score == 0.0

    def test_full_init(self):
        r = QualityReport(subject_id="S1", subject_type="image", passed=True,
                          checks={"resolution": True}, score=1.0)
        assert r.subject_id == "S1"
        assert r.score == 1.0


class TestStudioMetrics:
    def test_defaults(self):
        m = StudioMetrics()
        assert m.episodes_produced == 0
        assert m.automation_success_rate == 1.0
        assert m.average_quality_score == 100.0

    def test_full_init(self):
        m = StudioMetrics(episodes_produced=5, retry_rate=0.1)
        assert m.episodes_produced == 5


# ── Workflow Engine Tests ───────────────────────────────────────────────

class TestWorkflowEngine:
    def setup_method(self):
        self.engine = WorkflowEngine()

    def test_create_workflow(self):
        w = self.engine.create_workflow("W1", "Episode 1")
        assert w.workflow_id == "W1"
        assert w.name == "Episode 1"
        assert w.created_at != ""

    def test_add_step(self):
        w = self.engine.create_workflow("W1", "Episode 1")
        step = self.engine.add_step(w, "s1", "Story", "story")
        assert step.step_id == "s1"
        assert step.name == "Story"
        assert step.dependencies == []

    def test_add_step_with_dependencies(self):
        w = self.engine.create_workflow("W1", "Episode 1")
        self.engine.add_step(w, "s1", "Story", "story")
        step = self.engine.add_step(w, "s2", "Storyboard", "storyboard", ["s1"])
        assert step.dependencies == ["s1"]

    def test_next_ready_steps_empty_workflow(self):
        w = self.engine.create_workflow("W1", "Episode 1")
        assert self.engine.next_ready_steps(w) == []

    def test_next_ready_steps_initial(self):
        w = self.engine.create_workflow("W1", "Episode 1")
        self.engine.add_step(w, "s1", "Story", "story")
        self.engine.add_step(w, "s2", "Storyboard", "storyboard", ["s1"])
        ready = self.engine.next_ready_steps(w)
        assert len(ready) == 1
        assert ready[0].step_id == "s1"

    def test_next_ready_steps_after_complete(self):
        w = self.engine.create_workflow("W1", "Episode 1")
        self.engine.add_step(w, "s1", "Story", "story")
        self.engine.add_step(w, "s2", "Storyboard", "storyboard", ["s1"])
        self.engine.mark_step(w, "s1", TaskStatus.COMPLETED)
        ready = self.engine.next_ready_steps(w)
        assert len(ready) == 1
        assert ready[0].step_id == "s2"

    def test_mark_step_unknown(self):
        w = self.engine.create_workflow("W1", "Episode 1")
        assert self.engine.mark_step(w, "nope", TaskStatus.COMPLETED) is False

    def test_is_complete(self):
        w = self.engine.create_workflow("W1", "Episode 1")
        self.engine.add_step(w, "s1", "Story", "story")
        assert self.engine.is_complete(w) is False
        self.engine.mark_step(w, "s1", TaskStatus.COMPLETED)
        assert self.engine.is_complete(w) is True

    def test_is_complete_empty(self):
        w = self.engine.create_workflow("W1", "Episode 1")
        assert self.engine.is_complete(w) is False

    def test_completion_percentage(self):
        w = self.engine.create_workflow("W1", "Episode 1")
        self.engine.add_step(w, "s1", "Story", "story")
        self.engine.add_step(w, "s2", "Storyboard", "storyboard", ["s1"])
        assert self.engine.completion_percentage(w) == 0.0
        self.engine.mark_step(w, "s1", TaskStatus.COMPLETED)
        assert self.engine.completion_percentage(w) == 50.0

    def test_complete_workflow(self):
        w = self.engine.create_workflow("W1", "Episode 1")
        self.engine.add_step(w, "s1", "Story", "story")
        self.engine.mark_step(w, "s1", TaskStatus.COMPLETED)
        assert self.engine.complete_workflow(w) is True
        assert w.status == TaskStatus.COMPLETED
        assert w.completed_at != ""

    def test_complete_workflow_not_done(self):
        w = self.engine.create_workflow("W1", "Episode 1")
        self.engine.add_step(w, "s1", "Story", "story")
        assert self.engine.complete_workflow(w) is False


class TestEpisodeWorkflowFactory:
    def setup_method(self):
        self.factory = EpisodeWorkflowFactory()

    def test_build_episode_workflow_sequence(self):
        w = self.factory.build_episode_workflow("ep-001")
        assert w.workflow_id == "WF_ep-001"
        step_types = [s.task_type for s in w.steps]
        assert step_types == ["story", "storyboard", "images", "animation", "edit", "qc", "publish", "monitor"]

    def test_build_episode_workflow_dependencies(self):
        w = self.factory.build_episode_workflow("ep-001")
        for i, step in enumerate(w.steps):
            if i == 0:
                assert step.dependencies == []
            else:
                assert step.dependencies == [w.steps[i - 1].step_id]

    def test_custom_workflow_id(self):
        w = self.factory.build_episode_workflow("ep-001", workflow_id="CUSTOM")
        assert w.workflow_id == "CUSTOM"

    def test_create_task_for_step(self):
        w = self.factory.build_episode_workflow("ep-001")
        task = self.factory.create_task_for_step(w.steps[0], "ep-001")
        assert task.task_id == "TASK_ep-001_story"
        assert task.task_type == "story"
        assert task.payload["episode_id"] == "ep-001"


# ── Event Bus Tests ─────────────────────────────────────────────────────

class TestEventBus:
    def setup_method(self):
        self.bus = EventBus()

    def test_publish(self):
        event = self.bus.publish(EventType.STORY_APPROVED, "workflow", {"episode": "e1"})
        assert event.event_id == "EVT_1"
        assert event.source == "workflow"
        assert event.payload["episode"] == "e1"
        assert event.timestamp != ""

    def test_subscribe_unsubscribe(self):
        self.bus.subscribe(EventType.PUBLISHED, "analytics")
        assert self.bus.subscribers_for(EventType.PUBLISHED) == ["analytics"]
        assert self.bus.unsubscribe(EventType.PUBLISHED, "analytics") is True
        assert self.bus.subscribers_for(EventType.PUBLISHED) == []

    def test_subscribe_no_duplicates(self):
        self.bus.subscribe(EventType.PUBLISHED, "analytics")
        self.bus.subscribe(EventType.PUBLISHED, "analytics")
        assert len(self.bus.subscribers_for(EventType.PUBLISHED)) == 1

    def test_unsubscribe_missing(self):
        assert self.bus.unsubscribe(EventType.PUBLISHED, "nobody") is False

    def test_events_for_type(self):
        self.bus.publish(EventType.PUBLISHED, "s1")
        self.bus.publish(EventType.FAILED, "s2")
        self.bus.publish(EventType.PUBLISHED, "s3")
        assert len(self.bus.events_for(EventType.PUBLISHED)) == 2

    def test_events_from_source(self):
        self.bus.publish(EventType.PUBLISHED, "publishing")
        self.bus.publish(EventType.FAILED, "gpu")
        assert len(self.bus.events_from("publishing")) == 1

    def test_count_and_clear(self):
        self.bus.publish(EventType.PUBLISHED)
        assert self.bus.count() == 1
        self.bus.clear()
        assert self.bus.count() == 0

    def test_all_events(self):
        self.bus.publish(EventType.STORY_APPROVED)
        self.bus.publish(EventType.RENDERING_FINISHED)
        assert len(self.bus.all_events()) == 2


# ── Task Queue Tests ────────────────────────────────────────────────────

class TestTaskQueue:
    def setup_method(self):
        self.queue = TaskQueue()

    def test_enqueue(self):
        task = self.queue.enqueue("story", {"episode": "e1"}, priority=3)
        assert task.task_id == "TASK_1"
        assert task.status == TaskStatus.QUEUED
        assert task.priority == 3
        assert task.created_at != ""

    def test_enqueue_with_dependencies(self):
        t1 = self.queue.enqueue("story")
        t2 = self.queue.enqueue("storyboard", dependencies=[t1.task_id])
        assert t2.dependencies == [t1.task_id]

    def test_ready_tasks_respect_dependencies(self):
        t1 = self.queue.enqueue("story")
        t2 = self.queue.enqueue("storyboard", dependencies=[t1.task_id])
        assert len(self.queue.ready_tasks()) == 1
        assert self.queue.ready_tasks()[0].task_id == t1.task_id
        self.queue.complete(t1.task_id)
        assert len(self.queue.ready_tasks()) == 1
        assert self.queue.ready_tasks()[0].task_id == t2.task_id

    def test_priority_ordering(self):
        self.queue.enqueue("low", priority=1)
        self.queue.enqueue("high", priority=10)
        self.queue.enqueue("mid", priority=5)
        ready = self.queue.ready_tasks()
        assert [t.task_type for t in ready] == ["high", "mid", "low"]

    def test_dequeue_marks_running(self):
        task = self.queue.enqueue("story")
        popped = self.queue.dequeue()
        assert popped.task_id == task.task_id
        assert popped.status == TaskStatus.RUNNING

    def test_dequeue_empty(self):
        assert self.queue.dequeue() is None

    def test_complete(self):
        task = self.queue.enqueue("story")
        assert self.queue.complete(task.task_id) is True
        assert self.queue.get(task.task_id).status == TaskStatus.COMPLETED
        assert self.queue.get(task.task_id).completed_at != ""

    def test_complete_unknown(self):
        assert self.queue.complete("nope") is False

    def test_validate_and_archive(self):
        task = self.queue.enqueue("story")
        self.queue.complete(task.task_id)
        assert self.queue.validate(task.task_id) is True
        assert self.queue.get(task.task_id).status == TaskStatus.VALIDATED
        assert self.queue.archive(task.task_id) is True
        assert self.queue.get(task.task_id).status == TaskStatus.ARCHIVED

    def test_fail_retries(self):
        task = self.queue.enqueue("story")
        assert self.queue.fail(task.task_id) is True
        assert self.queue.get(task.task_id).status == TaskStatus.RETRYING
        assert self.queue.get(task.task_id).attempts == 1

    def test_fail_exhausts_retries(self):
        task = self.queue.enqueue("story")
        for _ in range(task.max_retries + 1):
            self.queue.fail(task.task_id)
        assert self.queue.get(task.task_id).status == TaskStatus.FAILED
        assert self.queue.get(task.task_id).attempts == task.max_retries

    def test_retry(self):
        task = self.queue.enqueue("story")
        self.queue.fail(task.task_id)
        assert self.queue.retry(task.task_id) is True
        assert self.queue.get(task.task_id).status == TaskStatus.QUEUED

    def test_retry_non_retrying(self):
        task = self.queue.enqueue("story")
        assert self.queue.retry(task.task_id) is False

    def test_retry_unknown(self):
        assert self.queue.retry("nope") is False

    def test_counts(self):
        self.queue.enqueue("story")
        self.queue.enqueue("storyboard")
        assert self.queue.pending_count() == 2
        assert self.queue.total_count() == 2
        assert self.queue.running_count() == 0

    def test_success_rate(self):
        assert self.queue.success_rate() == 1.0
        t1 = self.queue.enqueue("story")
        t2 = self.queue.enqueue("edit")
        self.queue.complete(t1.task_id)
        self.queue.fail(t2.task_id, auto_retry=False)
        assert self.queue.success_rate() == 0.5

    def test_list_by_status(self):
        t1 = self.queue.enqueue("story")
        self.queue.enqueue("storyboard")
        self.queue.complete(t1.task_id)
        assert len(self.queue.list_by_status(TaskStatus.COMPLETED)) == 1
        assert len(self.queue.list_by_status(TaskStatus.QUEUED)) == 1


# ── Agent Registry & Worker Pool Tests ─────────────────────────────────

class TestAgentRegistry:
    def setup_method(self):
        self.registry = AgentRegistry()

    def test_register_defaults(self):
        self.registry.register_defaults()
        assert self.registry.count() == len(AGENT_SPECS) == 16

    def test_default_agent_names(self):
        self.registry.register_defaults()
        names = [a.name for a in self.registry.list_agents()]
        assert "Creative Director Agent" in names
        assert "Localization Agent" in names
        assert "Infrastructure Agent" in names

    def test_register_single(self):
        agent = Agent(agent_id="x1", name="X", role="testing")
        self.registry.register(agent)
        assert self.registry.get("x1").name == "X"

    def test_get_missing(self):
        assert self.registry.get("nope").agent_id == ""

    def test_set_status(self):
        self.registry.register(Agent(agent_id="a1"))
        assert self.registry.set_status("a1", "working") is True
        assert self.registry.get("a1").status == "working"
        assert self.registry.set_status("nope", "x") is False

    def test_assign_task(self):
        self.registry.register(Agent(agent_id="a1"))
        assert self.registry.assign_task("a1", "story") is True
        assert self.registry.get("a1").status == "working"
        assert "story" in self.registry.get("a1").capabilities


class TestWorkerPool:
    def setup_method(self):
        self.pool = WorkerPool()

    def test_add_worker(self):
        worker = self.pool.add_worker("gpu-1", WorkerType.GPU)
        assert worker.worker_id == "WORKER_1"
        assert worker.worker_type == WorkerType.GPU

    def test_workers_of_type(self):
        self.pool.add_worker("gpu-1", WorkerType.GPU)
        self.pool.add_worker("cpu-1", WorkerType.CPU)
        gpus = self.pool.workers_of_type(WorkerType.GPU)
        cpus = self.pool.workers_of_type(WorkerType.CPU)
        assert len(gpus) == 1
        assert len(cpus) == 1

    def test_idle_workers(self):
        self.pool.add_worker("cpu-1", WorkerType.CPU)
        self.pool.add_worker("cpu-2", WorkerType.CPU)
        assert len(self.pool.idle_workers()) == 2

    def test_available_for(self):
        self.pool.add_worker("gpu-1", WorkerType.GPU)
        task = Task(worker_type=WorkerType.GPU)
        worker = self.pool.available_for(task)
        assert worker is not None
        assert worker.worker_type == WorkerType.GPU

    def test_available_for_none_idle(self):
        self.pool.add_worker("gpu-1", WorkerType.GPU)
        task = Task(worker_type=WorkerType.CPU)
        assert self.pool.available_for(task) is None

    def test_assign_and_release(self):
        w = self.pool.add_worker("cpu-1", WorkerType.CPU)
        task = Task(task_id="T1")
        assert self.pool.assign(w.worker_id, task) is True
        assert self.pool.get(w.worker_id).status == "busy"
        assert self.pool.get(w.worker_id).current_task == "T1"
        assert self.pool.busy_count() == 1
        assert self.pool.release(w.worker_id) is True
        assert self.pool.get(w.worker_id).status == "idle"
        assert self.pool.get(w.worker_id).completed_tasks == 1
        assert self.pool.busy_count() == 0

    def test_total_completed_tasks(self):
        w = self.pool.add_worker("cpu-1", WorkerType.CPU)
        task = Task(task_id="T1")
        self.pool.assign(w.worker_id, task)
        self.pool.release(w.worker_id)
        self.pool.assign(w.worker_id, Task(task_id="T2"))
        self.pool.release(w.worker_id)
        assert self.pool.total_completed_tasks() == 2

    def test_assign_unknown_worker(self):
        assert self.pool.assign("nope", Task()) is False

    def test_release_unknown_worker(self):
        assert self.pool.release("nope") is False


# ── Scheduler Tests ─────────────────────────────────────────────────────

class TestStudioScheduler:
    def setup_method(self):
        self.scheduler = StudioScheduler()

    def test_schedule(self):
        event = self.scheduler.schedule("production", "Episode 1", "2026-08-01T09:00:00")
        assert event.event_id == "SCHEVT_1"
        assert event.event_type == "production"
        assert event.recurring == "once"

    def test_schedule_daily_weekly_monthly(self):
        self.scheduler.schedule_daily("cleanup", "Daily cleanup")
        self.scheduler.schedule_weekly("planning", "Weekly planning")
        self.scheduler.schedule_monthly("review", "Monthly review")
        assert len(self.scheduler.recurring_events()) == 3

    def test_events_on(self):
        self.scheduler.schedule("production", "E1", "2026-08-01")
        self.scheduler.schedule("publish", "E2", "2026-08-01")
        self.scheduler.schedule("production", "E3", "2026-08-02")
        assert len(self.scheduler.events_on("2026-08-01")) == 2

    def test_events_of_type(self):
        self.scheduler.schedule("production", "E1", "2026-08-01")
        self.scheduler.schedule("publish", "E2", "2026-08-01")
        assert len(self.scheduler.events_of_type("production")) == 1

    def test_count_and_cancel(self):
        e = self.scheduler.schedule("production", "E1", "2026-08-01")
        assert self.scheduler.count() == 1
        assert self.scheduler.cancel(e.event_id) is True
        assert self.scheduler.count() == 0
        assert self.scheduler.cancel(e.event_id) is False

    def test_get(self):
        e = self.scheduler.schedule("production", "E1", "2026-08-01")
        assert self.scheduler.get(e.event_id).subject == "E1"
        assert self.scheduler.get("nope").event_id == ""

    def test_list_all(self):
        self.scheduler.schedule("a", "E1", "2026-08-01")
        self.scheduler.schedule("b", "E2", "2026-08-01")
        assert len(self.scheduler.list_all()) == 2


# ── Registry Tests ──────────────────────────────────────────────────────

class TestModelRegistry:
    def setup_method(self):
        self.registry = ModelRegistry()

    def test_register_model(self):
        entry = self.registry.register("flux-dev", purpose="image_generation",
                                       input_type="text", output_type="image")
        assert entry.name == "flux-dev"
        assert entry.category == "model"
        assert entry.status == "active"
        assert entry.metadata["purpose"] == "image_generation"

    def test_get(self):
        self.registry.register("flux-dev")
        assert self.registry.get("flux-dev").name == "flux-dev"
        assert self.registry.get("nope").name == ""

    def test_active_models(self):
        self.registry.register("m1")
        self.registry.register("m2")
        self.registry.set_status("m2", "retired")
        assert len(self.registry.active_models()) == 1

    def test_models_for_purpose(self):
        self.registry.register("flux-dev", purpose="image_generation")
        self.registry.register("titan", purpose="language")
        assert len(self.registry.models_for_purpose("image_generation")) == 1

    def test_set_status_unknown(self):
        assert self.registry.set_status("nope", "retired") is False

    def test_swap_model(self):
        self.registry.register("flux-dev", version="1.0")
        assert self.registry.swap_model("flux-dev", "2.0") is True
        assert self.registry.get("flux-dev").version == "2.0"
        assert self.registry.swap_model("nope", "2.0") is False

    def test_count(self):
        self.registry.register("m1")
        self.registry.register("m2")
        assert self.registry.count() == 2


class TestPromptRegistry:
    def setup_method(self):
        self.registry = PromptRegistry()

    def test_register_prompt(self):
        entry = self.registry.register_prompt("character_v1", "A cheerful robot", author="artist")
        assert entry.category == "prompt"
        assert entry.status == "draft"
        assert entry.metadata["text"] == "A cheerful robot"

    def test_register_approved(self):
        entry = self.registry.register_prompt("character_v1", "text", approved=True)
        assert entry.status == "approved"

    def test_version_history(self):
        self.registry.register_prompt("character_v1", "v1 text", version="1.0")
        self.registry.register_prompt("character_v1", "v2 text", version="2.0")
        assert len(self.registry.revision_history("character_v1")) == 2
        assert self.registry.get_version("character_v1", "1.0").metadata["text"] == "v1 text"
        assert self.registry.get_version("character_v1", "2.0").metadata["text"] == "v2 text"

    def test_latest(self):
        self.registry.register_prompt("character_v1", "v1 text", version="1.0")
        self.registry.register_prompt("character_v1", "v2 text", version="2.0")
        assert self.registry.latest("character_v1").version == "2.0"

    def test_latest_missing(self):
        assert self.registry.latest("nope").name == ""

    def test_list_and_count(self):
        self.registry.register_prompt("a", "t")
        self.registry.register_prompt("a", "t2", version="2.0")
        self.registry.register_prompt("b", "t")
        assert self.registry.list_prompt_ids() == ["a", "b"]
        assert self.registry.count() == 3

    def test_model_compatibility_and_performance(self):
        entry = self.registry.register_prompt(
            "character_v1",
            "A cheerful robot",
            author="artist",
            approved=True,
            model_compatibility=["gpt-4o", "claude-sonnet"],
            performance={"latency_ms": 250, "success_rate": 0.98},
        )
        assert entry.metadata["model_compatibility"] == ["gpt-4o", "claude-sonnet"]
        assert entry.metadata["performance"]["success_rate"] == 0.98

    def test_model_compatibility_defaults(self):
        entry = self.registry.register_prompt("p", "t")
        assert entry.metadata["model_compatibility"] == []
        assert entry.metadata["performance"] == {}


class TestAssetRegistry:
    def setup_method(self):
        self.registry = AssetRegistry()

    def test_valid_categories(self):
        assert "character" in self.registry.CATEGORIES
        assert "thumbnail" in self.registry.CATEGORIES
        assert len(self.registry.CATEGORIES) == 9

    def test_register(self):
        entry = self.registry.register("Lily", "character")
        assert entry is not None
        assert entry.entry_id == "ASSET_1"
        assert entry.category == "character"

    def test_register_invalid_category(self):
        assert self.registry.register("thing", "invalid") is None

    def test_by_category(self):
        self.registry.register("Lily", "character")
        self.registry.register("Milo", "character")
        self.registry.register("bg1", "background")
        assert len(self.registry.by_category("character")) == 2

    def test_count(self):
        self.registry.register("Lily", "character")
        assert self.registry.count() == 1

    def test_all_assets(self):
        self.registry.register("Lily", "character")
        assert len(self.registry.all_assets()) == 1


# ── Monitoring Tests ────────────────────────────────────────────────────

class TestMetricsCollector:
    def setup_method(self):
        self.collector = MetricsCollector()

    def test_record(self):
        sample = self.collector.record("gpu_util", 0.75, "%")
        assert sample.name == "gpu_util"
        assert sample.value == 0.75
        assert sample.unit == "%"

    def test_series_and_latest(self):
        self.collector.record("render_time", 10.0)
        self.collector.record("render_time", 12.0)
        assert len(self.collector.series("render_time")) == 2
        assert self.collector.latest("render_time").value == 12.0
        assert self.collector.latest("nope") is None

    def test_names_and_count(self):
        self.collector.record("a", 1.0)
        self.collector.record("b", 2.0)
        assert set(self.collector.names()) == {"a", "b"}
        assert self.collector.count() == 2


class TestStudioMonitor:
    def setup_method(self):
        self.monitor = StudioMonitor()

    def test_raise_alert(self):
        alert = self.monitor.raise_alert("GPU failed", "gpu-1", "critical")
        assert alert.alert_id == "ALERT_1"
        assert alert.severity == "critical"
        assert alert.subject == "gpu-1"
        assert alert.ack is False

    def test_acknowledge(self):
        alert = self.monitor.raise_alert("test")
        assert self.monitor.acknowledge(alert.alert_id) is True
        assert alert.ack is True
        assert self.monitor.open_alerts() == []
        assert self.monitor.acknowledge("nope") is False

    def test_alerts_by_severity(self):
        self.monitor.raise_alert("warn", severity="warning")
        self.monitor.raise_alert("crit", severity="critical")
        self.monitor.raise_alert("crit2", severity="critical")
        assert len(self.monitor.critical_alerts()) == 2
        assert len(self.monitor.alerts_by_severity("warning")) == 1

    def test_snapshot(self):
        collector = MetricsCollector()
        collector.record("gpu_util", 0.8)
        collector.record("ram", 32)
        snapshot = self.monitor.snapshot(collector)
        assert snapshot["gpu_util"] == 0.8
        assert snapshot["ram"] == 32


class TestProductionTracker:
    def setup_method(self):
        self.tracker = ProductionTracker()

    def test_track_and_count(self):
        self.tracker.track("episode", TaskStatus.COMPLETED)
        self.tracker.track("episode", TaskStatus.COMPLETED)
        self.tracker.track("episode", TaskStatus.FAILED)
        assert self.tracker.count("episode", TaskStatus.COMPLETED) == 2
        assert self.tracker.count("episode", TaskStatus.FAILED) == 1

    def test_rate(self):
        self.tracker.track("episode", TaskStatus.COMPLETED)
        self.tracker.track("episode", TaskStatus.FAILED)
        assert self.tracker.rate("episode", [TaskStatus.COMPLETED, TaskStatus.FAILED]) == 0.5

    def test_rate_empty(self):
        assert self.tracker.rate("episode", [TaskStatus.COMPLETED, TaskStatus.FAILED]) == 1.0

    def test_build_metrics(self):
        self.tracker.track("episode", TaskStatus.COMPLETED)
        metrics = self.tracker.build_metrics()
        assert metrics.episodes_produced == 1
        assert metrics.recorded_at != ""

    def test_reset(self):
        self.tracker.track("episode", TaskStatus.COMPLETED)
        self.tracker.reset()
        assert self.tracker.count("episode", TaskStatus.COMPLETED) == 0


# ── Quality Gate Tests ──────────────────────────────────────────────────

class TestQualityGate:
    def setup_method(self):
        self.gate = QualityGate()

    def test_register_checker(self):
        self.gate.register_checker("resolution")
        self.gate.register_checker("duration", "Episode duration")
        assert "resolution" in self.gate.checkers()
        assert "duration" in self.gate.checkers()

    def test_evaluate_pass(self):
        report = self.gate.evaluate("img-1", "image", {"resolution": True, "style": True})
        assert report.passed is True
        assert report.errors == []
        assert report.score == 1.0

    def test_evaluate_fail(self):
        report = self.gate.evaluate("img-1", "image", {"resolution": False, "style": True})
        assert report.passed is False
        assert report.errors == ["resolution"]
        assert report.score == 0.5

    def test_evaluate_minimum_score(self):
        report = self.gate.evaluate("img-1", "image", {"a": True, "b": False}, minimum_score=0.9)
        assert report.passed is False

    def test_report_for(self):
        self.gate.evaluate("img-1", "image", {"a": True})
        assert self.gate.report_for("img-1").subject_id == "img-1"
        assert self.gate.report_for("missing").passed is False

    def test_gate_task(self):
        task = Task(task_id="T1", task_type="image")
        assert self.gate.gate_task(task, {"resolution": True, "duration": True}) is True
        assert task.status == TaskStatus.VALIDATED

    def test_gate_task_fail(self):
        task = Task(task_id="T1", task_type="image")
        assert self.gate.gate_task(task, {"resolution": False}) is False
        assert task.status != TaskStatus.VALIDATED

    def test_last_report(self):
        self.gate.evaluate("a", "image", {"x": True})
        self.gate.evaluate("b", "image", {"x": False})
        assert self.gate.last_report().subject_id == "b"

    def test_passing_rate(self):
        assert self.gate.passing_rate() == 1.0
        self.gate.evaluate("a", "image", {"x": True})
        self.gate.evaluate("b", "image", {"x": False})
        assert self.gate.passing_rate() == 0.5


# ── Resource Manager Tests ──────────────────────────────────────────────

class TestResourceManager:
    def setup_method(self):
        self.manager = ResourceManager(gpu_units=8, cpu_cores=32, ram_gb=64)

    def test_allocate(self):
        alloc = self.manager.allocate("T1", gpu=2, cpu=4, ram=8)
        assert alloc is not None
        assert alloc.allocation_id == "ALLOC_1"
        assert alloc.task_id == "T1"
        assert alloc.gpu_units == 2

    def test_allocate_insufficient(self):
        alloc = self.manager.allocate("T1", gpu=100)
        assert alloc is None

    def test_availability(self):
        self.manager.allocate("T1", gpu=2, cpu=8, ram=16)
        assert self.manager.available_gpu() == 6
        assert self.manager.available_cpu() == 24
        assert self.manager.available_ram() == 48

    def test_release(self):
        alloc = self.manager.allocate("T1", gpu=2)
        assert self.manager.release(alloc.allocation_id) is True
        assert self.manager.available_gpu() == 8
        assert self.manager.release("nope") is False

    def test_active_allocations(self):
        a1 = self.manager.allocate("T1", gpu=1)
        self.manager.allocate("T2", gpu=1)
        self.manager.release(a1.allocation_id)
        assert len(self.manager.active_allocations()) == 1

    def test_allocations_for(self):
        self.manager.allocate("T1", gpu=1)
        self.manager.allocate("T1", gpu=1)
        assert len(self.manager.allocations_for("T1")) == 2

    def test_snapshot(self):
        self.manager.allocate("T1", gpu=4, cpu=16, ram=32)
        snap = self.manager.snapshot()
        assert snap.gpu_utilization == 0.5
        assert snap.cpu_utilization == 0.5
        assert snap.ram_used_gb == 32.0

    def test_snapshot_all_fields(self):
        snap = self.manager.snapshot()
        assert snap.gpu_utilization == 0.0
        assert snap.cpu_utilization == 0.0
        assert snap.ram_used_gb == 0.0
        assert snap.vram_used_gb == 0.0
        assert snap.disk_used_gb == 0.0
        assert snap.bandwidth_mbps == 0.0
        assert snap.power_watts == 0.0
        assert snap.timestamp != ""

    def test_capacity_totals(self):
        assert self.manager.total_vram == 96
        assert self.manager.total_disk == 2048
        assert self.manager.total_bandwidth == 1000
        assert self.manager.total_power == 5000

    def test_utilization(self):
        self.manager.allocate("T1", gpu=8, cpu=32)
        assert self.manager.utilization() == 1.0

    def test_empty_snapshot(self):
        snap = ResourceManager(gpu_units=0).snapshot()
        assert snap.gpu_utilization == 0.0


class TestRenderFarm:
    def setup_method(self):
        self.farm = RenderFarm(nodes=2, gpus_per_node=4)

    def test_total_gpus(self):
        assert self.farm.total_gpus() == 8

    def test_submit(self):
        assert self.farm.submit("R1", {"episode": "e1"}) is True
        assert self.farm.pending_count() == 1
        assert self.farm.submit("R1") is False

    def test_render_next(self):
        self.farm.submit("R1")
        self.farm.submit("R2")
        assert self.farm.render_next() == "R1"
        assert self.farm.rendered_count() == 1
        assert self.farm.pending_count() == 1

    def test_render_all(self):
        self.farm.submit("R1")
        self.farm.submit("R2")
        rendered = self.farm.render_all()
        assert rendered == ["R1", "R2"]
        assert self.farm.pending_count() == 0
        assert self.farm.rendered_count() == 2

    def test_render_next_empty(self):
        assert self.farm.render_next() is None

    def test_job_status(self):
        self.farm.submit("R1")
        self.farm.render_all()
        assert self.farm.job_status("R1") == "rendered"
        assert self.farm.job_status("nope") == "unknown"
        assert self.farm.job("nope") == {}


# ── Learning Loop Tests ─────────────────────────────────────────────────

class TestLearningLoop:
    def setup_method(self):
        self.loop = LearningLoop()

    def test_record(self):
        item = self.loop.record("success", "publishing", {"episode": "e1"})
        assert item.item_id == "LEARN_1"
        assert item.category == "success"
        assert item.weight == 1.0

    def test_record_success_failure(self):
        self.loop.record_success("publishing", {"x": 1})
        self.loop.record_failure("rendering", {"y": 2})
        assert len(self.loop.by_category("success")) == 1
        assert len(self.loop.by_category("failure")) == 1

    def test_success_rate(self):
        assert self.loop.success_rate() == 1.0
        self.loop.record_success("a", {})
        self.loop.record_success("a", {})
        self.loop.record_failure("a", {})
        self.loop.record_failure("a", {})
        assert self.loop.success_rate() == 0.5

    def test_top_sources(self):
        self.loop.record_success("publishing", {})
        self.loop.record_success("publishing", {})
        self.loop.record_success("rendering", {})
        assert self.loop.top_sources(1) == ["publishing"]

    def test_count(self):
        self.loop.record_success("a", {})
        self.loop.record_failure("b", {})
        assert self.loop.count() == 2

    def test_apply_feedback(self):
        self.loop.record_success("prompts", {"prompt_id": "p1"})
        assert self.loop.apply_feedback("p1", 0.2) is True
        assert self.loop.by_category("success")[0].weight == 1.2
        assert self.loop.apply_feedback("nope", 0.2) is False

    def test_apply_feedback_floor(self):
        self.loop.record_success("prompts", {"prompt_id": "p1"})
        self.loop.apply_feedback("p1", -10.0)
        assert self.loop.by_category("success")[0].weight == 0.1


# ── Analytics Tests ─────────────────────────────────────────────────────

class TestStudioAnalytics:
    def setup_method(self):
        self.analytics = StudioAnalytics()

    def test_sample_and_average(self):
        self.analytics.sample("retention", 0.5)
        self.analytics.sample("retention", 0.7)
        assert self.analytics.average("retention") == 0.6
        assert self.analytics.latest("retention") == 0.7

    def test_average_empty(self):
        assert self.analytics.average("nope") == 0.0

    def test_generate_report(self):
        self.analytics.sample("views", 100.0)
        report = self.analytics.generate_report("views", "month")
        assert report.report_id == "REPORT_1"
        assert report.metric == "views"
        assert report.period == "month"
        assert report.value == 100.0

    def test_metrics_and_trend(self):
        self.analytics.sample("views", 1.0)
        self.analytics.sample("views", 2.0)
        assert self.analytics.metrics() == ["views"]
        assert self.analytics.trend("views") == [1.0, 2.0]

    def test_report_and_count(self):
        r = self.analytics.generate_report("views")
        assert self.analytics.report(r.report_id).metric == "views"
        assert self.analytics.report("nope").metric == ""
        assert self.analytics.count() == 1
        assert len(self.analytics.all_reports()) == 1


class TestAIPerformanceTracker:
    def setup_method(self):
        self.tracker = AIPerformanceTracker()

    def test_record_run(self):
        self.tracker.record_run("image_generation", 30.0, 0.5)
        self.tracker.record_run("image_generation", 50.0, 1.5)
        assert self.tracker.runs_for("image_generation") == 2
        assert self.tracker.average_duration() == 40.0
        assert self.tracker.average_cost() == 1.0
        assert self.tracker.total_cost() == 2.0

    def test_empty(self):
        assert self.tracker.average_duration() == 0.0
        assert self.tracker.average_cost() == 0.0
        assert self.tracker.total_runs() == 0

    def test_total_runs(self):
        self.tracker.record_run("a", 1.0)
        self.tracker.record_run("b", 2.0)
        assert self.tracker.total_runs() == 2


# ── Orchestrator Tests ──────────────────────────────────────────────────

class TestPipelineOrchestrator:
    def setup_method(self):
        self.studio = PipelineOrchestrator()
        self.studio.setup_defaults()

    def test_default_setup(self):
        assert self.studio.agent_registry.count() == 16
        assert self.studio.worker_pool.count() == 3
        assert len(self.studio.quality_gate.checkers()) == 30
        assert "story:structure" in self.studio.quality_gate.checkers()
        assert "publishing:thumbnail" in self.studio.quality_gate.checkers()
        assert "accessibility:captions" in self.studio.quality_gate.checkers()

    def test_create_pipeline(self):
        pipeline = self.studio.create_pipeline("ep-001")
        assert pipeline.workflow_id == "WF_ep-001"
        assert len(pipeline.steps) == 8

    def test_pipeline_missing(self):
        assert self.studio.pipeline("nope").workflow_id == ""

    def test_ready_steps(self):
        self.studio.create_pipeline("ep-001")
        ready = self.studio.ready_steps("ep-001")
        assert len(ready) == 1
        assert ready[0].task_type == "story"

    def test_enqueue_ready_steps(self):
        self.studio.create_pipeline("ep-001")
        tasks = self.studio.enqueue_ready_steps("ep-001")
        assert len(tasks) == 1
        assert tasks[0].task_type == "story"
        assert tasks[0].worker_type == WorkerType.CPU
        assert self.studio.task_queue.pending_count() == 1

    def test_gpu_task_type(self):
        self.studio.create_pipeline("ep-001")
        self.studio.enqueue_ready_steps("ep-001")
        self.studio.mark_step_completed("ep-001", "ep-001_story")
        self.studio.enqueue_ready_steps("ep-001")
        tasks = self.studio.task_queue.list_by_status(TaskStatus.QUEUED)
        storyboard = [t for t in tasks if t.task_type == "storyboard"]
        assert storyboard and storyboard[0].worker_type == WorkerType.CPU
        self.studio.mark_step_completed("ep-001", "ep-001_storyboard")
        self.studio.enqueue_ready_steps("ep-001")
        images = [t for t in self.studio.task_queue.list_by_status(TaskStatus.QUEUED) if t.task_type == "images"]
        assert images and images[0].worker_type == WorkerType.GPU

    def test_execute_ready_steps_uses_workers(self):
        self.studio.create_pipeline("ep-001")
        tasks = self.studio.execute_ready_steps("ep-001")
        assert len(tasks) == 1
        task = self.studio.task_queue.get(tasks[0].task_id)
        assert task.status == TaskStatus.COMPLETED

    def test_mark_step_completed(self):
        self.studio.create_pipeline("ep-001")
        assert self.studio.mark_step_completed("ep-001", "ep-001_story") is True
        assert self.studio.mark_step_completed("ep-001", "nope") is False

    def test_process_pipeline_completes(self):
        self.studio.create_pipeline("ep-001")
        assert self.studio.process_pipeline("ep-001") is True
        assert self.studio.workflow_engine.is_complete(self.studio.pipeline("ep-001"))

    def test_process_pipeline_tasks_all_complete(self):
        self.studio.create_pipeline("ep-001")
        self.studio.process_pipeline("ep-001")
        completed = self.studio.task_queue.list_by_status(TaskStatus.COMPLETED)
        assert len(completed) == 8

    def test_publish_event(self):
        event = self.studio.publish_event(EventType.PUBLISHING_READY, "pipeline", {"episode": "ep-001"})
        assert event.event_type == EventType.PUBLISHING_READY
        assert self.studio.event_bus.count() == 1

    def test_pipeline_isolation(self):
        self.studio.create_pipeline("ep-001")
        self.studio.create_pipeline("ep-002")
        assert self.studio.ready_steps("ep-002")[0].step_id == "ep-002_story"
        assert self.studio.pipeline("ep-001") is not self.studio.pipeline("ep-002")

    def test_agent_capabilities_assignment(self):
        self.studio.agent_registry.assign_task("story_writer", "story")
        assert self.studio.agent_registry.get("story_writer").status == "working"

    def test_quality_gate_via_orchestrator(self):
        task = Task(task_id="TQC", task_type="qc")
        passed = self.studio.quality_gate.gate_task(task, {"resolution": True, "duration": True})
        assert passed is True
        assert task.status == TaskStatus.VALIDATED


# ── QualityGate Domain Checkers Tests ───────────────────────────────────

class TestQualityGateDomainCheckers:
    def setup_method(self):
        self.gate = QualityGate()

    def test_domains(self):
        domains = self.gate.domains()
        assert len(domains) == 10
        assert "story" in domains
        assert "image" in domains
        assert "animation" in domains
        assert "audio" in domains
        assert "video" in domains
        assert "metadata" in domains
        assert "publishing" in domains
        assert "localization" in domains
        assert "branding" in domains
        assert "accessibility" in domains

    def test_register_domain_checkers(self):
        self.gate.register_domain_checkers("story")
        assert "story:structure" in self.gate.checkers()
        assert "story:learning_objective" in self.gate.checkers()

    def test_register_all_domain_checkers(self):
        self.gate.register_all_domain_checkers()
        assert len(self.gate.checkers()) == 30

    def test_unknown_domain(self):
        self.gate.register_domain_checkers("nope")
        assert self.gate.checkers() == []


# ── ErrorRecoveryEngine Tests ───────────────────────────────────────────

class TestErrorRecoveryEngine:
    def setup_method(self):
        self.engine = ErrorRecoveryEngine()

    def test_retry_strategy(self):
        record = self.engine.handle_failure("images", "boom")
        assert record.status == "recovered"
        assert self.engine.recovered_count() == 1

    def test_fallback_model(self):
        self.engine.set_fallback_model("images", "sd-turbo")
        record = self.engine.handle_failure("images", "boom", capability="images", strategy="fallback_model")
        assert record.status == "recovered"
        assert self.engine.fallback_model("images") == "sd-turbo"

    def test_fallback_model_escalates_without_configured(self):
        record = self.engine.handle_failure("images", "boom", capability="images", strategy="fallback_model")
        assert record.status == "escalated"
        assert self.engine.escalated_count() == 1
        assert self.engine.escalation_ids() == [record.record_id]

    def test_fallback_prompt(self):
        self.engine.set_fallback_prompt("story", "story_v2")
        record = self.engine.handle_failure("story", "bad output", capability="story", strategy="fallback_prompt")
        assert record.status == "recovered"
        assert self.engine.fallback_prompt("story") == "story_v2"

    def test_checkpoint_resume(self):
        ckpt = self.engine.save_checkpoint("WF_1", "step_2", {"progress": 0.5})
        assert ckpt.workflow_id == "WF_1"
        resumed = self.engine.resume_from_checkpoint("WF_1")
        assert resumed.state == {"progress": 0.5}
        assert self.engine.latest_checkpoint("WF_1").step_id == "step_2"
        assert len(self.engine.checkpoints_for("WF_1")) == 1

    def test_checkpoint_missing(self):
        assert self.engine.resume_from_checkpoint("nope") is None

    def test_checkpoint_strategy(self):
        self.engine.save_checkpoint("WF_1", "step_2", {"progress": 0.5})
        record = self.engine.handle_failure("WF_1", "crash", capability="WF_1", strategy="checkpoint")
        assert record.status == "recovered"

    def test_checkpoint_strategy_escalates_without(self):
        record = self.engine.handle_failure("WF_1", "crash", capability="WF_1", strategy="checkpoint")
        assert record.status == "escalated"

    def test_manual_approval(self):
        record = self.engine.handle_failure("publish", "needs review", strategy="manual_approval")
        assert record.status == "awaiting_approval"
        assert self.engine.approve(record.record_id) is True
        assert self.engine.record(record.record_id).status == "recovered"

    def test_approve_unknown(self):
        assert self.engine.approve("nope") is False

    def test_record_and_rate(self):
        self.engine.handle_failure("a", "e1")
        self.engine.handle_failure("b", "e2")
        assert self.engine.record("nope").record_id == ""
        assert len(self.engine.records()) == 2
        assert self.engine.recovery_rate() == 1.0

    def test_metadata(self):
        record = self.engine.handle_failure("a", "err")
        assert record.source == "a"
        assert record.error == "err"
        assert record.max_attempts == 3
        assert record.created_at != ""


# ── Security Tests ──────────────────────────────────────────────────────

class TestAccessControl:
    def test_assign_and_check(self):
        ac = AccessControl()
        ac.assign_role("alice", "editor")
        ac.grant("editor", "assets")
        assert ac.role_of("alice") == "editor"
        assert ac.can_access("alice", "assets") is True
        assert ac.can_access("alice", "models") is False

    def test_unknown_user_denied(self):
        ac = AccessControl()
        assert ac.can_access("bob", "assets") is False

    def test_allowed_resources(self):
        ac = AccessControl()
        ac.assign_role("bob", "admin")
        ac.grant("admin", "assets")
        ac.grant("admin", "characters")
        assert ac.allowed_resources("bob") == ["assets", "characters"]


class TestAuditLog:
    def test_log_and_query(self):
        log = AuditLog()
        event = log.log("alice", "read", "models", "allowed")
        assert event.event_id == "AUDIT_1"
        assert log.events_for("alice") == [event]
        assert log.events_on("models") == [event]
        assert log.count() == 1

    def test_multiple_actors(self):
        log = AuditLog()
        log.log("a", "read", "assets", "allowed")
        log.log("b", "read", "assets", "denied")
        assert len(log.all_events()) == 2
        assert len(log.events_for("a")) == 1
        assert len(log.events_on("assets")) == 2


class TestSecurityManager:
    def setup_method(self):
        self.manager = SecurityManager()

    def test_admin_defaults(self):
        self.manager.access.assign_role("admin_user", "admin")
        for category in self.manager.list_categories():
            assert self.manager.access.can_access("admin_user", category)

    def test_protect_allowed(self):
        self.manager.access.assign_role("admin_user", "admin")
        assert self.manager.protect("admin_user", "assets", "read") is True

    def test_protect_denied_logs(self):
        assert self.manager.protect("guest", "models", "read") is False
        assert self.manager.audit.count() == 1
        assert self.manager.audit.all_events()[0].result == "denied"

    def test_secrets(self):
        self.manager.access.assign_role("admin_user", "admin")
        self.manager.store_secret("api_key", "sk-123", "admin_user")
        assert self.manager.get_secret("api_key", "admin_user") == "sk-123"

    def test_secret_denied(self):
        self.manager.access.assign_role("admin_user", "admin")
        self.manager.store_secret("api_key", "sk-123", "admin_user")
        assert self.manager.get_secret("api_key", "guest") == ""


# ── Backup Tests ────────────────────────────────────────────────────────

class TestBackupManager:
    def setup_method(self):
        self.manager = BackupManager()

    def test_create_backup(self):
        job = self.manager.create_backup("assets", size_mb=5.2)
        assert job.backup_id == "BACKUP_1"
        assert job.scope == "assets"
        assert job.status == "completed"
        assert job.created_at != ""

    def test_queries(self):
        self.manager.create_backup("assets")
        self.manager.create_backup("assets")
        self.manager.create_backup("models")
        assert len(self.manager.backups_for("assets")) == 2
        assert len(self.manager.all_backups()) == 3
        assert self.manager.count() == 3
        assert self.manager.latest_backup("assets").backup_id == "BACKUP_2"
        assert self.manager.latest_backup("none") is None
        assert self.manager.backup("nope").backup_id == ""


class TestDisasterRecovery:
    def test_recovery_targets(self):
        dr = DisasterRecovery()
        dr.set_recovery_target("assets", "60 minutes")
        assert dr.recovery_target("assets") == "60 minutes"
        assert dr.recovery_target("none") == ""

    def test_procedures(self):
        dr = DisasterRecovery()
        dr.add_procedure("Restore assets from latest backup")
        assert dr.procedures() == ["Restore assets from latest backup"]

    def test_restore(self):
        bm = BackupManager()
        job = bm.create_backup("assets", size_mb=1.0)
        dr = DisasterRecovery(bm)
        assert dr.restore(job.backup_id) is True
        assert dr.restore_count() == 1
        assert len(dr.restore_records()) == 1

    def test_restore_unknown(self):
        dr = DisasterRecovery()
        assert dr.restore("nope") is False

    def test_restore_from_latest(self):
        bm = BackupManager()
        bm.create_backup("assets")
        bm.create_backup("assets")
        dr = DisasterRecovery(bm)
        assert dr.restore_from_latest("assets") is True
        assert "v2" in dr.restore_records()[0]
        assert dr.restore_from_latest("none") is False

    def test_verify(self):
        bm = BackupManager()
        job = bm.create_backup("assets")
        dr = DisasterRecovery(bm)
        assert dr.verify(job.backup_id) is True
        assert dr.verify("nope") is False


# ── PluginRegistry Tests ────────────────────────────────────────────────

class TestPluginRegistry:
    def setup_method(self):
        self.registry = PluginRegistry()

    def test_register(self):
        plugin = self.registry.register("stable-diffusion-xl", "image_model", version="2.0")
        assert plugin.plugin_id == "PLUGIN_stable-diffusion-xl"
        assert plugin.category == "image_model"
        assert plugin.version == "2.0"

    def test_register_invalid_category(self):
        assert self.registry.register("weird", "not_a_category") is None

    def test_categories(self):
        cats = self.registry.categories()
        assert len(cats) == 9
        assert "voice_model" in cats
        assert "publishing_platform" in cats
        assert "translation_engine" in cats
        assert "storage_provider" in cats
        assert "rendering_backend" in cats

    def test_by_category_and_get(self):
        self.registry.register("sd-xl", "image_model")
        self.registry.register("dall-e", "image_model")
        self.registry.register("gpt-4o", "video_model")
        assert len(self.registry.by_category("image_model")) == 2
        assert self.registry.get("PLUGIN_gpt-4o").category == "video_model"
        assert self.registry.get("nope").plugin_id == ""
        assert self.registry.count() == 3

    def test_replace(self):
        self.registry.register("model-a", "image_model")
        self.registry.register("model-b", "image_model")
        assert self.registry.replace("PLUGIN_model-a", "PLUGIN_model-b") is True
        assert self.registry.get("PLUGIN_model-a").status == "inactive"
        assert self.registry.get("PLUGIN_model-b").status == "active"
        assert self.registry.replace("nope", "PLUGIN_model-b") is False

    def test_disable(self):
        self.registry.register("model-a", "image_model")
        assert self.registry.disable("PLUGIN_model-a") is True
        assert self.registry.get("PLUGIN_model-a").status == "inactive"
        assert self.registry.disable("nope") is False

    def test_active(self):
        self.registry.register("model-a", "image_model")
        self.registry.register("model-b", "image_model")
        self.registry.disable("PLUGIN_model-a")
        assert len(self.registry.active()) == 1


# ── StudioDashboard Tests ───────────────────────────────────────────────

class TestStudioDashboard:
    def setup_method(self):
        self.dashboard = StudioDashboard()

    def test_reports(self):
        self.dashboard.report_queue(2, 1, 9, 0)
        self.dashboard.report_gpu(0.5, 4, 8)
        self.dashboard.report_workers(2, 1, 3)
        self.dashboard.report_publishing(1, 5, 0)
        self.dashboard.report_localization(8, 10)
        self.dashboard.report_failures(1, 2)
        self.dashboard.report_render_time(45.0, 90.0)
        self.dashboard.report_episode("in_production", "ep-001")
        self.dashboard.report_revenue(1200.0, 15.0)
        self.dashboard.report_subscribers(10000, 5.0)
        self.dashboard.report_channel_health("healthy")

    def test_snapshot_sections(self):
        self.dashboard.report_queue(1, 0, 0, 0)
        self.dashboard.report_revenue(100.0)
        snap = self.dashboard.snapshot()
        assert set(snap.keys()) == {
            "production_queue", "gpu_status", "worker_status",
            "publishing_queue", "localization_status", "failures",
            "render_time", "episode_status", "revenue",
            "subscriber_growth", "channel_health",
        }
        assert snap["production_queue"]["queued"] == 1
        assert snap["revenue"]["total"] == 100.0

    def test_from_orchestrator(self):
        studio = PipelineOrchestrator()
        studio.setup_defaults()
        dashboard = StudioDashboard(studio)
        snap = dashboard.from_orchestrator()
        assert snap["gpu_status"]["total_units"] == 8
        assert snap["worker_status"]["total"] == 3

    def test_from_orchestrator_without(self):
        snap = StudioDashboard().from_orchestrator()
        assert snap["production_queue"] == {}


# ── StudioAPI Tests ─────────────────────────────────────────────────────

class TestStudioAPI:
    def setup_method(self):
        self.api = StudioAPI()

    def test_register_route(self):
        assert self.api.register_route("publishing", "/publish", "PublishingEngine.publish", "post") is True
        assert self.api.endpoint_exists("post", "/publishing/publish") is True
        assert self.api.count() == 1

    def test_register_route_invalid(self):
        assert self.api.register_route("not_a_domain", "/x", "handler") is False
        assert self.api.register_route("publishing", "/x", "handler", "frobnicate") is False

    def test_call(self):
        self.api.register_route("studio", "/episodes", "StudioAPI.list_episodes")
        result = self.api.call("get", "/studio/episodes", limit=10)
        assert result["ok"] is True
        assert result["handler"] == "StudioAPI.list_episodes"
        assert result["params"] == {"limit": 10}

    def test_call_missing_route(self):
        result = self.api.call("get", "/studio/missing")
        assert result["ok"] is False
        assert result["error"] == "route_not_found"

    def test_call_count(self):
        self.api.register_route("analytics", "/revenue", "handler")
        self.api.call("get", "/analytics/revenue")
        self.api.call("get", "/analytics/revenue")
        assert self.api.call_count("/analytics/revenue") == 2

    def test_routes_and_domains(self):
        self.api.register_route("publishing", "/publish", "h1", "post")
        self.api.register_route("publishing", "/status", "h2")
        self.api.register_route("rendering", "/render", "h3")
        assert len(self.api.routes()) == 3
        assert len(self.api.routes_for_domain("publishing")) == 2
        assert "POST /publishing/publish" in self.api.routes()

    def test_expose(self):
        self.api.register_route("studio", "/overview", "h")
        exposed = self.api.expose("studio")
        assert exposed["domain"] == "studio"
        assert exposed["base_path"] == "/api/studio"
        assert exposed["endpoints"] == ["GET /studio/overview"]
