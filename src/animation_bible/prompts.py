"""Animation prompt templates per Phase 4 (`Animation/PromptTemplates/`).

Follows the golden rules from the prompt-template bible:

1. Start with the character
2. Describe the action clearly
3. Set the emotional tone
4. Specify the environment
5. Add camera direction
6. Close with style qualifiers
7. Loop animations where appropriate
"""

from __future__ import annotations

from . import libraries as lib

# ---------------------------------------------------------------------------
# Base negative prompt (PHASE4.md + animation-negatives.md)
# ---------------------------------------------------------------------------

ANIMATION_NEGATIVE_BASE = (
    "violent motion, camera shake, fast cuts, stiff movement, "
    "robotic animation, jerky motion, limb distortion, "
    "unnatural physics, aggressive expressions, horror, "
    "dark lighting, glitches, low quality, text, watermark"
)

_STYLE_TAGS = (
    "Cocomelon-inspired, Pixar-quality, smooth preschool animation, "
    "consistent character motion, child-friendly, high-quality animation"
)

_QUALITY_TAGS = "soft rounded motion, stable camera, natural blinking"

_CATEGORY_NEGATIVES = {
    "base": ANIMATION_NEGATIVE_BASE,
    "walk_run": (
        "limping, sliding, moonwalk, floating, foot skating, "
        "uneven gait, dragging foot, sliding feet, clipping through floor"
    ),
    "dance": (
        "jerky, off-beat, uncoordinated, flailing, wild movement, "
        "erratic, off-rhythm, out of sync, robotic dance"
    ),
    "facial": (
        "frozen, twitching, asymmetric, drooping, lopsided, "
        "dead eyes, blank stare, expressionless, doll-like, "
        "mask-like, uncanny valley"
    ),
    "interaction": (
        "floating objects, wrong hand, wrong position, "
        "clipping into object, object passing through hand, "
        "misaligned hands, hovering item"
    ),
    "jump": (
        "weightless, floating forever, stiff landing, no anticipation, "
        "moonwalking, skating on ground"
    ),
    "singing": (
        "frozen jaw, mismatched lip sync, moving mouth wrong, "
        "off-sync singing, no expression, emotional mismatch"
    ),
}

# Placeholder structure from the prompt-template bible:
# [character] [action] [emotion], [detail...], [environment],
# [camera style], [style tags], [quality tags]

_BASE_STRUCTURE = (
    "{character} {action} {emotion}, {details}{environment}, {camera_style}, "
    "{style_tags}, {quality_tags}"
)

# Per-motion templates following the doc examples.
MOTION_PROMPT_TEMPLATES = {
    "idle": "{character} stands relaxed with gentle breathing, {emotion}, natural blinking, subtle weight shifts, ears and tail softly moving, {details}{environment}, {camera_style}, {style_tags}, {quality_tags}",
    "walk": "{character} walks forward at a comfortable pace, {emotion}, gentle arm swing, natural blinking, subtle breathing, {details}{environment}, {camera_style}, smooth preschool walk cycle, {style_tags}, {quality_tags}",
    "run": "{character} runs forward playfully, {emotion}, bouncing step, arms pumping, natural blinking, {details}{environment}, {camera_style}, smooth preschool run cycle, {style_tags}, {quality_tags}",
    "jump": "{character} jumps with a crouch, spring, and soft landing, {emotion}, {details}{environment}, {camera_style}, {style_tags}, {quality_tags}",
    "dance": "{character} dances happily in rhythm, {emotion}, bouncy steps, arms swinging to the beat, {details}{environment}, {camera_style}, seamless dance loop, {style_tags}, {quality_tags}",
    "wave": "{character} waves hello with a friendly open palm, {emotion}, wrist rotating side to side, {details}{environment}, {camera_style}, {style_tags}, {quality_tags}",
    "clap": "{character} claps hands together cheerfully, {emotion}, slight body bounce, {details}{environment}, {camera_style}, {style_tags}, {quality_tags}",
    "hug": "{character} hugs warmly, arms wrapping around, {emotion}, soft eyes, {details}{environment}, {camera_style}, {style_tags}, {quality_tags}",
    "sleep": "{character} sleeps peacefully, {emotion}, gentle rhythmic breathing, soft rise and fall of chest, {details}{environment}, {camera_style}, {style_tags}, {quality_tags}",
    "read": "{character} reads a book quietly, {emotion}, eyes tracking the page, slow head movement, {details}{environment}, {camera_style}, {style_tags}, {quality_tags}",
    "celebrate": "{character} celebrates joyfully, {emotion}, arms raised, happy bouncing, {details}{environment}, {camera_style}, {style_tags}, {quality_tags}",
}

_CAMERA_STYLE_DESCRIPTORS = {
    "establishing": "wide establishing shot, slow gentle pan",
    "wide": "wide shot, gentle tracking",
    "medium": "medium shot, steady and locked off",
    "close_up": "close-up, static camera",
    "over_shoulder": "over-the-shoulder shot, static",
    "tracking": "gentle tracking shot",
    "slow_push_in": "slow push-in, smooth and steady",
    "gentle_pan": "gentle pan",
    "gentle_tilt": "gentle tilt",
    "two_shot": "two-shot, balanced framing",
    "group_shot": "group shot, all faces visible",
    "insert_shot": "insert shot of the object",
}

_EMOTION_WORDS = {
    "happiness": "happily", "excitement": "excitedly", "curiosity": "curiously",
    "surprise": "with surprise", "confusion": "with a puzzled look",
    "pride": "proudly", "love": "lovingly", "sleepiness": "sleepily",
    "sadness": "gently", "fear": "timidly", "anger": "with a mild frown",
    "disgust": "with a small grimace", "embarrassment": "shyly",
    "neutral": "calmly",
}


def emotion_word(expression: str) -> str:
    return _EMOTION_WORDS.get(expression, "happily")


def camera_style_descriptor(camera_shot: str) -> str:
    return _CAMERA_STYLE_DESCRIPTORS.get(camera_shot, "medium shot, steady and locked off")


def category_negative(category: str, *, include_base: bool = True) -> str:
    """Layer a per-animation-type negative block on the base negative."""
    if category not in _CATEGORY_NEGATIVES:
        return ANIMATION_NEGATIVE_BASE
    if not include_base:
        return _CATEGORY_NEGATIVES[category]
    return f"{ANIMATION_NEGATIVE_BASE}, {_CATEGORY_NEGATIVES[category]}"


def build_animation_prompt(
    character: str,
    action: str,
    emotion: str = "happiness",
    environment: str = "",
    camera_shot: str = "medium",
    prop: str = "",
    details: tuple[str, ...] = (),
    style_tags: str = _STYLE_TAGS,
    quality_tags: str = _QUALITY_TAGS,
    template: str = "walk",
) -> str:
    """Build a bible-conformant animation prompt for one shot.

    Uses the placeholder convention from `Animation/PromptTemplates/`:
    [character] [action] [emotion], [details], [environment],
    [camera style], [style tags], [quality tags].
    """
    action = action.strip()
    if action == "walk":
        action = "walks forward at a comfortable pace"
    elif action == "run":
        action = "runs forward playfully"
    elif action == "idle":
        action = "stands relaxed"

    details_list = list(details)
    if prop:
        details_list.append(f"with the {prop}")
    details_str = ", ".join(d for d in details_list if d)
    if details_str:
        details_str += ", "

    env = f"{environment}, " if environment else ""
    camera = camera_style_descriptor(camera_shot)

    if template in MOTION_PROMPT_TEMPLATES:
        return MOTION_PROMPT_TEMPLATES[template].format(
            character=character,
            action=action,
            emotion=emotion_word(emotion),
            details=details_str,
            environment=env,
            camera_style=camera,
            style_tags=style_tags,
            quality_tags=quality_tags,
        )

    return _BASE_STRUCTURE.format(
        character=character,
        action=action,
        emotion=emotion_word(emotion),
        details=details_str,
        environment=env,
        camera_style=camera,
        style_tags=style_tags,
        quality_tags=quality_tags,
    )


def quality_checklist() -> list[str]:
    """Return the Phase 4 animation quality checklist."""
    return list(lib.QUALITY_CHECKS)
