# Animation Prompt Templates

## Little Learning Town Studios

### Version 1.0

---

## How to Write Effective Animation Prompts

An animation prompt is the instruction you give to an AI animation model (or human animator) to generate a specific motion sequence. A well-written prompt produces consistent, on-brand, child-friendly animation every time.

**Golden Rules:**

1. **Start with the character** — "Lily Bunny" rather than just "a bunny"
2. **Describe the action clearly** — "walks forward slowly" not "moves"
3. **Set the emotional tone** — "happily" or "curiously" or "gently"
4. **Specify the environment** — use an `[environment]` placeholder you fill from the environment library
5. **Add camera direction** — use a `[camera style]` placeholder from the camera library
6. **Close with style qualifiers** — "Pixar-quality, consistent character motion, child-friendly"
7. **Loop animations** where appropriate — "smooth preschool walk cycle" or "playful skip loop"

**Placeholder Convention:**

| Placeholder | Purpose | Example |
|---|---|---|
| `[character]` | Character name | Lily Bunny |
| `[environment]` | Scene location | Sunny Garden Playground |
| `[camera style]` | Camera shot type | Gentle tracking shot |
| `[emotion]` | Character feeling | happy, curious, excited |
| `[prop]` | Object involved | red ball, apple, book |

---

## Base Animation Prompt Structure

```
[character] [action] [emotion], [detail_1], [detail_2], ... [detail_N],
[environment], [camera style],
[style_tags],
[quality_tags]
```

**Example:**

```
Lily Bunny walks forward happily, gentle steps, soft arm swing,
warm smile, natural blinking, soft dress movement,
Sunny Garden Playground,
gentle tracking shot medium,
Cocomelon-inspired, Pixar-quality, smooth preschool walk cycle,
consistent character motion, child-friendly, high-quality animation
```

---

## Walk Cycles

### Slow Walk

```
[character] slowly walks forward, gentle steps, soft arm swing,
warm smile, natural breathing, subtle head bob,
[environment], [camera style],
smooth preschool walk cycle, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Medium wide shot. Gentle tracking or static. Stay at character eye level.
- **Lighting notes:** Soft, warm, diffused. No harsh shadows.
- **Timing notes:** 24fps. Each step takes ~12 frames. Loop length: 24 frames (2 steps).

---

### Normal Walk (Bunny)

```
Lily Bunny walks forward at a comfortable pace, gentle arm swing,
ears gently bouncing, soft dress swaying, warm expression,
natural blinking, subtle breathing,
[environment], [camera style],
Cocomelon-inspired walk cycle, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Medium shot. Slight tracking or locked off.
- **Lighting notes:** Bright, cheerful, even lighting.
- **Timing notes:** 24fps. Each step ~8 frames. Loop length: 16 frames (2 steps).

---

### Normal Walk (Bear)

```
Benny Bear walks forward at a comfortable pace, gentle arm swing,
soft tummy bounce, warm smile, natural blinking, subtle breathing,
[environment], [camera style],
Cocomelon-inspired walk cycle, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Medium shot. Slightly lower angle for bear height.
- **Lighting notes:** Bright, cheerful, even lighting.
- **Timing notes:** 24fps. Each step ~10 frames (slightly slower for bear). Loop length: 20 frames.

---

### Normal Walk (Duck)

```
Daisy Duck waddles forward, gentle side-to-side motion,
wings slightly out for balance, happy expression, soft quiver,
[environment], [camera style],
preschool waddle cycle, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Medium wide shot to accommodate waddle motion.
- **Lighting notes:** Bright, cheerful, even lighting.
- **Timing notes:** 24fps. Each step ~8 frames. Loop length: 16 frames. More lateral sway than bipedal characters.

---

### Normal Walk (Cat)

```
Charlie Cat walks forward gracefully, tail gently swaying,
soft paw steps, alert ears, curious expression, natural blinking,
[environment], [camera style],
smooth cat walk cycle, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Medium shot. Character eye level.
- **Lighting notes:** Bright, cheerful, even lighting.
- **Timing notes:** 24fps. Each step ~8 frames. Loop length: 16 frames.

---

### Happy Skip

```
[character] skips joyfully, bouncy steps, arms up, big smile,
happy eyes, light and floaty, ears/accessories bouncing,
[environment], [camera style],
playful skip loop, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Medium wide shot. Gentle tracking to follow the skip path.
- **Lighting notes:** Bright, warm, sunny feel. Slight lens flare optional.
- **Timing notes:** 24fps. Skip cycle: 12 frames per skip. Loop length: 24 frames.

---

## Run Cycles

### Excited Run

```
[character] runs excitedly, quick but gentle steps, big smile,
arms pumping softly, eyes bright, ears/accessories bouncing,
[environment], [camera style],
playful run cycle, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly, no aggressive motion
```

- **Camera notes:** Wide shot or tracking shot. Keep character centered.
- **Lighting notes:** Bright, energetic lighting.
- **Timing notes:** 24fps. Each step ~6 frames. Loop length: 12 frames. Keep speed moderate — no frantic motion.

---

### Play Chase

```
[character] runs playfully looking back, giggling expression,
happy eyes, soft arm pump, gentle bounce,
[environment], [camera style],
playful chase run, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Wide tracking shot. Camera at slight side angle.
- **Lighting notes:** Bright outdoor lighting. Warm tones.
- **Timing notes:** 24fps. Each step ~6 frames. Moderate speed, playful rather than urgent.

---

### Small Sprint

```
[character] sprints in short burst, fast little steps,
determined happy expression, arms pumping, big grin,
[environment], [camera style],
short sprint cycle, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly, no frantic motion
```

- **Camera notes:** Wide shot or side-profile tracking.
- **Lighting notes:** Bright dynamic lighting.
- **Timing notes:** 24fps. Each step ~4-5 frames. Short duration only (2-3 seconds max).

---

## Dance Loops

### Side-to-Side Dance

```
[character] dances side to side, shifting weight playfully,
happy expression, arms swaying, gentle hip movement,
ears/accessories bouncing with rhythm,
[environment], [camera style],
simple side-to-side dance loop, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Medium shot. Static camera.
- **Lighting notes:** Bright, colorful party lighting.
- **Timing notes:** 24fps. 4-beat loop: 24 frames total.

---

### Circle Dance

```
[character] dances in a circle, spinning slowly, arms out,
joyful expression, twirling with gentle momentum,
ears/accessories floating outward,
[environment], [camera style],
circle dance loop, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Wide shot. Static camera to show full motion.
- **Lighting notes:** Warm, festive lighting.
- **Timing notes:** 24fps. Full rotation: 48 frames (2 seconds).

---

### Clap Dance

```
[character] dances while clapping hands, happy bouncing,
rhythmic claps, big smile, head nodding to beat,
[environment], [camera style],
clap dance loop, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Medium shot. Focus on upper body.
- **Lighting notes:** Bright, cheerful stage lighting.
- **Timing notes:** 24fps. 4-beat loop: 24 frames. Clap on beats 2 and 4.

---

### Spin

```
[character] spins around playfully, arms extended,
joyful expression, soft blur on fast rotation,
ears/accessories trailing behind,
[environment], [camera style],
playful spin loop, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Wide shot. Static.
- **Lighting notes:** Soft glowing light.
- **Timing notes:** 24fps. Spin: 24 frames per rotation. 1-2 rotations.

---

## Facial Expressions

### Happy Smile

```
[character] smiles warmly, eyes crinkling happily,
gentle head tilt, soft blush on cheeks,
[environment], [camera style],
close-up happy expression, Cocomelon-inspired, Pixar-quality,
preschool-friendly, warm and inviting
```

- **Camera notes:** Close-up. Eye level.
- **Lighting notes:** Soft front lighting. Warm tones.
- **Timing notes:** Hold 3-5 seconds. Slow ease-in.

---

### Surprised Gasp

```
[character] gasps in happy surprise, eyes wide open,
mouth forming small O, eyebrows raised, leaning back slightly,
[environment], [camera style],
close-up surprise expression, Cocomelon-inspired, Pixar-quality,
preschool-friendly, playful surprise
```

- **Camera notes:** Close-up. Slight push-in on reaction.
- **Lighting notes:** Bright pop of light on reaction.
- **Timing notes:** Quick onset (4 frames), hold 2 seconds, slow release.

---

### Sad Cry

```
[character] looks sad, eyes welling up, lower lip trembling,
gentle frown, one tear rolling down cheek, sniffling,
[environment], [camera style],
close-up sad expression, Cocomelon-inspired, Pixar-quality,
preschool-friendly, gentle sadness, not frightening
```

- **Camera notes:** Close-up. Soft focus on eyes.
- **Lighting notes:** Softer, slightly cooler but still warm.
- **Timing notes:** Slow onset (12 frames), hold 3-4 seconds, slow recovery.

---

### Curious Tilt

```
[character] tilts head curiously, eyebrows slightly raised,
eyes looking up and to the side, gentle thoughtful expression,
mouth slightly open,
[environment], [camera style],
close-up curious expression, Cocomelon-inspired, Pixar-quality,
preschool-friendly, inquisitive
```

- **Camera notes:** Close-up. Eye level.
- **Lighting notes:** Bright, even lighting.
- **Timing notes:** Slow tilt (8 frames), hold 2-3 seconds.

---

### Excited Jump

```
[character] jumps up with excitement, eyes wide and sparkling,
huge smile, arms shooting up, bouncing on landing,
[environment], [camera style],
excited jump expression, Cocomelon-inspired, Pixar-quality,
preschool-friendly, pure joy
```

- **Camera notes:** Medium shot to capture full body bounce.
- **Lighting notes:** Bright, warm. Glint in eyes.
- **Timing notes:** Jump up: 6 frames, apex hold: 4 frames, land: 6 frames.

---

### Thinking Pose

```
[character] looks thoughtful, one hand on chin,
eyes looking upward, slight head tilt, gentle humming expression,
[environment], [camera style],
close-up thinking pose, Cocomelon-inspired, Pixar-quality,
preschool-friendly, thoughtful
```

- **Camera notes:** Medium close-up. Eye level.
- **Lighting notes:** Soft, slightly dimmer for thoughtful mood — but still warm.
- **Timing notes:** Slow ease-in (10 frames), hold 3-4 seconds.

---

## Interactions

### Open Door

```
[character] reaches for [prop/door handle], grasps gently,
turns handle, pushes door open, steps forward,
happy expression, natural motion,
[environment], [camera style],
door opening interaction, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Medium shot. Side or over-the-shoulder.
- **Lighting notes:** Interior warm light spilling through doorway.
- **Timing notes:** Reach: 8 frames, grasp: 4 frames, push: 12 frames, step through: 8 frames.

---

### Eat Apple

```
[character] holds [prop/apple] gently, brings to mouth,
takes small bite, chews happily, eyes closed contentedly,
swallows, smiles,
[environment], [camera style],
eating apple interaction, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Medium close-up. Focus on face and hand holding apple.
- **Lighting notes:** Bright, warm, appetizing lighting.
- **Timing notes:** Raise to mouth: 8 frames, bite: 4 frames, chew: 16 frames (4 chews), swallow: 4 frames, smile: 8 frames.

---

### Kick Ball

```
[character] approaches [prop/ball], pulls foot back,
kicks gently, ball rolls forward, follows with eyes,
claps happily,
[environment], [camera style],
kicking ball interaction, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Wide shot. Side angle shows full kicking motion.
- **Lighting notes:** Bright outdoor lighting.
- **Timing notes:** Approach: 12 frames, wind up: 8 frames, kick: 4 frames, follow through: 6 frames.

---

### Build Blocks

```
[character] picks up [prop/block], places carefully on tower,
adjusts position, reaches for next block, focused expression,
gentle stacking motion,
[environment], [camera style],
building blocks interaction, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Medium shot. Overhead or 3/4 angle.
- **Lighting notes:** Bright, even playroom lighting.
- **Timing notes:** Reach: 6 frames, grasp: 4 frames, lift: 6 frames, place: 8 frames, release: 4 frames.

---

### Brush Teeth

```
[character] holds [prop/toothbrush], applies toothpaste,
brings to mouth, brushes gently in circular motion,
humming happily, foamy mouth, rinses,
[environment], [camera style],
brushing teeth interaction, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Medium close-up. Bathroom mirror angle or side view.
- **Lighting notes:** Bright bathroom lighting. Clean, fresh feel.
- **Timing notes:** Apply toothpaste: 8 frames, brush each quadrant: 24 frames (3 seconds each), rinse: 12 frames.

---

### Wash Hands

```
[character] turns on [prop/faucet], wets hands,
applies soap, rubs hands together in circular motion,
rinses under water, shakes gently, dries on towel,
cheerful expression,
[environment], [camera style],
washing hands interaction, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Medium shot. Side or over-the-shoulder at sink height.
- **Lighting notes:** Bright, clean bathroom lighting.
- **Timing notes:** Turn on water: 6 frames, wet: 8 frames, soap: 6 frames, rub: 24 frames (sing ABCs), rinse: 12 frames, dry: 12 frames.

---

### Plant Flower

```
[character] holds [prop/seedling], digs small hole gently,
places seedling in, covers with soil, pats down,
pours water from [prop/watering can], wipes brow, smiles proudly,
[environment], [camera style],
planting flower interaction, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Wide shot or medium shot. Ground level or slight overhead.
- **Lighting notes:** Warm sunlight. Gentle god rays optional.
- **Timing notes:** Dig: 12 frames, place seedling: 6 frames, cover: 10 frames, water: 16 frames.

---

### Blow Out Candle

```
[character] looks at [prop/cake with candle], leans in,
purses lips, blows gently, flame extinguishes,
claps happily, big smile,
[environment], [camera style],
blowing candle interaction, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Medium close-up. Side or front angle.
- **Lighting notes:** Warm candlelight glow. Darker room with cake illumination.
- **Timing notes:** Lean in: 8 frames, purse lips: 4 frames, blow: 6 frames, flame out: 2 frames, clap: 8 frames.

---

## Scene Types

### Character Introduction

```
[character] enters frame cheerfully, waves at camera,
big welcoming smile, gentle bounce, introduces self with name,
[environment], [camera style],
character introduction sequence, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Medium wide shot. Slow push-in as character enters.
- **Lighting notes:** Bright, welcoming spotlight on character.
- **Timing notes:** Enter frame: 16 frames, wave: 24 frames (2 waves), hold pose: 24 frames.

---

### Conversation

```
[character A] and [character B] face each other,
[character A] speaks with expressive gestures,
[character B] listens attentively nodding,
alternating focus, natural blinking, gentle head tilts,
[environment], [camera style],
conversation scene, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly
```

- **Camera notes:** Over-the-shoulder alternating. Medium two-shot for wide. Close-ups for reactions.
- **Lighting notes:** Warm, even two-character lighting.
- **Timing notes:** Speaker holds for 3-5 seconds, listener reacts every 2-3 seconds. Shot changes every 4-6 seconds.

---

### Educational Moment

```
[character] points to [prop/visual aid], looks at camera,
explains with gentle gestures, nods encouragingly,
curious expression, patient demeanor,
[environment], [camera style],
educational scene, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly, clear readable motion
```

- **Camera notes:** Medium shot. Slow push-in for emphasis. Cut to close-up of teaching prop.
- **Lighting notes:** Bright, clear lighting. High visibility.
- **Timing notes:** Point and explain: 4-6 seconds per concept. Pause between ideas.

---

### Song and Dance

```
[character] sings joyfully, dances to music,
full body movement, expressive face, eyes sparkling,
arms gesturing to lyrics, bouncing to rhythm,
[environment], [camera style],
musical performance, Cocomelon-inspired, Pixar-quality,
consistent character motion, child-friendly, energetic but soft
```

- **Camera notes:** Wide shot for dance. Medium close-ups for singing. Dynamic but smooth cuts.
- **Lighting notes:** Colorful, musical lighting. Soft backlight for glow effect.
- **Timing notes:** Sync to 120bpm music = 24 frames per 2 beats. Hold chorus shots 4-8 seconds.

---

## Additional Notes

- **Always review the negative prompts** before generating (see animation-negatives.md).
- **Preview each generated animation** against the Quality Checklist (see QUALITY_CHECKLIST.md).
- **Templates are starting points** — adjust timing, camera, and energy to match specific scene needs.
- **Maintain consistency** across episodes by reusing the same template modifications.

---

*Document maintained by Little Learning Town Studios — Animation Department*
