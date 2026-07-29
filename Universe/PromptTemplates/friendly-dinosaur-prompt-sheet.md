# Friendly Dinosaur — Prompt Reference Sheet

> **Version:** 1.0
> **Character:** Friendly Dinosaur (Young)
> **Style:** Cocomelon-inspired, Pixar-quality, bright colorful nursery world

---

## Character Card

| Attribute | Value |
|-----------|-------|
| Name | Friendly Dinosaur |
| Species | Brontosaurus (baby) |
| Appearance | Blue-green pebbly skin with gentle pattern, gentle round brown eyes, very long flexible neck, bulky body, very long tail, thick sturdy four legs, broad friendly snout, wide nostrils, flat plant-eater teeth rarely shown, small rounded nails |
| Default Form | Standing — gentle giant posture, long neck reaching up |
| Style | Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| Signature Accessory | Very long neck, sometimes a flower crown gift from friends |

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{name}` | Character name | Friendly Dinosaur |
| `{species}` | Species description | Brontosaurus (baby) |
| `{appearance}` | Physical appearance | Blue-green pebbly skin, gentle brown eyes, long neck, ... |
| `{form}` | Current form/state | Eating, Walking, Neck Hug |
| `{form_variant}` | Alternate form | Curious exploring, Playing gently |
| `{expression}` | Expression name | Happy, Surprised, Sad |
| `{pose}` | Pose name | Standing, Walking, Neck Hug |
| `{angle}` | Camera angle | Front, 3/4, Profile, Back |
| `{lighting}` | Lighting condition | Golden hour, Morning, Night |
| `{style}` | Visual style | Pixar-quality, Cocomelon-inspired, ... |

---

## Expression Generation Prompts

Use template: `{name}, {species}, {appearance}, {expression} expression, portrait shot, {style}`

| # | Expression | Prompt Snippet |
|---|------------|---------------|
| 1 | Neutral | Friendly Dinosaur, Brontosaurus (baby), blue-green pebbly skin with gentle pattern, gentle round brown eyes, very long flexible neck, bulky body, very long tail, thick sturdy four legs, broad friendly snout, wide nostrils, flat plant-eater teeth rarely shown, small rounded nails, neutral expression, portrait shot, Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| 2 | Happy | (same base) + happy expression, portrait shot |
| 3 | Very Happy | (same base) + very happy expression, portrait shot |
| 4 | Laughing | (same base) + laughing expression, portrait shot |
| 5 | Giggling | (same base) + giggling expression, portrait shot |
| 6 | Smiling | (same base) + smiling expression, portrait shot |
| 7 | Excited | (same base) + excited expression, tail swaying, portrait shot |
| 8 | Surprised | (same base) + surprised expression, portrait shot |
| 9 | Confused | (same base) + confused expression, head tilted, portrait shot |
| 10 | Thinking | (same base) + thinking expression, portrait shot |
| 11 | Curious | (same base) + curious expression, neck extended, portrait shot |
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

Use template: `{name}, {species}, {appearance}, {pose} pose, full body, {style}`

| # | Pose | Description |
|---|------|-------------|
| 1 | Standing | Standing on all fours, full body |
| 2 | Walking | Walking pose, slow heavy steps, tail swaying, full body |
| 3 | Running | Running pose, heavy stomping, full body |
| 4 | Jumping | Jumping pose, full body |
| 5 | Stomping | Gentle stomping pose, full body |
| 6 | Sitting | Sitting on haunches pose, full body |
| 7 | Lying Down | Lying down pose, full body |
| 8 | Dancing | Dancing pose, gentle swaying, full body |
| 9 | Sleeping | Sleeping curled in a circle, tail wrapped around, full body |
| 10 | Reading | Reading pose, book on ground, full body |
| 11 | Writing | Writing with claw pose, full body |
| 12 | Pointing | Pointing with nose/neck pose, full body |
| 13 | Clapping | Clapping paws together pose, full body |
| 14 | Waving | Waving with foreleg pose, full body |
| 15 | Hugging | Neck hug pose, lowering head around friend, full body |
| 16 | Playing | Playing pose, chasing bubbles, full body |
| 17 | Neck Extended | Neck extended curiously pose, full body |
| 18 | Swimming | Swimming pose, full body |
| 19 | Eating | Eating pose, long neck reaching up, munching, full body |
| 20 | Flower Sniffing | Sniffing flowers pose, full body |

---

## Forms/States Generation

Use template: `{name}, {species}, {appearance}, {form_variant}, front view, full body, {style}`

| # | Form/State | Description |
|---|------------|-------------|
| 1 | Eating | Long neck reaching up, gentle munching |
| 2 | Walking | Slow, heavy steps, tail swaying |
| 3 | Neck Hug | Lowering head to wrap around friend |
| 4 | Sitting | Resting on haunches, head low |
| 5 | Sleeping | Curled in a circle, tail wrapped around |
| 6 | Curious | Neck extended, head tilted, sniffing |
| 7 | Playing | Gentle stomping, chasing bubbles |

---

## Age Variant Prompts

*Skipped — Friendly Dinosaur is a fixed young character.*

---

## Rotation Sheet Prompts

Use template: `{name}, {species}, {appearance}, {angle} view, {style}`

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

Use template: `{name}, {species}, {appearance}, {lighting} lighting, {style}`

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

## Quality Checklist for Friendly Dinosaur

- [ ] Character is instantly recognizable as Friendly Dinosaur
- [ ] Blue-green skin is pebbly and gentle (not scaly or scary)
- [ ] Brown eyes are gentle, round, and expressive
- [ ] Very long neck is a defining feature
- [ ] Long tail is visible (sometimes bumping things)
- [ ] Skin is blue-green (not dark green or gray)
- [ ] Proportions are baby brontosaurus (bulky but cute)
- [ ] Expression matches the requested emotion
- [ ] No scary dinosaur features (no sharp teeth, no claws)
- [ ] No watermarks, text, or logos
- [ ] Background is appropriate and child-friendly (meadow or forest)
- [ ] Lighting is soft and warm
- [ ] Style matches Cocomelon-inspired aesthetic
- [ ] Flower crown may be present (gift from friends)
- [ ] Character fills the frame appropriately for the type (portrait, full body)

---

*Generated for AI Nursery Rhyme Studio — Universe Library*
*Version 1.0 — 2026-07-29*
