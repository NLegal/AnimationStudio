#!/usr/bin/env python3
"""verify_catalog.py — Health check for the production catalog.db.

Detects the corruption signature caused by a sudden Colab termination
(see TODOPROJECT.md "RECOVERY — catalog.db") and reports per-table counts
so a doc-vs-DB discrepancy (e.g. the old 18,071 claim) is visible.

Usage:
    python scripts/verify_catalog.py [--db catalog.db]

Exit codes:
    0  healthy
    1  integrity_check failed or tables missing/unexpected
    2  WAL/SHM sidecar files detected (stale checkpoint possible)

Example recovery (only if exit 2 occurred after a Colab crash):
    Remove-Item catalog.db-wal, catalog.db-shm
    python scripts/verify_catalog.py
"""

import argparse
import os
import sqlite3
import sys
from pathlib import Path

EXPECTED_TABLES = {"characters", "assets"}


def verify(db_path: str) -> int:
    code = 0

    wal = f"{db_path}-wal"
    shm = f"{db_path}-shm"
    stale_sidecars = [p for p in (wal, shm) if os.path.exists(p)]
    if stale_sidecars:
        print(f"[FAIL] stale SQLite sidecar file(s) present: {', '.join(stale_sidecars)}")
        print("       remove them and re-run; they mean a checkpoint never completed")
        print("       Check for active writers (Review UI / Colab session) first.")
        code = 2

    if not os.path.exists(db_path):
        print(f"[FAIL] database not found: {db_path}")
        return 2

    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as exc:
        print(f"[FAIL] cannot open database: {exc}")
        return max(code, 1)
    cur = conn.cursor()

    try:
        cur.execute("PRAGMA integrity_check")
    except sqlite3.Error as exc:
        print(f"[FAIL] PRAGMA integrity_check -> {exc}")
        print("       see TODOPROJECT.md RECOVERY section")
        conn.close()
        return max(code, 1)
    result = cur.fetchone()
    if result != ("ok",):
        print(f"[FAIL] PRAGMA integrity_check -> {result}")
        print("       see TODOPROJECT.md RECOVERY section")
        code = max(code, 1)
    else:
        print("[ OK ] PRAGMA integrity_check -> ok")

    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall() if not row[0].startswith("sqlite_")}
    missing = EXPECTED_TABLES - tables
    if missing:
        print(f"[FAIL] missing table(s): {sorted(missing)}")
        code = max(code, 1)

    counts = {}
    for table in sorted(EXPECTED_TABLES & tables):
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cur.fetchone()[0]
        print(f"[ OK ] {table}: {counts[table]} rows")

    for table in sorted(tables):
        if table not in EXPECTED_TABLES:
            print(f"[info] extra table: {table}")

    if "assets" in counts:
        cur.execute("SELECT name FROM pragma_table_info('assets')")
        cols = {row[0] for row in cur.fetchall()}
        if "state" in cols:
            cur.execute("SELECT state, COUNT(*) FROM assets GROUP BY state ORDER BY 2 DESC")
            states = dict(cur.fetchall())
            print(f"[info] asset states: {states}")
            approved = sum(states.get(s, 0) for s in ("approved", "production"))
            if approved == 0:
                print("[info] approved/production assets: 0 (LoRA dataset build will find nothing)")
        else:
            print("[info] assets has no 'state' column (minimal/synthetic schema)")

    conn.close()
    print(f"[done] exit={code}" if code == 0 else f"[done] exit={code} (action needed)")
    return code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="catalog.db",
                        help="SQLite database path (default: catalog.db)")
    args = parser.parse_args()
    return verify(Path(args.db).as_posix())


if __name__ == "__main__":
    sys.exit(main())