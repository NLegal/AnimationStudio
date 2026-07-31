from datetime import datetime

from .models import ArchiveRecord, QCResult


class ArchiveEngine:
    def create_record(
        self,
        project_id: str,
        master_video: str = "",
        source_clips: list[str] | None = None,
        audio_stems: list[str] | None = None,
        subtitles: list[str] | None = None,
        thumbnails: list[str] | None = None,
        qc_report: str = "",
    ) -> ArchiveRecord:
        return ArchiveRecord(
            project_id=project_id,
            master_video=master_video,
            source_clips=source_clips or [],
            audio_stems=audio_stems or [],
            subtitles=subtitles or [],
            thumbnails=thumbnails or [],
            qc_report=qc_report,
            archived_at=datetime.now().isoformat(),
        )

    def generate_metadata(
        self,
        episode_id: str,
        title: str,
        description: str = "",
        keywords: list[str] | None = None,
        learning_objective: str = "",
        characters: list[str] | None = None,
        duration: float = 0.0,
        language: str = "en",
        version: int = 1,
    ) -> dict:
        return {
            "episode_id": episode_id,
            "title": title,
            "description": description,
            "keywords": keywords or [],
            "learning_objective": learning_objective,
            "characters": characters or [],
            "duration_seconds": duration,
            "language": language,
            "version": version,
            "generated_at": datetime.now().isoformat(),
        }

    def reproducibility_checklist(self, record: ArchiveRecord) -> dict[str, bool]:
        return {
            "has_project_id": bool(record.project_id),
            "has_master_video": bool(record.master_video),
            "has_source_clips": len(record.source_clips) > 0,
            "has_audio_stems": len(record.audio_stems) > 0,
            "has_subtitles": len(record.subtitles) > 0,
            "has_thumbnails": len(record.thumbnails) > 0,
            "has_qc_report": bool(record.qc_report),
            "has_archive_date": bool(record.archived_at),
        }
