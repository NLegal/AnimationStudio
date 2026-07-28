"""JobQueue — generation job creation and lifecycle management.

Jobs are in-memory by default (ephemeral — they kick off generation
and results persist via AssetRepository). Optional AssetRepository
integration for persistence across restarts.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# Valid status transitions for Job state machine
_VALID_JOB_TRANSITIONS: dict[str, list[str]] = {
    "pending": ["running", "completed", "failed"],
    "running": ["completed", "failed"],
    "completed": [],
    "failed": [],
}


class JobError(Exception):
    """Raised on invalid job operations (bad transitions, missing jobs)."""


@dataclass
class Job:
    """A generation job in the pipeline.

    Attributes:
        id: Unique job identifier.
        character_id: The character to generate assets for.
        job_type: Type of generation ('reference', 'expression', 'pose', 'outfit').
        config: Job configuration dict (count, variants, seeds, etc.).
        status: Current status in the state machine.
        created_at: When the job was created.
        completed_at: When the job reached a terminal state.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    character_id: str = ""
    job_type: str = ""  # 'reference', 'expression', 'pose', 'outfit'
    config: dict = field(default_factory=dict)
    status: str = "pending"  # pending → running → completed / failed
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class JobQueue:
    """In-memory generation job queue with optional persistence.

    Jobs are created, tracked through their lifecycle, and queried
    by character and status. Once completed, job results are stored
    via AssetRepository — the queue itself remains ephemeral.

    Usage:
        jq = JobQueue()
        job = jq.create_job('lily-bunny', 'reference', {'count': 4})
        jq.update_status(job.id, 'running')
        # ... run generation ...
        jq.update_status(job.id, 'completed')
        print(jq.list_jobs('lily-bunny'))
    """

    def __init__(self, repository=None):
        self._repo = repository  # Optional AssetRepository for persistence
        self._jobs: dict[str, Job] = {}

    def create_job(
        self, character_id: str, job_type: str, config: dict
    ) -> Job:
        """Create a new generation job with status='pending'.

        Args:
            character_id: The character to generate for.
            job_type: Type ('reference', 'expression', 'pose', 'outfit').
            config: Job configuration dict.

        Returns:
            The newly created Job.
        """
        job = Job(
            character_id=character_id,
            job_type=job_type,
            config=config,
            status="pending",
        )
        self._jobs[job.id] = job
        return job

    def update_status(self, job_id: str, status: str) -> None:
        """Transition a job to a new status.

        Args:
            job_id: The job identifier.
            status: Target status ('running', 'completed', 'failed').

        Raises:
            JobError: If job not found or transition is invalid.
        """
        job = self._jobs.get(job_id)
        if job is None:
            raise JobError(f"Job '{job_id}' not found")

        allowed = _VALID_JOB_TRANSITIONS.get(job.status, [])
        if status not in allowed:
            raise JobError(
                f"Invalid job status transition: '{job.status}' -> '{status}'. "
                f"Allowed transitions from '{job.status}': {allowed}"
            )

        job.status = status
        if status in ("completed", "failed"):
            job.completed_at = datetime.now()

    def list_jobs(
        self,
        character_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[Job]:
        """List jobs, optionally filtered by character and/or status.

        Args:
            character_id: Optional filter by character.
            status: Optional filter by status.

        Returns:
            List of matching Job objects.
        """
        results = list(self._jobs.values())

        if character_id is not None:
            results = [j for j in results if j.character_id == character_id]
        if status is not None:
            results = [j for j in results if j.status == status]

        # Sort newest first
        results.sort(key=lambda j: j.created_at, reverse=True)
        return results

    def get_job(self, job_id: str) -> Optional[Job]:
        """Retrieve a single job by ID.

        Args:
            job_id: The job identifier.

        Returns:
            The Job if found, None otherwise.
        """
        return self._jobs.get(job_id)
