"""Deterministic mock music generation backend.

Synthesizes tiny PCM data structures shaped as valid RIFF/WAV payloads
so the download-path parsing stays exercisable offline. This is a
data-structure exercise only — it is NOT audio rendering, touches no
audio hardware, and never performs network I/O.
"""

import math
import random
import struct
import uuid
from typing import Optional

from .backends import GenerationFailed, MusicGenerationBackend, _sleep
from .models import MusicRequest, MusicStatus


_SAMPLE_RATE = 8000        # 8 kHz mono
_NUM_SAMPLES = 2000        # ~2000 samples total (tiny on purpose)
_SEGMENT_LENGTH = 250      # 8 alternating tone/silence segments
_PEAK_AMPLITUDE = 12000    # well inside int16 headroom


def _synthesize_wav(seed: int) -> bytes:
    """Synthesize a deterministic tiny WAV for one effective seed.

    Same seed ⇒ byte-identical output. Structure: 44-byte canonical RIFF
    header + 16-bit little-endian mono samples alternating seed-derived
    sine segments with silence.
    """
    rng = random.Random(seed)
    samples = bytearray()
    segments = _NUM_SAMPLES // _SEGMENT_LENGTH
    for index in range(segments):
        if index % 2 == 0:
            # Seed-derived pitch (±2 semitones around A3), amplitude and phase.
            frequency = 220.0 * (2.0 ** (rng.randint(-2, 2) / 12.0))
            amplitude = _PEAK_AMPLITUDE * (0.6 + 0.4 * rng.random())
            phase = rng.random() * 2.0 * math.pi
            for n in range(_SEGMENT_LENGTH):
                value = amplitude * math.sin(
                    phase + 2.0 * math.pi * frequency * n / _SAMPLE_RATE
                )
                samples += struct.pack("<h", int(value))
        else:
            samples += b"\x00\x00" * _SEGMENT_LENGTH

    data_size = len(samples)
    header = b"".join([
        b"RIFF",
        struct.pack("<I", 36 + data_size),
        b"WAVE",
        b"fmt ",
        struct.pack("<IHHIIHH", 16, 1, 1, _SAMPLE_RATE,
                    _SAMPLE_RATE * 2, 2, 16),
        b"data",
        struct.pack("<I", data_size),
    ])
    return bytes(header) + bytes(samples)


class MockBackend:
    """Deterministic placeholder music backend.

    Contract: same effective seed ⇒ byte-identical output, so re-running
    a job with the same seeds reproduces the exact same bytes (useful for
    regression tests).

    Effective seed chain: ``request.seed`` → constructor ``seed`` → 0.
    Sample synthesis is driven entirely by ``random.Random(effective_seed)``.

    Usage:
        backend = MockBackend()
        result = backend.generate(MusicRequest(category="Bedtime", seed=7))
        assert result.audio.startswith(b"RIFF")
    """

    BACKEND_NAME = "mock"
    AUDIO_FORMAT = "wav"

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
        self._effective_seed: Optional[int] = None

    # ------------------------------------------------------------------ #
    #  MusicGenerationBackend surface (structural — no inheritance)       #
    # ------------------------------------------------------------------ #

    def is_configured(self) -> bool:
        """The mock always runs: no credentials, network, or hardware."""
        return True

    def submit(self, request: MusicRequest) -> str:
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
        job_id = f"mock-{uuid.uuid4().hex}"
        self._jobs[job_id] = {
            "request": request,
            "seed": effective_seed,
            "polls": 0,
        }
        self._effective_seed = effective_seed
        return job_id

    def poll(self, job_id: str) -> MusicStatus:
        """Walk pending→running→completed across states_before_complete calls."""
        job = self._jobs.get(job_id)
        if job is None:
            raise GenerationFailed(f"Unknown mock music job '{job_id}'")
        if self.latency_s > 0:
            _sleep(self.latency_s)
        polls = job["polls"]
        job["polls"] += 1
        if polls >= self.states_before_complete:
            return MusicStatus(state="completed", progress=1.0)
        state = "pending" if polls == 0 else "running"
        progress = 0.25 if state == "pending" else 0.6
        return MusicStatus(state=state, progress=progress)

    def download(self, job_id: str) -> bytes:
        """Return the deterministic WAV payload synthesized at submit time."""
        job = self._jobs.get(job_id)
        if job is None:
            raise GenerationFailed(f"Unknown mock music job '{job_id}'")
        return _synthesize_wav(job["seed"])

    # Reuse the shared default orchestration loop without inheriting from
    # the protocol (Protocol default methods are not inherited structurally).
    generate = MusicGenerationBackend.generate
