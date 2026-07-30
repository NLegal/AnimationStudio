from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from PIL import Image


@dataclass
class UpscaleResult:
    upscaled: Optional[Image.Image] = None
    original_size: tuple[int, int] = (0, 0)
    target_size: tuple[int, int] = (0, 0)
    method: str = ""
    success: bool = False
    error: str = ""


class UpscalingPipeline:
    SUPPORTED_METHODS = {"nearest", "bilinear", "bicubic", "lanczos"}

    def upscale(
        self,
        image: Image.Image,
        scale_factor: float = 2.0,
        target_width: Optional[int] = None,
        target_height: Optional[int] = None,
        method: str = "lanczos",
        keep_original: bool = True,
    ) -> UpscaleResult:
        if method not in self.SUPPORTED_METHODS:
            return UpscaleResult(
                original_size=image.size,
                method=method,
                success=False,
                error=f"Unsupported method '{method}'. Choose from {self.SUPPORTED_METHODS}",
            )

        resample_map = {
            "nearest": Image.NEAREST,
            "bilinear": Image.BILINEAR,
            "bicubic": Image.BICUBIC,
            "lanczos": Image.LANCZOS,
        }

        orig_w, orig_h = image.size

        if target_width and target_height:
            new_w, new_h = target_width, target_height
        elif target_width:
            ratio = target_width / orig_w
            new_w, new_h = target_width, int(orig_h * ratio)
        elif target_height:
            ratio = target_height / orig_h
            new_w, new_h = int(orig_w * ratio), target_height
        else:
            new_w, new_h = int(orig_w * scale_factor), int(orig_h * scale_factor)
            target_width, target_height = new_w, new_h

        if new_w <= 0 or new_h <= 0:
            return UpscaleResult(
                original_size=image.size,
                method=method,
                success=False,
                error=f"Invalid target dimensions: {new_w}x{new_h}",
            )

        try:
            if keep_original:
                image = image.copy()

            upscaled = image.resize((new_w, new_h), resample=resample_map[method])
            return UpscaleResult(
                upscaled=upscaled,
                original_size=(orig_w, orig_h),
                target_size=(new_w, new_h),
                method=method,
                success=True,
            )
        except Exception as exc:
            return UpscaleResult(
                original_size=image.size,
                method=method,
                success=False,
                error=str(exc),
            )

    def upscale_to_4k(self, image: Image.Image, method: str = "lanczos") -> UpscaleResult:
        return self.upscale(image, target_width=3840, target_height=2160, method=method)
