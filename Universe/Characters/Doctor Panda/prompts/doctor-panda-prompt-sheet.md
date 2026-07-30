# Doctor Panda — Prompt Reference Sheet

> **Version:** 1.0
> **Character:** Doctor Panda (Adult)
> **Style:** Cocomelon-inspired, Pixar-quality, bright colorful nursery world

---

## Character Card

| Attribute | Value |
|-----------|-------|
| Name | Doctor Panda |
| Species | Panda (white and black fur) |
| Appearance | White fur with black patches on arms, legs, ears and eye patches, dark brown soft kind eyes, round huggable body, small black triangle nose, tiny round white puff tail, gentle smile |
| Default Outfit | White lab coat over blue scrubs, stethoscope around neck, doctor's headband mirror |
| Style | Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
| Signature Accessory | Stethoscope, doctor's headband mirror |

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{name}` | Character name | Doctor Panda |
| `{species}` | Species description | Panda (white and black fur) |
| `{appearance}` | Physical appearance | White fur with black patches, dark brown kind eyes, ... |
| `{outfit}` | Outfit description | White lab coat over blue scrubs, stethoscope |
| `{outfit_variant}` | Alternate outfit | Cream sweater, soft brown pants |
| `{expression}` | Expression name | Happy, Surprised, Sad |
| `{pose}` | Pose name | Standing, Sitting, Listening |
| `{angle}` | Camera angle | Front, 3/4, Profile, Back |
| `{lighting}` | Lighting condition | Golden hour, Morning, Night |
| `{style}` | Visual style | Pixar-quality, Cocomelon-inspired, ... |

---

## Expression Generation Prompts

Use template: `{name}, {species}, {appearance}, wearing {outfit}, {expression} expression, portrait shot, {style}`

| # | Expression | Prompt Snippet |
|---|------------|---------------|
| 1 | Neutral | Doctor Panda, Panda (white and black fur), white fur with black patches on arms, legs, ears and eye patches, dark brown soft kind eyes, round huggable body, small black triangle nose, tiny round white puff tail, gentle smile, wearing white lab coat over blue scrubs, stethoscope around neck, doctor's headband mirror, neutral expression, portrait shot, Pixar-quality, Cocomelon-inspired, bright colorful nursery world, highly detailed, soft lighting, vibrant colors |
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
| 5 | Waddling | Waddling pose, full body |
| 6 | Sitting | Sitting pose, full body |
| 7 | Kneeling | Kneeling pose, full body |
| 8 | Dancing | Dancing pose, full body |
| 9 | Sleeping | Sleeping pose, full body |
| 10 | Reading | Reading pose, full body |
| 11 | Writing | Writing pose, full body |
| 12 | Pointing | Pointing pose, full body |
| 13 | Clapping | Clapping pose, paws together, full body |
| 14 | Waving | Waving pose, paw raised, full body |
| 15 | Hugging | Hugging pose, arms open, full body |
| 16 | Holding Hands | Holding paws with friend, full body |
| 17 | Listening | Listening to heartbeat with stethoscope, full body |
| 18 | Playing | Playing pose, full body |
| 19 | Swimming | Swimming pose, full body |
| 20 | Giving Checkup | Giving a gentle checkup pose, full body |

---

## Outfit Generation Prompts

Use template: `{name}, {species}, {appearance}, wearing {outfit_variant}, standing, front view, full body, {style}`

| # | Outfit | Description |
|---|--------|-------------|
| 1 | Daily Outfit | White lab coat over blue scrubs, stethoscope, headband mirror (signature look) |
| 2 | Casual | Cream sweater, soft brown pants |
| 3 | Winter Outfit | Blue puffy coat with hood, black boots |
| 4 | Rain Outfit | Yellow raincoat, matching boots |
| 5 | Pajamas | Soft green PJs with bamboo print |
| 6 | Exercise Gear | Sky blue tracksuit, white sneakers |
| 7 | Chef Apron | White apron with heart pocket, chef hat |
| 8 | Storytime Outfit | Comfy lavender cardigan |
| 9 | Halloween Costume | Dressed as a teddy bear |
| 10 | Christmas Outfit | Red vest with white trim, Santa hat |

---

## Age Variant Prompts

*Skipped — Doctor Panda is a fixed adult character.*

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

## Quality Checklist for Doctor Panda

- [ ] Character is instantly recognizable as Doctor Panda
- [ ] Stethoscope and headband mirror are visible
- [ ] Dark brown eyes are kind and expressive
- [ ] White lab coat over blue scrubs matches the signature look
- [ ] Black eye patches are distinct and symmetrical
- [ ] Fur is soft white (not gray or yellow)
- [ ] Proportions are panda-like (round and huggable)
- [ ] Expression matches the requested emotion
- [ ] No anatomical deformities (extra limbs, missing features)
- [ ] No watermarks, text, or logos
- [ ] Background is appropriate and child-friendly (clinic or park)
- [ ] Lighting is soft and warm
- [ ] Style matches Cocomelon-inspired aesthetic
- [ ] Nose is black and triangular
- [ ] Character fills the frame appropriately for the type (portrait, full body)

---

*Generated for AI Nursery Rhyme Studio — Universe Library*
*Version 1.0 — 2026-07-29*
