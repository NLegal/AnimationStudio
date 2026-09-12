"""XTTS v2 backend — a strict refusal stub (R&D-only license gate).

XTTS v2 (Coqui) is the phase's character engine (``CHARACTER_ENGINE`` ==
"XTTS v2"). Its CPML license restricts use to non-commercial research and
development, which conflicts with shipping the nursery content pipeline,
and the ~1.2 GB GPU-resident model is out of reach of the current CPU-only
build. This module therefore contains NO synthesis code: every operation
refuses loudly with the typed ``NotConfigured`` exception instead of
degrading silently (mirrors ``suno.py``).
"""

from .backends import NotConfigured
from .models import VoiceRequest, VoiceResult, VoiceStatus

# LOCKED gate message — cite, do not paraphrase.
XTTS_NO_API_MESSAGE = (
    "XTTS v2 is CPML-licensed (R&D-only) and needs ~1.2 GB + GPU; STACK.md "
    "restricts commercial use. Use Kokoro or the mock — see STACK.md and "
    ".planning/research"
)


class XttsBackend:
    """Refusing stub for the XTTS v2 voice engine.

    Every operation raises ``NotConfigured`` citing the CPML license gate;
    ``is_configured()`` is unconditionally False. Route to Kokoro or the
    mock instead.
    """

    def is_configured(self) -> bool:
        """Always False: the R&D-only license gate is fixed."""
        return False

    def submit(self, request: VoiceRequest) -> str:
        """Refuse: CPML R&D-only license gate."""
        raise NotConfigured(XTTS_NO_API_MESSAGE)

    def poll(self, job_id: str) -> VoiceStatus:
        """Refuse: CPML R&D-only license gate."""
        raise NotConfigured(XTTS_NO_API_MESSAGE)

    def download(self, job_id: str) -> bytes:
        """Refuse: CPML R&D-only license gate."""
        raise NotConfigured(XTTS_NO_API_MESSAGE)

    def generate(
        self,
        request: VoiceRequest,
        *,
        timeout_s: float = 300.0,
        poll_interval_s: float = 1.0,
    ) -> VoiceResult:
        """Refuse identically WITHOUT constructing any request."""
        raise NotConfigured(XTTS_NO_API_MESSAGE)