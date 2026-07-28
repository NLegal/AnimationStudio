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
