"""Pydantic v2 models for the voice generation backend contracts.

Mirrors the conventions of ``src/music_generation/models.py`` (and the
``src/models/schemas.py`` family): ``Literal`` enums, ``Optional[T] = None``,
bounded ``Field`` values, one docstring per class.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


# VISION Phase 5 Voices — narrator default voice. Kokoro American female,
# warm storybook tone; tune via the backend registry, never at runtime here.
DEFAULT_VOICE_CODE = "af_heart"

# Kokoro language code: "a" = American English.
DEFAULT_LANG_CODE = "a"


class VoiceRequest(BaseModel):
    """Request for one TTS (voice) generation job.

    ``text`` is the sentence to speak; ``speaker`` and ``voice_code`` carry
    the character identity so every line for one character shares the same
    voice. ``pace`` scales the speaking rate (1.0 = native), ``lang_code``
    selects the Kokoro model language, ``sample_rate`` the requested WAV
    sample rate (the mock honors it exactly; the real Kokoro engine outputs
    a fixed 24 kHz and resamples when a different rate is requested).
    """

    text: str = Field(min_length=1, max_length=2000)
    speaker: str = "unnamed"
    voice_code: str = DEFAULT_VOICE_CODE
    lang_code: str = DEFAULT_LANG_CODE
    pace: float = Field(default=1.0, ge=0.5, le=2.0)
    seed: Optional[int] = None
    sample_rate: int = Field(default=24000, ge=8000, le=48000)


class VoiceStatus(BaseModel):
    """Poll status of an async voice generation job.

    ``state`` vocabulary mirrors the pipeline job state machine
    (``src/pipeline/job_queue.py``): pending | running | completed | failed.
    """

    state: Literal["pending", "running", "completed", "failed"]
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    error: Optional[str] = None


class VoiceResult(BaseModel):
    """Result of a completed voice generation job.

    Held in memory only — persistence into the asset catalog is explicitly
    out of scope for the adapter layer.
    """

    request: VoiceRequest
    audio: bytes
    format: Literal["wav"] = "wav"
    sample_rate: int
    duration_s: float
    job_id: str
    backend: str
    seed: int