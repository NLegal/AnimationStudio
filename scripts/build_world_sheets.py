#!/usr/bin/env python3
"""build_world_sheets.py — Compose labeled reference sheets for the world.

Each environment sheet is a grid of the location's generated variants
(exteriors, interior, seasons, time-of-day, weather, and camera angles)
written to:

  * World/ReferenceSheets/Environments/<Zone>/<Identifier>_sheet.png

Vehicle sheets (front / side) are written to:

  * World/ReferenceSheets/Vehicles/<VEH_id>_sheet.png

Usage:
    python scripts/build_world_sheets.py --db catalog.db
    python scripts/build_world_sheets.py --zone Residential
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
    ("exterior", "exterior", ["front", "back", "garage", "garden",
                              "mailbox", "driveway", "top"]),
    ("interior", "interior", ["living_room", "kitchen", "bedroom", "bathroom",
                              "dining_room", "playroom", "garage", "garden",
                              "classroom", "music_room", "library",
                              "default_interior"]),
    ("season", "season", ["spring", "summer", "autumn", "winter"]),
    ("time", "time_of_day", ["morning", "noon", "golden_hour", "night"]),
    ("weather", "weather", ["sunny", "cloudy", "rain", "snow"]),
    ("camera", "camera", ["wide", "ultra_wide", "medium", "close",
                          "extreme_close", "overhead", "birds_eye",
                          "ground_level", "low_angle", "high_angle"]),
]

VEHICLE_VIEWS: list[str] = ["front", "side"]


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


def _env_panels(conn, char_id: str) -> list[tuple[str, Image.Image]]:
    panels: list[tuple[str, Image.Image]] = []
    for prefix, asset_type, variants in PANEL_GROUPS:
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
                label = variant if prefix == "exterior" else f"{prefix}-{variant}"
                panels.append((label, img))
    return panels


def _vehicle_panels(conn, char_id: str) -> list[tuple[str, Image.Image]]:
    panels: list[tuple[str, Image.Image]] = []
    for variant in VEHICLE_VIEWS:
        row = conn.execute(
            "SELECT file_path FROM assets "
            "WHERE character_id=? AND asset_type='vehicle' AND variant=? "
            "AND state IN ('shortlisted','approved','production') "
            "ORDER BY brand_score DESC LIMIT 1",
            (char_id, variant),
        ).fetchone()
        if row and row[0]:
            img = _load(row[0])
            if img is not None:
                panels.append((variant, img))
    return panels


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", default="catalog.db", help="SQLite database path")
    parser.add_argument("--world", default="World", help="World/ directory")
    parser.add_argument("--zone", default="",
                        help="Restrict to one zone dir name (e.g. Residential)")
    parser.add_argument("--reference-sheets", default="ReferenceSheets",
                        help="Subdirectory of World/ for the sheets")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    made = 0
    total_views = 0

    # Environment sheets, one per location.
    env_chars = conn.execute(
        "SELECT id, name, bio_data FROM characters WHERE category='environment' ORDER BY name"
    ).fetchall()
    for char_id, name, bio_data_json in env_chars:
        bio = json.loads(bio_data_json or "{}")
        if not bio.get("identifier"):
            continue  # zone summaries, not per-location environments
        zone_dir = bio.get("zone_dir") or "Zones"
        if args.zone and zone_dir.lower() != args.zone.lower():
            continue
        panels = _env_panels(conn, char_id)
        if not panels:
            continue
        out = (Path(args.world) / args.reference_sheets / "Environments" / _slugify(zone_dir)
               / f"{_slugify(bio['identifier'])}_sheet.png")
        views = _compose(panels, out)
        print(f"  ✓ {out} ({views} views)")
        made += 1
        total_views += views

    # Vehicle sheets, one per vehicle.
    veh_chars = conn.execute(
        "SELECT id, name, bio_data FROM characters WHERE category='vehicle' ORDER BY name"
    ).fetchall()
    for char_id, name, bio_data_json in veh_chars:
        bio = json.loads(bio_data_json or "{}")
        identifier = bio.get("asset_id") or name
        panels = _vehicle_panels(conn, char_id)
        if not panels:
            continue
        out = (Path(args.world) / args.reference_sheets / "Vehicles"
               / f"{_slugify(identifier)}_sheet.png")
        views = _compose(panels, out)
        print(f"  ✓ {out} ({views} views)")
        made += 1
        total_views += views

    print(f"\nComposed {made} sheets ({total_views} panels).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
