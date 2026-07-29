# Animation Negative Prompts

## Little Learning Town Studios

### Version 1.0

---

## What Are Negative Prompts?

Negative prompts tell the AI what NOT to include in the generated animation. They are as important as the main prompt. Always include negative prompts to prevent common animation problems.

---

## Base Negative Prompt

This is the default negative prompt for every animation. Add section-specific negatives as needed.

```
violent motion, camera shake, fast cuts, stiff movement,
robotic animation, jerky motion, limb distortion,
unnatural physics, aggressive expressions, horror,
dark lighting, glitches, low quality, text, watermark
```

---

## Motion Problems

Use with every animation. Prevents common motion artifacts.

| Problem | Negative Prompt |
|---|---|
| General motion issues | `violent motion, camera shake, fast cuts, stiff movement, robotic animation, jerky motion` |
| Limb problems | `limb distortion, broken joints, popping joints, contortion, unnatural arm positions` |
| Physics issues | `unnatural physics, floating, sliding feet, moonwalking, skating on ground` |
| Freezing/stuttering | `freezing, stuttering, twitching, frame skipping, strobing` |
| Ground contact | `sliding feet, foot skating, floating above ground, clipping through floor` |
| Weight problems | `weightless, too heavy, stomping, stomping motion` |

### Combined Block

Use this block when motion quality is the primary concern:

```
violent motion, camera shake, fast cuts, stiff movement,
robotic animation, jerky motion, limb distortion,
unnatural physics, twitching, freezing, popping,
sliding feet, broken joints, clipping, unnatural animation
```

---

## Facial Problems

Prevents uncanny or inappropriate expressions.

| Problem | Negative Prompt |
|---|---|
| General face issues | `aggressive expressions, dead eyes, blank stare, frozen face, expressionless` |
| Mismatch | `mismatched emotions, mismatched lip sync, wrong emotion` |
| Uncanny valley | `doll-like, mask-like, expressionless, uncanny valley, wax figure, mannequin` |
| Eye problems | `dead eyes, empty eyes, staring, unblinking, lazy eye, crossed eyes` |
| Mouth problems | `creepy smile, rictus grin, open mouth wrong, frozen jaw, moving mouth wrong` |

### Combined Block

Use when facial expressions are critical:

```
aggressive expressions, dead eyes, blank stare, frozen face,
mismatched emotions, doll-like, mask-like, expressionless,
creepy smile, uncanny valley, mannequin, wax figure
```

---

## Style Problems

Maintains the preschool/Cocomelon-inspired style.

| Problem | Negative Prompt |
|---|---|
| Wrong art style | `realistic proportions, adult animation, anime, manga, cartoon network style` |
| Mature content | `dark, horror, scary, violent, weapon, blood, injury, death, danger` |
| Wrong age group | `teen, adult, mature, gritty, edgy, dark fantasy` |
| Realism | `photorealistic, realistic textures, real skin, pores, wrinkles, realistic hair` |

### Combined Block

Use for every animation to protect studio style:

```
realistic proportions, adult animation, anime, manga, dark,
horror, scary, violent, weapon, blood, injury, mature content,
realistic textures, photorealistic, gritty
```

---

## Technical Problems

Prevents rendering and output artifacts.

| Problem | Negative Prompt |
|---|---|
| Quality | `low quality, low resolution, pixelated, blurry, out of focus` |
| Glitches | `glitch, artifact, flicker, noise, grain, compression artifacts` |
| Motion artifacts | `jitter, stutter, frame drop, motion blur artifacts, ghosting` |
| Rendering | `render error, missing textures, broken mesh, wireframe, untextured` |

### Combined Block

```
low quality, glitch, artifact, flicker, noise, grain,
compression artifacts, jitter, stutter, frame drop,
pixelated, blurry, low resolution, render error
```

---

## Composition Problems

Prevents framing and branding issues.

| Problem | Negative Prompt |
|---|---|
| Text/issues | `text, watermark, logo, signature, subtitle in image, caption` |
| Framing | `border, frame, out of frame, cropped awkwardly, cut off` |
| UI | `ui overlay, hud, menu, icon, button, interface` |
| Distractions | `cluttered background, confusing composition, busy` |

### Combined Block

```
text, watermark, logo, signature, border, frame,
subtitle in image, out of frame, cropped awkwardly,
ui overlay, hud, menu, icon, button
```

---

## Per-Animation-Type Negatives

### Walk/Run Cycles

Add to base negatives when generating walk or run animations:

```
limping, sliding, moonwalk, floating, foot skating,
uneven gait, dragging foot, hopping, stumbling,
tripping, falling, off-balance, staggered steps
```

### Dance Loops

Add to base negatives when generating dance animations:

```
jerky, off-beat, uncoordinated, flailing, wild movement,
erratic, stumbling, off-rhythm, out of sync,
robotic dance, stiff dance, frozen pose
```

### Facial Expressions

Add to base negatives for close-up facial animation:

```
frozen, twitching, asymmetric, drooping, lopsided,
half-closed eye, lazy eyelid, twitching eyebrow,
wrong eyebrow position, mismatched brows
```

### Interactions (Object Handling)

Add to base negatives when characters interact with objects:

```
floating objects, wrong hand, wrong position,
clipping into object, object passing through hand,
object phasing, disappearing object, wrong grip,
misaligned hands, hovering item
```

### Jump/Hop Animations

Add when generating jumping or hopping motions:

```
floating, too heavy, no gravity, hanging in air,
stiff landing, no impact, no weight shift,
uneven landing, wobbling, stumbling after
```

### Singing/Talking

Add for close-up dialogue or singing scenes:

```
frozen jaw, mismatched lip sync, mouth not moving,
open mouth stuck, wrong mouth shape, no expression,
emotionless, monotone expression
```

---

## Quick Reference Combinations

### Standard Animation

```
violent motion, camera shake, fast cuts, stiff movement,
robotic animation, jerky motion, limb distortion,
unnatural physics, aggressive expressions, horror,
dark lighting, glitches, low quality, text, watermark,
realistic proportions, adult animation, anime, manga
```

### Walk or Run Animation

Add to Standard:

```
limping, sliding, moonwalk, floating, foot skating,
uneven gait, dragging foot
```

### Dance Animation

Add to Standard:

```
jerky, off-beat, uncoordinated, flailing, wild movement,
erratic, off-rhythm, out of sync, robotic dance
```

### Facial Expression

Add to Standard:

```
frozen, twitching, asymmetric, drooping, lopsided,
dead eyes, blank stare, expressionless, doll-like,
mask-like, uncanny valley
```

### Interaction with Object

Add to Standard:

```
floating objects, wrong hand, wrong position,
clipping into object, object passing through hand,
misaligned hands, hovering item
```

### Song/Dance Scene

Add to Standard:

```
jerky, off-beat, uncoordinated, flailing, frozen jaw,
mismatched lip sync, no expression, out of sync,
emotional mismatch

```

---

## Notes

- Always include the **Base Negative Prompt** as a minimum.
- Layer **Per-Animation-Type Negatives** on top depending on the scene.
- If the AI tends to add watermarks or logos, repeat `watermark, logo, signature` twice.
- For characters with tails/ears/accessories, add `missing tail, missing ears, accessory disappearing` to prevent secondary body parts from vanishing.

---

*Document maintained by Little Learning Town Studios — Animation Department*
