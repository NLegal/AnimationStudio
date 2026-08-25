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

import time
import urllib.request
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
        """Convenience submit->poll->download loop.

        Minimal-but-correct orchestration in this task: poll on a fixed
        cadence until a terminal state, raise ``GenerationFailed`` on a
        terminal failed state. Backoff doubling, deadline enforcement,
        and the ``_monotonic`` seam land with the transport hardening.
        """
        job_id = self.submit(request)
        status = self.poll(job_id)
        while status.state not in ("completed", "failed"):
            _sleep(poll_interval_s)
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
# Module seams — every delay/network flow must route through these names      #
# --------------------------------------------------------------------------- #


def _sleep(seconds: float) -> None:
    """Delay seam: tests monkeypatch this instead of really waiting."""
    time.sleep(seconds)


_urlopen = urllib.request.urlopen
