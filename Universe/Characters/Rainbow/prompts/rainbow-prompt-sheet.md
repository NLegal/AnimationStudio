# Rainbow — Prompt Reference Sheet

> **Version:** 1.0
> **Character:** Rainbow (Ageless)
> **Style:** Cocomelon-inspired, Pixar-quality, bright colorful nursery world

---

## Character Card

| Attribute | Value |
|-----------|-------|
| Name | Rainbow |
| Species | Rainbow |
| Appearance | Seven shimmering colors spanning the sky (red, orange, yellow, green, blue, indigo, violet), perfect arch shape across the horizon, shimmering translucent glow, soft fading edges dissolving into sky, gentle happy face visible within the glow, warm celebratory presence, edges pulse gently |
| Default Form | Full Arc — classic rainbow from ground to ground |
| Style | Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| Signature Trait | Seven colors in perfect harmony, appearing after rain |

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{name}` | Character name | Rainbow |
| `{species}` | Species description | Rainbow |
| `{appearance}` | Physical appearance | Seven shimmering colors, perfect arch, translucent glow, ... |
| `{appearance_variant}` | Appearance variant | Full Arc, Double Rainbow, Baby Rainbow |
| `{mood}` | Mood/state name | Joyful, Peaceful, Fading |
| `{form_position}` | Form/position name | Arching, Stretching, Fading |
| `{lighting}` | Lighting condition | Golden hour, Morning, Night |
| `{style}` | Visual style | Pixar-quality, Cocomelon-inspired, ... |

---

## Mood/State Generation Prompts

Use template: `{name}, {species}, {appearance}, {mood} mood, full scene, {style}`

| # | Mood/State | Prompt Snippet |
|---|------------|---------------|
| 1 | Neutral | Rainbow, Rainbow, seven shimmering colors spanning the sky (red, orange, yellow, green, blue, indigo, violet), perfect arch shape across the horizon, shimmering translucent glow, soft fading edges dissolving into sky, gentle happy face visible within the glow, warm celebratory presence, edges pulse gently, neutral mood, full scene, Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| 2 | Joyful | (same base) + joyful mood, colors bright and vivid, full scene |
| 3 | Very Happy | (same base) + very happy mood, shimmering brighter, full scene |
| 4 | Laughing | (same base) + laughing mood, colors pulsing with mirth, full scene |
| 5 | Giggling | (same base) + giggling mood, edges tickling, full scene |
| 6 | Warm | (same base) + warm mood, golden tones emphasized, full scene |
| 7 | Excited | (same base) + excited mood, colors extra vivid, full scene |
| 8 | Surprised | (same base) + surprised mood, sudden bright flash, full scene |
| 9 | Confused | (same base) + confused mood, colors wobbling, full scene |
| 10 | Thoughtful | (same base) + thoughtful mood, soft slow pulse, full scene |
| 11 | Curious | (same base) + curious mood, stretching toward something, full scene |
| 12 | Sleepy | (same base) + sleepy mood, dimming slightly, full scene |
| 13 | Yawning | (same base) + yawning mood, stretching wider then relaxing, full scene |
| 14 | Crying | (same base) + crying mood, colors running, full scene |
| 15 | Sad | (same base) + sad mood, colors muted and dim, full scene |
| 16 | Scared | (same base) + scared mood, colors flickering, full scene |
| 17 | Embarrassed | (same base) + embarrassed mood, pink tones glowing, full scene |
| 18 | Proud | (same base) + proud mood, arching tall and bright, full scene |
| 19 | Determined | (same base) + determined mood, colors holding firm, full scene |
| 20 | Singing | (same base) + singing mood, colors vibrating in harmony, full scene |
| 21 | Whistling | (same base) + whistling mood, soft shimmer, full scene |
| 22 | Blowing Kiss | (same base) + blowing kiss mood, sending a color puff, full scene |
| 23 | Winking | (same base) + winking mood, one stripe flickering, full scene |

---

## Form/Position Generation Prompts

Use template: `{name}, {species}, {appearance}, {form_position} position, full scene, {style}`

| # | Form/Position | Description |
|---|--------------|-------------|
| 1 | Arching | Full arch across the sky, reaching both horizons |
| 2 | Stretching | Stretching wider across the sky |
| 3 | Rising | Rising from behind a hill, appearing slowly |
| 4 | Fading | Slowly dissolving, colors disappearing one by one |
| 5 | Brightening | Growing brighter and more vivid |
| 6 | Resting | Resting over a landscape, still and peaceful |
| 7 | Peeking | Peeking from behind a cloud, partial arc |
| 8 | Dancing | Colors pulsing and shimmering playfully |
| 9 | Sleeping | Softest glow, barely visible, resting |
| 10 | Reflecting | Reflecting in water below |
| 11 | Reaching | Reaching from cloud to ground |
| 12 | Bending | Bending into a tighter arc |
| 13 | Doubling | Double rainbow forming second arch |
| 14 | Waving | Colors rippling like a flag |
| 15 | Hugging | Curving around a mountain |
| 16 | Playing | Quick appearance and disappearance |
| 17 | Soaring | High arcing across the entire sky |
| 18 | Settling | Settling into a stable arch after rain |
| 19 | Connecting | Connecting two clouds together |
| 20 | Cradling | Cradling the horizon in a gentle arc |

---

## Appearance Variations

Use template: `{name}, {species}, {appearance_variant} appearance, full scene, {style}`

| # | Variation | Description |
|---|-----------|-------------|
| 1 | Full Arc | Classic rainbow from ground to ground |
| 2 | Double Rainbow | Fainter second arch above, colors reversed |
| 3 | Partial Rainbow | Small arc just appearing after quick rain |
| 4 | Sunset Rainbow | Deep, warm-toned, golden glow blending |
| 5 | Morning Rainbow | Soft pastel, dew-fresh colors |
| 6 | Fading Rainbow | Slowly dissolving, colors one by one |
| 7 | Bright Rainbow | Clear sky after rain, colors vivid |
| 8 | Baby Rainbow | Small, cute, low to ground |

---

## Age Variant Prompts

*Skipped — Rainbow is ageless.*

---

## Lighting Variant Prompts

Use template: `{name}, {species}, {appearance}, {lighting} lighting, {style}`

| Lighting | Description |
|----------|-------------|
| Morning | Soft morning lighting, pastel tones |
| Afternoon | Bright afternoon lighting, vivid colors |
| Golden Hour | Warm golden hour glow, colors warm |
| Night | Night lighting — Rainbow is hidden |
| Moonlight | Cool moonlight illumination — faint shimmer |
| Rain | Overcast, rainy lighting — Rainbow appearing |
| Snow | Bright snowy lighting — crisp colors |
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

## Quality Checklist for Rainbow

- [ ] Character is instantly recognizable as Rainbow
- [ ] Seven colors are visible: red, orange, yellow, green, blue, indigo, violet
- [ ] Arch shape is smooth and perfect
- [ ] Colors are ordered correctly (red outermost, violet innermost)
- [ ] Glow is translucent and shimmering (not opaque)
- [ ] Mood matches the requested emotion
- [ ] No harsh lines — edges fade softly into sky
- [ ] No watermarks, text, or logos
- [ ] Background is appropriate (sky after rain)
- [ ] Lighting is warm and inviting
- [ ] Style matches Cocomelon-inspired aesthetic
- [ ] Rainbow looks magical and friendly (not scientific)
- [ ] Form/position matches the requested variant
- [ ] Gentle face may be visible in the glow

---

*Generated for AI Nursery Rhyme Studio — Universe Library*
*Version 1.0 — 2026-07-29*
