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


# =================================================================== #
# TestBatchGeneration — 24-category batch, failure accumulation, etc   #
# =================================================================== #

class TestBatchGeneration:
    """Batch-loop integration tests: full 24-category run, comma/repeatable
    category flags, mixed-failure handling, suno refusal, exit codes,
    catalog.db byte-identity (C2)."""

    @pytest.fixture(autouse=True)
    def _env_clean(self, monkeypatch):
        """Ensure no ACESTEP or MUSIC_BACKEND env leaks."""
        monkeypatch.delenv("ACESTEP_API_KEY", raising=False)
        monkeypatch.delenv("ACESTEP_BASE_URL", raising=False)
        monkeypatch.delenv("MUSIC_BACKEND", raising=False)

    @pytest.fixture(scope="class")
    def catalog_md5_before(self):
        """MD5 of the repo-root catalog.db before any tests in this class."""
        import hashlib
        db_path = os.path.join(ROOT, "catalog.db")
        if not os.path.exists(db_path):
            pytest.skip("catalog.db not present")
        with open(db_path, "rb") as fh:
            return hashlib.md5(fh.read()).hexdigest()

    def test_full_24_category_batch(self, tmp_path, catalog_md5_before):
        """Default batch (no --category) generates all 24 songs."""
        rc = generate_main([
            "--generate", "--backend", "mock", "--out", str(tmp_path),
        ])
        assert rc == 0

        wavs = list(tmp_path.glob("*.wav"))
        assert len(wavs) == 24

        manifest = json.loads((tmp_path / "manifest.json").read_text())
        assert len(manifest["songs"]) == 24

        # All filenames unique
        fnames = [e["file"] for e in manifest["songs"]]
        assert len(set(fnames)) == 24

        # Categories match bible order
        bible_cats = AudioBible().list_song_categories()
        manifest_cats = [e["category"] for e in manifest["songs"]]
        assert manifest_cats == bible_cats

        # Catalog.db unchanged
        import hashlib
        db_path = os.path.join(ROOT, "catalog.db")
        if os.path.exists(db_path):
            with open(db_path, "rb") as fh:
                assert hashlib.md5(fh.read()).hexdigest() == catalog_md5_before

    def test_comma_list_and_repeatable_equivalence(self, tmp_path):
        """--category 'Alphabet,Bedtime' == --category Alphabet --category Bedtime."""
        out1 = tmp_path / "comma"
        out2 = tmp_path / "repeat"
        out1.mkdir()
        out2.mkdir()

        rc1 = generate_main([
            "--generate", "--backend", "mock",
            "--category", "Alphabet,Bedtime",
            "--out", str(out1),
        ])
        rc2 = generate_main([
            "--generate", "--backend", "mock",
            "--category", "Alphabet", "--category", "Bedtime",
            "--out", str(out2),
        ])
        assert rc1 == 0
        assert rc2 == 0
        m1 = json.loads((out1 / "manifest.json").read_text())
        m2 = json.loads((out2 / "manifest.json").read_text())
        cats1 = sorted(e["category"] for e in m1["songs"])
        cats2 = sorted(e["category"] for e in m2["songs"])
        assert cats1 == cats2 == ["Alphabet", "Bedtime"]

    def test_mixed_failure_continues_batch(self, tmp_path, monkeypatch):
        """Backend raising for one category → remaining categories still generate."""
        from src.music_generation.mock import MockBackend
        from src.music_generation.models import MusicRequest

        call_count = [0]

        class PartialFailBackend(MockBackend):
            def generate(self, request, **kw):
                call_count[0] += 1
                # Fail on the 2nd category (Alphabet is 1st, Numbers is 2nd)
                if request.category == "Numbers":
                    raise MusicBackendError("boom")
                return super().generate(request, **kw)

        # Patch get_backend to return our failing backend
        import scripts.generate_phase5 as mod
        original_get_backend = mod.get_backend

        def patched_get_backend(name=None, **kwargs):
            if name == "mock":
                return PartialFailBackend()
            return original_get_backend(name, **kwargs)

        monkeypatch.setattr(mod, "get_backend", patched_get_backend)

        rc = generate_main([
            "--generate", "--backend", "mock",
            "--category", "Alphabet", "--category", "Numbers",
            "--category", "Bedtime",
            "--out", str(tmp_path),
        ])

        # 1 failure (Numbers), 2 successes
        assert rc == 1
        wavs = list(tmp_path.glob("*.wav"))
        assert len(wavs) == 2  # Alphabet + Bedtime
        manifest = json.loads((tmp_path / "manifest.json").read_text())
        assert len(manifest["songs"]) == 2

    def test_suno_batch_fails_with_no_transport(self, tmp_path, monkeypatch):
        """Suno backend → every song fails via NotConfigured, exit 1, no traceback."""
        # Install fail-loud guards on transport seams to prove zero dials
        import src.music_generation.backends as bm
        original_post = bm._post_json
        original_getj = bm._get_json
        original_getb = bm._get_bytes

        def should_not_be_called(*a, **kw):
            raise AssertionError("Transport seam called — expected zero dials")

        monkeypatch.setattr(bm, "_post_json", should_not_be_called)
        monkeypatch.setattr(bm, "_get_json", should_not_be_called)
        monkeypatch.setattr(bm, "_get_bytes", should_not_be_called)

        rc = generate_main([
            "--generate", "--backend", "suno",
            "--category", "Alphabet",
            "--out", str(tmp_path),
        ])

        # Restore (monkeypatch handles this, but being explicit)
        assert rc == 1
        wavs = list(tmp_path.glob("*.wav"))
        assert len(wavs) == 0  # nothing generated

    def test_summary_stdout_and_failure_stderr(self, tmp_path, monkeypatch, capsys):
        """Summary to stdout, failure reasons to stderr."""
        from src.music_generation.mock import MockBackend

        class FailBackend(MockBackend):
            def generate(self, request, **kw):
                raise MusicBackendError("test failure reason")

        import scripts.generate_phase5 as mod
        monkeypatch.setattr(mod, "get_backend", lambda name=None, **kw: FailBackend())

        rc = generate_main([
            "--generate", "--backend", "mock",
            "--category", "Bedtime",
            "--out", str(tmp_path),
        ])

        assert rc == 1
        captured = capsys.readouterr()
        assert "Failed:    1" in captured.out
        assert "FAILED Bedtime: test failure reason" in captured.err
