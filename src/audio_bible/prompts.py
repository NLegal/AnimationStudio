"""Audio prompt templates per Phase 5 (`Audio/PromptTemplates/music-prompts.md`).

Follows the golden rules from the prompt-template bible:

1. State the category
2. Set the topic
3. Describe the vocals
4. Set the mood and key
5. Describe the melody
6. List the instrumentation
7. Set the atmosphere and duration
"""

from __future__ import annotations

from . import libraries as lib
from .models import VoiceProfile

# ---------------------------------------------------------------------------
# Base negative prompt (NegativePrompts/AUDIO_NEGATIVES.md)
# ---------------------------------------------------------------------------

AUDIO_NEGATIVE_BASE = (
    "harsh, jarring, aggressive, distorted, shrill, scary, frightening, "
    "menacing, sad, dark, loud, overwhelming, abrupt, chaotic, complex, "
    "adult content, bad quality, robotic, monotone"
)

_CATEGORY_NEGATIVES = {
    "base": AUDIO_NEGATIVE_BASE,
    "music": (
        "harsh arrangement, dissonant, atonal, aggressive drums, distorted guitar, "
        "minor-key menace, sad, scary, chaotic, loud noise, abrupt changes, "
        "off-key, out of tune, adult style"
    ),
    "voice": (
        "robotic, monotone, flat, emotionless, adult voice, gruff, harsh, nasal, "
        "whispery, garbled, mumbled, slurred, unclear pronunciation, creepy, "
        "unnatural, glitchy"
    ),
    "singing": (
        "off-key, breathy, strained, shouty, whispery, robotic, flat, "
        "no emotion, mumbling, unclear lyrics, autotune artifacts, glitchy"
    ),
    "sfx": (
        "harsh, loud, distorted, distorted noise, clipping, shrill, scary, "
        "startling, violent, metallic screech, unpleasant, jarring"
    ),
    "foley": (
        "harsh, loud, distorted, creaky, screeching, scraping, jarring, "
        "startling, mechanical noise, unpleasant"
    ),
    "ambience": (
        "loud, dominant, hissing, harsh, droning, artificial, abrupt, "
        "startling, distracting, noisy"
    ),
    "mastering": (
        "clipping, distortion, harsh highs, muddy lows, loudness war, "
        "over-compressed, digital artifacts, phase issues, shrill, boomy"
    ),
}

# Placeholder structure from the prompt-template bible:
# A [mood] preschool [category] about [topic], [vocals], [mood2] major key,
# simple repetitive melody, educational, bright instrumentation,
# [instrumentation], [atmosphere], approximately [duration].

_BASE_MUSIC_TEMPLATE = (
    "A {mood} preschool {category_hint} about {topic}, {vocals}, "
    "{mood2} major key, simple repetitive melody, educational, "
    "bright instrumentation, {instrumentation}, {atmosphere}, "
    "approximately {duration_label}."
)

MUSIC_PROMPT_TEMPLATES = {
    "Alphabet": (
        "A playful preschool alphabet song about letters and letter sounds, "
        "female lead vocal, children's choir, upbeat major key, simple repetitive "
        "melody, educational, bright instrumentation, hand claps, xylophone, piano, "
        "friendly atmosphere, approximately {duration_label}."
    ),
    "Numbers": (
        "A cheerful preschool counting song about numbers and counting, "
        "female lead vocal, children's choir, upbeat major key, simple repetitive "
        "melody, educational, bright instrumentation, hand claps, xylophone, "
        "friendly atmosphere, approximately {duration_label}."
    ),
    "Colors": (
        "A bright preschool color song about colors and color mixing, "
        "female lead vocal, children's choir, upbeat major key, simple repetitive "
        "melody, educational, bright instrumentation, xylophone, glockenspiel, "
        "friendly atmosphere, approximately {duration_label}."
    ),
    "Animals": (
        "A cheerful preschool animal song about animal sounds and friends, "
        "female lead vocal, children's choir, playful major key, simple repetitive "
        "melody, educational, bright instrumentation, hand claps, acoustic guitar, "
        "friendly atmosphere, approximately {duration_label}."
    ),
    "Bedtime": (
        "A gentle preschool lullaby about sleepy time and peaceful dreams, "
        "soft female lead vocal, gentle piano, calm major key, simple soothing "
        "melody, educational, warm instrumentation, soft piano, quiet strings, "
        "cozy atmosphere, approximately {duration_label}."
    ),
    "Dance Songs": (
        "A bouncy preschool dance song about moving and dancing, "
        "female lead vocal, children's choir, upbeat major key, simple repetitive "
        "melody, energetic but gentle, bright instrumentation, hand claps, "
        "light drums, party atmosphere, approximately {duration_label}."
    ),
    "Good Manners": (
        "A cheerful preschool good manners song about please, thank you, and "
        "sharing, female lead vocal, children's choir, upbeat major key, simple "
        "repetitive melody, educational, bright instrumentation, hand claps, "
        "ukulele, friendly atmosphere, approximately {duration_label}."
    ),
    "Interactive Learning": (
        "A playful preschool interactive learning song with call and response, "
        "female lead vocal, children's choir, upbeat major key, simple repetitive "
        "melody, educational, bright instrumentation, hand claps, xylophone, "
        "engaging atmosphere, approximately {duration_label}."
    ),
}

_DURATION_WORDS = {
    30: "thirty seconds", 60: "one minute", 120: "two minutes",
    180: "three minutes", 300: "five minutes",
}

_MOOD2 = {
    "Bedtime": "calm", "Dance Songs": "upbeat", "Family": "warm",
    "Emotions": "warm", "Nature": "sunny", "Space": "magical",
    "Ocean": "playful", "Farm": "sunny", "Weather": "playful",
    "Seasons": "cheerful", "Holiday Specials": "joyful",
    "Birthday Songs": "joyful", "Exercise": "energetic",
    "Morning Routine": "bouncy",
}

_CATEGORY_NEGATIVE_MAP = {
    "Bedtime": "music",
    "Dance Songs": "music",
    "Interactive Learning": "music",
    "Good Manners": "music",
}


def _mood_for_category(category: str, fallback: str = lib.DEFAULT_MOOD) -> str:
    lower = category.lower()
    if "dance" in lower or "exercise" in lower:
        return "bouncy"
    if "bedtime" in lower or "family" in lower or "emotion" in lower:
        return "gentle"
    return fallback


def _duration_for_label(label: str) -> int:
    for duration in lib.SONG_DURATIONS:
        if duration.label.lower() == label.lower():
            return duration.seconds
    return 120


def _category_for(category: str):
    for cat in lib.SONG_CATEGORIES:
        if cat.name.lower() == category.lower():
            return cat
    return None


def duration_word(seconds: int) -> str:
    return _DURATION_WORDS.get(seconds, f"{seconds} seconds")


def category_negative(category: str, *, include_base: bool = True) -> str:
    """Layer a per-category negative block on the base negative."""
    negative = _CATEGORY_NEGATIVES["music"]
    if category in _CATEGORY_NEGATIVE_MAP:
        negative = _CATEGORY_NEGATIVES[_CATEGORY_NEGATIVE_MAP[category]]
    if not include_base:
        return negative
    return f"{AUDIO_NEGATIVE_BASE}, {negative}"


def build_music_prompt(
    category: str,
    topic: str,
    duration_label: str = "Standard",
    vocals: str = "female lead vocal, children's choir",
    mood: str = "",
) -> str:
    """Build a bible-conformant music prompt for one song.

    Uses the placeholder convention from `Audio/PromptTemplates/`:
    A [mood] preschool [category] about [topic], [vocals], [mood2] major key, ...
    """
    duration = _duration_for_label(duration_label)
    cat = _category_for(category)
    template = MUSIC_PROMPT_TEMPLATES.get(
        category, MUSIC_PROMPT_TEMPLATES.get("Interactive Learning", "")
    )
    if template:
        return template.format(duration_label=duration_word(duration))

    mood = mood or _mood_for_category(category)
    return _BASE_MUSIC_TEMPLATE.format(
        mood=mood,
        category_hint=cat.prompt_keyword if cat else f"{category.lower()} song",
        topic=topic,
        vocals=vocals,
        mood2=_MOOD2.get(category, "upbeat"),
        instrumentation=", ".join(lib.SIGNATURE_INSTRUMENTATION[:4]),
        atmosphere="friendly atmosphere",
        duration_label=duration_word(duration),
    )


_VOICE_PROMPT_TEMPLATE = (
    "Warm preschool {role}, {pitch} pitch, {energy} energy, {pace} pace, "
    "clear pronunciation, friendly tone, {singing} singing style, "
    "{laugh} laugh, suitable for children ages 2-6."
)

_NARRATOR_PROMPT = (
    "Warm preschool narrator, calm pace, clear pronunciation, friendly tone, "
    "energetic but gentle, suitable for children ages 2-6."
)


def build_voice_prompt(profile: VoiceProfile) -> str:
    """Build a bible-conformant voice prompt from a voice profile."""
    if profile.role == "narrator":
        return _NARRATOR_PROMPT
    return _VOICE_PROMPT_TEMPLATE.format(
        role="girl voice" if profile.character == "Lily Bunny" else f"{profile.character} voice",
        pitch=profile.pitch.lower(),
        energy=profile.energy.lower(),
        pace=profile.speech_speed.lower(),
        singing=profile.singing_style.lower(),
        laugh=profile.laugh_style.lower(),
    )


def quality_checklist() -> list[str]:
    """Return the Phase 5 audio quality checklist."""
    return list(lib.QUALITY_CHECKS)
