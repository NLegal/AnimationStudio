"""Kokoro voice backend — real local TTS via the ``kokoro`` package.

Kokoro is the Phase 5 flagship TTS engine (``NARRATOR_ENGINE`` == "Kokoro"):
Apache-2.0, ~82M params, CPU real-time, 8 languages / 54 voices. ``kokoro``
is NOT a base dependency of this repo, so it is imported LAZILY inside the
backend; ``is_configured()`` reports True only when the package is actually
installed.

Offline-exercisable parity: the full backend surface (``submit``/``poll``/
``download`` and the default ``generate`` loop) runs without kokoro
installed — only ``download`` would touch the model, so ``submit`` performs
the engine-presence + request validation up front and raises
``NotConfigured`` with exact install instructions.

The ``seed`` field is accepted but NOT honored by the real engine (torch
inference is not bit-deterministic); the mock is the deterministic surface.
"""

from __future__ import annotations

import importlib.util
import io
import math
import uuid
import wave
from typing import Optional

from .backends import (
    GenerationFailed,
    NotConfigured,
    VoiceGenerationBackend,
    _sleep,
)
from .models import VoiceRequest, VoiceResult, VoiceStatus

KOKORO_INSTALL_MESSAGE = (
    "kokoro is not installed — run `pip install kokoro>=0.9.4 soundfile` "
    "(plus espeak-ng support for your platform) to enable local TTS"
)

# Kokoro v1.0 voice family prefixes (two-letter language + gender).
_KNOWN_VOICE_PREFIXES = frozenset({
    "af", "am", "bf", "bm", "ef", "em", "ff", "fm",
    "hf", "hm", "if", "im", "jf", "jm", "pf", "pm", "zf", "zm",
})

# Kokoro language codes accepted by KPipeline(lang_code=...).
_KNOWN_LANG_CODES = frozenset({
    "a", "b", "e", "f", "h", "i", "j", "p", "z",
})

_KOKORO_OUTPUT_RATE = 24000


def _float32_to_pcm16(mono) -> bytes:
    """Convert a float32 [-1, 1] mono array to little-endian int16 bytes."""
    import numpy as np

    clipped = np.clip(np.asarray(mono, dtype=np.float32), -1.0, 1.0)
    pcm = np.clip(np.rint(clipped * 32767.0), -32768, 32767)
    return pcm.astype(np.int16).tobytes()


def _resample_pcm16(pcm: bytes, src_rate: int, dst_rate: int) -> bytes:
    """Linearly resample int16 mono PCM between two rates."""
    import numpy as np

    samples = np.frombuffer(pcm, dtype=np.int16).astype(np.float32)
    num_out = max(1, int(round(len(samples) * dst_rate / src_rate)))
    x_old = np.linspace(0.0, 1.0, len(samples), endpoint=False)
    x_new = np.linspace(0.0, 1.0, num_out, endpoint=False)
    resampled = np.interp(x_new, x_old, samples)
    return np.clip(np.rint(resampled), -32768, 32767).astype(np.int16).tobytes()


def _pcm16_to_wav(pcm: bytes, sample_rate: int) -> bytes:
    """Wrap int16 mono PCM in a canonical 16-bit mono RIFF/WAV payload."""
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm)
    return buffer.getvalue()


class KokoroBackend:
    """Real local Kokoro TTS backend (lazy-installed engine).

    ``submit`` validates the voice code / language against the known Kokoro
    families and confirms the engine package is present (raising
    ``NotConfigured`` with install instructions otherwise). Rendering is
    synchronous — ``poll`` immediately reports ``completed`` and
    ``download`` synthesizes (and caches) the WAV on first call.
    """

    BACKEND_NAME = "kokoro"
    AUDIO_FORMAT = "wav"

    def __init__(self, latency_s: float = 0.0):
        self.latency_s = latency_s
        self._jobs: dict[str, VoiceRequest] = {}
        self._results: dict[str, bytes] = {}
        self._pipeline = None
        self._pipeline_lang: Optional[str] = None

    def is_configured(self) -> bool:
        """True only when the ``kokoro`` Python package is installed."""
        return importlib.util.find_spec("kokoro") is not None

    def _validate(self, request: VoiceRequest) -> None:
        """Reject requests the engine provably cannot render."""
        prefix = request.voice_code.split("_", 1)[0].lower()
        if prefix not in _KNOWN_VOICE_PREFIXES:
            raise NotConfigured(
                f"Unknown Kokoro voice family in {request.voice_code!r}; "
                "expected a code like 'af_heart' or 'am_michael'"
            )
        if request.lang_code.lower() not in _KNOWN_LANG_CODES:
            raise NotConfigured(
                f"Unknown Kokoro lang_code {request.lang_code!r}; "
                f"expected one of {', '.join(sorted(_KNOWN_LANG_CODES))}"
            )
        if not self.is_configured():
            raise NotConfigured(KOKORO_INSTALL_MESSAGE)

    def _pipeline_for(self, lang_code: str, kpipeline_cls):
        """Cache one ``KPipeline`` per language code (model load is heavy)."""
        if self._pipeline is not None and self._pipeline_lang == lang_code:
            return self._pipeline
        self._pipeline = kpipeline_cls(lang_code=lang_code)
        self._pipeline_lang = lang_code
        return self._pipeline

    def _synth(self, request: VoiceRequest) -> bytes:
        """Run (or simulate) Kokoro synthesis and return WAV bytes."""
        try:
            import numpy as np
            from kokoro import KPipeline
        except ImportError as exc:
            raise NotConfigured(KOKORO_INSTALL_MESSAGE) from exc

        try:
            pipeline = self._pipeline_for(request.lang_code, KPipeline)
            chunks: list = []
            for item in pipeline(
                request.text, voice=request.voice_code, speed=request.pace
            ):
                # Newer kokoro yields (i, gs, ps, audio); README's simple
                # example yields (gs, ps, audio). Accept both.
                if len(item) == 4:
                    audio = item[3]
                else:
                    audio = item[2]
                chunks.append(np.asarray(audio, dtype=np.float32))
        except NotConfigured:
            raise
        except Exception as exc:  # torch/model errors are engine failures
            raise GenerationFailed(
                f"Kokoro synthesis failed: {exc.__class__.__name__}"
            ) from exc

        if not chunks:
            raise GenerationFailed(
                f"Kokoro produced no audio for '{request.text[:40]!r}'"
            )
        pcm = _float32_to_pcm16(np.concatenate(chunks))
        if request.sample_rate != _KOKORO_OUTPUT_RATE:
            pcm = _resample_pcm16(pcm, _KOKORO_OUTPUT_RATE, request.sample_rate)
        return _pcm16_to_wav(pcm, request.sample_rate)

    # ------------------------------------------------------------------ #
    #  VoiceGenerationBackend surface (structural — no inheritance)       #
    # ------------------------------------------------------------------ #

    def submit(self, request: VoiceRequest) -> str:
        """Validate the request + engine presence, register one job."""
        self._validate(request)
        job_id = f"kokoro-{uuid.uuid4().hex}"
        self._jobs[job_id] = request
        return job_id

    def poll(self, job_id: str) -> VoiceStatus:
        """Synchronous engine: immediately report completed for known jobs."""
        if job_id not in self._jobs:
            raise GenerationFailed(f"Unknown kokoro voice job '{job_id}'")
        if self.latency_s > 0:
            _sleep(self.latency_s)
        return VoiceStatus(state="completed", progress=1.0)

    def download(self, job_id: str) -> bytes:
        """Synthesize (once) and return the WAV bytes for a completed job."""
        if job_id not in self._jobs:
            raise GenerationFailed(f"Unknown kokoro voice job '{job_id}'")
        if job_id not in self._results:
            self._results[job_id] = self._synth(self._jobs[job_id])
        return self._results[job_id]

    # Reuse the shared default orchestration loop.
    generate = VoiceGenerationBackend.generate