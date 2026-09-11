"""HunyuanVideo — cloud video generation adapter.

Thin shim wrapping ``CloudVideoBackend`` with HunyuanVideo-specific model
defaults. HunyuanVideo runs hosted on fal.ai and Replicate; there is no
local-ComfyUI adapter for it because the model requires ~70 GB VRAM.

This adapter exists purely so ``get_backend('hunyuan')`` returns a
pre-configured ``CloudVideoBackend`` with the correct model IDs,
matching the clean single-name resolution in ``music_generation.get_backend``.
"""

from __future__ import annotations

from typing import Optional

from .cloud import CloudVideoBackend


_HUNYUAN_MODEL_DEFAULTS: dict[str, str] = {
    "fal": "fal-ai/hunyuan-video",
    "replicate": "lucataco/hunyuan-video",
}


class HunyuanVideoBackend(CloudVideoBackend):
    """CloudVideoBackend pre-configured for HunyuanVideo.

    Accepts the same constructor arguments as its parent; ``model``
    defaults to the HunyuanVideo-specific endpoint for the chosen
    ``provider``.
    """

    def __init__(
        self,
        provider: str = "fal",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        poll_timeout_s: float = 600.0,
    ):
        resolved_model = model or _HUNYUAN_MODEL_DEFAULTS.get(
            provider.lower(), ""
        )
        super().__init__(
            provider=provider,
            api_key=api_key,
            model=resolved_model,
            poll_timeout_s=poll_timeout_s,
        )