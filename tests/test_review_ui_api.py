"""Tests for the realtime JSON API and Phase 4 motion page.

Covers ``/api/overview``, ``/api/candidates``, ``/api/review/next`` and the
``/api/assets/{id}/{action}`` lifecycle endpoint added for the studio UI.
"""

import pytest
from fastapi.testclient import TestClient

from src.review_ui.app import create_app


def _make_stub_repo():
    """One character with six scored expression assets (real scores on one)."""
    from src.review_ui.app import _StubAssetRepo
    repo = _StubAssetRepo()
    repo._characters["lily-001"] = {
        "id": "lily-001",
        "name": "Lily Bunny",
        "category": "main",
        "species": "rabbit",
    }
    for i in range(6):
        asset = {
            "id": f"asset-{i:03d}",
            "character_id": "lily-001",
            "asset_type": "expression",
            "state": "scored",
            "file_path": f"/tmp/test_{i}.png",
            "seed": 100 + i,
            "prompt": f"Lily Bunny expression {i}",
        }
        if i == 0:
            asset["scores"] = {"brand": 0.8, "prompt_alignment": 0.9}
            asset["brand_score"] = 0.8
        repo._assets.append(asset)
    return repo


@pytest.fixture
def client():
    return TestClient(create_app(asset_repo=_make_stub_repo()))


class TestApiOverview:
    """GET /api/overview returns live aggregate stats."""

    def test_overview_counts(self, client):
        data = client.get("/api/overview").json()
        assert data["total_entities"] == 1
        assert data["total_assets"] == 6
        assert data["pending"] == 6
        assert data["approved"] == 0
        assert data["by_state"]["scored"] == 6

    def test_overview_review_queue(self, client):
        data = client.get("/api/overview").json()
        queue = data["review_queue"]
        assert len(queue) >= 1
        assert queue[0]["entity_id"] == "lily-001"
        assert queue[0]["state"] == "scored"


class TestApiCandidates:
    """GET /api/candidates with filters."""

    def test_all_candidates(self, client):
        data = client.get("/api/candidates").json()
        assert len(data["candidates"]) == 6

    def test_limit(self, client):
        data = client.get("/api/candidates?limit=2").json()
        assert len(data["candidates"]) == 2

    def test_state_filter(self, client):
        data = client.get("/api/candidates?state=scored").json()
        assert len(data["candidates"]) == 6
        data = client.get("/api/candidates?state=approved").json()
        assert data["candidates"] == []

    def test_asset_type_filter(self, client):
        data = client.get("/api/candidates?asset_type=pose").json()
        assert data["candidates"] == []

    def test_candidate_carries_real_score(self, client):
        data = client.get("/api/candidates?limit=6").json()
        first = next(
            c for c in data["candidates"] if c["asset_id"] == "asset-000"
        )
        assert first["brand_score"] == 0.8
        assert first["score_present"] is True
        assert first["components"]["prompt_alignment"] == 0.9
        assert first["image_url"] == "/asset-image/asset-000"


class TestApiReviewNext:
    """GET /api/review/next returns the oldest pending candidate."""

    def test_next_candidate(self, client):
        data = client.get("/api/review/next").json()
        assert data["candidate"] is not None
        assert data["candidate"]["entity"] == "Lily Bunny"
        assert data["remaining"] >= 1

    def test_empty_queue_after_approvals(self, client):
        for i in range(6):
            r = client.post(f"/api/assets/asset-{i:03d}/approve")
            assert r.json()["ok"] is True
        data = client.get("/api/review/next").json()
        assert data["candidate"] is None
        assert data["remaining"] == 0


class TestApiActions:
    """POST /api/assets/{id}/{action} lifecycle transitions."""

    def test_approve(self, client):
        r = client.post("/api/assets/asset-001/approve")
        payload = r.json()
        assert payload["ok"] is True
        assert payload["message"] == "Approved"
        assert payload["state"] == "approved"
        # No longer pending
        data = client.get("/api/candidates").json()
        assert "asset-001" not in {c["asset_id"] for c in data["candidates"]}

    def test_promote(self, client):
        r = client.post("/api/assets/asset-002/promote")
        assert r.json()["state"] == "production"

    def test_shortlist(self, client):
        r = client.post("/api/assets/asset-003/shortlist")
        assert r.json()["state"] == "shortlisted"

    def test_reject_with_reason(self, client):
        r = client.post(
            "/api/assets/asset-004/reject", data={"reason": "blurry ears"}
        )
        assert r.json()["state"] == "draft"

    def test_reject_resets_to_draft(self, client):
        client.post("/api/assets/asset-005/approve")
        r = client.post("/api/assets/asset-005/reject")
        assert r.json()["state"] == "draft"

    def test_regenerate_returns_job(self, client):
        r = client.post("/api/assets/asset-000/regenerate")
        payload = r.json()
        assert payload["ok"] is True
        assert payload["job_id"]

    def test_unknown_action_returns_400(self, client):
        r = client.post("/api/assets/asset-000/frobnicate")
        assert r.status_code == 400
        assert r.json()["ok"] is False

    def test_missing_asset_returns_400(self, client):
        r = client.post("/api/assets/does-not-exist/approve")
        assert r.status_code == 400


class TestMotionPage:
    """Phase 4 animation bible browser."""

    def test_motion_page_renders(self, client):
        response = client.get("/motion")
        assert response.status_code == 200
        body = response.text
        assert "Animation Bible &amp; Motion System" in body
        assert "Motion Cycles" in body
        assert "idle" in body
        assert "Camera Shots" in body
        assert "Facial Expressions" in body
        assert "Gesture Library" in body
        assert "24" in body  # master frame rate


class TestRealtimeMarkup:
    """HTML pages expose the realtime action hooks + studio.js."""

    def test_entity_detail_has_realtime_actions(self, client):
        body = client.get("/character/lily-001").text
        assert 'data-asset-id="asset-000"' in body
        assert 'data-action="approve"' in body
        assert 'data-action="reject"' in body
        assert "/static/studio.js" in body

    def test_review_page_has_realtime_actions(self, client):
        body = client.get("/review/lily-001?asset_type=expression&batch=true").text
        assert 'data-action="approve"' in body
        assert 'data-action="promote"' in body
        assert 'data-action="reject"' in body
