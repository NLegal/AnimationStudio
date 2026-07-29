# Jump Library

## AI Nursery Studio — Vertical Motion Reference v1.0

---

## General Jump Principles

- Every jump has four phases: **Anticipation → Launch → Apex → Landing**
- Anticipation is mandatory — a character never leaves the ground without coiling first
- Landings are soft — knees and hips absorb impact, squash at the bottom
- Arms aid momentum: swing back during anticipation, up during launch, out at apex, forward for balance on landing
- Characters should never appear to float (unless magical) — gravity is gentle but present
- All cycles loop to and from a standing idle pose

---

## Standing Jump

The basic vertical jump — from standing to standing.

| Phase | Frames | Duration | Body Position | Arm Position | Leg Position |
|---|---|---|---|---|---|
| Anticipation | 1–3 | 3 frames (125ms) | Crouch — torso lowers ±15%, spine compresses | Arms swing back behind body, elbows bent | Knees bend to 60°, heels on ground |
| Launch | 4–6 | 3 frames (125ms) | Body extends rapidly, reaching up | Arms swing up overhead, fully extended | Legs straighten, feet push off, toes point down |
| Apex | 7–9 | 3 frames (125ms) | Full extension, slight hang-time | Arms at highest point, slightly out | Legs tucked or straight — character preference |
| Landing | 10–12 | 3 frames (125ms) | Crouch to absorb — torso lowers ±10% | Arms come forward for balance | Knees bend to 45°, feet contact toe-to-heel |

**Total: 12 frames (500ms at 24 fps)**

Height reached: 30% of character height (from ground to feet at apex)

Squash at landing: 80% height, 120% width — recover to neutral by frame 14

---

## Hop

A single-foot hop — shifting position or bouncing in place.

| Phase | Frames | Duration | Body Position | Arm Position | Leg Position |
|---|---|---|---|---|---|
| Anticipation | 1–2 | 2 frames (83ms) | Slight crouch on one foot | Arms rise slightly | One foot lifts, weight on standing leg |
| Launch | 3–5 | 3 frames (125ms) | Upward push from one foot | Arms help lift (small pump) | Standing foot pushes off, both feet off ground |
| Apex | 6 | 1 frame (42ms) | Brief hang-time | Arms at shoulder height | Feet together or hopping foot slightly tucked |
| Landing | 7–8 | 2 frames (83ms) | Soft landing on same foot | Arms lower for balance | Landing foot absorbs weight, other foot hovers |

**Total: 8 frames (333ms at 24 fps)**

Height reached: 15% of character height (shorter than jump)

The hop is lighter and quicker than a full jump. Used for shifting position, dancing, or expressing mild excitement.

---

## Skip

A hop combined with a step — forward locomotion with bounce.

Skip is not a pure vertical jump but a **hop-step** pattern. Each skip cycle covers one "hop" phase of the full skip gait.

| Phase | Frames | Duration | Body Position | Arm Position | Leg Position |
|---|---|---|---|---|---|
| Hop lift | 1–2 | 2 frames (83ms) | Body lifts on standing leg | Arms pump up | Standing leg pushes off, other leg extends forward |
| Airborne | 3–4 | 2 frames (83ms) | Suspended — weight transfers | Arms at chest height | Front leg extends, back leg tucks |
| Step landing | 5–6 | 2 frames (83ms) | Land on opposite foot | Arms lower slightly | Front foot lands, weight shifts |
| Transfer | 7–8 | 2 frames (83ms) | Repeat on other side | Arms cycle | Opposite leg prepares to hop |

**Total: 8 frames per skip-step (333ms)**

The skip alternates feet. A full skip in place (no forward movement) uses the same timing. Forward velocity adds 6–8% of character height per step.

---

## Jump for Joy

Exaggerated vertical jump expressing pure happiness.

| Phase | Frames | Duration | Body Position | Arm Position | Leg Position |
|---|---|---|---|---|---|
| Anticipation | 1–3 | 3 frames (125ms) | Deep crouch, ±20% compression | Arms swing far back | Knees deep (45°), chest down |
| Launch | 4–6 | 3 frames (125ms) | Explosive upward, ±15% stretch | Arms throw up and out (V-shape) | Legs straight, feet push off hard |
| Apex | 7–8 | 2 frames (83ms) | Full stretch, legs apart in air | Arms wide, hands open (jazz hands optional) | Legs spread (V-shape in air), feet pointed |
| Landing | 9–10 | 2 frames (83ms) | Soft landing, slight crouch | Arms come down, open | Feet land shoulder-width apart, knees bent |

**Total: 10 frames (417ms at 24 fps)**

Height reached: 45% of character height — the highest jump in standard vocabulary

Facial expression: maximum smile, eyes closed or wide with joy. Optional "cheer" sound at apex.

---

## Puddle Jump

Jumping over a puddle or small obstacle — curled legs avoid the splash.

| Phase | Frames | Duration | Body Position | Arm Position | Leg Position |
|---|---|---|---|---|---|
| Anticipation | 1–3 | 3 frames (125ms) | Crouch, looking down at puddle | Arms back, one hand may point at puddle | Knees bent, one foot slightly forward |
| Launch | 4–5 | 2 frames (83ms) | Forward + upward trajectory | Arms swing forward-up | Push off both feet |
| Apex / Curl | 6–7 | 2 frames (83ms) | Forward lean, legs tuck up high | Arms out for balance | Knees pulled up to chest (avoid splash) |
| Extend | 8 | 1 frame (42ms) | Legs extend forward for landing | Arms forward | Legs straighten to reach ground |
| Landing | 9–10 | 2 frames (83ms) | Soft land, slight crouch | Arms out for balance | Feet land, knees absorb |

**Total: 10 frames (417ms at 24 fps)**

Height reached: 25% of character height
Forward distance: 40% of character height

The key distinguishing feature of the puddle jump is the **leg curl** at apex — knees pulled up tightly, feet together, as if avoiding water.

---

## Dance Jump

A jump with a turn or clap — used in dance sequences.

### Variant A: Jump + Turn (90°)

| Phase | Frames | Duration | Body Position | Arm Position | Leg Position |
|---|---|---|---|---|---|
| Anticipation | 1–2 | 2 frames (83ms) | Slight crouch, coil for rotation | Arms to one side (wind-up) | Feet together, knees bent |
| Jump + turn | 3–5 | 3 frames (125ms) | Body rotates 90° in air | Arms swing to help rotation | Legs together, toes pointed |
| Landing | 6–8 | 3 frames (125ms) | Land facing new direction | Arms lower for balance | Feet land together, slight knee bend |

**Total: 8 frames (333ms at 24 fps)**

### Variant B: Jump + Clap

| Phase | Frames | Duration | Body Position | Arm Position | Leg Position |
|---|---|---|---|---|---|
| Anticipation | 1–2 | 2 frames (83ms) | Crouch | Arms down, ready | Feet together |
| Launch + clap | 3–5 | 3 frames (125ms) | Upward, bounce | Arms clap together overhead at apex | Legs straight, feet pointed |
| Landing | 6–8 | 3 frames (125ms) | Soft land | Arms come down, open | Feet land, knees bend |

**Total: 8 frames (333ms at 24 fps)**

---

## Jump Comparison Table

| Jump type | Total frames | Duration | Height | Anticipation | Launch | Apex | Landing | Difficulty |
|---|---|---|---|---|---|---|---|---|
| Standing jump | 12 | 500ms | 30% | 3 frames | 3 frames | 3 frames | 3 frames | Standard |
| Hop | 8 | 333ms | 15% | 2 frames | 3 frames | 1 frame | 2 frames | Easy |
| Skip (per step) | 8 | 333ms | 12% | — | — | — | — | Easy |
| Jump for joy | 10 | 417ms | 45% | 3 frames | 3 frames | 2 frames | 2 frames | Moderate |
| Puddle jump | 10 | 417ms | 25% | 3 frames | 2 frames | 3 frames | 2 frames | Moderate |
| Dance jump | 8 | 333ms | 20% | 2 frames | 3 frames | — | 3 frames | Easy |

---

## Landing Requirements

- **Soft landing is mandatory** — no stiff-legged landings ever
- Knee bend on landing: minimum 30° (hop), maximum 60° (jump for joy)
- Squash frame at lowest point of landing: 80% height, 120% width
- Recovery to neutral: 2–3 frames after landing contact
- Arms should be forward or out during landing — never behind the body
- Impact effects (optional): small dust puff, gentle ground ring, flower wobble

---

## Per-Character Jump Notes

| Character | Best jump | Modification |
|---|---|---|
| Lily Bunny | Jump for joy | Ears trail upward on launch, flop down on landing. Bow bounces 3-frame delay. |
| Penelope Pig | Standing jump | Heavier landing — squash to 75% height. Belly jiggles on impact. |
| Ollie Owl | Puddle jump | Wings half-extend during apex. Head stays level (owl compensates). |
| Ellie Elephant | Standing jump | Do not use Jump for Joy (out of character). Trunk curls up during airborne. |
| Tippy Mouse | Hop | All jumps are proportionally 1.5× higher relative to body. Tail bounces high. |
| Waddles Penguin | Dance jump | Flippers out. Lateral wobble on landing. Best at jump + turn. |
