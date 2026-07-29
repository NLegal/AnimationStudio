# Idle Animation Standards

## AI Nursery Studio — Subtle Movement Reference v1.0

---

## Importance of Subtle Movement

Characters must **never** appear frozen. Even when standing still, a living character breathes, blinks, and shifts weight. The idle animation is the character's baseline personality. A well-crafted idle makes the character feel alive, present, and ready to act.

An idle that is too still reads as "paused" or "dead." An idle that is too busy distracts from the scene. The goal is perceptible-but-unobtrusive movement.

---

## Breathing

The most fundamental idle layer. All characters breathe at a gentle, relaxed rate.

| Parameter | Value |
|---|---|
| Rate | 12 cycles per minute (5 seconds per full breath) |
| Inhalation | 2 seconds (48 frames at 24 fps) |
| Exhalation | 3 seconds (72 frames at 24 fps) |
| Chest rise | 2–4% of torso height |
| Shoulder rise | 1–2% of shoulder height (secondary) |

The breathing wave should be a smooth sine curve. No sharp in/out transitions. Belly characters (pig, elephant) may show slight belly movement instead of (or in addition to) chest movement.

Breathing is the lowest priority — it can be overridden by any other action.

---

## Eye Blinking

Essential for keeping characters feeling alive. Standardize across all characters.

| Parameter | Value |
|---|---|
| Frequency | Every 4–6 seconds (slightly randomized, never robotic) |
| Closure duration | 100 ms (2.4 frames at 24 fps → 2 frames) |
| Open-to-close | 1 frame (ease-in) |
| Closed hold | 0 frames — immediate reopen (fast blink, child-friendly) |
| Close-to-open | 1 frame (ease-out) |
| Total blink | 3 frames (close 1, open 2) — "snap shut, ease open" |

When speaking, characters blink less frequently (every 6–8 seconds). At the end of a sentence or thought, a slow blink (5 frames total) signals conclusion.

Never leave eyes closed for more than 3 frames unless sleeping.

---

## Head Sway

A gentle, almost imperceptible head movement breaks the statue effect.

| Parameter | Value |
|---|---|
| Rotation | ±3 degrees on the Y-axis (gentle shake) |
| Cycle duration | 4 seconds (96 frames) |
| Waveform | Slow sine wave |
| Tilt overlay | ±1 degree on the Z-axis (micro-tilt, offset by 90°) |

The head sway should be so subtle that it is only noticed when comparing frame 1 to frame 48. It is the character "living" in their body, not actively looking around.

When the character is actively watching something, head sway stops and is replaced by directed gaze.

---

## Body Weight Shifts

Characters shift weight from one foot to the other, even at rest.

| Parameter | Value |
|---|---|
| Shift loop | 6 seconds (144 frames) |
| Weight distribution | 60/40 → 50/50 → 40/60 → 50/50 |
| Hip sway | ±2 degrees rotation on the X-axis |
| Spine counter-sway | Opposite direction to hips, half the amplitude |
| Foot pressure | Slight heel/toe rock (±1 degree ankle) |

The shift should feel like the character is comfortable but not locked in place. Never shift so much that the character looks like they need to use the bathroom.

Tired characters shift more frequently (every 4 seconds). Alert characters shift less (every 8 seconds).

---

## Accessory Movement

Secondary elements add life during idle.

### Ear Movement

| Character | Motion | Timing |
|---|---|---|
| Bunny (Lily) | One ear flicks/twitches | Every 3–4 seconds, 6-frame flick |
| Bunny (Lily) | Both ears bounce from breathing | Continuous, 2-frame delay behind head |
| Mouse | Small ear flick | Every 5 seconds, 4-frame flick |
| Elephant | Gentle ear flap | Every 8 seconds, 12-frame flap |
| Dog | Ear perk | When hearing something, 6-frame perk |

### Tail Movement

| Character | Motion | Timing |
|---|---|---|
| Bunny | Tiny tail wiggle | Every 5 seconds, 4-frame wiggle |
| Dog | Tail wag | Continuous or when happy, 8-frame loop |
| Mouse | Tail twitch | Every 4 seconds, 3-frame twitch |
| Pig | Curly tail jiggle | Every 6 seconds, 6-frame jiggle |

### Clothing / Accessories

| Item | Motion | Timing |
|---|---|---|
| Dress (Lily) | Gentle sway from breathing | Continuous, 3-frame delay |
| Bow (Lily) | Bounce from head movement | Continuous, 2-frame delay |
| Scarf | Gentle flutter | Light breeze, 16-frame oscillation |
| Ribbon | Settle and rest | 8-frame decay after any movement |

---

## Per-Character Idle Notes

### Lily Bunny
- Ear twitch: every 3 seconds, one ear rotates 15°, then returns
- Nose sniffle: subtle nose crinkle every 5 seconds
- Foot tap: occasional (every 10 seconds), one-foot toe tap, 4 frames
- Bow bounce: follows head sway with 2-frame delay

### Penelope Pig
- Nose wiggle: most distinctive idle — wiggles every 4 seconds, 8 frames
- Snout sniff: audible-sniff body motion every 6 seconds
- Ear flap: gentle ear flop every 7 seconds
- Tail curl jiggle: constant micro-motion

### Ollie Owl
- Head tilt: iconic — tilts head 20° every 5 seconds, holds 2 seconds, returns
- Slow blink: uses nictitating membrane, blink takes 6 frames (slower than others)
- Wing adjust: small wing shift every 8 seconds
- Perch shift: weight shift more pronounced (owl feet grip)

### Ellie Elephant
- Trunk curl: gentle curl and uncurl, 24-frame cycle
- Ear flap: slow flap every 8 seconds, 16 frames
- Heavy breath: occasional deep breath, 50% larger than normal chest rise
- Foot rock: very subtle weight shift on large feet

### Tippy Mouse
- Whisker twitch: constant micro-twitch, 2-frame loop
- Head dart: quick head turn (4 frames) every 6 seconds, looks around
- Nose twitch: every 3 seconds
- Tail flick: every 5 seconds, 4-frame flick

### Waddles Penguin
- Flipper adjust: small flipper lift every 6 seconds
- Beak nibble: gentle beak rub every 8 seconds
- Belly breath: visible belly expansion, breath cycle 6 seconds (slower)
- Weight rock: penguin-specific side-to-side rock, 8-second loop

---

## Idle Timing Chart

| Layer | Duration | Easing | Priority | Notes |
|---|---|---|---|---|
| Breathing | 120 frames (5s) | Sine in/out | Background | Constant, lowest layer |
| Eye blink | 3 frames (125ms) | Linear in, ease out | Foreground | Every 4–6s, randomized |
| Head sway | 96 frames (4s) | Sine in/out | Midground | ±3°, continuous |
| Weight shift | 144 frames (6s) | Smooth step | Midground | 60/40 rock |
| Ear twitch | 6 frames (250ms) | Ease out | Foreground | Bunny, every 3–4s |
| Nose wiggle | 8 frames (333ms) | Sine in/out | Foreground | Pig, every 4s |
| Head tilt | 48 frames (2s) | Ease in/out | Foreground | Owl, every 5s |
| Tail wag | 8 frames (333ms) | Sine in/out | Midground | Continuous or triggered |
| Accessory delay | 2–3 frames behind | Follow-through | Foreground | Ear, bow, dress, tail |

All idle layers should blend together so no single action stands out as mechanical. The character breathes and occasionally fidgets, but never looks like they are waiting for a loading screen.
