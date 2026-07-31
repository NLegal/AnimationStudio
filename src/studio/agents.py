from __future__ import annotations

from .models import Agent, Worker, WorkerType, Task, TaskStatus

AGENT_SPECS: dict[str, dict] = {
    "creative_director": {"name": "Creative Director Agent", "role": "oversees creative vision and brand"},
    "curriculum_planner": {"name": "Curriculum Planner Agent", "role": "plans educational curriculum"},
    "story_writer": {"name": "Story Writer Agent", "role": "writes episode stories"},
    "storyboard": {"name": "Storyboard Agent", "role": "creates storyboards"},
    "prompt_engineer": {"name": "Prompt Engineer Agent", "role": "designs generation prompts"},
    "image_generation": {"name": "Image Generation Agent", "role": "generates images"},
    "animation": {"name": "Animation Agent", "role": "animates shots"},
    "audio": {"name": "Audio Agent", "role": "produces audio"},
    "editor": {"name": "Editor Agent", "role": "edits episodes"},
    "quality_assurance": {"name": "Quality Assurance Agent", "role": "validates output quality"},
    "seo": {"name": "SEO Agent", "role": "optimizes discoverability"},
    "publishing": {"name": "Publishing Agent", "role": "publishes episodes"},
    "analytics": {"name": "Analytics Agent", "role": "analyzes performance"},
    "trend_research": {"name": "Trend Research Agent", "role": "researches trends"},
    "localization": {"name": "Localization Agent", "role": "localizes content"},
    "infrastructure": {"name": "Infrastructure Agent", "role": "manages infrastructure"},
}


class AgentRegistry:
    def __init__(self):
        self._agents: dict[str, Agent] = {}

    def register_defaults(self) -> None:
        for agent_id, spec in AGENT_SPECS.items():
            self.register(Agent(agent_id=agent_id, name=spec["name"], role=spec["role"]))

    def register(self, agent: Agent) -> Agent:
        self._agents[agent.agent_id] = agent
        return agent

    def get(self, agent_id: str) -> Agent:
        return self._agents.get(agent_id, Agent())

    def list_agents(self) -> list[Agent]:
        return list(self._agents.values())

    def count(self) -> int:
        return len(self._agents)

    def set_status(self, agent_id: str, status: str) -> bool:
        agent = self._agents.get(agent_id)
        if agent is None:
            return False
        agent.status = status
        return True

    def assign_task(self, agent_id: str, task_type: str) -> bool:
        agent = self._agents.get(agent_id)
        if agent is None:
            return False
        agent.status = "working"
        agent.capabilities.append(task_type)
        return True


class WorkerPool:
    def __init__(self):
        self._workers: dict[str, Worker] = {}
        self._counter = 0

    def add_worker(self, name: str, worker_type: WorkerType = WorkerType.CPU) -> Worker:
        self._counter += 1
        worker = Worker(
            worker_id=f"WORKER_{self._counter}",
            name=name,
            worker_type=worker_type,
        )
        self._workers[worker.worker_id] = worker
        return worker

    def get(self, worker_id: str) -> Worker:
        return self._workers.get(worker_id, Worker())

    def list_workers(self) -> list[Worker]:
        return list(self._workers.values())

    def workers_of_type(self, worker_type: WorkerType) -> list[Worker]:
        return [w for w in self._workers.values() if w.worker_type == worker_type]

    def idle_workers(self) -> list[Worker]:
        return [w for w in self._workers.values() if w.status == "idle"]

    def available_for(self, task: Task) -> Worker | None:
        for worker in self.workers_of_type(task.worker_type):
            if worker.status == "idle":
                return worker
        return None

    def assign(self, worker_id: str, task: Task) -> bool:
        worker = self._workers.get(worker_id)
        if worker is None:
            return False
        worker.status = "busy"
        worker.current_task = task.task_id
        return True

    def release(self, worker_id: str) -> bool:
        worker = self._workers.get(worker_id)
        if worker is None:
            return False
        worker.status = "idle"
        worker.current_task = ""
        worker.completed_tasks += 1
        return True

    def count(self) -> int:
        return len(self._workers)

    def busy_count(self) -> int:
        return sum(1 for w in self._workers.values() if w.status == "busy")

    def total_completed_tasks(self) -> int:
        return sum(w.completed_tasks for w in self._workers.values())
