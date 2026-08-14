#!/usr/bin/env python3
"""generate_phase3_assets.py — Generate the full Phase 3 asset library.

Builds the reusable production asset library from PHASE3.md / Assets/ bibles:

  * references — canonical front product shot for every prop (1,523 props:
                  toys, food, books, furniture, nature, holiday, medical,
                  musical, school, playground, sports, occupations, materials
                  and textures)
  * views      — turnaround views (side / top / back) for every prop
  * materials  — alternate material finish per prop
  * colors     — alternate color palette per prop
  * lighting   — studio lighting study per prop

Every image goes through the standard pipeline (prompt → generate → score →
diversity filter → shortlist) and is persisted into the SQLite repository so
the Review UI and the export tooling can approve/lock it.

Works with any backend (mock / comfyui / cloud).  The mock backend is the
offline default and produces deterministic placeholder images.

Usage:
    python scripts/generate_phase3_assets.py --backend mock --count 2
    python scripts/generate_phase3_assets.py --asset-types materials colors --prompt-only
    python scripts/generate_phase3_assets.py --category Toys --asset-types views
    python scripts/generate_phase3_assets.py --materials all --colors all --category Food
"""

import argparse
import asyncio
import hashlib
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.asset_repository.sqlite_repo import SQLiteAssetRepository, SQLiteCharacterRepository
from src.identity_engine.scorer import IdentityScorer
from src.universe.batch_generator import BatchRunner, build_prompt, resolve_backend
from src.universe.catalog import discover_props

logger = logging.getLogger(__name__)

# Turnaround views (front is the reference library's own view).
VIEWS: list[str] = ["side", "top", "back"]
# Lighting studies (PHASE3.md pipeline step: style correction + approval).
LIGHTING_STUDIES: list[str] = ["studio", "natural"]

# asset-type key → (kind, asset_type, display name)
ASSET_TYPES: dict[str, tuple[str, str, str]] = {
    "references": ("prop", "reference", "canonical reference"),
    "views": ("prop", "view", "turnaround view"),
    "materials": ("prop", "material", "material variant"),
    "colors": ("prop", "color", "color variant"),
    "lighting": ("prop", "lighting", "lighting study"),
}

# alias / singular forms accepted by --asset-types (Phase 1 parity).
_ASSET_TYPE_ALIASES: dict[str, str] = {
    "reference": "references",
    "view": "views",
    "material": "materials",
    "color": "colors",
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
    """Expand a --materials/--colors option value.

    Empty keeps the single deterministic variant per prop; ``all`` / ``*``
    generates the full PHASE3.md catalog for that dimension; a comma list is
    validated against the catalog.
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


def _pick_material(seed) -> str:
    """Pick one deterministic alternate material per prop."""
    import src.prompt_builder.templates as _templates
    materials = sorted(_templates._PROP_MATERIALS)
    digest = hashlib.sha1(getattr(seed, "asset_id", seed.name).encode()).digest()[0]
    return materials[digest % len(materials)]


def _pick_color(seed) -> str:
    """Pick one deterministic alternate color palette per prop."""
    import src.prompt_builder.templates as _templates
    colors = sorted(_templates._PROP_COLOR_VARIANTS)
    digest = hashlib.sha1(
        getattr(seed, "asset_id", seed.name).encode()
    ).digest()[1]
    return colors[digest % len(colors)]


def _material_catalog() -> list[str]:
    """The full PHASE3.md material library (keys of ``_PROP_MATERIALS``)."""
    import src.prompt_builder.templates as _templates
    return sorted(_templates._PROP_MATERIALS)


def _color_catalog() -> list[str]:
    """The full prop color palette (keys of ``_PROP_COLOR_VARIANTS``)."""
    import src.prompt_builder.templates as _templates
    return sorted(_templates._PROP_COLOR_VARIANTS)


def _tasks(props: list, asset_types: list[str],
           materials: list[str] | None = None,
           colors: list[str] | None = None):
    """Yield (seed, kind, asset_type, variant) task tuples.

    Empty ``materials``/``colors`` picks one deterministic variant per prop;
    a list (from ``--materials all`` etc.) generates every catalog variant.
    """
    for key in asset_types:
        kind, asset_type, _label = ASSET_TYPES[key]
        if key == "references":
            for prop in props:
                yield prop, "prop", asset_type, "front"
        elif key == "views":
            for prop in props:
                for variant in VIEWS:
                    yield prop, "prop", asset_type, variant
        elif key == "materials":
            for prop in props:
                for variant in (materials if materials else [_pick_material(prop)]):
                    yield prop, "prop", asset_type, variant
        elif key == "colors":
            for prop in props:
                for variant in (colors if colors else [_pick_color(prop)]):
                    yield prop, "prop", asset_type, variant
        elif key == "lighting":
            for prop in props:
                for variant in LIGHTING_STUDIES:
                    yield prop, "prop", asset_type, variant


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
                        help="Comma list or 'all' (default): references, views, "
                             "materials, colors, lighting")
    parser.add_argument("--materials", default="",
                        help="Comma list or 'all' for the material catalog "
                             "(default: one deterministic material per prop)")
    parser.add_argument("--colors", default="",
                        help="Comma list or 'all' for the color palette "
                             "(default: one deterministic color per prop)")
    parser.add_argument("--category", default="",
                        help="Restrict to one category dir name "
                             "(e.g. Toys, Food, Animals, Books)")
    parser.add_argument("--props", default="",
                        help="Restrict to specific prop names or asset ids "
                             "(comma list, case-insensitive)")
    parser.add_argument("--backend", default="mock",
                        help="mock | comfyui | cloud (default: mock)")
    parser.add_argument("--provider", default="fal",
                        help="Cloud provider for --backend cloud: fal | replicate | bfl")
    parser.add_argument("--comfyui-url", default="http://localhost:8188",
                        help="ComfyUI server URL (default: http://localhost:8188)")
    parser.add_argument("--count", type=int, default=2,
                        help="Candidates to generate per (prop, variant) (default: 2)")
    parser.add_argument("--shortlist", type=int, default=1,
                        help="Top candidates to shortlist per (prop, variant) (default: 1)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Max props to process (default: all)")
    parser.add_argument("--jobs", type=int, default=8,
                        help="Concurrent generation jobs (default: 8)")
    parser.add_argument("--fast-scoring", action="store_true",
                        help="Skip torch-backed scoring plugins (DINOv2/CLIP); "
                             "much faster, fine for mock placeholders")
    parser.add_argument("--db", default="catalog.db",
                        help="SQLite database path (default: catalog.db)")
    parser.add_argument("--assets", default="Assets",
                        help="Path to the Assets/ directory")
    parser.add_argument("--universe", default="Universe",
                        help="Path to the Universe/ directory (default: Universe)")
    parser.add_argument("--world", default="World",
                        help="Path to the World/ directory (prop indexes)")
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
    materials = _parse_variants(args.materials, [], _material_catalog(), "material")
    colors = _parse_variants(args.colors, [], _color_catalog(), "color")

    props = discover_props(args.world, args.assets)
    if args.category:
        wanted = args.category.lower()
        props = [p for p in props if p.category_dir.lower() == wanted]
    if args.props:
        wanted = {p.strip().lower() for p in args.props.split(",") if p.strip()}
        matched = [
            p for p in props
            if p.name.lower() in wanted or p.asset_id.lower() in wanted
        ]
        missing = sorted(wanted - {p.name.lower() for p in matched}
                         - {p.asset_id.lower() for p in matched})
        if missing:
            names = ", ".join(repr(p.name) for p in props)
            raise SystemExit(f"Unknown prop(s): {missing}. Available: {names}")
        props = matched
    if args.limit:
        props = props[: args.limit]
    if not props:
        raise SystemExit("No props matched the given filters.")

    tasks = list(_tasks(props, asset_types, materials=materials, colors=colors))
    print("=" * 70)
    print("  PHASE 3 ASSET LIBRARY")
    print(f"  props: {len(props)}  categories: {len({p.category_dir for p in props})}")
    print(f"  asset-types: {', '.join(asset_types)}")
    if materials:
        print(f"  materials: {len(materials)}  colors: {len(colors)}")
    print(f"  tasks: {len(tasks)} (prop × variant)")
    print(f"  backend: {args.backend}  db: {args.db}")
    print("=" * 70)

    if args.prompt_only:
        for seed, kind, asset_type, variant in tasks:
            positive, negative = build_prompt(seed, kind, asset_type, variant)
            label = getattr(seed, "asset_id", seed.name)
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
    # image (same pattern as the Phase-1/2 notebooks).
    async def _on_asset(info: dict) -> None:
        label = info.get("file_path") or info.get("asset_id") or "asset"
        _checkpoint_sync(args, f"image {label} (per-image checkpoint)")

    runner = BatchRunner(asset_repo=asset_repo, char_repo=char_repo,
                         backend=backend, scorer=scorer,
                         persist_images=args.persist_images,
                         universe_dir=args.universe, world_dir=args.world,
                         assets_dir=args.assets,
                         on_asset=_on_asset if args.sync_every_image else None)

    batch_id = f"phase3_{int(time.time())}"
    overall = {"tasks": 0, "generated": 0, "shortlisted": 0, "failed": 0}

    by_variant: dict[tuple[str, str, str], list] = {}
    for seed, kind, asset_type, variant in tasks:
        by_variant.setdefault((kind, asset_type, variant), []).append(seed)

    print(f"\nRunning {len(by_variant)} variant groups…")
    group_index = 0
    for (kind, asset_type, variant), group_seeds in by_variant.items():
        group_index += 1
        label = getattr(group_seeds[0], "asset_id", "") or ""
        print(f"\n▶ {kind}/{asset_type} / {variant}  ({len(group_seeds)} props)")
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
                f"(asset library)",
            )

    if args.sync_every > 0:
        _checkpoint_sync(args, f"final sync after {group_index} groups (asset library)")

    print("\n" + "=" * 70)
    print("  SUMMARY")
    print(f"  Batch:       {batch_id}")
    print(f"  Props:       {len(props)}")
    print(f"  Tasks:       {overall['tasks']} ok, {overall['failed']} failed")
    print(f"  Generated:   {overall['generated']}")
    print(f"  Shortlisted: {overall['shortlisted']}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
