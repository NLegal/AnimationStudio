# Ben Bear — Prompt Reference Sheet

> **Version:** 1.0
> **Character:** Ben Bear (Preschool, 5 years)
> **Style:** Cocomelon-inspired, Pixar-quality, bright colorful nursery world

---

## Character Card

| Attribute | Value |
|-----------|-------|
| Name | Ben Bear |
| Species | Cute teddy bear |
| Appearance | Warm caramel brown fur, large bright blue eyes, small black nose, round teddy-bear ears, chubby cheeks, light brown paw pads, cute small white teeth, dimples when smiling |
| Default Outfit | Blue denim overalls, yellow striped T-shirt, red sneakers |
| Style | Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| Signature Accessory | Blue baseball cap (occasionally) |

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{name}` | Character name | Ben Bear |
| `{species}` | Species description | Cute teddy bear |
| `{appearance}` | Physical appearance | Warm caramel brown fur, large bright blue eyes, ... |
| `{outfit}` | Outfit description | Blue denim overalls, yellow striped T-shirt, red sneakers |
| `{outfit_variant}` | Alternate outfit | Blue puffy coat with faux fur hood |
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
| 1 | Neutral | Ben Bear, Cute teddy bear, warm caramel brown fur, large bright blue eyes, small black nose, round teddy-bear ears, chubby cheeks, light brown paw pads, cute small white teeth, dimples when smiling, wearing blue denim overalls, yellow striped T-shirt, red sneakers, neutral expression, portrait shot, Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
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
| 1 | Daily Outfit | Blue denim overalls, yellow striped T-shirt, red sneakers |
| 2 | Winter Coat | Blue puffy coat with faux fur hood, matching mittens |
| 3 | Rain Outfit | Yellow raincoat, matching boots |
| 4 | Swimsuit | Blue trunks with white stripes |
| 5 | Pajamas | Light blue PJs with honey pot print |
| 6 | Birthday Outfit | Blue outfit with gold star sash |
| 7 | Builder Costume | Hard hat, tool belt |
| 8 | Doctor Costume | White coat with blue trim, toy stethoscope |
| 9 | Sports Uniform | Blue and white athletic wear |
| 10 | Halloween Costume | Builder bear costume |
| 11 | Christmas Outfit | Red and green sweater with reindeer pattern |
| 12 | Explorer Costume | Safari hat, backpack, khaki vest |

---

## Age Variant Prompts

Use template: `{age_description} version of {name}, {species}, {appearance}, wearing {outfit}, {style}`

| Age | Descriptor | Notes |
|-----|-----------|-------|
| Toddler (2-3) | toddler, smaller body, rounder features, oversized head, 2 years old | Rounder, waddles, smaller proportions |
| Preschool (4-5) | preschool age, 5 years old | Current canonical design — calm builder |
| Kindergarten (5-6) | kindergarten age, 5-6 years old, slightly taller | Taller, more confident posture |

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

## Quality Checklist for Ben Bear

- [ ] Character is instantly recognizable as Ben Bear
- [ ] Blue eyes are bright and expressive
- [ ] Blue denim overalls and yellow striped T-shirt match the signature look
- [ ] Fur is warm caramel brown (not orange or dark brown)
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
- [ ] Teddy-bear ears are round and correctly positioned

---

*Generated for AI Nursery Rhyme Studio — Universe Library*
*Version 1.0 — 2026-07-28*
