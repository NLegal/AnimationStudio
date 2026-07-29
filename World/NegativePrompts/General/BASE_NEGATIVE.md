# BASE NEGATIVE PROMPT — Little Learning Town

This is the master base negative prompt applied to **ALL generations**. Combine it with category-specific negatives from the other negative prompt files.

---

## Danger / Scary

dark, abandoned, dirty, graffiti, broken windows, cracked roads, trash, blood, violence, weapons, fire, explosion, realistic decay, horror, foggy apocalypse, ruins, industrial pollution, scary, frightening, creepy, haunted, threatening, ominous, despair, sad, lonely, fearful, terrified, crying, distressed, injured, sick, diseased, toxic, dangerous, unsafe, hostile, aggressive, angry, evil, demonic, sinister, grim

## Quality

low quality, blurry, text, watermark, logo, signature, distorted, bad anatomy, ugly, deformed, mutated, disfigured, poorly drawn, low resolution, pixelated, compression artifacts, noise, grain, oversaturated, undersaturated, washed out, amateur, unfinished, sketchy, rough, messy, smudged, incomplete, corrupted, jpeg artifacts

## Style Mismatches

photorealistic, realistic, 3d render, live-action, anime, manga, live action, film grain, cel shaded, comic book style, oil painting, charcoal sketch, pencil drawing, black and white, sepia, monochrome, grunge, gothic, cyberpunk, steampunk, dark fantasy, horror style, zombie, skeleton, ghost, vampire, monster

## Coherence / Spatial

inconsistent perspective, mismatched scale, floating objects, clipping, overlapping elements, misaligned, unnatural proportions, distorted perspective, impossible geometry, vanishing point mismatch

## Usage

Combine this base negative with the relevant category-specific negative file:

```
# Environment generation example
Prompt: ...
Negative: [BASE_NEGATIVE] + [ENVIRONMENT_NEGATIVES] + [LIGHTING_NEGATIVES]
```
