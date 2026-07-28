"""Automated validation tests for Lily Bunny's character bio (bio.md).

Tests that the bio document is well-formed, contains all required sections
and fields, and is ready for downstream consumption by the Generation Engine
and Prompt Builder.
"""

from pathlib import Path


BIO_PATH = Path("Universe/Characters/Lily Bunny/bio.md")

REQUIRED_SECTIONS = [
    "Basic Information",
    "Appearance",
    "Clothing",
    "Personality",
    "Skills",
    "Weaknesses",
    "Catchphrases",
    "Relationships",
    "Emotion Matrix",
    "Age Progression",
    "Version History",
]

REQUIRED_FIELDS = [
    "Name:",
    "Species:",
    "Gender:",
    "Age:",
    "Favorite Color:",
    "Eye Color:",
    "Fur Color:",
]


def _read_bio() -> str:
    """Read the bio.md file and return its content as a string."""
    return BIO_PATH.read_text(encoding="utf-8")


def test_bio_file_exists():
    """Universe/Characters/Lily Bunny/bio.md exists."""
    assert BIO_PATH.exists(), f"bio.md not found at {BIO_PATH}"


def test_bio_has_required_sections():
    """bio.md contains all required markdown section headers."""
    content = _read_bio()
    for section in REQUIRED_SECTIONS:
        assert f"## {section}" in content, (
            f"Required section '## {section}' not found in bio.md"
        )


def test_bio_has_required_fields():
    """Name, Species, Gender, Age, Favorite Color, Eye Color, Fur Color fields present."""
    content = _read_bio()
    for field in REQUIRED_FIELDS:
        assert f"**{field}" in content or f"- **{field}" in content, (
            f"Required field '{field}' not found in bio.md"
        )


def test_bio_has_catchphrases():
    """At least 3 catchphrases are documented."""
    content = _read_bio()
    # Count numbered lines under Catchphrases section
    catchphrase_section = content.split("## Catchphrases")[1].split("##")[0]
    count = sum(1 for line in catchphrase_section.strip().split("\n")
                if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10.")))
    assert count >= 3, f"Expected at least 3 catchphrases, found {count}"


def test_bio_has_relationships():
    """At least 5 named relationships are documented."""
    content = _read_bio()
    rel_section = content.split("## Relationships")[1].split("##")[0]
    # Count table rows (lines starting with |)
    rows = [line for line in rel_section.split("\n")
            if line.strip().startswith("|") and "---" not in line]
    # Skip header and separator rows
    data_rows = [r for r in rows if r.count("|") >= 3 and "Name" not in r and "---" not in r]
    assert len(data_rows) >= 5, f"Expected at least 5 relationships, found {len(data_rows)}"


def test_bio_has_emotion_matrix():
    """At least 5 emotion entries are documented."""
    content = _read_bio()
    em_section = content.split("## Emotion Matrix")[1].split("##")[0]
    rows = [line for line in em_section.split("\n")
            if line.strip().startswith("|") and "---" not in line]
    data_rows = [r for r in rows if r.count("|") >= 2 and "Situation" not in r and "---" not in r]
    assert len(data_rows) >= 5, f"Expected at least 5 emotion entries, found {len(data_rows)}"


def test_bio_has_age_progression():
    """Toddler, preschool, kindergarten entries present."""
    content = _read_bio()
    assert "Toddler" in content, "Age progression entry 'Toddler' not found"
    assert "Preschool" in content, "Age progression entry 'Preschool' not found"
    assert "Kindergarten" in content, "Age progression entry 'Kindergarten' not found"


def test_bio_has_outfits():
    """At least 8 outfit variants are described."""
    content = _read_bio()
    cloth_section = content.split("## Clothing")[1].split("##")[0]
    rows = [line for line in cloth_section.split("\n")
            if line.strip().startswith("|") and "---" not in line]
    data_rows = [r for r in rows if r.count("|") >= 2 and "Variant" not in r and "---" not in r]
    assert len(data_rows) >= 8, f"Expected at least 8 outfit variants, found {len(data_rows)}"


def test_bio_version_history():
    """Versions recorded."""
    content = _read_bio()
    assert "v1.0" in content, "Version history 'v1.0' not found"
    assert "2026" in content, "Version history date not found"
