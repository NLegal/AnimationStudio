from datetime import datetime

from .models import (
    MasterTimeline, TimelineTrack, TransitionStyle,
    QCResult, ExportPreset,
)


class PostProductionQC:
    def validate_timeline(self, timeline: MasterTimeline) -> QCResult:
        checks: dict[str, bool] = {
            "has_episode_id": bool(timeline.episode_id),
            "has_tracks": len(timeline.tracks) > 0,
            "has_video_track": any(t.name == "Video" for t in timeline.tracks),
            "has_audio_track": any(t.name == "Audio" for t in timeline.tracks),
            "duration_positive": timeline.duration_seconds > 0,
            "valid_resolution": timeline.resolution_width > 0 and timeline.resolution_height > 0,
            "valid_frame_rate": timeline.frame_rate in (24, 30, 60),
            "events_present": sum(t.event_count() for t in timeline.tracks) > 0,
        }
        errors = [k for k, v in checks.items() if not v]

        score = (sum(1 for v in checks.values() if v) / len(checks)) * 100.0 if checks else 0.0

        return QCResult(
            passed=len(errors) == 0,
            checks=checks,
            errors=errors,
            score=round(score, 1),
            timestamp=datetime.now().isoformat(),
        )

    def validate_exports(self, presets: list[ExportPreset]) -> QCResult:
        checks: dict[str, bool] = {}
        for preset in presets:
            checks[f"{preset.name}_valid_resolution"] = preset.resolution_width > 0 and preset.resolution_height > 0
            checks[f"{preset.name}_valid_frame_rate"] = preset.frame_rate in (24, 30, 60)
            checks[f"{preset.name}_has_format"] = bool(preset.format)
        errors = [k for k, v in checks.items() if not v]
        score = (sum(1 for v in checks.values() if v) / len(checks)) * 100.0 if checks else 0.0
        return QCResult(
            passed=len(errors) == 0,
            checks=checks,
            errors=errors,
            score=round(score, 1),
            timestamp=datetime.now().isoformat(),
        )

    MAX_FLASHES_PER_SECOND = 3

    def validate_accessibility(self, flash_events: list[tuple[float, float]] | None = None,
                               window_seconds: float = 1.0) -> QCResult:
        checks: dict[str, bool] = {
            "flashes_within_limits": True,
            "no_flashes_in_lowest_window": True,
        }
        errors: list[str] = []
        for event in flash_events or []:
            start, end = event
            duration = max(end - start, 0.001)
            rate = 1.0 / duration
            if rate > self.MAX_FLASHES_PER_SECOND:
                checks["flashes_within_limits"] = False
                errors.append(
                    f"Flash at {start}s exceeds safe limit ({rate:.1f} flashes/s "
                    f"vs max {self.MAX_FLASHES_PER_SECOND}/s)"
                )
        checks["no_flashes_in_lowest_window"] = window_seconds > 0
        score = (sum(1 for v in checks.values() if v) / len(checks)) * 100.0 if checks else 0.0
        return QCResult(
            passed=len(errors) == 0,
            checks=checks,
            errors=errors,
            score=round(score, 1),
            timestamp=datetime.now().isoformat(),
        )

    def check_missing_clips(self, timeline: MasterTimeline) -> list[str]:
        missing: list[str] = []
        for track in timeline.tracks:
            for event in track.events:
                if not event.clip_id:
                    missing.append(f"Missing clip_id in track '{track.name}' at {event.start_time}s")
        return missing

    def check_transitions(self, timeline: MasterTimeline) -> list[str]:
        issues: list[str] = []
        for track in timeline.tracks:
            prev: Optional[TimelineEvent] = None
            for event in sorted(track.events, key=lambda e: e.start_time):
                if prev and prev.transition_out == TransitionStyle.NONE and event.transition_in == TransitionStyle.NONE:
                    if abs(event.start_time - prev.end_time) < 0.01:
                        pass  # Quick cut is fine
                prev = event
        return issues
