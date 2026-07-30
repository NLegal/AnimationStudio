from datetime import datetime
from typing import Optional

from .models import RenderJob, RenderStatus


class RenderQueue:
    def __init__(self):
        self._jobs: dict[str, RenderJob] = {}

    def enqueue(self, clip_id: str, priority: int = 5) -> RenderJob:
        job = RenderJob(
            clip_id=clip_id,
            status=RenderStatus.QUEUED,
            priority=priority,
            created_at=datetime.now().isoformat(),
        )
        job.job_id = f"RENDER_{clip_id}_{len(self._jobs) + 1}"
        self._jobs[job.job_id] = job
        return job

    def dequeue(self) -> Optional[RenderJob]:
        queued = sorted(
            [j for j in self._jobs.values() if j.status == RenderStatus.QUEUED],
            key=lambda j: (-j.priority, j.created_at),
        )
        if not queued:
            return None
        job = queued[0]
        job.status = RenderStatus.RENDERING
        return job

    def complete(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if job is None:
            return False
        job.status = RenderStatus.COMPLETED
        job.completed_at = datetime.now().isoformat()
        return True

    def fail(self, job_id: str, error: str = "") -> bool:
        job = self._jobs.get(job_id)
        if job is None:
            return False
        job.status = RenderStatus.FAILED
        job.error = error
        job.completed_at = datetime.now().isoformat()
        return True

    def get_job(self, job_id: str) -> Optional[RenderJob]:
        return self._jobs.get(job_id)

    def list_by_status(self, status: RenderStatus) -> list[RenderJob]:
        return [j for j in self._jobs.values() if j.status == status]

    def pending_count(self) -> int:
        return len(self.list_by_status(RenderStatus.QUEUED))

    def total_count(self) -> int:
        return len(self._jobs)

    def approve(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if job is None or job.status != RenderStatus.COMPLETED:
            return False
        job.status = RenderStatus.APPROVED
        return True

    def reject(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if job is None:
            return False
        job.status = RenderStatus.REJECTED
        return True


class RenderPipeline:
    def __init__(self, queue: Optional[RenderQueue] = None):
        self.queue = queue or RenderQueue()
        self._active_renders: set[str] = set()

    def submit_shot(self, clip_id: str, priority: int = 5) -> RenderJob:
        return self.queue.enqueue(clip_id, priority)

    def submit_batch(self, clip_ids: list[str], priority: int = 5) -> list[RenderJob]:
        return [self.queue.enqueue(cid, priority) for cid in clip_ids]

    def process_next(self) -> Optional[RenderJob]:
        job = self.queue.dequeue()
        if job:
            self._active_renders.add(job.job_id)
        return job

    def complete_job(self, job_id: str) -> bool:
        result = self.queue.complete(job_id)
        if result:
            self._active_renders.discard(job_id)
        return result

    def fail_job(self, job_id: str, error: str = "") -> bool:
        result = self.queue.fail(job_id, error)
        if result:
            self._active_renders.discard(job_id)
        return result

    def active_count(self) -> int:
        return len(self._active_renders)
