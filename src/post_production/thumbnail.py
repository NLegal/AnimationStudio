from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ThumbnailCandidate:
    frame_index: int = 0
    timestamp: float = 0.0
    eye_contact_score: float = 0.0
    color_brightness: float = 0.0
    emotion_clarity: float = 0.0
    clutter_score: float = 0.0
    contrast_score: float = 0.0
    educational_relevance: float = 0.0
    total_score: float = 0.0


class ThumbnailSelector:
    WEIGHTS = {
        "eye_contact": 0.25,
        "color_brightness": 0.20,
        "emotion_clarity": 0.20,
        "contrast": 0.15,
        "educational_relevance": 0.10,
        "low_clutter": 0.10,
    }

    def evaluate_candidate(
        self,
        eye_contact: float = 0.5,
        brightness: float = 0.5,
        emotion_clarity: float = 0.5,
        contrast: float = 0.5,
        educational_relevance: float = 0.5,
        clutter: float = 0.5,
    ) -> ThumbnailCandidate:
        total = (
            eye_contact * self.WEIGHTS["eye_contact"]
            + brightness * self.WEIGHTS["color_brightness"]
            + emotion_clarity * self.WEIGHTS["emotion_clarity"]
            + contrast * self.WEIGHTS["contrast"]
            + educational_relevance * self.WEIGHTS["educational_relevance"]
            + (1.0 - clutter) * self.WEIGHTS["low_clutter"]
        )
        candidate = ThumbnailCandidate(
            eye_contact_score=eye_contact,
            color_brightness=brightness,
            emotion_clarity=emotion_clarity,
            clutter_score=clutter,
            contrast_score=contrast,
            educational_relevance=educational_relevance,
            total_score=round(total, 4),
        )
        return candidate

    def select_best(self, candidates: list[ThumbnailCandidate]) -> Optional[ThumbnailCandidate]:
        if not candidates:
            return None
        return max(candidates, key=lambda c: c.total_score)

    def rank_candidates(self, candidates: list[ThumbnailCandidate]) -> list[ThumbnailCandidate]:
        return sorted(candidates, key=lambda c: c.total_score, reverse=True)
