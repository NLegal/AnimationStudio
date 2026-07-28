# Negative Prompt Standards

> **Version:** 1.0
> **Applies to:** All image generation in the AI Nursery Rhyme Studio

---

## Common Negative Prompt

This negative prompt is applied to **all** image generation requests:

```
low quality, blurry, deformed, mutated, duplicate, extra arms, extra legs,
extra fingers, missing fingers, cross eyed, cropped, watermark, text, logo,
dark, scary, horror, realistic skin, adult, violence, blood, ugly, noise,
anime, watercolor, 3D render, photorealistic, sketch, line art, black and
white, grayscale, low contrast, oversaturated
```

---

## Categories

### Quality Exclusions

These prevent low-quality or artifact-ridden outputs:

| Term | Reason |
|------|--------|
| low quality | Avoids basic quality degradation |
| blurry | Prevents out-of-focus images |
| deformed | Avoids anatomical distortions |
| mutated | Prevents unnatural character variations |
| duplicate | Avoids repeated elements |
| ugly | General aesthetic quality gate |
| noise | Prevents grainy or noisy images |

### Anatomical Corrections

These prevent common AI generation anatomical errors:

| Term | Reason |
|------|--------|
| extra arms | Standard anatomical correction |
| extra legs | Standard anatomical correction |
| extra fingers | Standard anatomical correction |
| missing fingers | Standard anatomical correction |
| cross eyed | Prevents eye alignment issues |

### Artifact Removal

These remove generation artifacts and unwanted elements:

| Term | Reason |
|------|--------|
| cropped | Prevents oddly cropped compositions |
| watermark | Removes stock image watermarks |
| text | Prevents garbled text in images |
| logo | Removes unwanted branding |

### Style Exclusions

These prevent generation in incompatible art styles:

| Term | Reason |
|------|--------|
| anime | Our style is Cocomelon-inspired, not anime |
| watercolor | Our style is digital render, not traditional media |
| 3D render | Avoids cold/plastic 3D look (we want warm Pixar-quality) |
| photorealistic | Characters are stylized, not realistic |
| sketch | Prevents unfinished sketch-like outputs |
| line art | Prevents flat line art without color |
| black and white | Color is essential for children's content |
| grayscale | Same as above |
| low contrast | Prevents washed-out images |
| oversaturated | Prevents color bleeding |

### Child Safety Exclusions

These are **mandatory** — they protect the child-friendly nature of the content:

| Term | Reason |
|------|--------|
| dark | Child-friendly content should be bright |
| scary | Content must not frighten children |
| horror | Content must not frighten children |
| realistic skin | Characters are stylized cartoon animals |
| adult | Content is exclusively for children |
| violence | Zero tolerance for violent content |
| blood | Zero tolerance for violent content |

---

## Per-Character Negative Additions

Each character may have additional negative terms specific to their design. These are stored in the character's `templates.json` under `negative_prompt`.

### Example: Lily Bunny

```json
{
  "negative_prompt": "low quality, blurry, deformed, mutated, duplicate, extra arms, extra legs, extra fingers, missing fingers, cross eyed, cropped, watermark, text, logo, dark, scary, horror, realistic skin, adult, violence, blood, ugly, noise, anime, watercolor, 3D render, photorealistic, sketch, line art, black and white, grayscale, low contrast, oversaturated"
}
```

### When Adding Character-Specific Negatives

1. Copy the common negative prompt
2. Add terms that prevent issues specific to that character's design
3. Keep child safety exclusions at the top
4. Document the reason for any additions

---

## Usage

### In Prompt Templates

Each character's `templates.json` includes the negative prompt as a field. The Prompt Builder appends it automatically.

### In Manual Generation

Always append the common negative prompt to every image generation request:

```
[positive prompt] --neg [negative prompt]
```

### Via CLI

```bash
nursery generate lily-bunny \
  --type expression \
  --var expression=happy \
  --negative "$(cat Universe/NegativePrompt/standards.md | grep -A 100 'Common Negative Prompt' | tail -n +3 | head -8)"
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-28 | Initial negative prompt standards from PHASE1.md |

---

*Part of the AI Nursery Rhyme Studio — Universe Library*
*Version 1.0 — 2026-07-28*
