"""Seed the studio repository from the Universe/World/Assets catalog.

Writes character records (categories ``main/family/friend/community/fantasy``)
plus world-zone records (category ``environment``) and prop records (category
``asset``) into a CharacterRepository so the Review UI and generation pipeline
can operate on the full universe.
"""

import logging
from collections import Counter
from typing import Optional

from src.models.schemas import CharacterModel
from src.universe.catalog import (
    CharacterSeed,
    EnvironmentSeed,
    PropSeed,
    discover_backgrounds,
    discover_characters,
    discover_environments,
    discover_props,
    discover_vehicles,
    discover_world_environments,
)

logger = logging.getLogger(__name__)


def build_character_model(seed: CharacterSeed) -> CharacterModel:
    """Convert a CharacterSeed into a persistent CharacterModel."""
    bio = dict(seed.bio_data)
    bio.setdefault("appearance", seed.appearance)
    bio.setdefault("default_outfit", seed.default_outfit)
    return CharacterModel(
        name=seed.name,
        category=seed.category,  # type: ignore[arg-type]
        species=seed.species,
        bio_data=bio,
    )


def build_environment_model(seed: EnvironmentSeed) -> CharacterModel:
    """Convert an EnvironmentSeed into an ``environment`` CharacterModel."""
    bio = {
        "zone": seed.zone,
        "identifier": seed.identifier,
        "description": seed.description,
        "prompt": seed.prompt,
        "negative_prompt": seed.negative_prompt,
    }
    bio.update(seed.bio_data)
    return CharacterModel(
        name=seed.name,
        category="environment",  # type: ignore[arg-type]
        species=seed.zone or "environment",
        bio_data=bio,
    )


def build_prop_model(seed: PropSeed) -> CharacterModel:
    """Convert a PropSeed into an ``asset``/``vehicle``/``background`` model."""
    category = {
        "vehicle": "vehicle",
        "background": "background",
    }.get(seed.category, "asset")
    return CharacterModel(
        name=seed.name,
        category=category,  # type: ignore[arg-type]
        species=seed.category or "prop",
        bio_data={
            "asset_id": seed.asset_id,
            "category": seed.category,
            "description": seed.description,
            "colors": seed.colors,
            "typical_location": seed.location,
        },
    )


def build_vehicle_model(seed: PropSeed) -> CharacterModel:
    """Convert a vehicle PropSeed into a ``vehicle`` CharacterModel."""
    return build_prop_model(seed)


def build_background_model(seed: PropSeed) -> CharacterModel:
    """Convert a background PropSeed into a ``background`` CharacterModel."""
    return build_prop_model(seed)


async def _find_existing(char_repo, model) -> Optional[object]:
    """Look up an existing record, preferring a category-exact match.

    Falls back to a name-only match for repositories that don't implement the
    category-aware lookup.  The category-exact match keeps world locations,
    vehicles and props that share a display name (e.g. "Pond", "Monkey Bars")
    from colliding during repeated seeding.
    """
    try:
        return await char_repo.find_character_by_name_and_category(
            model.name, model.category
        )
    except (NotImplementedError, AttributeError):
        return await char_repo.find_character_by_name(model.name)


async def seed_characters(char_repo, universe_dir: str = "Universe") -> int:
    """Seed all parsed character bios.  Returns the number created."""
    created = 0
    for seed in discover_characters(universe_dir):
        model = build_character_model(seed)
        if await _find_existing(char_repo, model) is not None:
            continue
        await char_repo.save_character(model)
        created += 1
    return created


async def seed_environments(char_repo, world_dir: str = "World") -> int:
    """Seed the nine world zones.  Returns the number created."""
    created = 0
    for seed in discover_environments(world_dir):
        model = build_environment_model(seed)
        if await _find_existing(char_repo, model) is not None:
            continue
        await char_repo.save_character(model)
        created += 1
    return created


async def seed_world_locations(char_repo, world_dir: str = "World") -> int:
    """Seed every named location from the Phase 2 zone bibles.

    Uses ``discover_world_environments`` (137 ENV_* entries) rather than the
    nine top-level zone summaries.  Returns the number created.
    """
    created = 0
    for seed in discover_world_environments(world_dir):
        model = build_environment_model(seed)
        if await _find_existing(char_repo, model) is not None:
            continue
        await char_repo.save_character(model)
        created += 1
    return created


async def seed_vehicles(char_repo, world_dir: str = "World") -> int:
    """Seed the vehicle library.  Returns the number created."""
    created = 0
    for seed in discover_vehicles(world_dir):
        model = build_prop_model(seed)
        if await _find_existing(char_repo, model) is not None:
            continue
        await char_repo.save_character(model)
        created += 1
    return created


async def seed_backgrounds(char_repo, world_dir: str = "World") -> int:
    """Seed the background library.  Returns the number created."""
    created = 0
    for seed in discover_backgrounds(world_dir):
        model = build_prop_model(seed)
        if await _find_existing(char_repo, model) is not None:
            continue
        await char_repo.save_character(model)
        created += 1
    return created


async def seed_props(char_repo, world_dir: str = "World", assets_dir: str = "Assets") -> int:
    """Seed reusable props/assets.  Returns the number created.

    Duplicate display names are made unique deterministically (suffixed with
    the stable asset id) so that re-seeding is idempotent.
    """
    seeds = discover_props(world_dir, assets_dir)
    name_counts = Counter(s.name for s in seeds)
    created = 0
    for seed in seeds:
        model = build_prop_model(seed)
        if name_counts[seed.name] > 1:
            model.name = f"{seed.name} ({seed.asset_id})"
        if await _find_existing(char_repo, model) is not None:
            continue
        await char_repo.save_character(model)
        created += 1
    return created


async def seed_all(
    char_repo,
    universe_dir: str = "Universe",
    world_dir: str = "World",
    assets_dir: str = "Assets",
    include_props: bool = True,
) -> dict:
    """Seed the full universe.  Returns a summary dict with per-scope counts.

    Safe to call repeatedly — records already present are skipped.
    """
    summary = {
        "characters": await seed_characters(char_repo, universe_dir),
        "zones": await seed_environments(char_repo, world_dir),
        "locations": await seed_world_locations(char_repo, world_dir),
        "vehicles": await seed_vehicles(char_repo, world_dir),
        "backgrounds": await seed_backgrounds(char_repo, world_dir),
        "props": 0,
    }
    if include_props:
        summary["props"] = await seed_props(char_repo, world_dir, assets_dir)
    summary["total"] = sum(summary.values())
    return summary
