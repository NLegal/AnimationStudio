"""Suno backends: a strict refusal stub plus an experimental wrapper hook.

Suno has NO official public API (as of Aug 2026) — see
``.planning/research/MUSIC-GENERATION.md`` for the full research baseline
and re-decision (COVERAGE.md Surface 2). This module therefore contains
NO HTTP code whatsoever (constraints C3/C4): every operation refuses
loudly with the typed ``NotConfigured`` exception instead of degrading
silently.
"""

from .backends import NotConfigured
from .models import MusicRequest, MusicResult, MusicStatus

# LOCKED message text — Phase 7 research §4, verbatim.
SUNO_NO_API_MESSAGE = (
    "Suno has no official public API (as of Aug 2026); "
    "see .planning/research/MUSIC-GENERATION.md"
)

_EXPERIMENTAL_SUFFIX = " (experimental third-party relay — disabled by default)"


class SunoBackend:
    """Refusing stub for Suno music generation.

    Every operation raises ``NotConfigured`` citing the missing official
    public API; ``is_configured()`` is unconditionally False. Callers
    should route to another backend (ACE-Step or mock) instead.
    """

    def is_configured(self) -> bool:
        """Always False: there is no official API to configure against."""
        return False

    def submit(self, request: MusicRequest) -> str:
        """Refuse: no official public API exists."""
        raise NotConfigured(SUNO_NO_API_MESSAGE)

    def poll(self, job_id: str) -> MusicStatus:
        """Refuse: no official public API exists."""
        raise NotConfigured(SUNO_NO_API_MESSAGE)

    def download(self, job_id: str) -> bytes:
        """Refuse: no official public API exists."""
        raise NotConfigured(SUNO_NO_API_MESSAGE)

    def generate(
        self,
        request: MusicRequest,
        *,
        timeout_s: float = 300.0,
        poll_interval_s: float = 2.0,
    ) -> MusicResult:
        """Refuse identically WITHOUT constructing any request."""
        raise NotConfigured(SUNO_NO_API_MESSAGE)


class SunoWrapperBackend(SunoBackend):
    """EXPERIMENTAL third-party relay integration point — disabled by default.

    This subclass exists so that, when a third-party Suno relay/wrapper
    API eventually emerges, it has a flagged home in this package. It is
    deliberately ABSENT from the ``_BACKENDS`` registry: registry
    resolution can never yield this wrapper (COVERAGE.md Surface 2
    assumption-delta invariant). Any future enablement must be an
    explicit operator decision, never a default.

    Refusal messages carry the same locked citation as ``SunoBackend``
    plus the experimental suffix below.
    """

    EXPERIMENTAL = True

    def _refusal(self) -> str:
        return SUNO_NO_API_MESSAGE + _EXPERIMENTAL_SUFFIX

    def submit(self, request: MusicRequest) -> str:
        raise NotConfigured(self._refusal())

    def poll(self, job_id: str) -> MusicStatus:
        raise NotConfigured(self._refusal())

    def download(self, job_id: str) -> bytes:
        raise NotConfigured(self._refusal())

    def generate(
        self,
        request: MusicRequest,
        *,
        timeout_s: float = 300.0,
        poll_interval_s: float = 2.0,
    ) -> MusicResult:
        raise NotConfigured(self._refusal())
