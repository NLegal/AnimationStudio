# Farmer Goat — Prompt Reference Sheet

> **Version:** 1.0
> **Character:** Farmer Goat (Adult)
> **Style:** Cocomelon-inspired, Pixar-quality, bright colorful nursery world

---

## Character Card

| Attribute | Value |
|-----------|-------|
| Name | Farmer Goat |
| Species | Goat (white with brown patches) |
| Appearance | White fur with brown patches on back and ears, warm amber friendly eyes, small white goatee, curved brown horns, long floppy brown-tipped ears, lean sturdy active body, long snout, oval pink nose |
| Default Outfit | Straw hat, blue denim overalls, green rubber boots |
| Style | Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| Signature Accessory | Straw hat (slightly worn) |

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{name}` | Character name | Farmer Goat |
| `{species}` | Species description | Goat (white with brown patches) |
| `{appearance}` | Physical appearance | White fur with brown patches, warm amber eyes, ... |
| `{outfit}` | Outfit description | Straw hat, blue denim overalls, green boots |
| `{outfit_variant}` | Alternate outfit | Brown woollen coat over overalls |
| `{expression}` | Expression name | Happy, Surprised, Sad |
| `{pose}` | Pose name | Standing, Gardening, Tending |
| `{angle}` | Camera angle | Front, 3/4, Profile, Back |
| `{lighting}` | Lighting condition | Golden hour, Morning, Night |
| `{style}` | Visual style | Pixar-quality, Cocomelon-inspired, ... |

---

## Expression Generation Prompts

Use template: `{name}, {species}, {appearance}, wearing {outfit}, {expression} expression, portrait shot, {style}`

| # | Expression | Prompt Snippet |
|---|------------|---------------|
| 1 | Neutral | Farmer Goat, Goat (white with brown patches), white fur with brown patches on back and ears, warm amber friendly eyes, small white goatee, curved brown horns, long floppy brown-tipped ears, lean sturdy active body, long snout, oval pink nose, wearing straw hat, blue denim overalls, green rubber boots, neutral expression, portrait shot, Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
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
| 13 | Yawning | (same base) + yawning expression, mouth open, portrait shot |
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
| 5 | Trotting | Trotting pose, full body |
| 6 | Sitting | Sitting pose, full body |
| 7 | Kneeling | Kneeling to tend plants, full body |
| 8 | Dancing | Dancing pose, full body |
| 9 | Sleeping | Sleeping pose, full body |
| 10 | Reading | Reading a seed catalog, full body |
| 11 | Writing | Writing in garden journal, full body |
| 12 | Pointing | Pointing at a plant pose, full body |
| 13 | Clapping | Clapping pose, hooves together, full body |
| 14 | Waving | Waving pose, hoof raised, full body |
| 15 | Hugging | Hugging pose, arms open, full body |
| 16 | Holding Hands | Holding hooves with friend, full body |
| 17 | Gardening | Gardening pose, holding a rake, full body |
| 18 | Watering | Watering plants pose, full body |
| 19 | Harvesting | Harvesting vegetables pose, full body |
| 20 | Playing | Playing pose, full body |

---

## Outfit Generation Prompts

Use template: `{name}, {species}, {appearance}, wearing {outfit_variant}, standing, front view, full body, {style}`

| # | Outfit | Description |
|---|--------|-------------|
| 1 | Daily Outfit | Straw hat, blue denim overalls, green boots (signature look) |
| 2 | Summer Wear | Straw hat, blue overalls rolled to knees, no shirt |
| 3 | Winter Outfit | Brown woollen coat over overalls, knitted hat under straw hat |
| 4 | Rain Outfit | Yellow slicker and matching hat cover |
| 5 | Pajamas | Green PJs with vegetable print |
| 6 | Market Day | Clean overalls, plaid shirt, straw hat |
| 7 | Barn Work | Brown apron over bare chest, work gloves |
| 8 | Casual | Cream linen shirt, brown pants |
| 9 | Halloween Costume | Dressed as a scarecrow |
| 10 | Christmas Outfit | Red and green plaid shirt, Santa hat |

---

## Age Variant Prompts

*Skipped — Farmer Goat is a fixed adult character.*

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

## Quality Checklist for Farmer Goat

- [ ] Character is instantly recognizable as Farmer Goat
- [ ] Straw hat is visible and slightly worn
- [ ] Warm amber eyes are friendly and expressive
- [ ] Small white goatee is present
- [ ] Blue denim overalls and green boots match the signature look
- [ ] Curved brown horns are visible
- [ ] Proportions are goat-like (long snout, floppy ears)
- [ ] Expression matches the requested emotion
- [ ] No anatomical deformities (extra limbs, missing features)
- [ ] No watermarks, text, or logos
- [ ] Background is appropriate and child-friendly (farm or garden)
- [ ] Lighting is soft and warm
- [ ] Style matches Cocomelon-inspired aesthetic
- [ ] Brown patches on fur are natural-looking
- [ ] Character fills the frame appropriately for the type (portrait, full body)

---

*Generated for AI Nursery Rhyme Studio — Universe Library*
*Version 1.0 — 2026-07-29*
