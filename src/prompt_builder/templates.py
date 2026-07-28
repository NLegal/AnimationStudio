"""Character-specific prompt templates per CHAR-08.

Provides parameterized prompt templates for reference sheets, expressions,
poses, and outfits. Never hand-write prompts — always use these templates.
"""

from dataclasses import dataclass


@dataclass
class CharacterPrompt:
    """Character data used to parameterize prompt templates."""

    name: str
    species: str
    appearance: str = ""
    outfit: str = ""
    style: str = "Pixar-quality, Cocomelon-inspired, bright colorful nursery world"


class PromptTemplates:
    """Static prompt template methods per asset type."""

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
