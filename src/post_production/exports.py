from typing import Optional

from .export_executor import ExportExecutor, ExportResult, get_export_executor
from .models import ExportPreset


EXPORT_PRESETS: dict[str, ExportPreset] = {
    "master_archive": ExportPreset(
        name="Master Archive",
        resolution_width=3840,
        resolution_height=2160,
        frame_rate=24,
        video_bitrate="50 Mbps",
        audio_bitrate="320 kbps",
        format="mp4",
        description="Highest quality master for archival and future reprocessing",
    ),
    "youtube": ExportPreset(
        name="YouTube",
        resolution_width=1920,
        resolution_height=1080,
        frame_rate=24,
        video_bitrate="16 Mbps",
        audio_bitrate="192 kbps",
        format="mp4",
        description="Standard YouTube upload format",
    ),
    "shorts": ExportPreset(
        name="YouTube Shorts",
        resolution_width=1080,
        resolution_height=1920,
        frame_rate=24,
        video_bitrate="12 Mbps",
        audio_bitrate="192 kbps",
        format="mp4",
        description="Vertical 9:16 format for YouTube Shorts",
    ),
    "tiktok": ExportPreset(
        name="TikTok",
        resolution_width=1080,
        resolution_height=1920,
        frame_rate=30,
        video_bitrate="10 Mbps",
        audio_bitrate="192 kbps",
        format="mp4",
        description="Vertical 9:16 format for TikTok",
    ),
    "instagram_reels": ExportPreset(
        name="Instagram Reels",
        resolution_width=1080,
        resolution_height=1920,
        frame_rate=30,
        video_bitrate="10 Mbps",
        audio_bitrate="192 kbps",
        format="mp4",
        description="Vertical 9:16 format for Instagram Reels",
    ),
    "facebook": ExportPreset(
        name="Facebook Video",
        resolution_width=1920,
        resolution_height=1080,
        frame_rate=24,
        video_bitrate="12 Mbps",
        audio_bitrate="192 kbps",
        format="mp4",
        description="Standard Facebook upload format",
    ),
    "website": ExportPreset(
        name="Website",
        resolution_width=1280,
        resolution_height=720,
        frame_rate=24,
        video_bitrate="5 Mbps",
        audio_bitrate="128 kbps",
        format="mp4",
        description="Web-optimized preview quality",
    ),
    "educational_platform": ExportPreset(
        name="Educational Platform",
        resolution_width=1920,
        resolution_height=1080,
        frame_rate=24,
        video_bitrate="8 Mbps",
        audio_bitrate="128 kbps",
        format="mp4",
        description="Standard format for educational distribution platforms",
    ),
}


class ExportEngine:
    def list_presets(self) -> dict[str, ExportPreset]:
        return dict(EXPORT_PRESETS)

    def get_preset(self, name: str) -> ExportPreset:
        return EXPORT_PRESETS.get(name, EXPORT_PRESETS["youtube"])

    def add_preset(self, name: str, preset: ExportPreset) -> None:
        EXPORT_PRESETS[name] = preset

    def export(
        self,
        clips: list[str],
        preset: "str | ExportPreset" = "youtube",
        *,
        output_path: Optional[str] = None,
        audio: Optional[list[str]] = None,
        images: Optional[list[str]] = None,
        seconds_per_frame: float = 2.0,
        executor: Optional[ExportExecutor] = None,
    ) -> ExportResult:
        """Render clips or stills into one real output file.

        ``preset`` may be a registered preset name or an ``ExportPreset``.
        ``clips`` are video fragments (ffmpeg concat); ``images`` are still
        frames assembled into an MP4 image-sequence with
        ``seconds_per_frame`` of hold time each (pass ``clips=[]``).
        ``executor`` selects the producer explicitly (real ffmpeg or the
        offline concat fallback); otherwise ``get_export_executor``
        resolves ``FFMPEG_EXECUTOR`` (default ``auto`` → ffmpeg when
        installed, else byte-copy fallback). Returns an ``ExportResult``
        for the written file.
        """
        if isinstance(preset, str):
            preset = self.get_preset(preset)
        if executor is None:
            executor = get_export_executor()
        return executor.export(clips, preset,
                               output_path=output_path, audio=audio,
                               images=images, seconds_per_frame=seconds_per_frame)
