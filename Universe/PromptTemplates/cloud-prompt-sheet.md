# Cloud — Prompt Reference Sheet

> **Version:** 1.0
> **Character:** Cloud (Ageless)
> **Style:** Cocomelon-inspired, Pixar-quality, bright colorful nursery world

---

## Character Card

| Attribute | Value |
|-----------|-------|
| Name | Cloud |
| Species | Cloud |
| Appearance | Soft white with cream undertones, sometimes rainbow-tinted edges from inner glow, smiling face visible in the cloud fluff, puffy ever-changing round shape, soft gentle dark eyes, simple curve kind smile, fluffy soft-edged texture, medium size (can grow or shrink) |
| Default Form | Puffy — classic rounded cloud, smiling |
| Style | Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| Signature Trait | Ever-changing shape, smiling face in the fluff |

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{name}` | Character name | Cloud |
| `{species}` | Species description | Cloud |
| `{appearance}` | Physical appearance | Soft white fluffy cloud, smiling face in fluff, ... |
| `{appearance_variant}` | Appearance variant | Puffy white, Sunset painted, Rainy gray |
| `{mood}` | Mood/state name | Happy, Sad, Playful |
| `{form_position}` | Form/position name | Drifting, Storytelling, Protective |
| `{lighting}` | Lighting condition | Golden hour, Morning, Night |
| `{style}` | Visual style | Pixar-quality, Cocomelon-inspired, ... |

---

## Mood/State Generation Prompts

Use template: `{name}, {species}, {appearance}, {mood} mood, portrait shot, {style}`

| # | Mood/State | Prompt Snippet |
|---|------------|---------------|
| 1 | Neutral | Cloud, Cloud, soft white with cream undertones, sometimes rainbow-tinted edges from inner glow, smiling face visible in the cloud fluff, puffy ever-changing round shape, soft gentle dark eyes, simple curve kind smile, fluffy soft-edged texture, medium size (can grow or shrink), neutral mood, portrait shot, Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| 2 | Happy | (same base) + happy mood, fluffier and whiter, portrait shot |
| 3 | Very Happy | (same base) + very happy mood, portrait shot |
| 4 | Laughing | (same base) + laughing mood, bouncing gently, portrait shot |
| 5 | Giggling | (same base) + giggling mood, portrait shot |
| 6 | Content | (same base) + content mood, soft warm edges, portrait shot |
| 7 | Excited | (same base) + excited mood, quick shape changes, portrait shot |
| 8 | Surprised | (same base) + surprised mood, puffing up, portrait shot |
| 9 | Confused | (same base) + confused mood, tilting, portrait shot |
| 10 | Thoughtful | (same base) + thoughtful mood, portrait shot |
| 11 | Curious | (same base) + curious mood, stretching toward something, portrait shot |
| 12 | Sleepy | (same base) + sleepy mood, slow drifting, portrait shot |
| 13 | Yawning | (same base) + yawning mood, stretching wide, portrait shot |
| 14 | Crying | (same base) + crying mood, soft drizzle falling, portrait shot |
| 15 | Sad | (same base) + sad mood, gray tinge, portrait shot |
| 16 | Scared | (same base) + scared mood, stretching thin nervously, portrait shot |
| 17 | Embarrassed | (same base) + embarrassed mood, pink tinge, portrait shot |
| 18 | Proud | (same base) + proud mood, fluffy and tall, portrait shot |
| 19 | Determined | (same base) + determined mood, firm shape, portrait shot |
| 20 | Singing | (same base) + singing mood, vibrating softly, portrait shot |
| 21 | Whistling | (same base) + whistling mood, wind sounds, portrait shot |
| 22 | Blowing Kiss | (same base) + blowing kiss mood, sending a puff, portrait shot |
| 23 | Winking | (same base) + winking mood, one side of face closing, portrait shot |

---

## Form/Position Generation Prompts

Use template: `{name}, {species}, {appearance}, {form_position} position, full scene, {style}`

| # | Form/Position | Description |
|---|--------------|-------------|
| 1 | Drifting | Drifting slowly across sky, full scene |
| 2 | Floating | Floating gently in place, full scene |
| 3 | Gliding | Gliding smoothly with wind, full scene |
| 4 | Bouncing | Bouncing lightly in breeze, full scene |
| 5 | Hovering | Hovering still over a spot, full scene |
| 6 | Resting | Resting against a mountain, full scene |
| 7 | Spreading | Spreading out wide, thin, full scene |
| 8 | Dancing | Dancing with the wind, shifting shapes, full scene |
| 9 | Sleeping | Sleeping slowly drifting, relaxed, full scene |
| 10 | Peeking | Peeking from behind another cloud, full scene |
| 11 | Reaching | Reaching down toward earth, full scene |
| 12 | Pointing | Pointing a wisp toward something, full scene |
| 13 | Gathering | Gathering with other clouds, full scene |
| 14 | Waving | Waving a wisp goodbye, full scene |
| 15 | Hugging | Wrapping around a mountain or friend, full scene |
| 16 | Playing | Playing shape-shifting game, full scene |
| 17 | Rising | Rising up higher in sky, full scene |
| 18 | Shifting | Shifting into animal shapes, full scene |
| 19 | Protecting | Protecting below from harsh sun, broad, full scene |
| 20 | Sinking | Sinking low near horizon, full scene |

---

## Appearance Variations

Use template: `{name}, {species}, {appearance_variant} appearance, full scene, {style}`

| # | Variation | Description |
|---|-----------|-------------|
| 1 | Puffy White | Classic rounded cloud, soft white, smiling |
| 2 | Storyteller | Shifting shapes — bunny, heart, tree, dragon |
| 3 | Rain Cloud | Sad mood, gray edges, gentle drizzle falling |
| 4 | Sunset Cloud | Painted pink and orange by the setting Sun |
| 5 | Rainbow Friend | Holding Rainbow in the sky, edges colorful |
| 6 | Sleeping Cloud | Slow drifting, face relaxed, soft edges |
| 7 | Playful Cloud | Quick shape changes, game of guess me |
| 8 | Protective Cloud | Broader shape, shielding below from harsh sun |

---

## Age Variant Prompts

*Skipped — Cloud is ageless.*

---

## Lighting Variant Prompts

Use template: `{name}, {species}, {appearance}, {lighting} lighting, {style}`

| Lighting | Description |
|----------|-------------|
| Morning | Soft morning lighting, warm tones |
| Afternoon | Bright afternoon lighting |
| Golden Hour | Warm golden hour glow, cloud blushes |
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

## Quality Checklist for Cloud

- [ ] Character is instantly recognizable as Cloud
- [ ] Smiling face is visible in the cloud fluff
- [ ] Color is soft white with cream undertones (not gray)
- [ ] Edges are puffy and soft (not sharp)
- [ ] Mood matches the requested emotion
- [ ] Cloud has gentle, kind expression
- [ ] No harsh lines or realistic cloud texture
- [ ] No watermarks, text, or logos
- [ ] Background is appropriate and child-friendly (sky scene)
- [ ] Lighting is soft and warm
- [ ] Style matches Cocomelon-inspired aesthetic
- [ ] Cloud looks fluffy and approachable (not stormy)
- [ ] Form/position matches the requested variant
- [ ] Character fills the frame appropriately for the type (portrait, full scene)

---

*Generated for AI Nursery Rhyme Studio — Universe Library*
*Version 1.0 — 2026-07-29*
