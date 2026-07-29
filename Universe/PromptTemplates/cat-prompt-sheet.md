# Cat — Prompt Reference Sheet

> **Version:** 1.0
> **Character:** Cat (Preschool, 3-4 years)
> **Style:** Pixar-quality, Cocomelon-inspired, bright colorful nursery world

---

## Character Card

| Attribute | Value |
|-----------|-------|
| Name | Cat |
| Species | Cute cat |
| Appearance | Soft orange fur with white patches on chest and paws, big bright green eyes, pointy triangular ears, long graceful tail curled at tip, heart-shaped face with delicate features, small pink triangle nose, light pink paw pads, tiny subtle fangs, light freckles across nose, purple ribbon on tail |
| Default Outfit | Purple sweater with cat pattern, matching leggings, lavender ballet flats |
| Style | Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| Signature Feature | Purple sweater, whiskers |

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{name}` | Character name | Cat |
| `{species}` | Species description | Cute cat |
| `{appearance}` | Physical appearance | Soft orange fur with white patches, ... |
| `{outfit}` | Outfit description | Purple sweater with cat pattern, leggings |
| `{outfit_variant}` | Alternate outfit | Purple puffy coat with lavender trim |
| `{expression}` | Expression name | Happy, Surprised, Sad |
| `{pose}` | Pose name | Standing, Jumping, Waving |
| `{angle}` | Camera angle | Front, 3/4, Profile, Back |
| `{age_description}` | Age variant descriptor | Toddler, smaller body, rounder features |
| `{lighting}` | Lighting condition | Golden hour, Morning, Night |
| `{style}` | Visual style | Pixar-quality, Cocomelon-inspired, ... |

---

## Expression Generation Prompts

Use template: `{name}, {species}, {appearance}, wearing {outfit}, {expression} expression, portrait shot, {style}`

| # | Expression | Prompt Snippet |
|---|------------|---------------|
| 1 | Neutral | Cat, Cute cat, soft orange fur with white patches on chest and paws, big bright green eyes, pointy triangular ears, long graceful tail curled at tip, heart-shaped face with delicate features, small pink triangle nose, light pink paw pads, tiny subtle fangs, light freckles across nose, purple ribbon on tail, wearing purple sweater with cat pattern, matching leggings, lavender ballet flats, neutral expression, portrait shot, Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| 2 | Happy | (same base) + happy expression, portrait shot |
| 3 | Very Happy | (same base) + very happy expression, portrait shot |
| 4 | Laughing | (same base) + laughing expression, portrait shot |
| 5 | Giggling | (same base) + giggling expression, portrait shot |
| 6 | Smiling | (same base) + smiling expression, portrait shot |
| 7 | Excited | (same base) + excited expression, portrait shot |
| 8 | Surprised | (same base) + surprised expression, portrait shot |
| 9 | Confused | (same base) + confused expression, portrait shot |
| 10 | Thinking | (same base) + thinking expression, portrait shot |
| 11 | Curious | (same base) + curious expression, portrait shot |
| 12 | Sleepy | (same base) + sleepy expression, portrait shot |
| 13 | Yawning | (same base) + yawning expression, portrait shot |
| 14 | Crying | (same base) + crying expression, portrait shot |
| 15 | Sad | (same base) + sad expression, portrait shot |
| 16 | Scared | (same base) + scared expression, portrait shot |
| 17 | Embarrassed | (same base) + embarrassed expression, portrait shot |
| 18 | Proud | (same base) + proud expression, portrait shot |
| 19 | Determined | (same base) + determined expression, portrait shot |
| 20 | Singing | (same base) + singing expression, portrait shot |
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
| 4 | Jumping | Jumping pose, full body |
| 5 | Skipping | Skipping pose, full body |
| 6 | Sitting | Sitting pose, full body |
| 7 | Kneeling | Kneeling pose, full body |
| 8 | Dancing | Dancing pose, full body |
| 9 | Sleeping | Sleeping pose, full body |
| 10 | Reading | Reading pose, full body |
| 11 | Writing | Writing pose, full body |
| 12 | Pointing | Pointing pose, full body |
| 13 | Clapping | Clapping pose, full body |
| 14 | Waving | Waving pose, full body |
| 15 | Hugging | Hugging pose, full body |
| 16 | Holding Hands | Holding hands pose, full body |
| 17 | Playing | Playing pose, full body |
| 18 | Swimming | Swimming pose, full body |
| 19 | Flying | Flying pose, full body |
| 20 | Sliding | Sliding pose, full body |

---

## Outfit Generation Prompts

Use template: `{name}, {species}, {appearance}, wearing {outfit_variant}, standing, front view, full body, {style}`

| # | Outfit | Description |
|---|--------|-------------|
| 1 | Daily Outfit | Purple sweater with cat pattern, matching leggings, lavender ballet flats (signature look) |
| 2 | Winter Coat | Purple puffy coat with lavender trim, matching earmuffs |
| 3 | Rain Outfit | Lavender raincoat with hood, matching boots |
| 4 | Swimsuit | Purple one-piece with white lace trim |
| 5 | Pajamas | Lavender PJs with paintbrush print, silk sleep mask |
| 6 | Birthday Outfit | Purple dress with watercolor rainbow sash |
| 7 | Artist Costume | Purple beret, smock with paint splatters, palette |
| 8 | Ballerina Costume | Purple tutu, ballet slippers, tiara |
| 9 | Princess Costume | Lavender princess gown with cat-ear tiara |
| 10 | Sports Uniform | Purple athletic wear, matching headband |
| 11 | Halloween Costume | Butterfly wings over purple dress |
| 12 | Christmas Outfit | Deep purple dress with silver star pattern, sparkly scarf |

---

## Age Variant Prompts

Use template: `{age_description} version of {name}, {species}, {appearance}, wearing {outfit}, {style}`

| Age | Descriptor | Notes |
|-----|-----------|-------|
| Toddler (2-3) | toddler, smaller body, rounder features, oversized head, 2 years old | Smaller proportions, wobbly, still graceful |
| Preschool (3-4) | preschool age, 3-4 years old | Current canonical design — quiet artist, keen observer |
| Kindergarten (5-6) | kindergarten age, 5-6 years old, slightly taller | Taller, more confident, skills refined |

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

## Quality Checklist for Cat

- [ ] Character is instantly recognizable as Cat
- [ ] Purple sweater is visible
- [ ] Green eyes are bright and expressive
- [ ] Fur is soft orange with white patches (not solid orange)
- [ ] Tail is visible and expressive with purple ribbon
- [ ] Proportions are toddler-like (not adult)
- [ ] Expression matches the requested emotion
- [ ] No anatomical deformities (extra limbs, missing features)
- [ ] No watermarks, text, or logos
- [ ] Background is appropriate and child-friendly
- [ ] Lighting is soft and warm
- [ ] Style matches Cocomelon-inspired aesthetic
- [ ] Age variant matches requested age group
- [ ] Outfit matches the requested variant description
- [ ] Character fills the frame appropriately for the type (portrait, full body)

---

*Generated for AI Nursery Rhyme Studio — Universe Library*
*Version 1.0 — 2026-07-29*
