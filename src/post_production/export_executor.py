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
    """Input clips, images or audio stems are missing or unusable."""


class FfmpegNotFound(ExportError):
    """The ffmpeg binary is required but unavailable."""


def _slug(name: str) -> str:
    slug = "".join(c if c.isalnum() else "_" for c in name.lower()).strip("_")
    return slug or "export"


def _default_output_path(first_path: str, preset: ExportPreset) -> str:
    stem = os.path.splitext(os.path.basename(first_path))[0] or "export"
    return os.path.join(os.path.dirname(first_path) or ".",
                        f"{stem}_{_slug(preset.name)}.{preset.format}")


def _validated_clips(clips) -> list[str]:
    if not clips:
        raise ExportValidationError("no clip paths provided")
    missing = [c for c in clips if not c or not os.path.isfile(c)]
    if missing:
        raise ExportValidationError(f"missing clip file(s): {missing}")
    return list(clips)


def _validated_images(images) -> list[str]:
    if not images:
        raise ExportValidationError(
            "no image paths provided for image-sequence export")
    missing = [p for p in images if not p or not os.path.isfile(p)]
    if missing:
        raise ExportValidationError(f"missing image file(s): {missing}")
    return list(images)


def _validated_audio(audio) -> list[str]:
    stems = list(audio or [])
    missing = [a for a in stems if not a or not os.path.isfile(a)]
    if missing:
        raise ExportValidationError(f"missing audio stem(s): {missing}")
    return stems


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
    """Renders clips or stills into one real file on disk.

    ``clips`` = video fragments (ffmpeg concat); ``images`` = still frames
    assembled into an MP4 image-sequence slideshow.
    """

    def export(
        self,
        clips: list[str],
        preset: ExportPreset,
        *,
        output_path: Optional[str] = None,
        audio: Optional[list[str]] = None,
        images: Optional[list[str]] = None,
        seconds_per_frame: float = 2.0,
    ) -> ExportResult: ...


def _encode_flags(preset: ExportPreset) -> list[str]:
    return [
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(preset.frame_rate),
        "-s", f"{preset.resolution_width}x{preset.resolution_height}",
        "-c:a", "aac", "-b:a", _bitrate_flag(preset.audio_bitrate),
        "-b:v", _bitrate_flag(preset.video_bitrate),
        "-movflags", "+faststart",
    ]


class FfmpegExportExecutor:
    """Real ffmpeg executor — the byte-producing consumer path.

    Concatenates input clips or assembles an image sequence, re-encodes to
    the preset's resolution, frame rate and bitrates, muxes any audio
    stems, and writes an MP4. Requires an ``ffmpeg`` binary on PATH or an
    explicit ``ffmpeg_bin``.
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
        images: Optional[list[str]] = None,
        seconds_per_frame: float = 2.0,
    ) -> ExportResult:
        if not self._ffmpeg_bin:
            raise FfmpegNotFound(
                "ffmpeg is not installed; install ffmpeg or use the "
                "ConcatExportExecutor fallback (FFMPEG_EXECUTOR=mock)."
            )
        if images and clips:
            raise ExportValidationError("give either clips or images, not both")
        stems = _validated_audio(audio)
        if images:
            return self._export_images(
                images, preset, output_path, stems, seconds_per_frame)
        return self._export_clips(_validated_clips(clips),
                                  preset, output_path, stems)

    def _export_clips(self, inputs, preset, output_path, stems) -> ExportResult:
        out = os.path.abspath(output_path or _default_output_path(inputs[0], preset))
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
                cmd += ["-filter_complex",
                        f"{mix}amix=inputs={len(stems)}:duration=longest[aout]",
                        "-map", "[aout]"]
            else:
                cmd += ["-map", "0:a?"]
            cmd += _encode_flags(preset) + [out]
            self._run_ffmpeg(cmd, list_path=list_path)
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

    def _export_images(self, images, preset, output_path, stems,
                       seconds_per_frame) -> ExportResult:
        if not 0.1 <= seconds_per_frame <= 60.0:
            raise ExportValidationError(
                f"seconds_per_frame out of range: {seconds_per_frame}")
        frames = _validated_images(images)
        out = os.path.abspath(output_path or _default_output_path(frames[0], preset))
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        n = len(frames)
        width, height, fps = (preset.resolution_width,
                              preset.resolution_height, preset.frame_rate)
        graph_parts, concat_in = [], []
        for i in range(n):
            graph_parts.append(
                f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,fps={fps},format=yuv420p[v{i}]"
            )
            concat_in.append(f"[v{i}]")
        graph = ";".join(graph_parts) + f";{''.join(concat_in)}concat=n={n}:v=1:a=0[vout]"
        audio_label = ""
        if stems and len(stems) == 1:
            audio_label = f"{n}:a"
        elif len(stems) > 1:
            mix_in = "".join(f"[{n + j}:a]" for j in range(len(stems)))
            graph += f";{mix_in}amix=inputs={len(stems)}:duration=longest[aout]"
            audio_label = "[aout]"
        cmd = [self._ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error"]
        for img in frames:
            cmd += ["-loop", "1", "-t", str(seconds_per_frame), "-i", img]
        for stem in stems:
            cmd += ["-i", stem]
        cmd += ["-filter_complex", graph, "-map", "[vout]"]
        if audio_label:
            cmd += ["-map", audio_label]
        cmd += _encode_flags(preset) + [out]
        self._run_ffmpeg(cmd)
        probed = _probe_duration_seconds(out)
        duration = probed if probed else round(n * seconds_per_frame, 3)
        return ExportResult(
            output_path=out,
            preset_name=preset.name,
            format=preset.format,
            clip_count=n,
            size_bytes=os.path.getsize(out),
            duration_s=round(duration, 3),
            video_frames=int(round(duration * preset.frame_rate)),
            executor="ffmpeg",
            ffmpeg_used=True,
            created_at=datetime.now().isoformat(),
        )

    def _run_ffmpeg(self, cmd: list[str], list_path: Optional[str] = None) -> None:
        try:
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


class ConcatExportExecutor:
    """Offline fallback that still writes a real file.

    Byte-copies the input clips verbatim into one output (no transcoding,
    so an ``ffmpeg`` binary is not required). Audio stems are not muxable
    in a pure byte copy and are ignored; image-sequence assembly requires
    the ffmpeg executor.
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
        images: Optional[list[str]] = None,
        seconds_per_frame: float = 2.0,
    ) -> ExportResult:
        if images:
            raise ExportValidationError(
                "image-sequence assembly requires the ffmpeg executor "
                "(install ffmpeg or set FFMPEG_EXECUTOR=ffmpeg)")
        inputs = _validated_clips(clips)
        out = os.path.abspath(output_path or _default_output_path(inputs[0], preset))
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