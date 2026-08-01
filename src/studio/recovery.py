from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RecoveryRecord:
    record_id: str = ""
    source: str = ""
    error: str = ""
    status: str = "pending"
    strategy: str = ""
    attempts: int = 0
    max_attempts: int = 3
    created_at: str = ""
    resolved_at: str = ""


@dataclass
class Checkpoint:
    checkpoint_id: str = ""
    workflow_id: str = ""
    step_id: str = ""
    state: dict = field(default_factory=dict)
    created_at: str = ""


class ErrorRecoveryEngine:
    def __init__(self):
        self._fallback_models: dict[str, str] = {}
        self._fallback_prompts: dict[str, str] = {}
        self._records: dict[str, RecoveryRecord] = {}
        self._checkpoints: list[Checkpoint] = []
        self._escalations: list[str] = []
        self._counter = 0

    def set_fallback_model(self, capability: str, model_name: str) -> None:
        self._fallback_models[capability] = model_name

    def fallback_model(self, capability: str) -> str:
        return self._fallback_models.get(capability, "")

    def set_fallback_prompt(self, capability: str, prompt_id: str) -> None:
        self._fallback_prompts[capability] = prompt_id

    def fallback_prompt(self, capability: str) -> str:
        return self._fallback_prompts.get(capability, "")

    def save_checkpoint(self, workflow_id: str, step_id: str, state: dict) -> Checkpoint:
        checkpoint = Checkpoint(
            checkpoint_id=f"CKPT_{self._counter}",
            workflow_id=workflow_id,
            step_id=step_id,
            state=dict(state),
            created_at=datetime.now().isoformat(),
        )
        self._counter += 1
        self._checkpoints.append(checkpoint)
        return checkpoint

    def latest_checkpoint(self, workflow_id: str) -> Checkpoint | None:
        for checkpoint in reversed(self._checkpoints):
            if checkpoint.workflow_id == workflow_id:
                return checkpoint
        return None

    def resume_from_checkpoint(self, workflow_id: str) -> Checkpoint | None:
        checkpoint = self.latest_checkpoint(workflow_id)
        if checkpoint is None:
            return None
        return checkpoint

    def checkpoints_for(self, workflow_id: str) -> list[Checkpoint]:
        return [c for c in self._checkpoints if c.workflow_id == workflow_id]

    def handle_failure(
        self,
        source: str,
        error: str,
        capability: str = "",
        strategy: str = "retry",
        max_attempts: int = 3,
    ) -> RecoveryRecord:
        self._counter += 1
        record = RecoveryRecord(
            record_id=f"REC_{self._counter}",
            source=source,
            error=error,
            status="pending",
            strategy=strategy,
            max_attempts=max_attempts,
            created_at=datetime.now().isoformat(),
        )
        self._records[record.record_id] = record
        self._resolve(record, capability)
        return record

    def _resolve(self, record: RecoveryRecord, capability: str) -> None:
        if record.strategy == "fallback_model":
            if self.fallback_model(capability):
                self._apply_recovery(record, f"fallback model {self.fallback_model(capability)}")
            else:
                self._escalate(record)
        elif record.strategy == "fallback_prompt":
            if self.fallback_prompt(capability):
                self._apply_recovery(record, f"fallback prompt {self.fallback_prompt(capability)}")
            else:
                self._escalate(record)
        elif record.strategy == "checkpoint":
            if self.latest_checkpoint(capability):
                self._apply_recovery(record, "resumed from checkpoint")
            else:
                self._escalate(record)
        elif record.strategy == "manual_approval":
            record.status = "awaiting_approval"
        elif record.strategy == "retry":
            self._apply_recovery(record, "automatic retry")

    def _apply_recovery(self, record: RecoveryRecord, detail: str) -> None:
        record.status = "recovered"
        record.resolved_at = datetime.now().isoformat()

    def _escalate(self, record: RecoveryRecord) -> None:
        record.status = "escalated"
        record.resolved_at = datetime.now().isoformat()
        self._escalations.append(record.record_id)

    def approve(self, record_id: str) -> bool:
        record = self._records.get(record_id)
        if record is None or record.status != "awaiting_approval":
            return False
        record.status = "recovered"
        record.resolved_at = datetime.now().isoformat()
        return True

    def record(self, record_id: str) -> RecoveryRecord:
        return self._records.get(record_id, RecoveryRecord())

    def records(self) -> list[RecoveryRecord]:
        return list(self._records.values())

    def recovered_count(self) -> int:
        return sum(1 for r in self._records.values() if r.status == "recovered")

    def escalated_count(self) -> int:
        return len(self._escalations)

    def escalation_ids(self) -> list[str]:
        return list(self._escalations)

    def recovery_rate(self) -> float:
        if not self._records:
            return 1.0
        resolved = sum(
            1 for r in self._records.values()
            if r.status in ("recovered", "awaiting_approval")
        )
        return round(resolved / len(self._records), 4)
