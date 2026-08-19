"""Universe catalog — structured seeds from the Universe/World/Assets markdown.

Parses the Phase 1/2/3 world-building documents (character bios, environment
bibles, and prop/asset indexes) into lightweight dataclasses that drive both
seeding (``src.universe.seed``) and batch generation (``src.universe.
batch_generator``) without hand-maintaining a second list of the universe.
"""

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
#  Shared constants
# ---------------------------------------------------------------------------

ART_DIRECTION = (
    "Pixar-quality, Cocomelon-inspired, bright colorful nursery world, "
    "rounded shapes, soft pastel colors, child-safe, highly detailed"
)

# Main art direction used as the base of every character prompt.
STYLE_TAG = "Pixar-quality, Cocomelon-inspired, bright colorful nursery world"

# Mapping of character name → canonical category (matches PHASE1.md groupings).
CHARACTER_CATEGORIES: dict[str, str] = {
    # Main cast (4)
    "Lily Bunny": "main",
    "Ben Bear": "main",
    "Charlie Fox": "main",
    "Daisy Duck": "main",
    # Family (5)
    "Baby Bunny": "family",
    "Daddy Bunny": "family",
    "Mommy Bunny": "family",
    "Grandma Bunny": "family",
    "Grandpa Bunny": "family",
    # Friends (10)
    "Cat": "friend",
    "Chicken": "friend",
    "Cow": "friend",
    "Dog": "friend",
    "Elephant": "friend",
    "Horse": "friend",
    "Monkey": "friend",
    "Mouse": "friend",
    "Pig": "friend",
    "Sheep": "friend",
    # Community (10)
    "Teacher Owl": "community",
    "Doctor Panda": "community",
    "Chef Pig": "community",
    "Farmer Goat": "community",
    "Firefighter Dalmatian": "community",
    "Police Officer Beaver": "community",
    "Librarian Hedgehog": "community",
    "Mail Carrier Turtle": "community",
    "Construction Worker Beaver": "community",
    "Musician Parrot": "community",
    # Fantasy (10)
    "Unicorn": "fantasy",
    "Friendly Dragon": "fantasy",
    "Friendly Dinosaur (Brontosaurus)": "fantasy",
    "Alien": "fantasy",
    "Robot": "fantasy",
    "Cloud": "fantasy",
    "Moon": "fantasy",
    "Stars": "fantasy",
    "Sun": "fantasy",
    "Rainbow": "fantasy",
}


# ---------------------------------------------------------------------------
#  Seed dataclasses
# ---------------------------------------------------------------------------


@dataclass
class CharacterSeed:
    """A parsed character from ``Universe/Characters/<name>/bio.md``."""

    name: str
    species: str = ""
    category: str = "main"
    appearance: str = ""
    default_outfit: str = ""
    bio_data: dict = field(default_factory=dict)

    @property
    def slug(self) -> str:
        return _slugify(self.name)


@dataclass
class EnvironmentSeed:
    """A world zone / named location from the Phase 2 environment bibles."""

    name: str
    zone: str = ""
    identifier: str = ""
    description: str = ""
    prompt: str = ""
    negative_prompt: str = ""
    bio_data: dict = field(default_factory=dict)

    @property
    def slug(self) -> str:
        return _slugify(self.name)


@dataclass
class PropSeed:
    """A single reusable prop/asset from a Phase 2/3 asset index."""

    asset_id: str
    name: str
    category: str = ""
    description: str = ""
    colors: str = ""
    location: str = ""
    material: str = ""
    scale: str = ""
    animation: str = ""
    interactive: str = ""
    category_dir: str = "Props"
    prompt: str = ""
    negative_prompt: str = ""
    child_safe: str = ""
    reusable: str = ""

    @property
    def slug(self) -> str:
        return _slugify(self.asset_id)


# Scale tiers per Assets/ReferenceSheets/Scale/SCALE_GUIDE.md (PHASE3.md
# §Scale Guide).  Used as per-prop defaults when a bible omits the field.
_PROP_SCALES: dict[str, str] = {
    "tiny": "under 5 cm",
    "small": "5-20 cm",
    "medium": "20-100 cm",
    "large": "1-3 m",
    "huge": "3-10 m",
    "massive": "10+ m",
}

# Per-category metadata defaults (PHASE3.md §Metadata).  Explicit values in
# the bibles always win; these guarantee every prop carries the full metadata
# set so records are never left with empty animation/interactive/scale/etc.
_PROP_METADATA_DEFAULTS: dict[str, dict[str, str]] = {
    "Toys": {"material": "plastic", "scale": "small",
             "animation": "rolling, spinning", "interactive": "yes",
             "location": "toy room, playground"},
    "Props": {"material": "plastic", "scale": "small",
              "animation": "static", "interactive": "yes",
              "location": "varies"},
    "Food": {"material": "food-safe plastic", "scale": "tiny",
             "animation": "static", "interactive": "no",
             "location": "kitchen, dining room, grocery"},
    "Books": {"material": "paper, cardboard", "scale": "small",
              "animation": "static", "interactive": "yes",
              "location": "library, bookshelf"},
    "Educational": {"material": "plastic, wood", "scale": "small",
                    "animation": "static", "interactive": "yes",
                    "location": "classroom"},
    "School": {"material": "plastic, wood", "scale": "medium",
               "animation": "static", "interactive": "yes",
               "location": "classroom, hallway"},
    "Playground": {"material": "metal, plastic", "scale": "large",
                   "animation": "static", "interactive": "yes",
                   "location": "playground"},
    "Sports": {"material": "rubber, plastic", "scale": "small",
               "animation": "rolling, bouncing", "interactive": "yes",
               "location": "gym, field"},
    "Musical": {"material": "wood, metal", "scale": "small",
                "animation": "static", "interactive": "yes",
                "location": "music room"},
    "Medical": {"material": "plastic", "scale": "small",
                "animation": "static", "interactive": "no",
                "location": "clinic"},
    "Occupations": {"material": "plastic", "scale": "small",
                    "animation": "static", "interactive": "yes",
                    "location": "varies"},
    "Nature": {"material": "wood, stone", "scale": "medium",
               "animation": "swaying", "interactive": "no",
               "location": "outdoors"},
    "Animals": {"material": "plush fabric", "scale": "small",
                "animation": "hopping, waddling", "interactive": "yes",
                "location": "farm, home, wildlife"},
    "Holidays": {"material": "paper, plastic", "scale": "small",
                 "animation": "static", "interactive": "yes",
                 "location": "home, festive decor"},
    "Kitchen": {"material": "metal, ceramic", "scale": "medium",
                "animation": "static", "interactive": "no",
                "location": "kitchen"},
    "Bathroom": {"material": "plastic, ceramic", "scale": "medium",
                 "animation": "static", "interactive": "no",
                 "location": "bathroom"},
    "Bedroom": {"material": "wood, fabric", "scale": "medium",
                "animation": "static", "interactive": "no",
                "location": "bedroom"},
    "LivingRoom": {"material": "wood, fabric", "scale": "medium",
                   "animation": "static", "interactive": "no",
                   "location": "living room"},
    "Materials": {"material": "varies", "scale": "small",
                  "animation": "static", "interactive": "no",
                  "location": "material library"},
    "Textures": {"material": "varies", "scale": "tiny",
                 "animation": "static", "interactive": "no",
                 "location": "material library"},
}

_PROP_METADATA_FALLBACK: dict[str, str] = {
    "material": "plastic",
    "scale": "small",
    "animation": "static",
    "interactive": "no",
    "location": "varies",
}


def _default_prop_color(seed: "PropSeed") -> str:
    """Deterministic pastel primary color for props without an explicit one."""
    try:
        from src.prompt_builder.templates import _PROP_COLOR_VARIANTS
        palette = sorted(_PROP_COLOR_VARIANTS.values())
    except Exception:
        palette = ["pastel blue", "pastel pink", "pastel yellow", "pastel green"]
    digest = hashlib.sha1(seed.asset_id.encode()).digest()[0]
    return palette[digest % len(palette)].capitalize()


def _enrich_prop_metadata(seed: "PropSeed") -> None:
    """Fill missing prop metadata from per-category defaults.

    Explicit values parsed from the bibles always win; the defaults cover the
    PHASE3.md §Metadata deliverable (material / scale / animation /
    interactive / typical_location / colors) for every prop record.
    """
    defaults = _PROP_METADATA_DEFAULTS.get(seed.category_dir, _PROP_METADATA_FALLBACK)
    if not seed.material:
        seed.material = defaults["material"]
    if not seed.scale:
        seed.scale = defaults["scale"]
    if not seed.animation:
        seed.animation = defaults["animation"]
    if not seed.interactive:
        seed.interactive = defaults["interactive"]
    if not seed.location:
        seed.location = defaults["location"]
    if not seed.colors:
        seed.colors = _default_prop_color(seed)
    if not seed.child_safe:
        seed.child_safe = "Yes"
    if not seed.reusable:
        seed.reusable = "Yes"


# ---------------------------------------------------------------------------
#  Utilities
# ---------------------------------------------------------------------------


def _slugify(name: str) -> str:
    """Turn a display name into a filesystem-safe lowercase identifier."""
    return re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")


def _extract_section(text: str, heading: str) -> str:
    """Extract the body of a markdown ``## Heading`` section (until next ##)."""
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE | re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        return ""
    body = text[match.end():]
    # Cut at the next markdown heading of any level.
    cut = re.search(r"^\s*#{1,6}\s", body, re.MULTILINE)
    end = cut.start() if cut else len(body)
    return body[:end].strip()


def _extract_fenced(text: str, heading: str) -> str:
    """Extract the fenced code block inside a ``## Heading`` section."""
    section = _extract_section(text, heading)
    fence = re.search(r"```\w*\n(.*?)\n```", section, re.DOTALL)
    if fence:
        return fence.group(1).strip()
    return section.strip()


def _parse_key_value_section(text: str) -> dict:
    """Parse ``- **Key:** value`` bullets into a dict of {key: value}."""
    result: dict[str, str] = {}
    for match in re.finditer(r"^-\s+\*\*([^*]+):\*\*\s*(.*)$", text, re.MULTILINE):
        key = match.group(1).strip().lower().replace(" ", "_")
        result[key] = match.group(2).strip()
    return result


def _parse_table(text: str) -> list[dict]:
    """Parse markdown table rows from contiguous ``|``-delimited blocks."""
    rows: list[dict] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("|"):
            block: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            if len(block) >= 2 and re.match(r"^\|[\s:\-|]+\|?$", block[1]):
                headers = [c.strip().lower().replace(" ", "_")
                           for c in block[0].strip("|").split("|")]
                for ln in block[2:]:
                    cells = [c.strip() for c in ln.strip("|").split("|")]
                    if len(cells) < len(headers):
                        cells += [""] * (len(headers) - len(cells))
                    rows.append(dict(zip(headers, cells)))
        else:
            i += 1
    return rows


# ---------------------------------------------------------------------------
#  Characters
# ---------------------------------------------------------------------------


def discover_characters(universe_dir: str = "Universe") -> list[CharacterSeed]:
    """Parse all character bios under ``Universe/Characters/``."""
    root = Path(universe_dir) / "Characters"
    seeds: list[CharacterSeed] = []
    if not root.is_dir():
        return seeds

    for bio_path in sorted(root.glob("*/bio.md")):
        seed = _parse_bio(bio_path)
        if seed is not None:
            seeds.append(seed)

    # Deterministic ordering: mains first, then by name.
    order = {"main": 0, "family": 1, "friend": 2, "community": 3, "fantasy": 4}
    seeds.sort(key=lambda s: (order.get(s.category, 9), s.name))
    return seeds


def _parse_bio(path: Path) -> Optional[CharacterSeed]:
    """Parse a single character bio.md into a CharacterSeed."""
    text = path.read_text(encoding="utf-8")
    name_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if not name_match:
        return None
    name = name_match.group(1).strip()

    basic = _parse_key_value_section(_extract_section(text, "Basic Information"))
    appearance = _extract_section(text, "Appearance")
    appearance_fields = _parse_key_value_section(appearance)
    clothing = _extract_section(text, "Clothing / Wardrobe")

    species = basic.get("species", "")
    # Species lines often carry descriptor text: "Bunny (soft white fur)".
    species_core = species.split("(")[0].strip()

    # Build a compact appearance summary for prompts.
    appearance_parts = []
    for key in ("eye_color", "fur_color", "skin_color", "ear_shape", "tail",
                "body_shape", "face_shape"):
        value = appearance_fields.get(key)
        if value:
            appearance_parts.append(f"{key.replace('_', ' ')}: {value}")
    if appearance_fields.get("accessories"):
        appearance_parts.append(f"accessories: {appearance_fields['accessories']}")
    appearance_summary = ", ".join(appearance_parts)

    # Default outfit from the wardrobe table's "Daily Outfit" row.
    default_outfit = ""
    for row in _parse_table(clothing):
        variant = row.get("variant", "").lower()
        if variant.startswith("daily"):
            default_outfit = row.get("description", "")

    bio_data: dict = {
        "basic_information": basic,
        "appearance_fields": appearance_fields,
        "appearance": appearance_summary,
        "default_outfit": default_outfit,
        "personality": _parse_key_value_section(_extract_section(text, "Personality")),
        "catchphrases": [
            line.strip().lstrip("0123456789.").strip()
            for line in _extract_section(text, "Catchphrases").splitlines()
            if line.strip() and not line.startswith("|")
        ],
        "source": str(path),
    }
    wardrobe = {
        row.get("variant", ""): row.get("description", "")
        for row in _parse_table(clothing)
    }
    if wardrobe:
        bio_data["wardrobe"] = wardrobe

    return CharacterSeed(
        name=name,
        species=species_core,
        category=CHARACTER_CATEGORIES.get(name, "friend"),
        appearance=appearance_summary or species_core,
        default_outfit=default_outfit or "default outfit",
        bio_data=bio_data,
    )


# ---------------------------------------------------------------------------
#  Environments
# ---------------------------------------------------------------------------


def discover_environments(world_dir: str = "World") -> list[EnvironmentSeed]:
    """Parse the nine world zones from ``World/WORLD_OVERVIEW.md``.

    Each zone is promoted to an EnvironmentSeed with a description, colour
    palette, and landmarks, plus a generation prompt derived from the zone
    identity and the default environment prompt template.
    """
    overview = Path(world_dir) / "WORLD_OVERVIEW.md"
    if not overview.is_file():
        return []

    text = overview.read_text(encoding="utf-8")
    default_prompt = _extract_fenced(text, "Prompt Template (Default Environment)")
    default_negative = _extract_fenced(text, "Negative Prompt Template (Default)")

    seeds: list[EnvironmentSeed] = []
    for match in re.finditer(
        r"^###\s+\d+\.\s+(.+?)\s+\(([^)]+)\)\s*$", text, re.MULTILINE
    ):
        title = match.group(1).strip()
        zone_kind = match.group(2).strip()
        block = text[match.end():]
        cut = re.search(r"^\s*###\s+\d+\.", block, re.MULTILINE)
        block = block[: cut.start()] if cut else block

        ident = re.search(r"\*\*Identifier:\*\*\s*([^\n]+)", block)
        palette = re.search(r"\*\*Color Palette:\*\*\s*([^\n]+)", block)
        desc = re.search(r"\n\s*(?!\*\*)([^\n]+)\n", block)

        description = (desc.group(1).strip() if desc else "").strip()
        identifier = ident.group(1).strip() if ident else zone_kind
        color_palette = palette.group(1).strip() if palette else ""

        zone_prompt = _build_environment_prompt(title, description, color_palette,
                                                default_prompt)
        negative = default_negative

        seeds.append(EnvironmentSeed(
            name=title,
            zone=title,
            identifier=identifier,
            description=description,
            prompt=zone_prompt,
            negative_prompt=negative,
            bio_data={
                "zone_kind": zone_kind,
                "color_palette": color_palette,
                "identifier": identifier,
                "source": str(overview),
            },
        ))

    return seeds


# ---------------------------------------------------------------------------
#  World locations (detailed Phase 2 environments)
# ---------------------------------------------------------------------------

# Zone docs in World/, keyed by the identifier prefix (ENV_<Zone>_NNN).
_WORLD_ZONE_DOCS: dict[str, tuple[str, str]] = {
    "Residential": ("RESIDENTIAL.md", "Sunny Meadow Residential Zone"),
    "Downtown": ("DOWNTOWN.md", "Main Street Downtown Zone"),
    "School": ("SCHOOL.md", "Little Learning Academy Education Zone"),
    "Playground": ("PLAYGROUND.md", "Happy Hills Park Recreation Zone"),
    "Farm": ("FARM.md", "Green Valley Farm Zone"),
    "Forest": ("FOREST.md", "Whispering Woods Forest Zone"),
    "Beach": ("BEACH.md", "Sandy Cove Beach Zone"),
    "Mountains": ("MOUNTAINS.md", "Pine Mountain Zone"),
    "Fantasy": ("FANTASY.md", "Dreamland Fantasy Zone"),
    "Transportation": ("TRANSPORTATION.md", "Busy Bridge Transportation Zone"),
}

# Fallback zone names for docs that don't declare identifiers.
_WORLD_DOC_ZONES: dict[str, str] = {
    "RESIDENTIAL.md": "Sunny Meadow Residential Zone",
    "DOWNTOWN.md": "Main Street Downtown Zone",
    "SCHOOL.md": "Little Learning Academy Education Zone",
    "PLAYGROUND.md": "Happy Hills Park Recreation Zone",
    "FARM.md": "Green Valley Farm Zone",
    "FOREST.md": "Whispering Woods Forest Zone",
    "BEACH.md": "Sandy Cove Beach Zone",
    "MOUNTAINS.md": "Pine Mountain Zone",
    "FANTASY.md": "Dreamland Fantasy Zone",
    "TRANSPORTATION.md": "Busy Bridge Transportation Zone",
}

_WORLD_DOC_NEGATIVES: dict[str, str] = {
    "DOWNTOWN.md": "urban, realistic city, cars, traffic, skyscrapers",
    "SCHOOL.md": "dark classroom, empty school, broken desks",
    "PLAYGROUND.md": "rusty equipment, cracked pavement, litter",
    "FARM.md": "industrial farm, factory, machinery noise",
    "FOREST.md": "dark forest, scary woods, wild animals, thorns",
    "BEACH.md": "deep water, waves, storm, marine litter",
    "MOUNTAINS.md": "steep cliff, avalanche, snowy blizzard",
    "FANTASY.md": "evil castle, dark magic, scary creatures",
    "RESIDENTIAL.md": "empty house, broken home, dark alleys",
    "TRANSPORTATION.md": "busy city, highway traffic, realistic cars, construction site",
}


def discover_world_environments(world_dir: str = "World") -> list[EnvironmentSeed]:
    """Parse every named environment from the Phase 2 zone bibles.

    Two formats are supported:

    * ``**Identifier:** ENV_X_###`` sections (Residential / Downtown /
      School / Playground / Farm) — title from the preceding heading.
    * ``### ENV_X_### — Name`` sections (Beach / Forest / Mountains /
      Fantasy) — title embedded in the heading.

    Returns one EnvironmentSeed per documented location (138 across the
    ten zones), carrying its identifier, zone, and a generation prompt.
    """
    seeds: list[EnvironmentSeed] = []
    world_root = Path(world_dir)
    zone_docs = _WORLD_ZONE_DOCS

    for zone_key, (doc_name, zone_name) in zone_docs.items():
        doc = world_root / zone_key / doc_name
        if not doc.is_file():
            continue
        negative = _WORLD_DOC_NEGATIVES.get(doc_name, "")
        seeds.extend(
            _parse_world_doc(doc, zone_key, zone_name, negative)
        )

    return sorted(seeds, key=lambda s: s.identifier)


def _parse_world_doc(doc: Path, zone_key: str, zone_name: str,
                     negative: str) -> list[EnvironmentSeed]:
    """Extract named locations from one zone bible document."""
    text = doc.read_text(encoding="utf-8")
    seeds: list[EnvironmentSeed] = []

    # Format A: "## <Name>" followed by "**Identifier:** ENV_Zone_NNN".
    for match in re.finditer(
        r"^#{2,3}\s+(.+?)\s*$\s*\n\s*\*\*Identifier:\*\*\s*(ENV_[A-Za-z]+_\d+)",
        text, re.MULTILINE,
    ):
        title = match.group(1).strip()
        identifier = match.group(2).strip()
        block = text[match.end():]
        cut = re.search(r"^\s*#{2,3}\s+.+\s*$\s*\n\s*\*\*Identifier:\*\*", block, re.MULTILINE)
        block = block[: cut.start()] if cut else block
        seed = _world_seed_from_block(
            title, identifier, zone_key, zone_name, negative, block, str(doc),
        )
        if seed is not None:
            seeds.append(seed)

    # Format B: "### ENV_Zone_NNN — Name".
    for match in re.finditer(
        r"^#{2,3}\s+(ENV_[A-Za-z]+_\d+)\s+[—\-–]\s+(.+?)\s*$",
        text, re.MULTILINE,
    ):
        identifier = match.group(1).strip()
        title = match.group(2).strip()
        block = text[match.end():]
        cut = re.search(r"^\s*#{2,3}\s+(ENV_|Prompt Template)", block, re.MULTILINE)
        block = block[: cut.start()] if cut else block
        seed = _world_seed_from_block(
            title, identifier, zone_key, zone_name, negative, block, str(doc),
        )
        if seed is not None:
            seeds.append(seed)

    # De-duplicate by identifier (Format A/B overlap is unlikely but possible).
    seen: set[str] = set()
    unique: list[EnvironmentSeed] = []
    for seed in seeds:
        if seed.identifier in seen:
            continue
        seen.add(seed.identifier)
        unique.append(seed)
    return unique


def _description_from_bold_label(line: str) -> str:
    """Return the text after a descriptive ``**Label:**`` prefix, if any."""
    for label in ("**Description:**", "**Exterior Architecture:**",
                  "**Architecture:**", "**Address:**"):
        if line.startswith(label):
            return line.split(label, 1)[1].strip()
    return ""


def _world_seed_from_block(
    title: str, identifier: str, zone_key: str, zone_name: str,
    negative: str, block: str, source: str,
) -> Optional[EnvironmentSeed]:
    """Build an EnvironmentSeed from one location's section body."""
    lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
    if not lines:
        return None

    description = ""
    plain = ""
    for line in lines:
        if line.startswith("**"):
            if not description:
                description = _description_from_bold_label(line)
            continue
        if line.startswith(("-", "|", "#")) or re.match(r"^\d+\.", line):
            continue
        if not plain:
            plain = line
    if not description and plain:
        description = plain
    description = description[:400]

    prompt = _build_environment_prompt(title, description, "", "")
    return EnvironmentSeed(
        name=title,
        zone=zone_name,
        identifier=identifier,
        description=description,
        prompt=prompt,
        negative_prompt=negative,
        bio_data={
            "zone_kind": zone_name,
            "zone_dir": zone_key,
            "identifier": identifier,
            "source": source,
        },
    )


# ---------------------------------------------------------------------------
#  Vehicles & background layers (Phase 2)
# ---------------------------------------------------------------------------


def discover_vehicles(world_dir: str = "World") -> list[PropSeed]:
    """Parse every vehicle from ``World/Vehicles/INDEX.md``.

    Entries use ``## VEH_*_NNN — Name`` headings with **Colors:/**
    **Who Drives It:/**Typical Location:** fields.
    """
    index = Path(world_dir) / "Vehicles" / "INDEX.md"
    if not index.is_file():
        return []
    seeds = _parse_prop_entries(index)
    for seed in seeds:
        seed.category = "vehicle"
    return seeds


def discover_backgrounds(world_dir: str = "World") -> list[PropSeed]:
    """Parse every background layer from ``World/Backgrounds/INDEX.md``.

    Entries use ``## BG_*_NNN — Name`` headings grouped under
    ``# Skies / Landscapes / Textures``.
    """
    index = Path(world_dir) / "Backgrounds" / "INDEX.md"
    if not index.is_file():
        return []
    seeds = _parse_prop_entries(index)
    for seed in seeds:
        seed.category = "background"
    return seeds


def _build_environment_prompt(name: str, description: str,
                              palette: str, base: str) -> str:
    """Compose a generation prompt for a world zone."""
    parts = [f"Little Learning Town, {name}"]
    if description:
        parts.append(description[:400])
    if palette:
        parts.append(f"color palette: {palette}")
    parts.append(STYLE_TAG)
    parts.append("cinematic lighting, consistent world design, child-safe")
    parts.append("masterpiece, 8k")
    return ", ".join(parts)


# ---------------------------------------------------------------------------
#  Props
# ---------------------------------------------------------------------------


def discover_props(world_dir: str = "World", assets_dir: str = "Assets") -> list[PropSeed]:
    """Parse every prop from the Phase 2/3 asset indexes.

    Sources:
      - ``World/Props/INDEX.md``  (``## PROP_Category_Number — Name`` entries)
      - ``Assets/*/INDEX.md``     (both ``## ID — Name`` heading entries and
        ``| ID | Name | Description | ... |`` table rows)
    """
    seeds: list[PropSeed] = []
    world_index = Path(world_dir) / "Props" / "INDEX.md"
    if world_index.is_file():
        seeds.extend(_parse_prop_entries(world_index, category_dir="Props"))

    assets_root = Path(assets_dir)
    if assets_root.is_dir():
        for index in sorted(assets_root.glob("*/INDEX.md")):
            category_dir = index.parent.name
            seeds.extend(_parse_prop_entries(index, category_dir=category_dir))
            seeds.extend(_parse_prop_table_index(index, category_dir=category_dir))

    seeds.sort(key=lambda s: s.asset_id)
    for seed in seeds:
        _enrich_prop_metadata(seed)
    return seeds


def _parse_prop_entries(index_path: Path, category_dir: str = "Props") -> list[PropSeed]:
    """Parse ``## ID — Name`` heading-style asset indexes."""
    text = index_path.read_text(encoding="utf-8")
    seeds: list[PropSeed] = []
    current_category = ""
    sections = re.split(r"(?m)^#\s+", text)
    for section in sections:
        if not section.strip():
            continue
        header = section.splitlines()[0].strip()
        # Section header: "Furniture (PROP_Furniture_001–020)" or a plain
        # subcategory name (e.g. "Story Books", "Blocks").
        cat_match = re.match(r"^([^(]+)\s*\([A-Z]+_\w+_\d+", header)
        if cat_match:
            current_category = cat_match.group(1).strip()
        else:
            candidate = re.sub(r"\s*\(.*\)\s*$", "", header).strip()
            if re.match(r"^[A-Za-z][A-Za-z /&'-]*$", candidate) and "—" not in candidate:
                current_category = candidate

        for entry in re.finditer(
            r"^##\s+([A-Z]+_[A-Za-z]+_\d+)\s+[—\-–]\s+(.+)$",
            section, re.MULTILINE,
        ):
            asset_id = entry.group(1)
            name = entry.group(2).strip()
            body = section[entry.end():]
            cut = re.search(r"^\s*##\s+[A-Z]+_[A-Za-z]+_\d+", body, re.MULTILINE)
            body = body[: cut.start()] if cut else body

            desc = ""
            for line in body.splitlines():
                line = line.strip()
                if line and not line.startswith(("-", "|")):
                    if line.startswith("**Description:**"):
                        line = line.split("**Description:**", 1)[1].strip()
                    desc = line
                    break

            fields = {"**Colors:**": "colors", "**Typical Location:**": "location",
                      "**Materials:**": "material", "**Scale:**": "scale",
                      "**Animation:**": "animation", "**Interactive:**": "interactive",
                      "**Child Safe:**": "child_safe", "**Reusable:**": "reusable"}
            values: dict[str, str] = {}
            for line in body.splitlines():
                for label, key in fields.items():
                    if label in line:
                        values[key] = line.split(label, 1)[1].strip()

            seeds.append(PropSeed(
                asset_id=asset_id,
                name=name,
                category=current_category,
                category_dir=category_dir,
                description=desc,
                colors=values.get("colors", ""),
                location=values.get("location", ""),
                material=values.get("material", ""),
                scale=values.get("scale", ""),
                animation=values.get("animation", ""),
                interactive=values.get("interactive", ""),
                child_safe=values.get("child_safe", ""),
                reusable=values.get("reusable", ""),
            ))

    return seeds


def _parse_prop_table_index(index_path: Path, category_dir: str = "Props") -> list[PropSeed]:
    """Parse ``Assets/<Category>/INDEX.md`` table-based asset indexes."""
    text = index_path.read_text(encoding="utf-8")
    seeds: list[PropSeed] = []
    current_category = ""

    sections = re.split(r"(?m)^#{1,6}\s+", text)
    for section in sections:
        if not section.strip():
            continue
        header = section.splitlines()[0].strip()
        cat_match = re.match(r"^([A-Za-z /&'-]+)\s*\([A-Z]+_", header)
        if cat_match:
            current_category = cat_match.group(1).strip()
        else:
            candidate = re.sub(r"\s*\(.*\)\s*$", "", header).strip()
            if re.match(r"^[A-Za-z][A-Za-z /&'-]*$", candidate) and "—" not in candidate:
                current_category = candidate

        for row in _parse_table(section):
            asset_id = row.get("asset_id", "") or row.get("id", "")
            if not re.match(r"^[A-Z]+_[A-Za-z]+_\d+$", asset_id):
                continue
            seeds.append(PropSeed(
                asset_id=asset_id,
                name=row.get("name", ""),
                category=current_category,
                category_dir=category_dir,
                description=row.get("description", ""),
                colors=row.get("primary_color", row.get("colors", "")),
                location=row.get("habitat", row.get("typical_location", "")),
                material=row.get("materials", row.get("material", "")),
                scale=row.get("scale", row.get("size", "")),
                animation=row.get("animation", ""),
                interactive=row.get("interactive", row.get("interactivity", "")),
                child_safe=row.get("child_safe", row.get("child_safety", "")),
                reusable=row.get("reusable", ""),
            ))

    return seeds
