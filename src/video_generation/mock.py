"""Deterministic mock video generation backend.

Synthesizes a tiny, structurally valid MP4-family byte payload (ftyp +
moov/mvhd + mdat with seed-derived bytes) so the download-path parsing
stays exercisable offline. This is a data-structure exercise only — it is
NOT video rendering, touches no GPU/FFmpeg, and never performs network I/O.

Contract: same effective seed ⇒ byte-identical output, mirroring the
music ``MockBackend`` regression guarantee.
"""

from __future__ import annotations

import random
import struct
import uuid
from typing import Optional

from .base import (
    GenerationFailed,
    VideoGenerationBackend,
    VideoInput,
    VideoOutput,
    _sleep,
)


def _box(box_type: bytes, payload: bytes) -> bytes:
    """Wrap *payload* in one ISO-BMFF box (size + type + payload)."""
    return struct.pack(">I", 8 + len(payload)) + box_type + payload


def _mp4_box(fourcc: bytes, payload: bytes) -> bytes:
    """Alias of ``_box`` that spells a 4-char code in the type slot."""
    return _box(fourcc, payload)


def _synthesize_mp4(seed: int) -> bytes:
    """Synthesize a deterministic tiny MP4-family payload for one seed."""
    rng = random.Random(seed)

    # ftyp: brand box (isom / mp42)
    ftyp = _mp4_box(
        b"ftyp",
        b"isom" + struct.pack(">I", 512) + b"isommp42",
    )

    # mvhd: empty movie header with a seed-derived timescale
    timescale = 1000 + (seed % 9000)
    ver_flags = b"\x00\x00\x00\x00"
    mvhd = _mp4_box(
        b"mvhd",
        ver_flags
        + struct.pack(">IIIII", rng.randint(0, 2**32), rng.randint(0, 2**32),
                      timescale, 0, 1000)
        + b"\x00" * 80,
    )
    moov = _mp4_box(b"moov", mvhd)

    # mdat: seed-derived opaque media bytes (deterministic, small)
    n = 256 + rng.randint(0, 2048)
    data_bytes = bytes(rng.getrandbits(8) for _ in range(n))
    mdat = _mp4_box(b"mdat", data_bytes)

    return ftyp + moov + mdat


class MockBackend:
    """Deterministic placeholder video backend.

    Usage:
        backend = MockBackend()
        result = backend.generate(VideoInput(prompt="a duck hops", seed=7))
        assert result.video.startswith(b"\x00\x00\x00\x18ftyp")
    """

    BACKEND_NAME = "mock"
    VIDEO_FORMAT = "mp4"

    def __init__(
        self,
        latency_s: float = 0.0,
        fail_submit: bool = False,
        states_before_complete: int = 0,
        seed: Optional[int] = None,
    ):
        self.latency_s = latency_s
        self.fail_submit = fail_submit
        self.states_before_complete = max(0, states_before_complete)
        self.seed = seed
        self._jobs: dict[str, dict] = {}

    # ------------------------------------------------------------------ #
    #  VideoGenerationBackend surface (structural — no inheritance)       #
    # ------------------------------------------------------------------ #

    def is_configured(self) -> bool:
        """The mock always runs: no credentials, network, or hardware."""
        return True

    def submit(self, request: VideoInput) -> str:
        """Register one job; honours fail_submit failure injection."""
        if self.fail_submit:
            raise GenerationFailed(
                "MockBackend configured with fail_submit=True"
            )
        effective_seed = request.seed
        if effective_seed is None:
            effective_seed = self.seed
        if effective_seed is None:
            effective_seed = 0
        job_id = f"mock-vid-{uuid.uuid4().hex}"
        self._jobs[job_id] = {
            "request": request,
            "seed": effective_seed,
            "polls": 0,
        }
        return job_id

    def poll(self, job_id: str) -> str:
        """Walk pending→running→completed across states_before_complete."""
        job = self._jobs.get(job_id)
        if job is None:
            raise GenerationFailed(f"Unknown mock video job '{job_id}'")
        if self.latency_s > 0:
            _sleep(self.latency_s)
        polls = job["polls"]
        job["polls"] += 1
        if polls >= self.states_before_complete:
            return "completed"
        return "running"

    def download(self, job_id: str) -> VideoOutput:
        """Return the deterministic MP4-family payload synthesized at submit."""
        job = self._jobs.get(job_id)
        if job is None:
            raise GenerationFailed(f"Unknown mock video job '{job_id}'")
        request: VideoInput = job["request"]
        return VideoOutput(
            video=_synthesize_mp4(job["seed"]),
            format=self.VIDEO_FORMAT,
            seed=job["seed"],
            frames=request.frames,
            job_id=job_id,
            backend=self.BACKEND_NAME,
        )

    generate = VideoGenerationBackend.generate