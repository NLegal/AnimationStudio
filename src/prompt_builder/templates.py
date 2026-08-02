"""Character-specific prompt templates per CHAR-8.

Provides parameterized prompt templates for reference sheets, expressions,
poses, and outfits, plus age variants, rotation/lighting templates, and
per-character override support. Never hand-write prompts — always use these
templates.
"""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Age variant descriptors
# ---------------------------------------------------------------------------

_AGE_DESCRIPTORS: dict[str, str] = {
    "toddler": "toddler version, smaller, rounder features, 2-3 years old",
    "preschool": "preschool age, 4-5 years old",
    "kindergarten": "kindergarten age, 5-6 years old",
}

# ---------------------------------------------------------------------------
# Environment / world variant descriptors (PHASE2.md)
# ---------------------------------------------------------------------------

_ENVIRONMENT_STYLE = (
    "Pixar-quality, Cocomelon-inspired, bright colorful nursery world, "
    "rounded architecture, soft pastel colors, consistent world design, "
    "highly detailed, cinematic lighting, child-safe, vibrant, masterpiece, 8k"
)

_ENVIRONMENT_VIEWS: dict[str, str] = {
    "front": "front view of the exterior",
    "back": "back view of the exterior",
    "garage": "garage exterior view",
    "garden": "garden view",
    "mailbox": "mailbox and front yard view",
    "driveway": "driveway view",
    "top": "top view of the location",
}

_INTERIOR_SETS: dict[str, str] = {
    "living_room": "cozy living room interior",
    "kitchen": "bright kitchen interior",
    "dining_room": "cheerful dining room interior",
    "bathroom": "clean bathroom interior",
    "bedroom": "cozy bedroom interior",
    "childrens_bedroom": "playful children's bedroom interior",
    "hallway": "bright hallway interior",
    "laundry": "laundry room interior",
    "attic": "cozy attic interior",
    "basement": "warm finished basement interior",
    "backyard": "backyard interior-facing view",
    "classroom": "bright classroom interior",
    "music_room": "music room interior",
    "art_room": "art room interior",
    "gym": "playful gym interior",
    "playground": "school playground",
    "lunch_room": "lunch room interior",
    "science_room": "science room interior",
    "library": "warm library interior",
    "principal_office": "friendly principal's office interior",
    "nurse_office": "cozy nurse's office interior",
    "garden": "school garden",
    "hallway_school": "bright school hallway interior",
    "lobby": "welcoming lobby interior",
    "default_interior": "bright child-friendly interior",
}

_SEASON_DESCRIPTORS: dict[str, str] = {
    "spring": "spring, cherry blossoms and blooming flowers",
    "summer": "summer, lush green trees and bright sunshine",
    "autumn": "autumn, golden and orange leaves",
    "winter": "winter, snow-capped rooftops and cozy warm windows",
    "holiday": "festive holiday decorations, string lights and wreaths",
    "halloween": "gentle Halloween decorations, friendly pumpkins, soft night",
    "christmas": "Christmas decorations, colorful lights, decorated tree",
    "new_year": "New Year decorations, confetti and sparkling lights",
    "easter": "Easter decorations, pastel eggs and spring flowers",
    "birthday": "birthday decorations, balloons and bunting",
}

_TIME_DESCRIPTORS: dict[str, str] = {
    "morning": "bright morning light, fresh and cheerful",
    "sunrise": "sunrise, soft pink and gold sky",
    "noon": "noon, bright even daylight",
    "afternoon": "warm afternoon light",
    "golden_hour": "golden hour, warm honey light, long soft shadows",
    "sunset": "sunset, orange and purple sky",
    "evening": "gentle evening light, lamps beginning to glow",
    "night": "night time, starry sky, warm glowing windows and street lamps",
    "moonlight": "moonlit scene, soft silver-blue light, gentle stars",
}

_WEATHER_DESCRIPTORS: dict[str, str] = {
    "sunny": "bright sunny day, clear blue sky",
    "cloudy": "soft overcast sky, gentle clouds",
    "rain": "gentle rain, rainbow-colored umbrellas, puddles to splash",
    "snow": "soft fluffy snow, snow-capped rooftops",
    "fog": "soft morning fog, friendly and dreamy",
    "wind": "gentle breeze, leaves drifting, kites in the sky",
    "rainbow": "a rainbow arching over the scene",
    "light_storm": "gentle storm, soft distant lightning, warm cozy feeling",
}

_CAMERA_DESCRIPTORS: dict[str, str] = {
    "wide": "wide establishing shot",
    "ultra_wide": "ultra-wide establishing shot",
    "medium": "medium shot",
    "close": "close-up",
    "extreme_close": "extreme close-up detail",
    "overhead": "overhead view",
    "birds_eye": "bird's eye view",
    "ground_level": "ground-level view",
    "tracking": "tracking shot",
    "walking_follow": "walking follow shot",
    "front": "front view",
    "side": "side view",
    "rear": "rear view",
    "low_angle": "low angle shot",
    "high_angle": "high angle shot",
    "top": "top view",
}

_LIGHTING_DESCRIPTORS: dict[str, str] = {
    "artificial": "warm indoor artificial lighting",
    "studio": "soft even studio lighting",
    "natural": "natural daylight",
}

# ---------------------------------------------------------------------------
#  Prop / asset variant descriptors (PHASE3.md)
# ---------------------------------------------------------------------------

_PROP_STYLE = (
    "Pixar-quality, Cocomelon-inspired, bright colorful nursery world, "
    "rounded edges, chunky child-safe proportions, soft shadows, "
    "highly detailed, consistent asset style, single object, product shot, "
    "clean background, no text, no logo, no watermark, masterpiece, 8k"
)

_PROP_VIEWS: dict[str, str] = {
    "front": "front view",
    "side": "side view",
    "back": "back view",
    "top": "top view",
    "three_quarter": "three-quarter view",
    "bottom": "bottom view",
}

_PROP_MATERIALS: dict[str, str] = {
    "wood": "warm oak wood finish, visible grain",
    "plastic": "smooth glossy plastic finish, primary color",
    "metal": "smooth brushed metal finish, rounded edges",
    "fabric": "soft plush fabric finish, cozy texture",
    "rubber": "soft matte rubber finish, flexible look",
    "glass": "clear rounded glass, safe smooth edges",
    "paper": "thick cardstock paper finish, matte surface",
    "cardboard": "sturdy cardboard finish, warm brown",
    "ceramic": "smooth glazed ceramic finish, glossy",
    "stone": "smooth polished stone finish, rounded",
    "foam": "soft foam finish, squishy safe texture",
}

_PROP_COLOR_VARIANTS: dict[str, str] = {
    "pastel_blue": "pastel blue",
    "pastel_pink": "pastel pink",
    "pastel_yellow": "pastel yellow",
    "pastel_green": "pastel green",
    "lavender": "lavender purple",
    "peach": "soft peach",
    "mint": "soft mint green",
    "coral": "coral orange",
    "teal": "teal",
    "sky_blue": "sky blue",
    "sunny_yellow": "sunny yellow",
    "blush_pink": "blush pink",
    "warm_red": "warm red",
    "leaf_green": "leaf green",
    "chocolate": "chocolate brown",
    "cream": "cream white",
}


@dataclass
class PropPrompt:
    """Reusable prop/asset data used to parameterize prop templates.

    Covers the Phase 3 asset library: toys, food, furniture, nature, holiday
    and educational props, plus materials and textures.
    """

    name: str
    description: str = ""
    colors: str = ""
    material: str = ""
    category: str = ""
    style: str = _PROP_STYLE
    custom_tags: str = ""


@dataclass
class EnvironmentPrompt:
    """World/environment data used to parameterize environment templates.

    Covers named locations (Phase 2), vehicles, and background layers.
    """

    name: str
    description: str = ""
    style: str = _ENVIRONMENT_STYLE
    custom_tags: str = ""


@dataclass
class CharacterPrompt:
    """Character data used to parameterize prompt templates.

    Extended with optional fields for age variant and custom prompt tags.
    """

    name: str
    species: str
    appearance: str = ""
    outfit: str = ""
    style: str = "Pixar-quality, Cocomelon-inspired, bright colorful nursery world"
    age: str = "preschool"
    custom_tags: str = ""


class PromptTemplates:
    """Template methods for character asset prompts.

    Base methods (reference_sheet, expression, pose, outfit) are static and
    accept a ``CharacterPrompt``.  Extended methods (age_variant, rotation,
    lighting) are instance methods that also accept an optional override dict.

    Usage::

        templates = PromptTemplates(overrides={"reference": ...})
        prompt = templates.reference_sheet(character, angle="front")
    """

    def __init__(
        self,
        overrides: Optional[dict[str, str]] = None,
    ):
        """Store per-character template overrides.

        Args:
            overrides: Mapping of ``{asset_type: template_string}`` where
                ``{name}``, ``{species}`` etc. are substituted at build time.
        """
        self._overrides = overrides or {}

    # ------------------------------------------------------------------ #
    #  Base static templates
    # ------------------------------------------------------------------ #

    @staticmethod
    def reference_sheet(character: CharacterPrompt, angle: str = "front") -> str:
        """Build a reference sheet prompt for the given character and camera angle."""
        return (
            f"{character.name}, {character.species}, {character.appearance}, "
            f"wearing {character.outfit}, {angle} view, "
            f"{character.style}, highly detailed, cinematic lighting, "
            f"consistent character, masterpiece, 8k, child-friendly"
        )

    @staticmethod
    def expression(character: CharacterPrompt, expression: str) -> str:
        """Build a prompt for a specific character expression."""
        return (
            f"{character.name}, {character.species}, {character.appearance}, "
            f"wearing {character.outfit}, {expression} expression, "
            f"{character.style}, portrait, highly detailed"
        )

    @staticmethod
    def pose(character: CharacterPrompt, pose: str) -> str:
        """Build a prompt for a specific character pose."""
        return (
            f"{character.name}, {character.species}, {character.appearance}, "
            f"wearing {character.outfit}, {pose} pose, "
            f"{character.style}, full body, highly detailed"
        )

    @staticmethod
    def outfit(character: CharacterPrompt, outfit: str) -> str:
        """Build a prompt for a specific outfit variant."""
        return (
            f"{character.name}, {character.species}, {character.appearance}, "
            f"wearing {outfit}, standing, front view, "
            f"{character.style}, highly detailed, full body"
        )

    # ------------------------------------------------------------------ #
    #  Environment / world templates (Phase 2)
    # ------------------------------------------------------------------ #

    @staticmethod
    def environment(
        env: "EnvironmentPrompt",
        view: str = "front",
        season: Optional[str] = None,
        time_of_day: Optional[str] = None,
        weather: Optional[str] = None,
        camera: Optional[str] = None,
        lighting: Optional[str] = None,
        set_name: Optional[str] = None,
    ) -> str:
        """Build an environment reference prompt with optional variant dims.

        The four variant dimensions (season / time-of-day / weather / camera)
        and lighting are additive — any subset may be supplied.  ``set_name``
        switches the prompt to a named interior set.
        """
        parts = [f"Little Learning Town, {env.name}"]
        if set_name:
            room = _INTERIOR_SETS.get(set_name, set_name.replace("_", " "))
            parts.append(room)
        elif view:
            parts.append(_ENVIRONMENT_VIEWS.get(view, f"{view.replace('_', ' ')} view"))
        if env.description:
            parts.append(env.description[:400])
        for label, table in (
            ("season", _SEASON_DESCRIPTORS),
            ("time_of_day", _TIME_DESCRIPTORS),
            ("weather", _WEATHER_DESCRIPTORS),
            ("camera", _CAMERA_DESCRIPTORS),
            ("lighting", _LIGHTING_DESCRIPTORS),
        ):
            value = {"season": season, "time_of_day": time_of_day,
                     "weather": weather, "camera": camera,
                     "lighting": lighting}.get(label)
            if value:
                parts.append(table.get(value, value.replace("_", " ")))
        parts.append(env.style)
        if env.custom_tags:
            parts.append(env.custom_tags)
        return ", ".join(parts)

    @staticmethod
    def vehicle(vehicle: "EnvironmentPrompt", view: str = "side") -> str:
        """Build a vehicle reference prompt."""
        parts = [
            f"Little Learning Town, {vehicle.name}",
            _CAMERA_DESCRIPTORS.get(view, f"{view.replace('_', ' ')} view"),
        ]
        if vehicle.description:
            parts.append(vehicle.description[:400])
        parts.append(
            "friendly rounded vehicle, smiling front grille, oversized windows, "
            "no text, no logos, "
        )
        parts.append(vehicle.style)
        parts.append("single vehicle, clean background, product shot")
        return ", ".join(parts)

    @staticmethod
    def background(bg: "EnvironmentPrompt", layer: str = "sky") -> str:
        """Build a reusable background layer prompt."""
        parts = [
            f"Little Learning Town, {bg.name}",
            f"{layer.replace('_', ' ')} background layer",
        ]
        if bg.description:
            parts.append(bg.description[:400])
        parts.append(
            "seamless modular background, no text, no logos, no people, "
            "soft gradients, clean and bright, "
        )
        parts.append(bg.style)
        return ", ".join(parts)

    # ------------------------------------------------------------------ #
    #  Prop / asset templates (Phase 3)
    # ------------------------------------------------------------------ #

    @staticmethod
    def prop(
        prop: "PropPrompt",
        view: Optional[str] = None,
        material: Optional[str] = None,
        color: Optional[str] = None,
        lighting: Optional[str] = None,
    ) -> str:
        """Build a reusable prop prompt with optional variant dims.

        ``view`` switches the camera angle (default ``front``), ``material``
        swaps the finish, ``color`` applies an alternate palette, and
        ``lighting`` adds a lighting study.  Any subset may be supplied.
        """
        parts = [f"{prop.name}"]
        if prop.category:
            parts.append(f"child-friendly {prop.category} prop")
        if view:
            parts.append(_PROP_VIEWS.get(view, f"{view.replace('_', ' ')} view"))
        details: list[str] = []
        if material:
            details.append(
                _PROP_MATERIALS.get(material, f"{material.replace('_', ' ')} finish")
            )
        if color:
            details.append(
                _PROP_COLOR_VARIANTS.get(color, color.replace("_", " "))
            )
        if prop.material:
            details.append(prop.material[:120])
        if prop.description:
            details.append(prop.description[:400])
        if prop.colors:
            details.append(prop.colors[:120])
        if lighting:
            details.append(_LIGHTING_DESCRIPTORS.get(lighting, f"{lighting} lighting"))
        if details:
            parts.append(", ".join(details))
        parts.append(prop.style)
        if prop.custom_tags:
            parts.append(prop.custom_tags)
        return ", ".join(parts)

    # ------------------------------------------------------------------ #
    #  Extended templates (age, rotation, lighting)
    # ------------------------------------------------------------------ #

    def age_variant(self, character: CharacterPrompt, age: str) -> str:
        """Prepend an age descriptor to the character's base reference prompt.

        Args:
            character: The character to describe.
            age: One of ``"toddler"``, ``"preschool"``, or ``"kindergarten"``.

        Returns:
            Prompt string with the age descriptor prepended.
        """
        descriptor = _AGE_DESCRIPTORS.get(age, f"{age} age")
        base = self.reference_sheet(character)
        return f"{descriptor}, {base}"

    def rotation(self, character: CharacterPrompt, angle: str) -> str:
        """Build a prompt for a rotation / turnaround image.

        Args:
            character: The character to describe.
            angle: Camera angle (e.g. ``"front"``, ``"3/4"``, ``"left"``,
                ``"right"``, ``"back"``, ``"top"``, ``"bottom"``).

        Returns:
            Prompt string for a rotation sheet image.
        """
        return (
            f"{character.name}, {character.species}, {character.appearance}, "
            f"wearing {character.outfit}, {angle} view, rotation sheet, "
            f"consistent character, {character.style}, "
            f"highly detailed, model sheet, turnaround, grid"
        )

    def lighting(self, character: CharacterPrompt, condition: str) -> str:
        """Build a prompt for a lighting variant.

        Args:
            character: The character to describe.
            condition: Lighting condition (e.g. ``"morning"``, ``"golden hour"``,
                ``"night"``, ``"studio lighting"``).

        Returns:
            Prompt string for a lighting study image.
        """
        return (
            f"{character.name}, {character.species}, {character.appearance}, "
            f"wearing {character.outfit}, {condition} lighting, "
            f"{character.style}, highly detailed, lighting study, "
            f"dramatic lighting, mood lighting"
        )
