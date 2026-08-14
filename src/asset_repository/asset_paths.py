"""Shared destination-path resolution for generated assets.

Used by the generation pipeline (to persist images at generation time), the
export script, and the Review UI image route so every asset lands in the same
organized tree:

    Universe/Characters/<Name>/expressions/angry_s123.png
    World/<Zone>/exteriors/<id>_<view>.png
    Assets/<Category>/references/<id>_<view>.png

:func:`asset_destination` returns an absolute path.  Asset rows store the
repository-root-relative form (``Universe/Characters/...``) so the same DB
is portable across checkouts (local repo, Colab, GitHub sync).
"""

import os
import re
from pathlib import Path
from typing import Optional

# Turnaround angles (front is the reference library's own view).
TURNAROUND_ANGLES = {"45", "left", "right", "back", "top", "bottom"}

# asset_type -> directory name (character scope)
CHARACTER_DIRS = {
    "reference": "references",
    "expression": "expressions",
    "pose": "poses",
    "outfit": "outfits",
    "lighting": "lighting",
    "accessory": "accessories",
}

# environment asset_type -> folder suffix used in the World/ zone tree
WORLD_DIRS = {
    "exterior": "exteriors",
    "environment": "exteriors",
    "interior": "interiors",
    "season": "seasons",
    "time_of_day": "time_of_day",
    "weather": "weather",
    "camera": "camera",
}

# prop asset_type -> folder suffix used under Assets/<Category>/
PROP_DIRS = {
    "reference": "references",
    "prop": "references",
    "view": "views",
    "material": "materials",
    "color": "colors",
    "lighting": "lighting",
}


def _slugify(name: str) -> str:
    """Filesystem-safe name."""
    return re.sub(r"[^A-Za-z0-9 _.-]+", "", name).strip().replace(" ", "_")


def asset_destination(
    character_name: str,
    category: str,
    asset_type: str,
    variant: str,
    bio_data: dict,
    universe_dir: str,
    world_dir: str,
    assets_dir: str,
    seed: Optional[int] = None,
) -> Path:
    """Resolve the absolute destination path for one asset record.

    ``seed`` (when given) is appended to the file label so multiple
    candidates for the same variant never collide on disk.
    """
    suffix = f"_s{seed}" if seed is not None else ""
    label = _slugify(variant or "asset")

    if category in ("environment", "vehicle", "background"):
        identifier = bio_data.get("identifier") or bio_data.get("asset_id") or character_name
        if category == "environment":
            zone_dir = _slugify(bio_data.get("zone_dir") or "Zones")
            base = Path(world_dir) / zone_dir
        else:
            base = Path(world_dir) / ("Vehicles" if category == "vehicle" else "Backgrounds")
        sub = WORLD_DIRS.get(asset_type)
        if sub:
            base = base / sub
        return base / f"{_slugify(identifier)}_{label}{suffix}.png"

    if category == "asset":
        category_dir = _slugify(bio_data.get("category_dir") or "Props")
        identifier = bio_data.get("asset_id") or character_name
        sub = PROP_DIRS.get(asset_type)
        if sub:
            base = Path(assets_dir) / category_dir / sub
        else:
            base = Path(assets_dir) / category_dir
        return base / f"{_slugify(identifier)}_{label}{suffix}.png"

    base = Path(universe_dir) / "Characters" / character_name
    if asset_type == "reference" and variant in TURNAROUND_ANGLES:
        return base / "turnarounds" / f"{_slugify(variant)}{suffix}.png"
    directory = CHARACTER_DIRS.get(asset_type, "references")
    return base / directory / f"{label}{suffix}.png"


def repo_relative_path(destination: Path, catalog_root: Path) -> str:
    """Portable repository-root-relative path for an absolute destination.

    ``catalog_root`` is the directory containing ``Universe/``, ``World/`` and
    ``Assets/`` (i.e. ``Path(universe_dir).parent`` under the standard layout).
    """
    return str(Path(os.path.relpath(destination, catalog_root)).as_posix())
