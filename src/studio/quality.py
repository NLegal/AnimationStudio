from __future__ import annotations
from datetime import datetime

from .models import QualityReport, TaskStatus, Task


class QualityGate:
    DOMAIN_CHECKERS = {
        "story": ["structure", "learning_objective", "age_appropriate_language"],
        "image": ["resolution", "clarity", "character_consistency"],
        "animation": ["smoothness", "frame_rate", "render_consistency"],
        "audio": ["clarity", "volume_level", "no_noise"],
        "video": ["resolution", "duration", "bitrate"],
        "metadata": ["title", "description", "keywords"],
        "publishing": ["thumbnail", "visibility", "schedule"],
        "localization": ["translations", "subtitles", "audio_track"],
        "branding": ["logo", "colors", "social_links"],
        "accessibility": ["captions", "audio_description", "color_contrast"],
    }

    def __init__(self):
        self._reports: dict[str, QualityReport] = {}
        self._checkers: dict[str, str] = {}

    def register_checker(self, check_name: str, description: str = "") -> None:
        self._checkers[check_name] = description

    def register_domain_checkers(self, domain: str) -> None:
        for check_name in self.DOMAIN_CHECKERS.get(domain, []):
            self.register_checker(f"{domain}:{check_name}")

    def register_all_domain_checkers(self) -> None:
        for domain in self.DOMAIN_CHECKERS:
            self.register_domain_checkers(domain)

    def domains(self) -> list[str]:
        return list(self.DOMAIN_CHECKERS.keys())

    def checkers(self) -> list[str]:
        return list(self._checkers.keys())

    def evaluate(
        self,
        subject_id: str,
        subject_type: str,
        results: dict[str, bool],
        minimum_score: float = 0.8,
    ) -> QualityReport:
        errors = [k for k, v in results.items() if not v]
        passed = len(errors) == 0
        score = round(sum(1 for v in results.values() if v) / max(len(results), 1), 2)
        report = QualityReport(
            subject_id=subject_id,
            subject_type=subject_type,
            passed=passed and score >= minimum_score,
            checks=results,
            errors=errors,
            score=score,
            timestamp=datetime.now().isoformat(),
        )
        self._reports[subject_id] = report
        return report

    def report_for(self, subject_id: str) -> QualityReport:
        return self._reports.get(subject_id, QualityReport(subject_id=subject_id))

    def gate_task(self, task: Task, results: dict[str, bool], minimum_score: float = 0.8) -> bool:
        report = self.evaluate(task.task_id, task.task_type, results, minimum_score)
        if report.passed:
            task.status = TaskStatus.VALIDATED
        return report.passed

    def last_report(self) -> QualityReport:
        if not self._reports:
            return QualityReport()
        return list(self._reports.values())[-1]

    def reports(self) -> list[QualityReport]:
        return list(self._reports.values())

    def passing_rate(self) -> float:
        if not self._reports:
            return 1.0
        passed = sum(1 for r in self._reports.values() if r.passed)
        return round(passed / len(self._reports), 4)
