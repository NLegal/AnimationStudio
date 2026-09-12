"""Phase 5 — Voice Generation Backend (VISION Phase 5: Voices).

Provider-agnostic local voice (TTS) layer: typed request/status/result
models, the runtime-checkable ``VoiceGenerationBackend`` protocol, the
typed exception taxonomy (shared names with the music and video layers),
a deterministic offline mock, the real Kokoro backend (lazy-installed
engine), the refusing Piper/XTTS stubs (license gates), and the
``get_backend`` + ``backend_for_engine`` registries anchored on the
Phase 5 audio bible.

Constraints honored by this package: no network transport (every backend
is page-local), no database access (results stay in memory), and
mock/refusal paths are fully offline-exercisable in tests.
"""

from .backends import (
    BackendUnavailable,
    GenerationFailed,
    NotConfigured,
    VoiceBackendError,
    VoiceGenerationBackend,
    backend_for_engine,
    build_voice_request,
    get_backend,
    save_voice_result,
    voice_code_for_brief,
)
from .kokoro import KokoroBackend
from .mock import MockBackend
from .models import (
    DEFAULT_LANG_CODE,
    DEFAULT_VOICE_CODE,
    VoiceRequest,
    VoiceResult,
    VoiceStatus,
)
from .piper import PiperBackend
from .xtts import XttsBackend

__all__ = [
    "VoiceRequest",
    "VoiceStatus",
    "VoiceResult",
    "VoiceGenerationBackend",
    "VoiceBackendError",
    "NotConfigured",
    "BackendUnavailable",
    "GenerationFailed",
    "MockBackend",
    "KokoroBackend",
    "PiperBackend",
    "XttsBackend",
    "get_backend",
    "backend_for_engine",
    "build_voice_request",
    "voice_code_for_brief",
    "save_voice_result",
    "DEFAULT_VOICE_CODE",
    "DEFAULT_LANG_CODE",
]