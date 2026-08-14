"""Tests for the batch generation runner (``src.universe.batch_generator``).

Covers backend resolution, prompt building for all three seed kinds, and an
end-to-end mock generation run that persists scored + shortlisted assets.
"""

import pytest

from src.asset_repository.sqlite_repo import SQLiteAssetRepository, SQLiteCharacterRepository
from src.generation_engine.base import GenerationBackend
from src.universe.batch_generator import BatchRunner, build_prompt, resolve_backend
from src.universe.catalog import (
    ART_DIRECTION,
    discover_characters,
    discover_environments,
    discover_props,
)


class TestResolveBackend:
    """Backend selection by name."""

    def test_mock_default(self):
        backend = resolve_backend("mock")
        assert isinstance(backend, GenerationBackend)

    def test_empty_name_defaults_to_mock(self):
        assert isinstance(resolve_backend(""), GenerationBackend)

    def test_unknown_backend_raises(self):
        with pytest.raises(ValueError):
            resolve_backend("nonexistent")

    def test_comfyui_and_cloud(self):
        # Only assert they construct without hardware (no network calls).
        assert isinstance(resolve_backend("comfyui"), GenerationBackend)
        assert isinstance(resolve_backend("cloud"), GenerationBackend)


class TestBuildPrompt:
    """Prompt construction per seed kind."""

    def test_character_prompt(self):
        seed = discover_characters("Universe")[0]
        positive, negative = build_prompt(seed, "character", "reference", "front")
        assert seed.name in positive
        assert ART_DIRECTION in positive
        assert negative

    def test_character_asset_type_variants(self):
        seed = discover_characters("Universe")[0]
        for atype in ("reference", "expression", "pose", "outfit", "accessory"):
            positive, _ = build_prompt(seed, "character", atype, "front")
            assert positive

    def test_environment_prompt(self):
        seed = discover_environments("World")[0]
        positive, negative = build_prompt(seed, "environment", "environment", "front")
        assert "Little Learning Town" in positive
        assert "**" not in positive
        assert negative

    def test_prop_prompt(self):
        seed = discover_props("World", "Assets")[0]
        positive, negative = build_prompt(seed, "prop", "prop", "front")
        assert seed.name in positive
        assert "single object" in positive
        assert negative

    def test_prop_variant_prompts(self):
        seed = discover_props("World", "Assets")[0]
        for atype, variant in (("reference", "front"), ("view", "side"),
                               ("view", "top"), ("view", "back"),
                               ("material", "wood"), ("color", "pastel_blue"),
                               ("lighting", "studio")):
            positive, negative = build_prompt(seed, "prop", atype, variant)
            assert positive
            assert negative
            assert "**" not in positive

    def test_prop_without_description_no_double_comma(self):
        seed = discover_props("World", "Assets")[0]
        # Force empty description/colors to simulate bare rows.
        seed.description = ""
        seed.colors = ""
        positive, _ = build_prompt(seed, "prop", "prop", "front")
        assert ", ," not in positive
        assert positive.startswith(seed.name)

    def test_unknown_kind_raises(self):
        seed = discover_characters("Universe")[0]
        with pytest.raises(ValueError):
            build_prompt(seed, "nope", "reference", "front")


@pytest.mark.asyncio
class TestBatchRunner:
    """End-to-end generation into SQLite with the mock backend."""

    @pytest.fixture
    def repos(self, tmp_path):
        db = str(tmp_path / "batch.db")
        return (
            SQLiteAssetRepository(db_path=db),
            SQLiteCharacterRepository(db_path=db),
        )

    async def test_generate_character_batch(self, repos):
        asset_repo, char_repo = repos
        runner = BatchRunner(asset_repo=asset_repo, char_repo=char_repo)
        seeds = discover_characters("Universe")[:2]
        result = await runner.run_seeds(
            seeds, "character", count=3, shortlist=2, batch_id="test"
        )
        assert result["items_attempted"] == 2
        assert result["items_succeeded"] == 2
        assert result["items_failed"] == 0
        assert result["total_generated"] == 6
        assert result["total_shortlisted"] == 4
        assert result["batch_id"] == "test"

    async def test_generate_environment_and_prop(self, repos):
        asset_repo, char_repo = repos
        runner = BatchRunner(asset_repo=asset_repo, char_repo=char_repo)
        envs = discover_environments("World")[:1]
        props = discover_props("World", "Assets")[:2]
        env_result = await runner.run_seeds(envs, "environment", count=2, shortlist=1)
        prop_result = await runner.run_seeds(props, "prop", count=2, shortlist=1)
        assert env_result["total_generated"] == 2
        assert prop_result["total_generated"] == 4

    async def test_assets_persisted_with_states(self, repos):
        asset_repo, char_repo = repos
        runner = BatchRunner(asset_repo=asset_repo, char_repo=char_repo)
        seeds = discover_characters("Universe")[:1]
        await runner.run_seeds(seeds, "character", count=3, shortlist=2)
        conn = asset_repo._get_conn()
        states = {
            row["state"] for row in
            conn.execute("SELECT state FROM assets").fetchall()
        }
        assert "scored" in states
        assert "shortlisted" in states

    async def test_backend_override_per_run(self, repos):
        from src.generation_engine.mock_backend import MockBackend
        asset_repo, char_repo = repos
        runner = BatchRunner(asset_repo=asset_repo, char_repo=char_repo)
        seeds = discover_characters("Universe")[:1]
        result = await runner.run_seeds(
            seeds, "character", count=2, shortlist=1, backend=MockBackend()
        )
        assert result["items_succeeded"] == 1

    async def test_rerun_skip_scored_resume_semantics(self, repos):
        """skip_scored=True treats generated-but-unshortlisted assets as done
        (Colab crash-resume), while the default re-generates them (re-try)."""
        asset_repo, char_repo = repos
        runner = BatchRunner(asset_repo=asset_repo, char_repo=char_repo)
        seeds = discover_characters("Universe")[:1]

        first = await runner.run_seeds(seeds, "character", count=2, shortlist=1)
        assert first["total_generated"] == 2

        # Simulate a batch that generated + synced images but crashed before
        # shortlisting finished: demote the shortlisted asset to "scored".
        conn = asset_repo._get_conn()
        conn.execute("UPDATE assets SET state='scored' WHERE state='shortlisted'")
        conn.commit()

        resume = await runner.run_seeds(
            seeds, "character", count=2, shortlist=1, skip_scored=True
        )
        assert resume["items_succeeded"] == 1
        assert resume["total_generated"] == 0

        retry = await runner.run_seeds(
            seeds, "character", count=2, shortlist=1
        )
        assert retry["total_generated"] == 2

    async def test_plain_rerun_skips_shortlisted(self, repos):
        """A plain rerun never duplicates already-shortlisted work."""
        asset_repo, char_repo = repos
        runner = BatchRunner(asset_repo=asset_repo, char_repo=char_repo)
        seeds = discover_characters("Universe")[:1]
        first = await runner.run_seeds(seeds, "character", count=2, shortlist=1)
        assert first["total_generated"] == 2
        second = await runner.run_seeds(
            seeds, "character", count=2, shortlist=1, skip_scored=True
        )
        assert second["items_succeeded"] == 1
        assert second["total_generated"] == 0

    async def test_on_asset_called_once_per_image(self, repos):
        """The on_asset hook fires once per saved image with full metadata."""
        asset_repo, char_repo = repos
        seen = []

        async def hook(info):
            seen.append(info)

        runner = BatchRunner(
            asset_repo=asset_repo, char_repo=char_repo, on_asset=hook
        )
        seeds = discover_characters("Universe")[:1]
        result = await runner.run_seeds(
            seeds, "character", count=3, shortlist=2
        )
        assert result["total_generated"] == 3
        assert len(seen) == 3
        first = seen[0]
        assert first["asset_type"] == "reference"
        assert first["state"] == "scored"
        assert first["asset_id"]
        assert first["character_id"]
        assert first["brand_score"] is not None

    async def test_on_asset_reports_persisted_image_path(self, repos, tmp_path):
        """With persist_images=True the hook sees the real on-disk path."""
        asset_repo, char_repo = repos
        seen = []

        async def hook(info):
            seen.append(info)

        runner = BatchRunner(
            asset_repo=asset_repo, char_repo=char_repo, on_asset=hook,
            persist_images=True,
            universe_dir=str(tmp_path / "Universe"),
            world_dir=str(tmp_path / "World"),
            assets_dir=str(tmp_path / "Assets"),
        )
        seeds = discover_characters("Universe")[:1]
        await runner.run_seeds(seeds, "character", count=1, shortlist=1)
        assert len(seen) == 1
        assert seen[0]["file_path"], "persisted image path should be reported"
        assert (tmp_path / seen[0]["file_path"]).exists()

    async def test_on_asset_hook_failure_does_not_abort_generation(self, repos):
        """A failing sync hook is swallowed; generation keeps going."""
        asset_repo, char_repo = repos

        async def bad_hook(info):
            raise RuntimeError("git push failed")

        runner = BatchRunner(
            asset_repo=asset_repo, char_repo=char_repo, on_asset=bad_hook
        )
        seeds = discover_characters("Universe")[:1]
        result = await runner.run_seeds(
            seeds, "character", count=2, shortlist=1
        )
        assert result["total_generated"] == 2
        assert result["items_failed"] == 0
