"""Video Generation Engine — pluggable video backend layer (VISION Phase 9).

Provider-agnostic video generation: typed request/output models, the
``@runtime_checkable`` ``VideoGenerationBackend`` protocol, typed exception
taxonomy, deterministic offline mock, local ComfyUI Wan 2.x adapter,
and cloud fal/Replicate/HunyuanVideo adapters.

No service is started or installed by this package; every adapter routes
network calls through stdlib transport seams, keeping the full stack fully
offline-exercisable in tests.

Exit keys: ``VideoInput``, ``VideoOutput``, ``VideoBackendError``,
``VideoGenerationBackend``, ``get_backend``.
"""

from .backends import get_backend
from .base import (
    BackendUnavailable,
    GenerationFailed,
    NotConfigured,
    VideoBackendError,
    VideoGenerationBackend,
    VideoInput,
    VideoOutput,
)
from .mock import MockBackend

__all__ = [
    "VideoInput",
    "VideoOutput",
    "VideoGenerationBackend",
    "VideoBackendError",
    "NotConfigured",
    "BackendUnavailable",
    "GenerationFailed",
    "MockBackend",
    "get_backend",
]