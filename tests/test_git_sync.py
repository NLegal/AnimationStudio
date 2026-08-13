"""Tests for the Colab git auto-sync helper (colab/git_sync.py).

Covers the GitHub PAT auth header (basic auth, not Bearer — GitHub's git
smart-HTTP rejects Bearer) and origin-URL propagation from ``remote_url``.
"""

import base64
import os
import subprocess

import pytest

from colab.git_sync import _basic_auth_header


def _git(*args, cwd=None, check=True):
    res = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True
    )
    if check and res.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {res.stderr}")
    return res


@pytest.fixture
def scratch_repo(tmp_path):
    """A git repo with a bare origin remote."""
    repo = tmp_path / "repo"
    bare = tmp_path / "bare.git"
    repo.mkdir()
    _git("init", cwd=str(repo))
    _git("config", "user.email", "test@example.com", cwd=str(repo))
    _git("config", "user.name", "Test", cwd=str(repo))
    _git("init", "--bare", str(bare))
    _git("remote", "add", "origin", str(bare), cwd=str(repo))
    (repo / "README.md").write_text("hi")
    _git("add", ".", cwd=str(repo))
    _git("commit", "-m", "init", cwd=str(repo))
    _git("branch", "-M", "main", cwd=str(repo))
    return {"repo": str(repo), "bare": str(bare)}


class TestBasicAuthHeader:
    """The GitHub PAT header must be basic auth with x-access-token."""

    def test_encodes_x_access_token(self):
        header = _basic_auth_header("ghp_testtoken")
        assert header.startswith("basic ")
        decoded = base64.b64decode(header.split(" ", 1)[1]).decode()
        assert decoded == "x-access-token:ghp_testtoken"

    def test_roundtrip_any_token(self):
        header = _basic_auth_header("secret-123")
        decoded = base64.b64decode(header.split(" ", 1)[1]).decode()
        assert decoded.startswith("x-access-token:")


class TestAutoSync:
    """auto_sync copies the DB, commits, repoints origin, and pushes."""

    def test_remote_url_repoints_origin(self, scratch_repo, tmp_path):
        from colab.git_sync import auto_sync

        new_bare = tmp_path / "new_bare.git"
        _git("init", "--bare", str(new_bare))
        db = tmp_path / "catalog.db"
        db.write_bytes(b"db-bytes")

        pushed = auto_sync(
            repo=scratch_repo["repo"],
            branch="main",
            db_path=str(db),
            remote_url=str(new_bare),
            token="ghp_testtoken",
        )
        assert pushed is True

        origin = _git(
            "remote", "get-url", "origin", cwd=scratch_repo["repo"]
        ).stdout.strip()
        assert origin == str(new_bare)

        # The new bare remote actually received the commit.
        branch = _git(
            "branch", "--list", "main", cwd=str(new_bare)
        ).stdout
        assert "main" in branch

    def test_autosync_commits_db_and_images(self, scratch_repo, tmp_path):
        from colab.git_sync import auto_sync

        db = tmp_path / "catalog.db"
        db.write_bytes(b"db-bytes")
        assets = tmp_path / "repo" / "Assets"
        assets.mkdir(parents=True)
        (assets / "happy.png").write_bytes(b"png")

        pushed = auto_sync(
            repo=scratch_repo["repo"],
            branch="main",
            db_path=str(db),
            remote_url=scratch_repo["bare"],
            dirs=("Assets",),
        )
        assert pushed is True

        bare = _git("show", "main:catalog.db", cwd=str(scratch_repo["bare"])).stdout
        assert bare == "db-bytes"
        assert b"png" == _git(
            "show", "main:Assets/happy.png", cwd=str(scratch_repo["bare"])
        ).stdout.encode()

    def test_autosync_idempotent_when_clean(self, scratch_repo, tmp_path):
        """Second sync with nothing new pushes nothing and returns False."""
        from colab.git_sync import auto_sync

        db = tmp_path / "catalog.db"
        db.write_bytes(b"db-bytes")

        first = auto_sync(
            repo=scratch_repo["repo"],
            branch="main",
            db_path=str(db),
            remote_url=scratch_repo["bare"],
        )
        assert first is True
        second = auto_sync(
            repo=scratch_repo["repo"],
            branch="main",
            db_path=str(db),
            remote_url=scratch_repo["bare"],
        )
        assert second is False


class TestWalCheckpoint:
    """auto_sync must flush WAL contents before copying the DB file."""

    def test_checkpoint_flushes_wal_before_copy(self, scratch_repo, tmp_path):
        import sqlite3

        from colab.git_sync import auto_sync

        db = tmp_path / "catalog.db"
        conn = sqlite3.connect(str(db))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("CREATE TABLE assets (id TEXT)")
        conn.execute("INSERT INTO assets VALUES ('wal-row')")
        conn.commit()
        # Keep the connection open: without a checkpoint the row lives only
        # in catalog.db-wal and a plain copy would commit a stale DB.
        assert os.path.exists(str(db) + "-wal")

        pushed = auto_sync(
            repo=scratch_repo["repo"],
            branch="main",
            db_path=str(db),
            remote_url=scratch_repo["bare"],
        )
        assert pushed is True
        conn.close()

        committed = tmp_path / "committed.db"
        blob = subprocess.run(
            ["git", "show", "main:catalog.db"],
            cwd=scratch_repo["bare"], capture_output=True, check=True,
        ).stdout
        committed.write_bytes(blob)
        check = sqlite3.connect(str(committed))
        rows = check.execute("SELECT id FROM assets").fetchall()
        check.close()
        assert rows == [("wal-row",)]
