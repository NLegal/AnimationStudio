# Moon — Prompt Reference Sheet

> **Version:** 1.0
> **Character:** Moon (Ageless)
> **Style:** Cocomelon-inspired, Pixar-quality, bright colorful nursery world

---

## Character Card

| Attribute | Value |
|-----------|-------|
| Name | Moon |
| Species | Moon |
| Appearance | Soft silver-white glow, kind smiling face with craters forming gentle features, warm white light, phases from crescent to full, smooth luminous surface, gentle sleepy crescent-shaped eyes when smiling, warm soft curve mouth, rosy blush visible on full moon, large in the night sky, surrounded by tiny star friends |
| Default Form | Full Moon — complete circle, brightest, face clear |
| Style | Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| Signature Trait | Silver-white glow, phases from crescent to full |

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{name}` | Character name | Moon |
| `{species}` | Species description | Moon |
| `{appearance}` | Physical appearance | Soft silver-white glow, kind smiling face, ... |
| `{appearance_variant}` | Appearance variant | Full Moon, Crescent, Gibbous |
| `{mood}` | Mood/state name | Peaceful, Sleepy, Guardian |
| `{form_position}` | Form/position name | Rising, Setting, Peeking |
| `{lighting}` | Lighting condition | Golden hour, Morning, Night |
| `{style}` | Visual style | Pixar-quality, Cocomelon-inspired, ... |

---

## Mood/State Generation Prompts

Use template: `{name}, {species}, {appearance}, {mood} mood, full scene, {style}`

| # | Mood/State | Prompt Snippet |
|---|------------|---------------|
| 1 | Peaceful | Moon, Moon, soft silver-white glow, kind smiling face with craters forming gentle features, warm white light, phases from crescent to full, smooth luminous surface, gentle sleepy crescent-shaped eyes when smiling, warm soft curve mouth, rosy blush visible on full moon, large in the night sky, surrounded by tiny star friends, peaceful mood, full scene, Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| 2 | Happy | (same base) + happy mood, warm glow, full scene |
| 3 | Very Happy | (same base) + very happy mood, brightest silver, full scene |
| 4 | Laughing | (same base) + laughing mood, gentle wobble, full scene |
| 5 | Giggling | (same base) + giggling mood, craters twinkling, full scene |
| 6 | Smiling | (same base) + smiling mood, crescent eyes, full scene |
| 7 | Excited | (same base) + excited mood, brighter glow, full scene |
| 8 | Surprised | (same base) + surprised mood, eyes wide, full scene |
| 9 | Confused | (same base) + confused mood, tilting slightly, full scene |
| 10 | Thoughtful | (same base) + thoughtful mood, soft dim glow, full scene |
| 11 | Curious | (same base) + curious mood, leaning forward, full scene |
| 12 | Sleepy | (same base) + sleepy mood, softest glow, half-closed eyes, full scene |
| 13 | Yawning | (same base) + yawning mood, stretching glow, full scene |
| 14 | Crying | (same base) + crying mood, dim light, full scene |
| 15 | Sad | (same base) + sad mood, dim and low, full scene |
| 16 | Scared | (same base) + scared mood, half behind cloud, full scene |
| 17 | Embarrassed | (same base) + embarrassed mood, rosy blush, full scene |
| 18 | Proud | (same base) + proud mood, full and bright, full scene |
| 19 | Determined | (same base) + determined mood, steady glow, full scene |
| 20 | Singing | (same base) + singing mood, gentle vibration, full scene |
| 21 | Whistling | (same base) + whistling mood, soft breeze, full scene |
| 22 | Blowing Kiss | (same base) + blowing kiss mood, sending a moonbeam, full scene |
| 23 | Winking | (same base) + winking mood, one eye closing playfully, full scene |

---

## Form/Position Generation Prompts

Use template: `{name}, {species}, {appearance}, {form_position} position, full scene, {style}`

| # | Form/Position | Description |
|---|--------------|-------------|
| 1 | Rising | Rising over the horizon, evening |
| 2 | Setting | Setting below horizon, dawn approaching |
| 3 | High | High in the night sky, centered |
| 4 | Peeking | Peeking from behind a cloud, partially hidden |
| 5 | Resting | Resting at the horizon, large and low |
| 6 | Glowing | Glowing brightly, illuminating the night |
| 7 | Hiding | Hiding behind clouds, peekaboo |
| 8 | Dancing | Moonbeams dancing, glow shimmering |
| 9 | Sleeping | Dim glow, resting, barely visible |
| 10 | Watching | Watching over sleeping world, guardian |
| 11 | Leaning | Leaning slightly, curious about below |
| 12 | Beaming | Sending a single bright moonbeam down |
| 13 | Sailing | Sailing across the sky, moving gracefully |
| 14 | Waving | Waves a moonbeam goodbye |
| 15 | Hugging | Glow wrapping around the night sky |
| 16 | Playing | Playing peekaboo with clouds |
| 17 | Climbing | Climbing higher in the sky |
| 18 | Settling | Settling into position for the night |
| 19 | Vanishing | Fading as dawn approaches |
| 20 | Cradling | Cradling stars in her glow |

---

## Appearance Variations

Use template: `{name}, {species}, {appearance_variant} appearance, full scene, {style}`

| # | Variation | Description |
|---|-----------|-------------|
| 1 | Full Moon | Complete circle, brightest, face clear |
| 2 | Crescent Moon | Thin smile in sky, smallest glow |
| 3 | Gibbous Moon | Mostly full, nearly complete |
| 4 | Half Moon | Split evenly — gentle profile |
| 5 | Shy Moon | Partially behind cloud, peeking out |
| 6 | Bedtime Moon | Yawning, softest glow, sleepy eyes |
| 7 | Guardian Moon | Full, bright, watchful over sleeping world |
| 8 | New Moon | Invisible — resting, no glow |

---

## Age Variant Prompts

*Skipped — Moon is ageless.*

---

## Lighting Variant Prompts

Use template: `{name}, {species}, {appearance}, {lighting} lighting, {style}`

| Lighting | Description |
|----------|-------------|
| Morning | Morning lighting — Moon fading |
| Afternoon | Afternoon — Moon invisible |
| Golden Hour | Golden hour — Moon beginning to appear |
| Night | Night lighting, Moon at full brilliance |
| Moonlight | Moon's own cool illumination |
| Rain | Overcast, rainy — Moon hidden |
| Snow | Bright snowy night — Moon reflects |
| Cloudy | Soft diffused — Moon peeking |
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

## Quality Checklist for Moon

- [ ] Character is instantly recognizable as Moon
- [ ] Silver-white glow is soft and warm (not harsh)
- [ ] Kind smiling face is visible in the craters
- [ ] Phase matches the requested variant (crescent, half, full, etc.)
- [ ] Glow is luminous and inviting (not dark or scary)
- [ ] Blush is visible on full moon
- [ ] Stars may accompany her in the scene
- [ ] No watermarks, text, or logos
- [ ] Background is appropriate (night sky)
- [ ] Lighting is soft and warm
- [ ] Style matches Cocomelon-inspired aesthetic
- [ ] Moon looks friendly and soothing (not eerie)
- [ ] Form/position matches the requested variant
- [ ] Craters form gentle facial features (not harsh)

---

*Generated for AI Nursery Rhyme Studio — Universe Library*
*Version 1.0 — 2026-07-29*
