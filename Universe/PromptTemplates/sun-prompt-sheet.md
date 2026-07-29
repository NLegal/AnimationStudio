# Sun — Prompt Reference Sheet

> **Version:** 1.0
> **Character:** Sun (Ageless)
> **Style:** Cocomelon-inspired, Pixar-quality, bright colorful nursery world

---

## Character Card

| Attribute | Value |
|-----------|-------|
| Name | Sun |
| Species | Sun |
| Appearance | Bright golden yellow perfect circle, warm golden rays radiating in all directions, big cheerful smile, warm bright crescent-shaped eyes when smiling, rosy pink cheeks, wide happy smile, warm golden halo around edges, large and commanding in sky |
| Default Form | Morning Rise — peeking over horizon, half-awake rays |
| Style | Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| Signature Trait | Golden rays radiating, warm cheerful face |

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{name}` | Character name | Sun |
| `{species}` | Species description | Sun |
| `{appearance}` | Physical appearance | Bright golden yellow circle, warm golden rays, ... |
| `{appearance_variant}` | Appearance variant | Morning Rise, Noon Bright, Sunset |
| `{mood}` | Mood/state name | Happy, Sleepy, Playful |
| `{form_position}` | Form/position name | Rising, High, Setting |
| `{lighting}` | Lighting condition | Golden hour, Morning, Night |
| `{style}` | Visual style | Pixar-quality, Cocomelon-inspired, ... |

---

## Mood/State Generation Prompts

Use template: `{name}, {species}, {appearance}, {mood} mood, full scene, {style}`

| # | Mood/State | Prompt Snippet |
|---|------------|---------------|
| 1 | Cheerful | Sun, Sun, bright golden yellow perfect circle, warm golden rays radiating in all directions, big cheerful smile, warm bright crescent-shaped eyes when smiling, rosy pink cheeks, wide happy smile, warm golden halo around edges, large and commanding in sky, cheerful mood, full scene, Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| 2 | Happy | (same base) + happy mood, rays waving, full scene |
| 3 | Very Happy | (same base) + very happy mood, brightest rays, full scene |
| 4 | Laughing | (same base) + laughing mood, rays bouncing, full scene |
| 5 | Giggling | (same base) + giggling mood, golden sparkles, full scene |
| 6 | Smiling | (same base) + smiling mood, warm gentle glow, full scene |
| 7 | Excited | (same base) + excited mood, rays extending far, full scene |
| 8 | Surprised | (same base) + surprised mood, eyes wide, full scene |
| 9 | Confused | (same base) + confused mood, tilting, rays drooping, full scene |
| 10 | Thoughtful | (same base) + thoughtful mood, soft warm glow, full scene |
| 11 | Curious | (same base) + curious mood, leaning toward earth, full scene |
| 12 | Sleepy | (same base) + sleepy mood, rays drooping, dimmer, full scene |
| 13 | Yawning | (same base) + yawning mood, rays stretching, full scene |
| 14 | Crying | (same base) + crying mood, dim warm rain, full scene |
| 15 | Sad | (same base) + sad mood, dim behind clouds, full scene |
| 16 | Scared | (same base) + scared mood, half behind cloud, full scene |
| 17 | Embarrassed | (same base) + embarrassed mood, rosier cheeks, full scene |
| 18 | Proud | (same base) + proud mood, rays extended proudly, full scene |
| 19 | Determined | (same base) + determined mood, steady bright, full scene |
| 20 | Singing | (same base) + singing mood, rays vibrating, full scene |
| 21 | Whistling | (same base) + whistling mood, warm breeze, full scene |
| 22 | Blowing Kiss | (same base) + blowing kiss mood, sending a warm ray, full scene |
| 23 | Winking | (same base) + winking mood, one eye closing playfully, full scene |

---

## Form/Position Generation Prompts

Use template: `{name}, {species}, {appearance}, {form_position} position, full scene, {style}`

| # | Form/Position | Description |
|---|--------------|-------------|
| 1 | Rising | Peeking over horizon, half-awake rays |
| 2 | High | High in sky, centered, rays extended |
| 3 | Setting | Sinking below horizon, long warm rays |
| 4 | Peeking | Peeking from behind a cloud, playful |
| 5 | Resting | Resting on the horizon, large and golden |
| 6 | Beaming | Beaming brightly, rays reaching far |
| 7 | Hiding | Hiding behind clouds, peekaboo game |
| 8 | Dancing | Rays dancing and waving playfully |
| 9 | Sleeping | Setting, yawning, rays drooping |
| 10 | Watching | Watching over the world, gentle warmth |
| 11 | Reaching | Rays reaching down to touch the earth |
| 12 | Warming | Warming a specific spot, focused rays |
| 13 | Sailing | Sailing across the sky, daily journey |
| 14 | Waving | Rays waving goodbye at sunset |
| 15 | Hugging | Wrap-around glow embracing the sky |
| 16 | Playing | Playing peekaboo behind passing clouds |
| 17 | Climbing | Climbing higher since morning rise |
| 18 | Descending | Descending toward the horizon |
| 19 | Blazing | Brightest at noon, rays at maximum |
| 20 | Dipping | Dipping below the horizon, last gleam |

---

## Appearance Variations

Use template: `{name}, {species}, {appearance_variant} appearance, full scene, {style}`

| # | Variation | Description |
|---|-----------|-------------|
| 1 | Morning Rise | Peeking over horizon, half-awake rays |
| 2 | Noon Bright | High, brightest, rays extended proudly |
| 3 | Afternoon Warm | Golden, softer rays, warmest glow |
| 4 | Sunset | Deep orange, sinking, long rays |
| 5 | Peekaboo | Behind cloud, half-hidden, playful smile |
| 6 | Sleepy Sun | Setting, yawning, rays drooping |
| 7 | Happy Sun | Brightest, rays waving in all directions |
| 8 | Gentle Sun | Warm, soft, encouraging morning growth |

---

## Age Variant Prompts

*Skipped — Sun is ageless.*

---

## Lighting Variant Prompts

Use template: `{name}, {species}, {appearance}, {lighting} lighting, {style}`

| Lighting | Description |
|----------|-------------|
| Morning | Soft morning lighting, Sun just risen |
| Afternoon | Bright afternoon lighting, Sun high |
| Golden Hour | Warm golden hour glow, Sun setting |
| Night | Night lighting — Sun is hidden |
| Moonlight | Cool moonlight — Sun is gone |
| Rain | Overcast — Sun behind clouds |
| Snow | Bright snowy — Sun reflects |
| Cloudy | Soft diffused — Sun peeking |
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

## Quality Checklist for Sun

- [ ] Character is instantly recognizable as Sun
- [ ] Golden yellow color is warm and bright
- [ ] Cheerful face is visible with rosy cheeks
- [ ] Rays radiate in all directions evenly
- [ ] Glow is warm and inviting (not blinding)
- [ ] Circle shape is perfect and clean
- [ ] Mood matches the requested emotion
- [ ] No harsh lines — rays fade softly
- [ ] No watermarks, text, or logos
- [ ] Background is appropriate (daytime sky)
- [ ] Lighting is warm and golden
- [ ] Style matches Cocomelon-inspired aesthetic
- [ ] Sun looks friendly and cheerful (not intense)
- [ ] Form/position matches the requested variant
- [ ] Eyes are warm and crescent-shaped when smiling

---

*Generated for AI Nursery Rhyme Studio — Universe Library*
*Version 1.0 — 2026-07-29*
