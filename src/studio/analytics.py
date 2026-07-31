from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AnalyticsReport:
    report_id: str = ""
    metric: str = ""
    period: str = ""
    value: float = 0.0
    breakdown: dict = field(default_factory=dict)
    generated_at: str = ""


class StudioAnalytics:
    def __init__(self):
        self._reports: dict[str, AnalyticsReport] = {}
        self._samples: dict[str, list[float]] = {}
        self._counter = 0

    def sample(self, metric: str, value: float) -> None:
        if metric not in self._samples:
            self._samples[metric] = []
        self._samples[metric].append(value)

    def average(self, metric: str) -> float:
        values = self._samples.get(metric, [])
        if not values:
            return 0.0
        return round(sum(values) / len(values), 4)

    def latest(self, metric: str) -> float:
        values = self._samples.get(metric, [])
        return values[-1] if values else 0.0

    def generate_report(self, metric: str, period: str = "week") -> AnalyticsReport:
        self._counter += 1
        report = AnalyticsReport(
            report_id=f"REPORT_{self._counter}",
            metric=metric,
            period=period,
            value=self.average(metric),
            generated_at=datetime.now().isoformat(),
        )
        self._reports[report.report_id] = report
        return report

    def report(self, report_id: str) -> AnalyticsReport:
        return self._reports.get(report_id, AnalyticsReport())

    def all_reports(self) -> list[AnalyticsReport]:
        return list(self._reports.values())

    def metrics(self) -> list[str]:
        return list(self._samples.keys())

    def trend(self, metric: str) -> list[float]:
        return list(self._samples.get(metric, []))

    def count(self) -> int:
        return len(self._reports)


class AIPerformanceTracker:
    def __init__(self):
        self._timings: list[float] = []
        self._costs: list[float] = []
        self._counts: dict[str, int] = {}

    def record_run(self, step_type: str, duration_seconds: float, cost: float = 0.0) -> None:
        self._timings.append(duration_seconds)
        self._costs.append(cost)
        self._counts[step_type] = self._counts.get(step_type, 0) + 1

    def average_duration(self) -> float:
        if not self._timings:
            return 0.0
        return round(sum(self._timings) / len(self._timings), 4)

    def average_cost(self) -> float:
        if not self._costs:
            return 0.0
        return round(sum(self._costs) / len(self._costs), 4)

    def runs_for(self, step_type: str) -> int:
        return self._counts.get(step_type, 0)

    def total_runs(self) -> int:
        return sum(self._counts.values())

    def total_cost(self) -> float:
        return round(sum(self._costs), 4)
