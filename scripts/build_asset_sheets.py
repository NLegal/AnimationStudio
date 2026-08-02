#!/usr/bin/env python3
"""build_asset_sheets.py — Compose labeled reference sheets for the asset library.

Each prop sheet is a grid of the prop's generated variants (reference, views,
material, color, and lighting studies) written to:

  * Assets/ReferenceSheets/<CategoryDir>/<ASSET_ID>_sheet.png

Usage:
    python scripts/build_asset_sheets.py --db catalog.db
    python scripts/build_asset_sheets.py --category Toys
"""

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

THUMB = 256
LABEL_H = 28

# (label prefix, asset_type, variants) — variant ordering per sheet.
PANEL_GROUPS: list[tuple[str, str, list[str]]] = [
    ("reference", "reference", ["front"]),
    ("view", "view", ["side", "top", "back"]),
    ("material", "material", []),
    ("color", "color", []),
    ("lighting", "lighting", ["studio", "natural"]),
]


def _slugify(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9 _.-]+", "", name).strip().replace(" ", "_")


def _load(path: str):
    p = Path(path)
    return Image.open(p) if p.exists() else None


def _compose(panels: list[tuple[str, Image.Image]], out: Path) -> int:
    if not panels:
        return 0
    cols = max(1, min(len(panels), 7))
    rows = (len(panels) + cols - 1) // cols
    cell_w, cell_h = THUMB, THUMB + LABEL_H
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)

    for i, (label, img) in enumerate(panels):
        img = img.convert("RGB").resize((THUMB, THUMB), Image.LANCZOS)
        r, c = divmod(i, cols)
        x, y = c * cell_w, r * cell_h
        sheet.paste(img, (x, y))
        draw.rectangle([x, y + THUMB, x + cell_w, y + cell_h], fill=(245, 245, 245))
        draw.text((x + 8, y + THUMB + 6), label, fill=(40, 40, 40))

    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return len(panels)


def _prop_panels(conn, char_id: str) -> list[tuple[str, Image.Image]]:
    panels: list[tuple[str, Image.Image]] = []
    for prefix, asset_type, variants in PANEL_GROUPS:
        variants = variants or _existing_variants(conn, char_id, asset_type)
        for variant in variants:
            row = conn.execute(
                "SELECT file_path FROM assets "
                "WHERE character_id=? AND asset_type=? AND variant=? "
                "AND state IN ('shortlisted','approved','production') "
                "ORDER BY brand_score DESC LIMIT 1",
                (char_id, asset_type, variant),
            ).fetchone()
            if not row or not row[0]:
                continue
            img = _load(row[0])
            if img is not None:
                label = variant if prefix == "reference" else f"{prefix}-{variant}"
                panels.append((label, img))
    return panels


def _existing_variants(conn, char_id: str, asset_type: str) -> list[str]:
    rows = conn.execute(
        "SELECT DISTINCT variant FROM assets "
        "WHERE character_id=? AND asset_type=? AND variant IS NOT NULL "
        "AND state IN ('shortlisted','approved','production') "
        "ORDER BY variant",
        (char_id, asset_type),
    ).fetchall()
    return [r[0] for r in rows]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", default="catalog.db", help="SQLite database path")
    parser.add_argument("--assets", default="Assets", help="Assets/ directory")
    parser.add_argument("--category", default="",
                        help="Restrict to one category dir (e.g. Toys)")
    parser.add_argument("--reference-sheets", default="ReferenceSheets",
                        help="Subdirectory of Assets/ for the sheets")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    made = 0
    total_views = 0

    chars = conn.execute(
        "SELECT id, name, bio_data FROM characters WHERE category='asset' ORDER BY name"
    ).fetchall()
    for char_id, name, bio_data_json in chars:
        bio = json.loads(bio_data_json or "{}")
        asset_id = bio.get("asset_id") or name
        category_dir = bio.get("category_dir") or "Props"
        if args.category and category_dir.lower() != args.category.lower():
            continue
        panels = _prop_panels(conn, char_id)
        if not panels:
            continue
        out = (Path(args.assets) / args.reference_sheets / _slugify(category_dir)
               / f"{_slugify(asset_id)}_sheet.png")
        views = _compose(panels, out)
        print(f"  ✓ {out} ({views} panels)")
        made += 1
        total_views += views

    print(f"\nComposed {made} sheets ({total_views} panels).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
