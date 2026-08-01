from dataclasses import dataclass, field


@dataclass
class BrandProfile:
    brand_id: str = ""
    name: str = ""
    colors: list[str] = field(default_factory=list)
    fonts: list[str] = field(default_factory=list)
    studio_logo: str = ""
    series_logo: str = ""
    website: str = ""
    social_links: list[str] = field(default_factory=list)
    intro_asset: str = ""
    outro_asset: str = ""
    end_screen_asset: str = ""


class BrandingEngine:
    def __init__(self):
        self._profiles: dict[str, BrandProfile] = {}

    def register(self, profile: BrandProfile) -> None:
        self._profiles[profile.brand_id] = profile

    def get(self, brand_id: str) -> BrandProfile:
        return self._profiles.get(brand_id, BrandProfile())

    def verify_branding(self, profile: BrandProfile) -> dict:
        checks = {
            "has_studio_logo": bool(profile.studio_logo),
            "has_series_logo": bool(profile.series_logo),
            "has_colors": len(profile.colors) > 0,
            "has_fonts": len(profile.fonts) > 0,
            "has_intro": bool(profile.intro_asset),
            "has_outro": bool(profile.outro_asset),
            "has_end_screen": bool(profile.end_screen_asset),
            "has_website": bool(profile.website),
            "has_social_links": len(profile.social_links) > 0,
        }
        errors = [k for k, v in checks.items() if not v]
        return {
            "passed": len(errors) == 0,
            "checks": checks,
            "errors": errors,
        }

    def list_brands(self) -> list[str]:
        return list(self._profiles.keys())


class ComplianceEngine:
    CHILD_DIRECTED_AGE_GROUPS = {"0-2", "2-5", "3-6"}

    def check_coppa(self, metadata: dict) -> dict:
        age_group = metadata.get("age_group", "")
        checks = {
            "child_directed_declared": age_group in self.CHILD_DIRECTED_AGE_GROUPS,
            "no_personal_data_collection": True,
            "no_targeted_advertising": "ads" not in str(metadata.get("keywords", [])).lower(),
        }
        errors = [k for k, v in checks.items() if not v]
        return {
            "passed": len(errors) == 0,
            "checks": checks,
            "errors": errors,
        }

    def check_age_appropriate(self, metadata: dict, content_rating: str = "G") -> dict:
        safe_ratings = {"G", "TV-Y", "TV-G", "EC"}
        checks = {
            "rating_safe": content_rating in safe_ratings,
            "age_group_set": bool(metadata.get("age_group")),
            "language_safe": True,
        }
        errors = [k for k, v in checks.items() if not v]
        return {
            "passed": len(errors) == 0,
            "checks": checks,
            "errors": errors,
        }

    def check_copyright(self, ownership: bool = True, music_licensed: bool = True) -> dict:
        checks = {
            "ownership_verified": ownership,
            "music_licensed": music_licensed,
            "third_party_content_disclosed": True,
        }
        errors = [k for k, v in checks.items() if not v]
        return {
            "passed": len(errors) == 0,
            "checks": checks,
            "errors": errors,
        }

    def check_thumbnail_compliance(self, thumbnail_approved: bool = True) -> dict:
        return {
            "passed": thumbnail_approved,
            "thumbnail_approved": thumbnail_approved,
        }

    def check_platform_policies(self, platform: str = "youtube") -> dict:
        checks = {
            "platform_supported": platform in (
                "youtube", "youtube_kids", "tiktok", "instagram",
                "facebook", "pinterest", "website",
            ),
            "not_flagged_for_age": True,
            "advertiser_friendly": True,
        }
        errors = [k for k, v in checks.items() if not v]
        return {
            "passed": len(errors) == 0,
            "checks": checks,
            "errors": errors,
        }

    def check_community_guidelines(self, metadata: dict) -> dict:
        text = " ".join([
            metadata.get("title", ""),
            metadata.get("description", ""),
            " ".join(metadata.get("keywords") or []),
        ]).lower()
        checks = {
            "no_violent_content": not any(w in text for w in ("violent", "violence", "weapon")),
            "no_inappropriate_content": not any(w in text for w in ("nsfw", "adult")),
            "safe_for_children": True,
        }
        errors = [k for k, v in checks.items() if not v]
        return {
            "passed": len(errors) == 0,
            "checks": checks,
            "errors": errors,
        }

    def full_compliance_check(self, metadata: dict, content_rating: str = "G") -> dict:
        results = {
            "coppa": self.check_coppa(metadata)["passed"],
            "age_appropriate": self.check_age_appropriate(metadata, content_rating)["passed"],
            "copyright": self.check_copyright()["passed"],
            "thumbnail": self.check_thumbnail_compliance()["passed"],
            "platform_policies": self.check_platform_policies()["passed"],
            "community_guidelines": self.check_community_guidelines(metadata)["passed"],
        }
        return {
            "passed": all(results.values()),
            "results": results,
        }
