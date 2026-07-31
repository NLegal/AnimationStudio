from datetime import datetime
from typing import Optional

from .models import (
    MasterTimeline, TimelineTrack, TimelineEvent,
    VideoTrackType, AudioTrackType, TransitionStyle,
)


class TimelineEngine:
    def create(self, episode_id: str, title: str = "") -> MasterTimeline:
        return MasterTimeline(
            episode_id=episode_id,
            title=title or episode_id,
            created_at=datetime.now().isoformat(),
        )

    def add_track(self, timeline: MasterTimeline, name: str, order: int = 0) -> TimelineTrack:
        track = TimelineTrack(name=name, order=order)
        timeline.tracks.append(track)
        return track

    def add_event(
        self,
        track: TimelineTrack,
        event_id: str,
        start_time: float = 0.0,
        end_time: float = 0.0,
        clip_id: str = "",
        video_track: VideoTrackType = VideoTrackType.ANIMATION,
        audio_track: AudioTrackType = AudioTrackType.DIALOGUE,
        transition_in: TransitionStyle = TransitionStyle.NONE,
        transition_out: TransitionStyle = TransitionStyle.NONE,
    ) -> TimelineEvent:
        event = TimelineEvent(
            event_id=event_id,
            start_time=start_time,
            end_time=end_time,
            duration=end_time - start_time,
            clip_id=clip_id,
            video_track=video_track,
            audio_track=audio_track,
            transition_in=transition_in,
            transition_out=transition_out,
        )
        track.events.append(event)
        return event

    def calculate_duration(self, timeline: MasterTimeline) -> float:
        if not timeline.tracks:
            timeline.duration_seconds = 0.0
            return 0.0
        duration = max(t.total_duration() for t in timeline.tracks)
        timeline.duration_seconds = duration
        return duration

    def find_gaps(self, track: TimelineTrack) -> list[tuple[float, float]]:
        if not track.events:
            return [(0.0, 0.0)]
        sorted_events = sorted(track.events, key=lambda e: e.start_time)
        gaps: list[tuple[float, float]] = []
        current_end = 0.0
        for event in sorted_events:
            if event.start_time > current_end + 0.01:
                gaps.append((current_end, event.start_time))
            current_end = max(current_end, event.end_time)
        return gaps

    def find_overlaps(self, track: TimelineTrack) -> list[tuple[str, str, float]]:
        sorted_events = sorted(track.events, key=lambda e: e.start_time)
        overlaps: list[tuple[str, str, float]] = []
        for i, a in enumerate(sorted_events):
            for b in sorted_events[i + 1:]:
                if b.start_time < a.end_time:
                    overlaps.append((a.event_id, b.event_id, b.start_time - a.end_time))
                else:
                    break
        return overlaps

    def timeline_to_dict(self, timeline: MasterTimeline) -> dict:
        return {
            "episode_id": timeline.episode_id,
            "title": timeline.title,
            "duration_seconds": timeline.duration_seconds,
            "frame_rate": timeline.frame_rate,
            "resolution": f"{timeline.resolution_width}x{timeline.resolution_height}",
            "tracks": [
                {
                    "name": t.name,
                    "events": [
                        {
                            "event_id": e.event_id,
                            "start": e.start_time,
                            "end": e.end_time,
                            "clip_id": e.clip_id,
                            "transition_in": e.transition_in.value,
                            "transition_out": e.transition_out.value,
                        }
                        for e in t.events
                    ],
                }
                for t in timeline.tracks
            ],
        }
