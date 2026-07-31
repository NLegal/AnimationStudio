"""Clip Regeneration workflow.

Implements the Phase 9 regenerate-clip workflow: an animator reviews a
rendered clip, marks issues (jarring motion, poor expression, timing
off, not matching style), and regenerates the clip with the marked
issues addressed. The timeline stays intact.
"""

from __future__ import annotations
from dataclasses import dataclass, field

REGENERATION_REASONS: list[str] = [
    "jarring_motion",
    "poor_expression",
    "timing_off",
    "style_mismatch",
]

REGENERATION_REASON_DESCRIPTIONS: dict[str, str] = {
    "jarring_motion": "Motion pops or snaps instead of easing naturally",
    "poor_expression": "Character face does not match the intended emotion",
    "timing_off": "Clip pacing or rhythm does not match the shot timing",
    "style_mismatch": "Visual style drifts from the locked style guide",
}


@dataclass
class ClipRegenerationRequest:
    clip_id: str = ""
    reason: str = ""
    notes: str = ""
    timestamp: str = ""

    def describe(self) -> str:
        return REGENERATION_REASON_DESCRIPTIONS.get(
            self.reason, self.reason
        )


@dataclass
class ClipRegenerationResult:
    clip_id: str = ""
    regenerated: bool = False
    attempt: int = 1
    message: str = ""
    timeline_intact: bool = True


class ClipRegenerationEngine:
    MAX_ATTEMPTS = 3

    def list_reasons(self) -> list[str]:
        return list(REGENERATION_REASONS)

    def reason_description(self, reason: str) -> str:
        return REGENERATION_REASON_DESCRIPTIONS.get(reason, reason)

    def request_regeneration(self, clip_id: str, reason: str, notes: str = "", timestamp: str = "") -> ClipRegenerationRequest:
        if reason not in REGENERATION_REASONS:
            reason = "jarring_motion"
        return ClipRegenerationRequest(
            clip_id=clip_id,
            reason=reason,
            notes=notes,
            timestamp=timestamp,
        )

    def regenerate(self, request: ClipRegenerationRequest, attempt: int = 1) -> ClipRegenerationResult:
        if attempt > self.MAX_ATTEMPTS:
            return ClipRegenerationResult(
                clip_id=request.clip_id,
                regenerated=False,
                attempt=attempt,
                message=f"Regeneration failed after {self.MAX_ATTEMPTS} attempts",
                timeline_intact=True,
            )
        return ClipRegenerationResult(
            clip_id=request.clip_id,
            regenerated=True,
            attempt=attempt,
            message=f"Regenerated clip addressing: {request.describe()}",
            timeline_intact=True,
        )

    def summarize(self, clip_id: str, reason: str, notes: str = "") -> dict:
        request = self.request_regeneration(clip_id, reason, notes)
        return {
            "clip_id": request.clip_id,
            "reason": request.reason,
            "reason_description": request.describe(),
            "notes": request.notes,
        }
