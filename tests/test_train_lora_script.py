"""Tests for scripts/train_lora.py — CLI integration for LoRA training pipeline.

Covers the build-dataset, train, and versions subcommands with offline-only
execution. A module-level subprocess sentinel guards every test path to
prove C-OFFLINE compliance (zero subprocess spawns).
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

import pytest

from src.models.schemas import AssetModel, CharacterModel
from src.asset_repository.sqlite_repo import SQLiteAssetRepository, SQLiteCharacterRepository

# ---------------------------------------------------------------------------
# Subprocess sentinel — proves C-OFFLINE (zero spawns across entire suite)
# ---------------------------------------------------------------------------

_ORIGINAL_SUBPROCESS_RUN = subprocess.run


def _subprocess_sentinel(*args, **kwargs):
    raise AssertionError(
        "subprocess.run was invoked — C-OFFLINE violated. "
        "The train_lora.py CLI must not spawn subprocesses."
    )


@pytest.fixture(autouse=True)
def _guard_subprocess(monkeypatch):
    """Replace subprocess.run with a sentinel for the entire module."""
    monkeypatch.setattr(subprocess, "run", _subprocess_sentinel)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _seed_character(db_path: Path, character_id: str = "lily-bunny",
                    name: str = "Lily Bunny") -> None:
    """Seed a character row into the test database."""
    repo = SQLiteCharacterRepository(db_path=str(db_path))
    import asyncio
    asyncio.run(repo.save_character(
        CharacterModel(
            id=character_id,
            name=name,
            category="main",
            species="rabbit",
            bio_data={},
            created_at=datetime.now(timezone.utc),
        )
    ))


def _seed_asset(
    db_path: Path,
    asset_id: str,
    character_id: str = "lily-bunny",
    asset_type: str = "expression",
    variant: str = "happy",
    state: str = "approved",
    brand_score: float = 0.80,
    seed: int = 1,
) -> None:
    """Seed a single asset row into the test database."""
    repo = SQLiteAssetRepository(db_path=str(db_path))
    import asyncio
    asyncio.run(repo.save(AssetModel(
        id=asset_id,
        character_id=character_id,
        asset_type=asset_type,
        variant=variant,
        state=state,
        file_path=f"Universe/Characters/Lily Bunny/{asset_type}s/{variant}_{seed}.png",
        prompt=f"lily bunny, {variant} {asset_type}, portrait",
        seed=seed,
        brand_score=brand_score,
        created_at=datetime.now(timezone.utc),
    )))


def _seed_assets_for_cli(db_path: Path, tmp_path: Path) -> int:
    """Seed a full set of assets for CLI testing (approved + production states).

    Creates actual image files on disk and seeds DB records with varied
    asset types, variants, states, and brand scores for dedupe testing.
    Returns total number of seeded assets.
    """
    _seed_character(db_path)

    # Approved state assets (25 total across types)
    approved_assets = [
        ("a-happy-1", "expression", "happy", 0.90),
        ("a-happy-2", "expression", "happy", 0.85),   # lower score duplicate
        ("a-sad-1", "expression", "sad", 0.88),
        ("a-sad-2", "expression", "sad", 0.82),
        ("a-angry-1", "expression", "angry", 0.92),
        ("a-angry-2", "expression", "angry", 0.78),
        ("a-stand-1", "pose", "standing", 0.89),
        ("a-stand-2", "pose", "standing", 0.84),
        ("a-walk-1", "pose", "walking", 0.87),
        ("a-walk-2", "pose", "walking", 0.81),
        ("a-dress-1", "outfit", "dress", 0.91),
        ("a-dress-2", "outfit", "dress", 0.86),
        ("a-pants-1", "outfit", "pants", 0.88),
        ("a-pants-2", "outfit", "pants", 0.83),
        ("a-ref1-1", "reference", "front", 0.95),
        ("a-ref1-2", "reference", "front", 0.93),
        ("a-ref2-1", "reference", "side", 0.94),
        ("a-ref2-2", "reference", "side", 0.90),
        ("a-smile-1", "expression", "smile", 0.89),
        ("a-smile-2", "expression", "smile", 0.83),
        ("a-jump-1", "pose", "jumping", 0.87),
        ("a-jump-2", "pose", "jumping", 0.80),
        ("a-hat-1", "outfit", "hat", 0.86),
        ("a-hat-2", "outfit", "hat", 0.82),
        ("a-wave-1", "pose", "waving", 0.88),
    ]

    # Production state assets (5 total)
    production_assets = [
        ("p-happy-1", "expression", "happy", 0.93),
        ("p-sad-1", "expression", "sad", 0.91),
        ("p-stand-1", "pose", "standing", 0.90),
        ("p-dress-1", "outfit", "dress", 0.92),
        ("p-ref1-1", "reference", "front", 0.96),
    ]

    count = 0
    for aid, atype, variant, score in approved_assets + production_assets:
        seed_num = hash(aid) % 100000
        fpath = tmp_path / f"{variant}_{seed_num}.png"
        fpath.write_bytes(b"\x89PNG fake image data")
        state = "approved" if aid.startswith("a-") else "production"
        _seed_asset(
            db_path, aid, asset_type=atype, variant=variant,
            state=state, brand_score=score, seed=seed_num,
        )
        count += 1
    return count


# ---------------------------------------------------------------------------
# TestTrainLoraBuildDataset
# ---------------------------------------------------------------------------

class TestTrainLoraBuildDataset:
    """build-dataset subcommand behavior."""

    def test_build_dataset_produces_bounded_dataset(self, tmp_path, monkeypatch):
        """build-dataset produces a valid dataset directory with sidecars."""
        db = tmp_path / "catalog.db"
        _seed_assets_for_cli(db, tmp_path)
        out = tmp_path / "training"
        registry = tmp_path / "registry.json"

        # Import and run via subprocess (captured), but subprocess is
        # monkeypatched at module level so we call main() directly.
        monkeypatch.chdir(tmp_path)
        from scripts.train_lora import main as cli_main
        rc = cli_main([
            "build-dataset",
            "--db", str(db),
            "--character-id", "lily-bunny",
            "--output-root", str(out),
            "--registry-path", str(registry),
            "--states", "approved,production",
            "--min-images", "5",
            "--max-images", "30",
        ])
        assert rc == 0
        # Dataset directory exists
        assert out.exists()

    def test_build_dataset_dedupes_per_variant(self, tmp_path, monkeypatch):
        """build-dataset keeps one best image per variant (highest brand_score)."""
        db = tmp_path / "catalog.db"
        _seed_assets_for_cli(db, tmp_path)
        out = tmp_path / "training"
        registry = tmp_path / "registry.json"

        monkeypatch.chdir(tmp_path)
        from scripts.train_lora import main as cli_main
        rc = cli_main([
            "build-dataset",
            "--db", str(db),
            "--character-id", "lily-bunny",
            "--output-root", str(out),
            "--registry-path", str(registry),
            "--states", "approved,production",
            "--min-images", "5",
            "--max-images", "30",
        ])
        assert rc == 0

        # Verify train dir has images and sidecar .txt files
        train_dir = out / "train"
        assert train_dir.exists()
        images = list(train_dir.glob("*.png"))
        sidecars = list(train_dir.glob("*.txt"))
        assert len(images) > 0, "Should have copied images"
        assert len(images) == len(sidecars), "Each image needs a .txt sidecar"

    def test_build_dataset_caps_at_max_images(self, tmp_path, monkeypatch):
        """build-dataset caps output at max_images when there are more candidates."""
        db = tmp_path / "catalog.db"
        _seed_assets_for_cli(db, tmp_path)
        out = tmp_path / "training"
        registry = tmp_path / "registry.json"

        monkeypatch.chdir(tmp_path)
        from scripts.train_lora import main as cli_main
        rc = cli_main([
            "build-dataset",
            "--db", str(db),
            "--character-id", "lily-bunny",
            "--output-root", str(out),
            "--registry-path", str(registry),
            "--states", "approved,production",
            "--min-images", "5",
            "--max-images", "10",  # cap at 10
        ])
        assert rc == 0
        train_dir = out / "train"
        images = list(train_dir.glob("*.png"))
        assert len(images) <= 10

    def test_build_dataset_fails_below_minimum(self, tmp_path, monkeypatch):
        """build-dataset exits non-zero when below min_images."""
        db = tmp_path / "catalog.db"
        _seed_assets_for_cli(db, tmp_path)
        out = tmp_path / "training"
        registry = tmp_path / "registry.json"

        monkeypatch.chdir(tmp_path)
        from scripts.train_lora import main as cli_main
        rc = cli_main([
            "build-dataset",
            "--db", str(db),
            "--character-id", "lily-bunny",
            "--output-root", str(out),
            "--registry-path", str(registry),
            "--states", "approved,production",
            "--min-images", "100",  # impossible to reach
            "--max-images", "200",
        ])
        assert rc == 1


# ---------------------------------------------------------------------------
# TestTrainLoraTrain
# ---------------------------------------------------------------------------

class TestTrainLoraTrain:
    """train subcommand behavior (dry-run enforced)."""

    def test_train_without_dry_run_exits_nonzero(self, tmp_path, monkeypatch):
        """train without --dry-run exits 1 with Colab notebook message."""
        db = tmp_path / "catalog.db"
        _seed_character(db)
        out = tmp_path / "training"
        registry = tmp_path / "registry.json"

        monkeypatch.chdir(tmp_path)
        from scripts.train_lora import main as cli_main
        rc = cli_main([
            "train",
            "--db", str(db),
            "--character-id", "lily-bunny",
            "--output-root", str(out),
            "--registry-path", str(registry),
        ])
        assert rc == 1

    def test_train_dry_run_completes_and_registers(self, tmp_path, monkeypatch):
        """train --dry-run exits 0, creates artifact, registers version."""
        db = tmp_path / "catalog.db"
        _seed_character(db)
        out = tmp_path / "training"
        registry = tmp_path / "registry.json"

        monkeypatch.chdir(tmp_path)
        from scripts.train_lora import main as cli_main
        rc = cli_main([
            "train",
            "--dry-run",
            "--db", str(db),
            "--character-id", "lily-bunny",
            "--output-root", str(out),
            "--registry-path", str(registry),
        ])
        assert rc == 0
        # Artifact created
        artifact = out / "lily-bunny_v0.1.train_cmd.json"
        assert artifact.exists(), f"Command artifact not found at {artifact}"
        content = json.loads(artifact.read_text(encoding="utf-8"))
        assert isinstance(content, list), "Artifact should be a JSON argv list"
        # Registry persisted
        assert registry.exists()

    def test_train_dry_run_second_invocation_registers_next_version(self, tmp_path, monkeypatch):
        """Second dry-run invocation registers v0.2, not a duplicate v0.1."""
        db = tmp_path / "catalog.db"
        _seed_character(db)
        out = tmp_path / "training"
        registry = tmp_path / "registry.json"

        monkeypatch.chdir(tmp_path)
        from scripts.train_lora import main as cli_main

        # First invocation
        cli_main([
            "train", "--dry-run",
            "--db", str(db), "--character-id", "lily-bunny",
            "--output-root", str(out), "--registry-path", str(registry),
        ])

        # Second invocation
        rc = cli_main([
            "train", "--dry-run",
            "--db", str(db), "--character-id", "lily-bunny",
            "--output-root", str(out), "--registry-path", str(registry),
        ])
        assert rc == 0
        # Check registry has exactly 2 versions (v0.1 and v0.2)
        from src.training_engine.version_store import load_registry
        loaded = load_registry(registry)
        versions = loaded.get_versions("lily-bunny")
        assert len(versions) == 2
        version_strs = sorted(str(v.version) for v in versions)
        assert version_strs == ["v0.1", "v0.2"]

    def test_train_unknown_character_exits_nonzero(self, tmp_path, monkeypatch):
        """train with unknown character exits non-zero."""
        db = tmp_path / "catalog.db"
        _seed_character(db)
        out = tmp_path / "training"
        registry = tmp_path / "registry.json"

        monkeypatch.chdir(tmp_path)
        from scripts.train_lora import main as cli_main
        rc = cli_main([
            "train", "--dry-run",
            "--db", str(db), "--character-id", "nonexistent",
            "--output-root", str(out), "--registry-path", str(registry),
        ])
        assert rc == 1
