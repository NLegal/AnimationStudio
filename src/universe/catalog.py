"""Universe catalog — structured seeds from the Universe/World/Assets markdown.

Parses the Phase 1/2/3 world-building documents (character bios, environment
bibles, and prop/asset indexes) into lightweight dataclasses that drive both
seeding (``src.universe.seed``) and batch generation (``src.universe.
batch_generator``) without hand-maintaining a second list of the universe.
"""

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
    prompt: str = ""
    negative_prompt: str = ""

    @property
    def slug(self) -> str:
        return _slugify(self.asset_id)


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
      - ``Assets/*/INDEX.md``     (``| ID | Name | Description | ... |`` tables)
    """
    seeds: list[PropSeed] = []
    world_index = Path(world_dir) / "Props" / "INDEX.md"
    if world_index.is_file():
        seeds.extend(_parse_prop_entries(world_index))

    assets_root = Path(assets_dir)
    if assets_root.is_dir():
        for index in sorted(assets_root.glob("*/INDEX.md")):
            seeds.extend(_parse_prop_table_index(index))

    seeds.sort(key=lambda s: s.asset_id)
    return seeds


def _parse_prop_entries(index_path: Path) -> list[PropSeed]:
    """Parse ``World/Props/INDEX.md`` style prop entries."""
    text = index_path.read_text(encoding="utf-8")
    seeds: list[PropSeed] = []
    current_category = ""
    sections = re.split(r"(?m)^#\s+", text)
    for section in sections:
        if not section.strip():
            continue
        header = section.splitlines()[0].strip()
        # Section header: "Furniture (PROP_Furniture_001–020)"
        cat_match = re.match(r"^([^(]+)\s*\(PROP_\w+_\d+", header)
        if cat_match:
            current_category = cat_match.group(1).strip()

        for entry in re.finditer(
            r"^##\s+(PROP_[A-Za-z]+_\d+)\s+[—\-–]\s+(.+)$",
            section, re.MULTILINE,
        ):
            asset_id = entry.group(1)
            name = entry.group(2).strip()
            body = section[entry.end():]
            cut = re.search(r"^\s*##\s+PROP_", body, re.MULTILINE)
            body = body[: cut.start()] if cut else body

            desc = ""
            for line in body.splitlines():
                line = line.strip()
                if line and not line.startswith(("-", "|")):
                    desc = line
                    break

            colors = ""
            loc = ""
            for line in body.splitlines():
                if "**Colors:**" in line:
                    colors = line.split("**Colors:**", 1)[1].strip()
                elif "**Typical Location:**" in line:
                    loc = line.split("**Typical Location:**", 1)[1].strip()

            seeds.append(PropSeed(
                asset_id=asset_id,
                name=name,
                category=current_category,
                description=desc,
                colors=colors,
                location=loc,
            ))

    return seeds


def _parse_prop_table_index(index_path: Path) -> list[PropSeed]:
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

        for row in _parse_table(section):
            asset_id = row.get("asset_id", "")
            if not re.match(r"^[A-Z]+_[A-Za-z]+_\d+$", asset_id):
                continue
            seeds.append(PropSeed(
                asset_id=asset_id,
                name=row.get("name", ""),
                category=current_category,
                description=row.get("description", ""),
                colors=row.get("primary_color", ""),
                location=row.get("habitat", row.get("typical_location", "")),
            ))

    return seeds
