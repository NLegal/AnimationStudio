"""Tests for the universe catalog parser (``src.universe.catalog``).

Verifies that the Phase 1/2/3 markdown documents parse into the expected
catalog: 39 character seeds, 10 world zones, and the reusable props/assets,
with correct categories, identifiers, and prompt-building data.
"""

from src.universe.catalog import (
    ART_DIRECTION,
    CHARACTER_CATEGORIES,
    discover_backgrounds,
    discover_characters,
    discover_environments,
    discover_props,
    discover_vehicles,
    discover_world_environments,
)


class TestDiscoverCharacters:
    """Parsing of Universe/Characters/*/bio.md into CharacterSeed objects."""

    def test_parses_all_bios(self):
        seeds = discover_characters("Universe")
        assert len(seeds) == 39

    def test_every_seed_has_category(self):
        seeds = discover_characters("Universe")
        assert all(s.category for s in seeds)

    def test_categories_are_valid(self):
        seeds = discover_characters("Universe")
        valid = set(CHARACTER_CATEGORIES.values())
        assert all(s.category in valid for s in seeds)

    def test_lily_seed_details(self):
        seeds = {s.name: s for s in discover_characters("Universe")}
        lily = seeds["Lily Bunny"]
        assert lily.category == "main"
        assert lily.species == "Bunny"
        assert "blue bow" in lily.default_outfit.lower()
        assert "appearance" in lily.bio_data

    def test_art_direction_constant(self):
        assert "Pixar-quality" in ART_DIRECTION
        assert "child-safe" in ART_DIRECTION

    def test_character_categories_cover_all_bios(self):
        seeds = discover_characters("Universe")
        categories = {s.category for s in seeds}
        assert categories <= set(CHARACTER_CATEGORIES.values())


class TestDiscoverEnvironments:
    """Parsing of World/WORLD_OVERVIEW.md into EnvironmentSeed objects."""

    def test_parses_all_zones(self):
        seeds = discover_environments("World")
        assert len(seeds) == 10

    def test_zone_names(self):
        seeds = {s.name for s in discover_environments("World")}
        for expected in ("Sunny Meadow", "Main Street", "Dreamland", "Busy Bridge"):
            assert expected in seeds

    def test_identifiers_present(self):
        seeds = discover_environments("World")
        assert all(s.identifier for s in seeds)
        assert "ENV_Residential" in seeds[0].identifier

    def test_description_is_real_paragraph(self):
        """Description must not leak markdown metadata (the old bug)."""
        seeds = discover_environments("World")
        for s in seeds:
            assert "**" not in s.description
            assert s.description

    def test_prompt_composed(self):
        seeds = discover_environments("World")
        first = seeds[0]
        assert "Little Learning Town" in first.prompt
        assert first.description[:60] in first.prompt

    def test_negative_prompt_present(self):
        seeds = discover_environments("World")
        assert all(s.negative_prompt for s in seeds)


class TestDiscoverWorldLocations:
    """Per-location environment parsing from the Phase 2 zone bibles."""

    def test_parses_all_locations(self):
        seeds = discover_world_environments("World")
        assert len(seeds) == 138

    def test_all_identifiers_unique(self):
        seeds = discover_world_environments("World")
        identifiers = [s.identifier for s in seeds]
        assert len(identifiers) == len(set(identifiers))

    def test_identifiers_use_zone_prefix(self):
        seeds = discover_world_environments("World")
        prefixes = {s.identifier.split("_")[1] for s in seeds}
        for zone in ("Residential", "Downtown", "School", "Playground",
                     "Farm", "Forest", "Beach", "Mountains", "Fantasy"):
            assert zone in prefixes

    def test_zone_assignment(self):
        seeds = discover_world_environments("World")
        assert all(s.zone for s in seeds)
        assert any("Residential" in s.zone for s in seeds)
        assert any("Fantasy" in s.zone for s in seeds)

    def test_description_is_real_paragraph(self):
        seeds = discover_world_environments("World")
        assert all("**" not in s.description for s in seeds)
        assert all(s.description for s in seeds)

    def test_prompt_composed(self):
        seeds = discover_world_environments("World")
        first = seeds[0]
        assert "Little Learning Town" in first.prompt
        assert first.description[:60] in first.prompt

    def test_zone_dir_tracked(self):
        seeds = discover_world_environments("World")
        assert all(s.bio_data.get("zone_dir") for s in seeds)


class TestDiscoverVehicles:
    """Vehicle library parsing from World/Vehicles/INDEX.md."""

    def test_parses_vehicles(self):
        seeds = discover_vehicles("World")
        assert len(seeds) == 20

    def test_all_vehicles_have_ids(self):
        seeds = discover_vehicles("World")
        assert all(s.asset_id.startswith("VEH_") for s in seeds)

    def test_categories_set_to_vehicle(self):
        seeds = discover_vehicles("World")
        assert all(s.category == "vehicle" for s in seeds)

    def test_vehicles_have_descriptions(self):
        seeds = discover_vehicles("World")
        assert all(s.description for s in seeds)


class TestDiscoverBackgrounds:
    """Background library parsing from World/Backgrounds/INDEX.md."""

    def test_parses_backgrounds(self):
        seeds = discover_backgrounds("World")
        assert len(seeds) == 26

    def test_all_backgrounds_have_ids(self):
        seeds = discover_backgrounds("World")
        assert all(s.asset_id.startswith("BG_") for s in seeds)

    def test_layer_groups_present(self):
        seeds = discover_backgrounds("World")
        groups = {s.asset_id.split("_")[1] for s in seeds}
        for expected in ("Sky", "Landscape", "Texture"):
            assert expected in groups

    def test_categories_set_to_background(self):
        seeds = discover_backgrounds("World")
        assert all(s.category == "background" for s in seeds)


class TestDiscoverProps:
    """Parsing of World/Props/INDEX.md and Assets/*/INDEX.md into PropSeed."""

    def test_parses_prop_rows(self):
        seeds = discover_props("World", "Assets")
        assert len(seeds) > 1500

    def test_no_empty_categories(self):
        seeds = discover_props("World", "Assets")
        assert all(s.category for s in seeds)

    def test_top_categories_present(self):
        seeds = discover_props("World", "Assets")
        categories = {s.category for s in seeds}
        for expected in ("Furniture", "Decor", "Flowers"):
            assert expected in categories

    def test_prop_has_id_and_name(self):
        seeds = discover_props("World", "Assets")
        for s in seeds[:10]:
            assert s.asset_id
            assert s.name

    def test_prop_has_promptable_text(self):
        """A prop needs at least a name to build a generation prompt."""
        seeds = discover_props("World", "Assets")
        assert all(s.name for s in seeds)

    def test_all_prefixes_discovered(self):
        """Every index format (headings, ID tables, name tables) is parsed."""
        seeds = discover_props("World", "Assets")
        prefixes = {s.asset_id.split("_")[0] for s in seeds}
        for expected in ("TOY", "BOOK", "EDUC", "MUS", "MED", "OCC",
                         "SCH", "SPORT", "PLAY", "PROP", "FOOD", "ANM"):
            assert expected in prefixes, f"missing prefix {expected}"

    def test_no_duplicate_ids(self):
        seeds = discover_props("World", "Assets")
        ids = [s.asset_id for s in seeds]
        assert len(ids) == len(set(ids))

    def test_metadata_fields_captured(self):
        """Heading-style entries carry material/scale/animation metadata."""
        seeds = discover_props("World", "Assets")
        by_id = {s.asset_id: s for s in seeds}
        block = by_id.get("TOY_Block_001")
        assert block is not None
        assert block.category_dir == "Toys"
        assert block.category == "Blocks"
        assert "wood" in block.material.lower() or block.material
        assert block.scale or block.animation or block.interactive

    def test_table_entries_use_id_column(self):
        """Docs with an ``ID`` header (not ``Asset ID``) are still parsed."""
        seeds = discover_props("World", "Assets")
        by_id = {s.asset_id: s for s in seeds}
        for expected in ("MUS_Keyboard_001", "MED_Tool_001", "SCH_Furniture_001"):
            assert expected in by_id, f"missing {expected}"

    def test_description_has_no_markdown_labels(self):
        seeds = discover_props("World", "Assets")
        assert all("**" not in s.description for s in seeds)
