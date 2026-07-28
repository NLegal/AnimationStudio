# Prompt Templates — Universe Library

> **Part of the AI Nursery Rhyme Studio Universe Library**
> **Version 1.0**

---

## Overview

The Prompt Templates system provides reusable, parameterized prompt templates for generating character-consistent images using AI image generation models (Flux, SDXL, etc.). Every character in the universe has a set of templates stored in `Universe/Characters/<Character Name>/prompts/templates.json`.

The templates are consumed by the **Prompt Builder** module (`src/prompt_builder/`) which substitutes variables at generation time.

---

## How to Use Templates

### For Direct Image Generation

Use the template format with your chosen image generation model:

```
Lily Bunny, Cute bunny rabbit, soft white fur, large bright green eyes, small pink nose, long floppy ears with blue bow, round rosy cheeks, cute buck teeth, light pink paw pads, wearing light pink dress with white collar, happy expression, portrait shot, Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors
```

### Via the Prompt Builder (Programmatic)

```python
from prompt_builder import PromptBuilder

builder = PromptBuilder()
prompt = builder.build(
    character="Lily Bunny",
    template_type="expression",
    variables={
        "expression": "happy",
        "outfit": "light pink dress with white collar"
    }
)
```

### Via the CLI

```bash
nursery prompt build lily-bunny --type expression --var expression=happy
```

---

## Template Variable Reference

| Variable | Description | Source |
|----------|-------------|--------|
| `{name}` | Character's full name | bio.md |
| `{species}` | Species description | bio.md |
| `{appearance}` | Physical appearance details | bio.md → Appearance section |
| `{outfit}` | Current outfit description | bio.md → Clothing section |
| `{outfit_variant}` | Alternate outfit for outfit-specific generation | bio.md → Clothing section |
| `{expression}` | Expression name (see Expression Library) | PHASE1.md Expression List |
| `{pose}` | Pose name (see Pose Library) | PHASE1.md Pose List |
| `{angle}` | Camera/view angle | reference/rotation sheets |
| `{age_description}` | Age variant descriptor (toddler, preschool, etc.) | bio.md → Age Progression |
| `{lighting}` | Lighting condition name | Lighting Library |
| `{style}` | Visual style string | character's style definition |

---

## Template Types

| Type | Purpose | Variables Required |
|------|---------|-------------------|
| `reference` | Multi-angle reference sheets | name, species, appearance, outfit, angle, style |
| `expression` | Expression portrait shots | name, species, appearance, outfit, expression, style |
| `pose` | Full-body pose images | name, species, appearance, outfit, pose, style |
| `outfit` | Outfit variant showcase | name, species, appearance, outfit_variant, style |
| `rotation` | Turnaround/model sheet frames | name, species, appearance, outfit, angle, style |
| `age_variant` | Age progression images | age_description, name, species, appearance, outfit, style |
| `lighting` | Lighting condition variants | name, species, appearance, outfit, lighting, style |

---

## Adding a New Character's Templates

1. Create the character directory:
   ```
   Universe/Characters/<Character Name>/prompts/
   ```

2. Create `templates.json` based on the template from an existing character:
   ```bash
   # Clone Lily Bunny's templates as a starting point
   cp Universe/Characters/Lily\ Bunny/prompts/templates.json \
      "Universe/Characters/<Character Name>/prompts/templates.json"
   ```

3. Update the template fields:
   - `character.name` — Character's full name
   - `character.species` — Species description
   - `character.appearance` — Physical appearance (from bio.md Appearance section)
   - `character.default_outfit` — Default/signature outfit
   - `character.style` — Visual style (keep consistent with universe style)
   - `character.negative_prompt` — Character-specific negative additions

4. Validate the JSON:
   ```bash
   python3 -c "import json; json.loads(open('Universe/Characters/<Name>/prompts/templates.json').read())"
   ```

5. Create a human-readable prompt sheet:
   ```
   Universe/PromptTemplates/<character-name>-prompt-sheet.md
   ```

---

## How the Prompt Builder Consumes Templates

The Prompt Builder (`src/prompt_builder/`) reads `templates.json` at runtime:

1. Loads character data and templates from JSON
2. Validates that requested template type exists
3. Substitutes variables using Python `str.format()` pattern
4. Appends the common style string and negative prompt
5. Returns the final prompt string

### Template Resolution Order

1. Character-specific template in `templates.json`
2. If not found, falls back to generic template
3. Variables not provided are left as `{variable_name}` placeholders

---

## Negative Prompt Standards

Each character's `templates.json` includes a `negative_prompt` field. The common negative prompt is also documented in `Universe/NegativePrompt/standards.md`.

Always append the negative prompt when generating images:

```
low quality, blurry, deformed, mutated, duplicate, extra arms, extra legs,
extra fingers, missing fingers, cross eyed, cropped, watermark, text, logo,
dark, scary, horror, realistic skin, adult, violence, blood, ugly, noise,
anime, watercolor, 3D render, photorealistic, sketch, line art, black and
white, grayscale, low contrast, oversaturated
```

---

## Directory Structure

```
Universe/
├── Characters/
│   └── Lily Bunny/
│       └── prompts/
│           └── templates.json       # Machine-readable templates
├── PromptTemplates/
│   ├── README.md                    # This file — system documentation
│   ├── lily-bunny-prompt-sheet.md   # Human-readable reference
│   └── ...                          # More character prompt sheets
└── NegativePrompt/
    └── standards.md                 # Negative prompt standards
```

---

*Part of the AI Nursery Rhyme Studio — Universe Library*
*Version 1.0 — 2026-07-28*
