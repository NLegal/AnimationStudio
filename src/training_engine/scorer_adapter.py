"""ScorerProvider adapter — bridges identity_engine.IdentityScorer into LoRABenchmark.

The benchmark's ``ScorerProvider`` protocol expects a ``score_identity`` method
that takes file paths and returns ``dict[str, float]`` keyed by dimension name.
The identity engine's ``IdentityScorer`` works with PIL images and returns dicts
keyed by plugin names.

This adapter opens images with PIL, delegates to the wrapped scorer, and filters
the returned mapping to keys present in the canonical benchmark weight table —
dropping unknown plugin names with a warning so stray future plugins cannot
silently skew composites.
"""

import warnings
from pathlib import Path
from typing import Optional

from PIL import Image

from src.training_engine.benchmark import _BENCHMARK_WEIGHTS


class IdentityScorerProvider:
    """Adapts ``identity_engine.IdentityScorer`` to the ``ScorerProvider`` protocol.

    Usage::

        provider = IdentityScorerProvider()  # light=True, offline-safe
        benchmark = LoRABenchmark(scorer_provider=provider)

    For production scoring on Colab (full plugin stack)::

        provider = IdentityScorerProvider(light=False)

    Or inject a pre-built scorer for testing::

        from src.identity_engine import IdentityScorer
        scorer = IdentityScorer(light=True)
        provider = IdentityScorerProvider(scorer=scorer)
    """

    def __init__(
        self,
        scorer: Optional[object] = None,
        light: bool = True,
    ) -> None:
        """Initialise the adapter.

        Args:
            scorer: An ``IdentityScorer`` instance (dependency injection for
                tests).  When *None* a fresh ``IdentityScorer(light=light)``
                is constructed.
            light: Passed to ``IdentityScorer()`` when *scorer* is *None*.
                ``light=True`` drops torch-backed plugins (offline-safe).
        """
        if scorer is not None:
            self._scorer = scorer
        else:
            from src.identity_engine import IdentityScorer
            self._scorer = IdentityScorer(light=light)

    def score_identity(
        self,
        image_path: Path,
        reference_path: Optional[Path] = None,
        character_id: Optional[str] = None,
    ) -> dict[str, float]:
        """Score a generated image for identity consistency.

        Opens the target image (and optionally the reference) with PIL,
        delegates to the wrapped scorer's ``score_all``, and filters the
        result to keys present in the canonical benchmark weight table.

        Args:
            image_path: Path to the generated image.
            reference_path: Optional path to a reference image.
            character_id: Optional character identifier (accepted for protocol
                compliance; forwarded to the scorer's ``score_all`` via kwargs
                if the underlying implementation uses it).

        Returns:
            Dict mapping canonical dimension name → score (0.0–1.0).
        """
        img = Image.open(image_path).convert("RGB")

        kwargs: dict = {}
        if reference_path is not None:
            kwargs["reference"] = Image.open(reference_path).convert("RGB")
        if character_id is not None:
            kwargs["character_id"] = character_id

        raw_scores = self._scorer.score_all(img, **kwargs)

        # Filter to canonical benchmark keys; drop unknowns with a warning
        result: dict[str, float] = {}
        for name, score in raw_scores.items():
            if name in _BENCHMARK_WEIGHTS:
                result[name] = score
            else:
                warnings.warn(
                    f"Plugin '{name}' not in benchmark weight table — "
                    f"score {score:.4f} dropped",
                    stacklevel=2,
                )

        return result
