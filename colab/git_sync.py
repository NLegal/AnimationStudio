"""Incremental git sync for the AnimationStudio Colab notebooks.

Uploads freshly generated images (plus the asset DB) to GitHub immediately
after a generation batch — approved or not — so a lost/restarted session
never forces a full regeneration.

Usage (from a notebook cell):

    import sys
    sys.path.insert(0, f"{REPO}/colab")
    from git_sync import auto_sync

    auto_sync(repo=REPO, branch=BRANCH, db_path=DB,
              token=GITHUB_TOKEN, git_name=GIT_NAME, git_email=GIT_EMAIL)
"""

import os
import shutil
import subprocess
from datetime import datetime


def _run(cmd, cwd=None, check=True):
    print("+ " + " ".join(str(c) for c in cmd))
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr:
        print(res.stderr.strip())
    if check and res.returncode != 0:
        raise subprocess.CalledProcessError(
            res.returncode, cmd, res.stdout, res.stderr
        )
    return res


def auto_sync(
    repo: str,
    branch: str,
    db_path: str,
    token: str = "",
    git_name: str = "Colab Studio",
    git_email: str = "colab@animationstudio.local",
    dirs: tuple[str, ...] = ("Universe", "World", "Assets"),
    message: str | None = None,
) -> bool:
    """Copy the Drive DB into the repo, commit new/changed files, and push.

    Returns True when something was pushed, False otherwise (including
    failures — generation must never be blocked by a sync hiccup).

    Args:
        repo: Path to the cloned AnimationStudio checkout.
        branch: Git branch to push (e.g. "colab-gpu").
        db_path: The catalog DB that was just written (usually on Drive).
        token: GitHub PAT.  Colab has no credential helper, so the token is
            passed per-command via ``http.extraheader`` and never stored.
        dirs: Repository subdirectories that hold generated images.
        message: Optional commit message; defaults to a timestamped one.
    """
    try:
        if os.path.exists(db_path):
            repo_db = os.path.join(repo, "catalog.db")
            try:
                same = os.path.samefile(db_path, repo_db)
            except OSError:
                same = False
            if not same:
                shutil.copyfile(db_path, repo_db)
        else:
            print("Auto-sync: no DB at", db_path, "— committing images only")

        _run(["git", "config", "user.name", git_name], cwd=repo, check=False)
        _run(["git", "config", "user.email", git_email], cwd=repo, check=False)

        # Only stage directories that actually exist (World/Assets may not
        # have been created on the very first run).
        existing = [d for d in dirs if os.path.isdir(os.path.join(repo, d))]
        _run(["git", "add", "-f", "catalog.db", *existing], cwd=repo, check=False)

        dirty = _run(["git", "status", "--porcelain"], cwd=repo, check=False)
        if not dirty.stdout.strip():
            print("Auto-sync: nothing new to commit")
            return False

        msg = message or f"generated assets {datetime.now():%Y-%m-%d %H:%M:%S}"
        _run(["git", "commit", "-m", msg], cwd=repo, check=False)

        pushed = dirty.stdout.strip().count("\n") + 1
        if token:
            _run(
                ["git", "-c", f"http.extraheader=Authorization: Bearer {token}",
                 "push", "origin", branch],
                cwd=repo,
            )
        else:
            _run(["git", "push", "origin", branch], cwd=repo)

        print(f"Auto-sync: pushed {pushed} new/changed file(s) to {branch}")
        return True
    except Exception as exc:
        print("Auto-sync FAILED (generation continues):", exc)
        return False
