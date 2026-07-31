from typing import Optional

from .models import (
    MasterTimeline, TimelineEvent, SceneAssembly,
    ClipReference, VideoTrackType, AudioTrackType,
    TransitionStyle,
)
from .timeline import TimelineEngine


class PacingEngine:
    MIN_SHOT_DURATION = 1.5
    MAX_SHOT_DURATION = 12.0
    QUESTION_PAUSE = 2.0
    COUNTING_PAUSE = 0.8
    SONG_REPEAT_PAUSE = 1.5

    def suggest_shot_duration(self, content_type: str, age_range: str = "2-5") -> float:
        durations = {
            "dialogue": 4.0,
            "narration": 5.0,
            "song": 6.0,
            "learning": 5.0,
            "counting": 3.0,
            "question": 4.5,
            "transition": 2.0,
            "action": 3.0,
            "celebration": 4.0,
            "intro": 6.0,
            "outro": 8.0,
        }
        return max(self.MIN_SHOT_DURATION, durations.get(content_type, 4.0))

    def educational_pause(self, activity: str) -> float:
        pauses = {
            "count": self.COUNTING_PAUSE,
            "question": self.QUESTION_PAUSE,
            "song_repeat": self.SONG_REPEAT_PAUSE,
            "color_recognition": 2.5,
            "shape_recognition": 2.5,
            "letter_recognition": 2.0,
            "number_recognition": 2.0,
        }
        return pauses.get(activity, 1.0)

    def estimate_scene_duration(self, scene_type: str) -> float:
        estimates = {
            "opening": 8.0,
            "introduction": 15.0,
            "learning": 30.0,
            "song": 45.0,
            "practice": 25.0,
            "review": 20.0,
            "celebration": 15.0,
            "outro": 15.0,
        }
        return estimates.get(scene_type, 20.0)

    def total_episode_estimate(self, has_song: bool = True, scene_count: int = 8) -> float:
        total = 0.0
        total += self.estimate_scene_duration("opening")
        total += self.estimate_scene_duration("introduction")
        total += self.estimate_scene_duration("learning")
        if has_song:
            total += self.estimate_scene_duration("song")
        total += self.estimate_scene_duration("practice")
        total += self.estimate_scene_duration("review")
        total += self.estimate_scene_duration("celebration")
        total += self.estimate_scene_duration("outro")
        return total


class EditingEngine:
    def __init__(self):
        self.pacing = PacingEngine()
        self.timeline_engine = TimelineEngine()

    def assemble_scenes(
        self,
        episode_id: str,
        assembly: SceneAssembly,
        title: str = "",
    ) -> MasterTimeline:
        timeline = self.timeline_engine.create(episode_id, title)
        video_track = self.timeline_engine.add_track(timeline, "Video", 0)
        audio_track = self.timeline_engine.add_track(timeline, "Audio", 1)
        subtitle_track = self.timeline_engine.add_track(timeline, "Subtitles", 2)

        current_time = 0.0
        scene_order = [
            ("opening", assembly.opening, TransitionStyle.FADE),
            ("introduction", assembly.introduction, TransitionStyle.CROSSFADE),
            ("learning", assembly.learning, TransitionStyle.SLIDE),
            ("song", assembly.song, TransitionStyle.CROSSFADE),
            ("practice", assembly.practice, TransitionStyle.SLIDE),
            ("review", assembly.review, TransitionStyle.CROSSFADE),
            ("celebration", assembly.celebration, TransitionStyle.ZOOM),
            ("outro", assembly.outro, TransitionStyle.FADE),
        ]

        for scene_name, clips, transition in scene_order:
            if not clips:
                continue
            for clip in clips:
                end_time = current_time + clip.duration
                self.timeline_engine.add_event(
                    video_track,
                    event_id=clip.clip_id,
                    start_time=current_time,
                    end_time=end_time,
                    clip_id=clip.clip_id,
                    video_track=VideoTrackType.ANIMATION,
                    audio_track=AudioTrackType.DIALOGUE,
                    transition_in=transition,
                    transition_out=TransitionStyle.NONE,
                )
                current_time = end_time

        self.timeline_engine.calculate_duration(timeline)
        return timeline

    def insert_pause(self, video_track, audio_track, at_time: float, duration: float) -> None:
        pass
