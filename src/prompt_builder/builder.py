"""PromptBuilder — composes positive and negative prompts from templates.

The PromptBuilder orchestrates template selection and negative prompt
assembly to produce the final prompt pair for generation.
"""

import logging
from typing import Optional

from src.prompt_builder.templates import CharacterPrompt, EnvironmentPrompt, PromptTemplates
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
    #  Environment / world builders (Phase 2)
    # ------------------------------------------------------------------ #

    # PHASE2.md environment negative prompt (world rules).
    ENVIRONMENT_NEGATIVE = (
        "dark, abandoned, dirty, graffiti, broken windows, cracked roads, "
        "trash, blood, violence, weapons, fire, explosion, realistic decay, "
        "horror, foggy apocalypse, ruins, industrial pollution, "
        "low quality, blurry, text, watermark, logo"
    )

    def build_environment(
        self,
        environment: EnvironmentPrompt,
        asset_type: str = "exterior",
        variant: Optional[str] = None,
        set_name: Optional[str] = None,
        custom_negative: str = "",
    ) -> tuple[str, str]:
        """Build a (positive, negative) prompt pair for a world location.

        Args:
            environment: EnvironmentPrompt for the named location.
            asset_type: One of ``environment``/``exterior`` (reference),
                ``interior`` (set), ``season``, ``time_of_day``, ``weather``,
                ``camera``, or ``lighting``.  The ``variant`` carries the
                dimension value for all but the base reference types.
            variant: Dimension value (view, room, season, time, weather,
                camera angle, or lighting condition).
            set_name: Interior set name (alias for variant on interiors).
            custom_negative: Extra negative terms appended to the base set.
        """
        negative = ", ".join(
            p for p in (self.ENVIRONMENT_NEGATIVE, custom_negative) if p
        )

        if asset_type in ("interior",):
            return (
                self.templates.environment(
                    environment, view="interior",
                    set_name=set_name or variant or "default_interior",
                ),
                negative,
            )
        if asset_type in ("season",):
            return (
                self.templates.environment(
                    environment, view="front", season=variant or "summer",
                ),
                negative,
            )
        if asset_type in ("time_of_day",):
            return (
                self.templates.environment(
                    environment, view="front", time_of_day=variant or "day",
                ),
                negative,
            )
        if asset_type in ("weather",):
            return (
                self.templates.environment(
                    environment, view="front", weather=variant or "sunny",
                ),
                negative,
            )
        if asset_type in ("camera",):
            return (
                self.templates.environment(
                    environment, view="front", camera=variant or "wide",
                ),
                negative,
            )
        if asset_type in ("lighting",):
            return (
                self.templates.environment(
                    environment, view="front", lighting=variant or "natural",
                ),
                negative,
            )
        # Base exterior reference (asset_type "environment" or "exterior")
        view = variant or "front"
        return (
            self.templates.environment(environment, view=view),
            negative,
        )

    def build_vehicle(
        self,
        vehicle: EnvironmentPrompt,
        variant: str = "side",
        custom_negative: str = "",
    ) -> tuple[str, str]:
        """Build a (positive, negative) prompt pair for a vehicle sheet."""
        negative = ", ".join(
            p for p in (self.ENVIRONMENT_NEGATIVE, custom_negative) if p
        )
        return self.templates.vehicle(vehicle, view=variant), negative

    def build_background(
        self,
        bg: EnvironmentPrompt,
        variant: str = "sky",
        custom_negative: str = "",
    ) -> tuple[str, str]:
        """Build a (positive, negative) prompt pair for a background layer."""
        negative = ", ".join(
            p for p in (self.ENVIRONMENT_NEGATIVE, custom_negative) if p
        )
        return self.templates.background(bg, layer=variant), negative

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
        """Return the merged superset of PHASE1.md + code pose names.

        PHASE1.md (20): standing, walking, running, jumping, skipping,
        sitting, kneeling, dancing, sleeping, reading, writing, pointing,
        clapping, waving, hugging, holding_hands, playing, swimming,
        flying, sliding.

        Code extras (8): hopping, eating, drinking, drawing, crawling,
        hiding, stretching, bouncing.

        Total merged: 28 poses (all lowercase, unique).
        """
        return {
            # PHASE1.md poses (20)
            "standing", "walking", "running", "jumping", "skipping",
            "sitting", "kneeling", "dancing", "sleeping", "reading",
            "writing", "pointing", "clapping", "waving", "hugging",
            "holding_hands", "playing", "swimming", "flying", "sliding",
            # Code extras (8) — none overlap with PHASE1.md
            "hopping", "eating", "drinking", "drawing", "crawling",
            "hiding", "stretching", "bouncing",
        }
