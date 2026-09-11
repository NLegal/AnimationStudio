"""Cloud-based video generation backends (fal.ai / Replicate / BFL).

Wraps cloud-hosted Wan / HunyuanVideo / LTX-Video endpoints behind the
``VideoGenerationBackend`` protocol so video generation is possible
without a local GPU. The ``get_backend('cloud')`` factory returns this
class. An explicit ``provider`` key selects the API; keys are
``fal`` / ``replicate``.

API keys are read from environment variables (same as
``generation_engine.cloud_backend``):
  - ``FAL_API_KEY``       → fal.ai
  - ``REPLICATE_API_KEY`` → Replicate

Keys are never logged or embedded in output metadata (threat T7-02-I).
"""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

from .base import (
    BackendUnavailable,
    GenerationFailed,
    NotConfigured,
    VideoGenerationBackend,
    VideoInput,
    VideoOutput,
    _monotonic,
    _sleep,
)

logger = logging.getLogger(__name__)

_PROVIDER_ENV: dict[str, str] = {
    "fal": "FAL_API_KEY",
    "replicate": "REPLICATE_API_KEY",
}

# Default video model endpoint per provider. fal models are accessed via
# ``https://fal.run/{model_id}``; Replicate models via their REST predictions
# API.
_PROVIDER_DEFAULT_MODEL: dict[str, str] = {
    "fal": "fal-ai/wan/v2.1/480p",
    "replicate": "wavespeedai/wan-2.1-i2v-480p-5s",
}


class CloudVideoBackend:
    """Cloud video generation adapter for fal.ai / Replicate.

    This backend raises ``NotConfigured`` at construction if no API key
    resolves, keeping the generation engine fail-fast on misconfiguration.

    Usage:
        backend = CloudVideoBackend(provider="fal", api_key="...")
        result = backend.generate(VideoInput(prompt="a duck hops", seed=42))
    """

    BACKEND_NAME = "cloud"
    VIDEO_FORMAT = "mp4"

    def __init__(
        self,
        provider: str = "fal",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        poll_timeout_s: float = 600.0,
    ):
        self.provider = provider.lower()
        self.api_key = api_key or os.environ.get(_PROVIDER_ENV.get(self.provider, ""), "")
        self.model = model or _PROVIDER_DEFAULT_MODEL.get(self.provider, "")
        self.poll_timeout_s = poll_timeout_s
        if not self.api_key:
            raise NotConfigured(
                f"No API key for cloud provider {self.provider!r}. "
                f"Set {_PROVIDER_ENV.get(self.provider, '?')} environment variable."
            )

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def submit(self, request: VideoInput) -> str:
        """Submit a generation job to the cloud provider; return a job id."""
        if self.provider == "fal":
            return self._submit_fal(request)
        if self.provider == "replicate":
            return self._submit_replicate(request)
        raise GenerationFailed(f"Unknown cloud provider: {self.provider}")

    def poll(self, job_id: str) -> str:
        """Return ``"completed"`` / ``"running"`` / ``"failed"`` for a job."""
        if self.provider == "fal":
            return self._poll_fal(job_id)
        if self.provider == "replicate":
            return self._poll_replicate(job_id)
        return "failed"

    def download(self, job_id: str) -> VideoOutput:
        """Fetch the rendered video bytes for a completed cloud job."""
        if self.provider == "fal":
            return self._download_fal(job_id)
        if self.provider == "replicate":
            return self._download_replicate(job_id)
        raise GenerationFailed(f"Unknown cloud provider: {self.provider}")

    generate = VideoGenerationBackend.generate

    # ------------------------------------------------------------------ #
    #  fal.ai                                                             #
    # ------------------------------------------------------------------ #

    def _submit_fal(self, request: VideoInput) -> str:
        payload = {
            "prompt": request.prompt,
            "seed": request.seed,
            "num_frames": request.frames,
            "fps": request.fps,
            "width": request.width,
            "height": request.height,
        }
        if request.first_frame_path:
            payload["image_url"] = request.first_frame_path

        body = self._post_json(
            f"https://fal.run/{self.model}",
            payload,
        )
        request_id = body.get("request_id", "")
        if not request_id:
            raise GenerationFailed("fal /run missing request_id")
        return request_id

    def _poll_fal(self, job_id: str) -> str:
        try:
            body = self._get_json(f"https://fal.run/{self.model}/requests/{job_id}")
        except GenerationFailed:
            return "running"
        status = body.get("status", "")
        if status == "COMPLETED":
            return "completed"
        if status in ("FAILED", "ERROR"):
            return "failed"
        return "running"

    def _download_fal(self, job_id: str) -> VideoOutput:
        body = self._get_json(f"https://fal.run/{self.model}/requests/{job_id}")
        video_url = body.get("output", {}).get("video", {}).get("url", "")
        if not video_url:
            raise GenerationFailed("fal job returned no video URL")
        video_bytes = self._download_url(video_url)
        return VideoOutput(
            video=video_bytes,
            format="mp4",
            seed=0,
            frames=0,
            job_id=job_id,
            backend=self.BACKEND_NAME,
            metadata={"provider": "fal", "model": self.model},
        )

    # ------------------------------------------------------------------ #
    #  Replicate                                                          #
    # ------------------------------------------------------------------ #

    def _submit_replicate(self, request: VideoInput) -> str:
        payload = {
            "input": {
                "prompt": request.prompt,
                "seed": request.seed,
                "num_frames": request.frames,
                "fps": request.fps,
                "width": request.width,
                "height": request.height,
            }
        }
        body = self._post_json(
            f"https://api.replicate.com/v1/models/{self.model}/predictions",
            payload,
            extra_headers={"Prefer": "wait"},
        )
        prediction_id = body.get("id", "")
        if not prediction_id:
            raise GenerationFailed("Replicate prediction missing id")
        return prediction_id

    def _poll_replicate(self, job_id: str) -> str:
        try:
            body = self._get_json(
                f"https://api.replicate.com/v1/predictions/{job_id}"
            )
        except GenerationFailed:
            return "running"
        status = body.get("status", "")
        if status == "succeeded":
            return "completed"
        if status == "failed":
            return "failed"
        return "running"

    def _download_replicate(self, job_id: str) -> VideoOutput:
        body = self._get_json(
            f"https://api.replicate.com/v1/predictions/{job_id}"
        )
        output = body.get("output", "")
        video_url = output if isinstance(output, str) else (output[0] if output else "")
        if not video_url:
            raise GenerationFailed("Replicate prediction returned no output")
        video_bytes = self._download_url(video_url)
        return VideoOutput(
            video=video_bytes,
            format="mp4",
            seed=0,
            frames=0,
            job_id=job_id,
            backend=self.BACKEND_NAME,
            metadata={"provider": "replicate", "model": self.model},
        )

    # ------------------------------------------------------------------ #
    #  Transport helpers (seams for tests)                                #
    # ------------------------------------------------------------------ #

    def _post_json(self, url: str, payload: dict, extra_headers: Optional[dict] = None) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as exc:
            code = exc.code
            if code in (401, 403):
                raise NotConfigured(f"Cloud backend rejected credentials (HTTP {code})")
            raise GenerationFailed(f"Cloud backend returned HTTP {code}")
        except urllib.error.URLError as exc:
            raise BackendUnavailable(f"Cloud backend unreachable: {exc.reason}") from exc

        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise GenerationFailed(f"Malformed JSON from cloud backend: {exc}") from exc

    def _get_json(self, url: str) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=60) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as exc:
            raise GenerationFailed(f"Cloud backend returned HTTP {exc.code}")
        except urllib.error.URLError as exc:
            raise BackendUnavailable(f"Cloud backend unreachable: {exc.reason}") from exc

        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise GenerationFailed(f"Malformed JSON from cloud backend: {exc}") from exc

    def _download_url(self, url: str) -> bytes:
        request = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(request, timeout=120) as resp:
                return resp.read()
        except urllib.error.URLError as exc:
            raise GenerationFailed(f"Failed to download video from {url}") from exc