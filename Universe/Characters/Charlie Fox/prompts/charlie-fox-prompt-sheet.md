# Charlie Fox — Prompt Reference Sheet

> **Version:** 1.0
> **Character:** Charlie Fox (Preschool, 5 years)
> **Style:** Cocomelon-inspired, Pixar-quality, bright colorful nursery world

---

## Character Card

| Attribute | Value |
|-----------|-------|
| Name | Charlie Fox |
| Species | Cute fox |
| Appearance | Orange fur, white chest and belly, fluffy tail with white tip, bright green eyes, scattered freckles across nose and cheeks, small black nose, pointed fox ears, pink inner ears, wide mischievous grin, small pointed canines when grinning |
| Default Outfit | Green hoodie, brown shorts, hiking boots |
| Style | Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| Signature Accessory | Fluffy tail with white tip (always present) |

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{name}` | Character name | Charlie Fox |
| `{species}` | Species description | Cute fox |
| `{appearance}` | Physical appearance | Orange fur, white chest and belly, fluffy tail with white tip, ... |
| `{outfit}` | Outfit description | Green hoodie, brown shorts, hiking boots |
| `{outfit_variant}` | Alternate outfit | Green puffy jacket with fur-lined hood |
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
| 1 | Neutral | Charlie Fox, Cute fox, orange fur, white chest and belly, fluffy tail with white tip, bright green eyes, scattered freckles across nose and cheeks, small black nose, pointed fox ears, pink inner ears, wide mischievous grin, small pointed canines when grinning, wearing green hoodie, brown shorts, hiking boots, neutral expression, portrait shot, Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
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
| 1 | Daily Outfit | Green hoodie, brown shorts, hiking boots |
| 2 | Winter Coat | Green puffy jacket with fur-lined hood |
| 3 | Rain Outfit | Orange raincoat, matching boots |
| 4 | Swimsuit | Green and orange trunks |
| 5 | Pajamas | Orange PJs with leaf prints |
| 6 | Birthday Outfit | Green outfit with explorer sash |
| 7 | Explorer Costume | Safari hat, binoculars, khaki vest |
| 8 | Sports Uniform | Green athletic wear |
| 9 | Halloween Costume | Adventurer fox costume |
| 10 | Christmas Outfit | Green sweater with fox print |
| 11 | Camper Outfit | Cozy flannel, warm scarf, campfire glow |

---

## Age Variant Prompts

Use template: `{age_description} version of {name}, {species}, {appearance}, wearing {outfit}, {style}`

| Age | Descriptor | Notes |
|-----|-----------|-------|
| Toddler (2-3) | toddler, smaller body, rounder features, oversized head, 2 years old | Smaller, wobbly on feet, oversized tail |
| Preschool (4-5) | preschool age, 5 years old | Current canonical design — curious explorer |
| Kindergarten (5-6) | kindergarten age, 5-6 years old, slightly taller | Taller, more confident, longer tail |

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

## Quality Checklist for Charlie Fox

- [ ] Character is instantly recognizable as Charlie Fox
- [ ] Green eyes are bright and expressive
- [ ] Green hoodie matches the signature look
- [ ] Fur is orange with white chest and belly (not solid orange)
- [ ] Fluffy tail with white tip is visible
- [ ] Pointed fox ears are perked and correctly positioned
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
*Version 1.0 — 2026-07-28*
