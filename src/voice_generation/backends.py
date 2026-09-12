"""VoiceGenerationBackend protocol, typed exceptions, and wiring helpers.

This module is the provider-agnostic core of the Phase 5 Voices layer
(VISION.md Phase 5 — Kokoro / XTTS v2 / Piper). It deliberately mirrors
``src/music_generation/backends.py`` so both audio-facing pipelines share
one shape:

- ``VoiceGenerationBackend`` is a ``@runtime_checkable`` ``typing.Protocol``
  satisfied by duck-typing WITHOUT inheritance.
- The typed exception taxonomy reuses the same names/meaning as the music
  and video layers, so orchestration code treats backends uniformly.
- ``build_voice_request`` derives a ``VoiceRequest`` from a bible
  ``VoiceBrief`` (or ``VoiceProfile``) — voice code per character, pace per
  speech-speed label.
- ``backend_for_engine`` maps the bible's approved engine names
  (``NARRATOR_ENGINE`` = "Kokoro", ``CHARACTER_ENGINE`` = "XTTS v2",
  ``OFFLINE_ENGINE`` = "Piper") to concrete backends; unknown engines
  resolve to the safe offline mock.
- ``get_backend`` reads the ``TTS_BACKEND`` environment variable and falls
  back to the deterministic offline mock.

Constraint reminders: no network transport (every voice backend is page
local), no database access, and no real speech rendering in this module —
``_wav_duration`` only parses a WAV header for bookkeeping.
"""

from __future__ import annotations

import io
import os
import re
import time
import wave
from typing import Callable, Optional, Protocol, runtime_checkable

from .models import (
    DEFAULT_LANG_CODE,
    DEFAULT_VOICE_CODE,
    VoiceRequest,
    VoiceResult,
    VoiceStatus,
)

# --------------------------------------------------------------------------- #
# Typed exception taxonomy (shared names with music/video layers)              #
# --------------------------------------------------------------------------- #


class VoiceBackendError(Exception):
    """Base class for every voice-generation backend failure."""


class NotConfigured(VoiceBackendError):
    """Raised when a backend cannot be used at all.

    Conditions: missing TTS engine (Python package not installed), an
    unknown voice code or language, unapproved license (refusing stubs),
    or misconfiguration. Callers should route to another backend instead
    of retrying.
    """


class BackendUnavailable(VoiceBackendError):
    """Raised when the local engine cannot be loaded (hardware/init error).

    Callers may retry later or fall back offline.
    """


class GenerationFailed(VoiceBackendError):
    """Raised when a voice generation job itself fails.

    Conditions: model inference error, empty audio output, or unknown job.
    """


# --------------------------------------------------------------------------- #
# Protocol + default orchestration loop                                        #
# --------------------------------------------------------------------------- #


@runtime_checkable
class VoiceGenerationBackend(Protocol):
    """Provider-agnostic voice (TTS) generation interface.

    Concrete backends (Mock today; Kokoro real, Piper/XTTS refusing stubs)
    satisfy this protocol structurally — isinstance checks work via
    ``@runtime_checkable`` without any inheritance.

    Class-attribute conventions consumed by the default ``generate()`` loop:

    - ``BACKEND_NAME``: name reported in ``VoiceResult.backend``
      (fallback: the concrete class name).
    - ``AUDIO_FORMAT``: format reported in ``VoiceResult.format``
      (fallback: ``"wav"``).

    Note for duck-typed backends: Protocol default methods are NOT inherited
    structurally. Reuse the default orchestration loop with a plain class
    assignment, e.g. ``generate = VoiceGenerationBackend.generate``.
    """

    def is_configured(self) -> bool:
        """Return True when the backend has everything it needs to run."""
        ...

    def submit(self, request: VoiceRequest) -> str:
        """Start one generation job and return its job id."""
        ...

    def poll(self, job_id: str) -> VoiceStatus:
        """Return the current status for a previously submitted job."""
        ...

    def download(self, job_id: str) -> bytes:
        """Return the raw WAV bytes for a completed job."""
        ...

    def generate(
        self,
        request: VoiceRequest,
        *,
        timeout_s: float = 300.0,
        poll_interval_s: float = 1.0,
    ) -> VoiceResult:
        """Convenience submit->poll->download loop with bounded waiting.

        Poll cadence: ``_sleep`` between attempts, doubling each retry
        (base -> x8 cap), until a terminal state or the monotonic deadline
        (``timeout_s``, default 300 s) passes. Deadline expiry and terminal
        failed states raise ``GenerationFailed``. All delays route through
        the ``_sleep`` seam; all clock reads through the ``_monotonic``
        seam — tests patch both and never really wait.
        """
        started = _monotonic()
        deadline = started + timeout_s
        job_id = self.submit(request)

        delay = poll_interval_s
        cap = poll_interval_s * 8
        status = self.poll(job_id)
        while status.state not in ("completed", "failed"):
            now = _monotonic()
            if now >= deadline:
                elapsed = now - started
                raise GenerationFailed(
                    f"Job '{job_id}' did not complete within {timeout_s}s "
                    f"(elapsed {elapsed:.1f}s)"
                )
            _sleep(delay)
            delay = min(delay * 2, cap)
            status = self.poll(job_id)

        if status.state == "failed":
            raise GenerationFailed(
                f"Job '{job_id}' failed: {status.error or 'unknown error'}"
            )
        audio = self.download(job_id)
        return VoiceResult(
            request=request,
            audio=audio,
            format=getattr(self, "AUDIO_FORMAT", "wav"),
            sample_rate=request.sample_rate,
            duration_s=_wav_duration(audio, request.sample_rate),
            job_id=job_id,
            backend=getattr(self, "BACKEND_NAME", type(self).__name__),
            seed=getattr(
                self, "_effective_seed",
                request.seed if request.seed is not None else 0,
            ),
        )


# --------------------------------------------------------------------------- #
# Bible-aware request assembly                                                 #
# --------------------------------------------------------------------------- #

# Bible-approved speech-speed labels -> Kokoro pace multiplier.
_SPEED_LABEL_TO_PACE = {
    "fast": 1.15,
    "medium": 1.0,
    "medium-fast": 1.1,
    "slow": 0.9,
    "slow-medium": 0.9,
    "calm": 0.9,
}

# Phase 5 character roster -> Kokoro v1.0 voice code (tuneable seed map).
# Every code is an American male/female voice so the narrator default lang
# ("a") applies to every character without a separate language context.
CHARACTER_VOICE_CODES = {
    "lily bunny": "af_sarah",
    "ben bear": "am_michael",
    "daisy duck": "af_nova",
    "charlie fox": "am_fenrir",
    "mommy bunny": "af_heart",
    "daddy bunny": "am_adam",
    "grandma bunny": "af_kore",
    "grandpa bunny": "am_eric",
    "baby bunny": "af_sky",
    "teacher owl": "af_nicole",
    "narrator": "af_heart",
}


def voice_code_for_brief(brief) -> str:
    """Return the Kokoro voice code for a ``VoiceBrief``/``VoiceProfile``.

    Looks the character up case-insensitively in ``CHARACTER_VOICE_CODES``;
    unknown characters fall back to the narrator default so a synthesized
    voice always exists.
    """
    name = getattr(brief, "character", "") or ""
    return CHARACTER_VOICE_CODES.get(name.strip().lower(), DEFAULT_VOICE_CODE)


def pace_for_brief(brief) -> float:
    """Map a bible speech-speed label to a Kokoro pace multiplier."""
    label = getattr(brief, "speech_speed", "") or ""
    return _SPEED_LABEL_TO_PACE.get(label.strip().lower(), 1.0)


def build_voice_request(
    text: str,
    *,
    voice_code: Optional[str] = None,
    speaker: Optional[str] = None,
    pace: Optional[float] = None,
    seed: Optional[int] = None,
    lang_code: Optional[str] = None,
    sample_rate: Optional[int] = None,
    brief=None,
) -> VoiceRequest:
    """Build a ``VoiceRequest`` with bible-aware defaults.

    An explicit keyword always wins over values derived from ``brief``.
    ``brief`` may be a ``VoiceBrief`` or ``VoiceProfile`` (anything with
    ``character``/``speech_speed`` attributes).
    """
    return VoiceRequest(
        text=text,
        speaker=speaker or (getattr(brief, "character", None) or "unnamed"),
        voice_code=voice_code or voice_code_for_brief(brief),
        lang_code=lang_code or DEFAULT_LANG_CODE,
        pace=pace if pace is not None else pace_for_brief(brief),
        seed=seed,
        sample_rate=sample_rate or 24000,
    )


# --------------------------------------------------------------------------- #
# Engine-name resolution (bible approved engines -> concrete backends)         #
# --------------------------------------------------------------------------- #

_ENGINE_TO_BACKEND = {
    "kokoro": "kokoro",
    "xtts": "xtts",
    "xtts v2": "xtts",
    "piper": "piper",
}


def backend_for_engine(engine_name, **kwargs):
    """Resolve a bible-approved engine name to a voice backend.

    Mirrors the mapping in ``AudioBible.validate_voice_brief``: "Kokoro"
    -> the local Kokoro backend, "XTTS v2" -> refusing XTTS stub,
    "Piper" -> refusing Piper stub (license gates, see STACK.md). Any
    unknown engine name resolves to the deterministic offline mock so the
    production pipeline never hard-fails on an unapproved engine label.
    """
    key = _ENGINE_TO_BACKEND.get(str(engine_name or "").strip().lower())
    if key is None:
        return get_backend("mock", **kwargs)
    return get_backend(key, **kwargs)


# --------------------------------------------------------------------------- #
# WAV bookkeeping + file persistence                                           #
# --------------------------------------------------------------------------- #


def _wav_duration(audio: bytes, sample_rate: int) -> float:
    """Return a WAV payload's duration in seconds; 0.0 on any parse issue."""
    try:
        with wave.open(io.BytesIO(audio), "rb") as wav:
            frames = wav.getnframes()
            rate = wav.getframerate() or sample_rate
    except (wave.Error, ValueError, EOFError):
        return 0.0
    return round(frames / rate, 4)


def _slugify(text: str) -> str:
    """Lowercase slug: non-alphanumeric runs collapse to single hyphens."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")
    return slug or "voice"


def save_voice_result(
    result: VoiceResult,
    out_dir: str,
    *,
    speaker: Optional[str] = None,
) -> str:
    """Write a ``VoiceResult``'s WAV to ``out_dir`` and return the path.

    Deterministic name ``{speaker}-{seed}-{job_id8}.wav`` so re-running the
    same request overwrites (not duplicates) its file.
    """
    os.makedirs(out_dir, exist_ok=True)
    who = speaker or result.request.speaker or "unnamed"
    slug = _slugify(who)
    fname = f"{slug}-{result.seed}-{result.job_id[:8]}.wav"
    path = os.path.join(out_dir, fname)
    with open(path, "wb") as fh:
        fh.write(result.audio)
    return path


# --------------------------------------------------------------------------- #
# Delay/clock seams — tests monkeypatch these instead of really waiting        #
# --------------------------------------------------------------------------- #


def _sleep(seconds: float) -> None:
    """Delay seam: tests monkeypatch this instead of really waiting."""
    time.sleep(seconds)


def _monotonic() -> float:
    """Clock seam for deadline math: tests patch this to fast-forward time."""
    return time.monotonic()


# --------------------------------------------------------------------------- #
# Backend registry + factory                                                   #
#                                                                             #
# Hooks import adapter modules LAZILY inside get_backend to avoid circular    #
# imports (piper/xtts import the taxonomy from this module).                  #
# --------------------------------------------------------------------------- #


def _import_mock() -> type:
    from .mock import MockBackend

    return MockBackend


def _import_kokoro() -> type:
    from .kokoro import KokoroBackend

    return KokoroBackend


def _import_piper() -> type:
    from .piper import PiperBackend

    return PiperBackend


def _import_xtts() -> type:
    from .xtts import XttsBackend

    return XttsBackend


_BACKENDS: dict[str, Callable[[], type]] = {
    "kokoro": _import_kokoro,
    "mock": _import_mock,
    "piper": _import_piper,
    "xtts": _import_xtts,
}


def get_backend(name: Optional[str] = None, **kwargs):
    """Construct a voice backend instance by name.

    Resolution: an explicit ``name`` wins; ``None`` falls back to the
    ``TTS_BACKEND`` environment variable and then to the safe offline
    default ``"mock"``. Unknown names raise ``VoiceBackendError`` listing
    the four valid choices.
    """
    resolved = name if name is not None else os.environ.get("TTS_BACKEND", "mock")
    key = str(resolved).strip().lower()
    hook = _BACKENDS.get(key)
    if hook is None:
        valid = ", ".join(sorted(_BACKENDS))
        raise VoiceBackendError(
            f"Unknown voice backend {resolved!r}. Valid backends: {valid}"
        )
    backend_cls = hook()
    return backend_cls(**kwargs)