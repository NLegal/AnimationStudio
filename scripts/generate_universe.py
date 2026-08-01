#!/usr/bin/env python3
"""generate_universe.py — Batch generation for the full studio universe.

Generates candidates for characters, world zones, and/or reusable props
through the standard pipeline (prompt → generate → score → diversity filter
→ shortlist) and saves them into the SQLite repository for human review.

Works with any backend:
  - mock:    deterministic placeholder images (no hardware needed)
  - comfyui: requires ComfyUI at http://localhost:8188 with Flux installed
  - cloud:   requires FAL_API_KEY / REPLICATE_API_KEY / BFL_API_KEY

Usage:
    python scripts/generate_universe.py --scope all --backend mock --count 8
    python scripts/generate_universe.py --scope characters --backend comfyui --serve
    python scripts/generate_universe.py --scope props --backend cloud --count 4 --limit 20

After generating, start the Review UI to approve/shortlist the winners:
    python scripts/generate_universe.py --serve
"""

import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.asset_repository.sqlite_repo import SQLiteAssetRepository, SQLiteCharacterRepository
from src.universe.batch_generator import BatchRunner, resolve_backend
from src.universe.catalog import discover_characters, discover_environments, discover_props

logger = logging.getLogger(__name__)


def _parse_scope(value: str) -> list[str]:
    """Expand 'all' into the individual scopes."""
    value = (value or "all").lower()
    scopes = ["characters", "environments", "props"]
    if value == "all":
        return scopes
    for s in scopes:
        if value == s:
            return [s]
    raise SystemExit(f"Unknown scope '{value}'. Use one of: characters, environments, props, all")


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scope", default="all",
                        help="characters | environments | props | all (default: all)")
    parser.add_argument("--backend", default="mock",
                        help="mock | comfyui | cloud (default: mock)")
    parser.add_argument("--provider", default="fal",
                        help="Cloud provider for --backend cloud: fal | replicate | bfl")
    parser.add_argument("--comfyui-url", default="http://localhost:8188",
                        help="ComfyUI server URL (default: http://localhost:8188)")
    parser.add_argument("--count", type=int, default=8,
                        help="Candidates to generate per item (default: 8)")
    parser.add_argument("--shortlist", type=int, default=5,
                        help="Top candidates to shortlist per item (default: 5)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Max items to process per scope (default: all)")
    parser.add_argument("--jobs", type=int, default=1,
                        help="Concurrent generation jobs (default: 1)")
    parser.add_argument("--db", default="catalog.db",
                        help="SQLite database path (default: catalog.db)")
    parser.add_argument("--universe", default="Universe",
                        help="Path to the Universe/ directory")
    parser.add_argument("--world", default="World",
                        help="Path to the World/ directory")
    parser.add_argument("--assets", default="Assets",
                        help="Path to the Assets/ directory")
    parser.add_argument("--asset-type", default=None,
                        help="For characters: reference | expression | pose | outfit")
    parser.add_argument("--variant", default="front",
                        help="Variant name for character generation (default: front)")
    parser.add_argument("--prompt-only", action="store_true",
                        help="Print prompts without generating images")
    parser.add_argument("--serve", action="store_true",
                        help="Start the Review UI after generation")
    parser.add_argument("--port", type=int, default=8000,
                        help="Review UI port (default: 8000)")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable debug logging")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    scopes = _parse_scope(args.scope)

    asset_repo = SQLiteAssetRepository(db_path=args.db)
    char_repo = SQLiteCharacterRepository(db_path=args.db)
    backend = resolve_backend(args.backend, comfyui_url=args.comfyui_url,
                              provider=args.provider)
    runner = BatchRunner(asset_repo=asset_repo, char_repo=char_repo, backend=backend)

    print("=" * 70)
    print(f"  UNIVERSE GENERATION — scope={', '.join(scopes)} backend={args.backend}")
    print(f"  db={args.db}  count={args.count}  shortlist={args.shortlist}"
          f"  jobs={args.jobs}")
    print("=" * 70)

    batch_id = f"universe_{int(time.time())}"
    overall = {"generated": 0, "shortlisted": 0, "succeeded": 0, "failed": 0}

    for scope in scopes:
        if scope == "characters":
            seeds = discover_characters(args.universe)
            kind = "character"
        elif scope == "environments":
            seeds = discover_environments(args.world)
            kind = "environment"
        else:
            seeds = discover_props(args.world, args.assets)
            kind = "prop"

        print(f"\n▶ {scope} ({len(seeds)} items)")

        if args.prompt_only:
            for seed in seeds[: args.limit] if args.limit else seeds:
                from src.universe.batch_generator import build_prompt
                asset_type = args.asset_type or {
                    "character": "reference", "environment": "environment",
                    "prop": "prop",
                }[kind]
                positive, negative = build_prompt(seed, kind, asset_type, args.variant)
                label = getattr(seed, "name", None) or getattr(seed, "asset_id", None)
                print(f"\n--- {label} ---")
                print(f"POSITIVE: {positive}")
                print(f"NEGATIVE: {negative}")
            continue

        summary = await runner.run_seeds(
            seeds, kind,
            count=args.count,
            shortlist=args.shortlist,
            limit=args.limit,
            jobs=args.jobs,
            batch_id=batch_id,
        )
        overall["generated"] += summary["total_generated"]
        overall["shortlisted"] += summary["total_shortlisted"]
        overall["succeeded"] += summary["items_succeeded"]
        overall["failed"] += summary["items_failed"]

        print(f"  generated: {summary['total_generated']}")
        print(f"  shortlisted: {summary['total_shortlisted']}")
        print(f"  items: {summary['items_succeeded']} ok, "
              f"{summary['items_failed']} failed")
        for fail in summary["failures"]:
            print(f"    ✗ {fail.get('name')}: {fail.get('error')}")

    print("\n" + "=" * 70)
    print("  SUMMARY")
    print(f"  Batch:        {batch_id}")
    print(f"  Items ok:     {overall['succeeded']}  failed: {overall['failed']}")
    print(f"  Generated:    {overall['generated']}")
    print(f"  Shortlisted:  {overall['shortlisted']}")
    print(f"  DB:           {args.db}")
    print("=" * 70)

    if args.serve:
        await _serve(args)

    return 0


async def _serve(args) -> None:
    """Start the Review UI wired to the same database + generation backend."""
    import uvicorn
    from src.review_ui.app import create_app
    from src.universe.batch_generator import resolve_backend as _resolve
    from src.universe.seed import seed_all
    from src.universe.sqlite_bridge import SQLiteCombinedRepo

    asset_repo = SQLiteAssetRepository(db_path=args.db)
    char_repo = SQLiteCharacterRepository(db_path=args.db)
    combined = SQLiteCombinedRepo(char_repo, asset_repo)
    backend = _resolve(args.backend, comfyui_url=args.comfyui_url,
                       provider=args.provider)

    async def _seed(char_repo_):
        return await seed_all(char_repo_)

    app = create_app(
        asset_repo=combined,
        character_repo=char_repo,
        generation_backend=backend,
        seed_catalog=_seed,
    )
    print(f"\nReview UI starting at http://localhost:{args.port}")
    uvicorn.run(app, host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
