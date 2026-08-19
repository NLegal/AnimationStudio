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
    python scripts/generate_phase2_world.py --seasons all --times all --weathers all
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

# Home Library views (PHASE2.md §Home Library) — applied to Residential
# locations.  Front/Back/Garage/Garden/Mailbox/Driveway/Trees/Fence come
# straight from the spec; "top" satisfies the §Environment Standards Top View.
HOME_VIEWS: list[str] = [
    "front", "back", "garage", "garden", "mailbox", "driveway",
    "trees", "fence", "top",
]
# Standard exterior reference for every other location.
STANDARD_VIEW: str = "front"

# Full PHASE2.md variant catalogs (supersets used with --seasons/--times/
# --weathers/--cameras all).
SEASONS_ALL: list[str] = [
    "spring", "summer", "autumn", "winter",
    "holiday", "halloween", "christmas", "new_year", "easter", "birthday",
]
TIMES_ALL: list[str] = [
    "morning", "sunrise", "noon", "afternoon", "golden_hour",
    "sunset", "evening", "night", "moonlight",
]
WEATHERS_ALL: list[str] = [
    "sunny", "cloudy", "rain", "snow",
    "fog", "wind", "rainbow", "light_storm",
]
CAMERA_ANGLES_ALL: list[str] = [
    "wide", "ultra_wide", "medium", "close", "extreme_close",
    "overhead", "birds_eye", "ground_level", "tracking", "walking_follow",
    "front", "side", "rear", "low_angle", "high_angle",
]

# Seasonal / time / weather variants — the four core values for each
# dimension by default.  Pass --seasons/--times/--weathers/--cameras 'all'
# (or a comma list) to generate the complete PHASE2.md catalog.
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


# alias / singular forms accepted by --asset-types (Phase 1 parity).
_ASSET_TYPE_ALIASES: dict[str, str] = {
    "exterior": "exteriors",
    "interior": "interiors",
    "season": "seasons",
    "times": "time",
    "camera": "camera",
    "cameras": "camera",
    "vehicle": "vehicles",
    "background": "backgrounds",
}


def _parse_asset_types(value: str) -> list[str]:
    """Expand the --asset-types option into individual library keys."""
    value = (value or "all").strip().lower()
    keys = list(ASSET_TYPES)
    if value in ("all", "*"):
        return keys
    wanted: list[str] = []
    for part in value.split(","):
        part = part.strip().lower()
        part = _ASSET_TYPE_ALIASES.get(part, part)
        if not part or part in wanted:
            continue
        if part not in keys:
            raise SystemExit(
                f"Unknown asset type '{part}'. Use one of: {', '.join(keys)}, all"
            )
        wanted.append(part)
    if not wanted:
        raise SystemExit("No asset types selected. Use --asset-types 'all' or a comma list.")
    return wanted


def _parse_variants(value: str, default: list[str], catalog: list[str],
                    label: str) -> list[str]:
    """Expand a --seasons/--times/--weathers/--cameras option value.

    Accepts ``all`` / ``*`` (the full PHASE2.md catalog), a comma list
    validated against the catalog, or an empty value (keeps the core default
    list for that dimension).
    """
    value = (value or "").strip().lower()
    if value in ("", "all", "*"):
        return list(catalog if value else default)
    wanted: list[str] = []
    for part in value.split(","):
        part = part.strip()
        if not part or part in wanted:
            continue
        if part not in catalog:
            raise SystemExit(
                f"Unknown {label} '{part}'. Use one of: {', '.join(catalog)}, all"
            )
        wanted.append(part)
    if not wanted:
        raise SystemExit(f"No {label} selected.")
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


def _tasks(envs: list, vehs: list, bgs: list, asset_types: list[str],
           seasons: list[str] | None = None,
           times: list[str] | None = None,
           weathers: list[str] | None = None,
           cameras: list[str] | None = None):
    """Yield (seed, kind, asset_type, variant) task tuples."""
    rooms = _rooms()
    hero = _hero_locations(envs)
    seasons = seasons or SEASONS
    times = times or TIMES
    weathers = weathers or WEATHERS
    cameras = cameras or CAMERA_ANGLES

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
                for variant in seasons:
                    yield env, "environment", asset_type, variant
        elif key == "time":
            for env in envs:
                for variant in times:
                    yield env, "environment", asset_type, variant
        elif key == "weather":
            for env in envs:
                for variant in weathers:
                    yield env, "environment", asset_type, variant
        elif key == "camera":
            for env in hero:
                for variant in cameras:
                    yield env, "environment", asset_type, variant
        elif key == "vehicles":
            for veh in vehs:
                for variant in ("front", "side"):
                    yield veh, "vehicle", asset_type, variant
        elif key == "backgrounds":
            for bg in bgs:
                yield bg, "background", asset_type, _bg_layer(bg)


def _checkpoint_sync(args, message: str) -> None:
    """Push generated images + the DB to git; never block generation on it."""
    try:
        from colab.git_sync import auto_sync
    except Exception as exc:  # pragma: no cover - environment dependent
        logger.warning("Periodic sync unavailable (generation continues): %s", exc)
        return
    repo = args.sync_repo or str(Path(__file__).resolve().parents[1])
    auto_sync(repo=repo, branch=args.sync_branch, db_path=args.db,
              token=args.sync_token, remote_url=args.sync_remote_url,
              git_name=args.sync_git_name, git_email=args.sync_git_email,
              message=message)


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--asset-types", default="all",
                        help="Comma list or 'all' (default): exteriors, interiors, "
                             "seasons, time, weather, camera, vehicles, backgrounds")
    parser.add_argument("--seasons", default="",
                        help="Comma list or 'all' for the seasonal catalog "
                             "(default: spring,summer,autumn,winter)")
    parser.add_argument("--times", default="",
                        help="Comma list or 'all' for the time-of-day catalog "
                             "(default: morning,noon,golden_hour,night)")
    parser.add_argument("--weathers", default="",
                        help="Comma list or 'all' for the weather catalog "
                             "(default: sunny,cloudy,rain,snow)")
    parser.add_argument("--cameras", default="",
                        help="Comma list or 'all' for the camera-angle catalog "
                             "(default: the 10 standard angles)")
    parser.add_argument("--zone", default="",
                        help="Restrict to one zone dir name (e.g. Residential)")
    parser.add_argument("--locations", default="",
                        help="Restrict to specific location identifiers or names "
                             "(comma list, case-insensitive)")
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
    parser.add_argument("--universe", default="Universe",
                        help="Path to the Universe/ directory (default: Universe)")
    parser.add_argument("--assets", default="Assets",
                        help="Path to the Assets/ directory (default: Assets)")
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
    parser.add_argument("--sync-every", type=int, default=0,
                        help="After every N variant groups, push generated "
                             "images + the DB to git (default: 0 = only a "
                             "final sync at the end, driven by the notebook)")
    parser.add_argument("--sync-every-image", action="store_true",
                        help="Push each individual image + the DB to git the "
                             "moment it is generated, so a Colab termination "
                             "loses at most the single in-flight image")
    parser.add_argument("--sync-repo", default="",
                        help="Local git repo path for syncing (default: repo root)")
    parser.add_argument("--sync-branch", default="",
                        help="Git branch to push synced output to")
    parser.add_argument("--sync-token", default="",
                        help="GitHub PAT for the sync push")
    parser.add_argument("--sync-remote-url", default="",
                        help="Remote URL (with token embedded) for the sync push")
    parser.add_argument("--sync-git-name", default="Colab Studio",
                        help="Git author name for sync commits")
    parser.add_argument("--sync-git-email", default="colab@animationstudio.local",
                        help="Git author email for sync commits")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    asset_types = _parse_asset_types(args.asset_types)
    seasons = _parse_variants(args.seasons, SEASONS, SEASONS_ALL, "season")
    times = _parse_variants(args.times, TIMES, TIMES_ALL, "time of day")
    weathers = _parse_variants(args.weathers, WEATHERS, WEATHERS_ALL, "weather")
    cameras = _parse_variants(args.cameras, CAMERA_ANGLES, CAMERA_ANGLES_ALL,
                              "camera angle")

    envs = discover_world_environments(args.world)
    vehs = discover_vehicles(args.world)
    bgs = discover_backgrounds(args.world)
    if args.zone:
        envs = [e for e in envs if e.bio_data.get("zone_dir", "").lower()
                == args.zone.lower()]
    if args.locations:
        wanted = {p.strip().lower() for p in args.locations.split(",") if p.strip()}
        matched = [
            e for e in envs
            if e.name.lower() in wanted
            or str(getattr(e, "identifier", "")).lower() in wanted
            or str(getattr(e, "asset_id", "")).lower() in wanted
        ]
        missing = sorted(wanted - {e.name.lower() for e in matched}
                         - {str(getattr(e, "identifier", "")).lower() for e in matched}
                         - {str(getattr(e, "asset_id", "")).lower() for e in matched})
        if missing:
            names = ", ".join(repr(e.name) for e in envs)
            raise SystemExit(f"Unknown location(s): {missing}. Available: {names}")
        envs = matched
    if args.limit:
        envs = envs[: args.limit]
    if not envs and not vehs and not bgs:
        raise SystemExit("No world locations matched the given filters.")

    tasks = list(_tasks(envs, vehs, bgs, asset_types,
                        seasons=seasons, times=times,
                        weathers=weathers, cameras=cameras))
    print("=" * 70)
    print(f"  PHASE 2 WORLD LIBRARY")
    print(f"  locations: {len(envs)}  vehicles: {len(vehs)}  backgrounds: {len(bgs)}")
    print(f"  asset-types: {', '.join(asset_types)}")
    print(f"  variants -> seasons: {len(seasons)}  time: {len(times)}"
          f"  weather: {len(weathers)}  camera: {len(cameras)}")
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

    # Per-image git checkpoint hook: push each image + the DB the moment it is
    # generated, so a Colab termination loses at most the single in-flight
    # image (same pattern as the Phase-1 notebook).
    async def _on_asset(info: dict) -> None:
        label = info.get("file_path") or info.get("asset_id") or "asset"
        _checkpoint_sync(args, f"image {label} (per-image checkpoint)")

    runner = BatchRunner(asset_repo=asset_repo, char_repo=char_repo,
                         backend=backend, scorer=scorer,
                         persist_images=args.persist_images,
                         universe_dir=args.universe, world_dir=args.world,
                         assets_dir=args.assets,
                         on_asset=_on_asset if args.sync_every_image else None)

    batch_id = f"phase2_{int(time.time())}"
    overall = {"tasks": 0, "generated": 0, "shortlisted": 0, "failed": 0}

    by_variant: dict[tuple[str, str, str], list] = {}
    for seed, kind, asset_type, variant in tasks:
        by_variant.setdefault((kind, asset_type, variant), []).append(seed)

    print(f"\nRunning {len(by_variant)} variant groups…")
    group_index = 0
    for (kind, asset_type, variant), group_seeds in by_variant.items():
        group_index += 1
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
                skip_scored=True,
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
        if args.sync_every > 0 and group_index % args.sync_every == 0:
            _checkpoint_sync(
                args,
                f"checkpoint {group_index}/{len(by_variant)} groups "
                f"(world library)",
            )

    if args.sync_every > 0:
        _checkpoint_sync(args, f"final sync after {group_index} groups (world library)")

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
