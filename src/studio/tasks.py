from __future__ import annotations
from datetime import datetime

from .models import Task, TaskStatus, WorkerType


class TaskQueue:
    def __init__(self):
        self._tasks: dict[str, Task] = {}
        self._counter = 0

    def enqueue(
        self,
        task_type: str,
        payload: dict | None = None,
        priority: int = 0,
        dependencies: list[str] | None = None,
        worker_type: WorkerType = WorkerType.CPU,
    ) -> Task:
        self._counter += 1
        task = Task(
            task_id=f"TASK_{self._counter}",
            task_type=task_type,
            status=TaskStatus.QUEUED,
            priority=priority,
            payload=payload or {},
            dependencies=dependencies or [],
            worker_type=worker_type,
            created_at=datetime.now().isoformat(),
        )
        self._tasks[task.task_id] = task
        return task

    def ready_tasks(self) -> list[Task]:
        ready = [
            t for t in self._tasks.values()
            if t.status == TaskStatus.QUEUED
            and all(self._tasks.get(d, Task()).status == TaskStatus.COMPLETED for d in t.dependencies)
        ]
        return sorted(ready, key=lambda t: t.priority, reverse=True)

    def dequeue(self) -> Task | None:
        ready = self.ready_tasks()
        if not ready:
            return None
        task = ready[0]
        task.status = TaskStatus.RUNNING
        return task

    def complete(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task is None:
            return False
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now().isoformat()
        return True

    def validate(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task is None:
            return False
        task.status = TaskStatus.VALIDATED
        return True

    def archive(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task is None:
            return False
        task.status = TaskStatus.ARCHIVED
        return True

    def fail(self, task_id: str, auto_retry: bool = True) -> bool:
        task = self._tasks.get(task_id)
        if task is None:
            return False
        if auto_retry and task.attempts < task.max_retries:
            task.attempts += 1
            task.status = TaskStatus.RETRYING
        else:
            task.status = TaskStatus.FAILED
        return True

    def retry(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task is None:
            return False
        if task.status != TaskStatus.RETRYING:
            return False
        task.status = TaskStatus.QUEUED
        return True

    def get(self, task_id: str) -> Task:
        return self._tasks.get(task_id, Task())

    def list_by_status(self, status: TaskStatus) -> list[Task]:
        return [t for t in self._tasks.values() if t.status == status]

    def pending_count(self) -> int:
        return sum(1 for t in self._tasks.values() if t.status == TaskStatus.QUEUED)

    def running_count(self) -> int:
        return sum(1 for t in self._tasks.values() if t.status == TaskStatus.RUNNING)

    def total_count(self) -> int:
        return len(self._tasks)

    def success_rate(self) -> float:
        if not self._tasks:
            return 1.0
        completed = sum(
            1 for t in self._tasks.values()
            if t.status in (TaskStatus.COMPLETED, TaskStatus.VALIDATED, TaskStatus.ARCHIVED)
        )
        return round(completed / len(self._tasks), 4)
