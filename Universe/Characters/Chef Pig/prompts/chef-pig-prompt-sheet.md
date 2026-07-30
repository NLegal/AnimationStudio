# Chef Pig — Prompt Reference Sheet

> **Version:** 1.0
> **Character:** Chef Pig (Adult)
> **Style:** Cocomelon-inspired, Pixar-quality, bright colorful nursery world

---

## Character Card

| Attribute | Value |
|-----------|-------|
| Name | Chef Pig |
| Species | Pig (light pink) |
| Appearance | Light pink skin all over, bright cheerful brown eyes, round expressive snout, large floppy pink ears, small curly pink tail, round soft friendly body, wide joyful smile |
| Default Outfit | White chef jacket, red apron, tall white chef hat, striped chef pants |
| Style | Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| Signature Accessory | Tall white chef hat, red apron |

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{name}` | Character name | Chef Pig |
| `{species}` | Species description | Pig (light pink) |
| `{appearance}` | Physical appearance | Light pink skin, bright cheerful brown eyes, ... |
| `{outfit}` | Outfit description | White chef jacket, red apron, tall chef hat |
| `{outfit_variant}` | Alternate outfit | Warm orange polo shirt, khaki pants |
| `{expression}` | Expression name | Happy, Surprised, Sad |
| `{pose}` | Pose name | Standing, Cooking, Tasting |
| `{angle}` | Camera angle | Front, 3/4, Profile, Back |
| `{lighting}` | Lighting condition | Golden hour, Morning, Night |
| `{style}` | Visual style | Pixar-quality, Cocomelon-inspired, ... |

---

## Expression Generation Prompts

Use template: `{name}, {species}, {appearance}, wearing {outfit}, {expression} expression, portrait shot, {style}`

| # | Expression | Prompt Snippet |
|---|------------|---------------|
| 1 | Neutral | Chef Pig, Pig (light pink), light pink skin all over, bright cheerful brown eyes, round expressive snout, large floppy pink ears, small curly pink tail, round soft friendly body, wide joyful smile, wearing white chef jacket, red apron, tall white chef hat, striped chef pants, neutral expression, portrait shot, Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
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
| 13 | Yawning | (same base) + yawning expression, snout open, portrait shot |
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
| 5 | Waddling | Waddling pose, full body |
| 6 | Sitting | Sitting pose, full body |
| 7 | Kneeling | Kneeling pose, full body |
| 8 | Dancing | Dancing pose, full body |
| 9 | Sleeping | Sleeping pose, full body |
| 10 | Reading | Reading a recipe book, full body |
| 11 | Writing | Writing a recipe, full body |
| 12 | Pointing | Pointing at ingredients pose, full body |
| 13 | Clapping | Clapping pose, trotters together, full body |
| 14 | Waving | Waving pose, trotter raised, full body |
| 15 | Hugging | Hugging pose, arms open, full body |
| 16 | Holding Hands | Holding trotters with friend, full body |
| 17 | Cooking | Cooking at the stove pose, full body |
| 18 | Tasting | Tasting food pose, thoughtful, full body |
| 19 | Baking | Baking pose, holding a whisk, full body |
| 20 | Playing | Playing pose, full body |

---

## Outfit Generation Prompts

Use template: `{name}, {species}, {appearance}, wearing {outfit_variant}, standing, front view, full body, {style}`

| # | Outfit | Description |
|---|--------|-------------|
| 1 | Daily Outfit | White chef jacket, red apron, tall chef hat, striped pants (signature look) |
| 2 | Casual | Warm orange polo shirt, khaki pants |
| 3 | Winter Outfit | White puffy chef coat (insulated), red scarf |
| 4 | Rain Outfit | Yellow apron, rain boots |
| 5 | Pajamas | Red and white striped PJs, chef hat sleep mask |
| 6 | Market Day | Casual plaid shirt, jeans, flat cap |
| 7 | Tasting Event | Formal white chef coat, medals pinned |
| 8 | Baking Day | Flour-dusted apron, bandana |
| 9 | Halloween Costume | Dressed as a giant cupcake |
| 10 | Christmas Outfit | Red chef jacket with holly trim, Santa chef hat |

---

## Age Variant Prompts

*Skipped — Chef Pig is a fixed adult character.*

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

## Quality Checklist for Chef Pig

- [ ] Character is instantly recognizable as Chef Pig
- [ ] Tall white chef hat is visible and signature
- [ ] Bright brown eyes are cheerful and expressive
- [ ] Red apron over white chef jacket matches the signature look
- [ ] Skin is light pink (not dark pink or red)
- [ ] Snout is round and expressive
- [ ] Proportions are pig-like (round soft body)
- [ ] Expression matches the requested emotion
- [ ] No anatomical deformities (extra limbs, missing features)
- [ ] No watermarks, text, or logos
- [ ] Background is appropriate and child-friendly (kitchen or market)
- [ ] Lighting is soft and warm
- [ ] Style matches Cocomelon-inspired aesthetic
- [ ] Curly tail is visible from behind
- [ ] Character fills the frame appropriately for the type (portrait, full body)

---

*Generated for AI Nursery Rhyme Studio — Universe Library*
*Version 1.0 — 2026-07-29*
