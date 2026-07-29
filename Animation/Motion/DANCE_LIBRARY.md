# Dance Library

## AI Nursery Studio — Choreographed Motion Reference v1.0

---

## General Dance Principles

- All dance loops are **seamlessly loopable** — frame 0 equals frame N
- Dance is always **voluntary** — characters dance because they are happy
- Facial expressions during dance: smile (minimum), laugh/big smile (preferred)
- Dances can be performed solo or in a group
- Group dances require **beat sync** — all characters hit the same keyframes
- Character spacing during group dance: minimum 50% of character width
- Easing: bouncy ease (fast in, slow out with overshoot) for most dance moves
- All dance speeds assume 120 BPM (beats per minute) — 24 frames per beat at 24 fps

---

## Side-to-Side

The simplest dance — weight shifts side to side with a head bob.

| Parameter | Value |
|---|---|
| Frame count | 8 frames per full loop (4 frames per side) |
| Description | Gentle sway, minimal effort, head bobbing to the beat |
| Footwork | Weight shifts from left foot to right foot. Feet stay planted, heels may lift. |
| Body position | Upper body sways opposite to hips (counter-balance) |
| Arm position | Arms relaxed at sides, swing gently with the sway, ±15° |
| Head position | Bobs on beat — slight down-nod on each weight shift, 2-frame cycle |
| Easing | Smooth step — gentle, not sharp |

**8-frame loop (333ms):**
- Frames 1–2: Shift weight to right, hips right, head nods
- Frames 3–4: Hold right, slight rise
- Frames 5–6: Shift weight to left, hips left, head nods
- Frames 7–8: Hold left, slight rise

Character spacing: 100% of character width (close, casual)

---

## Circle Dance

A group dance — characters hold hands and rotate in a circle.

| Parameter | Value |
|---|---|
| Frame count | 12 frames per quarter rotation (48 frames per full circle) |
| Description | Group circle, hands joined, stepping in unison |
| Footwork | Step-together pattern: step forward (outside foot), together (inside foot) |
| Body position | Upright, facing center or slightly rotated in the direction of travel |
| Arm position | Arms extended to sides, hands joined with neighbors, natural swing |
| Head position | Facing center, slight head bob on each step |
| Easing | Smooth step with slight hop at the step |

**12 frames per quarter (500ms):**
- Frames 1–4: Step forward with outside foot (2 frames), bring inside foot together (2 frames)
- Frames 5–8: Step forward with outside foot (2 frames), bring inside foot together (2 frames)
- Frames 9–12: Small hop at transition, prepare for next quarter

Character spacing: Arms-length apart (hand-join distance). Minimum 120% of character width between centers.

Each quarter rotation is 90°. A full circle takes 48 frames (2 seconds).

---

## Clap Dance

Clapping on the beat with body movement.

| Parameter | Value |
|---|---|
| Frame count | 8 frames per full loop |
| Clap timing | Clap on frame 2 (beat 2) and frame 6 (beat 4) |
| Description | Stepping side-to-side, clapping on the off-beats |
| Footwork | Step right (frames 1–2), step left (frames 3–4), step right (frames 5–6), step left (frames 7–8) |
| Body position | Upright, slight bounce on each step |
| Arm position | Arms open on beats 1 and 3 (frames 1, 5), clap on beats 2 and 4 (frames 2–3, 6–7) |
| Head position | Bobs on step, looks at hands during clap |

**8-frame loop (333ms):**
- Frame 1: Step right, arms open to sides
- Frame 2: Weight on right, clap at chest height
- Frame 3: Hold clap, begin shifting weight left
- Frame 4: Step left, arms open
- Frame 5: Weight on left, arms open
- Frame 6: Clap at chest height
- Frame 7: Hold clap, begin shifting right
- Frame 8: Prepare for step right (loop)

Character spacing: 80% of character width (close enough to see each other's claps)

---

## Spin

A solo rotation — twirling in place.

| Parameter | Value |
|---|---|
| Frame count | 8 frames per full rotation |
| Description | 360° turn in place, arms out for balance, ends facing forward |
| Footwork | Step-step-turn pattern. Pivot on one foot, step around with the other. |
| Body position | Upright, slight lean in the direction of the turn |
| Arm position | Arms extended to sides (±45°) for balance and flair |
| Head position | Head leads the turn — looks at the direction of travel, then snaps forward at the end |

**8-frame rotation (333ms):**
- Frame 1: Start turn — right foot crosses in front, arms out
- Frame 2: Pivot on left foot, 90° turned
- Frame 3: Step around with right foot, 180°
- Frame 4: Pivot on left foot, 270°
- Frame 5: Right foot lands facing forward, head snaps to camera
- Frames 6–8: Settle — arms lower, slight knee bend, recover to neutral

For younger or less stable characters, use 12 frames per rotation (slower, more controlled).

The **head snap** on frame 5 is the signature moment — the character completes the spin and locks eyes with the audience.

---

## March

High-energy, rhythmic marching in place or forward.

| Parameter | Value |
|---|---|
| Frame count | 6 frames per step (12 per full stride) |
| Description | High knees, arms pumping, military-style but playful |
| Footwork | Knee lifts to 90° on each step, feet flexed, stamp on each landing |
| Body position | Upright, chest slightly puffed, chin up |
| Arm position | Arms pump opposite to legs, elbows bent 90°, hands in fists |
| Head position | Steady, slight bob, looking forward |

**12-frame stride (500ms):**
- Frame 1: Left knee up (90°), right arm forward, left arm back
- Frame 2: Left knee at peak, arms at extremes
- Frame 3: Left foot stamps down, arms begin transition
- Frame 4: Right knee up (90°), left arm forward, right arm back
- Frame 5: Right knee at peak, arms at extremes
- Frame 6: Right foot stamps down, arms transition

Character spacing (group march): 150% of character width (needs room for knee lift)

March can be performed in place (no forward movement) or as a traveling march (6% of character height per step forward).

---

## Freeze Dance

Dance movement interrupted by brief freeze poses.

| Parameter | Value |
|---|---|
| Frame count | 12 frames per loop (8 frames move, 4 frames freeze) |
| Description | Any dance move for 8 frames, then stop abruptly for 4 frames |
| Move phase | 8 frames (333ms) — use Side-to-Side or Clap Dance footwork |
| Freeze phase | 4 frames (167ms) — complete stop, character holds the pose |
| Body position during freeze | Whatever position the character was in when the music "stopped" |
| Expression during freeze | Surprised look — eyes wide, mouth in small "o", caught off-guard |
| Resume | Frame 1 of next loop resumes the dance as if nothing happened |

**12-frame loop (500ms):**
- Frames 1–8: Dance (any sequence, typically Side-to-Side)
- Frames 9–12: Freeze! Hold pose with surprised expression

The freeze should look like the music literally stopped mid-beat. Characters should freeze in slightly awkward poses for comedic effect.

Character spacing: 100% of character width (enough room to not collide during freeze)

---

## Ribbon Dance

A flowing, graceful dance with a ribbon or streamer.

| Parameter | Value |
|---|---|
| Frame count | 16 frames per full loop |
| Description | Arm circles with ribbon, gentle full-body movement |
| Footwork | Gentle step-touch pattern — step right (4 frames), touch left (4 frames), step left (4 frames), touch right (4 frames) |
| Body position | Upright, torso follows the arm circle with a gentle twist |
| Arm position | Dominant arm makes large circles (overhead, around, figure-8s). Non-dominant arm is out for balance. |
| Ribbon path | Continuous spiral or figure-8 pattern. Ribbon trails the hand with 3-frame delay. |
| Head position | Follows the ribbon with the eyes — head tilts up when ribbon goes overhead |

**16-frame loop (667ms):**
- Frames 1–4: Step right, right arm circles up and over (12 o'clock → 3 o'clock)
- Frames 5–8: Touch left foot, arm continues circle (3 o'clock → 6 o'clock → 9 o'clock)
- Frames 9–12: Step left, arm completes circle and begins figure-8 cross (9 o'clock → 12 o'clock → diagonal down)
- Frames 13–16: Touch right foot, arm finishes figure-8, returns to start

The ribbon itself follows the hand path with a 3-frame wave delay. Ribbon length should be 150–200% of character height.

Character spacing: 200% of character width (ribbon needs clearance)

---

## Dance Library Summary

| Dance | Frames | Duration (24fps) | Difficulty | Group? | Spacing | Best mood |
|---|---|---|---|---|---|---|
| Side-to-side | 8 | 333ms | Easy | Yes | 100% | Casual happy |
| Circle dance | 48 (full circle) | 2000ms | Moderate | Required | 120% | Playful group |
| Clap dance | 8 | 333ms | Easy | Yes | 80% | Energetic |
| Spin | 8 | 333ms | Moderate | Solo | 150% | Show-off |
| March | 12 | 500ms | Easy | Yes | 150% | Silly / proud |
| Freeze dance | 12 | 500ms | Easy | Yes | 100% | Goofy |
| Ribbon dance | 16 | 667ms | Moderate | Solo | 200% | Graceful |

---

## Per-Character Dance Preferences

| Character | Best dance | Notes |
|---|---|---|
| Lily Bunny | Jump for joy + Spin | Combines two moves. Ears and bow add beautiful secondary motion during spin. |
| Penelope Pig | Clap dance | Snout wiggles on claps. Belly jiggles on steps. Natural entertainer. |
| Ollie Owl | Ribbon dance | Wings make ribbon manipulation natural. Head tracks the ribbon path perfectly. |
| Ellie Elephant | March | Heavy stomps feel powerful and fun. Trunk curls rhythmically. |
| Tippy Mouse | Freeze dance | Surprised freeze is the funniest with mouse proportions. Tiny statue pose. |
| Waddles Penguin | Side-to-side | Natural waddle translates directly into dance. Minimal effort, maximum charm. |
