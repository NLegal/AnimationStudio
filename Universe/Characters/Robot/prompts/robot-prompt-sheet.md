# Robot — Prompt Reference Sheet

> **Version:** 1.0
> **Character:** Robot (Built recently)
> **Style:** Cocomelon-inspired, Pixar-quality, bright colorful nursery world

---

## Character Card

| Attribute | Value |
|-----------|-------|
| Name | Robot |
| Species | Robot |
| Appearance | Silver metallic smooth body, round screen face that displays expressions, blue LED eyes, small silver antenna with glowing blue tip, wheels instead of feet, cylindrical body with round head, spindly jointed claw-like gentle hands, colored decorative buttons on chest, speaker grill on chest |
| Default Form | Active — standing tall, screen bright, antenna glowing |
| Style | Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| Signature Accessory | Screen face with expressions, antenna with glowing tip |

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{name}` | Character name | Robot |
| `{species}` | Species description | Robot |
| `{appearance}` | Physical appearance | Silver metallic body, round screen face, blue LED eyes, ... |
| `{form}` | Current form/state | Active, Learning, Helping |
| `{form_variant}` | Alternate form | Charging, Confused, Happy |
| `{expression}` | Screen expression | Happy emoji, Question marks, Stars |
| `{pose}` | Pose name | Standing, Rolling, Helping |
| `{angle}` | Camera angle | Front, 3/4, Profile, Back |
| `{lighting}` | Lighting condition | Golden hour, Morning, Night |
| `{style}` | Visual style | Pixar-quality, Cocomelon-inspired, ... |

---

## Expression Generation Prompts

Use template: `{name}, {species}, {appearance}, screen showing {expression} expression, portrait shot, {style}`

| # | Screen Expression | Prompt Snippet |
|---|-------------------|---------------|
| 1 | Neutral flat expression | Robot, Robot, silver metallic smooth body, round screen face that displays expressions, blue LED eyes, small silver antenna with glowing blue tip, wheels instead of feet, cylindrical body with round head, spindly jointed claw-like gentle hands, colored decorative buttons on chest, speaker grill on chest, screen showing neutral flat expression, portrait shot, Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| 2 | Happy smile emoji | (same base) + screen showing happy smile emoji, portrait shot |
| 3 | Very happy big smile | (same base) + screen showing very happy big smile emoji, portrait shot |
| 4 | Laughing emoji | (same base) + screen showing laughing emoji, portrait shot |
| 5 | Giggle emoji | (same base) + screen showing giggling emoji, portrait shot |
| 6 | Smiling emoji | (same base) + screen showing warm smiling emoji, portrait shot |
| 7 | Excited starry eyes | (same base) + screen showing excited starry eyes emoji, portrait shot |
| 8 | Surprised wide eyes | (same base) + screen showing surprised wide eyes emoji, portrait shot |
| 9 | Confused question marks | (same base) + screen showing confused question marks, portrait shot |
| 10 | Thinking with ellipsis | (same base) + screen showing thinking with ellipsis, portrait shot |
| 11 | Curious magnifying glass | (same base) + screen showing curious magnifying glass emoji, portrait shot |
| 12 | Sleepy closed eyes Zzz | (same base) + screen showing sleepy closed eyes with Zzz, portrait shot |
| 13 | Yawning open mouth | (same base) + screen showing yawning open mouth emoji, portrait shot |
| 14 | Crying teardrop emoji | (same base) + screen showing crying teardrop emoji, portrait shot |
| 15 | Sad frown emoji | (same base) + screen showing sad frown emoji, portrait shot |
| 16 | Scared wide shake | (same base) + screen showing scared wide eyes shaking emoji, portrait shot |
| 17 | Embarrassed blush | (same base) + screen showing embarrassed blush pink glow, portrait shot |
| 18 | Proud star medal | (same base) + screen showing proud star medal emoji, portrait shot |
| 19 | Determined focused | (same base) + screen showing determined focused expression, portrait shot |
| 20 | Singing music notes | (same base) + screen showing singing music notes emoji, portrait shot |
| 21 | Whistling emoji | (same base) + screen showing whistling emoji, portrait shot |
| 22 | Blowing kiss heart | (same base) + screen showing blowing kiss heart emoji, portrait shot |
| 23 | Winking emoji | (same base) + screen showing winking emoji, portrait shot |

---

## Pose Generation Prompts

Use template: `{name}, {species}, {appearance}, {pose} pose, full body, {style}`

| # | Pose | Description |
|---|------|-------------|
| 1 | Standing | Standing on wheels, full body |
| 2 | Rolling | Rolling forward pose, full body |
| 3 | Rolling Fast | Rolling fast pose, full body |
| 4 | Jumping | Jumping with booster pose, full body |
| 5 | Gliding | Gliding smoothly pose, full body |
| 6 | Sitting | Sitting on docking station pose, full body |
| 7 | Kneeling | Kneeling pose, full body |
| 8 | Dancing | Spinning dance pose, full body |
| 9 | Sleeping | Charging pose, docked, screen dim, full body |
| 10 | Reading | Reading pose, scanning a book, full body |
| 11 | Writing | Writing with claw pose, full body |
| 12 | Pointing | Pointing arm extended pose, full body |
| 13 | Clapping | Clapping claws together pose, full body |
| 14 | Waving | Waving arm raised pose, full body |
| 15 | Hugging | Hugging arms extended pose, full body |
| 16 | Holding Hands | Holding claws with friend pose, full body |
| 17 | Helping | Helping arms extended pose, tools out, full body |
| 18 | Computing | Computing pose, screen active with data, full body |
| 19 | Spinning | Spinning on wheels pose, full body |
| 20 | Charging | Charging pose, docked, pulsing blue light, full body |

---

## Forms/States Generation

Use template: `{name}, {species}, {appearance}, {form_variant}, front view, full body, {style}`

| # | Form/State | Description |
|---|------------|-------------|
| 1 | Active | Standing tall, screen bright, antenna glowing |
| 2 | Learning | Screen showing book emoji, head tilted |
| 3 | Helping | Arms extended, screen showing tools |
| 4 | Charging | Docked, screen dim, pulsing blue light |
| 5 | Confused | Screen showing question marks, head rotation |
| 6 | Happy | Screen showing big smile emoji, bouncing |
| 7 | Sad | Screen showing teardrop, dim lights |
| 8 | Excited | Screen stars and exclamation, rapid beeps |

---

## Age Variant Prompts

*Skipped — Robot is a fixed design.*

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

## Quality Checklist for Robot

- [ ] Character is instantly recognizable as Robot
- [ ] Screen face is displaying the correct expression
- [ ] Blue LED eyes are visible and glowing
- [ ] Antenna with glowing tip is present
- [ ] Body is silver metallic and smooth
- [ ] Wheels are visible instead of feet
- [ ] Proportions are cute and child-friendly (not intimidating machine)
- [ ] Screen expression matches the requested emotion
- [ ] No anatomical deformities (extra arms, missing features)
- [ ] No watermarks, text, or logos
- [ ] Background is appropriate and child-friendly (workshop or classroom)
- [ ] Lighting is soft and warm
- [ ] Style matches Cocomelon-inspired aesthetic
- [ ] Claw-like hands are gentle-looking (not sharp)
- [ ] Character fills the frame appropriately for the type (portrait, full body)

---

*Generated for AI Nursery Rhyme Studio — Universe Library*
*Version 1.0 — 2026-07-29*
