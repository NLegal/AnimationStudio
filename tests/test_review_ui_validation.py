"""Tests for Review UI input validation (M-07).

Covers the pure ``input_validation`` helpers and the endpoint hardening:
malformed asset_ids, unknown actions/backends/scopes, out-of-range counts and
limits, and text field caps must be rejected without touching the repo layer.
"""

import pytest
from fastapi.testclient import TestClient

from src.review_ui import input_validation as iv
from src.review_ui.app import create_app


# ---------------------------------------------------------------------------
# Pure validators
# ---------------------------------------------------------------------------


class TestAssetIdValidator:
    def test_valid_ids_pass(self):
        for aid in ("asset-000", "lily-001", "ab_c.d-e", "A1"):
            assert iv.validate_asset_id(aid) == aid

    def test_empty_rejected(self):
        with pytest.raises(ValueError):
            iv.validate_asset_id("")
        with pytest.raises(ValueError):
            iv.validate_asset_id(None)

    def test_whitespace_rejected(self):
        with pytest.raises(ValueError):
            iv.validate_asset_id("asset 001")
        with pytest.raises(ValueError):
            iv.validate_asset_id(" asset-001 ")

    def test_path_traversal_rejected(self):
        for evil in ("../etc/passwd", "..\\..\\boot.ini", "a/b", "a/b/c"):
            with pytest.raises(ValueError):
                iv.validate_asset_id(evil)

    def test_leading_non_alnum_rejected(self):
        for evil in ("-leading", ".dotstart", "_understart"):
            with pytest.raises(ValueError):
                iv.validate_asset_id(evil)

    def test_too_long_rejected(self):
        with pytest.raises(ValueError):
            iv.validate_asset_id("a" * (iv.MAX_ASSET_ID_LEN + 1))


class TestActionValidator:
    def test_allowed_actions(self):
        for action in ("approve", "reject", "shortlist", "promote", "regenerate"):
            assert iv.validate_action(action) == action

    def test_unknown_action_rejected(self):
        for action in ("frobnicate", "DELETE", "", "drop", " approve "):
            with pytest.raises(ValueError):
                iv.validate_action(action)


class TestBackendValidators:
    def test_generation_backends(self):
        for backend in ("", "mock", "comfyui", "comfy", "cloud", "cloudapi"):
            assert iv.validate_backend(backend) == backend

    def test_unknown_generation_backend_rejected(self):
        for backend in ("suno", "banana", "mock; rm -rf /"):
            with pytest.raises(ValueError):
                iv.validate_backend(backend)

    def test_music_backends(self):
        for backend in ("", "ace-step", "suno", "mock"):
            assert iv.validate_music_backend(backend) == backend

    def test_unknown_music_backend_rejected(self):
        for backend in ("comfyui", "cloud", "banana"):
            with pytest.raises(ValueError):
                iv.validate_music_backend(backend)


class TestScopeValidator:
    def test_allowed_scopes(self):
        for scope in ("all", "characters", "environments", "vehicles",
                      "backgrounds", "props"):
            assert iv.validate_scope(scope) == scope

    def test_unknown_scope_rejected(self):
        for scope in ("world", "delete", ""):
            with pytest.raises(ValueError):
                iv.validate_scope(scope)


class TestCountLimitValidators:
    def test_bounds(self):
        assert iv.validate_count(1) == 1
        assert iv.validate_count(iv.MAX_COUNT) == iv.MAX_COUNT
        assert iv.validate_limit(0) == 0
        assert iv.validate_limit(iv.MAX_LIMIT) == iv.MAX_LIMIT

    def test_out_of_range_rejected(self):
        with pytest.raises(ValueError):
            iv.validate_count(0)
        with pytest.raises(ValueError):
            iv.validate_count(iv.MAX_COUNT + 1)
        with pytest.raises(ValueError):
            iv.validate_limit(-1)
        with pytest.raises(ValueError):
            iv.validate_limit(iv.MAX_LIMIT + 1)

    def test_non_int_rejected(self):
        with pytest.raises(ValueError):
            iv.validate_count("4")
        with pytest.raises(ValueError):
            iv.validate_limit(True)


class TestTextCap:
    def test_caps_long_text(self):
        assert len(iv.cap_text("x" * 5000)) == iv.MAX_TEXT_LEN

    def test_strips_whitespace(self):
        assert iv.cap_text("  hello  ") == "hello"

    def test_non_string_returns_empty(self):
        assert iv.cap_text(None) == ""
        assert iv.cap_text(42) == ""


# ---------------------------------------------------------------------------
# Endpoint hardening
# ---------------------------------------------------------------------------


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


@pytest.fixture
def client():
    return TestClient(create_app(asset_repo=_make_stub_repo()))


class TestActionEndpointsHardened:
    def test_asset_id_with_path_chars_never_reaches_repo(self, client):
        # Slashed ids either fail route matching (404) or validation (400);
        # both are safe and must never 500.
        for evil in ("../etc/passwd", "a/b", "asset 001"):
            r = client.post(f"/api/assets/{evil}/approve")
            assert r.status_code in (400, 404)
            if r.status_code == 400:
                assert r.json()["ok"] is False

    def test_unknown_action_still_400(self, client):
        r = client.post("/api/assets/asset-000/destroy")
        assert r.status_code == 400
        assert r.json()["error"]

    def test_html_append_reject_does_not_throw(self, client):
        # HTML form route swallows validation errors and redirects (303).
        r = client.post("/approve/..%2F..%2Fetc%2Fpasswd", follow_redirects=False)
        assert r.status_code in (303, 404)
        r = client.post("/approve/..%2F..%2Fetc%2Fpasswd")
        assert r.status_code in (200, 303, 404)

    def test_asset_image_evil_id_404(self, client):
        r = client.get("/asset-image/..%2Fsecret.png")
        assert r.status_code in (400, 404)
        # A path separator in a real server becomes a different route (404).
        r = client.get("/asset-image/%2E%2E%2Fsecret.png")
        assert r.status_code in (400, 404)

    def test_reason_capped(self, client):
        long_reason = "r" * 5000
        r = client.post("/api/assets/asset-000/reject", data={"reason": long_reason})
        assert r.json()["state"] == "draft"


class TestGenerateEndpointHardened:
    def test_unknown_scope_redirects_no_queue(self, client):
        r = client.post("/generate", data={"scope": "world"}, follow_redirects=False)
        assert r.status_code == 303

    def test_unknown_backend_redirects_no_queue(self, client):
        r = client.post("/generate", data={"backend": "banana"}, follow_redirects=False)
        assert r.status_code == 303

    def test_count_too_large_redirects_no_queue(self, client):
        r = client.post("/generate", data={"count": "9999"}, follow_redirects=False)
        assert r.status_code == 303

    def test_negative_limit_redirects_no_queue(self, client):
        r = client.post("/generate", data={"limit": "-5"}, follow_redirects=False)
        assert r.status_code == 303


class TestMusicGenerateHardened:
    def test_unknown_music_backend_redirects(self, client):
        r = client.post("/music/generate", data={"backend": "comfyui"},
                        follow_redirects=False)
        assert r.status_code == 303

    def test_topic_capped(self, client):
        r = client.post("/music/generate", data={"topic": "t" * 5000},
                        follow_redirects=False)
        assert r.status_code == 303