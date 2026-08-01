#!/usr/bin/env python3
"""finalize_phase1.py — Approve final assets so the Phase 1 library is "real".

Promotes shortlisted assets to ``approved`` (and stamps ``approved_at``) so
the quality checklist item "reference approved" is satisfied for every
finalized character.

By default only the highest-scoring *reference* (front view) per character is
approved — the canonical "finalized character" reference.  Use ``--all`` to
approve every shortlisted asset (the full Phase 1 library).

Usage:
    python scripts/finalize_phase1.py --db catalog.db
    python scripts/finalize_phase1.py --all
"""

import argparse
import datetime
import sqlite3
import sys
from pathlib import Path

APPROVED_STATES = ("approved", "production")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", default="catalog.db", help="SQLite database path")
    parser.add_argument("--all", action="store_true",
                        help="Approve every shortlisted asset (full library) "
                             "instead of only the best reference per character")
    parser.add_argument("--characters", default="",
                        help="Comma list of character names to finalize (default: all)")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    now = datetime.datetime.now(datetime.UTC).isoformat()

    char_filter = ""
    params = []
    if args.characters:
        wanted = [c.strip() for c in args.characters.split(",") if c.strip()]
        char_filter = f" AND c.name IN ({', '.join('?' * len(wanted))})"
        params = wanted

    if args.all:
        rows = conn.execute(
            "SELECT a.id FROM assets a JOIN characters c ON c.id = a.character_id "
            "WHERE a.state = 'shortlisted'" + char_filter,
            params,
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT a.id FROM assets a JOIN characters c ON c.id = a.character_id "
            "WHERE a.state = 'shortlisted' AND a.asset_type = 'reference' "
            "AND a.variant = 'front' "
            "AND a.brand_score = ("
            "  SELECT MAX(a2.brand_score) FROM assets a2 "
            "  WHERE a2.character_id = a.character_id AND a2.asset_type = 'reference' "
            "  AND a2.variant = 'front' AND a2.state = 'shortlisted'"
            ")" + char_filter,
            params,
        ).fetchall()

    for (asset_id,) in rows:
        conn.execute(
            "UPDATE assets SET state = 'approved', approved_at = ? WHERE id = ?",
            (now, asset_id),
        )

    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM assets WHERE state = 'approved'").fetchone()[0]
    print(f"Approved {len(rows)} assets ({total} approved total in DB).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
