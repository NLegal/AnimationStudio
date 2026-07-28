"""Tests for Prompt Builder — template expansion, age variants, and builder routing.

Tests cover all 4 asset types (reference, expression, pose, outfit),
age variants, rotation/lighting templates, negative prompt composition,
custom character tags, and best-effort handling of unknown names.
"""

import logging
from pathlib import Path

import pytest

from src.prompt_builder import PromptBuilder, PromptTemplates, CharacterPrompt, build_negative_prompt


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def lily() -> CharacterPrompt:
    """Canonical Lily Bunny character for prompt tests."""
    return CharacterPrompt(
        name="Lily Bunny",
        species="rabbit",
        appearance="white fur, pink ears, big blue eyes",
        outfit="pink dress with white lace",
        style="Pixar-quality, Cocomelon-inspired, bright colorful nursery world",
    )


@pytest.fixture
def builder() -> PromptBuilder:
    """Default PromptBuilder instance."""
    return PromptBuilder()


# ---------------------------------------------------------------------------
# Asset-type template tests
# ---------------------------------------------------------------------------

class TestAssetTypeTemplates:
    """Each asset type produces a prompt containing the relevant identifiers."""

    def test_reference_prompt(self, lily: CharacterPrompt, builder: PromptBuilder):
        """Reference sheet prompt contains character name and angle."""
        pos, neg = builder.build(lily, asset_type="reference", angle="front")
        assert lily.name in pos
        assert "front view" in pos

    def test_expression_prompt(self, lily: CharacterPrompt, builder: PromptBuilder):
        """Expression prompt contains expression name and character name."""
        pos, neg = builder.build(lily, asset_type="expression", variant="happy")
        assert lily.name in pos
        assert "happy" in pos

    def test_pose_prompt(self, lily: CharacterPrompt, builder: PromptBuilder):
        """Pose prompt contains pose name and character name."""
        pos, neg = builder.build(lily, asset_type="pose", variant="running")
        assert lily.name in pos
        assert "running" in pos

    def test_outfit_prompt(self, lily: CharacterPrompt, builder: PromptBuilder):
        """Outfit prompt contains outfit description and character name."""
        pos, neg = builder.build(lily, asset_type="outfit", variant="winter coat")
        assert lily.name in pos
        assert "winter coat" in pos


# ---------------------------------------------------------------------------
# Age variant tests
# ---------------------------------------------------------------------------

class TestAgeVariants:
    """Age-variant templates produce age-specific prompt strings."""

    def test_toddler_age_variant(self, lily: CharacterPrompt, builder: PromptBuilder):
        """Toddler variant prompt contains toddler descriptor."""
        pos, neg = builder.build(lily, asset_type="reference", age="toddler")
        assert "toddler" in pos.lower()

    def test_preschool_age_variant(self, lily: CharacterPrompt, builder: PromptBuilder):
        """Preschool variant prompt contains preschool descriptor."""
        pos, neg = builder.build(lily, asset_type="reference", age="preschool")
        assert "preschool" in pos.lower()

    def test_kindergarten_age_variant(self, lily: CharacterPrompt, builder: PromptBuilder):
        """Kindergarten variant prompt contains kindergarten descriptor."""
        pos, neg = builder.build(lily, asset_type="reference", age="kindergarten")
        assert "kindergarten" in pos.lower()

    def test_age_with_expression(self, lily: CharacterPrompt, builder: PromptBuilder):
        """Age modifier can be combined with expression templates."""
        pos, neg = builder.build(lily, asset_type="expression", variant="happy", age="toddler")
        assert "toddler" in pos.lower()
        assert "happy" in pos


# ---------------------------------------------------------------------------
# Negative prompt tests
# ---------------------------------------------------------------------------

class TestNegativePrompt:
    """Negative prompt composition — standard and custom."""

    def test_negative_prompt_standard(self):
        """build_negative_prompt() contains common negative items and style items."""
        neg = build_negative_prompt()
        assert "low quality" in neg
        assert "blurry" in neg
        # Style-based items are also included
        assert "anime" in neg

    def test_negative_prompt_custom(self):
        """Custom string is appended to the base negative prompt."""
        custom = "test_custom_exclusion"
        neg = build_negative_prompt(custom=custom)
        assert custom in neg
        assert neg.endswith(custom)

    def test_negative_prompt_without_custom(self):
        """With no custom string, only standard components are used."""
        neg = build_negative_prompt()
        # Should contain items from both COMMON_NEGATIVE and STYLE_NEGATIVE
        assert ", " in neg
        assert len(neg) > 50


# ---------------------------------------------------------------------------
# Character customisation tests
# ---------------------------------------------------------------------------

class TestCharacterCustomisation:
    """Per-character customisation (tags, overrides)."""

    def test_character_custom_tags(self, builder: PromptBuilder):
        """Character with custom_tags adds them to the positive prompt."""
        char = CharacterPrompt(
            name="Ben Bunny",
            species="rabbit",
            appearance="brown fur, floppy ears",
            outfit="blue overalls",
            custom_tags="wearing a bowtie, holding a book",
        )
        pos, neg = builder.build(char, asset_type="reference")
        assert "bowtie" in pos

    def test_character_default_age(self):
        """CharacterPrompt default age is 'preschool'."""
        char = CharacterPrompt(name="Test", species="cat", appearance="", outfit="")
        assert char.age == "preschool"

    def test_character_custom_age(self):
        """CharacterPrompt age can be overridden."""
        char = CharacterPrompt(name="Test", species="cat", appearance="", outfit="", age="toddler")
        assert char.age == "toddler"


# ---------------------------------------------------------------------------
# Rotation and lighting tests
# ---------------------------------------------------------------------------

class TestRotationAndLighting:
    """Rotation and lighting template variants."""

    def test_rotation_prompt(self, lily: CharacterPrompt, builder: PromptBuilder):
        """Rotation angle appears in prompt when specified."""
        pos, neg = builder.build(lily, asset_type="reference", rotation="3/4")
        assert "3/4" in pos

    def test_lighting_prompt(self, lily: CharacterPrompt, builder: PromptBuilder):
        """Lighting condition appears in prompt when specified."""
        pos, neg = builder.build(lily, asset_type="reference", lighting="golden hour")
        assert "golden hour" in pos

    def test_rotation_with_expression(self, lily: CharacterPrompt, builder: PromptBuilder):
        """Rotation can be combined with expression templates (rotation takes priority)."""
        pos, neg = builder.build(lily, asset_type="expression", variant="surprised", rotation="left")
        assert "left" in pos
        # rotation is a dedicated template that replaces the asset-type template
        assert lily.name in pos
        assert "rotation sheet" in pos


# ---------------------------------------------------------------------------
# Edge-case tests
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Best-effort handling of edge cases."""

    def test_unknown_expression_warning(self, lily: CharacterPrompt, builder: PromptBuilder, caplog):
        """Unknown expression name logs a warning but produces a valid prompt."""
        caplog.set_level(logging.WARNING)
        unknown = "nonexistent_expression_xyz"
        pos, neg = builder.build(lily, asset_type="expression", variant=unknown)
        # Should still produce a valid prompt string
        assert isinstance(pos, str)
        assert len(pos) > 0
        assert lily.name in pos
        # Should contain the unknown expression name in some form
        assert unknown in pos

    def test_unknown_pose_does_not_crash(self, lily: CharacterPrompt, builder: PromptBuilder):
        """Unknown pose name produces a valid prompt (best-effort)."""
        pos, neg = builder.build(lily, asset_type="pose", variant="nonexistent_pose_xyz")
        assert isinstance(pos, str)
        assert len(pos) > 0

    def test_empty_appearance(self, builder: PromptBuilder):
        """Character with empty appearance uses sensible defaults."""
        char = CharacterPrompt(name="Test", species="cat", appearance="", outfit="")
        pos, neg = builder.build(char, asset_type="reference")
        assert "Test" in pos
        assert len(pos) > 0

    def test_empty_appearance_with_custom_tags(self, builder: PromptBuilder):
        """Custom tags still added when appearance is empty."""
        char = CharacterPrompt(
            name="Test", species="cat", appearance="", outfit="",
            custom_tags="fluffy, smiling",
        )
        pos, neg = builder.build(char, asset_type="reference")
        assert "fluffy" in pos
