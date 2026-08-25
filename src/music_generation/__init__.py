"""Phase 7 — Music Generation Backend Integration.

Provider-agnostic music generation core: typed request/status/result
models, the runtime-checkable ``MusicGenerationBackend`` protocol, the
typed exception taxonomy, the category → music-parameter mapping anchored
on the Phase 5 audio bible standards, a stdlib-only transport seam, and a
deterministic offline mock backend. Real adapters (ACE-Step, Suno), the
``get_backend`` registry, and the CLI land in plan 07-02.

Constraints honored by this package: no visual-asset generation, no audio
rendering (mock emits tiny deterministic PCM data structures only), no
database access (results stay in memory), no network outside the
injectable transport seam, stdlib ``urllib.request`` transport only.
"""

from .backends import (
    BackendUnavailable,
    GenerationFailed,
    MusicBackendError,
    MusicGenerationBackend,
    NotConfigured,
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
]
