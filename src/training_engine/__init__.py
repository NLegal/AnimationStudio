"""Training Engine — LoRA training abstraction with adapter pattern.

Provides the ``TrainingBackend`` ABC that all training adapters implement,
the ``TrainingConfig`` and ``TrainingResult`` dataclasses that form the
training contract, and the ``KohyaAdapter`` which wraps Kohya SS
sd-scripts for LoRA training (the Phase 1 training backend).
"""

from .base import TrainingBackend, TrainingConfig, TrainingResult
from .kohya_adapter import KohyaAdapter

__all__ = [
    "TrainingBackend",
    "TrainingConfig",
    "TrainingResult",
    "KohyaAdapter",
]
