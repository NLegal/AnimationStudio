#!/usr/bin/env python3
"""export_assets.py — Write generated assets from the DB to the file tree.

Phase 1 requires an *organized asset repository*: image files on disk under
``Universe/Characters/<Name>/references|expressions|poses|outfits|
turnarounds|lighting`` (plus ``World/`` zones and ``Assets/`` categories).

The pipeline stores assets in SQLite with metadata and may already persist
image bytes at generation time (``--persist-images``).  This script writes a
PNG for any asset whose file is missing, then records the
``file_path`` on the asset row.

The mock backend is reproducible offline (deterministic from prompt + seed).
With ``--backend comfyui`` (or ``cloud``) the image is re-generated on the
live backend, so a Colab/GPU run can persist real images into the file tree.

Usage:
    python scripts/export_assets.py --db catalog.db
    python scripts/export_assets.py --states shortlisted approved
    python scripts/export_assets.py --scope characters --asset-types expressions,poses
    python scripts/export_assets.py --backend comfyui --comfyui-url http://localhost:8188 --size 1024
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.asset_repository.asset_paths import asset_destination, repo_relative_path
from src.asset_repository.sqlite_repo import SQLiteAssetRepository, SQLiteCharacterRepository
from src.generation_engine.base import GenerationInput
from src.universe.batch_generator import resolve_backend


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", default="catalog.db",
                        help="SQLite database path (default: catalog.db)")
    parser.add_argument("--states", default="shortlisted,approved,production",
                        help="Comma list of asset states to export (default: shortlisted,approved,production)")
    parser.add_argument("--scope", default="characters",
                        help="characters | environments | vehicles | backgrounds | props | all (default: characters)")
    parser.add_argument("--asset-types", default="",
                        help="Optional comma list: reference,expression,pose,outfit,lighting,"
                             "accessory,exterior,interior,season,time_of_day,weather,camera,"
                             "vehicle,background,view,material,color")
    parser.add_argument("--universe", default="Universe", help="Universe/ directory")
    parser.add_argument("--world", default="World", help="World/ directory")
    parser.add_argument("--assets", default="Assets", help="Assets/ directory")
    parser.add_argument("--backend", default="mock",
                        help="mock | comfyui | cloud (default: mock)")
    parser.add_argument("--comfyui-url", default="http://localhost:8188",
                        help="ComfyUI server URL (default: http://localhost:8188)")
    parser.add_argument("--provider", default="fal",
                        help="Cloud provider for --backend cloud: fal | replicate | bfl")
    parser.add_argument("--size", type=int, default=512,
                        help="Image size for regenerated images (default: 512)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print destinations without writing files")
    args = parser.parse_args()

    states = {s.strip().lower() for s in args.states.split(",") if s.strip()}
    scopes = (args.scope or "characters").lower()
    if scopes not in ("characters", "environments", "vehicles", "backgrounds", "props", "all"):
        raise SystemExit(f"Unknown scope '{scopes}'")
    # Accept the plural CLI forms (expressions, poses, ...) that match the
    # catalog's singular asset_type column values (expression, pose, ...).
    _SINGULAR = {
        "expressions": "expression", "poses": "pose", "outfits": "outfit",
        "accessories": "accessory", "references": "reference", "views": "view",
        "materials": "material",
        "colors": "color", "exteriors": "exterior", "interiors": "interior",
        "seasons": "season", "weathers": "weather", "vehicles": "vehicle",
        "backgrounds": "background",
    }
    wanted_types = {_SINGULAR.get(t.strip(), t.strip())
                    for t in args.asset_types.split(",") if t.strip()}

    asset_repo = SQLiteAssetRepository(db_path=args.db)
    char_repo = SQLiteCharacterRepository(db_path=args.db)
    backend = resolve_backend(args.backend, comfyui_url=args.comfyui_url,
                              provider=args.provider)

    conn = asset_repo._get_conn()
    rows = conn.execute(
        "SELECT id, character_id, asset_type, variant, state, file_path, prompt, seed "
        "FROM assets WHERE state IN (%s) ORDER BY character_id" % ", ".join("?" * len(states)),
        tuple(states),
    ).fetchall()

    exported = 0
    skipped = 0
    for row in rows:
        asset_id, character_id, asset_type, variant, state, file_path, prompt, seed = row
        if wanted_types and asset_type not in wanted_types:
            continue

        char_row = char_repo._get_conn().execute(
            "SELECT name, category, bio_data FROM characters WHERE id = ?", (character_id,)
        ).fetchone()
        if char_row is None:
            skipped += 1
            continue
        character_name, category, bio_data_json = char_row
        bio_data = json.loads(bio_data_json or "{}")

        if scopes != "all" and not (
            (scopes == "characters" and category not in ("environment", "asset", "vehicle", "background"))
            or (scopes == "environments" and category == "environment")
            or (scopes == "vehicles" and category == "vehicle")
            or (scopes == "backgrounds" and category == "background")
            or (scopes == "props" and category == "asset")
        ):
            continue

        if file_path and Path(file_path).exists():
            skipped += 1
            continue

        destination = asset_destination(
            character_name, category, asset_type, variant or "",
            bio_data, args.universe, args.world, args.assets,
            seed=seed,
        )
        if args.dry_run:
            print(f"  {destination}")
            exported += 1
            continue

        if not prompt or seed is None:
            skipped += 1
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            output = backend.generate(
                GenerationInput(prompt=prompt, seed=seed, num_images=1,
                                width=args.size, height=args.size)
            )
            if not output.images:
                skipped += 1
                continue
            output.images[0].save(destination, format="PNG")
        except Exception as exc:
            print(f"  ✗ {character_name}/{asset_type}/{variant}: {exc}")
            skipped += 1
            continue

        repo_path = repo_relative_path(destination, Path(args.universe).parent)
        asset_repo._get_conn().execute(
            "UPDATE assets SET file_path = ? WHERE id = ?",
            (repo_path, asset_id),
        )
        asset_repo._get_conn().commit()
        exported += 1
        print(f"  ✓ {destination}")

    print(f"\nExported {exported} assets ({skipped} skipped) to the file tree.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
