# Unicorn — Prompt Reference Sheet

> **Version:** 1.0
> **Character:** Unicorn (Ageless)
> **Style:** Cocomelon-inspired, Pixar-quality, bright colorful nursery world

---

## Character Card

| Attribute | Value |
|-----------|-------|
| Name | Unicorn |
| Species | Unicorn |
| Appearance | Pure white shimmering coat, rainbow mane flowing through all colors, rainbow tail matching mane, golden spiral horn that glows softly, large kind purple eyes, elegant graceful pony-proportioned body, refined gentle face, silver polished hooves, long slender legs, long beautiful eyelashes |
| Default Form | Standing — proud, elegant, horn catching light |
| Style | Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| Signature Accessory | Golden spiral horn, rainbow mane and tail |

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{name}` | Character name | Unicorn |
| `{species}` | Species description | Unicorn |
| `{appearance}` | Physical appearance | White shimmering coat, rainbow mane, golden horn, ... |
| `{form}` | Current form/state | Grazing, Galloping, Sleeping |
| `{form_variant}` | Alternate form | Artistic creating rainbow, Playful prancing |
| `{expression}` | Expression name | Happy, Surprised, Sad |
| `{pose}` | Pose name | Standing, Galloping, Prancing |
| `{angle}` | Camera angle | Front, 3/4, Profile, Back |
| `{lighting}` | Lighting condition | Golden hour, Morning, Night |
| `{style}` | Visual style | Pixar-quality, Cocomelon-inspired, ... |

---

## Expression Generation Prompts

Use template: `{name}, {species}, {appearance}, {expression} expression, portrait shot, {style}`

| # | Expression | Prompt Snippet |
|---|------------|---------------|
| 1 | Neutral | Unicorn, Unicorn, pure white shimmering coat, rainbow mane flowing through all colors, rainbow tail matching mane, golden spiral horn that glows softly, large kind purple eyes, elegant graceful pony-proportioned body, refined gentle face, silver polished hooves, long slender legs, long beautiful eyelashes, neutral expression, portrait shot, Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| 2 | Happy | (same base) + happy expression, portrait shot |
| 3 | Very Happy | (same base) + very happy expression, portrait shot |
| 4 | Laughing | (same base) + laughing expression, portrait shot |
| 5 | Giggling | (same base) + giggling expression, portrait shot |
| 6 | Smiling | (same base) + smiling expression, portrait shot |
| 7 | Excited | (same base) + excited expression, horn glowing brighter, portrait shot |
| 8 | Surprised | (same base) + surprised expression, portrait shot |
| 9 | Confused | (same base) + confused expression, head tilted, portrait shot |
| 10 | Thinking | (same base) + thinking expression, portrait shot |
| 11 | Curious | (same base) + curious expression, ears forward, portrait shot |
| 12 | Sleepy | (same base) + sleepy expression, portrait shot |
| 13 | Yawning | (same base) + yawning expression, mouth open, portrait shot |
| 14 | Crying | (same base) + crying expression, portrait shot |
| 15 | Sad | (same base) + sad expression, horn dimmed, portrait shot |
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
| 1 | Standing | Standing pose, full body |
| 2 | Walking | Walking pose, full body |
| 3 | Trotting | Trotting pose, full body |
| 4 | Galloping | Galloping pose, magical stride, full body |
| 5 | Prancing | Prancing pose, playful, full body |
| 6 | Sitting | Sitting on haunches pose, full body |
| 7 | Lying Down | Lying down pose, full body |
| 8 | Dancing | Dancing pose, elegant steps, full body |
| 9 | Sleeping | Sleeping on side pose, full body |
| 10 | Reading | Reading pose, book held in magic, full body |
| 11 | Writing | Writing with magic pose, full body |
| 12 | Pointing | Pointing with horn pose, full body |
| 13 | Clapping | Clapping hooves together pose, full body |
| 14 | Waving | Waving with foreleg pose, full body |
| 15 | Hugging | Nuzzling hug pose, full body |
| 16 | Playing | Playing pose, inviting friends, full body |
| 17 | Grazing | Grazing pose, head down, mane flowing, full body |
| 18 | Swimming | Swimming pose, full body |
| 19 | Jumping | Jumping over obstacle pose, full body |
| 20 | Creating Rainbow | Creating rainbow with horn pose, eyes closed, full body |

---

## Forms/States Generation

Use template: `{name}, {species}, {appearance}, {form_variant}, front view, full body, {style}`

| # | Form/State | Description |
|---|------------|-------------|
| 1 | Grazing | Head down, mane flowing, peaceful |
| 2 | Galloping | Magical stride, rainbow trail, mane streaming |
| 3 | Standing | Proud, elegant, horn catching light |
| 4 | Sleeping | Lying down, head on hooves, horn dimmed |
| 5 | Nervous | Horn glowing brighter, looking around |
| 6 | Artistic | Creating rainbows with horn, eyes closed |
| 7 | Playful | Prancing, inviting friends to follow |

---

## Age Variant Prompts

*Skipped — Unicorn is ageless.*

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

## Quality Checklist for Unicorn

- [ ] Character is instantly recognizable as Unicorn
- [ ] Golden spiral horn is visible and glowing softly
- [ ] Rainbow mane and tail are vibrant with all colors
- [ ] Purple eyes are large, kind, and expressive
- [ ] Coat is pure white with a slight shimmer
- [ ] Hooves are silver and polished
- [ ] Proportions are pony-like and elegant (not horse-like adult)
- [ ] Expression matches the requested emotion
- [ ] No anatomical deformities (extra legs, missing features)
- [ ] No watermarks, text, or logos
- [ ] Background is appropriate and child-friendly (meadow or sky)
- [ ] Lighting is soft and magical
- [ ] Style matches Cocomelon-inspired aesthetic
- [ ] Mane flows naturally with rainbow colors
- [ ] Character fills the frame appropriately for the type (portrait, full body)

---

*Generated for AI Nursery Rhyme Studio — Universe Library*
*Version 1.0 — 2026-07-29*
