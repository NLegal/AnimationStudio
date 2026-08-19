"""Tests for the Phase 2 world library generator
(``scripts.generate_phase2_world``).

Covers the asset-type catalogue parsing (aliases, ``all``), the PHASE2.md
variant-dimension selection (seasons / time / weather / camera), the task
expansion across world locations / vehicles / backgrounds, and the location
filter — all of which must line up with the PHASE2.md world deliverables.
"""

import pytest

from scripts.generate_phase2_world import (
    ASSET_TYPES,
    CAMERA_ANGLES,
    CAMERA_ANGLES_ALL,
    HOME_VIEWS,
    SEASONS,
    SEASONS_ALL,
    TIMES,
    TIMES_ALL,
    WEATHERS,
    WEATHERS_ALL,
    _bg_layer,
    _hero_locations,
    _parse_asset_types,
    _parse_variants,
    _tasks,
)
from src.universe.catalog import (
    discover_backgrounds,
    discover_vehicles,
    discover_world_environments,
)


def _world():
    envs = discover_world_environments("World")
    vehs = discover_vehicles("World")
    bgs = discover_backgrounds("World")
    assert envs and vehs and bgs  # World/ tree must be present
    return envs, vehs, bgs


def test_parse_asset_types_all_default():
    assert _parse_asset_types("all") == list(ASSET_TYPES)
    assert _parse_asset_types("") == list(ASSET_TYPES)
    assert _parse_asset_types("*") == list(ASSET_TYPES)


def test_parse_asset_types_comma_list_and_aliases():
    assert _parse_asset_types("seasons,time") == ["seasons", "time"]
    # Singular/alias forms map onto the canonical library keys.
    assert _parse_asset_types("exterior,interior") == ["exteriors", "interiors"]
    assert _parse_asset_types("season,weather,camera") == [
        "seasons", "weather", "camera",
    ]
    assert _parse_asset_types("vehicle,background") == ["vehicles", "backgrounds"]
    # Mixed case, spacing and duplicates are handled.
    assert _parse_asset_types(" Exteriors,season,EXTERIORS ") == ["exteriors", "seasons"]


def test_parse_asset_types_unknown_raises():
    with pytest.raises(SystemExit):
        _parse_asset_types("bogus")


def test_variant_dimension_defaults_are_core_sets():
    assert SEASONS == ["spring", "summer", "autumn", "winter"]
    assert TIMES == ["morning", "noon", "golden_hour", "night"]
    assert WEATHERS == ["sunny", "cloudy", "rain", "snow"]
    assert len(CAMERA_ANGLES) == 10


def test_parse_variants_all_expands_full_catalog():
    assert _parse_variants("all", SEASONS, SEASONS_ALL, "season") == SEASONS_ALL
    assert _parse_variants("all", TIMES, TIMES_ALL, "time") == TIMES_ALL
    assert _parse_variants("all", WEATHERS, WEATHERS_ALL, "weather") == WEATHERS_ALL
    assert _parse_variants("all", CAMERA_ANGLES, CAMERA_ANGLES_ALL, "camera") == CAMERA_ANGLES_ALL


def test_parse_variants_empty_keeps_core_defaults():
    assert _parse_variants("", SEASONS, SEASONS_ALL, "season") == SEASONS
    assert _parse_variants("", TIMES, TIMES_ALL, "time") == TIMES
    assert _parse_variants("", WEATHERS, WEATHERS_ALL, "weather") == WEATHERS
    assert _parse_variants("", CAMERA_ANGLES, CAMERA_ANGLES_ALL, "camera") == CAMERA_ANGLES


def test_parse_variants_comma_list_and_aliases():
    assert _parse_variants("sunrise,morning, noon", TIMES, TIMES_ALL, "time") == [
        "sunrise", "morning", "noon",
    ]
    assert _parse_variants("holiday,CHRISTMAS", SEASONS, SEASONS_ALL, "season") == [
        "holiday", "christmas",
    ]


def test_parse_variants_unknown_raises():
    with pytest.raises(SystemExit):
        _parse_variants("blizzard", WEATHERS, WEATHERS_ALL, "weather")


def test_tasks_exteriors_home_views_only_for_residential():
    envs, _vehs, _bgs = _world()
    residential = [e for e in envs if e.bio_data.get("zone_dir") == "Residential"]
    non_residential = [e for e in envs if e.bio_data.get("zone_dir") != "Residential"]
    tasks = list(_tasks(envs, [], [], ["exteriors"]))
    # 9 Home Library views per residential home, one front view otherwise.
    assert sum(1 for t in tasks if t[0] in residential) == len(residential) * len(HOME_VIEWS)
    assert sum(1 for t in tasks if t[0] in non_residential) == len(non_residential)
    variants = {t[3] for t in tasks if t[0] in residential}
    assert variants == set(HOME_VIEWS)


def test_tasks_interiors_rotate_rooms():
    envs, _vehs, _bgs = _world()
    tasks = list(_tasks(envs, [], [], ["interiors"]))
    assert len(tasks) == len(envs)
    rooms = {t[3] for t in tasks}
    assert len(rooms) > 1  # rooms actually rotate across locations


def test_tasks_seasons_times_weathers_cover_every_location():
    envs, _vehs, _bgs = _world()
    for key, variants in (("seasons", SEASONS), ("time", TIMES), ("weather", WEATHERS)):
        tasks = list(_tasks(envs, [], [], [key]))
        assert len(tasks) == len(envs) * len(variants)
        per_env = {}
        for t in tasks:
            per_env.setdefault(t[0].identifier, set()).add(t[3])
        assert all(v == set(variants) for v in per_env.values())


def test_tasks_camera_one_hero_location_per_zone():
    envs, _vehs, _bgs = _world()
    tasks = list(_tasks(envs, [], [], ["camera"]))
    heroes = _hero_locations(envs)
    assert len(heroes) == len({e.bio_data.get("zone_dir") for e in envs})
    assert len(tasks) == len(heroes) * len(CAMERA_ANGLES)
    assert {t[0].identifier for t in tasks} == {h.identifier for h in heroes}


def test_tasks_vehicles_front_and_side():
    _envs, vehs, _bgs = _world()
    tasks = list(_tasks([], vehs, [], ["vehicles"]))
    assert len(tasks) == len(vehs) * 2
    assert {t[3] for t in tasks} == {"front", "side"}


def test_tasks_backgrounds_layer_mapping():
    _envs, _vehs, bgs = _world()
    tasks = list(_tasks([], [], bgs, ["backgrounds"]))
    assert len(tasks) == len(bgs)
    layers = {t[3] for t in tasks}
    assert layers == {"sky", "landscape", "texture"}
    for t in tasks:
        assert t[3] == _bg_layer(t[0])


def test_bg_layer_uses_asset_id_prefix():
    class _Fake:
        asset_id = "BG_Landscape_003"
    assert _bg_layer(_Fake()) == "landscape"
    class _Fake:
        asset_id = "BG_Texture_002"
    assert _bg_layer(_Fake()) == "texture"
    class _Fake:
        asset_id = "BG_Sky_007"
    assert _bg_layer(_Fake()) == "sky"


def test_tasks_full_catalogs_expand():
    envs, vehs, bgs = _world()
    heroes = _hero_locations(envs)
    tasks = list(_tasks(envs, vehs, bgs, ["seasons", "time", "weather", "camera"],
                        seasons=SEASONS_ALL, times=TIMES_ALL,
                        weathers=WEATHERS_ALL, cameras=CAMERA_ANGLES_ALL))
    expected = (
        len(envs) * len(SEASONS_ALL)
        + len(envs) * len(TIMES_ALL)
        + len(envs) * len(WEATHERS_ALL)
        + len(heroes) * len(CAMERA_ANGLES_ALL)
    )
    assert len(tasks) == expected
    assert any(t[3] == "holiday" for t in tasks)
    assert any(t[3] == "moonlight" for t in tasks)
    assert any(t[3] == "rainbow" for t in tasks)
    assert any(t[3] == "tracking" for t in tasks)


def test_tasks_all_asset_types_core_workload():
    """The default 'all' workload matches PHASE2_STATUS.md (2,298 tasks)."""
    envs, vehs, bgs = _world()
    tasks = list(_tasks(envs, vehs, bgs, list(ASSET_TYPES)))
    assert len(tasks) == 2298
