from .models import AudioTrackType


AUDIO_PRIORITY: list[AudioTrackType] = [
    AudioTrackType.DIALOGUE,
    AudioTrackType.NARRATION,
    AudioTrackType.SINGING,
    AudioTrackType.LEARNING_SOUNDS,
    AudioTrackType.SOUND_EFFECTS,
    AudioTrackType.MUSIC,
    AudioTrackType.AMBIENCE,
]


class AudioSyncEngine:
    def mix_levels(self, track_types: list[AudioTrackType]) -> dict[str, float]:
        base_levels: dict[AudioTrackType, float] = {
            AudioTrackType.DIALOGUE: 0.0,
            AudioTrackType.NARRATION: -3.0,
            AudioTrackType.SINGING: -3.0,
            AudioTrackType.LEARNING_SOUNDS: -6.0,
            AudioTrackType.SOUND_EFFECTS: -8.0,
            AudioTrackType.MUSIC: -12.0,
            AudioTrackType.AMBIENCE: -18.0,
        }
        return {
            t.value: base_levels.get(t, -12.0)
            for t in track_types
        }

    def estimate_dialogue_duration(self, text: str, words_per_minute: float = 150) -> float:
        word_count = len(text.split())
        if word_count == 0:
            return 0.0
        return (word_count / words_per_minute) * 60

    def check_sync(self, clip_duration: float, audio_duration: float, tolerance: float = 0.1) -> dict:
        diff = abs(clip_duration - audio_duration)
        return {
            "in_sync": diff <= tolerance,
            "difference": round(diff, 3),
            "tolerance": tolerance,
            "clip_duration": clip_duration,
            "audio_duration": audio_duration,
        }

    def suggest_music_fade(self, scene_duration: float) -> dict:
        if scene_duration <= 5:
            return {"fade_in": 0.3, "fade_out": 0.3}
        return {"fade_in": min(2.0, scene_duration * 0.1), "fade_out": min(2.0, scene_duration * 0.1)}
