from __future__ import annotations

from .models import TitleVariant, ContentVariant


class ThumbnailStrategy:
    WEIGHTS = {
        "eye_contact": 0.25,
        "facial_expression": 0.20,
        "brightness": 0.15,
        "contrast": 0.15,
        "readability": 0.15,
        "educational_focus": 0.10,
    }

    def evaluate(
        self,
        eye_contact: float = 0.5,
        facial_expression: float = 0.5,
        brightness: float = 0.5,
        contrast: float = 0.5,
        readability: float = 0.5,
        educational_focus: float = 0.5,
    ) -> dict:
        total = (
            eye_contact * self.WEIGHTS["eye_contact"]
            + facial_expression * self.WEIGHTS["facial_expression"]
            + brightness * self.WEIGHTS["brightness"]
            + contrast * self.WEIGHTS["contrast"]
            + readability * self.WEIGHTS["readability"]
            + educational_focus * self.WEIGHTS["educational_focus"]
        )
        return {
            "eye_contact": eye_contact,
            "facial_expression": facial_expression,
            "brightness": brightness,
            "contrast": contrast,
            "readability": readability,
            "educational_focus": educational_focus,
            "total_score": round(total, 4),
        }

    def select_best(self, candidates: list[dict]) -> dict | None:
        if not candidates:
            return None
        return max(candidates, key=lambda c: c["total_score"])


class ContentVariantEngine:
    VARIANT_SPECS = {
        "full": {"platform": "youtube", "duration_scale": 1.0, "resolution": "1920x1080"},
        "shorts": {"platform": "youtube_shorts", "duration_scale": 0.15, "resolution": "1080x1920"},
        "tiktok": {"platform": "tiktok", "duration_scale": 0.15, "resolution": "1080x1920"},
        "reel": {"platform": "instagram_reels", "duration_scale": 0.15, "resolution": "1080x1920"},
        "trailer": {"platform": "youtube", "duration_scale": 0.3, "resolution": "1920x1080"},
        "teaser": {"platform": "all", "duration_scale": 0.1, "resolution": "1920x1080"},
        "gif": {"platform": "all", "duration_scale": 0.05, "resolution": "480x270"},
    }

    def plan_variants(self, episode_id: str, duration: float) -> list[ContentVariant]:
        variants: list[ContentVariant] = []
        for kind, spec in self.VARIANT_SPECS.items():
            variants.append(ContentVariant(
                variant_id=f"{episode_id}_{kind}",
                episode_id=episode_id,
                kind=kind,
                platform=spec["platform"],
                duration=round(duration * spec["duration_scale"], 2),
                resolution=spec["resolution"],
            ))
        return variants

    def plan_variant(self, episode_id: str, duration: float, kind: str) -> ContentVariant | None:
        spec = self.VARIANT_SPECS.get(kind)
        if spec is None:
            return None
        return ContentVariant(
            variant_id=f"{episode_id}_{kind}",
            episode_id=episode_id,
            kind=kind,
            platform=spec["platform"],
            duration=round(duration * spec["duration_scale"], 2),
            resolution=spec["resolution"],
        )

    def list_variant_kinds(self) -> list[str]:
        return list(self.VARIANT_SPECS.keys())
