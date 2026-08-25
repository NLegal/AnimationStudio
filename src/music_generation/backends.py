"""MusicGenerationBackend protocol, typed exceptions, and transport seams.

This module is the provider-agnostic core of the music generation layer
(Phase 7 research §4/§5 — LOCKED design decisions):

- ``MusicGenerationBackend`` is a ``@runtime_checkable`` ``typing.Protocol``
  so concrete backends satisfy it by duck-typing WITHOUT inheritance.
- The typed exception taxonomy maps transport/job failures per the
  research §2 error map and is consumed unchanged by the plan 07-02
  adapters (``AceStepBackend``, ``SunoBackend``).
- Module-level seams (``_sleep``, ``_urlopen``) route every delay and
  network flow through two patchable names so tests stay fully offline.

Constraint reminders: stdlib ``urllib.request`` only (no new deps), no
database access, no audio rendering anywhere in this package.
"""

import json
import socket
import time
import urllib.error
import urllib.request
from types import SimpleNamespace
from typing import Optional, Protocol, runtime_checkable

from pydantic import BaseModel

from src.audio_bible.prompts import category_negative

from .models import MusicRequest, MusicResult, MusicStatus

# --------------------------------------------------------------------------- #
# Typed exception taxonomy (research §2 error map)                            #
# --------------------------------------------------------------------------- #


class MusicBackendError(Exception):
    """Base class for every music-generation backend failure."""


class NotConfigured(MusicBackendError):
    """Raised when a backend cannot be used at all.

    Conditions: missing credential (env var unset), unauthorized access
    (HTTP 401/403), or a refusing stub backend. Callers should skip to
    another backend instead of retrying.
    """


class BackendUnavailable(MusicBackendError):
    """Raised when a remote backend cannot be reached.

    Conditions: connection refused, DNS failure, or timeout on submit,
    poll, or download. Callers may retry later or fall back offline.
    """


class GenerationFailed(MusicBackendError):
    """Raised when a generation job itself fails.

    Conditions: terminal ``failed`` job status, malformed response body
    (non-JSON, missing fields), submit-time failure injection, or the
    overall orchestration deadline expiring before completion.
    """


# --------------------------------------------------------------------------- #
# Protocol                                                                    #
# --------------------------------------------------------------------------- #


@runtime_checkable
class MusicGenerationBackend(Protocol):
    """Provider-agnostic music generation interface.

    Concrete backends (Mock today; ACE-Step / Suno in plan 07-02)
    satisfy this protocol structurally — isinstance checks work via
    ``@runtime_checkable`` without any inheritance.

    Class-attribute conventions consumed by the default ``generate()``
    loop below:

    - ``BACKEND_NAME``: name reported in ``MusicResult.backend``
      (fallback: the concrete class name).
    - ``AUDIO_FORMAT``: file format reported in ``MusicResult.format``
      (fallback: ``"wav"``).

    Note for duck-typed backends: Protocol default methods are NOT
    inherited structurally. Reuse the default orchestration loop with a
    plain class-level assignment, e.g. ``generate =
    MusicGenerationBackend.generate`` inside the concrete class body.
    """

    def is_configured(self) -> bool:
        """Return True when the backend has everything it needs to run."""
        ...

    def submit(self, request: MusicRequest) -> str:
        """Start one generation job and return its job id."""
        ...

    def poll(self, job_id: str) -> MusicStatus:
        """Return the current status for a previously submitted job."""
        ...

    def download(self, job_id: str) -> bytes:
        """Return the raw audio bytes for a completed job."""
        ...

    def generate(
        self,
        request: MusicRequest,
        *,
        timeout_s: float = 300.0,
        poll_interval_s: float = 2.0,
    ) -> MusicResult:
        """Convenience submit->poll->download loop with bounded waiting.

        Poll cadence: ``_sleep`` between attempts, doubling each retry
        (base -> x8 cap), until a terminal state or the monotonic deadline
        (``timeout_s``, default 300 s) passes. Deadline expiry and terminal
        failed states raise ``GenerationFailed`` (job id + elapsed seconds /
        server error text respectively). All delays route through the
        ``_sleep`` seam; all clock reads through the ``_monotonic`` seam —
        tests patch both and never really wait.
        """
        started = _monotonic()
        deadline = started + timeout_s
        job_id = self.submit(request)

        delay = poll_interval_s
        cap = poll_interval_s * 8
        status = self.poll(job_id)
        while status.state not in ("completed", "failed"):
            now = _monotonic()
            if now >= deadline:
                elapsed = now - started
                raise GenerationFailed(
                    f"Job '{job_id}' did not complete within {timeout_s}s "
                    f"(elapsed {elapsed:.1f}s)"
                )
            _sleep(delay)
            delay = min(delay * 2, cap)
            status = self.poll(job_id)

        if status.state == "failed":
            raise GenerationFailed(
                f"Job '{job_id}' failed: {status.error or 'unknown error'}"
            )
        audio = self.download(job_id)
        return MusicResult(
            request=request,
            audio=audio,
            format=getattr(self, "AUDIO_FORMAT", "wav"),
            job_id=job_id,
            backend=getattr(self, "BACKEND_NAME", type(self).__name__),
            seed=getattr(
                self, "_effective_seed",
                request.seed if request.seed is not None else 0,
            ),
        )


# --------------------------------------------------------------------------- #
# Category -> music-parameter mapping (RESEARCH §3 — LOCKED)                  #
# --------------------------------------------------------------------------- #


class CategoryMusicParams(BaseModel):
    """Numeric music parameters + lyric scaffold for one song category.

    Values are LOCKED by Phase 7 research §3 and anchored on the Phase 5
    audio bible standards — implement verbatim, do not redesign.
    """

    bpm: int
    key_scale: str
    time_signature: str
    lyric_structure: str
    duration_s: int
    caption_keyword: str


CATEGORY_MUSIC_PARAMS: dict[str, CategoryMusicParams] = {
    "Alphabet": CategoryMusicParams(
        bpm=110, key_scale="C major", time_signature="4/4",
        lyric_structure="[verse][chorus][verse][chorus]",
        duration_s=75, caption_keyword="alphabet",
    ),
    "Numbers": CategoryMusicParams(
        bpm=116, key_scale="D major", time_signature="4/4",
        lyric_structure="[verse][chorus][verse][chorus]",
        duration_s=75, caption_keyword="counting",
    ),
    "Colors": CategoryMusicParams(
        bpm=108, key_scale="G major", time_signature="4/4",
        lyric_structure="[verse][chorus][bridge][chorus]",
        duration_s=60, caption_keyword="colors",
    ),
    "Animals": CategoryMusicParams(
        bpm=120, key_scale="C major", time_signature="4/4",
        lyric_structure="[verse][chorus][verse][chorus]",
        duration_s=80, caption_keyword="animal",
    ),
    "Bedtime": CategoryMusicParams(
        bpm=66, key_scale="F major", time_signature="3/4",
        lyric_structure="[instrumental intro][verse][chorus][verse][outro]",
        duration_s=120, caption_keyword="lullaby",
    ),
}

# Generic fallback row mirroring the base-template path of
# build_music_prompt; the caption keyword is derived from the category
# slug at resolve time (template value here is a placeholder).
_GENERIC_ROW_TEMPLATE = CategoryMusicParams(
    bpm=110, key_scale="C major", time_signature="4/4",
    lyric_structure="[verse][chorus][verse][chorus]",
    duration_s=60, caption_keyword="",
)

_CATEGORY_LOOKUP = {
    name.lower(): params for name, params in CATEGORY_MUSIC_PARAMS.items()
}

DEFAULT_VOCALS = "female lead vocal, children's choir"


def resolve_music_params(category: str) -> CategoryMusicParams:
    """Resolve one category's locked parameters, case-insensitively.

    Exact-name matches against the five Phase 5 song categories return a
    copy of the locked row; anything else falls back to the generic row
    with its caption keyword derived from the category slug.
    """
    params = _CATEGORY_LOOKUP.get(category.strip().lower())
    if params is not None:
        return params.model_copy()
    slug = category.strip().lower() or "song"
    return _GENERIC_ROW_TEMPLATE.model_copy(update={"caption_keyword": slug})


def build_music_request(
    category: str,
    topic: str = "",
    *,
    vocals: str = DEFAULT_VOCALS,
    mood: str = "",
    seed: Optional[int] = None,
    lyrics_override: Optional[str] = None,
    tags: Optional[list[str]] = None,
    duration_s: Optional[int] = None,
) -> MusicRequest:
    """Build a ``MusicRequest`` with category-resolved defaults.

    Duration comes from the category's locked parameters when
    ``duration_s`` is None; an explicit value always wins.

    NOTE (locked decision, research §3): captions are NOT baked into this
    builder. Adapters compose captions by calling
    ``src.audio_bible.prompts.build_music_prompt`` so bible ordering rules
    stay authoritative; ``mood`` participates in that caption composition
    (and any future adapter payload), it is not part of ``MusicRequest``.
    """
    if duration_s is None:
        duration_s = resolve_music_params(category).duration_s
    return MusicRequest(
        category=category,
        topic=topic,
        duration_s=duration_s,
        vocals=vocals,
        lyrics_override=lyrics_override,
        seed=seed,
        tags=list(tags) if tags else [],
    )


def music_negative_prompt(category: str) -> str:
    """Thin wrapper returning the bible's layered category negatives.

    Pure delegation to ``category_negative(..., include_base=True)`` —
    zero re-implementation of negative-prompt rules.
    """
    return category_negative(category, include_base=True)


# --------------------------------------------------------------------------- #
# Transport seam — every delay/network flow must route through these names     #
# (stdlib urllib only per constraint C4; single choke point for the RESEARCH   #
# §2 error map, reused unchanged by plan 07-02 adapters)                       #
# --------------------------------------------------------------------------- #

# Explicit (connect_s, read_s) timeout tuple per RESEARCH §5.
_TRANSPORT_TIMEOUT = (5, 30)


def _sleep(seconds: float) -> None:
    """Delay seam: tests monkeypatch this instead of really waiting."""
    time.sleep(seconds)


def _monotonic() -> float:
    """Clock seam for deadline math: tests patch this to fast-forward time."""
    return time.monotonic()


def _urlopen(request: urllib.request.Request, timeout=None):
    """Network seam wrapping stdlib ``urllib.request.urlopen``.

    ``timeout`` may be a ``(connect_s, read_s)`` tuple — preserved at the
    seam so fakes/tests can assert the full contract — flattened here to
    the single socket timeout stdlib urlopen supports (conservative sum
    of both budgets). Plain numbers pass through unchanged.
    """
    if isinstance(timeout, (int, float)):
        flat = float(timeout)
    else:
        connect_s, read_s = timeout
        flat = float(connect_s) + float(read_s)
    return urllib.request.urlopen(request, timeout=flat)


def _http_error_to_typed(exc: urllib.error.HTTPError) -> MusicBackendError:
    """Map an HTTP error status to the typed taxonomy (RESEARCH §2).

    Header values (including Authorization) are never embedded in
    exception messages — threat T7-01-I.
    """
    code = getattr(exc, "code", None)
    if code in (401, 403):
        return NotConfigured(
            f"Music backend rejected credentials (HTTP {code})"
        )
    return GenerationFailed(f"Music backend returned HTTP {code}")


def _decode_json_object(raw: bytes) -> dict:
    """Strictly decode a JSON object body; anything else is a failure."""
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise GenerationFailed(
            "Malformed JSON body from music backend"
        ) from exc
    if not isinstance(parsed, dict):
        raise GenerationFailed(
            "Unexpected JSON shape from music backend (expected object)"
        )
    return parsed


def _post_json(
    url: str,
    payload: dict,
    headers: Optional[dict[str, str]] = None,
    timeout=_TRANSPORT_TIMEOUT,
) -> dict:
    """POST a JSON payload and decode the JSON object response."""
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    try:
        with _urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        raise _http_error_to_typed(exc) from exc
    except (urllib.error.URLError, socket.timeout, TimeoutError, OSError) as exc:
        raise BackendUnavailable(
            f"Music backend unreachable ({exc.__class__.__name__})"
        ) from exc
    return _decode_json_object(raw)


def _get_json(
    url: str,
    headers: Optional[dict[str, str]] = None,
    timeout=_TRANSPORT_TIMEOUT,
) -> dict:
    """GET a JSON object response."""
    request = urllib.request.Request(
        url, method="GET", headers=dict(headers or {}),
    )
    try:
        with _urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        raise _http_error_to_typed(exc) from exc
    except (urllib.error.URLError, socket.timeout, TimeoutError, OSError) as exc:
        raise BackendUnavailable(
            f"Music backend unreachable ({exc.__class__.__name__})"
        ) from exc
    return _decode_json_object(raw)


def _get_bytes(
    url: str,
    headers: Optional[dict[str, str]] = None,
    timeout=_TRANSPORT_TIMEOUT,
) -> bytes:
    """GET raw binary bytes (audio download)."""
    request = urllib.request.Request(
        url, method="GET", headers=dict(headers or {}),
    )
    try:
        with _urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise _http_error_to_typed(exc) from exc
    except (urllib.error.URLError, socket.timeout, TimeoutError, OSError) as exc:
        raise BackendUnavailable(
            f"Music backend unreachable ({exc.__class__.__name__})"
        ) from exc


# Pinned attribute names: plan 07-02 adapters consume these exactly as
# self._transport.post_json / self._transport.get_json / self._transport.get_bytes
DEFAULT_TRANSPORT = SimpleNamespace(
    post_json=_post_json,
    get_json=_get_json,
    get_bytes=_get_bytes,
)
