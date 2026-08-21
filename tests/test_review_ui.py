"""Tests for the Review UI grid size parameterization (D-16).

Uses the application factory (``create_app``) with the in-memory stub repo
so tests do not need a live database.
"""

import pytest
from fastapi.testclient import TestClient

from src.review_ui.app import create_app


def _make_stub_repo():
    """Build a ``_StubAssetRepo`` with one character and 20 candidate assets."""
    from src.review_ui.app import _StubAssetRepo
    repo = _StubAssetRepo()
    repo._characters["lily-001"] = {
        "id": "lily-001",
        "name": "Lily Bunny",
        "category": "main",
        "species": "rabbit",
    }
    for i in range(20):
        repo._assets.append({
            "id": f"asset-{i:03d}",
            "character_id": "lily-001",
            "asset_type": "expression",
            "state": "scored",
            "file_path": f"/tmp/test_{i}.png",
            "seed": 100 + i,
            "prompt": f"Lily Bunny expression {i}",
        })
    return repo


@pytest.fixture
def stub_repo():
    """Fixture providing a pre-populated stub repo."""
    return _make_stub_repo()


@pytest.fixture
def client(stub_repo):
    """Fixture providing a TestClient wired to the application factory."""
    app = create_app(asset_repo=stub_repo)
    return TestClient(app)


# ---------------------------------------------------------------------------
#  Grid parameter — size parsing and fallback
# ---------------------------------------------------------------------------


class TestReviewGridSizes:
    """Configurable batch grid sizes (3x3, 4x4) per D-16."""

    @pytest.fixture(autouse=True)
    def _setup(self, client):
        self.client = client

    def _get_context(self, url: str) -> dict:
        """Fetch a review page and extract Jinja2 template context.

        We cheat by inspecting the *last* template rendered via the TestClient
        ``app.extra`` dictionary — because ``_StubAssetRepo`` does not return
        ``AssetModel`` objects, the actual template context is what matters.
        """
        response = self.client.get(url)
        assert response.status_code == 200, f"GET {url} returned {response.status_code}"
        # The jinja2 environment stores the last rendered context on the app
        # when using the ``TESTING`` pattern.  We use a simpler approach:
        # parse the response body for expected grid parameters.
        return {"response": response, "text": response.text}

    # ── 2x2 (default) ───────────────────────────────────────────────

    def test_grid_2x2_default(self):
        """Default grid is 2x2 when no ``grid`` parameter provided."""
        # When batch=true without a grid param we expect 4 candidates (2x2)
        response = self.client.get(
            "/review/lily-001?asset_type=expression&batch=true"
        )
        assert response.status_code == 200

        body = response.text
        # The grid-2x2 class should be present
        assert 'grid-2x2' in body
        # The grid selector should highlight 2x2 as active
        assert 'grid=2x2' in body and 'btn-active' in body
        # Should render 4 batch cards (the grid selector text "Grid:" appears too)
        card_count = body.count('class="batch-card"')
        # We expect 4 cards for a 2x2 grid (capped by grid_capacity=4)
        # The stub repo has 20 assets but grid renders at most 4
        assert card_count == 4, f"Expected 4 batch cards for 2x2, got {card_count}"

    def test_grid_2x2_explicit(self):
        """Explicit grid=2x2 behaves the same as the default."""
        response = self.client.get(
            "/review/lily-001?asset_type=expression&batch=true&grid=2x2"
        )
        assert response.status_code == 200
        assert 'grid-2x2' in response.text
        card_count = response.text.count('class="batch-card"')
        assert card_count == 4

    # ── 3x3 ─────────────────────────────────────────────────────────

    def test_grid_3x3(self):
        """grid=3x3 renders 9 candidates in a 3-column grid."""
        response = self.client.get(
            "/review/lily-001?asset_type=expression&batch=true&grid=3x3"
        )
        assert response.status_code == 200
        assert 'grid-3x3' in response.text
        card_count = response.text.count('class="batch-card"')
        assert card_count == 9, f"Expected 9 batch cards for 3x3, got {card_count}"

    # ── 4x4 ─────────────────────────────────────────────────────────

    def test_grid_4x4(self):
        """grid=4x4 renders 16 candidates in a 4-column grid."""
        response = self.client.get(
            "/review/lily-001?asset_type=expression&batch=true&grid=4x4"
        )
        assert response.status_code == 200
        assert 'grid-4x4' in response.text
        card_count = response.text.count('class="batch-card"')
        # There are 20 assets in the stub, capped at grid_capacity=16
        assert card_count == 16, f"Expected 16 batch cards for 4x4, got {card_count}"

    # ── Invalid grid fallback ───────────────────────────────────────

    def test_grid_invalid_fallback(self):
        """An unrecognised grid value falls back to 2x2 (4 candidates)."""
        response = self.client.get(
            "/review/lily-001?asset_type=expression&batch=true&grid=5x5"
        )
        assert response.status_code == 200
        # Falls back to grid-2x2
        assert 'grid-2x2' in response.text
        assert 'grid-5x5' not in response.text
        card_count = response.text.count('class="batch-card"')
        assert card_count == 4, f"Expected 4 batch cards (2x2 fallback), got {card_count}"

    # ── Non-batch ignores grid ──────────────────────────────────────

    def test_grid_non_batch_ignores_grid(self):
        """When ``batch=false`` the grid parameter is ignored (all candidates shown)."""
        response = self.client.get(
            "/review/lily-001?asset_type=expression&batch=false&grid=4x4"
        )
        assert response.status_code == 200
        # Non-batch mode does not use grid selector — single view shows all candidates
        assert 'batch-card' not in response.text, \
            "Batch cards should NOT appear in single-view mode"
        # Should contain candidate cards in single-review mode
        assert 'candidate-card' in response.text or 'empty-state' in response.text


# ---------------------------------------------------------------------------
#  Asset-type tabs on the review page (phase-scoped library tabs)
# ---------------------------------------------------------------------------


class TestReviewAssetTypeTabs:
    """Review pages expose phase-scoped asset-type tabs (Phase 3 parity)."""

    @pytest.fixture(autouse=True)
    def _setup(self, client):
        self.client = client

    def test_tabs_rendered_on_review_page(self):
        """The review page renders an asset-type tab strip."""
        response = self.client.get("/review/lily-001?asset_type=expression")
        assert response.status_code == 200
        assert 'asset-type-tabs' in response.text

    def test_character_tabs_are_phase1_types(self):
        """Character review pages show character library tabs."""
        body = self.client.get("/review/lily-001").text
        for label in ("Expressions", "Poses", "Outfits"):
            assert label in body, f"missing character tab: {label}"

    def test_prop_tabs_are_phase3_types(self):
        """Prop review pages show the five Phase 3 asset-type tabs."""
        from src.review_ui.app import _StubAssetRepo
        repo = _StubAssetRepo()
        repo._characters["ball-001"] = {
            "id": "ball-001",
            "name": "Bouncy Ball",
            "category": "asset",
        }
        app = create_app(asset_repo=repo)
        client = TestClient(app)
        body = client.get("/review/ball-001").text
        assert 'asset-type-tabs' in body
        for label in ("References", "Views", "Materials", "Colors", "Lighting"):
            assert label in body, f"missing prop tab: {label}"

    def test_default_asset_type_follows_entity_category(self):
        """Without ?asset_type= the page defaults to the entity's primary type."""
        from src.review_ui.app import _StubAssetRepo
        repo = _StubAssetRepo()
        repo._characters["ball-001"] = {
            "id": "ball-001",
            "name": "Bouncy Ball",
            "category": "asset",
        }
        app = create_app(asset_repo=repo)
        client = TestClient(app)
        body = client.get("/review/ball-001").text
        # Props default to reference review, not expression.
        assert "Review: Bouncy Ball &mdash; references" in body

    def test_unknown_asset_type_falls_back_to_primary(self):
        """An invalid asset_type falls back to the entity's primary type."""
        from src.review_ui.app import _StubAssetRepo
        repo = _StubAssetRepo()
        repo._characters["ball-001"] = {
            "id": "ball-001",
            "name": "Bouncy Ball",
            "category": "asset",
        }
        app = create_app(asset_repo=repo)
        client = TestClient(app)
        body = client.get("/review/ball-001?asset_type=expression").text
        assert "Review: Bouncy Ball &mdash; references" in body
