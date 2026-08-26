"""Training Engine — LoRA training abstraction with adapter pattern.

Provides the ``TrainingBackend`` ABC that all training adapters implement,
the ``TrainingConfig`` and ``TrainingResult`` dataclasses that form the
training contract, and the ``KohyaAdapter`` which wraps Kohya SS
sd-scripts for LoRA training (the Phase 1c training backend).

Additional modules:
    - ``DatasetBuilder`` — builds Kohya-compatible datasets from approved assets
    - ``VersionRegistry`` / ``LoRAVersion`` — semver-style version management
    - ``LoRABenchmark`` / ``MockScorerProvider`` — quality benchmark harness
"""

from .base import TrainingBackend, TrainingConfig, TrainingResult
from .kohya_adapter import KohyaAdapter
from .dataset_builder import DatasetBuilder, DatasetEntry, DatasetConfig, BuildResult
from .versioning import LoRAVersion, VersionRegistry, VersionRecord
from .benchmark import LoRABenchmark, BenchmarkConfig, BenchmarkResult, MockScorerProvider
from .scorer_adapter import IdentityScorerProvider

__all__ = [
    "TrainingBackend",
    "TrainingConfig",
    "TrainingResult",
    "KohyaAdapter",
    "DatasetBuilder",
    "DatasetEntry",
    "DatasetConfig",
    "BuildResult",
    "LoRAVersion",
    "VersionRegistry",
    "VersionRecord",
    "LoRABenchmark",
    "BenchmarkConfig",
    "BenchmarkResult",
    "MockScorerProvider",
    "IdentityScorerProvider",
]
