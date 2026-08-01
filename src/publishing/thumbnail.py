from __future__ import annotations

from .models import TitleVariant, ContentVariant


class ThumbnailStrategy:
    WEIGHTS = {
        "eye_contact": 0.25,
        "facial_expression": 0.20,
        "brightness": 0.15,
        "contrast": 0.10,
        "readability": 0.10,
        "emotion": 0.10,
        "educational_focus": 0.10,
    }

    def evaluate(
        self,
        eye_contact: float = 0.5,
        facial_expression: float = 0.5,
        brightness: float = 0.5,
        contrast: float = 0.5,
        readability: float = 0.5,
        emotion: float = 0.5,
        educational_focus: float = 0.5,
    ) -> dict:
        total = (
            eye_contact * self.WEIGHTS["eye_contact"]
            + facial_expression * self.WEIGHTS["facial_expression"]
            + brightness * self.WEIGHTS["brightness"]
            + contrast * self.WEIGHTS["contrast"]
            + readability * self.WEIGHTS["readability"]
            + emotion * self.WEIGHTS["emotion"]
            + educational_focus * self.WEIGHTS["educational_focus"]
        )
        return {
            "eye_contact": eye_contact,
            "facial_expression": facial_expression,
            "brightness": brightness,
            "contrast": contrast,
            "readability": readability,
            "emotion": emotion,
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
        "facebook_clip": {"platform": "facebook", "duration_scale": 0.25, "resolution": "1920x1080"},
        "trailer": {"platform": "youtube", "duration_scale": 0.3, "resolution": "1920x1080"},
        "teaser": {"platform": "all", "duration_scale": 0.1, "resolution": "1920x1080"},
        "bts": {"platform": "all", "duration_scale": 0.2, "resolution": "1920x1080"},
        "thumbnail": {"platform": "all", "duration_scale": 0.01, "resolution": "1280x720"},
        "gif": {"platform": "all", "duration_scale": 0.05, "resolution": "480x270"},
        "preview": {"platform": "all", "duration_scale": 0.03, "resolution": "640x360"},
        "newsletter": {"platform": "email", "duration_scale": 0.02, "resolution": "1200x630"},
        "website": {"platform": "website", "duration_scale": 0.02, "resolution": "1920x1080"},
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
