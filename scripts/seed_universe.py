#!/usr/bin/env python3
"""seed_universe.py — Seed the studio database from the Universe/World/Assets catalog.

Loads all 39 character bios, the 9 world zones, and the reusable props/assets
into a SQLite CharacterRepository so the Review UI and the generation pipeline
operate on the full universe.

Usage:
    python scripts/seed_universe.py [--db catalog.db] [--no-props]
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.asset_repository.sqlite_repo import SQLiteCharacterRepository
from src.universe.seed import seed_all


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="catalog.db",
                        help="SQLite database path (default: catalog.db)")
    parser.add_argument("--universe", default="Universe",
                        help="Path to the Universe/ directory")
    parser.add_argument("--world", default="World",
                        help="Path to the World/ directory")
    parser.add_argument("--assets", default="Assets",
                        help="Path to the Assets/ directory")
    parser.add_argument("--no-props", action="store_true",
                        help="Skip seeding reusable props/assets")
    args = parser.parse_args()

    char_repo = SQLiteCharacterRepository(db_path=args.db)
    summary = await seed_all(
        char_repo,
        universe_dir=args.universe,
        world_dir=args.world,
        assets_dir=args.assets,
        include_props=not args.no_props,
    )

    print(f"Seeded '{args.db}':")
    print(f"  characters:   {summary['characters']}")
    print(f"  environments: {summary['environments']}")
    print(f"  props:        {summary['props']}")
    print(f"  total new:    {summary['total']}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
