#!/usr/bin/env python3
"""build_model_sheets.py — Compose per-character model sheets.

Each model sheet is a labeled grid of the character's turnarounds
(front / 45 / left / right / back / top / bottom) exported to:

  * Universe/ModelSheets/<Name>_model_sheet.png
  * Universe/Characters/<Name>/turnarounds/model_sheet.png

Usage:
    python scripts/build_model_sheets.py --db catalog.db
    python scripts/build_model_sheets.py --characters "Lily Bunny"
"""

import argparse
import re
import sqlite3
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

THUMB = 256
LABEL_H = 28
PANEL_ORDER = ["front", "45", "left", "right", "back", "top", "bottom"]


def _load(path: str) -> Image.Image | None:
    p = Path(path)
    return Image.open(p) if p.exists() else None


def _compose(panels: list[tuple[str, Image.Image]], out: Path) -> None:
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
    print(f"  ✓ {out} ({len(panels)} views)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", default="catalog.db", help="SQLite database path")
    parser.add_argument("--universe", default="Universe", help="Universe/ directory")
    parser.add_argument("--model-sheets", default="Universe/ModelSheets",
                        help="Where to write the composite sheets")
    parser.add_argument("--characters", default="",
                        help="Comma list of character names (default: all with turnarounds)")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    if args.characters:
        wanted = {c.strip() for c in args.characters.split(",") if c.strip()}
        placeholders = ", ".join("?" * len(wanted))
        chars = conn.execute(
            f"SELECT id, name FROM characters WHERE name IN ({placeholders})",
            tuple(wanted),
        ).fetchall()
    else:
        chars = conn.execute(
            "SELECT id, name FROM characters "
            "WHERE category NOT IN ('environment', 'asset') ORDER BY name"
        ).fetchall()

    made = 0
    for char_id, name in chars:
        panels = []
        for angle in PANEL_ORDER:
            row = conn.execute(
                "SELECT file_path FROM assets "
                "WHERE character_id=? AND asset_type='reference' AND variant=? "
                "AND state IN ('shortlisted','approved','production') "
                "ORDER BY brand_score DESC LIMIT 1",
                (char_id, angle),
            ).fetchone()
            if row and row[0]:
                img = _load(row[0])
                if img is not None:
                    panels.append((angle, img))
        if not panels:
            continue
        slug = re.sub(r"[^A-Za-z0-9 _.-]+", "", name).strip().replace(" ", "_")
        _compose(panels, Path(args.model_sheets) / f"{slug}_model_sheet.png")
        _compose(panels, Path(args.universe) / "Characters" / name / "turnarounds" / "model_sheet.png")
        made += 1

    print(f"\nComposed {made} model sheets.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
