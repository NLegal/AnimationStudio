from __future__ import annotations
from datetime import datetime

from .models import Workflow, WorkflowStep, TaskStatus, Task


class WorkflowEngine:
    def create_workflow(self, workflow_id: str, name: str) -> Workflow:
        return Workflow(
            workflow_id=workflow_id,
            name=name,
            created_at=datetime.now().isoformat(),
        )

    def add_step(
        self,
        workflow: Workflow,
        step_id: str,
        name: str,
        task_type: str,
        dependencies: list[str] | None = None,
    ) -> WorkflowStep:
        step = WorkflowStep(
            step_id=step_id,
            name=name,
            task_type=task_type,
            dependencies=dependencies or [],
        )
        workflow.steps.append(step)
        return step

    def next_ready_steps(self, workflow: Workflow) -> list[WorkflowStep]:
        completed = {s.step_id for s in workflow.steps if s.status == TaskStatus.COMPLETED}
        return [
            s for s in workflow.steps
            if s.status == TaskStatus.QUEUED and all(d in completed for d in s.dependencies)
        ]

    def mark_step(self, workflow: Workflow, step_id: str, status: TaskStatus) -> bool:
        for step in workflow.steps:
            if step.step_id == step_id:
                step.status = status
                return True
        return False

    def is_complete(self, workflow: Workflow) -> bool:
        return len(workflow.steps) > 0 and all(
            s.status in (TaskStatus.COMPLETED, TaskStatus.VALIDATED, TaskStatus.ARCHIVED)
            for s in workflow.steps
        )

    def completion_percentage(self, workflow: Workflow) -> float:
        if not workflow.steps:
            return 0.0
        done = sum(
            1 for s in workflow.steps
            if s.status in (TaskStatus.COMPLETED, TaskStatus.VALIDATED, TaskStatus.ARCHIVED)
        )
        return round((done / len(workflow.steps)) * 100, 1)

    def complete_workflow(self, workflow: Workflow) -> bool:
        if not self.is_complete(workflow):
            return False
        workflow.status = TaskStatus.COMPLETED
        workflow.completed_at = datetime.now().isoformat()
        return True


class EpisodeWorkflowFactory:
    STEP_SEQUENCE = [
        ("story", "Generate Story"),
        ("storyboard", "Generate Storyboard"),
        ("images", "Generate Images"),
        ("animation", "Animate"),
        ("edit", "Edit"),
        ("qc", "QC"),
        ("publish", "Publish"),
        ("monitor", "Monitor"),
    ]

    def build_episode_workflow(self, episode_id: str, workflow_id: str = "") -> Workflow:
        engine = WorkflowEngine()
        workflow = engine.create_workflow(
            workflow_id or f"WF_{episode_id}",
            f"Produce Episode {episode_id}",
        )
        previous = ""
        for step_type, name in self.STEP_SEQUENCE:
            step = engine.add_step(
                workflow,
                step_id=f"{episode_id}_{step_type}",
                name=name,
                task_type=step_type,
                dependencies=[previous] if previous else None,
            )
            previous = step.step_id
        return workflow

    def create_task_for_step(self, step: WorkflowStep, episode_id: str) -> Task:
        return Task(
            task_id=f"TASK_{step.step_id}",
            task_type=step.task_type,
            dependencies=step.dependencies,
            payload={"episode_id": episode_id, "step_id": step.step_id},
        )
