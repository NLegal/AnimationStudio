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
