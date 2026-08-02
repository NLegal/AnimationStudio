"""Tests for universe seeding (``src.universe.seed``).

Verifies that catalog seeds convert into persistent CharacterModels and that
``seed_all`` writes them into a CharacterRepository idempotently.
"""

import pytest

from src.asset_repository.sqlite_repo import SQLiteCharacterRepository
from src.universe.catalog import (
    discover_backgrounds,
    discover_characters,
    discover_environments,
    discover_props,
    discover_vehicles,
    discover_world_environments,
)
from src.universe.seed import (
    build_background_model,
    build_character_model,
    build_environment_model,
    build_prop_model,
    build_vehicle_model,
    seed_all,
)


class TestBuildModels:
    """Seed dataclasses convert into the persistent model types."""

    def test_build_character_model(self):
        seed = discover_characters("Universe")[0]
        model = build_character_model(seed)
        assert model.name == seed.name
        assert model.category == seed.category
        assert model.species == seed.species
        assert model.bio_data["appearance"] == seed.appearance

    def test_build_environment_model(self):
        seed = discover_environments("World")[0]
        model = build_environment_model(seed)
        assert model.category == "environment"
        assert model.bio_data["prompt"] == seed.prompt
        assert model.bio_data["identifier"] == seed.identifier

    def test_build_prop_model(self):
        seed = discover_props("World", "Assets")[0]
        model = build_prop_model(seed)
        assert model.category == "asset"
        assert model.name == seed.name

    def test_build_vehicle_model(self):
        seed = discover_vehicles("World")[0]
        model = build_vehicle_model(seed)
        assert model.category == "vehicle"
        assert model.bio_data["asset_id"].startswith("VEH_")

    def test_build_background_model(self):
        seed = discover_backgrounds("World")[0]
        model = build_background_model(seed)
        assert model.category == "background"
        assert model.bio_data["asset_id"].startswith("BG_")


@pytest.mark.asyncio
class TestSeedAll:
    """End-to-end seeding into a real repository."""

    @pytest.fixture
    def char_repo(self, tmp_path):
        return SQLiteCharacterRepository(db_path=str(tmp_path / "seed.db"))

    async def test_seeds_full_catalog(self, char_repo):
        summary = await seed_all(char_repo)
        assert summary["characters"] == 39
        assert summary["zones"] == 9
        assert summary["locations"] == len(discover_world_environments("World"))
        assert summary["vehicles"] == len(discover_vehicles("World"))
        assert summary["backgrounds"] == len(discover_backgrounds("World"))
        assert summary["props"] == len(discover_props("World", "Assets"))
        assert summary["total"] == sum(
            summary[k] for k in ("characters", "zones", "locations",
                                 "vehicles", "backgrounds", "props")
        )

    async def test_seeding_is_idempotent(self, char_repo):
        await seed_all(char_repo)
        second = await seed_all(char_repo)
        assert second["total"] == 0
        chars = await char_repo.list_characters()
        assert len(chars) == 1048

    async def test_categories_in_repo(self, char_repo):
        await seed_all(char_repo)
        chars = await char_repo.list_characters()
        categories = {c.category for c in chars}
        assert {"main", "environment", "asset", "vehicle", "background"} <= categories

    async def test_seed_excludes_props_when_requested(self, char_repo):
        summary = await seed_all(char_repo, include_props=False)
        assert summary["props"] == 0
        assert summary["characters"] == 39
        assert summary["zones"] == 9
        assert summary["locations"] == len(discover_world_environments("World"))
