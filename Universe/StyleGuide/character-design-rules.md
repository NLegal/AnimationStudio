# Character Design Rules — Style Guide

> **Version:** 1.0
> **Style:** Cocomelon-inspired, Pixar-quality rendering
> **Applies to:** All 20 characters in the AI Nursery Rhyme Studio Universe

---

## Core Principles

Every character must follow the same design language. Consistency builds a recognizable brand. Never mix styles — do not suddenly generate anime, watercolor, or photorealistic characters.

### Design Language

- **Child-friendly:** No sharp edges, clean geometry, smooth skin, expressive faces
- **Colorful:** High saturation, vibrant colors, warm tones
- **Rounded:** Soft proportions, no harsh angles
- **Expressive:** Large eyes, visible emotions, exaggerated features
- **Simple:** Clean shapes, minimal detail where it doesn't matter

---

## Head

| Rule | Description |
|------|-------------|
| Size | Large relative to body (approximately 1:3 head-to-body ratio for preschoolers) |
| Shape | Rounded, soft curves |
| Proportions | Cute, child-like — oversized compared to realistic anatomy |

### Age Scaling

| Age Group | Head-to-Body Ratio | Notes |
|-----------|-------------------|-------|
| Toddler (2-3) | ~1:2.5 | Oversized head, very cute proportions |
| Preschool (4-5) | ~1:3 | Canonical design ratio |
| Kindergarten (5-6) | ~1:3.5 | Slightly more proportional, still cute |

---

## Eyes

| Rule | Description |
|------|-------------|
| Size | Large — approximately 1/3 of face height |
| Shape | Rounded or slightly oval |
| Iris | Large, fills most of the visible eye area |
| Highlights | Visible catchlights (2-3 per eye) for sparkle |
| Expressiveness | Highly expressive — eyebrows and eye shape carry emotion |
| Spacing | Wide-set — approximately one eye width apart |
| Color | Bright, saturated colors (green for Lily, blue for Ben, etc.) |

### Eye Shapes by Emotion

| Emotion | Eye Shape |
|---------|-----------|
| Happy | Arched bottom, slight squint |
| Sad | Drooping upper lid, downward slant |
| Surprised | Wide open, large iris visible |
| Angry | Angled inward, narrowed |
| Sleepy | Half-closed, drooping |
| Laughing | Closed in an arch (^ ^) |
| Curious | One slightly narrower, head tilt implied |

---

## Nose

| Rule | Description |
|------|-------------|
| Size | Small — minimal visual weight |
| Shape | Rounded, simple |
| Placement | Centered, low on face between eyes and mouth |
| Detail | Minimal — often just a small oval or dot |
| Species Variation | Animal characters get species-appropriate noses (round pink for bunnies, brown oval for bears, orange triangle for foxes) |

---

## Mouth

| Rule | Description |
|------|-------------|
| Size | Moderate — can stretch wide for big smiles |
| Shape | Simple curve |
| Default | Gentle smile in neutral expression |
| Teeth | Simple, cute — buck teeth for bunnies, flat for bears |
| Tongue | Occasionally visible in laughing expressions |
| Singing | Open, rounded — appropriate for singing poses |

### Mouth Shapes by Expression

| Expression | Mouth Shape |
|------------|-------------|
| Smiling | Gentle upward curve |
| Happy | Wide smile, teeth visible |
| Laughing | Wide open, tongue visible |
| Surprised | Small 'o' shape |
| Sad | Frown, slight downward curve |
| Crying | Open square, downturned |
| Singing | Open oval |
| Proud | Confident smile, one side slightly higher |

---

## Body

| Rule | Description |
|------|-------------|
| Proportions | Soft, rounded — no realistic anatomy |
| Limbs | Rounded, slightly pudgy |
| Torso | Short relative to legs |
| Neck | Short or minimal — head sits close to shoulders |
| Joints | Smooth transitions — no visible knuckles or joints |
| Silhouette | Instantly recognizable — each character has a distinct outline |

### Body Types by Category

| Category | Body Type | Examples |
|----------|-----------|----------|
| Main Characters | Soft, rounded, toddler-like proportions | Lily Bunny, Ben Bear, Daisy Duck, Charlie Fox |
| Family | Slightly taller, adult proportions but still cute | Mom Bunny, Dad Bunny |
| Friends | Similar to main characters, species-specific variations | Monkey, Elephant, Cat |
| Community | Adult proportions, profession-specific accessories | Teacher, Doctor, Firefighter |
| Fantasy | Varies by concept | Dragon, Unicorn, Robot |

---

## Hands

| Rule | Description |
|------|-------------|
| Fingers | Simple — 3-4 visible fingers per hand |
| Size | Large enough for expressive animation |
| Shape | Rounded fingertips, no sharp nails |
| Poses | Open for waving, closed for holding |
| Mittens | Winter characters may have mitten-style hands |

---

## Feet

| Rule | Description |
|------|-------------|
| Size | Oversized relative to legs |
| Shape | Rounded, shoe-like |
| Detail | Minimal — shoes are part of the design |
| Species | Animal characters get species-appropriate feet (paws for bears, webbed for ducks) |

---

## Color Guidelines

| Rule | Description |
|------|-------------|
| Palette | Use the brand palette — 5 primary + 5 pastel colors |
| Skin/Fur | Natural species colors (white bunny, brown bear, yellow duck) |
| Clothing | Bright, saturated — use brand palette colors |
| Avoid | Pure black, pure red, neon colors, dark desaturated tones |
| Background | Always light pastel or gradient, never solid dark |
| Contrast | High contrast between character and background |

See [`Universe/ColorPalette/brand-palette.json`](../ColorPalette/brand-palette.json) for the complete color reference.

---

## Expression Guidelines

All 22 expressions must be generated for every main character. Expressions should be:

1. **Exaggerated** — subtle expressions don't read well on young audiences
2. **Distinct** — each expression clearly different from others
3. **Consistent** — character is recognizable regardless of expression
4. **Child-friendly** — no scary or threatening expressions

### Expression List

| # | Expression | Key Visual Cues |
|---|------------|-----------------|
| 1 | Neutral | Relaxed face, gentle expression |
| 2 | Happy | Smile, slightly raised eyebrows |
| 3 | Very Happy | Wide smile, raised eyebrows, bright eyes |
| 4 | Laughing | Wide open mouth, closed or squinted eyes |
| 5 | Giggling | Hand near mouth, slightly squinted eyes |
| 6 | Smiling | Gentle warm smile, soft eyes |
| 7 | Excited | Wide eyes, open mouth, raised eyebrows |
| 8 | Surprised | Very wide eyes, dropped jaw or 'o' mouth |
| 9 | Confused | One eyebrow raised, slight head tilt |
| 10 | Thinking | Eyes looking up, finger on chin |
| 11 | Curious | Head tilted, wide eyes, slight smile |
| 12 | Sleepy | Half-closed eyes, slight droop |
| 13 | Yawning | Wide open mouth, closed eyes |
| 14 | Crying | Eyes squeezed shut, tears, downturned mouth |
| 15 | Sad | Drooping eyebrows, slight frown, teary eyes |
| 16 | Scared | Wide eyes, lowered eyebrows, open mouth |
| 17 | Embarrassed | Blush marks, eyes wide or avoiding, nervous smile |
| 18 | Proud | Chin up, confident smile, closed or half-closed eyes |
| 19 | Determined | Focused eyes, straight mouth, slight frown of concentration |
| 20 | Singing | Open mouth (oval), slightly closed eyes, joyful |
| 21 | Whistling | Pursed lips, slightly puffed cheeks |
| 22 | Blowing Kiss | Eyes closed, lips puckered, hand near mouth |
| 23 | Winking | One eye closed, one open, playful smile |

---

## Pose Guidelines

All 20 poses must be generated for every main character. Poses should be:

1. **Clear silhouette** — readable at small thumbnail size
2. **Age-appropriate** — natural for preschool characters
3. **Expressive** — shows character personality through body language
4. **Animatable** — natural transitions between poses

### Pose List

| # | Pose | Silhouette | Notes |
|---|------|------------|-------|
| 1 | Standing | Tall, arms at sides or slightly out | Default pose |
| 2 | Walking | One foot forward, arms swinging | Natural gait |
| 3 | Running | Arms back, one leg forward, leaning | Playful running |
| 4 | Jumping | Arms up, legs apart, airborne | Joyful jump |
| 5 | Skipping | One leg up, arms swinging | Rhythmic skip |
| 6 | Sitting | Legs together or crossed | Ground or chair |
| 7 | Kneeling | One or both knees on ground | Play/rest |
| 8 | Dancing | Asymmetric arms, one leg lifted | Grooving |
| 9 | Sleeping | Curled or lying flat, peaceful | Eyes closed |
| 10 | Reading | Sitting, holding book, looking down | Quiet activity |
| 11 | Writing | Sitting at desk, holding pencil | Fine motor |
| 12 | Pointing | Arm extended, finger pointing | Directing attention |
| 13 | Clapping | Hands together, excited stance | Celebration |
| 14 | Waving | One arm up, hand open | Greeting |
| 15 | Hugging | Arms wrapped around | Affection |
| 16 | Holding Hands | Arms extended to side, hands clasped | Walking together |
| 17 | Playing | Active pose, reaching or holding toy | Recreation |
| 18 | Swimming | Arms extended, kicking motion | Water play |
| 19 | Flying | Arms out like wings, leaning forward | Imaginative play |
| 20 | Sliding | Arms up, leaning back | Playground fun |

---

## Quality Checklist

Every character must pass the following review before being locked:

- [ ] Instantly recognizable
- [ ] Works in silhouette
- [ ] Memorable color palette
- [ ] Child-friendly
- [ ] Large expressive eyes
- [ ] Consistent proportions
- [ ] Distinct personality
- [ ] Reusable wardrobe
- [ ] Complete expression library (22 expressions)
- [ ] Complete pose library (20 poses)
- [ ] Complete turnaround sheet (6 angles)
- [ ] Prompt template finalized
- [ ] Negative prompt tested
- [ ] Reference sheet approved
- [ ] Ready for LoRA training (if used)

---

## Rotation / Turnaround Standards

Every character needs turnaround sheets from 6 angles:

| Angle | Purpose |
|-------|---------|
| Front | Main reference — character looking at camera |
| 3/4 | Most natural view — primary for scenes |
| Profile | Side view — for animation reference |
| Back | Back view — for full turnaround |
| Top | Top-down — for scene blocking |
| Bottom | Low angle — for dynamic shots |

---

## Version Control

All style guide documents are versioned. Major changes (proportion shifts, new rules) increment the major version. Minor clarifications and additions increment the minor version.

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-28 | Initial style guide — rules derived from PHASE1.md |

---

*Part of the AI Nursery Rhyme Studio — Universe Library*
*Version 1.0 — 2026-07-28*
