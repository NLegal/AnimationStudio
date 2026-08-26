"""LoRA quality benchmark — evaluates trained LoRAs against identity standards.

Measures how well a trained LoRA preserves character identity by generating
test images and scoring them with the identity scorer, then comparing results
against a baseline of pre-LoRA generated images.
"""

import json
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Protocol


# ---------------------------------------------------------------------------
# Benchmark configuration
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkConfig:
    """Configuration for a LoRA benchmark evaluation run.

    Attributes:
        test_prompts: List of (prompt_text, asset_type) tuples to generate.
        baseline_dir: Directory containing pre-LoRA reference images.
        num_test_images: Test images to generate per prompt.
        similarity_threshold: Minimum identity score to pass (0.0–1.0).
        resolution: Image resolution for test generation.
    """

    test_prompts: list[tuple[str, str]] = field(default_factory=lambda: [
        ("happy expression, portrait", "expression"),
        ("standing, full body", "pose"),
        ("wearing default outfit, front view", "reference"),
        ("surprised expression, portrait", "expression"),
        ("waving, full body", "pose"),
    ])
    baseline_dir: Optional[Path] = None
    num_test_images: int = 5
    similarity_threshold: float = 0.90
    resolution: int = 1024


@dataclass
class BenchmarkDimension:
    """Score for a single evaluation dimension."""

    name: str
    score: float
    weight: float
    baseline_score: Optional[float] = None
    improvement: Optional[float] = None

    @property
    def passed(self) -> bool:
        return self.score >= 0.6 and (
            self.baseline_score is None or self.score >= self.baseline_score * 0.9
        )


@dataclass
class BenchmarkResult:
    """Complete result of a LoRA benchmark evaluation.

    Attributes:
        lora_path: Path to the evaluated LoRA file.
        version: LoRA version string.
        dimensions: Per-dimension scores.
        composite_score: Weighted average of all dimensions.
        baseline_composite: Composite score from baseline (if available).
        improvement: Percentage improvement over baseline.
        passed: True if all critical dimensions pass.
    """

    lora_path: Path
    version: str
    dimensions: list[BenchmarkDimension]
    composite_score: float = 0.0
    baseline_composite: Optional[float] = None
    improvement: Optional[float] = None
    passed: bool = False
    weight_coverage: float = 1.0


# ---------------------------------------------------------------------------
# Scoring provider protocol
# ---------------------------------------------------------------------------

class ScorerProvider(Protocol):
    """Protocol for an object that can score image identity consistency.

    Implementations wrap the identity scorer plugins so the benchmark
    can run without importing the full identity engine directly.
    """

    def score_identity(
        self,
        image_path: Path,
        reference_path: Optional[Path] = None,
        character_id: Optional[str] = None,
    ) -> dict[str, float]:
        """Score a generated image for identity consistency.

        Args:
            image_path: Path to the generated image.
            reference_path: Optional path to a reference image.
            character_id: Optional character identifier.

        Returns:
            Dict mapping dimension name → score (0.0–1.0).
        """
        ...


# ---------------------------------------------------------------------------
# Mock provider for testing without ML models
# ---------------------------------------------------------------------------

class MockScorerProvider:
    """Mock scorer that returns plausible random scores.

    Used for testing and development when ML models are not available.
    """

    def __init__(self, seed: int = 42) -> None:
        import random
        self._rng = random.Random(seed)

    def score_identity(
        self,
        image_path: Path,
        reference_path: Optional[Path] = None,
        character_id: Optional[str] = None,
    ) -> dict[str, float]:
        return {
            "character_consistency": self._rng.uniform(0.6, 0.98),
            "prompt_accuracy": self._rng.uniform(0.6, 0.98),
            "color_harmony": self._rng.uniform(0.6, 0.98),
            "facial_appeal": self._rng.uniform(0.6, 0.98),
            "silhouette_recognizability": self._rng.uniform(0.6, 0.98),
            "child_friendliness": self._rng.uniform(0.6, 0.98),
            "style_consistency": self._rng.uniform(0.6, 0.98),
        }


# ---------------------------------------------------------------------------
# Benchmark weights
# ---------------------------------------------------------------------------

_BENCHMARK_WEIGHTS: dict[str, float] = {
    "character_consistency": 0.40,
    "prompt_accuracy": 0.20,
    "color_harmony": 0.10,
    "facial_appeal": 0.10,
    "silhouette_recognizability": 0.05,
    "child_friendliness": 0.05,
    "style_consistency": 0.10,
}


# ---------------------------------------------------------------------------
# Main benchmark class
# ---------------------------------------------------------------------------

class LoRABenchmark:
    """Evaluates trained LoRA quality against identity standards.

    Usage::

        benchmark = LoRABenchmark(scorer_provider=MockScorerProvider())
        result = benchmark.evaluate(
            lora_path=Path("/output/lily-bunny_v0.1.safetensors"),
            character_id="lily-bunny",
        )
        print(f"Composite: {result.composite_score:.2%}")
    """

    def __init__(
        self,
        scorer_provider: Optional[ScorerProvider] = None,
        config: Optional[BenchmarkConfig] = None,
    ):
        """Initialise the benchmark.

        Args:
            scorer_provider: Provider for identity scoring.
                Defaults to MockScorerProvider for safe fallback.
            config: Benchmark configuration.  Uses defaults if not provided.
        """
        self._scorer = scorer_provider or MockScorerProvider()
        self._config = config or BenchmarkConfig()

    def evaluate(
        self,
        lora_path: Path,
        character_id: str,
        test_images: Optional[list[Path]] = None,
    ) -> BenchmarkResult:
        """Evaluate a trained LoRA.

        If *test_images* are provided they are scored directly.  Otherwise
        the benchmark generates test images using the LoRA (requires a
        generation backend with LoRA loading support — currently
        documented as a stub for integration).

        Args:
            lora_path: Path to the LoRA .safetensors file.
            character_id: Character identifier for scoring context.
            test_images: Optional list of pre-generated test images.

        Returns:
            A BenchmarkResult with per-dimension and composite scores.
        """
        if not lora_path.exists():
            return BenchmarkResult(
                lora_path=lora_path,
                version="unknown",
                dimensions=[],
                composite_score=0.0,
                passed=False,
            )

        # When test images are provided, score them directly.
        # Otherwise attempt generation (may fail without GPU — caller
        # should provide images or use a mock for testing).
        if test_images:
            images_to_score = list(test_images)
        else:
            images_to_score = self._generate_test_images(lora_path, character_id)

        if not images_to_score:
            warnings.warn("No test images available for benchmarking")
            return BenchmarkResult(
                lora_path=lora_path,
                version="unknown",
                dimensions=[],
                composite_score=0.0,
                passed=False,
            )

        baseline_images = self._load_baseline_images(character_id)

        all_dim_scores: dict[str, list[float]] = {}
        for img in images_to_score:
            scores = self._scorer.score_identity(
                image_path=img,
                reference_path=baseline_images[0] if baseline_images else None,
                character_id=character_id,
            )
            for dim_name, score in scores.items():
                if dim_name not in all_dim_scores:
                    all_dim_scores[dim_name] = []
                all_dim_scores[dim_name].append(score)

        baseline_dim_scores: dict[str, list[float]] = {}
        for img in baseline_images:
            scores = self._scorer.score_identity(
                image_path=img,
                character_id=character_id,
            )
            for dim_name, score in scores.items():
                if dim_name not in baseline_dim_scores:
                    baseline_dim_scores[dim_name] = []
                baseline_dim_scores[dim_name].append(score)

        import numpy as np

        dimensions: list[BenchmarkDimension] = []
        composite_total = 0.0
        matched_weight_sum = 0.0
        total_canonical_weight = sum(_BENCHMARK_WEIGHTS.values())
        baseline_total = 0.0

        for dim_name, weight in _BENCHMARK_WEIGHTS.items():
            scores = all_dim_scores.get(dim_name)
            if scores is None:
                # Dimension absent from provider output — skip entirely;
                # weight excluded from numerator and denominator (A7 honesty).
                continue
            avg_score = float(np.mean(scores)) if scores else 0.0

            baseline_avg: Optional[float] = None
            improvement: Optional[float] = None
            bl_scores = baseline_dim_scores.get(dim_name, [])
            if bl_scores:
                baseline_avg = float(np.mean(bl_scores))
                if baseline_avg > 0:
                    improvement = (avg_score - baseline_avg) / baseline_avg

            dimensions.append(BenchmarkDimension(
                name=dim_name,
                score=round(avg_score, 4),
                weight=weight,
                baseline_score=round(baseline_avg, 4) if baseline_avg is not None else None,
                improvement=round(improvement, 4) if improvement is not None else None,
            ))
            composite_total += avg_score * weight
            matched_weight_sum += weight
            if baseline_avg is not None:
                baseline_total += baseline_avg * weight

        weight_coverage = (
            matched_weight_sum / total_canonical_weight
            if total_canonical_weight > 0 else 0.0
        )
        weight_coverage = round(weight_coverage, 4)
        composite_score = composite_total / matched_weight_sum if matched_weight_sum > 0 else 0.0
        composite_score = round(composite_score, 4)
        baseline_composite = (
            baseline_total / matched_weight_sum if (matched_weight_sum > 0 and baseline_total > 0)
            else None
        )

        overall_improvement: Optional[float] = None
        if baseline_composite is not None and baseline_composite > 0:
            overall_improvement = (
                (composite_score - baseline_composite) / baseline_composite
            )

        passed = (
            len(dimensions) > 0
            and composite_score >= self._config.similarity_threshold
            and weight_coverage >= 1.0
        )

        return BenchmarkResult(
            lora_path=lora_path,
            version=self._derive_version(lora_path),
            dimensions=dimensions,
            composite_score=round(composite_score, 4),
            baseline_composite=round(baseline_composite, 4) if baseline_composite is not None else None,
            improvement=round(overall_improvement, 4) if overall_improvement is not None else None,
            passed=passed,
            weight_coverage=round(weight_coverage, 4),
        )

    def _generate_test_images(
        self,
        lora_path: Path,
        character_id: str,
    ) -> list[Path]:
        """Generate test images using the trained LoRA.

        **Stub**: This method documents the intended integration point.
        Production use requires a generation backend with LoRA loading
        support (e.g. FluxPipeline with LoRA weights).  For testing,
        callers should provide pre-generated *test_images* directly.

        Args:
            lora_path: Path to the LoRA safetensors file.
            character_id: Character identifier.

        Returns:
            Empty list — override or provide test images directly.
        """
        warnings.warn(
            f"LoRA test image generation not implemented. "
            f"Provide test_images directly or use MockScorerProvider. "
            f"LoRA: {lora_path}, Character: {character_id}"
        )
        return []

    def _load_baseline_images(
        self,
        character_id: str,
    ) -> list[Path]:
        """Load baseline images for *character_id*.

        Baseline images are pre-LoRA generated images stored in
        *baseline_dir* / {character_id} /.

        Args:
            character_id: Character identifier.

        Returns:
            List of baseline image paths, or empty list if unavailable.
        """
        if self._config.baseline_dir is None:
            return []
        baseline_char_dir = self._config.baseline_dir / character_id
        if not baseline_char_dir.exists():
            return []
        return sorted(
            p for p in baseline_char_dir.iterdir()
            if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
        )

    @staticmethod
    def _derive_version(lora_path: Path) -> str:
        """Extract version string from LoRA filename.

        Expects format: ``{character_id}_v{major}.{minor}.safetensors``

        Args:
            lora_path: Path to the LoRA file.

        Returns:
            Version string or ``"unknown"`` if parsing fails.
        """
        import re
        stem = lora_path.stem
        match = re.search(r"_v(\d+\.\d+)$", stem)
        if match:
            return f"v{match.group(1)}"
        return "unknown"

    def report(self, result: BenchmarkResult) -> str:
        """Generate a human-readable benchmark report.

        Args:
            result: The BenchmarkResult to report.

        Returns:
            A formatted markdown string with the full evaluation report.
        """
        lines = [
            "# LoRA Benchmark Report",
            "",
            f"**LoRA:** `{result.lora_path}`",
            f"**Version:** {result.version}",
            f"**Status:** {'✅ PASSED' if result.passed else '❌ FAILED'}",
            "",
            "## Composite Scores",
            "",
            f"| Metric | Score |",
            f"|--------|-------|",
            f"| Composite | {result.composite_score:.2%} |",
        ]

        if result.weight_coverage < 1.0:
            lines.append(
                f"| Weight Coverage | {result.weight_coverage:.0%} "
                f"(partial — gate requires 100%) |"
            )

        if result.baseline_composite is not None:
            lines.append(f"| Baseline | {result.baseline_composite:.2%} |")
            if result.improvement is not None:
                sign = "+" if result.improvement >= 0 else ""
                lines.append(f"| Improvement | {sign}{result.improvement:.2%} |")

        lines += [
            "",
            "## Per-Dimension Scores",
            "",
            "| Dimension | Score | Weight | Baseline | Improvement | Pass |",
            "|-----------|-------|--------|----------|-------------|------|",
        ]

        for dim in result.dimensions:
            baseline_str = f"{dim.baseline_score:.2%}" if dim.baseline_score is not None else "—"
            improvement_str = f"{dim.improvement:+.2%}" if dim.improvement is not None else "—"
            pass_str = "✅" if dim.passed else "❌"
            lines.append(
                f"| {dim.name} | {dim.score:.2%} | {dim.weight:.0%} | "
                f"{baseline_str} | {improvement_str} | {pass_str} |"
            )

        lines.append("")
        return "\n".join(lines)
