"""Tests for the Phase 1 library generator (``scripts.generate_phase1_library``).

Covers the asset-type catalogue parsing (aliases, ``all``), per-character
variant expansion (expressions / poses / outfits / turnarounds / lighting /
accessories) and the character selection filter.  All of this must line up
with the PHASE1.md deliverable libraries.
"""

import pytest

from scripts.generate_phase1_library import (
    ASSET_TYPES,
    _accessories_for,
    _parse_asset_types,
    _tasks,
    _variants,
)
from src.universe.catalog import discover_characters


def test_parse_asset_types_all_default():
    assert _parse_asset_types("all") == list(ASSET_TYPES)
    assert _parse_asset_types("") == list(ASSET_TYPES)
    assert _parse_asset_types("*") == list(ASSET_TYPES)


def test_parse_asset_types_comma_list_and_aliases():
    assert _parse_asset_types("expressions,poses") == ["expressions", "poses"]
    # Singular/alias forms map onto the canonical library keys.
    assert _parse_asset_types("reference,expressions") == ["reference", "expressions"]
    assert _parse_asset_types("turnaround,accessory") == ["turnarounds", "accessories"]


def test_parse_asset_types_unknown_raises():
    with pytest.raises(SystemExit):
        _parse_asset_types("bogus")


def test_variant_coverage_matches_phase1():
    """PHASE1.md rotation (7) and lighting (11) libraries, plus expressions and
    poses pulled from the PromptBuilder superset."""
    seed = discover_characters("Universe")[0]
    variants = {key: _variants(key, seed) for key in ASSET_TYPES}
    assert variants["reference"] == ["front"]
    assert variants["turnarounds"] == ["45", "left", "right", "back", "top", "bottom"]
    assert len(variants["lighting"]) == 11
    assert len(variants["expressions"]) >= 23
    assert len(variants["poses"]) >= 20
    assert variants["outfits"]  # at least one wardrobe entry


def test_accessories_from_bio():
    seeds = {s.name: s for s in discover_characters("Universe")}
    lily = seeds["Lily Bunny"]
    accessories = _accessories_for(lily)
    assert "Blue bow on left ear (signature)" in accessories
    assert "small backpack" in accessories


def test_accessories_are_deduplicated():
    seed = discover_characters("Universe")[0]
    accessories = _accessories_for(seed)
    assert len(accessories) == len(set(accessories))


def test_tasks_expand_character_variants():
    seeds = discover_characters("Universe")[:1]
    tasks = list(_tasks(seeds, ["reference", "accessories"]))
    assert tasks and tasks[0][0] is seeds[0]
    assert tasks[0][1] == "reference"
    assert {t[1] for t in tasks} == {"reference", "accessories"}
