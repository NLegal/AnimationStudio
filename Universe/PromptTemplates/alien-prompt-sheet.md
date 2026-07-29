# Alien — Prompt Reference Sheet

> **Version:** 1.0
> **Character:** Alien (Unknown age)
> **Style:** Cocomelon-inspired, Pixar-quality, bright colorful nursery world

---

## Character Card

| Attribute | Value |
|-----------|-------|
| Name | Alien |
| Species | Alien (unknown origin) |
| Appearance | Mint green smooth slightly luminescent skin, three big eyes (left pink, center yellow, right blue), small antenna on head with glowing orb tips, slim small frame, spindly long arms with three-fingered hands, thin legs that float rather than walk, small expressive mouth |
| Default Form | Floating — drifting gently, eyes wide, curious |
| Style | Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| Signature Accessory | Three colorful eyes (pink, yellow, blue), antenna with glowing orbs |

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{name}` | Character name | Alien |
| `{species}` | Species description | Alien (unknown origin) |
| `{appearance}` | Physical appearance | Mint green luminescent skin, three big eyes, ... |
| `{form}` | Current form/state | Floating, Observing, Exploring |
| `{form_variant}` | Alternate form | Sleeping curled midair, Translating |
| `{expression}` | Expression name | Happy, Surprised, Sad |
| `{pose}` | Pose name | Floating, Drifting, Exploring |
| `{angle}` | Camera angle | Front, 3/4, Profile, Back |
| `{lighting}` | Lighting condition | Golden hour, Morning, Night |
| `{style}` | Visual style | Pixar-quality, Cocomelon-inspired, ... |

---

## Expression Generation Prompts

Use template: `{name}, {species}, {appearance}, {expression} expression, portrait shot, {style}`

| # | Expression | Prompt Snippet |
|---|------------|---------------|
| 1 | Neutral | Alien, Alien (unknown origin), mint green smooth slightly luminescent skin, three big eyes (left pink, center yellow, right blue), small antenna on head with glowing orb tips, slim small frame, spindly long arms with three-fingered hands, thin legs that float rather than walk, small expressive mouth, neutral expression, portrait shot, Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| 2 | Happy | (same base) + happy expression, all eyes bright, portrait shot |
| 3 | Very Happy | (same base) + very happy expression, portrait shot |
| 4 | Laughing | (same base) + laughing expression, portrait shot |
| 5 | Giggling | (same base) + giggling expression, portrait shot |
| 6 | Smiling | (same base) + smiling expression, portrait shot |
| 7 | Excited | (same base) + excited expression, bouncing in air, portrait shot |
| 8 | Surprised | (same base) + surprised expression, all eyes wide, portrait shot |
| 9 | Confused | (same base) + confused expression, eyes blinking one by one, portrait shot |
| 10 | Thinking | (same base) + thinking expression, antenna twitching, portrait shot |
| 11 | Curious | (same base) + curious expression, head tilted, portrait shot |
| 12 | Sleepy | (same base) + sleepy expression, eyes half-closed, portrait shot |
| 13 | Yawning | (same base) + yawning expression, mouth open, portrait shot |
| 14 | Crying | (same base) + crying expression, portrait shot |
| 15 | Sad | (same base) + sad expression, eyes dim, portrait shot |
| 16 | Scared | (same base) + scared expression, all eyes wide, portrait shot |
| 17 | Embarrassed | (same base) + embarrassed expression, portrait shot |
| 18 | Proud | (same base) + proud expression, portrait shot |
| 19 | Determined | (same base) + determined expression, portrait shot |
| 20 | Singing | (same base) + singing expression, happy bleeps, portrait shot |
| 21 | Whistling | (same base) + whistling expression, portrait shot |
| 22 | Blowing Kiss | (same base) + blowing kiss expression, portrait shot |
| 23 | Winking | (same base) + winking expression, one eye closing, portrait shot |

---

## Pose Generation Prompts

Use template: `{name}, {species}, {appearance}, {pose} pose, full body, {style}`

| # | Pose | Description |
|---|------|-------------|
| 1 | Floating | Floating gently pose, full body |
| 2 | Drifting | Drifting slowly pose, full body |
| 3 | Gliding | Gliding fast pose, full body |
| 4 | Bouncing | Bouncing up and down pose, full body |
| 5 | Hovering | Hovering still pose, full body |
| 6 | Sitting Midair | Sitting cross-legged midair pose, full body |
| 7 | Curled Midair | Curled in a ball midair pose, full body |
| 8 | Dancing | Floating dance pose, full body |
| 9 | Sleeping | Sleeping curled midair pose, soft glow, full body |
| 10 | Reading | Reading hovered over a book pose, full body |
| 11 | Writing | Writing in air with finger pose, full body |
| 12 | Pointing | Pointing arm extended pose, full body |
| 13 | Clapping | Clapping three-fingered hands pose, full body |
| 14 | Waving | Waving hand raised pose, full body |
| 15 | Hugging | Hugging arms around friend pose, full body |
| 16 | Holding Hands | Holding three-fingered hands with friend, floating, full body |
| 17 | Exploring | Exploring reaching out touching pose, full body |
| 18 | Translating | Translating antenna glowing pose, full body |
| 19 | Communicating | Communicating eyes flashing signals pose, full body |
| 20 | Stargazing | Stargazing floating upward pose, full body |

---

## Forms/States Generation

Use template: `{name}, {species}, {appearance}, {form_variant}, front view, full body, {style}`

| # | Form/State | Description |
|---|------------|-------------|
| 1 | Floating | Drifting gently, eyes wide, curious |
| 2 | Observing | Hovering still, eyes focusing, antenna twitching |
| 3 | Excited | Bouncing in air, eyes wide, rapid bleeps |
| 4 | Confused | Tilted floating, head tilted, eyes blinking one by one |
| 5 | Exploring | Reaching out, touching things gently |
| 6 | Translating | Antenna glowing, speaking in bleep-bops |
| 7 | Sleeping | Curled in a ball mid-air, soft glow pulsing |
| 8 | Communicating | Eyes flashing in sequence, antenna signals |

---

## Age Variant Prompts

*Skipped — Alien is ageless/unknown.*

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

## Quality Checklist for Alien

- [ ] Character is instantly recognizable as Alien
- [ ] Three eyes (pink, yellow, blue) are visible and bright
- [ ] Mint green skin is smooth and slightly luminescent
- [ ] Antenna with glowing orb tips are present
- [ ] Body is slim and small (not tall or scary)
- [ ] Three-fingered hands are visible
- [ ] Proportions are cute and alien-like (not human)
- [ ] Expression matches the requested emotion
- [ ] No anatomical deformities (extra limbs, missing features)
- [ ] No watermarks, text, or logos
- [ ] Background is appropriate and child-friendly (meadow or sky)
- [ ] Lighting is soft and warm
- [ ] Style matches Cocomelon-inspired aesthetic
- [ ] Alien looks friendly not scary
- [ ] Character fills the frame appropriately for the type (portrait, full body)

---

*Generated for AI Nursery Rhyme Studio — Universe Library*
*Version 1.0 — 2026-07-29*
