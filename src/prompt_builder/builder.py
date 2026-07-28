"""PromptBuilder — composes positive and negative prompts from templates.

The PromptBuilder orchestrates template selection and negative prompt
assembly to produce the final prompt pair for generation.
"""

from src.prompt_builder.templates import CharacterPrompt, PromptTemplates
from src.prompt_builder.negative import build_negative_prompt


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
        **kwargs,
    ) -> tuple[str, str]:
        """Build a (positive_prompt, negative_prompt) tuple.

        Args:
            character: CharacterPrompt with character details.
            asset_type: One of 'reference', 'expression', 'pose', 'outfit'.
            variant: Sub-type (expression name, pose name, outfit name, angle).
            **kwargs: Extra args passed to the template method.

        Returns:
            Tuple of (positive_prompt, negative_prompt).
        """
        # Route to the correct template method
        if asset_type == "reference":
            angle = variant or kwargs.get("angle", "front")
            positive = self.templates.reference_sheet(character, angle=angle)
        elif asset_type == "expression":
            expression = variant or kwargs.get("expression", "neutral")
            positive = self.templates.expression(character, expression)
        elif asset_type == "pose":
            pose = variant or kwargs.get("pose", "standing")
            positive = self.templates.pose(character, pose)
        elif asset_type == "outfit":
            outfit = variant or kwargs.get("outfit", character.outfit)
            positive = self.templates.outfit(character, outfit)
        else:
            raise ValueError(f"Unknown asset_type: {asset_type}")

        negative = self.negative_fn(custom=kwargs.get("custom_negative", ""))
        return positive, negative
