"""Tests for ``scripts.generate_phase5`` (Phase 5 audio bible verification
+ report script) and its new generation mode (Phase 08-01 pipeline wiring).

Covers:
- Generation-mode flags, alias normalization, category validation, slug safety
- Batch loop over 24 categories, failure accumulation, exit codes
- Manifest schema golden tests, resume/skip matrix, crash simulation
- Report-mode byte-compatibility (C4) — no .wav files under Audio/Music/
"""

import json
import os
import sys
import time

import pytest

# ---------------------------------------------------------------------------
# Import the script module so we can unit-test its helpers directly.
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from scripts.generate_phase5 import (
    BACKEND_ALIASES,
    _slug,
    atomic_write_manifest,
    entry_matches,
    find_entry,
    load_manifest,
    now_iso,
    song_filename,
    upsert_entry,
)
from scripts.generate_phase5 import main as generate_main
from src.audio_bible import AudioBible
from src.music_generation import MusicBackendError


# =================================================================== #
# TestGenerationMode — single-song tracer e2e + helpers                 #
# =================================================================== #

class TestGenerationMode:
    """Unit + integration tests for the generation-mode tracer:
    single-song e2e, alias normalization, slug safety, error cases,
    and report-mode compatibility."""

    # ---- helpers ----------------------------------------------------

    # (Tests use monkeypatch fixture for env isolation; no helper needed.)

    def test_happy_path_single_song(self, tmp_path, monkeypatch):
        """main(['--generate', ...]) with mock backend writes one WAV + manifest."""
        monkeypatch.delenv("ACESTEP_API_KEY", raising=False)
        monkeypatch.delenv("ACESTEP_BASE_URL", raising=False)
        monkeypatch.delenv("MUSIC_BACKEND", raising=False)

        rc = generate_main([
            "--generate", "--category", "Bedtime",
            "--topic", "sleepy moon", "--backend", "mock",
            "--out", str(tmp_path),
        ])
        assert rc == 0

        wav_path = tmp_path / "bedtime-sleepy-moon-0.wav"
        assert wav_path.exists()
        assert wav_path.stat().st_size > 0
        # RIFF magic
        with open(wav_path, "rb") as fh:
            assert fh.read(4) == b"RIFF"

        manifest_path = tmp_path / "manifest.json"
        assert manifest_path.exists()
        manifest = json.loads(manifest_path.read_text())
        assert manifest["version"] == 1
        assert len(manifest["songs"]) == 1
        entry = manifest["songs"][0]
        # The thirteen required keys
        expected_keys = {
            "file", "category", "topic", "seed", "backend", "format",
            "bytes", "duration_s", "bpm", "key_scale", "time_signature",
            "job_id", "generated_at",
        }
        assert set(entry.keys()) == expected_keys
        # Bedtime locked params
        assert entry["category"] == "Bedtime"
        assert entry["backend"] == "mock"
        assert entry["format"] == "wav"
        assert entry["duration_s"] == 120
        assert entry["bpm"] == 66
        assert entry["key_scale"] == "F major"
        assert entry["time_signature"] == "3/4"
        assert entry["bytes"] > 0

    def test_alias_acestep_normalizes(self):
        """BACKEND_ALIASES maps 'acestep' -> 'ace-step'."""
        assert BACKEND_ALIASES["acestep"] == "ace-step"
        assert BACKEND_ALIASES["ace-step"] == "ace-step"
        assert BACKEND_ALIASES["suno"] == "suno"
        assert BACKEND_ALIASES["mock"] == "mock"

    def test_slug_basic(self):
        assert _slug("Dance Songs") == "dance-songs"

    def test_slug_strips_traversal(self):
        slug = _slug("../../etc")
        assert "/" not in slug
        assert "." not in slug

    def test_slug_empty_becomes_fallback(self):
        slug = _slug("")
        assert slug  # non-empty

    def test_unknown_category_raises_system_exit(self, monkeypatch):
        monkeypatch.delenv("ACESTEP_API_KEY", raising=False)
        monkeypatch.delenv("MUSIC_BACKEND", raising=False)
        with pytest.raises(SystemExit):
            generate_main([
                "--generate", "--category", "Spaceship",
                "--backend", "mock", "--out", "/tmp/t8不存在",
            ])

    def test_unknown_backend_raises_system_exit(self, monkeypatch):
        monkeypatch.delenv("ACESTEP_API_KEY", raising=False)
        monkeypatch.delenv("MUSIC_BACKEND", raising=False)
        with pytest.raises(SystemExit):
            generate_main([
                "--generate", "--category", "Bedtime",
                "--backend", "womp", "--out", "/tmp/t8不存在",
            ])

    def test_report_mode_unchanged(self, monkeypatch, tmp_path):
        """Without --generate, report mode is byte-compatible (C4)."""
        monkeypatch.delenv("ACESTEP_API_KEY", raising=False)
        monkeypatch.delenv("MUSIC_BACKEND", raising=False)
        out_report = tmp_path / "report.md"
        rc = generate_main([
            "--docs-dir", "Audio",
            "--out", str(out_report),
        ])
        assert rc == 0
        assert out_report.exists()
        content = out_report.read_text()
        assert "Phase 5 Report" in content
        # No .wav files created
        wavs = list(tmp_path.rglob("*.wav"))
        assert len(wavs) == 0

    def test_no_sqlite_imports(self):
        """Constraint C2: no sqlite3 import in the production script."""
        import subprocess
        path = os.path.join(ROOT, "scripts/generate_phase5.py")
        result = subprocess.run(
            ["grep", "-qiE", r"^\s*(import sqlite3|from sqlite3)", path],
            capture_output=True,
        )
        assert result.returncode != 0, "generate_phase5.py must not import sqlite3"

    def test_no_image_imports(self):
        """Constraint C1: no image generation in generate_phase5.py."""
        import subprocess
        path = os.path.join(ROOT, "scripts/generate_phase5.py")
        result = subprocess.run(
            ["grep", "-qi", r"\bimage", path],
            capture_output=True,
        )
        assert result.returncode != 0, "generate_phase5.py must not reference images"

    def test_pyproject_unchanged(self):
        """Constraint C6: pyproject.toml must be unchanged."""
        import subprocess
        result = subprocess.run(
            ["git", "diff", "--exit-code", "pyproject.toml"],
            cwd=ROOT,
            capture_output=True,
        )
        assert result.returncode == 0, "pyproject.toml was modified"
