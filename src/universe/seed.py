"""Seed the studio repository from the Universe/World/Assets catalog.

Writes character records (categories ``main/family/friend/community/fantasy``)
plus world-zone records (category ``environment``) and prop records (category
``asset``) into a CharacterRepository so the Review UI and generation pipeline
can operate on the full universe.
"""

import logging
from collections import Counter

from src.models.schemas import CharacterModel
from src.universe.catalog import (
    CharacterSeed,
    EnvironmentSeed,
    PropSeed,
    discover_characters,
    discover_environments,
    discover_props,
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
    """Convert a PropSeed into an ``asset`` CharacterModel."""
    return CharacterModel(
        name=seed.name,
        category="asset",  # type: ignore[arg-type]
        species=seed.category or "prop",
        bio_data={
            "asset_id": seed.asset_id,
            "category": seed.category,
            "description": seed.description,
            "colors": seed.colors,
            "typical_location": seed.location,
        },
    )


async def seed_characters(char_repo, universe_dir: str = "Universe") -> int:
    """Seed all parsed character bios.  Returns the number created."""
    created = 0
    for seed in discover_characters(universe_dir):
        model = build_character_model(seed)
        existing = await char_repo.find_character_by_name(model.name)
        if existing is not None:
            continue
        await char_repo.save_character(model)
        created += 1
    return created


async def seed_environments(char_repo, world_dir: str = "World") -> int:
    """Seed the nine world zones.  Returns the number created."""
    created = 0
    for seed in discover_environments(world_dir):
        model = build_environment_model(seed)
        existing = await char_repo.find_character_by_name(model.name)
        if existing is not None:
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
        existing = await char_repo.find_character_by_name(model.name)
        if existing is not None:
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
        "environments": await seed_environments(char_repo, world_dir),
        "props": 0,
    }
    if include_props:
        summary["props"] = await seed_props(char_repo, world_dir, assets_dir)
    summary["total"] = sum(summary.values())
    return summary
