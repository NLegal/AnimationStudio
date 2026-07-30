from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from PIL import Image

from .metadata import ImageMetadata


@dataclass
class ValidationResult:
    passed: bool = False
    checks: dict[str, bool] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def summary(self) -> str:
        total = len(self.checks)
        passed_count = sum(1 for v in self.checks.values() if v)
        if not total:
            return "No checks performed"
        return f"{passed_count}/{total} checks passed"

    def failed_checks(self) -> list[str]:
        return [k for k, v in self.checks.items() if not v]


class ImageValidator:
    MIN_DIMENSION = 64
    MAX_DIMENSION = 8192
    ALLOWED_FORMATS = {"PNG", "JPEG", "WEBP"}
    MIN_FILE_SIZE = 1024
    MAX_FILE_SIZE = 50 * 1024 * 1024

    def validate_format(self, image: Image.Image) -> bool:
        return image.mode in {"RGB", "RGBA"}

    def validate_dimensions(self, image: Image.Image) -> bool:
        w, h = image.size
        return (self.MIN_DIMENSION <= w <= self.MAX_DIMENSION and
                self.MIN_DIMENSION <= h <= self.MAX_DIMENSION)

    def validate_aspect_ratio(self, image: Image.Image) -> bool:
        w, h = image.size
        if h == 0:
            return False
        ratio = max(w, h) / min(w, h) if min(w, h) > 0 else 0
        return ratio <= 4.0

    def validate_resolution_standard(self, image: Image.Image) -> bool:
        VALID_SIZES = {
            (1024, 1024), (1536, 1536), (2048, 2048),
            (1280, 720), (1920, 1080), (1080, 1920),
        }
        return image.size in VALID_SIZES or (image.size[0] >= 1024 and image.size[1] >= 1024)

    def validate_metadata(self, metadata: ImageMetadata) -> ValidationResult:
        checks = {
            "has_image_id": bool(metadata.image_id),
            "has_model": bool(metadata.model),
            "has_generation_date": bool(metadata.generation_date),
            "has_valid_dimensions": (metadata.width > 0 and metadata.height > 0),
            "has_seed": True,
            "has_prompt_version": bool(metadata.prompt_version),
        }
        errors = []
        for key, passed in checks.items():
            if not passed:
                errors.append(f"Missing or invalid: {key}")
        return ValidationResult(
            passed=len(errors) == 0,
            checks=checks,
            errors=errors,
        )

    def validate_image(self, image: Image.Image, metadata: Optional[ImageMetadata] = None) -> ValidationResult:
        checks = {
            "format": self.validate_format(image),
            "dimensions": self.validate_dimensions(image),
            "aspect_ratio": self.validate_aspect_ratio(image),
            "resolution_standard": self.validate_resolution_standard(image),
        }

        if metadata:
            meta_result = self.validate_metadata(metadata)
            checks.update(meta_result.checks)
            if meta_result.errors:
                checks["metadata_complete"] = False
            else:
                checks["metadata_complete"] = True

        errors = [k for k, v in checks.items() if not v]
        return ValidationResult(
            passed=len(errors) == 0,
            checks=checks,
            errors=errors,
        )
