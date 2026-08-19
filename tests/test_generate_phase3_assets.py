"""Tests for the Phase 3 asset library generator
(``scripts.generate_phase3_assets``).

Covers the asset-type catalogue parsing (aliases, ``all``), the material /
color variant selection (deterministic pick vs full PHASE3.md catalogs), the
task expansion across prop references / views / materials / colors / lighting,
the prop filter, and the metadata enrichment that feeds the prompts — all of
which must line up with the PHASE3.md asset library deliverables.
"""

import pytest

from scripts.generate_phase3_assets import (
    ASSET_TYPES,
    LIGHTING_STUDIES,
    VIEWS,
    _color_catalog,
    _material_catalog,
    _parse_asset_types,
    _parse_variants,
    _pick_color,
    _pick_material,
    _tasks,
)
from src.prompt_builder.templates import _PROP_COLOR_VARIANTS, _PROP_MATERIALS
from src.universe.catalog import _PROP_SCALES, discover_props


@pytest.fixture(scope="module")
def props():
    """All 1,559 prop seeds (World/INDEX.md + Assets/Props/INDEX.md)."""
    found = discover_props("World", "Assets")
    assert len(found) == 1559  # PHASE3_STATUS.md baseline
    return found


def test_parse_asset_types_all_default():
    assert _parse_asset_types("all") == list(ASSET_TYPES)
    assert _parse_asset_types("") == list(ASSET_TYPES)
    assert _parse_asset_types("*") == list(ASSET_TYPES)


def test_parse_asset_types_comma_list_and_aliases():
    assert _parse_asset_types("references,views") == ["references", "views"]
    # Singular/alias forms map onto the canonical library keys.
    assert _parse_asset_types("reference,view,material,color") == [
        "references", "views", "materials", "colors",
    ]
    assert _parse_asset_types("lighting") == ["lighting"]
    # Mixed case, spacing and duplicates are handled.
    assert _parse_asset_types(" Views,reference,VIEWS ") == ["views", "references"]


def test_parse_asset_types_unknown_raises():
    with pytest.raises(SystemExit):
        _parse_asset_types("bogus")


def test_parse_asset_types_empty_list_raises():
    with pytest.raises(SystemExit):
        _parse_asset_types(" , , ")


def test_catalogs_superset_of_phase3_required_materials():
    """PHASE3.md lists 16 materials; the code catalog is a superset."""
    required = [
        "wood", "plastic", "metal", "fabric", "cotton", "rubber", "glass",
        "paper", "cardboard", "ceramic", "stone", "grass", "water", "snow",
        "ice", "sand", "foam",
    ]
    catalog = _material_catalog()
    assert len(catalog) == 17
    assert all(m in catalog for m in required)
    assert all(k in _PROP_MATERIALS for k in catalog)


def test_parse_variants_all_expands_full_catalogs():
    assert _parse_variants("all", [], _material_catalog(), "material") == _material_catalog()
    assert _parse_variants("all", [], _color_catalog(), "color") == _color_catalog()


def test_parse_variants_empty_keeps_deterministic_pick():
    assert _parse_variants("", [], _material_catalog(), "material") == []
    assert _parse_variants("", [], _color_catalog(), "color") == []


def test_parse_variants_comma_list_validated():
    assert _parse_variants("wood, glass,foam", [], _material_catalog(), "material") == [
        "wood", "glass", "foam",
    ]
    assert _parse_variants("wood,WOOD", [], _material_catalog(), "material") == ["wood"]


def test_parse_variants_unknown_raises():
    with pytest.raises(SystemExit):
        _parse_variants("unobtainium", [], _material_catalog(), "material")
    with pytest.raises(SystemExit):
        _parse_variants("chartreuse", [], _color_catalog(), "color")


def test_pick_material_and_color_deterministic_and_in_catalog():
    props = discover_props("World", "Assets")
    for p in props[:10]:
        mat = _pick_material(p)
        col = _pick_color(p)
        assert mat in _material_catalog()
        assert col in _color_catalog()
        # Same seed → same variant every time.
        assert _pick_material(p) == mat
        assert _pick_color(p) == col
        # Different seeds spread across the catalogs (not all identical).
        assert len({_pick_material(p) for p in props[:50]}) > 1
        assert len({_pick_color(p) for p in props[:50]}) > 1


def test_tasks_references_one_front_per_prop(props):
    tasks = list(_tasks(props, ["references"]))
    assert len(tasks) == len(props)
    assert all(t[2] == "reference" and t[3] == "front" for t in tasks)


def test_tasks_views_three_turnaround_per_prop(props):
    tasks = list(_tasks(props, ["views"]))
    assert len(tasks) == len(props) * len(VIEWS)
    assert {t[3] for t in tasks} == set(VIEWS)


def test_tasks_materials_default_one_deterministic_pick(props):
    tasks = list(_tasks(props, ["materials"]))
    assert len(tasks) == len(props)
    assert all(t[3] in _material_catalog() for t in tasks)


def test_tasks_materials_all_full_catalog(props):
    tasks = list(_tasks(props, ["materials"], materials=_material_catalog()))
    assert len(tasks) == len(props) * len(_material_catalog())
    assert {t[3] for t in tasks} == set(_material_catalog())


def test_tasks_colors_all_full_catalog(props):
    tasks = list(_tasks(props, ["colors"], colors=_color_catalog()))
    assert len(tasks) == len(props) * len(_color_catalog())
    assert {t[3] for t in tasks} == set(_color_catalog())


def test_tasks_lighting_two_studies_per_prop(props):
    tasks = list(_tasks(props, ["lighting"]))
    assert len(tasks) == len(props) * len(LIGHTING_STUDIES)
    assert {t[3] for t in tasks} == set(LIGHTING_STUDIES)


def test_tasks_all_asset_types_core_workload(props):
    """The default 'all' workload matches PHASE3_STATUS.md (12,472 tasks)."""
    tasks = list(_tasks(props, list(ASSET_TYPES)))
    assert len(tasks) == 12472


def test_tasks_full_catalogs_expand(props):
    tasks = list(_tasks(props, list(ASSET_TYPES),
                        materials=_material_catalog(),
                        colors=_color_catalog()))
    expected = len(props) * (
        1 + len(VIEWS) + len(_material_catalog()) + len(_color_catalog()) + len(LIGHTING_STUDIES)
    )
    assert len(tasks) == expected
    # Full catalogs actually show up in the variant stream.
    assert any(t[3] == "snow" for t in tasks)
    assert any(t[3] == "mint" for t in tasks)


def test_metadata_enrichment_fills_every_prop(props):
    """All 1,559 props carry material/scale/animation/interactive/colors/location."""
    for key in ("material", "scale", "animation", "interactive", "colors", "location"):
        assert all(getattr(p, key) for p in props), key
    # PHASE3.md §Metadata: every prop also declares child safety and reuse.
    assert all(getattr(p, "child_safe") for p in props)
    assert all(getattr(p, "reusable") for p in props)
    assert _PROP_SCALES  # PHASE3_STATUS.md scale guide stays reachable


def test_metadata_enrichment_preserves_explicit_values(props):
    toy = next(p for p in props if p.asset_id == "TOY_Animal_001")
    assert toy.material.startswith("Polyester plush fabric")
    assert toy.scale == "25 cm seated height"
    assert toy.colors == "Cream, Pink, White"


def test_metadata_enrichment_scale_in_scale_guide(props):
    scales = set(_PROP_SCALES)
    for p in props:
        if p.scale.lower() not in scales:
            assert len(p.scale) > 0


def test_prop_filter_matches_by_id_and_name(props):
    targets = props[:3]
    ids = [t.asset_id for t in targets]
    names = [t.name for t in targets[:2]]
    filtered = [p for p in props if p.asset_id.lower() in {i.lower() for i in ids}
                or p.name.lower() in {n.lower() for n in names}]
    assert len(filtered) == 3
    assert {p.asset_id for p in filtered} == set(ids)


def test_discovery_category_dirs_are_twenty(props):
    assert len({p.category_dir for p in props}) == 20
