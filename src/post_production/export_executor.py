from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from typing import Optional, Protocol, runtime_checkable

from .models import ExportPreset, ExportResult


class ExportError(Exception):
    """Base error for the export stage."""


class ExportValidationError(ExportError):
    """Input clips or audio stems are missing or unusable."""


class FfmpegNotFound(ExportError):
    """The ffmpeg binary is required but unavailable."""


def _slug(name: str) -> str:
    slug = "".join(c if c.isalnum() else "_" for c in name.lower()).strip("_")
    return slug or "export"


def _default_output_path(clips: list[str], preset: ExportPreset) -> str:
    first = clips[0]
    stem = os.path.splitext(os.path.basename(first))[0] or "export"
    return os.path.join(os.path.dirname(first) or ".",
                        f"{stem}_{_slug(preset.name)}.{preset.format}")


def _validated_clips(clips) -> list[str]:
    if not clips:
        raise ExportValidationError("no clip paths provided")
    missing = [c for c in clips if not c or not os.path.isfile(c)]
    if missing:
        raise ExportValidationError(f"missing clip file(s): {missing}")
    return list(clips)


def _bitrate_flag(rate: str) -> str:
    parts = rate.strip().lower().split()
    if not parts:
        return "auto"
    value = parts[0]
    if len(parts) > 1:
        unit = parts[1]
        if unit.startswith("mb"):
            value += "M"
        elif unit.startswith("kb"):
            value += "k"
    return value


def _probe_duration_seconds(path: str) -> Optional[float]:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    try:
        result = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True, timeout=30,
        )
        return float(result.stdout.strip())
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


@runtime_checkable
class ExportExecutor(Protocol):
    """Renders a list of clip files into one real file on disk."""

    def export(
        self,
        clips: list[str],
        preset: ExportPreset,
        *,
        output_path: Optional[str] = None,
        audio: Optional[list[str]] = None,
    ) -> ExportResult: ...


class FfmpegExportExecutor:
    """Real ffmpeg executor — the byte-producing consumer path.

    Concatenates the input clips (re-encoding to the preset's resolution,
    frame rate and bitrates), muxes any audio stems, and writes an MP4.
    Requires an ``ffmpeg`` binary on PATH or an explicit ``ffmpeg_bin``.
    """

    def __init__(self, ffmpeg_bin: Optional[str] = None):
        self._ffmpeg_bin = ffmpeg_bin or shutil.which("ffmpeg")

    def is_configured(self) -> bool:
        return bool(self._ffmpeg_bin)

    def export(
        self,
        clips: list[str],
        preset: ExportPreset,
        *,
        output_path: Optional[str] = None,
        audio: Optional[list[str]] = None,
    ) -> ExportResult:
        if not self._ffmpeg_bin:
            raise FfmpegNotFound(
                "ffmpeg is not installed; install ffmpeg or use the "
                "ConcatExportExecutor fallback (FFMPEG_EXECUTOR=mock)."
            )
        inputs = _validated_clips(clips)
        stems = list(audio or [])
        missing_audio = [a for a in stems if not a or not os.path.isfile(a)]
        if missing_audio:
            raise ExportValidationError(f"missing audio stem(s): {missing_audio}")
        out = os.path.abspath(output_path or _default_output_path(inputs, preset))
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

        list_path = None
        try:
            fd, list_path = tempfile.mkstemp(suffix=".txt", text=True)
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                for clip in inputs:
                    path = clip.replace("\\", "/").replace("'", "'\\''")
                    fh.write(f"file '{path}'\n")

            cmd = [self._ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error",
                   "-f", "concat", "-safe", "0", "-i", list_path]
            for stem in stems:
                cmd += ["-i", stem]

            cmd += ["-map", "0:v?"]
            if stems and len(stems) == 1:
                cmd += ["-map", "1:a"]
            elif len(stems) > 1:
                mix = "".join(f"[{idx + 1}:a]" for idx in range(len(stems)))
                cmd += ["-filter_complex", f"{mix}amix=inputs={len(stems)}:duration=longest[aout]",
                        "-map", "[aout]"]
            else:
                cmd += ["-map", "0:a?"]

            cmd += [
                "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                "-pix_fmt", "yuv420p", "-r", str(preset.frame_rate),
                "-s", f"{preset.resolution_width}x{preset.resolution_height}",
                "-c:a", "aac", "-b:a", _bitrate_flag(preset.audio_bitrate),
                "-b:v", _bitrate_flag(preset.video_bitrate),
                "-movflags", "+faststart",
                out,
            ]
            subprocess.run(cmd, capture_output=True, text=True,
                           timeout=600, check=True)
        except subprocess.CalledProcessError as exc:
            detail = (exc.stderr or "").strip().splitlines()[-3:]
            raise ExportError(f"ffmpeg export failed (rc={exc.returncode}): "
                              f"{'; '.join(detail)}") from exc
        except FileNotFoundError as exc:
            raise FfmpegNotFound(
                f"ffmpeg binary not found at {self._ffmpeg_bin!r}") from exc
        finally:
            if list_path and os.path.exists(list_path):
                os.unlink(list_path)

        duration = _probe_duration_seconds(out) or 0.0
        return ExportResult(
            output_path=out,
            preset_name=preset.name,
            format=preset.format,
            clip_count=len(inputs),
            size_bytes=os.path.getsize(out),
            duration_s=round(duration, 3),
            video_frames=int(round(duration * preset.frame_rate)),
            executor="ffmpeg",
            ffmpeg_used=True,
            created_at=datetime.now().isoformat(),
        )


class ConcatExportExecutor:
    """Offline fallback that still writes a real file.

    Byte-copies the input clips verbatim into one output (no transcoding,
    so an ``ffmpeg`` binary is not required). Audio stems are not muxable
    in a pure byte copy and are ignored.
    """

    def is_configured(self) -> bool:
        return True

    def export(
        self,
        clips: list[str],
        preset: ExportPreset,
        *,
        output_path: Optional[str] = None,
        audio: Optional[list[str]] = None,
    ) -> ExportResult:
        inputs = _validated_clips(clips)
        out = os.path.abspath(output_path or _default_output_path(inputs, preset))
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        with open(out, "wb") as dst:
            for clip in inputs:
                with open(clip, "rb") as src:
                    shutil.copyfileobj(src, dst, length=1024 * 1024)
        duration = _probe_duration_seconds(out) or 0.0
        return ExportResult(
            output_path=out,
            preset_name=preset.name,
            format=preset.format,
            clip_count=len(inputs),
            size_bytes=os.path.getsize(out),
            duration_s=round(duration, 3),
            video_frames=int(round(duration * preset.frame_rate)),
            executor="concat",
            ffmpeg_used=False,
            created_at=datetime.now().isoformat(),
        )


def get_export_executor(backend: Optional[str] = None) -> ExportExecutor:
    """Resolve the export producer.

    An explicit ``backend`` wins; otherwise the ``FFMPEG_EXECUTOR``
    environment variable (``auto`` | ``ffmpeg`` | ``mock``). ``auto``
    selects ffmpeg when installed, else the offline concat fallback.
    """
    mode = backend or os.environ.get("FFMPEG_EXECUTOR", "auto") or "auto"
    if mode == "ffmpeg":
        return FfmpegExportExecutor()
    if mode == "mock":
        return ConcatExportExecutor()
    if mode == "auto":
        executor = FfmpegExportExecutor()
        if executor.is_configured():
            return executor
        return ConcatExportExecutor()
    raise ExportError(f"unknown FFMPEG_EXECUTOR mode: {mode!r}")