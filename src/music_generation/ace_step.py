"""ACE-Step 1.5 local REST adapter.

Speaks the real ACE-Step 1.5 async REST contract (vendor ``docs/en/API.md``)
against an EXTERNAL local service (ACE-Step Studio, default
``http://localhost:8001``). This code never starts, installs, or configures
the service; every network flow is routed through the injected transport
(``DEFAULT_TRANSPORT`` from ``backends.py`` when omitted), so tests stay
fully offline.

Vendor API (ACE-Step 1.5) — the only authoritative contract:
- ``GET  /health``              -> readiness probe
- ``POST /release_task``        -> create a task; returns ``task_id``
- ``POST /query_result``        -> batch status query (int status: 0 running,
  1 succeeded, 2 failed); ``result`` holds a JSON-encoded audio record
- ``GET  /v1/audio?path=...``   -> download audio bytes
- Auth: ``Authorization: Bearer <key>`` header OR ``ai_token`` body field.
  When the server has no ``ACESTEP_API_KEY`` configured, auth is DISABLED
  and requests carry no credential (our client sends the header only when a
  key resolves).

Error map (kept consistent with the LOCKED taxonomy):
- connection refused / DNS failure / timeout -> ``BackendUnavailable``
- HTTP 401/403                               -> ``NotConfigured``
- task status ``2`` / malformed bodies       -> ``GenerationFailed``

Header values (including the Bearer token) are never embedded in raised
messages or log records (threat T7-02-I).
"""

import json
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

# Real ACE-Step 1.5 response wrapper: {data, code, error, timestamp, extra}.
_DATA_KEY = "data"

# Real task status mapping (int) -> our MusicStatus.state.
_TASK_STATUS = {0: "running", 1: "completed", 2: "failed"}


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


def _unwrap(data):
    """Extract the 'data' field from the ACE-Step response wrapper.

    The vendor wraps every response as ``{data, code, error, ...}``.
    Tolerate a bare object (no wrapper) for robustness against simpler
    test scripts and future contract variants.
    """
    if isinstance(data, dict) and _DATA_KEY in data:
        inner = data[_DATA_KEY]
        if isinstance(inner, dict) or isinstance(inner, list):
            error = data.get("error")
            if isinstance(error, str) and error.strip():
                raise GenerationFailed(f"ACE-Step server error: {error}")
            return inner
    return data


def _decode_result_json(raw):
    """Parse the JSON-encoded ``result`` value found on a completed task.

    The real ACE-Step 1.5 contract (API.md §5.3) encodes ``result`` as a JSON
    string whose parsed value is an ARRAY of record dicts (one per generated
    item), e.g. ``'[{"file": "/v1/audio?path=...", "status": 1, ...}]'``.
    Some variants return a bare dict instead. Return the parsed value
    verbatim (dict or list); callers normalize via ``_record_from_result``.
    Only truly malformed values raise ``GenerationFailed``.
    """
    if isinstance(raw, dict):
        return raw
    if not isinstance(raw, str) or not raw.strip():
        return {}
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        raise GenerationFailed(
            "Malformed query result from ACE-Step (result is not JSON)"
        ) from exc
    if not isinstance(value, (dict, list)):
        raise GenerationFailed(
            "Malformed query result from ACE-Step (result is not an object)"
        )
    return value


def _record_from_result(result) -> dict:
    """Reduce a decoded ``result`` to a single record dict.

    Accepts either a dict directly, or a list of record dicts (the real
    ACE-Step shape). For a list, the first element is used (a single task
    yields one item); the first non-empty dict wins.
    """
    if isinstance(result, dict):
        return result
    if isinstance(result, list):
        for item in result:
            if isinstance(item, dict) and item:
                return item
    return {}


def _safe_snippet(value, limit: int = 200) -> str:
    """Render a decoded result record compactly for diagnostics."""
    try:
        text = json.dumps(value, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        text = str(value)
    if len(text) > limit:
        text = text[: limit - 3] + "..."
    return text


class AceStepBackend:
    """Async-job REST adapter for a LOCAL ACE-Step 1.5 service.

    - External dependency policy: this backend talks to a local service
      the operator starts themselves; we never spawn or install it.
    - Transport: every HTTP flow goes through ``self._transport``
      (pinned names ``post_json``/``get_json``/``get_bytes``), which
      defaults to the shared stdlib ``DEFAULT_TRANSPORT`` and can be
      replaced wholesale by fakes in tests (constraint C3).
    - Lifecycle: submit -> poll -> download via the protocol default
      ``generate()`` loop (doubling backoff capped x8, monotonic
      deadline of ``timeout_s=300``).
    - Auth: optional Bearer header. When ``ACESTEP_API_KEY`` is unset the
      real service runs with auth disabled and we simply omit the header.

    Error map: connection-level failures raise ``BackendUnavailable``;
    HTTP 401/403 raise ``NotConfigured``; failed terminal statuses (2)
    and malformed responses raise ``GenerationFailed``. Authorization
    header values never appear in exception messages or logs.
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
        self.api_key = api_key if api_key is not None else os.environ.get("ACESTEP_API_KEY")
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
        # task_id -> audio URL remembered from completed polls.
        self._audio_urls: dict[str, str] = {}
        self._effective_seed = None

    # ------------------------------------------------------------------ #
    #  MusicGenerationBackend surface (structural - no inheritance)       #
    # ------------------------------------------------------------------ #

    def _auth_headers(self) -> dict[str, str]:
        """Assemble Bearer headers at call time (never logged/serialized).

        An unset key means the local server runs without auth: omit the
        Authorization header entirely (matches the vendor contract).
        """
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def is_configured(self) -> bool:
        """True iff the local service answers a short-timeout health probe.

        Probes ``GET {base}/health`` (the real ACE-Step 1.5 readiness
        endpoint), falling back to a root GET when that path is missing
        (HTTP 404). ANY connection-level failure degrades to False —
        never a bare log line. A 401/403 still means False without
        probing further. No API key is required: the real service can
        run with auth disabled.
        """
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        try:
            _typed_transport_call(
                self._transport.get_json,
                f"{self.base_url}/health",
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
            # Endpoint missing (HTTP 404) or malformed body - the service
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
        """Start one generation task; returns its task id.

        Payload follows the vendor ``/release_task`` contract: bible-composed
        caption (prompt, <=512), category-scaffold lyrics (<=4096),
        audio_duration, bpm/key_scale/time_signature, integer seed with
        ``use_random_seed=false`` so the seed is honored, thinking=False,
        and the selected model name.
        """
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
            "prompt": caption,
            "lyrics": lyrics,
            "audio_duration": request.duration_s,
            "bpm": params.bpm,
            "key_scale": params.key_scale,
            "time_signature": params.time_signature,
            "seed": effective_seed,
            "use_random_seed": False,
            "thinking": False,
            "model": self.model,
        }

        response = _typed_transport_call(
            self._transport.post_json,
            f"{self.base_url}/release_task",
            payload,
            headers=self._auth_headers(),
        )
        data = _unwrap(response)
        if not isinstance(data, dict):
            raise GenerationFailed(
                "Malformed submit response from ACE-Step (missing data object)"
            )
        task_id = data.get("task_id")
        if not isinstance(task_id, str) or not task_id.strip():
            raise GenerationFailed(
                "Malformed submit response from ACE-Step (missing task_id)"
            )
        self._effective_seed = effective_seed
        return task_id

    def poll(self, task_id: str) -> MusicStatus:
        """Fetch one task's status from ``POST /query_result``.

        The vendor API is batch-oriented: we query a single-element list.
        Status codes are integers (0 running, 1 succeeded, 2 failed);
        unknown codes and non-object bodies are malformed responses
        (GenerationFailed). Completed tasks have their audio URL
        remembered for ``download()``.
        """
        response = _typed_transport_call(
            self._transport.post_json,
            f"{self.base_url}/query_result",
            {"task_id_list": [task_id]},
            headers=self._auth_headers(),
        )
        entries = _unwrap(response)
        if not isinstance(entries, list):
            raise GenerationFailed(
                "Malformed poll response from ACE-Step (expected data list)"
            )

        match = None
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            if entry.get("task_id") == task_id:
                match = entry
                break
        if match is None:
            raise GenerationFailed(
                f"ACE-Step poll returned no entry for task {task_id!r}"
            )

        code = match.get("status")
        if code not in _TASK_STATUS:
            raise GenerationFailed(
                f"Malformed poll response from ACE-Step "
                f"(unknown status {code!r})"
            )
        state = _TASK_STATUS[code]

        error = None
        if state == "failed":
            # Surface the real server-side reason. Common detail locations:
            # match-level error/message, then the decoded result record's
            # error/message/reason/exception fields, then a raw-record snippet.
            raw_error = match.get("error") or match.get("message")
            if isinstance(raw_error, str) and raw_error.strip():
                error = raw_error
            else:
                record = _record_from_result(
                    _decode_result_json(match.get("result"))
                )
                for key in ("error", "message", "reason", "exception",
                            "traceback"):
                    value = record.get(key)
                    if isinstance(value, str) and value.strip():
                        error = value
                        break
                if error is None:
                    # Fall back to a compact representation of the raw record
                    # so the caller can see what the server actually returned.
                    snippet = _safe_snippet(record)
                    if snippet:
                        error = f"server returned {snippet}"

        if state == "completed":
            record = _record_from_result(
                _decode_result_json(match.get("result"))
            )
            for key in ("file", "audio_path", "path", "output"):
                value = record.get(key)
                if isinstance(value, str) and value.strip():
                    self._audio_urls[task_id] = value
                    break

        return MusicStatus(
            state=state,
            progress=1.0 if state == "completed" else 0.0,
            error=error,
        )

    def download(self, task_id: str) -> bytes:
        """Return raw audio bytes for a completed task.

        Looks up the audio URL remembered by ``poll()``; when absent
        (poll never ran) performs exactly one poll first. The vendor
        ``result.file`` is itself a URL (usually ``/v1/audio?path=...``);
        relative URLs are resolved against ``base_url``. Audio bytes are
        accepted as opaque binary.
        """
        url = self._audio_urls.get(task_id)
        if url is None:
            status = self.poll(task_id)
            if status.state != "completed":
                raise GenerationFailed(
                    f"Task '{task_id}' has no downloadable audio "
                    f"(state: {status.state})"
                )
            url = self._audio_urls.get(task_id)
        if not url:
            raise GenerationFailed(
                f"Completed task '{task_id}' carried no audio URL"
            )

        if url.startswith("http://") or url.startswith("https://"):
            full_url = url
        else:
            full_url = f"{self.base_url}/{url.lstrip('/')}"

        payload = _typed_transport_call(
            self._transport.get_bytes,
            full_url,
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
