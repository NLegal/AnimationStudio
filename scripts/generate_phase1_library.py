#!/usr/bin/env python3
"""generate_phase1_library.py — Generate the full Phase 1 character library.

Produces the complete per-character asset library from PHASE1.md:

  * reference sheets (front view)
  * expressions (all known expressions)
  * poses (all known poses)
  * outfits (each wardrobe variant from the character's bio)
  * turnarounds (front / 45 / left / right / back / top / bottom)
  * lighting studies (morning, golden hour, night, …)

Every image goes through the standard pipeline (prompt → generate → score →
diversity filter → shortlist) and is persisted into the SQLite repository so
the Review UI and the export tooling can approve/lock it.

Works with any backend (mock / comfyui / cloud).  The mock backend is the
offline default and produces deterministic placeholder images.

Usage:
    python scripts/generate_phase1_library.py --backend mock --count 2
    python scripts/generate_phase1_library.py --characters "Lily Bunny" --asset-types expressions --prompt-only
    python scripts/generate_phase1_library.py --asset-types turnarounds,lighting
"""

import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.asset_repository.sqlite_repo import SQLiteAssetRepository, SQLiteCharacterRepository
from src.identity_engine.scorer import IdentityScorer
from src.prompt_builder.builder import PromptBuilder
from src.universe.batch_generator import BatchRunner, build_prompt, resolve_backend
from src.universe.catalog import discover_characters

logger = logging.getLogger(__name__)

# Library catalogue (PHASE1.md).  Expressions/poses are pulled from the
# PromptBuilder so the source of truth stays in one place.
EXPRESSIONS: list[str] = sorted(PromptBuilder._known_expressions())
POSES: list[str] = sorted(PromptBuilder._known_poses())
# "front" belongs to the reference library; turnarounds cover the other angles.
TURNAROUNDS: list[str] = ["45", "left", "right", "back", "top", "bottom"]
LIGHTING: list[str] = [
    "morning", "afternoon", "golden hour", "night", "moonlight", "rain",
    "snow", "cloudy", "indoor", "birthday lights", "christmas lights",
]

# asset-type key → (display name, human label)
ASSET_TYPES: dict[str, tuple[str, str]] = {
    "reference": ("reference", "reference sheet"),
    "expressions": ("expression", "expression"),
    "poses": ("pose", "pose"),
    "outfits": ("outfit", "outfit"),
    "turnarounds": ("reference", "turnaround"),
    "lighting": ("lighting", "lighting study"),
}


def _parse_asset_types(value: str) -> list[str]:
    """Expand the --asset-types option into individual library keys."""
    value = (value or "all").lower()
    keys = list(ASSET_TYPES)
    if value == "all":
        return keys
    wanted = [v.strip() for v in value.split(",") if v.strip()]
    for w in wanted:
        if w not in keys:
            raise SystemExit(
                f"Unknown asset type '{w}'. Use one of: {', '.join(keys)}, all"
            )
    return wanted


def _outfits_for(seed) -> list[str]:
    """Wardrobe variant names for a character (from the bio's wardrobe table)."""
    wardrobe = seed.bio_data.get("wardrobe", {})
    return [name for name in wardrobe if name]


def _variants(asset_type: str, seed) -> list[str]:
    """The variant labels for one library asset type."""
    key = asset_type
    if key == "reference":
        return ["front"]
    if key == "expressions":
        return EXPRESSIONS
    if key == "poses":
        return POSES
    if key == "outfits":
        return _outfits_for(seed) or ["default outfit"]
    if key == "turnarounds":
        return TURNAROUNDS
    if key == "lighting":
        return LIGHTING
    return []


def _tasks(seeds: list, asset_types: list[str]):
    """Yield (seed, asset_type_key, asset_type, variant) task tuples."""
    for seed in seeds:
        for key in asset_types:
            asset_type, _label = ASSET_TYPES[key]
            for variant in _variants(key, seed):
                yield seed, key, asset_type, variant


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--asset-types", default="all",
                        help="Comma list or 'all' (default): reference, expressions, "
                             "poses, outfits, turnarounds, lighting")
    parser.add_argument("--backend", default="mock",
                        help="mock | comfyui | cloud (default: mock)")
    parser.add_argument("--provider", default="fal",
                        help="Cloud provider for --backend cloud: fal | replicate | bfl")
    parser.add_argument("--comfyui-url", default="http://localhost:8188",
                        help="ComfyUI server URL (default: http://localhost:8188)")
    parser.add_argument("--count", type=int, default=2,
                        help="Candidates to generate per (character, variant) (default: 2)")
    parser.add_argument("--shortlist", type=int, default=1,
                        help="Top candidates to shortlist per (character, variant) (default: 1)")
    parser.add_argument("--characters", default="",
                        help="Comma list of character names to include (default: all)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Max characters to process (default: all)")
    parser.add_argument("--jobs", type=int, default=4,
                        help="Concurrent generation jobs (default: 4)")
    parser.add_argument("--fast-scoring", action="store_true",
                        help="Skip torch-backed scoring plugins (DINOv2/CLIP); "
                             "much faster, fine for mock placeholders")
    parser.add_argument("--db", default="catalog.db",
                        help="SQLite database path (default: catalog.db)")
    parser.add_argument("--universe", default="Universe",
                        help="Path to the Universe/ directory")
    parser.add_argument("--world", default="World",
                        help="Path to the World/ directory")
    parser.add_argument("--assets", default="Assets",
                        help="Path to the Assets/ directory")
    parser.add_argument("--persist-images", dest="persist_images",
                        action="store_true", default=True,
                        help="Write each generated image into the catalog tree "
                             "(default: on)")
    parser.add_argument("--no-persist-images", dest="persist_images",
                        action="store_false",
                        help="Record assets without writing image files")
    parser.add_argument("--prompt-only", action="store_true",
                        help="Print prompts without generating images")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable debug logging")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    asset_types = _parse_asset_types(args.asset_types)

    seeds = discover_characters(args.universe)
    if args.characters:
        wanted = {c.strip().lower() for c in args.characters.split(",") if c.strip()}
        seeds = [s for s in seeds if s.name.lower() in wanted]
    if args.limit:
        seeds = seeds[: args.limit]
    if not seeds:
        raise SystemExit("No characters matched the given filters.")

    tasks = list(_tasks(seeds, asset_types))
    print("=" * 70)
    print(f"  PHASE 1 LIBRARY — {len(seeds)} characters × {len(asset_types)} asset types")
    print(f"  asset-types: {', '.join(asset_types)}")
    print(f"  tasks: {len(tasks)} (character × variant)")
    print(f"  backend: {args.backend}  db: {args.db}")
    print("=" * 70)

    if args.prompt_only:
        for seed, key, asset_type, variant in tasks:
            positive, negative = build_prompt(seed, "character", asset_type, variant)
            print(f"\n--- {seed.name} [{key}] {variant} ---")
            print(f"POSITIVE: {positive}")
            print(f"NEGATIVE: {negative}")
        return 0

    char_repo = SQLiteCharacterRepository(db_path=args.db)
    asset_repo = SQLiteAssetRepository(db_path=args.db)
    backend = resolve_backend(args.backend, comfyui_url=args.comfyui_url,
                              provider=args.provider)
    scorer = IdentityScorer(light=args.fast_scoring)
    runner = BatchRunner(asset_repo=asset_repo, char_repo=char_repo,
                         backend=backend, scorer=scorer,
                         persist_images=args.persist_images,
                         universe_dir=args.universe, world_dir=args.world,
                         assets_dir=args.assets)

    batch_id = f"phase1_{int(time.time())}"
    overall = {"tasks": 0, "generated": 0, "shortlisted": 0, "failed": 0}

    # Group tasks by (asset_type, variant) so one run_seeds call covers every
    # selected character for that variant.
    by_variant: dict[tuple[str, str], list] = {}
    for seed, key, asset_type, variant in tasks:
        by_variant.setdefault((asset_type, variant), []).append((seed, key))

    print(f"\nRunning {len(by_variant)} variant groups…")
    for (asset_type, variant), group in by_variant.items():
        group_seeds = [seed for seed, _key in group]
        print(f"\n▶ {asset_type} / {variant}  ({len(group_seeds)} characters)")
        try:
            result = await runner.run_seeds(
                group_seeds,
                "character",
                count=args.count,
                shortlist=args.shortlist,
                jobs=args.jobs,
                asset_type=asset_type,
                variant=variant,
                batch_id=batch_id,
            )
        except Exception as exc:
            logger.exception("Group %s/%s failed: %s", asset_type, variant, exc)
            overall["failed"] += 1
            continue
        overall["tasks"] += result["items_attempted"]
        overall["generated"] += result["total_generated"]
        overall["shortlisted"] += result["total_shortlisted"]
        overall["failed"] += result["items_failed"]
        for fail in result["failures"]:
            print(f"    ✗ {fail.get('name')}: {fail.get('error')}")

    print("\n" + "=" * 70)
    print("  SUMMARY")
    print(f"  Batch:       {batch_id}")
    print(f"  Characters:  {len(seeds)}")
    print(f"  Tasks:       {overall['tasks']} ok, {overall['failed']} failed")
    print(f"  Generated:   {overall['generated']}")
    print(f"  Shortlisted: {overall['shortlisted']}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
