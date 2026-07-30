# Chicken — Prompt Reference Sheet

> **Version:** 1.0
> **Character:** Chicken (Preschool, 3-4 years)
> **Style:** Pixar-quality, Cocomelon-inspired, bright colorful nursery world

---

## Character Card

| Attribute | Value |
|-----------|-------|
| Name | Chicken |
| Species | Cute chicken |
| Appearance | Pure white feathers, bright red comb on top of head, small red wattle under chin, small bright orange eyes, small orange beak, orange legs and feet, white perky upright tail feathers, round fluffy plump body, small yellow bow on tail |
| Default Outfit | Yellow dress with white trim, small yellow bow on tail |
| Style | Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| Signature Feature | Red comb |

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{name}` | Character name | Chicken |
| `{species}` | Species description | Cute chicken |
| `{appearance}` | Physical appearance | Pure white feathers, bright red comb, ... |
| `{outfit}` | Outfit description | Yellow dress with white trim |
| `{outfit_variant}` | Alternate outfit | Yellow puffy coat with feather trim |
| `{expression}` | Expression name | Happy, Surprised, Sad |
| `{pose}` | Pose name | Standing, Jumping, Waving |
| `{angle}` | Camera angle | Front, 3/4, Profile, Back |
| `{age_description}` | Age variant descriptor | Chick, smaller body, rounder features |
| `{lighting}` | Lighting condition | Golden hour, Morning, Night |
| `{style}` | Visual style | Pixar-quality, Cocomelon-inspired, ... |

---

## Expression Generation Prompts

Use template: `{name}, {species}, {appearance}, wearing {outfit}, {expression} expression, portrait shot, {style}`

| # | Expression | Prompt Snippet |
|---|------------|---------------|
| 1 | Neutral | Chicken, Cute chicken, pure white feathers, bright red comb on top of head, small red wattle under chin, small bright orange eyes, small orange beak, orange legs and feet, white perky upright tail feathers, round fluffy plump body, small yellow bow on tail, wearing yellow dress with white trim, neutral expression, portrait shot, Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
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
| 1 | Daily Outfit | Yellow dress with white trim, small yellow bow on tail (signature look) |
| 2 | Winter Coat | Yellow puffy coat with feather trim, matching hat |
| 3 | Rain Outfit | Yellow rain bonnet with ribbons, matching coat |
| 4 | Swimsuit | Yellow one-piece with ruffle trim |
| 5 | Pajamas | Yellow PJs with egg pattern |
| 6 | Birthday Outfit | Yellow dress with "Sunny Birthday" sash |
| 7 | Nurse Costume | White nurse dress with yellow cross, nurse cap |
| 8 | Teacher Costume | Yellow cardigan, reading glasses, pointer |
| 9 | Farmer Costume | Yellow dress, straw hat |
| 10 | Sports Uniform | Yellow athletic wear, matching headband |
| 11 | Halloween Costume | Sunflower costume (yellow petals) |
| 12 | Christmas Outfit | Yellow and gold dress with star pattern, halo |

---

## Age Variant Prompts

Use template: `{age_description} version of {name}, {species}, {appearance}, wearing {outfit}, {style}`

| Age | Descriptor | Notes |
|-----|-----------|-------|
| Chick (1-3) | chick, smaller body, fluffy yellow down, tiny, 1-3 years old | Fluffy yellow ball, tiny, always cheeping |
| Preschool (3-4) | preschool age, 3-4 years old | Current canonical design — white feathers, responsible, early riser |
| Kindergarten (5-6) | kindergarten age, 5-6 years old, slightly taller | Taller, more feathers, schedule expert |

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

## Quality Checklist for Chicken

- [ ] Character is instantly recognizable as Chicken
- [ ] Red comb on head is visible
- [ ] Orange eyes are bright and alert
- [ ] Feathers are pure white (not gray or yellow)
- [ ] Yellow dress and bow are visible
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
