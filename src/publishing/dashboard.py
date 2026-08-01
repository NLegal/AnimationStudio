"""Publishing operational dashboard.

Aggregates upcoming releases, publishing queue, localization status,
copyright alerts, analytics overview, trending episodes, failed uploads,
performance reports, revenue summary, and automation status for complete
operational visibility.
"""

from __future__ import annotations


class PublishingDashboard:
    def __init__(self):
        self._upcoming: list[dict] = []
        self._queue: list[dict] = []
        self._localization: list[dict] = []
        self._copyright_alerts: list[dict] = []
        self._analytics: list[dict] = []
        self._failed_uploads: list[dict] = []

    def set_upcoming_releases(self, releases: list[dict]) -> None:
        self._upcoming = list(releases)

    def set_publishing_queue(self, queue: list[dict]) -> None:
        self._queue = list(queue)

    def set_localization_status(self, statuses: list[dict]) -> None:
        self._localization = list(statuses)

    def add_copyright_alert(self, alert: dict) -> None:
        self._copyright_alerts.append(alert)

    def add_failed_upload(self, record: dict) -> None:
        self._failed_uploads.append(record)

    def set_analytics_overview(self, overview: dict) -> None:
        self._analytics = [overview]

    def overview(self) -> dict:
        return {
            "upcoming_releases": list(self._upcoming),
            "publishing_queue": list(self._queue),
            "localization_status": list(self._localization),
            "copyright_alerts": list(self._copyright_alerts),
            "analytics_overview": list(self._analytics),
            "trending_episodes": self.trending_episodes(),
            "failed_uploads": list(self._failed_uploads),
            "performance_reports": self.performance_reports(),
            "revenue_summary": self.revenue_summary(),
            "automation_status": self.automation_status(),
        }

    def trending_episodes(self, limit: int = 5) -> list[dict]:
        episodes: list[dict] = []
        for overview in self._analytics:
            for episode in overview.get("episodes", []):
                episodes.append(episode)
        episodes.sort(key=lambda e: e.get("views", 0), reverse=True)
        return episodes[:limit]

    def performance_reports(self) -> list[dict]:
        reports: list[dict] = []
        for overview in self._analytics:
            if "reports" in overview:
                reports.extend(overview["reports"])
        return reports

    def revenue_summary(self) -> float:
        total = 0.0
        for overview in self._analytics:
            total += overview.get("revenue", 0.0)
        return round(total, 2)

    def automation_status(self) -> dict:
        return {
            "queue_count": len(self._queue),
            "failed_uploads": len(self._failed_uploads),
            "copyright_alerts": len(self._copyright_alerts),
            "localization_languages": len({s.get("language") for s in self._localization}),
        }
