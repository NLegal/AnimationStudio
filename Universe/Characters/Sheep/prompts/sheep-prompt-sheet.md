# Sheep — Prompt Reference Sheet

> **Version:** 1.0
> **Character:** Sheep (Preschool, 4-5 years)
> **Style:** Pixar-quality, Cocomelon-inspired, bright colorful nursery world

---

## Character Card

| Attribute | Value |
|-----------|-------|
| Name | Sheep |
| Species | Cute sheep |
| Appearance | Fluffy white wool (soft and cloud-like), black face/ears/legs, gentle dark brown eyes, pointy medium ears sticking out to sides, short fluffy tail, round pillowy body, long gentle face, black soft nose, long thick eyelashes, blue scarf |
| Default Outfit | Blue scarf (no other clothes, wool is warm enough), blue slippers |
| Style | Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| Signature Feature | Fluffy white wool |

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{name}` | Character name | Sheep |
| `{species}` | Species description | Cute sheep |
| `{appearance}` | Physical appearance | Fluffy white wool, black face/ears/legs, ... |
| `{outfit}` | Outfit description | Blue scarf, blue slippers |
| `{outfit_variant}` | Alternate outfit | Blue wool coat with extra fluffy lining |
| `{expression}` | Expression name | Happy, Surprised, Sad |
| `{pose}` | Pose name | Standing, Jumping, Waving |
| `{angle}` | Camera angle | Front, 3/4, Profile, Back |
| `{age_description}` | Age variant descriptor | Lamb, smaller body, rounder features |
| `{lighting}` | Lighting condition | Golden hour, Morning, Night |
| `{style}` | Visual style | Pixar-quality, Cocomelon-inspired, ... |

---

## Expression Generation Prompts

Use template: `{name}, {species}, {appearance}, wearing {outfit}, {expression} expression, portrait shot, {style}`

| # | Expression | Prompt Snippet |
|---|------------|---------------|
| 1 | Neutral | Sheep, Cute sheep, fluffy white wool soft and cloud-like, black face/ears/legs, gentle dark brown eyes, pointy medium ears sticking out to sides, short fluffy tail, round pillowy body, long gentle face, black soft nose, long thick eyelashes, blue scarf, wearing blue scarf, blue slippers, neutral expression, portrait shot, Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
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
| 1 | Daily Outfit | Blue scarf, blue slippers (signature look, wool is warm enough) |
| 2 | Winter Coat | Blue wool coat with extra fluffy lining |
| 3 | Rain Outfit | Blue rain poncho with hood |
| 4 | Swimsuit | Blue swimsuit with ruffled trim |
| 5 | Pajamas | Blue cozy PJs with cloud pattern, sleep mask |
| 6 | Birthday Outfit | Blue dress with star pattern, party hat |
| 7 | Angel Costume | Blue sash, fluffy wings, halo |
| 8 | Cloud Costume | Blue and white fluffy cloud suit |
| 9 | Storyteller Costume | Blue shawl, reading glasses |
| 10 | Sports Uniform | Blue athletic wear (she tries her best) |
| 11 | Halloween Costume | Constellation costume (glow-in-the-dark stars) |
| 12 | Christmas Outfit | Blue sweater with snowflake pattern, star headband |

---

## Age Variant Prompts

Use template: `{age_description} version of {name}, {species}, {appearance}, wearing {outfit}, {style}`

| Age | Descriptor | Notes |
|-----|-----------|-------|
| Lamb (1-3) | lamb, smaller body, even fluffier, wobbly legs, 1-3 years old | Smaller, even fluffier, wobbly legs |
| Preschool (4-5) | preschool age, 4-5 years old | Current canonical design — gentle listener, peaceful soul |
| Kindergarten (5-6) | kindergarten age, 5-6 years old, slightly taller | Taller, still fluffy, wise beyond years |

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

## Quality Checklist for Sheep

- [ ] Character is instantly recognizable as Sheep
- [ ] Blue scarf is visible
- [ ] Dark brown eyes are gentle and expressive
- [ ] Wool is fluffy white (not gray or yellow)
- [ ] Face/ears/legs are black
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
