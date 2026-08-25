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
from typing import Protocol, runtime_checkable

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
# Module seams — every delay/network flow must route through these names      #
# --------------------------------------------------------------------------- #


def _sleep(seconds: float) -> None:
    """Delay seam: tests monkeypatch this instead of really waiting."""
    time.sleep(seconds)


_urlopen = urllib.request.urlopen
