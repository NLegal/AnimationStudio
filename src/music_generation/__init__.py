"""Phase 7 — Music Generation Backend Integration.

Provider-agnostic music generation layer: typed request/status/result
models, the runtime-checkable ``MusicGenerationBackend`` protocol, the
typed exception taxonomy, the category → music-parameter mapping anchored
on the Phase 5 audio bible standards, a stdlib-only transport seam, the
real ACE-Step REST adapter plus a deterministic offline mock, and the
``get_backend`` registry (Suno refusal stub + experimental wrapper land
later in plan 07-02).

Constraints honored by this package: no visual-asset generation, no audio
rendering (mock emits tiny deterministic PCM data structures only), no
database access (results stay in memory), no network outside the
injectable transport seam, stdlib ``urllib.request`` transport only.
"""

from .ace_step import AceStepBackend
from .backends import (
    BackendUnavailable,
    GenerationFailed,
    MusicBackendError,
    MusicGenerationBackend,
    NotConfigured,
    get_backend,
)
from .mock import MockBackend
from .models import MusicRequest, MusicResult, MusicStatus

__all__ = [
    "MusicRequest",
    "MusicStatus",
    "MusicResult",
    "MusicGenerationBackend",
    "MusicBackendError",
    "NotConfigured",
    "BackendUnavailable",
    "GenerationFailed",
    "MockBackend",
    "AceStepBackend",
    "get_backend",
]
