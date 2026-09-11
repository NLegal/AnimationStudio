"""Video generation engine — abstract base for pluggable video backends.

Closes the VISION Phase 9 image-to-video gap (no Wan / HunyuanVideo /
LTX-Video adapter existed). Mirrors the ``music_generation`` adapter
architecture: a ``@runtime_checkable`` Protocol, a typed error taxonomy,
and opt-in transport seams so every network-capable adapter stays fully
exercisable offline in tests.

This module NEVER starts, installs, or configures a video service. Each
concrete adapter decides its own transport (local ComfyUI REST for Wan,
cloud REST for fal/Replicate) behind the same three-phase
submit → poll → download contract.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional, Protocol, runtime_checkable


@dataclass
class VideoInput:
    """Input contract for video generation."""

    prompt: str = ""
    negative_prompt: str = ""
    first_frame_path: str = ""      # optional conditioning image (img2vid)
    seed: int = 42
    width: int = 1280
    height: int = 720
    frames: int = 120               # total frames (duration_seconds x fps)
    fps: int = 24
    motion_bucket: int = 127        # Wan-style motion intensity 1-255
    model: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class VideoOutput:
    """Output contract for video generation."""

    video: bytes = b""              # raw mp4 bytes (download-path payload)
    format: str = "mp4"
    seed: int = 0
    frames: int = 0
    job_id: str = ""
    backend: str = ""
    metadata: dict = field(default_factory=dict)


class VideoBackendError(Exception):
    """Base class for every video-generation backend failure."""


class NotConfigured(VideoBackendError):
    """Raised when a backend cannot be used at all.

    Conditions: missing credential / endpoint (env var unset), or a
    refusing stub backend. Callers should skip to another backend.
    """


class BackendUnavailable(VideoBackendError):
    """Raised when a remote backend cannot be reached.

    Conditions: connection refused, DNS failure, or timeout on submit,
    poll, or download. Callers may retry later or fall back offline.
    """


class GenerationFailed(VideoBackendError):
    """Raised when a generation job itself fails.

    Conditions: terminal ``failed`` job status, malformed response body,
    submit-time failure injection, or the orchestration deadline expiring
    before completion.
    """


# --------------------------------------------------------------------------- #
# Transport seams — every delay/network flow must route through these names    #
# --------------------------------------------------------------------------- #

def _sleep(seconds: float) -> None:
    time.sleep(seconds)


def _monotonic() -> float:
    return time.monotonic()


# --------------------------------------------------------------------------- #
# Protocol                                                                     #
# --------------------------------------------------------------------------- #

@runtime_checkable
class VideoGenerationBackend(Protocol):
    """Provider-agnostic video generation interface.

    Concrete backends (Mock today; Wan / cloud in this package) satisfy
    the protocol structurally — isinstance checks work via
    ``@runtime_checkable`` without inheritance.

    Class-attribute conventions consumed by the default ``generate()``
    loop below:

    - ``BACKEND_NAME``: name reported in ``VideoOutput.backend``.
    - ``VIDEO_FORMAT``: file format reported in ``VideoOutput.format``.

    Note for duck-typed backends: Protocol default methods are NOT
    inherited structurally. Reuse the default orchestration loop with a
    plain class-level assignment, e.g. ``generate =
    VideoGenerationBackend.generate`` inside the concrete class body.
    """

    def is_configured(self) -> bool:
        """Return True when the backend has everything it needs to run."""
        ...

    def submit(self, request: VideoInput) -> str:
        """Start one generation job and return its job id."""
        ...

    def poll(self, job_id: str):
        """Return the current terminal/reference state for a job."""
        ...

    def download(self, job_id: str) -> VideoOutput:
        """Return the raw video output for a completed job."""
        ...

    def generate(
        self,
        request: VideoInput,
        *,
        timeout_s: float = 900.0,
        poll_interval_s: float = 2.0,
    ) -> VideoOutput:
        """Convenience submit → poll → download loop with bounded waiting.

        Poll cadence: ``_sleep`` between attempts, doubling each retry up
        to a ``poll_interval_s * 8`` cap, until a terminal state or the
        monotonic deadline passes. Deadline expiry and terminal failed
        states raise ``GenerationFailed``. All delays route through the
        ``_sleep`` seam; all clock reads through ``_monotonic`` — tests
        patch both and never really wait.
        """
        started = _monotonic()
        deadline = started + timeout_s
        job_id = self.submit(request)

        delay = poll_interval_s
        cap = poll_interval_s * 8
        status = self.poll(job_id)
        while status not in ("completed", "failed"):
            if _monotonic() >= deadline:
                raise GenerationFailed(
                    f"{self.__class__.__name__} did not complete within "
                    f"{timeout_s}s (job {job_id})"
                )
            _sleep(delay)
            delay = min(delay * 2, cap)
            status = self.poll(job_id)

        if status == "failed":
            raise GenerationFailed(
                f"{self.__class__.__name__} job {job_id} failed"
            )

        result = self.download(job_id)
        if not result.video and not result.metadata.get("output_path"):
            raise GenerationFailed(
                f"{self.__class__.__name__} job {job_id} returned no video"
            )
        return result