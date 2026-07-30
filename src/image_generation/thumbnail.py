from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from PIL import Image


PLATFORM_SIZES: dict[str, tuple[int, int]] = {
    "youtube_thumbnail": (1280, 720),
    "youtube_shorts": (1080, 1920),
    "tiktok": (1080, 1920),
    "instagram_square": (1080, 1080),
    "instagram_portrait": (1080, 1350),
    "facebook": (1200, 630),
    "website_banner": (1920, 480),
    "twitter": (1200, 675),
    "pinterest": (1000, 1500),
}


@dataclass
class ThumbnailResult:
    thumbnail: Optional[Image.Image] = None
    platform: str = ""
    size: tuple[int, int] = (0, 0)
    success: bool = False
    error: str = ""


class ThumbnailGenerator:
    def generate(
        self,
        image: Image.Image,
        platform: str = "youtube_thumbnail",
    ) -> ThumbnailResult:
        if platform not in PLATFORM_SIZES:
            return ThumbnailResult(
                platform=platform,
                success=False,
                error=f"Unknown platform '{platform}'. Known: {list(PLATFORM_SIZES.keys())}",
            )

        target_size = PLATFORM_SIZES[platform]
        try:
            thumbnail = self._fit_to_size(image, target_size)
            return ThumbnailResult(
                thumbnail=thumbnail,
                platform=platform,
                size=target_size,
                success=True,
            )
        except Exception as exc:
            return ThumbnailResult(
                platform=platform,
                size=target_size,
                success=False,
                error=str(exc),
            )

    def generate_all(
        self,
        image: Image.Image,
        platforms: Optional[list[str]] = None,
    ) -> dict[str, ThumbnailResult]:
        if platforms is None:
            platforms = list(PLATFORM_SIZES.keys())
        return {p: self.generate(image, p) for p in platforms}

    def _fit_to_size(self, image: Image.Image, target: tuple[int, int]) -> Image.Image:
        img_ratio = image.width / image.height
        target_ratio = target[0] / target[1]

        if img_ratio > target_ratio:
            new_w = target[0]
            new_h = int(target[0] / img_ratio)
        else:
            new_h = target[1]
            new_w = int(target[1] * img_ratio)

        resized = image.resize((new_w, new_h), Image.LANCZOS)

        if (new_w, new_h) != target:
            result = Image.new("RGB", target, (255, 255, 255))
            x = (target[0] - new_w) // 2
            y = (target[1] - new_h) // 2
            result.paste(resized, (x, y))
            return result

        return resized
