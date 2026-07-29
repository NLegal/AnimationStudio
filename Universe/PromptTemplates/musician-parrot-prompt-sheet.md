# Musician Parrot — Prompt Reference Sheet

> **Version:** 1.0
> **Character:** Musician Parrot (Adult)
> **Style:** Cocomelon-inspired, Pixar-quality, bright colorful nursery world

---

## Character Card

| Attribute | Value |
|-----------|-------|
| Name | Musician Parrot |
| Species | Parrot (red, blue, and yellow feathers) |
| Appearance | Bright red body feathers, blue and yellow wings, yellow head crest, curved black beak, sparkling black eyes with white ring, long graduated tail with blue tips, broad colorful wings, round face with white face patch, dark gray feet |
| Default Outfit | Tropical shirt (red/yellow/blue pattern), colorful feathered hat, music note pendant |
| Style | Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| Signature Accessory | Colorful feathered hat, music note pendant |

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{name}` | Character name | Musician Parrot |
| `{species}` | Species description | Parrot (red, blue, and yellow feathers) |
| `{appearance}` | Physical appearance | Bright red body feathers, blue and yellow wings, ... |
| `{outfit}` | Outfit description | Tropical shirt, feathered hat, music pendant |
| `{outfit_variant}` | Alternate outfit | Sparkly red jacket, bow tie |
| `{expression}` | Expression name | Happy, Surprised, Sad |
| `{pose}` | Pose name | Standing, Flying, Singing |
| `{angle}` | Camera angle | Front, 3/4, Profile, Back |
| `{lighting}` | Lighting condition | Golden hour, Morning, Night |
| `{style}` | Visual style | Pixar-quality, Cocomelon-inspired, ... |

---

## Expression Generation Prompts

Use template: `{name}, {species}, {appearance}, wearing {outfit}, {expression} expression, portrait shot, {style}`

| # | Expression | Prompt Snippet |
|---|------------|---------------|
| 1 | Neutral | Musician Parrot, Parrot (red, blue, and yellow feathers), bright red body feathers, blue and yellow wings, yellow head crest, curved black beak, sparkling black eyes with white ring, long graduated tail with blue tips, broad colorful wings, round face with white face patch, dark gray feet, wearing tropical shirt (red/yellow/blue pattern), colorful feathered hat, music note pendant, neutral expression, portrait shot, Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| 2 | Happy | (same base) + happy expression, portrait shot |
| 3 | Very Happy | (same base) + very happy expression, portrait shot |
| 4 | Laughing | (same base) + laughing expression, portrait shot |
| 5 | Giggling | (same base) + giggling expression, portrait shot |
| 6 | Smiling | (same base) + smiling expression, portrait shot |
| 7 | Excited | (same base) + excited expression, crest raised, portrait shot |
| 8 | Surprised | (same base) + surprised expression, portrait shot |
| 9 | Confused | (same base) + confused expression, head tilted, portrait shot |
| 10 | Thinking | (same base) + thinking expression, portrait shot |
| 11 | Curious | (same base) + curious expression, portrait shot |
| 12 | Sleepy | (same base) + sleepy expression, portrait shot |
| 13 | Yawning | (same base) + yawning expression, beak open, portrait shot |
| 14 | Crying | (same base) + crying expression, portrait shot |
| 15 | Sad | (same base) + sad expression, portrait shot |
| 16 | Scared | (same base) + scared expression, portrait shot |
| 17 | Embarrassed | (same base) + embarrassed expression, portrait shot |
| 18 | Proud | (same base) + proud expression, portrait shot |
| 19 | Determined | (same base) + determined expression, portrait shot |
| 20 | Singing | (same base) + singing expression, beak open, portrait shot |
| 21 | Whistling | (same base) + whistling expression, portrait shot |
| 22 | Blowing Kiss | (same base) + blowing kiss expression, portrait shot |
| 23 | Winking | (same base) + winking expression, portrait shot |

---

## Pose Generation Prompts

Use template: `{name}, {species}, {appearance}, wearing {outfit}, {pose} pose, full body, {style}`

| # | Pose | Description |
|---|------|-------------|
| 1 | Standing | Standing pose, full body |
| 2 | Walking | Walking pose, full body |
| 3 | Running | Running pose, full body |
| 4 | Hopping | Hopping pose, full body |
| 5 | Jumping | Jumping pose, full body |
| 6 | Sitting | Sitting pose, full body |
| 7 | Perching | Perching on a stand, full body |
| 8 | Dancing | Dancing pose, full body |
| 9 | Sleeping | Sleeping pose, head tucked, full body |
| 10 | Reading | Reading music sheets, full body |
| 11 | Writing | Writing a song, full body |
| 12 | Pointing | Pointing pose, wing extended, full body |
| 13 | Clapping | Clapping pose, wings together, full body |
| 14 | Waving | Waving pose, wing raised, full body |
| 15 | Hugging | Hugging pose, wings open, full body |
| 16 | Holding Hands | Holding wings with friend, full body |
| 17 | Playing Guitar | Playing guitar pose, full body |
| 18 | Flying | Flying pose, wings spread, full body |
| 19 | Singing | Singing pose, beak open, full body |
| 20 | Gliding | Gliding pose, full body |

---

## Outfit Generation Prompts

Use template: `{name}, {species}, {appearance}, wearing {outfit_variant}, standing, front view, full body, {style}`

| # | Outfit | Description |
|---|--------|-------------|
| 1 | Daily Outfit | Tropical shirt (red/yellow/blue pattern), feathered hat, music pendant (signature look) |
| 2 | Performance | Sparkly red jacket, feathered hat, bow tie |
| 3 | Casual | Yellow linen shirt, lightweight pants |
| 4 | Winter Outfit | Cozy orange sweater, scarf |
| 5 | Rain Outfit | Bright yellow slicker, feathered rain hat |
| 6 | Pajamas | Bright tropical PJs, sleep mask with music notes |
| 7 | Guitar Teacher | Casual button-up, guitar strap |
| 8 | Drum Session | Headband, sleeveless shirt |
| 9 | Music Class | Sky blue polo with music note pin |
| 10 | Halloween Costume | Dressed as his favorite rock star |
| 11 | Christmas Outfit | Red and green tropical shirt, Santa hat |

---

## Age Variant Prompts

*Skipped — Musician Parrot is a fixed adult character.*

---

## Rotation Sheet Prompts

Use template: `{name}, {species}, {appearance}, wearing {outfit}, {angle} view, {style}`

| Angle | Description |
|-------|-------------|
| Front | Front view, looking at camera |
| 3/4 | Three-quarter view |
| Profile | Profile view (side) |
| Back | Back view |
| Top | Top-down view |
| Bottom | Bottom-up view (low angle) |

---

## Lighting Variant Prompts

Use template: `{name}, {species}, {appearance}, wearing {outfit}, {lighting} lighting, {style}`

| Lighting | Description |
|----------|-------------|
| Morning | Soft morning lighting, warm tones |
| Afternoon | Bright afternoon lighting |
| Golden Hour | Warm golden hour glow |
| Night | Night lighting, gentle moonlight |
| Moonlight | Cool moonlight illumination |
| Rain | Overcast, rainy lighting |
| Snow | Bright snowy lighting |
| Cloudy | Soft diffused cloudy lighting |
| Indoor | Warm indoor lighting |
| Birthday Lights | Festive colorful lighting |
| Christmas Lights | Warm twinkling holiday lights |

---

## Common Negative Prompt

```
low quality, blurry, deformed, mutated, duplicate, extra arms, extra legs,
extra fingers, missing fingers, cross eyed, cropped, watermark, text, logo,
dark, scary, horror, realistic skin, adult, violence, blood, ugly, noise,
anime, watercolor, 3D render, photorealistic, sketch, line art, black and
white, grayscale, low contrast, oversaturated
```

---

## Quality Checklist for Musician Parrot

- [ ] Character is instantly recognizable as Musician Parrot
- [ ] Colorful feathered hat and music pendant are visible
- [ ] Feather colors are vibrant red, blue, and yellow
- [ ] Yellow head crest is visible and expressive
- [ ] Tropical shirt matches the signature look
- [ ] Beak is curved and black
- [ ] Proportions are parrot-like (lively, colorful)
- [ ] Expression matches the requested emotion
- [ ] No anatomical deformities (extra wings, missing features)
- [ ] No watermarks, text, or logos
- [ ] Background is appropriate and child-friendly (stage or music room)
- [ ] Lighting is soft and warm
- [ ] Style matches Cocomelon-inspired aesthetic
- [ ] Long tail with blue tips is visible
- [ ] Character fills the frame appropriately for the type (portrait, full body)

---

*Generated for AI Nursery Rhyme Studio — Universe Library*
*Version 1.0 — 2026-07-29*
