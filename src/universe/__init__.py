"""Universe — catalog, seeding, and batch generation for the studio world.

Bridges the Phase 1/2/3 world-building documents (``Universe/``, ``World/``,
``Assets/``) with the runtime pipeline (repositories, generation backends, and
the Review UI).
"""

from src.universe.catalog import (
    ART_DIRECTION,
    CharacterSeed,
    EnvironmentSeed,
    PropSeed,
    discover_characters,
    discover_environments,
    discover_props,
)
from src.universe.seed import (
    build_character_model,
    build_environment_model,
    build_prop_model,
    seed_all,
    seed_characters,
    seed_environments,
    seed_props,
)
from src.universe.batch_generator import BatchRunner, build_prompt, resolve_backend
from src.universe.sqlite_bridge import SQLiteCombinedRepo

__all__ = [
    "ART_DIRECTION",
    "CharacterSeed",
    "EnvironmentSeed",
    "PropSeed",
    "discover_characters",
    "discover_environments",
    "discover_props",
    "build_character_model",
    "build_environment_model",
    "build_prop_model",
    "seed_all",
    "seed_characters",
    "seed_environments",
    "seed_props",
    "BatchRunner",
    "build_prompt",
    "resolve_backend",
    "SQLiteCombinedRepo",
]
