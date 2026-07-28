"""Standardized negative prompt definitions per PHASE1.md and CHAR-08.

Provides reusable negative prompt components and a composition function
that assembles common negatives with optional custom additions.
"""

COMMON_NEGATIVE = (
    "low quality, blurry, deformed, mutated, duplicate, extra arms, extra legs, "
    "extra fingers, missing fingers, cross eyed, cropped, watermark, text, logo, "
    "dark, scary, horror, realistic skin, adult, violence, blood, ugly, noise"
)


STYLE_NEGATIVE = (
    "anime, watercolor, 3D render, photorealistic, sketch, line art, "
    "black and white, grayscale, sepia, low contrast, oversaturated"
)


def build_negative_prompt(*, custom: str = "") -> str:
    """Build a composite negative prompt from reusable components.

    Args:
        custom: Optional custom negative terms to append.

    Returns:
        Comma-separated negative prompt string.
    """
    parts = [COMMON_NEGATIVE, STYLE_NEGATIVE]
    if custom:
        parts.append(custom)
    return ", ".join(parts)
