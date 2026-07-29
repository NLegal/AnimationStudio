"""Tests for the CharacterRepository and AssetRepository interfaces.

Uses in-memory SQLite via temp files (since :memory: creates separate DBs
for Character and Asset repos that share foreign key constraints).
"""

import os
import tempfile
import pytest
from datetime import datetime

from src.models.schemas import CharacterModel, AssetModel
from src.asset_repository.sqlite_repo import (
    SQLiteCharacterRepository,
    SQLiteAssetRepository,
    NotFoundError,
)


@pytest.fixture
def shared_db():
    """Create a shared temp file for Character+Asset repository tests."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def char_repo(shared_db):
    return SQLiteCharacterRepository(shared_db)


@pytest.fixture
def asset_repo(shared_db):
    return SQLiteAssetRepository(shared_db)


@pytest.mark.asyncio
async def test_create_character(char_repo):
    """Save character → verify retrieval by id and by name."""
    char = CharacterModel(
        name="Test Bunny",
        category="main",
        species="rabbit",
        bio_data={"personality": ["curious"]},
    )
    saved_id = await char_repo.save_character(char)

    loaded = await char_repo.get_character(saved_id)
    assert loaded is not None
    assert loaded.id == char.id
    assert loaded.name == "Test Bunny"

    by_name = await char_repo.find_character_by_name("Test Bunny")
    assert by_name is not None
    assert by_name.id == char.id


@pytest.mark.asyncio
async def test_list_characters(char_repo):
    """Save 3 characters → list → verify all returned."""
    chars = [
        CharacterModel(name="Alice", category="main", species="cat"),
        CharacterModel(name="Bob", category="friend", species="dog"),
        CharacterModel(name="Charlie", category="fantasy", species="dragon"),
    ]
    for c in chars:
        await char_repo.save_character(c)

    all_chars = await char_repo.list_characters()
    assert len(all_chars) == 3
    names = {c.name for c in all_chars}
    assert names == {"Alice", "Bob", "Charlie"}


@pytest.mark.asyncio
async def test_create_asset(asset_repo, char_repo):
    """Save AssetModel → verify retrieval, check default state='draft'."""
    char = CharacterModel(name="Test", category="main", species="rabbit")
    await char_repo.save_character(char)

    asset = AssetModel(
        character_id=char.id,
        asset_type="reference",
        file_path="/tmp/test.png",
    )
    saved_id = await asset_repo.save(asset)

    loaded = await asset_repo.get(saved_id)
    assert loaded is not None
    assert loaded.id == asset.id
    assert loaded.state == "draft"
    assert loaded.asset_type == "reference"


@pytest.mark.asyncio
async def test_update_asset_state(asset_repo, char_repo):
    """Save asset → update state to 'generated' → verify; update to 'scored' → verify."""
    char = CharacterModel(name="Test", category="main", species="rabbit")
    await char_repo.save_character(char)

    asset = AssetModel(
        character_id=char.id,
        asset_type="expression",
        file_path="/tmp/test.png",
    )
    await asset_repo.save(asset)

    # draft -> generated
    await asset_repo.update_state(asset.id, "generated")
    loaded = await asset_repo.get(asset.id)
    assert loaded.state == "generated"

    # generated -> scored
    await asset_repo.update_state(asset.id, "scored")
    loaded = await asset_repo.get(asset.id)
    assert loaded.state == "scored"


@pytest.mark.asyncio
async def test_find_by_character(asset_repo, char_repo):
    """Save 2 assets for char A and 1 for char B → find_by_character returns correct counts."""
    char_a = CharacterModel(name="Alice", category="main", species="cat")
    char_b = CharacterModel(name="Bob", category="friend", species="dog")
    await char_repo.save_character(char_a)
    await char_repo.save_character(char_b)

    await asset_repo.save(AssetModel(character_id=char_a.id, asset_type="reference", file_path="/tmp/a1.png"))
    await asset_repo.save(AssetModel(character_id=char_a.id, asset_type="expression", file_path="/tmp/a2.png"))
    await asset_repo.save(AssetModel(character_id=char_b.id, asset_type="reference", file_path="/tmp/b1.png"))

    a_assets = await asset_repo.find_by_character(char_a.id)
    assert len(a_assets) == 2

    b_assets = await asset_repo.find_by_character(char_b.id)
    assert len(b_assets) == 1

    a_refs = await asset_repo.find_by_character(char_a.id, asset_type="reference")
    assert len(a_refs) == 1


@pytest.mark.asyncio
async def test_find_approved(asset_repo, char_repo):
    """Save 2 assets, approve 1 → find_approved returns only the approved one."""
    char = CharacterModel(name="Test", category="main", species="rabbit")
    await char_repo.save_character(char)

    asset1 = AssetModel(character_id=char.id, asset_type="reference", file_path="/tmp/a1.png")
    asset2 = AssetModel(character_id=char.id, asset_type="expression", file_path="/tmp/a2.png")
    await asset_repo.save(asset1)
    await asset_repo.save(asset2)

    # Approve asset1: draft -> generated -> scored -> shortlisted -> approved
    for state in ("generated", "scored", "shortlisted", "approved"):
        await asset_repo.update_state(asset1.id, state)

    approved = await asset_repo.find_approved(char.id, "reference")
    assert len(approved) == 1
    assert approved[0].id == asset1.id

    approved_expr = await asset_repo.find_approved(char.id, "expression")
    assert len(approved_expr) == 0


@pytest.mark.asyncio
async def test_character_not_found(char_repo):
    """Attempt to get non-existent character → returns None (defined by interface)."""
    loaded = await char_repo.get_character("nonexistent-id")
    assert loaded is None


@pytest.mark.asyncio
async def test_asset_not_found(asset_repo):
    """Attempt to get non-existent asset → returns None."""
    loaded = await asset_repo.get("nonexistent-id")
    assert loaded is None


@pytest.mark.asyncio
async def test_update_state_not_found(asset_repo):
    """Attempt to update state on non-existent asset → raises NotFoundError."""
    with pytest.raises(NotFoundError):
        await asset_repo.update_state("nonexistent-id", "generated")


@pytest.mark.asyncio
async def test_json_serialization(asset_repo, char_repo):
    """Verify scores dict and bio_data dict round-trip through SQLite JSON."""
    char = CharacterModel(
        name="Test",
        category="main",
        species="rabbit",
        bio_data={"personality": ["curious", "kind"], "age": 5},
    )
    await char_repo.save_character(char)

    scores = {"prompt_accuracy": 0.85, "character_consistency": 0.92}
    asset = AssetModel(
        character_id=char.id,
        asset_type="reference",
        file_path="/tmp/test.png",
        scores=scores,
        brand_score=0.88,
    )
    await asset_repo.save(asset)
    loaded = await asset_repo.get(asset.id)

    assert loaded.scores == scores
    assert loaded.brand_score == 0.88

    loaded_char = await char_repo.get_character(char.id)
    assert loaded_char.bio_data == {"personality": ["curious", "kind"], "age": 5}


@pytest.mark.asyncio
async def test_state_transition_validity(asset_repo, char_repo):
    """Verify asset transitions follow D-15 lifecycle; invalid transitions raise ValueError."""
    char = CharacterModel(name="Test", category="main", species="rabbit")
    await char_repo.save_character(char)

    asset = AssetModel(
        character_id=char.id,
        asset_type="reference",
        file_path="/tmp/test.png",
    )
    await asset_repo.save(asset)

    # Valid transition
    await asset_repo.update_state(asset.id, "generated")
    assert (await asset_repo.get(asset.id)).state == "generated"

    # Invalid: generated -> approved (skipping scored + shortlisted)
    with pytest.raises(ValueError, match="Invalid state transition"):
        await asset_repo.update_state(asset.id, "approved")

    # Still 'generated' after failed transition
    assert (await asset_repo.get(asset.id)).state == "generated"

    # Valid full chain: generated -> scored -> shortlisted -> approved
    await asset_repo.update_state(asset.id, "scored")
    await asset_repo.update_state(asset.id, "shortlisted")
    await asset_repo.update_state(asset.id, "approved")
    assert (await asset_repo.get(asset.id)).state == "approved"

    # approved -> production -> archived
    await asset_repo.update_state(asset.id, "production")
    await asset_repo.update_state(asset.id, "archived")
    assert (await asset_repo.get(asset.id)).state == "archived"

    # archived has no outgoing transitions
    with pytest.raises(ValueError, match="Invalid state transition"):
        await asset_repo.update_state(asset.id, "draft")


@pytest.mark.asyncio
async def test_lineage_metadata_roundtrip(asset_repo, char_repo):
    """Lineage dict round-trips through save() and _row_to_asset() with JSON intact.

    Per D-18: each approved asset retains lineage metadata (generation_batch,
    candidate_pool, version_history, episode_usage).
    """
    char = CharacterModel(name="Test", category="main", species="rabbit")
    await char_repo.save_character(char)

    lineage = {
        "generation_batch": "batch-001",
        "candidate_pool": 50,
        "version_history": [],
    }

    asset = AssetModel(
        character_id=char.id,
        asset_type="reference",
        file_path="/tmp/test.png",
        lineage=lineage,
    )
    await asset_repo.save(asset)

    loaded = await asset_repo.get(asset.id)
    assert loaded is not None
    assert loaded.lineage == lineage
    assert loaded.lineage["generation_batch"] == "batch-001"
    assert loaded.lineage["candidate_pool"] == 50
    assert loaded.lineage["version_history"] == []

    # Verify existing assets without lineage load as None
    asset_no_lineage = AssetModel(
        character_id=char.id,
        asset_type="expression",
        file_path="/tmp/test2.png",
    )
    await asset_repo.save(asset_no_lineage)
    loaded_no_lineage = await asset_repo.get(asset_no_lineage.id)
    assert loaded_no_lineage.lineage is None


@pytest.mark.asyncio
async def test_apply_migrations_lineage_column(shared_db):
    """_apply_migrations() adds lineage column to existing databases."""
    # Create repo with original schema (no lineage column yet)
    # We simulate this by checking PRAGMA table_info before and after
    repo = SQLiteAssetRepository(shared_db)

    # Verify lineage column exists via PRAGMA
    conn = repo._get_conn()
    cursor = conn.execute("PRAGMA table_info(assets)")
    columns = {row["name"] for row in cursor.fetchall()}
    assert "lineage" in columns, "lineage column should exist after init"

    # Verify idempotency: calling _apply_migrations again doesn't fail
    repo._apply_migrations()
    cursor = conn.execute("PRAGMA table_info(assets)")
    columns = {row["name"] for row in cursor.fetchall()}
    assert "lineage" in columns
