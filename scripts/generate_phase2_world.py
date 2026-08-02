#!/usr/bin/env python3
"""generate_phase2_world.py — Generate the full Phase 2 world library.

Builds the reusable world asset library from PHASE2.md / World/ bibles:

  * exteriors   — front reference for every ENV_* location (residential
                  homes get the full Home Library view set)
  * interiors   — interior reference sets (varied rooms per location)
  * seasons     — spring / summer / autumn / winter for every location
  * time        — morning / noon / golden hour / night for every location
  * weather     — sunny / cloudy / rain / snow for every location
  * camera      — camera-angle reference library (one hero location per zone
                  across all standard angles)
  * vehicles    — every VEH_* vehicle (front + side)
  * backgrounds — every BG_* background layer (sky / landscape / texture)

Every image goes through the standard pipeline (prompt → generate → score →
diversity filter → shortlist) and is persisted into the SQLite repository so
the Review UI and the export tooling can approve/lock it.

Works with any backend (mock / comfyui / cloud).  The mock backend is the
offline default and produces deterministic placeholder images.

Usage:
    python scripts/generate_phase2_world.py --backend mock --count 2
    python scripts/generate_phase2_world.py --asset-types seasons weather --prompt-only
    python scripts/generate_phase2_world.py --zone Residential --asset-types exteriors
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
from src.universe.catalog import (
    discover_backgrounds,
    discover_vehicles,
    discover_world_environments,
)

logger = logging.getLogger(__name__)

# Home Library views (PHASE2.md) — applied to Residential locations.
HOME_VIEWS: list[str] = ["front", "back", "garage", "garden", "mailbox", "driveway", "top"]
# Standard exterior reference for every other location.
STANDARD_VIEW: str = "front"

# Seasonal / time / weather variants (PHASE2.md lists the full catalog;
# the script defaults to the four core values for each dimension).
SEASONS: list[str] = ["spring", "summer", "autumn", "winter"]
TIMES: list[str] = ["morning", "noon", "golden_hour", "night"]
WEATHERS: list[str] = ["sunny", "cloudy", "rain", "snow"]

# Camera-angle reference library (one hero location per zone).
CAMERA_ANGLES: list[str] = [
    "wide", "ultra_wide", "medium", "close", "extreme_close",
    "overhead", "birds_eye", "ground_level", "low_angle", "high_angle",
]

# asset-type key → (kind, asset_type, display name)
ASSET_TYPES: dict[str, tuple[str, str, str]] = {
    "exteriors": ("environment", "exterior", "exterior reference"),
    "interiors": ("environment", "interior", "interior set"),
    "seasons": ("environment", "season", "seasonal variant"),
    "time": ("environment", "time_of_day", "time-of-day variant"),
    "weather": ("environment", "weather", "weather variant"),
    "camera": ("environment", "camera", "camera-angle reference"),
    "vehicles": ("vehicle", "vehicle", "vehicle reference"),
    "backgrounds": ("background", "background", "background layer"),
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


def _rooms() -> list[str]:
    """Named interior rooms used to vary the interior reference sets."""
    import src.prompt_builder.templates as _templates
    return sorted(_templates._INTERIOR_SETS)


def _interior_variant(index: int) -> str:
    rooms = _rooms()
    return rooms[index % len(rooms)]


def _hero_locations(envs: list) -> list:
    """One representative location per zone (first of each zone)."""
    hero: list = []
    seen_zones: set[str] = set()
    for env in envs:
        if env.zone not in seen_zones:
            seen_zones.add(env.zone)
            hero.append(env)
    return hero


def _bg_layer(seed) -> str:
    """Map a BG_* asset id prefix to its background layer name."""
    asset_id = getattr(seed, "asset_id", "")
    if asset_id.startswith("BG_Landscape"):
        return "landscape"
    if asset_id.startswith("BG_Texture"):
        return "texture"
    return "sky"


def _tasks(envs: list, vehs: list, bgs: list, asset_types: list[str]):
    """Yield (seed, kind, asset_type, variant) task tuples."""
    rooms = _rooms()
    hero = _hero_locations(envs)

    for key in asset_types:
        kind, asset_type, _label = ASSET_TYPES[key]
        if key == "exteriors":
            for i, env in enumerate(envs):
                if env.bio_data.get("zone_dir") == "Residential":
                    for view in HOME_VIEWS:
                        yield env, "environment", asset_type, view
                else:
                    yield env, "environment", asset_type, STANDARD_VIEW
        elif key == "interiors":
            for i, env in enumerate(envs):
                yield env, "environment", asset_type, rooms[i % len(rooms)]
        elif key == "seasons":
            for env in envs:
                for variant in SEASONS:
                    yield env, "environment", asset_type, variant
        elif key == "time":
            for env in envs:
                for variant in TIMES:
                    yield env, "environment", asset_type, variant
        elif key == "weather":
            for env in envs:
                for variant in WEATHERS:
                    yield env, "environment", asset_type, variant
        elif key == "camera":
            for env in hero:
                for variant in CAMERA_ANGLES:
                    yield env, "environment", asset_type, variant
        elif key == "vehicles":
            for veh in vehs:
                for variant in ("front", "side"):
                    yield veh, "vehicle", asset_type, variant
        elif key == "backgrounds":
            for bg in bgs:
                yield bg, "background", asset_type, _bg_layer(bg)


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--asset-types", default="all",
                        help="Comma list or 'all' (default): exteriors, interiors, "
                             "seasons, time, weather, camera, vehicles, backgrounds")
    parser.add_argument("--zone", default="",
                        help="Restrict to one zone dir name (e.g. Residential)")
    parser.add_argument("--backend", default="mock",
                        help="mock | comfyui | cloud (default: mock)")
    parser.add_argument("--provider", default="fal",
                        help="Cloud provider for --backend cloud: fal | replicate | bfl")
    parser.add_argument("--comfyui-url", default="http://localhost:8188",
                        help="ComfyUI server URL (default: http://localhost:8188)")
    parser.add_argument("--count", type=int, default=2,
                        help="Candidates to generate per (location, variant) (default: 2)")
    parser.add_argument("--shortlist", type=int, default=1,
                        help="Top candidates to shortlist per (location, variant) (default: 1)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Max environments to process (default: all)")
    parser.add_argument("--jobs", type=int, default=8,
                        help="Concurrent generation jobs (default: 8)")
    parser.add_argument("--fast-scoring", action="store_true",
                        help="Skip torch-backed scoring plugins (DINOv2/CLIP); "
                             "much faster, fine for mock placeholders")
    parser.add_argument("--db", default="catalog.db",
                        help="SQLite database path (default: catalog.db)")
    parser.add_argument("--world", default="World",
                        help="Path to the World/ directory")
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

    envs = discover_world_environments(args.world)
    vehs = discover_vehicles(args.world)
    bgs = discover_backgrounds(args.world)
    if args.zone:
        envs = [e for e in envs if e.bio_data.get("zone_dir", "").lower()
                == args.zone.lower()]
    if args.limit:
        envs = envs[: args.limit]
    if not envs and not vehs and not bgs:
        raise SystemExit("No world locations matched the given filters.")

    tasks = list(_tasks(envs, vehs, bgs, asset_types))
    print("=" * 70)
    print(f"  PHASE 2 WORLD LIBRARY")
    print(f"  locations: {len(envs)}  vehicles: {len(vehs)}  backgrounds: {len(bgs)}")
    print(f"  asset-types: {', '.join(asset_types)}")
    print(f"  tasks: {len(tasks)} (location × variant)")
    print(f"  backend: {args.backend}  db: {args.db}")
    print("=" * 70)

    if args.prompt_only:
        for seed, kind, asset_type, variant in tasks:
            positive, negative = build_prompt(seed, kind, asset_type, variant)
            label = getattr(seed, "identifier", None) or getattr(seed, "asset_id", seed.name)
            print(f"\n--- {label} [{kind}/{asset_type}] {variant} ---")
            print(f"POSITIVE: {positive}")
            print(f"NEGATIVE: {negative}")
        return 0

    char_repo = SQLiteCharacterRepository(db_path=args.db)
    asset_repo = SQLiteAssetRepository(db_path=args.db)
    backend = resolve_backend(args.backend, comfyui_url=args.comfyui_url,
                              provider=args.provider)
    scorer = IdentityScorer(light=args.fast_scoring)
    runner = BatchRunner(asset_repo=asset_repo, char_repo=char_repo,
                         backend=backend, scorer=scorer)

    batch_id = f"phase2_{int(time.time())}"
    overall = {"tasks": 0, "generated": 0, "shortlisted": 0, "failed": 0}

    by_variant: dict[tuple[str, str, str], list] = {}
    for seed, kind, asset_type, variant in tasks:
        by_variant.setdefault((kind, asset_type, variant), []).append(seed)

    print(f"\nRunning {len(by_variant)} variant groups…")
    for (kind, asset_type, variant), group_seeds in by_variant.items():
        label = getattr(group_seeds[0], "identifier", None) or ""
        print(f"\n▶ {kind}/{asset_type} / {variant}  ({len(group_seeds)} locations)")
        try:
            result = await runner.run_seeds(
                group_seeds,
                kind,
                count=args.count,
                shortlist=args.shortlist,
                jobs=args.jobs,
                asset_type=asset_type,
                variant=variant,
                batch_id=batch_id,
            )
        except Exception as exc:
            logger.exception("Group %s/%s/%s failed: %s",
                             kind, asset_type, variant, exc)
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
    print(f"  Locations:   {len(envs)}  Vehicles: {len(vehs)}  Backgrounds: {len(bgs)}")
    print(f"  Tasks:       {overall['tasks']} ok, {overall['failed']} failed")
    print(f"  Generated:   {overall['generated']}")
    print(f"  Shortlisted: {overall['shortlisted']}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
