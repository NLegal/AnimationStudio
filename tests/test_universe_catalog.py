"""Tests for the universe catalog parser (``src.universe.catalog``).

Verifies that the Phase 1/2/3 markdown documents parse into the expected
catalog: 39 character seeds, 9 world zones, and the reusable props/assets,
with correct categories, identifiers, and prompt-building data.
"""

from src.universe.catalog import (
    ART_DIRECTION,
    CHARACTER_CATEGORIES,
    discover_characters,
    discover_environments,
    discover_props,
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

    def test_parses_nine_zones(self):
        seeds = discover_environments("World")
        assert len(seeds) == 9

    def test_zone_names(self):
        seeds = {s.name for s in discover_environments("World")}
        for expected in ("Sunny Meadow", "Main Street", "Dreamland"):
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


class TestDiscoverProps:
    """Parsing of World/Props/INDEX.md and Assets/*/INDEX.md into PropSeed."""

    def test_parses_prop_rows(self):
        seeds = discover_props("World", "Assets")
        assert len(seeds) > 500

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
