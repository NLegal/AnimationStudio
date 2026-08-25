"""ACE-Step 1.5 local REST adapter.

Speaks the LOCKED Phase 7 research §2 contract against an EXTERNAL local
service (ACE-Step Studio, default ``http://localhost:8001``). This code
never starts, installs, or configures the service; every network flow is
routed through the injected transport (``DEFAULT_TRANSPORT`` from
``backends.py`` when omitted), so tests stay fully offline.

Error map (research §2 — enforced here AND at the plan-01 seam):
- connection refused / DNS failure / timeout → ``BackendUnavailable``
- HTTP 401/403                               → ``NotConfigured``
- job status ``failed`` / malformed bodies   → ``GenerationFailed``

Header values (including the Bearer token) are never embedded in raised
messages or log records (threat T7-02-I).
"""

import logging
import os
import re
import socket
import urllib.error
import urllib.parse

from src.audio_bible.prompts import build_music_prompt

from .backends import (
    DEFAULT_TRANSPORT,
    BackendUnavailable,
    GenerationFailed,
    MusicBackendError,
    MusicGenerationBackend,
    NotConfigured,
    _http_error_to_typed,
    resolve_music_params,
)
from .models import MusicRequest, MusicStatus

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://localhost:8001"
VALID_MODELS = ("acestep-v15-turbo", "acestep-v15-sft")
DEFAULT_MODEL = "acestep-v15-turbo"

_CAPTION_MAX_CHARS = 512
_LYRICS_MAX_CHARS = 4096
_HEALTH_TIMEOUT = (5.0, 5.0)     # short connect budget per RESEARCH §5
_MARKER_RE = re.compile(r"\[[^\]]*\]")

_AUDIO_PATH_KEYS = ("audio_path", "path", "output")


def _typed_transport_call(fn, *args, **kwargs):
    """Invoke one transport call, normalizing raw network errors.

    The pinned transport surface already maps errors at the seam, but
    fake/injected transports may raise raw ``URLError``/``HTTPError``
    directly — translate those with the exact same locked error map so
    the taxonomy holds end-to-end through the adapter.
    """
    try:
        return fn(*args, **kwargs)
    except MusicBackendError:
        raise
    except urllib.error.HTTPError as exc:
        raise _http_error_to_typed(exc) from exc
    except (urllib.error.URLError, socket.timeout, TimeoutError, OSError) as exc:
        raise BackendUnavailable(
            f"Music backend unreachable ({exc.__class__.__name__})"
        ) from exc


class AceStepBackend:
    """Async-job REST adapter for a LOCAL ACE-Step Studio service.

    - External dependency policy: this backend talks to a local service
      the operator starts themselves; we never spawn or install it.
    - Transport: every HTTP flow goes through ``self._transport``
      (pinned names ``post_json``/``get_json``/``get_bytes``), which
      defaults to the shared stdlib ``DEFAULT_TRANSPORT`` and can be
      replaced wholesale by fakes in tests (constraint C3).
    - Lifecycle: submit → poll → download via the protocol default
      ``generate()`` loop (doubling backoff capped x8, monotonic
      deadline of ``timeout_s=300``).

    Error map summary (research §2): connection-level failures raise
    ``BackendUnavailable``; HTTP 401/403 raise ``NotConfigured``;
    failed terminal states and malformed responses raise
    ``GenerationFailed``. Authorization header values never appear in
    exception messages or logs.
    """

    BACKEND_NAME = "ace-step"
    AUDIO_FORMAT = "wav"

    def __init__(
        self,
        api_key=None,
        base_url=None,
        model=None,
        transport=None,
    ):
        # Credential/base resolution order per C5: constructor arg > env.
        self.api_key = api_key or os.environ.get("ACESTEP_API_KEY")
        resolved_base = (
            base_url
            or os.environ.get("ACESTEP_BASE_URL")
            or DEFAULT_BASE_URL
        )
        self.base_url = str(resolved_base).rstrip("/")
        if model is not None and model not in VALID_MODELS:
            raise ValueError(
                f"Invalid ACE-Step model {model!r}. "
                f"Valid models: {', '.join(VALID_MODELS)}"
            )
        self.model = model or DEFAULT_MODEL
        self._transport = transport if transport is not None else DEFAULT_TRANSPORT
        # job_id -> audio path/URL remembered from completed polls.
        self._audio_paths: dict[str, str] = {}
        self._effective_seed = None

    # ------------------------------------------------------------------ #
    #  MusicGenerationBackend surface (structural — no inheritance)       #
    # ------------------------------------------------------------------ #

    def _auth_headers(self) -> dict[str, str]:
        """Assemble Bearer headers at call time (never logged/serialized)."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def is_configured(self) -> bool:
        """True iff a key resolves AND a short-timeout probe succeeds.

        Probes ``GET {base}/v1/jobs/health`` first, falling back to a
        root GET when that endpoint is missing (HTTP 404). ANY
        connection-level failure degrades to False — never a bare log
        line. A 401/403 means the key itself was rejected: False without
        probing further.
        """
        if not self.api_key:
            return False
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            _typed_transport_call(
                self._transport.get_json,
                f"{self.base_url}/v1/jobs/health",
                headers=headers,
                timeout=_HEALTH_TIMEOUT,
            )
            return True
        except NotConfigured:
            return False
        except BackendUnavailable as exc:
            logger.warning(
                "ACE-Step service at %s unreachable during health probe (%s); "
                "backend reports not configured.",
                self.base_url, exc.__class__.__name__,
            )
            return False
        except MusicBackendError:
            # Endpoint missing (HTTP 404) or malformed body — the service
            # answered, so try the root probe before degrading.
            logger.debug("ACE-Step health endpoint missing at %s; "
                         "falling back to root probe", self.base_url)

        try:
            _typed_transport_call(
                self._transport.get_json,
                f"{self.base_url}/",
                headers=headers,
                timeout=_HEALTH_TIMEOUT,
            )
            return True
        except MusicBackendError as exc:
            logger.warning(
                "ACE-Step service at %s unreachable during health probe (%s); "
                "backend reports not configured.",
                self.base_url, exc.__class__.__name__,
            )
            return False

    def submit(self, request: MusicRequest) -> str:
        """Start one generation job; returns its job id.

        Payload fields follow research §2 verbatim: bible-composed
        caption (≤512), category-scaffold lyrics (≤4096), audio_duration,
        bpm/key_scale/time_signature from the locked table, integer seed,
        thinking=False, and the selected model name.
        """
        if not self.api_key:
            raise NotConfigured(
                "No ACE-Step API key configured; set ACESTEP_API_KEY "
                "(or pass api_key to the constructor)"
            )

        params = resolve_music_params(request.category)
        caption = build_music_prompt(
            request.category, request.topic, vocals=request.vocals,
        )[:_CAPTION_MAX_CHARS]
        if request.lyrics_override is not None:
            lyrics = request.lyrics_override[:_LYRICS_MAX_CHARS]
        else:
            lyrics = "\n".join(_MARKER_RE.findall(params.lyric_structure))

        effective_seed = int(request.seed or 0)
        payload = {
            "caption": caption,
            "lyrics": lyrics,
            "audio_duration": request.duration_s,
            "bpm": params.bpm,
            "key_scale": params.key_scale,
            "time_signature": params.time_signature,
            "seed": effective_seed,
            "thinking": False,
            "model": self.model,
        }

        response = _typed_transport_call(
            self._transport.post_json,
            f"{self.base_url}/v1/music/generate",
            payload,
            headers=self._auth_headers(),
        )

        job_id = response.get("job_id") if isinstance(response, dict) else None
        if not isinstance(job_id, str) or not job_id.strip():
            raise GenerationFailed(
                "Malformed submit response from ACE-Step (missing job_id)"
            )
        self._effective_seed = effective_seed
        return job_id

    def poll(self, job_id: str) -> MusicStatus:
        """Fetch one job's current status from ``GET /v1/jobs/{id}``.

        Status strings pass straight into ``MusicStatus.state``; unknown
        strings and non-object bodies are malformed responses
        (GenerationFailed). Completed jobs have their audio path/URL
        remembered for ``download()``.
        """
        response = _typed_transport_call(
            self._transport.get_json,
            f"{self.base_url}/v1/jobs/{job_id}",
            headers=self._auth_headers(),
        )
        if not isinstance(response, dict):
            raise GenerationFailed(
                "Malformed poll response from ACE-Step (expected JSON object)"
            )
        state = response.get("status")
        if state not in ("pending", "running", "completed", "failed"):
            raise GenerationFailed(
                f"Malformed poll response from ACE-Step "
                f"(unknown status {state!r})"
            )
        try:
            default_progress = 1.0 if state == "completed" else 0.0
            progress = float(response.get("progress", default_progress))
        except (TypeError, ValueError) as exc:
            raise GenerationFailed(
                "Malformed poll response from ACE-Step (invalid progress)"
            ) from exc

        if state == "completed":
            for key in _AUDIO_PATH_KEYS:
                value = response.get(key)
                if isinstance(value, str) and value.strip():
                    self._audio_paths[job_id] = value
                    break

        return MusicStatus(
            state=state,
            progress=progress,
            error=response.get("error") if state == "failed" else None,
        )

    def download(self, job_id: str) -> bytes:
        """Return raw audio bytes for a completed job.

        Looks up the path remembered by ``poll()``; when absent (poll
        never ran) performs exactly one poll first. The path is
        percent-encoded into the query string verbatim. Audio bytes are
        accepted as opaque binary; when the transport exposes response
        headers, a non-audio content-type only logs a warning.
        """
        path = self._audio_paths.get(job_id)
        if path is None:
            status = self.poll(job_id)
            if status.state != "completed":
                raise GenerationFailed(
                    f"Job '{job_id}' has no downloadable audio "
                    f"(state: {status.state})"
                )
            path = self._audio_paths.get(job_id)
        if not path:
            raise GenerationFailed(
                f"Completed job '{job_id}' carried no audio path"
            )

        url = (
            f"{self.base_url}/v1/audio?"
            f"path={urllib.parse.quote(path, safe='')}"
        )
        payload = _typed_transport_call(
            self._transport.get_bytes,
            url,
            headers=self._auth_headers(),
        )

        # Best-effort content-type visibility: plain-bytes transports
        # carry none (opaque acceptance), richer fakes may expose one.
        headers = getattr(payload, "headers", None)
        getter = getattr(headers, "get", None)
        if callable(getter):
            content_type = str(
                getter("content-type") or getter("Content-Type") or ""
            )
            if content_type and not content_type.startswith("audio/"):
                logger.warning(
                    "ACE-Step download returned non-audio content-type %r; "
                    "continuing (bytes treated as opaque binary)",
                    content_type,
                )
        return payload

    # Reuse the shared default orchestration loop without inheriting from
    # the protocol (Protocol default methods are not inherited structurally).
    generate = MusicGenerationBackend.generate
