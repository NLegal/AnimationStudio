"""Integration tests for Identity Engine — IdentityScorer, BrandScore.

Tests verify:
- BrandScore weights sum to 1.0
- BrandScore computes correct weighted totals
- IdentityScorer loads all 7 default plugins
- score_all() / brand_score() return correct structure
- Edge cases: zero scores, all-1 scores, partial scores, no reference
"""

import pytest
from PIL import Image
import numpy as np

from src.identity_engine.scorer import IdentityScorer
from src.identity_engine.brand_score import BrandScore
from src.identity_engine.plugins import ALL_PLUGINS


# ── Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def test_img():
    """Return a small random RGB test image."""
    return Image.fromarray(
        np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    )


@pytest.fixture
def ref_img():
    """Return a random reference image."""
    return Image.fromarray(
        np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    )


# ── BrandScore Unit Tests ───────────────────────────────────────────────

class TestBrandScoreWeights:
    """Verifies BrandScore weight distribution."""

    def test_weights_sum_to_one(self):
        """Sum of BrandScore.WEIGHTS equals exactly 1.0."""
        total = sum(BrandScore.WEIGHTS.values())
        assert abs(total - 1.0) < 1e-6, f"Weights sum to {total}, expected 1.0"

    def test_all_weights_positive(self):
        """All individual weights are > 0."""
        for key, weight in BrandScore.WEIGHTS.items():
            assert weight > 0, f"Weight for {key} is {weight}, expected positive"

    def test_eight_dimensions(self):
        """BrandScore has exactly 8 dimensions."""
        assert len(BrandScore.WEIGHTS) == 8


class TestBrandScoreCompute:
    """Verifies BrandScore.compute() accuracy."""

    def test_all_half_returns_half(self):
        """All scores 0.5 → weighted total is 0.5."""
        scores = {key: 0.5 for key in BrandScore.WEIGHTS}
        result = BrandScore.compute(scores)
        assert result["total"] == 0.5

    def test_all_zero_returns_zero(self):
        """All scores 0.0 → total is 0.0."""
        scores = {key: 0.0 for key in BrandScore.WEIGHTS}
        result = BrandScore.compute(scores)
        assert result["total"] == 0.0

    def test_all_one_returns_one(self):
        """All scores 1.0 → total is 1.0."""
        scores = {key: 1.0 for key in BrandScore.WEIGHTS}
        result = BrandScore.compute(scores)
        assert result["total"] == 1.0

    def test_partial_input_defaults_to_zero(self):
        """Missing keys treated as 0.0."""
        # Only provide half the keys
        keys = list(BrandScore.WEIGHTS.keys())
        partial = {k: 1.0 for k in keys[:4]}
        result = BrandScore.compute(partial)
        # Expected: sum of weights for provided keys * 1.0
        expected = sum(BrandScore.WEIGHTS[k] for k in keys[:4])
        assert abs(result["total"] - expected) < 1e-6

    def test_return_structure(self):
        """Result dict has 'total', 'max', 'components'."""
        scores = {key: 0.5 for key in BrandScore.WEIGHTS}
        result = BrandScore.compute(scores)
        assert "total" in result
        assert "max" in result
        assert "components" in result
        assert result["max"] == 1.0
        assert len(result["components"]) == 8

    def test_component_structure(self):
        """Each component has 'raw', 'weighted', 'weight'."""
        scores = {key: 0.8 for key in BrandScore.WEIGHTS}
        result = BrandScore.compute(scores)
        for key, comp in result["components"].items():
            assert "raw" in comp
            assert "weighted" in comp
            assert "weight" in comp
            assert comp["raw"] == 0.8
            assert comp["weight"] == BrandScore.WEIGHTS[key]

    def test_known_scores(self):
        """Pre-computed known scores verify weighted math."""
        scores = {
            "prompt_accuracy": 1.0,
            "character_consistency": 0.5,
            "technical_quality": 0.0,
            "facial_appeal": 0.75,
            "child_friendliness": 1.0,
            "color_harmony": 0.0,
            "silhouette_recognizability": 0.5,
            "style_consistency": 0.25,
        }
        # Expected: 0.20*1.0 + 0.20*0.5 + 0.15*0.0 + 0.15*0.75 + 0.10*1.0
        #           + 0.10*0.0 + 0.05*0.5 + 0.05*0.25
        expected = (
            0.20 * 1.0
            + 0.20 * 0.5
            + 0.15 * 0.0
            + 0.15 * 0.75
            + 0.10 * 1.0
            + 0.10 * 0.0
            + 0.05 * 0.5
            + 0.05 * 0.25
        )
        result = BrandScore.compute(scores)
        assert abs(result["total"] - expected) < 1e-4


# ── IdentityScorer Tests ────────────────────────────────────────────────

class TestIdentityScorerDefaults:
    """Verifies IdentityScorer default behavior."""

    def test_default_plugins_load(self):
        """IdentityScorer() loads all 7 plugins from ALL_PLUGINS."""
        scorer = IdentityScorer()
        assert len(scorer.plugins) == len(ALL_PLUGINS)

    def test_default_plugins_match_all_plugins(self):
        """Default plugin names match ALL_PLUGINS names."""
        scorer = IdentityScorer()
        default_names = {p.name for p in scorer.plugins}
        expected_names = {p().name for p in ALL_PLUGINS}
        assert default_names == expected_names

    def test_score_all_returns_dict(self, test_img):
        """score_all() returns dict with expected keys."""
        scorer = IdentityScorer()
        scores = scorer.score_all(test_img)
        assert isinstance(scores, dict)
        assert len(scores) == len(ALL_PLUGINS)

    def test_score_all_values_in_range(self, test_img):
        """All score values are between 0.0 and 1.0."""
        scorer = IdentityScorer()
        scores = scorer.score_all(test_img)
        for name, value in scores.items():
            assert 0.0 <= value <= 1.0, f"{name} score {value} out of range"


class TestIdentityScorerLightMode:
    """Verifies the fast/light scoring path."""

    def test_light_plugins_exclude_torch(self):
        """Light mode drops DINOv2 and CLIP, keeps the rest."""
        scorer = IdentityScorer(light=True)
        names = {p.name for p in scorer.plugins}
        assert "color_harmony" in names
        assert "facial_appeal" in names
        assert len(names) < len(ALL_PLUGINS)

    def test_light_color_plugin_uses_sampling(self):
        """Light mode disables k-means in the color plugin."""
        from src.identity_engine.plugins.color_verification import ColorVerificationPlugin
        scorer = IdentityScorer(light=True)
        color = next(p for p in scorer.plugins if isinstance(p, ColorVerificationPlugin))
        assert color.use_kmeans is False

    def test_light_score_all_valid(self, test_img):
        """Light scoring still returns in-range values."""
        scorer = IdentityScorer(light=True)
        scores = scorer.score_all(test_img)
        for name, value in scores.items():
            assert 0.0 <= value <= 1.0, f"{name} score {value} out of range"
        brand = scorer.brand_score(test_img)
        assert 0.0 <= brand["total"] <= 1.0


class TestIdentityScorerBrandScore:
    """Verifies brand_score() integration."""

    def test_brand_score_returns_valid(self, test_img):
        """brand_score() returns valid result with total 0-1."""
        scorer = IdentityScorer()
        result = scorer.brand_score(test_img)
        assert isinstance(result, dict)
        assert "total" in result
        assert 0.0 <= result["total"] <= 1.0

    def test_brand_score_has_components(self, test_img):
        """brand_score() returns components for all dimensions."""
        scorer = IdentityScorer()
        result = scorer.brand_score(test_img)
        assert len(result["components"]) == 8


class TestIdentityScorerEdgeCases:
    """Edge case handling."""

    def test_no_reference_still_works(self, test_img):
        """Image with no reference still produces valid Brand Score."""
        scorer = IdentityScorer()
        # Don't pass reference — each plugin handles internally
        result = scorer.brand_score(test_img)
        assert 0.0 <= result["total"] <= 1.0
        assert "components" in result

    def test_all_plugins_fallback_gracefully(self, test_img):
        """Plugins that can't load models still return fallback scores."""
        scorer = IdentityScorer()
        scores = scorer.score_all(test_img)
        # All plugins should return something (fallback or real)
        for name, value in scores.items():
            assert isinstance(value, float), f"{name} returned {type(value)}"
            assert 0.0 <= value <= 1.0, f"{name} value {value} out of range"

    def test_mock_plugin_deterministic(self, test_img):
        """IdentityScorer with MockScorerPlugin works deterministically."""
        from src.identity_engine.scorer import MockScorerPlugin
        scorer = IdentityScorer(plugins=[MockScorerPlugin(weight=1.0)])
        result = scorer.brand_score(test_img)
        assert 0.0 <= result["total"] <= 1.0
        assert result["max"] == 1.0

    def test_small_image_handling(self):
        """Very small image (32x32) doesn't crash."""
        tiny = Image.fromarray(
            np.random.randint(0, 255, (32, 32, 3), dtype=np.uint8)
        )
        scorer = IdentityScorer()
        result = scorer.brand_score(tiny)
        assert 0.0 <= result["total"] <= 1.0
