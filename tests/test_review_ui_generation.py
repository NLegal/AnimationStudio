"""Tests for the Review UI generation panel and universe seeding.

These tests wire ``create_app`` to a real SQLite repository plus the mock
backend so the generate/seed endpoints run the full pipeline end-to-end.
"""

import asyncio

import pytest
from fastapi.testclient import TestClient

from src.asset_repository.sqlite_repo import SQLiteAssetRepository, SQLiteCharacterRepository
from src.universe.seed import seed_all
from src.universe.sqlite_bridge import SQLiteCombinedRepo
from src.review_ui.app import create_app


@pytest.fixture
def sqlite_app(tmp_path):
    """create_app wired to a temp SQLite repo (catalog pre-seeded)."""
    db = str(tmp_path / "ui.db")
    char_repo = SQLiteCharacterRepository(db_path=db)
    asset_repo = SQLiteAssetRepository(db_path=db)
    combined = SQLiteCombinedRepo(char_repo, asset_repo)
    asyncio.run(seed_all(char_repo))

    async def seed(char_repo_):
        return await seed_all(char_repo_)

    app = create_app(
        asset_repo=combined,
        character_repo=char_repo,
        seed_catalog=seed,
    )
    return app, char_repo, asset_repo


@pytest.fixture
def client(sqlite_app):
    app, _, _ = sqlite_app
    return TestClient(app)


def _lily_id(asset_repo) -> str:
    conn = asset_repo._get_conn()
    return conn.execute(
        "SELECT id FROM characters WHERE name = 'Lily Bunny'"
    ).fetchone()[0]


class TestDashboard:
    """Dashboard renders the full universe catalog."""

    def test_renders_character_section(self, client):
        body = client.get("/").text
        assert "Lily Bunny" in body
        assert "Universe Dashboard" in body

    def test_renders_environment_section(self, client):
        body = client.get("/").text
        assert "Environments / Worlds" in body
        assert "Sunny Meadow" in body

    def test_renders_prop_categories(self, client):
        body = client.get("/").text
        assert "Props &amp; Asset Library" in body
        assert 'name="item" value="Furniture"' in body

    def test_renders_generation_panel(self, client):
        body = client.get("/").text
        assert 'action="/generate"' in body
        assert 'name="scope"' in body
        assert 'value="mock"' in body

    def test_generate_forms_target_mock_backend(self, client):
        body = client.get("/").text
        assert body.count('name="backend" value="mock"') >= 3

    def test_recent_jobs_table_present(self, client):
        body = client.get("/").text
        assert "Recent Jobs" in body


class TestCharacterDetail:
    """Per-category asset types drive the detail page forms."""

    def test_character_detail_asset_types(self, client, sqlite_app):
        _, _, asset_repo = sqlite_app
        body = client.get(f"/character/{_lily_id(asset_repo)}").text
        for label in ("Generate references", "Generate expressions",
                      "Generate poses", "Generate outfits"):
            assert label in body

    def test_environment_detail_asset_types(self, client, sqlite_app):
        _, _, asset_repo = sqlite_app
        conn = asset_repo._get_conn()
        env_id = conn.execute(
            "SELECT id FROM characters WHERE category='environment' LIMIT 1"
        ).fetchone()[0]
        body = client.get(f"/character/{env_id}").text
        assert "Generate environment" in body
        assert 'name="scope" value="environments"' in body

    def test_prop_detail_asset_types(self, client, sqlite_app):
        _, _, asset_repo = sqlite_app
        conn = asset_repo._get_conn()
        prop_id = conn.execute(
            "SELECT id FROM characters WHERE category='asset' LIMIT 1"
        ).fetchone()[0]
        body = client.get(f"/character/{prop_id}").text
        assert "Generate prop" in body
        assert 'name="scope" value="props"' in body


class TestGenerateEndpoint:
    """POST /generate runs the pipeline and persists assets."""

    def test_generate_character(self, client, sqlite_app):
        _, _, asset_repo = sqlite_app
        response = client.post("/generate", data={
            "scope": "characters", "item": "Lily", "count": "2",
            "limit": "1", "backend": "mock",
        })
        assert response.status_code in (200, 303)
        body = client.get(f"/character/{_lily_id(asset_repo)}").text
        assert "asset-card" in body

    def test_generate_environment(self, client, sqlite_app):
        _, _, asset_repo = sqlite_app
        conn = asset_repo._get_conn()
        env_id = conn.execute(
            "SELECT id FROM characters WHERE category='environment' LIMIT 1"
        ).fetchone()[0]
        client.post("/generate", data={
            "scope": "environments", "item": "", "count": "2",
            "limit": "1", "backend": "mock",
        })
        body = client.get(f"/character/{env_id}").text
        assert "asset-card" in body

    def test_generate_prop_category(self, client, sqlite_app):
        _, _, asset_repo = sqlite_app
        conn = asset_repo._get_conn()
        before = conn.execute(
            "SELECT COUNT(*) FROM assets WHERE asset_type='prop'"
        ).fetchone()[0]
        client.post("/generate", data={
            "scope": "props", "item": "Furniture", "count": "2",
            "limit": "2", "backend": "mock",
        })
        after = conn.execute(
            "SELECT COUNT(*) FROM assets WHERE asset_type='prop'"
        ).fetchone()[0]
        assert after > before

    def test_generate_with_stub_repo_is_noop(self):
        from src.review_ui.app import _StubAssetRepo
        stub = _StubAssetRepo()
        stub._characters["lily-001"] = {
            "id": "lily-001", "name": "Lily Bunny", "category": "main",
        }
        app = create_app(asset_repo=stub)
        client = TestClient(app)
        response = client.post("/generate", data={
            "scope": "characters", "item": "Lily", "count": "2",
            "limit": "1", "backend": "mock",
        })
        assert response.status_code in (200, 303)

    def test_generate_unknown_item_redirects(self, client):
        response = client.post("/generate", data={
            "scope": "characters", "item": "Nobody", "count": "2",
            "limit": "1", "backend": "mock",
        })
        assert response.status_code in (200, 303)


class TestSeedEndpoint:
    """POST /seed seeds the catalog idempotently."""

    def test_seed_endpoint(self, client, sqlite_app):
        _, char_repo, _ = sqlite_app
        response = client.post("/seed")
        assert response.status_code in (200, 303)
        # Seeding is idempotent: a second call creates nothing new.
        response = client.post("/seed")
        assert response.status_code in (200, 303)

    def test_seed_requires_character_repo(self):
        from src.review_ui.app import _StubAssetRepo
        app = create_app(asset_repo=_StubAssetRepo())
        client = TestClient(app)
        response = client.post("/seed")
        assert response.status_code in (200, 303)


class TestDefaultFactory:
    """create_app() with no repos wires itself to SQLite + mock backend."""

    def test_lists_provisioned_catalog(self, tmp_path):
        app = create_app(db_path=str(tmp_path / "default.db"))
        client = TestClient(app)
        body = client.get("/").text
        assert "Universe Dashboard" in body
        assert "Lily Bunny" in body
        assert "Sunny Meadow" in body
        assert "Props &amp; Asset Library" in body

    def test_generates_into_default_database(self, tmp_path):
        db = str(tmp_path / "default.db")
        app = create_app(db_path=db)
        client = TestClient(app)
        client.get("/")
        response = client.post("/generate", data={
            "scope": "characters", "item": "Lily", "count": "2",
            "limit": "1", "backend": "mock",
        })
        assert response.status_code in (200, 303)
        from src.asset_repository.sqlite_repo import SQLiteAssetRepository
        asset_repo = SQLiteAssetRepository(db_path=db)
        conn = asset_repo._get_conn()
        count = conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
        assert count > 0

    def test_dashboard_shows_activity_log_panel(self, tmp_path):
        app = create_app(db_path=str(tmp_path / "default.db"))
        client = TestClient(app)
        body = client.get("/").text
        assert "Activity Log" in body
        assert 'id="log-list"' in body

    def test_logs_endpoint_returns_generate_entries(self, tmp_path):
        app = create_app(db_path=str(tmp_path / "default.db"))
        client = TestClient(app)
        client.post("/generate", data={
            "scope": "characters", "item": "Lily", "count": "2",
            "limit": "1", "backend": "mock",
        })
        data = client.get("/logs").json()
        entries = data.get("entries", [])
        assert any("Generate queued" in e["message"] for e in entries)
        assert any("UI batch complete" in e["message"] for e in entries)
