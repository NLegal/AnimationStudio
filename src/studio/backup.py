from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class BackupJob:
    backup_id: str = ""
    scope: str = ""
    version: str = "1"
    status: str = "completed"
    size_mb: float = 0.0
    created_at: str = ""


class BackupManager:
    def __init__(self):
        self._backups: dict[str, BackupJob] = {}
        self._counter = 0

    def create_backup(self, scope: str, size_mb: float = 0.0) -> BackupJob:
        self._counter += 1
        job = BackupJob(
            backup_id=f"BACKUP_{self._counter}",
            scope=scope,
            version=str(self._counter),
            status="completed",
            size_mb=size_mb,
            created_at=datetime.now().isoformat(),
        )
        self._backups[job.backup_id] = job
        return job

    def backup(self, backup_id: str) -> BackupJob:
        return self._backups.get(backup_id, BackupJob())

    def backups_for(self, scope: str) -> list[BackupJob]:
        return [b for b in self._backups.values() if b.scope == scope]

    def latest_backup(self, scope: str) -> BackupJob | None:
        backups = self.backups_for(scope)
        return backups[-1] if backups else None

    def all_backups(self) -> list[BackupJob]:
        return list(self._backups.values())

    def count(self) -> int:
        return len(self._backups)


class DisasterRecovery:
    def __init__(self, backup_manager: BackupManager | None = None):
        self.backup_manager = backup_manager or BackupManager()
        self._targets: dict[str, str] = {}
        self._restores: dict[str, str] = {}
        self._procedures: list[str] = []
        self._counter = 0

    def set_recovery_target(self, scope: str, rto_minutes: str) -> None:
        self._targets[scope] = rto_minutes

    def recovery_target(self, scope: str) -> str:
        return self._targets.get(scope, "")

    def add_procedure(self, procedure: str) -> None:
        self._procedures.append(procedure)

    def procedures(self) -> list[str]:
        return list(self._procedures)

    def restore(self, backup_id: str, target: str = "production") -> bool:
        job = self.backup_manager.backup(backup_id)
        if job.backup_id == "":
            return False
        self._counter += 1
        self._restores[f"RESTORE_{self._counter}"] = (
            f"{target} <- {backup_id} (v{job.version})"
        )
        return True

    def restore_from_latest(self, scope: str, target: str = "production") -> bool:
        job = self.backup_manager.latest_backup(scope)
        if job is None:
            return False
        return self.restore(job.backup_id, target)

    def restore_records(self) -> list[str]:
        return list(self._restores.values())

    def restore_count(self) -> int:
        return len(self._restores)

    def verify(self, backup_id: str) -> bool:
        return self.backup_manager.backup(backup_id).backup_id != ""
