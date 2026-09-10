"""Test the production catalog.db health and the verify_catalog.py guard.

Covers TODOPROJECT.md C-00: the corruption signature caused by a sudden
Google Colab termination (stale -wal/-shm sidecars) and the recovery
procedure (sidecar removal) are validated here offline.
"""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "catalog.db"

ALLOWED_STATES = {
    "pending", "generated", "scored", "shortlisted", "approved",
    "production", "rejected", "archived",
}


@pytest.fixture(scope="module")
def prod_db():
    if not DB_PATH.is_file():
        pytest.skip("catalog.db not present")
    return DB_PATH


class TestCatalogIntegrity:
    """The recovered catalog.db must be fully consistent."""

    def test_no_stale_sidecars(self, prod_db):
        assert not Path(str(prod_db) + "-wal").exists(), "stale -wal present after recovery"
        assert not Path(str(prod_db) + "-shm").exists(), "stale -shm present after recovery"

    def test_integrity_check_ok(self, prod_db):
        conn = sqlite3.connect(str(prod_db))
        conn.execute("PRAGMA foreign_keys=ON")
        assert conn.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        conn.close()

    def test_expected_tables_present(self, prod_db):
        conn = sqlite3.connect(str(prod_db))
        tables = {
            r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        conn.close()
        assert {"characters", "assets"} <= tables

    def test_characters_and_assets_populated(self, prod_db):
        conn = sqlite3.connect(str(prod_db))
        chars = conn.execute("SELECT COUNT(*) FROM characters").fetchone()[0]
        assets = conn.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
        conn.close()
        assert chars >= 39, f"expected >=39 characters, got {chars}"
        assert assets > 0, "assets table empty"

    def test_no_null_or_duplicate_primary_keys(self, prod_db):
        conn = sqlite3.connect(str(prod_db))
        dupes = conn.execute(
            "SELECT id FROM assets GROUP BY id HAVING COUNT(*) > 1"
        ).fetchall()
        nulls = conn.execute(
            "SELECT COUNT(*) FROM assets WHERE id IS NULL OR character_id IS NULL"
        ).fetchone()[0]
        state_bad = conn.execute(
            "SELECT COUNT(*) FROM assets WHERE state IS NOT NULL AND state NOT IN (%s)"
            % ",".join("?" * len(ALLOWED_STATES)),
            list(ALLOWED_STATES),
        ).fetchone()[0]
        conn.close()
        assert not dupes, f"duplicate asset ids: {dupes[:5]}"
        assert nulls == 0, f"{nulls} rows with NULL id/character_id"
        assert state_bad == 0, f"{state_bad} rows in unexpected asset states"


class TestVerifyCatalogScript:
    """scripts/verify_catalog.py must fail closed on corrupt DBs."""

    def _run(self, db: Path):
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "verify_catalog.py"), "--db", str(db)],
            capture_output=True, text=True,
        )

    def test_healthy_db_exits_zero(self, tmp_path):
        db = tmp_path / "catalog.db"
        conn = sqlite3.connect(str(db))
        conn.execute("CREATE TABLE characters (id TEXT PRIMARY KEY)")
        conn.execute("CREATE TABLE assets (id TEXT PRIMARY KEY, character_id TEXT)")
        conn.execute("INSERT INTO characters VALUES ('001')")
        conn.execute("INSERT INTO assets VALUES ('a1', '001')")
        conn.commit()
        conn.close()
        r = self._run(db)
        assert r.returncode == 0, r.stdout + r.stderr

    def test_corrupt_db_exits_one(self, tmp_path):
        db = tmp_path / "catalog.db"
        db.write_bytes(b"this is not a sqlite file")
        r = self._run(db)
        assert r.returncode >= 1, r.stdout

    def test_stale_sidecar_exits_two(self, tmp_path):
        db = tmp_path / "catalog.db"
        db.write_bytes(b"garbage")
        with open(str(db) + "-wal", "w") as fh:  # noqa: PTH123
            fh.write("stale")
        r = self._run(db)
        assert r.returncode == 2, r.stdout
        assert "-wal" in r.stdout or "-wal" in r.stderr
        Path(str(db) + "-wal").unlink(missing_ok=True)