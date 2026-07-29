"""PromptBuilder — composes positive and negative prompts from templates.

The PromptBuilder orchestrates template selection and negative prompt
assembly to produce the final prompt pair for generation.
"""

import logging

from src.prompt_builder.templates import CharacterPrompt, PromptTemplates
from src.prompt_builder.negative import build_negative_prompt

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Composes positive and negative prompts for asset generation.

    Usage:
        prompt = CharacterPrompt(name="Lily Bunny", ...)
        pos, neg = PromptBuilder().build(prompt, asset_type="reference", angle="front")
    """

    def __init__(
        self,
        templates: type[PromptTemplates] = PromptTemplates,
        negative_fn=build_negative_prompt,
    ):
        self.templates = templates
        self.negative_fn = negative_fn

    def build(
        self,
        character: CharacterPrompt,
        asset_type: str,
        variant: str = None,
        age: str = None,
        rotation: str = None,
        lighting: str = None,
        **kwargs,
    ) -> tuple[str, str]:
        """Build a (positive_prompt, negative_prompt) tuple.

        Args:
            character: CharacterPrompt with character details.
            asset_type: One of 'reference', 'expression', 'pose', 'outfit'.
            variant: Sub-type (expression name, pose name, outfit name, angle).
            age: Optional age descriptor ('toddler', 'preschool', 'kindergarten')
                to prepend as an age variant modifier.
            rotation: Optional rotation angle string for rotation library templates.
            lighting: Optional lighting condition string for lighting variant templates.
            **kwargs: Extra args (custom_negative, angle, etc.) passed through.

        Returns:
            Tuple of (positive_prompt, negative_prompt).
        """
        # --- Route to the correct template ---
        #
        # Priority order: 1) rotation/lighting (variants that use their own
        # template), 2) age modifier wraps the base asset-type template, 3)
        # standard asset-type routing.
        if rotation is not None:
            template = self.templates()
            positive = template.rotation(character, rotation)
        elif lighting is not None:
            template = self.templates()
            positive = template.lighting(character, lighting)
        else:
            # Standard asset-type routing
            if asset_type == "reference":
                angle = variant or kwargs.get("angle", "front")
                positive = self.templates.reference_sheet(character, angle=angle)
            elif asset_type == "expression":
                expression = variant or kwargs.get("expression", "neutral")
                if expression not in self._known_expressions():
                    logger.warning("Unknown expression name '%s' — using best-effort", expression)
                positive = self.templates.expression(character, expression)
            elif asset_type == "pose":
                pose = variant or kwargs.get("pose", "standing")
                if pose not in self._known_poses():
                    logger.warning("Unknown pose name '%s' — using best-effort", pose)
                positive = self.templates.pose(character, pose)
            elif asset_type == "outfit":
                outfit = variant or kwargs.get("outfit", character.outfit)
                positive = self.templates.outfit(character, outfit)
            else:
                raise ValueError(f"Unknown asset_type: {asset_type}")

            # Age modifier — prepend age descriptor to the base prompt
            if age is not None:
                descriptor = self._age_descriptor(age)
                positive = f"{descriptor}, {positive}"

        # --- Append custom tags if present ---
        if character.custom_tags:
            positive = f"{positive}, {character.custom_tags}"

        # --- Negative prompt ---
        negative = self.negative_fn(custom=kwargs.get("custom_negative", ""))
        return positive, negative

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    _AGE_DESCRIPTORS: dict[str, str] = {
        "toddler": "toddler version, smaller, rounder features, 2-3 years old",
        "preschool": "preschool age, 4-5 years old",
        "kindergarten": "kindergarten age, 5-6 years old",
    }

    def _age_descriptor(self, age: str) -> str:
        """Return the age descriptor string for the given age key."""
        return self._AGE_DESCRIPTORS.get(age, f"{age} age")

    @staticmethod
    def _known_expressions() -> set[str]:
        """Return the merged superset of PHASE1.md + code expression names.

        PHASE1.md (23): neutral, happy, very_happy, laughing, giggling,
        smiling, excited, surprised, confused, thinking, curious, sleepy,
        yawning, crying, sad, scared, embarrassed, proud, determined,
        singing, whistling, blowing_kiss, winking.

        Code extras (9): angry, shy, silly, sneezing, coughing, sighing,
        tired, worried, disgusted.

        Total merged: 32 expressions (all lowercase, unique).
        """
        return {
            # PHASE1.md expressions (23)
            "neutral", "happy", "very_happy", "laughing", "giggling",
            "smiling", "excited", "surprised", "confused", "thinking",
            "curious", "sleepy", "yawning", "crying", "sad", "scared",
            "embarrassed", "proud", "determined", "singing", "whistling",
            "blowing_kiss", "winking",
            # Code extras (9) — none overlap with PHASE1.md
            "angry", "shy", "silly", "sneezing", "coughing", "sighing",
            "tired", "worried", "disgusted",
        }

    @staticmethod
    def _known_poses() -> set[str]:
        """Return the set of known pose names (from PHASE1.md)."""
        return {
            "standing", "running", "jumping", "sitting", "dancing",
            "walking", "hopping", "clapping", "waving", "skipping",
            "sleeping", "eating", "drinking", "reading", "drawing",
            "crawling", "sliding", "hiding", "stretching", "bouncing",
        }
