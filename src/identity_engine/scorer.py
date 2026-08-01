"""Identity scoring engine with plugin-based architecture.

Each scoring dimension is a plugin following the ScoringPlugin protocol.
The IdentityScorer discovers and weights them (D-06, D-07).
"""

import random
from typing import Optional, Protocol

from PIL import Image

from src.identity_engine.brand_score import BrandScore


class ScoringPlugin(Protocol):
    """Protocol for identity scoring plugins.

    Each plugin must expose:
    - name: str — unique identifier for the score dimension
    - weight: float — relative importance (sum of all plugin weights should = 1.0)
    - score(image, reference, **kwargs) -> float — returns a 0-1 score
    """

    name: str
    weight: float

    def score(
        self,
        image: Image.Image,
        reference: Optional[Image.Image] = None,
        **kwargs,
    ) -> float: ...


class MockScorerPlugin:
    """A mock plugin that returns random scores between 0.5 and 1.0.

    Used for testing without real ML models.
    """

    name: str = "mock_score"
    weight: float

    def __init__(self, weight: float = 0.0):
        self.weight = weight

    def score(
        self,
        image: Image.Image,
        reference: Optional[Image.Image] = None,
        **kwargs,
    ) -> float:
        return round(random.uniform(0.5, 1.0), 4)


class IdentityScorer:
    """Orchestrates multiple scoring plugins to produce a composite identity score.

    Usage:
        scorer = IdentityScorer()
        scores = scorer.score_all(image)
        brand = scorer.brand_score(image)
    """

    def __init__(self, plugins: Optional[list[ScoringPlugin]] = None,
                 light: bool = False):
        self.plugins = plugins or self._default_plugins(light=light)

    def _default_plugins(self, light: bool = False) -> list[ScoringPlugin]:
        """Return the default set of scoring plugins with D-06 weights.

        D-06 weights: DINOv2 40%, CLIP 20%, Color 10%, Part 10%,
        Pose 5%, Expression 5%, Style 10%.
        Each plugin class carries its own weight default; we instantiate
        from ALL_PLUGINS so future plugins auto-register.

        ``light=True`` drops the torch-backed plugins (DINOv2, CLIP) whose
        CPU inference dominates runtime.  Scores from the remaining
        numpy/PIL plugins are still deterministic and sufficient for
        placeholder/mock library population.
        """
        from src.identity_engine.plugins import ALL_PLUGINS

        if not light:
            return [cls() for cls in ALL_PLUGINS]

        from src.identity_engine.plugins.clip_score import CLIPScoringPlugin
        from src.identity_engine.plugins.color_verification import ColorVerificationPlugin
        from src.identity_engine.plugins.dinov2_score import DINOv2ScoringPlugin

        plugins = []
        for cls in ALL_PLUGINS:
            if cls in (CLIPScoringPlugin, DINOv2ScoringPlugin):
                continue
            if cls is ColorVerificationPlugin:
                plugins.append(cls(use_kmeans=False))
            else:
                plugins.append(cls())
        return plugins

    def score_all(self, image: Image.Image, **kwargs) -> dict[str, float]:
        """Run all plugins and return a dict of {name: score}."""
        return {p.name: p.score(image, **kwargs) for p in self.plugins}

    def brand_score(self, image: Image.Image, **kwargs) -> dict:
        """Compute the weighted Brand Score composite."""
        scores = self.score_all(image, **kwargs)
        return BrandScore.compute(scores)
