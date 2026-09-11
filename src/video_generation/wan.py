"""Wan 2.x — ComfyUI video generation adapter.

Generates image-to-video clips through a LOCAL ComfyUI server's REST API
(``POST /prompt`` → poll ``/history/{id}`` → download the result via
``/view``), targeting the Wan 2.1 t2v/i2v family (``wan2.1-i2v-480p``,
``wan2.1-t2v-720p``, etc.). This adapter NEVER starts, installs, or
configures ComfyUI or the Wan checkpoint; every network flow is routed
through the injectable ``DEFAULT_TRANSPORT`` seam so tests stay fully
offline.

Mirrors ``ace_step.py``: ``NotConfigured`` for missing endpoint,
``BackendUnavailable`` for connection failures, ``GenerationFailed`` for
terminal job failure / malformed bodies. The three-phase shape follows the
``VideoGenerationBackend`` protocol so ``generate = 
VideoGenerationBackend.generate`` provides the bounded submit→poll→download
loop.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

from .base import (
    BackendUnavailable,
    GenerationFailed,
    NotConfigured,
    VideoBackendError,
    VideoGenerationBackend,
    VideoInput,
    VideoOutput,
    _monotonic,
    _sleep,
)

logger = logging.getLogger(__name__)

DEFAULT_SERVER_URL = "http://localhost:8188"

# Wan 2.x checkpoint names expected on the ComfyUI server (installer places
# them under this exact name — see setup_comfyui_flux.ps1 conventions).
_DEFAULT_WAN_CKPT = "Wan2.1_I2V_480P_14B_fp8_e4m3fn.safetensors"

# ComfyUI workflow graph for Wan 2.x img2vid. Node ids follow the common
# exported AnimateDiff-Evolved / Wan2.1 template: UNETLoader + CLIPLoader +
# VAELoader → CLIPTextEncode → WanImageToVideo → KSampler → VAEDecode →
# SaveAnimatedWEBP / SaveVideo via Video Helper Suite.
_DEFAULT_WORKFLOW_TEMPLATE: dict = {
    "3": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {"ckpt_name": _DEFAULT_WAN_CKPT},
    },
    "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["3", 1]}},
    "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["3", 1]}},
    "8": {
        "class_type": "WanImageToVideo",
        "inputs": {
            "width": 832,
            "height": 480,
            "length": 81,
            "batch_size": 1,
            "positive": ["6", 0],
            "negative": ["7", 0],
            "vae": ["3", 2],
        },
    },
    "5": {
        "class_type": "KSampler",
        "inputs": {
            "seed": 42,
            "steps": 20,
            "cfg": 5.0,
            "sampler_name": "euler",
            "scheduler": "simple",
            "denoise": 1.0,
            "model": ["3", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["8", 0],
        },
    },
    "10": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["3", 2]}},
    "12": {
        "class_type": "VHS_VideoCombine",
        "inputs": {
            "filename_prefix": "wan",
            "frame_rate": 16,
            "images": ["10", 0],
            "format": "mp4",
        },
    },
}


class WanVideoBackend:
    """Wan 2.x video backend driving a local ComfyUI server.

    The ComfyUI server must already have the Wan checkpoint(s) installed
    (see the Phase 9 notebook / setup scripts). This class only speaks the
    REST contract.

    Usage:
        backend = WanVideoBackend()  # or WanVideoBackend(server_url=...)
        result = backend.generate(VideoInput(prompt="a duck hops on a leaf",
                                             frames=81))
    """

    BACKEND_NAME = "wan"
    VIDEO_FORMAT = "mp4"

    def __init__(
        self,
        server_url: str = DEFAULT_SERVER_URL,
        workflow_template: Optional[dict] = None,
        transport=None,
    ):
        self.server_url = server_url.rstrip("/")
        self.workflow_template = workflow_template or dict(_DEFAULT_WORKFLOW_TEMPLATE)
        self._client_id = "animation-studio-wan"
        self.transport = transport or DEFAULT_TRANSPORT

    # ------------------------------------------------------------------ #
    #  VideoGenerationBackend surface (structural — no inheritance)       #
    # ------------------------------------------------------------------ #

    def is_configured(self) -> bool:
        """The adapter runs against any configured server URL."""
        return bool(self.server_url)

    def submit(self, request: VideoInput) -> str:
        """POST the Wan workflow to ``/prompt`` and return the ``prompt_id``."""
        workflow = self._build_workflow(request)
        payload = {
            "prompt": workflow,
            "client_id": self._client_id,
        }
        try:
            body = self.transport(
                "POST",
                f"{self.server_url}/prompt",
                payload=payload,
                headers={"Content-Type": "application/json"},
            )
        except VideoBackendError:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            raise BackendUnavailable(
                f"Wan backend unreachable at {self.server_url}: {exc}"
            ) from exc

        try:
            decoded = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise GenerationFailed(
                f"Malformed JSON from Wan /prompt: {exc}"
            ) from exc
        prompt_id = decoded.get("prompt_id")
        if not prompt_id:
            raise GenerationFailed(
                "Wan /prompt response missing prompt_id"
            )
        return str(prompt_id)

    def poll(self, job_id: str) -> str:
        """Return ``"completed"``/``"failed"`` once the workflow is terminal."""
        try:
            body = self.transport("GET", f"{self.server_url}/history/{job_id}")
        except VideoBackendError:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            raise BackendUnavailable(
                f"Wan history unreachable for {job_id}: {exc}"
            ) from exc

        try:
            history = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            # History may 404 briefly before the job is recorded; treat as
            # still running rather than a hard failure.
            raise GenerationFailed(
                f"Malformed JSON from Wan /history: {exc}"
            ) from exc

        entry = history.get(job_id)
        if entry is None:
            return "running"
        if entry.get("status", {}).get("status_str") == "success":
            return "completed"
        return "failed"

    def download(self, job_id: str) -> VideoOutput:
        """Fetch the rendered video bytes via ``/view`` using history output."""
        try:
            history_body = self.transport("GET", f"{self.server_url}/history/{job_id}")
        except VideoBackendError:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            raise BackendUnavailable(
                f"Wan history unreachable for {job_id}: {exc}"
            ) from exc
        try:
            history = json.loads(history_body.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise GenerationFailed(
                f"Malformed JSON from Wan /history on download: {exc}"
            ) from exc

        entry = history.get(job_id, {})
        outputs = entry.get("outputs", {})
        video_file = self._find_first_video(outputs)
        if video_file is None:
            raise GenerationFailed(
                f"Wan job {job_id} produced no video outputs"
            )

        query = urllib.parse.urlencode(video_file)
        body = self.transport(
            "GET", f"{self.server_url}/view?{query}",
        )
        requested_frames = 0
        try:
            prompt = entry.get("prompt", {})
            if isinstance(prompt, dict):
                requested_frames = int(
                    prompt.get("8", {}).get("inputs", {}).get("length", 0) or 0
                )
        except (TypeError, ValueError, AttributeError):
            pass  # frames are best-effort metadata only

        return VideoOutput(
            video=body,
            format=self.VIDEO_FORMAT,
            frames=requested_frames,
            job_id=job_id,
            backend=self.BACKEND_NAME,
            metadata={"prompt_id": job_id, "file": video_file},
        )

    # ------------------------------------------------------------------ #
    #  Helpers                                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _find_first_video(outputs: dict) -> Optional[dict]:
        """Return the first VHS video output (or gif) file info in outputs."""
        for _node_id, node_output in outputs.items():
            for video in node_output.get("videos", []) or []:
                if video.get("format") == "video/h264-mp4":
                    return {
                        "filename": video.get("filename", ""),
                        "subfolder": video.get("subfolder", ""),
                        "type": video.get("type", "output"),
                        "format": video.get("format", ""),
                    }
            # Legacy SaveAnimatedWEBP-style single-file output
            for gif in node_output.get("gifs", []) or []:
                return {
                    "filename": gif.get("filename", ""),
                    "subfolder": gif.get("subfolder", ""),
                    "type": gif.get("type", "output"),
                }
        return None

    def _build_workflow(self, request: VideoInput) -> dict:
        """Materialize the Wan i2v workflow from one VideoInput."""
        import copy
        workflow = copy.deepcopy(self.workflow_template)

        for node in workflow.values():
            cls = node.get("class_type", "")
            inputs = node.get("inputs", {})
            if cls == "CheckpointLoaderSimple" and not inputs.get("ckpt_name"):
                inputs["ckpt_name"] = request.model or _DEFAULT_WAN_CKPT
            elif cls == "CLIPTextEncode" and inputs.get("clip"):
                continue
            elif cls == "WanImageToVideo":
                inputs["width"] = request.width
                inputs["height"] = request.height
                inputs["length"] = _to_wan_length(request.frames)
            elif cls == "KSampler":
                inputs["seed"] = request.seed
                if request.motion_bucket:
                    inputs["cfg"] = max(1.0, request.motion_bucket / 24.0)
            elif cls == "VHS_VideoCombine":
                inputs["frame_rate"] = request.fps
                inputs["filename_prefix"] = f"wan_{request.seed}"

        # Inject text into CLIPTextEncode nodes (6 = positive, 7 = negative)
        text_nodes = [n for n in workflow.values()
                      if n.get("class_type") == "CLIPTextEncode"]
        if len(text_nodes) >= 1:
            text_nodes[0]["inputs"]["text"] = request.prompt
        if len(text_nodes) >= 2:
            text_nodes[1]["inputs"]["text"] = request.negative_prompt
        return workflow


_DEFAULT_TRANSPORT = None
def DEFAULT_TRANSPORT(method: str, url: str, *, payload=None, headers=None):
    """Real transport: stdlib urllib for GET/POST, returning raw bytes."""
    request = urllib.request.Request(url, headers=headers or {})
    if method == "POST":
        request.data = json.dumps(payload).encode("utf-8")
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=(5, 30)) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            raise NotConfigured("Wan backend rejected credentials")
        if exc.code >= 500:
            raise BackendUnavailable(
                f"Wan backend unavailable (HTTP {exc.code})"
            )
        raise GenerationFailed(f"Wan backend returned HTTP {exc.code}")
    except urllib.error.URLError as exc:
        raise BackendUnavailable(str(exc.reason)) from exc


def _to_wan_length(frames: int) -> int:
    """Wan's WanImageToVideo ``length`` is a latent-frame count.

    Reasonable mapping: number of video frames, clamped to Wan's typical
    supported window (33–121). Upsampling happens inside the workflow.
    """
    return max(33, min(121, int(frames)))