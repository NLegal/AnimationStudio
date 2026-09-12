"""Security tests for the Review UI (audit A-04).

Covers:
  - Optional token gate on every state-changing POST route when
    ``create_app(ui_token=...)`` is set (401 without/with wrong token,
    success with the right token).
  - GET routes stay readable without a token (the UI must render publicly
    to humans; state changes require the token).
  - Open-redirect via the ``Referer`` header is blocked: foreign-host
    referers fall back to ``/``; same-origin referers are honored.
"""

import pytest
from fastapi.testclient import TestClient

from src.review_ui.app import create_app


def _make_stub_repo():
    from src.review_ui.app import _StubAssetRepo
    repo = _StubAssetRepo()
    repo._characters["lily-001"] = {
        "id": "lily-001",
        "name": "Lily Bunny",
        "category": "main",
        "species": "rabbit",
    }
    for i in range(3):
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


TOKEN = "studio-token-abc"


@pytest.fixture
def client():
    return TestClient(create_app(asset_repo=_make_stub_repo(), ui_token=TOKEN))


@pytest.fixture
def open_client():
    return TestClient(create_app(asset_repo=_make_stub_repo(), ui_token=None))


POST_ROUTES = [
    "/approve/asset-000",
    "/reject/asset-000",
    "/regenerate/asset-000",
    "/promote/asset-000",
    "/seed",
]


class TestTokenGate:
    @pytest.mark.parametrize("route", POST_ROUTES)
    def test_post_without_token_401(self, client, route):
        assert client.post(route).status_code == 401

    @pytest.mark.parametrize("route", POST_ROUTES)
    def test_post_with_wrong_token_401(self, client, route):
        assert client.post(route, params={"token": "nope"}).status_code == 401

    @pytest.mark.parametrize("route", POST_ROUTES)
    def test_post_with_correct_token_succeeds(self, client, route):
        resp = client.post(route, params={"token": TOKEN})
        assert resp.status_code in (200, 303, 307)

    @pytest.mark.parametrize("route", POST_ROUTES)
    def test_post_with_correct_header_succeeds(self, client, route):
        resp = client.post(route, headers={"X-UI-Token": TOKEN})
        assert resp.status_code in (200, 303, 307)

    @pytest.mark.parametrize("route", POST_ROUTES)
    def test_open_app_requires_no_token(self, open_client, route):
        """ui_token=None keeps the local stack fully open (backward compat)."""
        assert open_client.post(route).status_code in (200, 303, 307, 400)

    def test_generate_and_music_routes_also_gated(self, client):
        assert client.post("/generate").status_code == 401
        assert client.post("/music/generate").status_code == 401
        assert client.post("/music/prompt").status_code == 401
        assert client.post("/motion/prompt").status_code == 401
        assert client.post("/api/assets/asset-000/approve").status_code == 401

    def test_get_routes_are_public_with_token_enabled(self, client):
        """Human browsing stays open; only writes need the token."""
        assert client.get("/").status_code == 200
        assert client.get("/api/overview").status_code == 200
        assert client.get("/api/candidates").status_code == 200


class TestOpenRedirect:
    def test_foreign_host_referer_falls_back_to_root(self, client):
        resp = client.post(
            "/approve/asset-000",
            params={"token": TOKEN},
            headers={"Referer": "https://evil.example.com/phish"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/"

    def test_javascript_scheme_referer_rejected(self, client):
        resp = client.post(
            "/approve/asset-000",
            params={"token": TOKEN},
            headers={"Referer": "javascript:alert(1)"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert not resp.headers["location"].lower().startswith("javascript")

    def test_garbage_referer_rejected(self, client):
        resp = client.post(
            "/approve/asset-000",
            params={"token": TOKEN},
            headers={"Referer": ":::not-a-url:::"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/"

    def test_scheme_relative_referer_rejected(self, client):
        resp = client.post(
            "/approve/asset-000",
            params={"token": TOKEN},
            headers={"Referer": "//evil.example.com/phish"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/"

    def test_same_host_referer_honored(self, client):
        resp = client.post(
            "/approve/asset-000",
            params={"token": TOKEN},
            headers={"Referer": "http://testserver/review/lily-001"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert resp.headers["location"] == "http://testserver/review/lily-001"

    def test_relative_path_referer_honored(self, client):
        resp = client.post(
            "/approve/asset-000",
            params={"token": TOKEN},
            headers={"Referer": "/review/lily-001"},
            follow_redirects=False,
        )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/review/lily-001"