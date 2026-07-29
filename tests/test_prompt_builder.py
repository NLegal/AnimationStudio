"""Tests for Prompt Builder — template expansion, age variants, and builder routing.

Tests cover all 4 asset types (reference, expression, pose, outfit),
age variants, rotation/lighting templates, negative prompt composition,
custom character tags, and best-effort handling of unknown names.
"""

import logging
from pathlib import Path

import pytest

from src.prompt_builder import PromptBuilder, PromptTemplates, CharacterPrompt, build_negative_prompt
from src.pipeline import GenerationJob, JobQueue, DiversityFilter
from src.identity_engine.scorer import IdentityScorer, MockScorerPlugin
from src.asset_repository.sqlite_repo import SQLiteAssetRepository, SQLiteCharacterRepository
from tests.conftest import MockBackend


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


# ---------------------------------------------------------------------------
# Merged expression list tests (CHAR-03)
# ---------------------------------------------------------------------------

class TestMergedExpressionList:
    """PromptBuilder._known_expressions() returns the merged PHASE1.md + code superset.

    PHASE1.md (23): neutral, happy, very_happy, laughing, giggling, smiling,
        excited, surprised, confused, thinking, curious, sleepy, yawning,
        crying, sad, scared, embarrassed, proud, determined, singing,
        whistling, blowing_kiss, winking
    Code extras (9): angry, shy, silly, sneezing, coughing, sighing,
        tired, worried, disgusted
    Merged total: 32 expressions.
    """

    MERGED_EXPRESSIONS = frozenset({
        # PHASE1.md (23)
        "neutral", "happy", "very_happy", "laughing", "giggling", "smiling",
        "excited", "surprised", "confused", "thinking", "curious", "sleepy",
        "yawning", "crying", "sad", "scared", "embarrassed", "proud",
        "determined", "singing", "whistling", "blowing_kiss", "winking",
        # Code extras (9)
        "angry", "shy", "silly", "sneezing", "coughing", "sighing",
        "tired", "worried", "disgusted",
    })

    def test_merged_expression_count(self, builder: PromptBuilder):
        """_known_expressions() returns exactly 32 expressions."""
        known = builder._known_expressions()
        assert len(known) == 32, f"Expected 32, got {len(known)}"

    def test_expression_includes_phase1_additions(self, builder: PromptBuilder):
        """PHASE1.md additions (blowing_kiss, winking, very_happy, giggling, whistling) are in the set."""
        known = builder._known_expressions()
        for expr in ("blowing_kiss", "winking", "very_happy", "giggling", "whistling"):
            assert expr in known, f"Missing PHASE1.md expression: {expr}"

    def test_expression_retains_code_extras(self, builder: PromptBuilder):
        """Code extras (angry, shy, silly, sneezing, coughing, sighing) are in the set."""
        known = builder._known_expressions()
        for expr in ("angry", "shy", "silly", "sneezing", "coughing", "sighing"):
            assert expr in known, f"Missing code extra: {expr}"

    @pytest.mark.parametrize("expression", sorted(MERGED_EXPRESSIONS))
    def test_every_expression_produces_valid_prompt(
        self, expression: str, lily: CharacterPrompt, builder: PromptBuilder
    ):
        """Every known expression produces a valid prompt with character name."""
        pos, neg = builder.build(lily, asset_type="expression", variant=expression)
        assert lily.name in pos, f"Character name missing for expression '{expression}'"
        assert expression in pos, f"Expression name '{expression}' missing from prompt"

    def test_best_effort_unknown_expression_warning(
        self, lily: CharacterPrompt, builder: PromptBuilder, caplog
    ):
        """Unknown expression name logs a warning but still produces valid prompt."""
        caplog.set_level(logging.WARNING)
        unknown = "nonexistent_expression_xyz"
        pos, neg = builder.build(lily, asset_type="expression", variant=unknown)
        assert isinstance(pos, str)
        assert len(pos) > 0
        assert lily.name in pos
        assert unknown in pos


# ---------------------------------------------------------------------------
# End-to-end expression pipeline integration test (CHAR-03)
# ---------------------------------------------------------------------------

class TestEndToEndExpressionPipeline:
    """Integration test: GenerationJob + MockBackend + updated PromptBuilder.

    Proves the full pipeline (build prompt → generate → score → diversity
    filter → save) works end-to-end with the updated expression list.
    """

    @pytest.mark.asyncio
    async def test_expression_pipeline_end_to_end(self):
        """GenerationJob with MockBackend processes one expression variant."""
        import tempfile
        import os
        from src.models.schemas import CharacterModel

        # Use a shared temp file so both character and asset repos share the DB
        fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            char_repo = SQLiteCharacterRepository(db_path)
            repo = SQLiteAssetRepository(db_path)

            # Create a character record first (needed for FK constraint)
            char = CharacterModel(
                name="Lily Bunny",
                category="main",
                species="rabbit",
            )
            await char_repo.save_character(char)

            backend = MockBackend()
            prompt_builder = PromptBuilder()
            scorer = IdentityScorer(plugins=[MockScorerPlugin(weight=1.0)])
            df = DiversityFilter(n_clusters=2)
            gj = GenerationJob(
                backend=backend,
                prompt_builder=prompt_builder,
                identity_scorer=scorer,
                asset_repo=repo,
                diversity_filter=df,
            )

            jq = JobQueue()
            job = jq.create_job(
                character_id=char.id,
                job_type="expression",
                config={
                    "variants": [
                        {
                            "name": "happy",
                            "prompt": "Lily Bunny, rabbit, happy expression",
                        }
                    ],
                    "count": 2,
                    "shortlist_size": 1,
                },
            )

            # Execute
            result = await gj.execute(job)

            # Verify
            assert result["total_generated"] >= 1
            assert result["total_scored"] >= 1
            assert result["variants_completed"] == 1
            assert result["variants_failed"] == 0

            # At least one asset should be shortlisted
            shortlisted = result.get("shortlisted_ids", [])
            assert len(shortlisted) >= 1, (
                f"No assets were shortlisted. "
                f"Generated: {result['total_generated']}, "
                f"Scored: {result['total_scored']}"
            )
            asset = await repo.get(shortlisted[0])
            assert asset is not None
            assert asset.state == "shortlisted"
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
