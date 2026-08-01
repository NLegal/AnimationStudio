from __future__ import annotations
from datetime import datetime


class StudioDashboard:
    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator
        self._queue_metrics: dict[str, dict] = {}
        self._gpu_metrics: dict[str, float] = {}
        self._worker_metrics: dict[str, dict] = {}
        self._publishing_metrics: dict[str, dict] = {}
        self._localization_metrics: dict[str, dict] = {}
        self._failure_metrics: dict[str, dict] = {}
        self._render_metrics: dict[str, dict] = {}
        self._episode_metrics: dict[str, dict] = {}
        self._revenue_metrics: dict[str, float] = {}
        self._subscriber_metrics: dict[str, float] = {}
        self._channel_metrics: dict[str, str] = {}

    def report_queue(self, queued: int, running: int, completed: int, failed: int) -> None:
        self._queue_metrics = {
            "queued": queued,
            "running": running,
            "completed": completed,
            "failed": failed,
            "updated_at": datetime.now().isoformat(),
        }

    def report_gpu(self, utilization: float, free_units: int, total_units: int) -> None:
        self._gpu_metrics = {
            "utilization": utilization,
            "free_units": free_units,
            "total_units": total_units,
            "updated_at": datetime.now().isoformat(),
        }

    def report_workers(self, idle: int, busy: int, total: int) -> None:
        self._worker_metrics = {
            "idle": idle,
            "busy": busy,
            "total": total,
            "updated_at": datetime.now().isoformat(),
        }

    def report_publishing(self, queued: int, published: int, failed: int) -> None:
        self._publishing_metrics = {
            "queued": queued,
            "published": published,
            "failed": failed,
            "updated_at": datetime.now().isoformat(),
        }

    def report_localization(self, completed_languages: int, total_languages: int) -> None:
        self._localization_metrics = {
            "completed_languages": completed_languages,
            "total_languages": total_languages,
            "updated_at": datetime.now().isoformat(),
        }

    def report_failures(self, critical: int, warning: int) -> None:
        self._failure_metrics = {
            "critical": critical,
            "warning": warning,
            "updated_at": datetime.now().isoformat(),
        }

    def report_render_time(self, average_minutes: float, longest_minutes: float) -> None:
        self._render_metrics = {
            "average_minutes": average_minutes,
            "longest_minutes": longest_minutes,
            "updated_at": datetime.now().isoformat(),
        }

    def report_episode(self, status: str, episode_id: str = "") -> None:
        self._episode_metrics = {
            "status": status,
            "episode_id": episode_id,
            "updated_at": datetime.now().isoformat(),
        }

    def report_revenue(self, total: float, growth_pct: float = 0.0) -> None:
        self._revenue_metrics = {"total": total, "growth_pct": growth_pct}

    def report_subscribers(self, count: int, growth_pct: float = 0.0) -> None:
        self._subscriber_metrics = {"count": count, "growth_pct": growth_pct}

    def report_channel_health(self, health: str) -> None:
        self._channel_metrics = {"health": health}

    def snapshot(self) -> dict:
        return {
            "production_queue": self._queue_metrics,
            "gpu_status": self._gpu_metrics,
            "worker_status": self._worker_metrics,
            "publishing_queue": self._publishing_metrics,
            "localization_status": self._localization_metrics,
            "failures": self._failure_metrics,
            "render_time": self._render_metrics,
            "episode_status": self._episode_metrics,
            "revenue": self._revenue_metrics,
            "subscriber_growth": self._subscriber_metrics,
            "channel_health": self._channel_metrics,
        }

    def from_orchestrator(self) -> dict:
        if self.orchestrator is None:
            return self.snapshot()
        resources = self.orchestrator.resource_manager.snapshot()
        workers = self.orchestrator.worker_pool.list_workers()
        self.report_gpu(
            resources.gpu_utilization,
            self.orchestrator.resource_manager.available_gpu(),
            self.orchestrator.resource_manager.total_gpu,
        )
        self.report_workers(
            sum(1 for w in workers if w.status == "idle"),
            sum(1 for w in workers if w.status == "busy"),
            len(workers),
        )
        return self.snapshot()
