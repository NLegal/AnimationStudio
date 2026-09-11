"""Backend registry and factory for the video generation package.

Mirrors the ``music_generation.backends.get_backend`` semantics: an
explicit ``name`` wins, ``None`` falls back to the ``VIDEO_BACKEND``
environment variable and then the safe offline default ``"mock"``.
Unknown names raise ``VideoBackendError`` listing the valid choices.
"""

from __future__ import annotations

import os
from typing import Callable, Optional

from .base import VideoBackendError


def _import_mock() -> type:
    from .mock import MockBackend

    return MockBackend


def _import_wan() -> type:
    from .wan import WanVideoBackend

    return WanVideoBackend


def _import_hunyuan() -> type:
    from .hunyuan import HunyuanVideoBackend

    return HunyuanVideoBackend


def _import_cloud() -> type:
    from .cloud import CloudVideoBackend

    return CloudVideoBackend


_BACKENDS: dict[str, Callable[[], type]] = {
    "mock": _import_mock,
    "wan": _import_wan,
    "hunyuan": _import_hunyuan,
    "cloud": _import_cloud,
}


def get_backend(name: Optional[str] = None, **kwargs):
    """Construct a video backend instance by name.

    Resolution: an explicit ``name`` wins; ``None`` falls back to the
    ``VIDEO_BACKEND`` environment variable and then to the safe offline
    default ``"mock"``. Unknown names raise ``VideoBackendError`` listing
    the valid choices.
    """
    resolved = name if name is not None else os.environ.get("VIDEO_BACKEND", "mock")
    key = str(resolved).strip().lower()
    hook = _BACKENDS.get(key)
    if hook is None:
        valid = ", ".join(sorted(_BACKENDS))
        raise VideoBackendError(
            f"Unknown video backend {resolved!r}. Valid backends: {valid}"
        )
    backend_cls = hook()
    if key in ("wan", "hunyuan", "cloud"):
        return backend_cls(**kwargs)
    return backend_cls()