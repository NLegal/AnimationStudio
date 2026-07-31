from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime

from .models import StudioMetrics, TaskStatus


@dataclass
class Alert:
    alert_id: str = ""
    severity: str = "info"
    message: str = ""
    subject: str = ""
    timestamp: str = ""
    ack: bool = False


@dataclass
class MetricSample:
    name: str = ""
    value: float = 0.0
    unit: str = ""
    timestamp: str = ""


class MetricsCollector:
    def __init__(self):
        self._samples: list[MetricSample] = []
        self._counter = 0

    def record(self, name: str, value: float, unit: str = "") -> MetricSample:
        sample = MetricSample(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now().isoformat(),
        )
        self._samples.append(sample)
        return sample

    def series(self, name: str) -> list[MetricSample]:
        return [s for s in self._samples if s.name == name]

    def latest(self, name: str) -> MetricSample | None:
        series = self.series(name)
        return series[-1] if series else None

    def names(self) -> list[str]:
        return list({s.name for s in self._samples})

    def count(self) -> int:
        return len(self._samples)


class StudioMonitor:
    def __init__(self):
        self._alerts: list[Alert] = []
        self._counter = 0

    def snapshot(self, collector: MetricsCollector) -> dict[str, float]:
        latest = {
            name: (collector.latest(name).value if collector.latest(name) else 0.0)
            for name in collector.names()
        }
        return latest

    def raise_alert(self, message: str, subject: str = "", severity: str = "info") -> Alert:
        self._counter += 1
        alert = Alert(
            alert_id=f"ALERT_{self._counter}",
            severity=severity,
            message=message,
            subject=subject,
            timestamp=datetime.now().isoformat(),
        )
        self._alerts.append(alert)
        return alert

    def acknowledge(self, alert_id: str) -> bool:
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.ack = True
                return True
        return False

    def open_alerts(self) -> list[Alert]:
        return [a for a in self._alerts if not a.ack]

    def alerts_by_severity(self, severity: str) -> list[Alert]:
        return [a for a in self._alerts if a.severity == severity]

    def all_alerts(self) -> list[Alert]:
        return list(self._alerts)

    def critical_alerts(self) -> list[Alert]:
        return self.alerts_by_severity("critical")


class ProductionTracker:
    def __init__(self):
        self._counts: dict[str, int] = {}
        self._rates: dict[str, float] = {}

    def track(self, pipeline: str, outcome: TaskStatus) -> None:
        key = f"{pipeline}:{outcome.value}"
        self._counts[key] = self._counts.get(key, 0) + 1

    def count(self, pipeline: str, outcome: TaskStatus) -> int:
        return self._counts.get(f"{pipeline}:{outcome.value}", 0)

    def rate(self, pipeline: str, outcomes: list[TaskStatus]) -> float:
        total = sum(self.count(pipeline, o) for o in outcomes)
        completed = self.count(pipeline, TaskStatus.COMPLETED) + self.count(pipeline, TaskStatus.VALIDATED)
        if total == 0:
            return 1.0
        return round(completed / total, 4)

    def build_metrics(self) -> StudioMetrics:
        metrics = StudioMetrics(recorded_at=datetime.now().isoformat())
        metrics.episodes_produced = self.count("episode", TaskStatus.COMPLETED)
        metrics.automation_success_rate = self.rate("episode", [TaskStatus.COMPLETED, TaskStatus.FAILED])
        return metrics

    def reset(self) -> None:
        self._counts = {}
        self._rates = {}
