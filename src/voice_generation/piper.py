"""Piper backend — a strict refusal stub (GPL license gate).

Piper (the original ``rhasspy/piper`` repo is archived; the maintained fork
ships as ``piper1-gpl``) is the phase's offline engine, but it is GPL-3.0
licensed. STACK.md marks GPL software "edge", and exporting GPL-based TTS
inside a commercial nursery product requires a clean-room licensing review
that has not happened. This module therefore contains NO synthesis code:
every operation refuses loudly with the typed ``NotConfigured`` exception
instead of degrading silently (mirrors ``suno.py``).
"""

from .backends import NotConfigured
from .models import VoiceRequest, VoiceResult, VoiceStatus

# LOCKED gate message — cite, do not paraphrase.
PIPER_NO_API_MESSAGE = (
    "Piper is GPL-3.0 and flagged 'edge' in STACK.md; the maintained fork "
    "ships as `piper1-gpl`. GPL-based TTS export needs a clean-room "
    "licensing review — use Kokoro or the mock — see STACK.md and "
    ".planning/research"
)


class PiperBackend:
    """Refusing stub for the Piper offline TTS engine.

    Every operation raises ``NotConfigured`` citing the GPL licensing gate;
    ``is_configured()`` is unconditionally False. Route to Kokoro or the
    mock instead.
    """

    def is_configured(self) -> bool:
        """Always False: the GPL export gate is not lifted."""
        return False

    def submit(self, request: VoiceRequest) -> str:
        """Refuse: GPL export gate."""
        raise NotConfigured(PIPER_NO_API_MESSAGE)

    def poll(self, job_id: str) -> VoiceStatus:
        """Refuse: GPL export gate."""
        raise NotConfigured(PIPER_NO_API_MESSAGE)

    def download(self, job_id: str) -> bytes:
        """Refuse: GPL export gate."""
        raise NotConfigured(PIPER_NO_API_MESSAGE)

    def generate(
        self,
        request: VoiceRequest,
        *,
        timeout_s: float = 300.0,
        poll_interval_s: float = 1.0,
    ) -> VoiceResult:
        """Refuse identically WITHOUT constructing any request."""
        raise NotConfigured(PIPER_NO_API_MESSAGE)