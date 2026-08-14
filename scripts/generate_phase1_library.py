#!/usr/bin/env python3
"""generate_phase1_library.py — Generate the full Phase 1 character library.

Produces the complete per-character asset library from PHASE1.md:

  * reference sheets (front view)
  * expressions (all known expressions)
  * poses (all known poses)
  * outfits (each wardrobe variant from the character's bio)
  * turnarounds (front / 45 / left / right / back / top / bottom)
  * lighting studies (morning, golden hour, night, …)
  * accessories (each accessory declared in the character's bio)

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
    "accessories": ("accessory", "accessory"),
}

# Accept the plural CLI forms (expressions, references, ...) that match the
# on-disk library directories.  Maps onto the canonical library keys.
_ASSET_TYPE_ALIASES: dict[str, str] = {
    "references": "reference",
    "expressions": "expressions",
    "expression": "expressions",
    "poses": "poses",
    "pose": "poses",
    "outfits": "outfits",
    "outfit": "outfits",
    "turnarounds": "turnarounds",
    "turnaround": "turnarounds",
    "lighting": "lighting",
    "lightings": "lighting",
    "accessories": "accessories",
    "accessory": "accessories",
}


def _parse_asset_types(value: str) -> list[str]:
    """Expand the --asset-types option into individual library keys."""
    value = (value or "all").strip().lower()
    keys = list(ASSET_TYPES)
    if value in ("all", "*", ""):
        return keys
    wanted: list[str] = []
    for part in value.split(","):
        w = part.strip().lower()
        if not w:
            continue
        w = _ASSET_TYPE_ALIASES.get(w, w)
        if w not in keys:
            raise SystemExit(
                f"Unknown asset type '{part.strip()}'. Use one of: "
                f"{', '.join(keys)}, all"
            )
        if w not in wanted:
            wanted.append(w)
    return wanted


def _outfits_for(seed) -> list[str]:
    """Wardrobe variant names for a character (from the bio's wardrobe table)."""
    wardrobe = seed.bio_data.get("wardrobe", {})
    return [name for name in wardrobe if name]


def _accessories_for(seed) -> list[str]:
    """Per-character accessory names (from the bio's Appearance field).

    PHASE1.md puts an ``accessories/`` directory under every character and
    lists an Accessory Library as a Phase-1 deliverable; each bio already
    declares the character's own accessories (e.g. Lily Bunny's "Blue bow on
    left ear (signature), small backpack").  We generate one study per
    accessory so the character library covers that deliverable too.
    """
    appearance = seed.bio_data.get("appearance_fields", {}) or {}
    raw = appearance.get("accessories", "")
    parts = [p.strip(" .") for p in raw.split(",") if p.strip()]
    # De-duplicate, preserving order.
    return list(dict.fromkeys(p for p in parts if p))


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
    if key == "accessories":
        return _accessories_for(seed) or ["default accessory"]
    return []


def _tasks(seeds: list, asset_types: list[str]):
    """Yield (seed, asset_type_key, asset_type, variant) task tuples."""
    for seed in seeds:
        for key in asset_types:
            asset_type, _label = ASSET_TYPES[key]
            for variant in _variants(key, seed):
                yield seed, key, asset_type, variant


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
                        help="Comma list or 'all' (default): reference, expressions, "
                             "poses, outfits, turnarounds, lighting, accessories")
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
                        help="Comma list of character names to include, or "
                             "'all' (default: all)")
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
    parser.add_argument("--sync-every", type=int, default=0,
                        help="After every N variant groups, push generated "
                             "images + the DB to git (default: 0 = only a "
                             "final sync at the end, driven by the notebook)")
    parser.add_argument("--sync-every-image", action="store_true",
                        help="Push each individual image + the DB to git the "
                             "moment it is generated, so a Colab termination "
                             "never loses more than the in-flight image")
    parser.add_argument("--sync-repo", default="",
                        help="Git checkout to push from (default: repo root)")
    parser.add_argument("--sync-branch", default="main",
                        help="Git branch to push to (default: main)")
    parser.add_argument("--sync-token", default="",
                        help="GitHub PAT for the push")
    parser.add_argument("--sync-remote-url", default="",
                        help="GitHub clone URL; origin is repointed to it")
    parser.add_argument("--sync-git-name", default="Colab Studio",
                        help="Git identity name for checkpoint commits")
    parser.add_argument("--sync-git-email", default="colab@animationstudio.local",
                        help="Git identity email for checkpoint commits")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    asset_types = _parse_asset_types(args.asset_types)

    seeds = discover_characters(args.universe)
    wanted = args.characters.strip()
    if wanted and wanted.lower() not in ("all", "*"):
        wanted = {c.strip().lower() for c in wanted.split(",") if c.strip()}
        matched = [s for s in seeds if s.name.lower() in wanted]
        missing = sorted(wanted - {s.name.lower() for s in matched})
        if missing:
            known = ", ".join(f"'{s.name}'" for s in seeds)
            raise SystemExit(
                f"Unknown character name(s): {', '.join(missing)}.\n"
                f"Discoverable characters ({len(seeds)}): {known}."
            )
        seeds = matched
    if args.limit:
        seeds = seeds[: args.limit]
    if not seeds:
        raise SystemExit("No characters matched the given filters.")

    tasks = list(_tasks(seeds, asset_types))
    print("=" * 70)
    print(f"  PHASE 1 LIBRARY — {len(seeds)} characters × {len(asset_types)} asset types")
    if len(seeds) <= 8:
        print("  characters: " + ", ".join(s.name for s in seeds))
    else:
        print(f"  characters: {len(seeds)} total (first: "
              + ", ".join(s.name for s in seeds[:3]) + ", …)")
    print(f"  asset-types: {', '.join(asset_types)}")
    print(f"  tasks: {len(tasks)} (character × variant)")
    print(f"  backend: {args.backend}  db: {args.db}")
    if args.sync_every_image:
        print("  git sync: PER IMAGE (each image is pushed before the next starts)")
    elif args.sync_every > 0:
        print(f"  git sync: every {args.sync_every} variant group(s)")
    else:
        print("  git sync: off (notebook drives final push)")
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

    # Per-image checkpoint sync: push the moment each image is generated, so
    # a Colab termination loses at most the single in-flight image.  The hook
    # runs inside the generation loop (blocking until the push completes —
    # exactly the "generate one, upload, generate next" pattern requested).
    async def _on_asset(info: dict) -> None:
        label = info.get("file_path") or info.get("asset_id") or "asset"
        _checkpoint_sync(args, f"image {label} (per-image checkpoint)")

    runner = BatchRunner(asset_repo=asset_repo, char_repo=char_repo,
                         backend=backend, scorer=scorer,
                         persist_images=args.persist_images,
                         universe_dir=args.universe, world_dir=args.world,
                         assets_dir=args.assets,
                         on_asset=_on_asset if args.sync_every_image else None)

    batch_id = f"phase1_{int(time.time())}"
    overall = {"tasks": 0, "generated": 0, "shortlisted": 0, "failed": 0}

    # Group tasks by (asset_type, variant) so one run_seeds call covers every
    # selected character for that variant.
    by_variant: dict[tuple[str, str], list] = {}
    for seed, key, asset_type, variant in tasks:
        by_variant.setdefault((asset_type, variant), []).append((seed, key))

    print(f"\nRunning {len(by_variant)} variant groups…")
    for group_index, ((asset_type, variant), group) in enumerate(
            by_variant.items(), start=1):
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
                skip_scored=True,
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

        # Checkpoint: ship everything generated so far to git after every N
        # groups, so a Colab termination loses at most the in-flight group.
        # Re-running this script skips the synced groups (skip_scored=True).
        if args.sync_every > 0 and group_index % args.sync_every == 0:
            _checkpoint_sync(
                args,
                f"checkpoint {group_index}/{len(by_variant)} groups "
                f"({asset_type}/{variant})",
            )

    # Final flush so nothing waits on the notebook-side auto_sync.
    if args.sync_every > 0:
        _checkpoint_sync(args, "final checkpoint after full batch")

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
