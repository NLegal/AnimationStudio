"""Post-Production Analytics.

Implements Phase 10 analytics metadata: duration breakdown by section,
question count, subtitle count, render time, export size, compression
ratio, and QC score for the master video.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class AnalyticsReport:
    episode_id: str = ""
    duration_breakdown: dict = field(default_factory=dict)
    question_count: int = 0
    subtitle_count: int = 0
    render_time_seconds: float = 0.0
    export_size_mb: float = 0.0
    compression_ratio: float = 0.0
    qc_score: float = 0.0
    timestamp: str = ""

    def as_dict(self) -> dict:
        return {
            "episode_id": self.episode_id,
            "duration_breakdown": self.duration_breakdown,
            "question_count": self.question_count,
            "subtitle_count": self.subtitle_count,
            "render_time_seconds": self.render_time_seconds,
            "export_size_mb": self.export_size_mb,
            "compression_ratio": self.compression_ratio,
            "qc_score": self.qc_score,
            "timestamp": self.timestamp,
        }


class PostProductionAnalytics:
    def build_report(self, episode_id: str = "", **kwargs) -> AnalyticsReport:
        return AnalyticsReport(
            episode_id=episode_id,
            duration_breakdown=kwargs.get("duration_breakdown", {}),
            question_count=kwargs.get("question_count", 0),
            subtitle_count=kwargs.get("subtitle_count", 0),
            render_time_seconds=kwargs.get("render_time_seconds", 0.0),
            export_size_mb=kwargs.get("export_size_mb", 0.0),
            compression_ratio=kwargs.get("compression_ratio", 0.0),
            qc_score=kwargs.get("qc_score", 0.0),
            timestamp=kwargs.get("timestamp", ""),
        )

    def compression_ratio(self, source_size_mb: float, export_size_mb: float) -> float:
        if source_size_mb <= 0:
            return 0.0
        return round(source_size_mb / export_size_mb, 3) if export_size_mb > 0 else 0.0

    def duration_breakdown(self, sections: dict[str, float]) -> dict:
        total = sum(sections.values()) or 1.0
        return {
            section: {
                "seconds": seconds,
                "percent": round((seconds / total) * 100.0, 1),
            }
            for section, seconds in sections.items()
        }
