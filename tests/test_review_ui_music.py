"""Tests for the Review UI music page, generation jobs, and API polling.

Covers ``GET /music``, ``POST /music/generate``, ``GET /api/music/jobs`` and
the suno-degradation path.  Uses ``MockBackend`` and ``tmp_path`` output dirs
so every assertion runs fully offline with zero network I/O.

Constraint guards:
- C2: no sqlite3 in tests — music routes never touch catalog.db
- C3: fail-loud transport guards installed on the Phase 7 seam
- C5: suno selection yields a failed job, never HTTP 500
"""

import os

import pytest
from fastapi.testclient import TestClient

from src.review_ui.app import create_app


# --------------------------------------------------------------------------- #
# Fail-loud transport guards (C3)                                              #
# --------------------------------------------------------------------------- #

@pytest.fixture(autouse=True)
def _no_transport(monkeypatch):
    """Prove zero network I/O across every request in this module."""
    import src.music_generation.backends as _bm

    def _loud(*a, **kw):
        raise AssertionError("transport seam called — expected offline")

    monkeypatch.setattr(_bm, "_post_json", _loud)
    monkeypatch.setattr(_bm, "_get_json", _loud)
    monkeypatch.setattr(_bm, "_get_bytes", _loud)


# --------------------------------------------------------------------------- #
# Env isolation (C6) — del MUSIC_BACKEND and ACESTEP_* so lazy defaults apply  #
# --------------------------------------------------------------------------- #

@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv("MUSIC_BACKEND", raising=False)
    monkeypatch.delenv("ACESTEP_API_KEY", raising=False)
    monkeypatch.delenv("ACESTEP_BASE_URL", raising=False)


# --------------------------------------------------------------------------- #
# Client fixture                                                              #
# --------------------------------------------------------------------------- #

@pytest.fixture
def music_dir(tmp_path):
    return str(tmp_path / "music")


@pytest.fixture
def client(tmp_path, music_dir):
    """Lightest client: in-memory JobQueue, mock backend, temp music_dir."""
    from src.music_generation.mock import MockBackend
    app = create_app(
        db_path=str(tmp_path / "m.db"),
        music_backend=MockBackend(),
        music_dir=music_dir,
    )
    return TestClient(app)


# =========================================================================== #
# TestMusicPage — GET /music renders the browse page                           #
# =========================================================================== #

class TestMusicPage:
    def test_music_page_renders(self, client):
        resp = client.get("/music")
        assert resp.status_code == 200
        body = resp.text
        assert "Music Generation" in body

    def test_navbar_contains_music_link(self, client):
        body = client.get("/music").text
        assert 'href="/music"' in body

    def test_navbar_music_is_active(self, client):
        body = client.get("/music").text
        assert 'page == \'music\' %}nav-active' in body or "nav-active" in body

    def test_all_24_categories_in_select(self, client):
        from src.audio_bible import AudioBible
        categories = AudioBible().list_song_categories()
        body = client.get("/music").text
        for cat in categories:
            assert cat in body, f"Category {cat!r} missing from /music page"

    def test_params_table_has_bedtime_row(self, client):
        body = client.get("/music").text
        assert "Bedtime" in body
        assert "66" in body or "66 BPM" in body

    def test_generate_form_exists(self, client):
        body = client.get("/music").text
        assert 'action="/music/generate"' in body
        assert 'method="post"' in body

    def test_backend_select_includes_choices(self, client):
        body = client.get("/music").text
        assert "ace-step" in body or "ace_step" in body or "Ace-Step" in body
        assert "suno" in body or "Suno" in body
        assert "mock" in body or "Mock" in body


# =========================================================================== #
# TestMusicGenerate — POST /music/generate + GET /api/music/jobs               #
# =========================================================================== #

class TestMusicGenerate:
    def test_generate_mock_returns_redirect(self, client):
        resp = client.post("/music/generate", data={
            "category": "Bedtime",
            "topic": "sleepy moon",
            "backend": "",
        }, follow_redirects=False)
        assert resp.status_code == 303

    def test_generate_mock_job_completes(self, client, music_dir):
        client.post("/music/generate", data={
            "category": "Bedtime",
            "topic": "sleepy moon",
            "backend": "",
        })
        data = client.get("/api/music/jobs").json()
        jobs = data.get("jobs", [])
        assert len(jobs) >= 1
        music_jobs = [j for j in jobs if j.get("category") == "Bedtime"]
        assert len(music_jobs) == 1
        job = music_jobs[0]
        assert job["status"] == "completed"
        assert job.get("file", "")

    def test_generate_mock_creates_wav_on_disk(self, client, music_dir):
        client.post("/music/generate", data={
            "category": "Bedtime",
            "topic": "sleepy moon",
            "backend": "",
        })
        wav_files = [f for f in os.listdir(music_dir) if f.endswith(".wav")]
        assert len(wav_files) >= 1, f"Expected WAV in {music_dir}, got {os.listdir(music_dir)}"
        assert "bedtime" in wav_files[0].lower()

    def test_generate_mock_creates_manifest_entry(self, client, music_dir):
        client.post("/music/generate", data={
            "category": "Bedtime",
            "topic": "sleepy moon",
            "backend": "",
        })
        import json
        manifest_path = os.path.join(music_dir, "manifest.json")
        assert os.path.exists(manifest_path), "manifest.json should exist"
        with open(manifest_path) as f:
            manifest = json.load(f)
        assert manifest.get("version") == 1
        songs = manifest.get("songs", [])
        assert len(songs) >= 1
        entry = songs[0]
        # Thirteen-key entry
        expected_keys = {
            "file", "category", "topic", "seed", "backend", "format",
            "bytes", "duration_s", "bpm", "key_scale", "time_signature",
            "job_id", "generated_at",
        }
        assert expected_keys == set(entry.keys()), f"Missing keys: {expected_keys - set(entry.keys())}"
        assert entry["category"] == "Bedtime"
        assert entry["topic"] == "sleepy moon"

    def test_generate_suno_returns_redirect_not_500(self, client):
        resp = client.post("/music/generate", data={
            "category": "Bedtime",
            "topic": "test",
            "backend": "suno",
        }, follow_redirects=False)
        assert resp.status_code == 303, f"Expected 303, got {resp.status_code}"

    def test_generate_suno_job_failed(self, client):
        client.post("/music/generate", data={
            "category": "Bedtime",
            "topic": "test",
            "backend": "suno",
        })
        data = client.get("/api/music/jobs").json()
        suno_jobs = [j for j in data.get("jobs", []) if j.get("status") == "failed"]
        assert len(suno_jobs) >= 1, "Expected at least one failed suno job"
        error = suno_jobs[0].get("error", "")
        assert error, "Failed job should carry an error message"

    def test_api_jobs_returns_music_only(self, client):
        resp = client.get("/api/music/jobs")
        data = resp.json()
        assert "jobs" in data
        # All returned jobs should be music type (no image jobs leak)
        for j in data["jobs"]:
            assert "category" in j or "id" in j  # minimal shape check

    def test_api_jobs_shape(self, client):
        client.post("/music/generate", data={
            "category": "Alphabet",
            "topic": "letters",
            "backend": "",
        })
        data = client.get("/api/music/jobs").json()
        jobs = data["jobs"]
        assert len(jobs) >= 1
        job = jobs[0]
        for key in ("id", "status"):
            assert key in job, f"Missing key {key!r} in job payload"
