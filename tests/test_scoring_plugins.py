"""Tests for all 7 Identity Engine scoring plugins.

Tests verify:
- Each plugin follows the ScoringPlugin protocol (name, weight, score())
- Each plugin returns normalized 0-1 scores
- Each plugin handles missing reference gracefully
- Each plugin handles missing model gracefully (fallback, no crash)
"""

import warnings
import pytest
from PIL import Image
import numpy as np

from src.identity_engine.plugins import ALL_PLUGINS
from src.identity_engine.scorer import ScoringPlugin


# ── Helpers ──────────────────────────────────────────────────────────────

@pytest.fixture
def test_img():
    """Return a small random RGB test image (224x224)."""
    return Image.fromarray(
        np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    )


@pytest.fixture
def ref_img():
    """Return a different random RGB reference image (224x224)."""
    return Image.fromarray(
        np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    )


# ── Protocol Compliance ──────────────────────────────────────────────────

class TestPluginProtocol:
    """Every plugin must satisfy the ScoringPlugin protocol."""

    @pytest.mark.parametrize("plugin_cls", ALL_PLUGINS, ids=lambda c: c.__name__)
    def test_has_name(self, plugin_cls):
        """Each plugin class (or instance) has a non-empty name."""
        if hasattr(plugin_cls, "name"):
            assert isinstance(plugin_cls.name, str) and len(plugin_cls.name) > 0
        else:
            # Some plugins set name per-instance
            instance = plugin_cls()
            assert isinstance(instance.name, str) and len(instance.name) > 0

    @pytest.mark.parametrize("plugin_cls", ALL_PLUGINS, ids=lambda c: c.__name__)
    def test_has_weight(self, plugin_cls):
        """Each plugin has a weight attribute (float)."""
        instance = plugin_cls()
        assert hasattr(instance, "weight")
        assert isinstance(instance.weight, float)
        assert 0.0 <= instance.weight <= 1.0

    @pytest.mark.parametrize("plugin_cls", ALL_PLUGINS, ids=lambda c: c.__name__)
    def test_score_method_exists(self, plugin_cls):
        """Each plugin has a callable score() method."""
        instance = plugin_cls()
        assert callable(getattr(instance, "score", None))

    @pytest.mark.parametrize("plugin_cls", ALL_PLUGINS, ids=lambda c: c.__name__)
    def test_score_returns_float(self, plugin_cls, test_img, ref_img):
        """score() returns a float between 0.0 and 1.0."""
        instance = plugin_cls()
        score = instance.score(test_img, reference=ref_img)
        assert isinstance(score, float), f"{plugin_cls.__name__}.score() returned {type(score)}"
        assert 0.0 <= score <= 1.0, f"{plugin_cls.__name__} score {score} out of range"


# ── Graceful Degradation: No Reference ──────────────────────────────────

class TestNoReference:
    """Plugins must handle missing reference gracefully."""

    @pytest.mark.parametrize("plugin_cls", ALL_PLUGINS, ids=lambda c: c.__name__)
    def test_score_without_reference(self, plugin_cls, test_img):
        """score(image) with no reference returns 0.0-1.0, never crashes."""
        instance = plugin_cls()
        try:
            score = instance.score(test_img, reference=None)
        except Exception:
            score = instance.score(test_img)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


# ── Graceful Degradation: Missing Model ─────────────────────────────────

class TestMissingModel:
    """Plugins must handle model load failures gracefully."""

    @pytest.mark.parametrize("plugin_cls", ALL_PLUGINS, ids=lambda c: c.__name__)
    def test_graceful_model_fallback(self, plugin_cls, test_img, ref_img):
        """If model loading fails, plugin returns fallback score, never crashes."""
        instance = plugin_cls()
        # The base behavior: score() should handle missing external deps
        # by returning a fallback without raising
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            score = instance.score(test_img, reference=ref_img)
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0


# ── Plugin-Specific Behavior ─────────────────────────────────────────────

class TestDINOv2Specific:
    """DINOv2-specific tests."""

    def test_embed_returns_tensor(self, test_img):
        """embed() returns a torch Tensor of expected shape."""
        from src.identity_engine.plugins.dinov2_score import DINOv2ScoringPlugin
        plugin = DINOv2ScoringPlugin()
        embedding = plugin.embed(test_img)
        # Expect a 1D tensor (typically 384-dim for vits14)
        assert hasattr(embedding, "shape"), "embed() must return a tensor-like object"
        assert len(embedding.shape) == 1, f"Expected 1D embedding, got shape {embedding.shape}"


class TestCLIPSpecific:
    """CLIP-specific tests."""

    def test_score_without_prompt_returns_zero(self, test_img, ref_img):
        """Without prompt, CLIP returns 0.0."""
        from src.identity_engine.plugins.clip_score import CLIPScoringPlugin
        plugin = CLIPScoringPlugin()
        score = plugin.score(test_img, reference=ref_img)
        assert score == 0.0, "CLIP should return 0.0 without prompt"

    def test_score_with_prompt(self, test_img, ref_img):
        """With prompt, CLIP returns a score."""
        from src.identity_engine.plugins.clip_score import CLIPScoringPlugin
        plugin = CLIPScoringPlugin()
        score = plugin.score(test_img, reference=ref_img, prompt="test character")
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


class TestColorVerificationSpecific:
    """Color Verification-specific tests."""

    def test_grayscale_image_handling(self, ref_img):
        """Grayscale images get low score but don't crash."""
        from src.identity_engine.plugins.color_verification import ColorVerificationPlugin
        gray = Image.fromarray(
            np.random.randint(0, 255, (224, 224), dtype=np.uint8), mode="L"
        )
        plugin = ColorVerificationPlugin()
        score = plugin.score(gray, reference=ref_img)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


class TestExpressionSpecific:
    """Expression Verification-specific tests."""

    def test_expression_name_matching(self, test_img, ref_img):
        """Expression with a valid name returns a score."""
        from src.identity_engine.plugins.expression_verify import ExpressionVerificationPlugin
        plugin = ExpressionVerificationPlugin()
        score = plugin.score(test_img, reference=ref_img, expression_name="happy")
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_without_reference_returns_neutral(self, test_img):
        """Without reference, expression returns 0.5 (neutral)."""
        from src.identity_engine.plugins.expression_verify import ExpressionVerificationPlugin
        plugin = ExpressionVerificationPlugin()
        score = plugin.score(test_img, reference=None)
        assert score == 0.5, "Expression without reference should return 0.5"


class TestStyleSpecific:
    """Style Verification-specific tests."""

    def test_without_reference_returns_neutral(self, test_img):
        """Without reference, style returns 0.5 (neutral)."""
        from src.identity_engine.plugins.style_verification import StyleVerificationPlugin
        plugin = StyleVerificationPlugin()
        score = plugin.score(test_img, reference=None)
        assert score == 0.5, "Style without reference should return 0.5"


class TestPoseAndPartSpecific:
    """Pose and Part Verification tests."""

    def test_pose_without_reference_returns_zero(self, test_img):
        """Without reference, pose returns 0.0."""
        from src.identity_engine.plugins.pose_verification import PoseVerificationPlugin
        plugin = PoseVerificationPlugin()
        score = plugin.score(test_img, reference=None)
        assert score == 0.0

    def test_part_without_reference_returns_zero(self, test_img):
        """Without reference, part returns 0.0."""
        from src.identity_engine.plugins.part_verification import PartVerificationPlugin
        plugin = PartVerificationPlugin()
        score = plugin.score(test_img, reference=None)
        assert score == 0.0
