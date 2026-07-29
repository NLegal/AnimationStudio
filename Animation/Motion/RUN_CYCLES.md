# Run Cycle Standards

## AI Nursery Studio — Locomotion Reference v1.0

---

## General Run Principles

- Run cycles have an **airborne phase** — both feet leave the ground
- Forward lean differentiates run from walk
- Arms pump forward-backward (not side-to-side)
- Runs are **short duration** — a character should not run for more than 3 seconds continuously without a reason
- **No aggressive or frantic running** — all runs are child-friendly play
- All cycles loop seamlessly (frame 0 = frame N)

---

## Normal Run

Everyday running — playing in the park, chasing a ball.

| Parameter | Value |
|---|---|
| Frame count | 5 frames per stride (10 per full cycle) |
| Speed | 80% of maximum character speed |
| Airborne frames | 2 frames per stride |
| Description | Standard forward run, playful energy, neutral expression or slight smile |
| Posture | Forward lean ±12° |
| Arm position | Elbows bent 90°, arms pump forward-backward, arc ±40° |
| Leg position | Knee drive forward, foot extends behind on push-off, heel kick toward glutes |
| Arm/leg timing | Opposite arm/leg drive — right arm forward when left leg forward |
| Character height variation | ±8% per stride (bounce from push-off and landing) |
| Easing curve | Quick push-off ease-out, slight hang, landing ease-in |

---

## Excited Run

The character is thrilled — a birthday present, a friend arriving, a favorite song starting.

| Parameter | Value |
|---|---|
| Frame count | 4 frames per stride (8 per full cycle) |
| Speed | 90% of maximum character speed |
| Airborne frames | 3 frames per stride |
| Description | Fast, pumping, big smile, eyes wide, joyful expression |
| Posture | Forward lean ±15°, chest slightly puffed |
| Arm position | Elbows bent 90°, arms pump aggressively, arc ±50°, fists clenched |
| Leg position | High knee drive, heels kick toward glutes, longer stride |
| Arm/leg timing | Opposite arm/leg drive, more pronounced than normal run |
| Character height variation | ±12% per stride — high bounce, extended airborne |
| Easing curve | Explosive push-off ease-out, extended hang, soft landing |

The excited run sacrifices some control for enthusiasm. The character may throw their head back slightly on the airborne frames (a joyful "wheee!" moment).

---

## Play Chase

Running while looking back at a friend — tag, hide-and-seek, follow-the-leader.

| Parameter | Value |
|---|---|
| Frame count | 5 frames per stride (10 per full cycle) |
| Speed | 85% of maximum character speed |
| Airborne frames | 2 frames per stride |
| Description | Playful, looking over shoulder, smirk or laugh, one hand may reach back |
| Posture | Forward lean ±10°, upper body rotated ±20° toward the camera or target |
| Arm position | One arm pumps forward (lead arm), other reaches back playfully or waves |
| Leg position | Standard running stride, slightly wider stance for balance |
| Arm/leg timing | Asymmetric due to upper body rotation — arm pump is offset |
| Character height variation | ±6% per stride (slightly less bounce due to torso rotation) |
| Easing curve | Normal run ease, with torso rotation on a gradual sine wave |

The challenge of Play Chase is the upper body rotation — the character runs forward but twists to look back, making the silhouette slightly off-balance but intentionally playful.

**Safety note:** The character must never look scared or panicked. This is fun chase, not a scary chase. Smile or laugh must be visible.

---

## Small Sprint

Maximum speed — short bursts only. The character is racing to the playground.

| Parameter | Value |
|---|---|
| Frame count | 3 frames per stride (6 per full cycle) |
| Speed | 95% of maximum character speed |
| Airborne frames | 3 frames per stride (almost entirely airborne) |
| Description | Fastest gait, extreme forward lean, intense (but happy) focus |
| Posture | Forward lean ±20°, head down slightly, arms drive hard |
| Arm position | Elbows bent 90°, arms pump maximum arc ±55°, fists tight |
| Leg position | Maximum knee drive, feet barely touch the ground, extreme heel kick |
| Arm/leg timing | Opposite arm/leg, synchronized at maximum speed |
| Character height variation | ±10% per stride |
| Easing curve | Near-linear with very short ground-contact ease |

**Warning:** The sprint is the fastest motion in the studio's vocabulary. It must be used sparingly (maximum 2 seconds of continuous sprint). After a sprint, the character must slow down visibly — never cut from full sprint to idle. Use a 4-frame deceleration to fast walk, then slow to idle.

---

## Summary Table

| Cycle | Frames/stride | Speed | Airborne | Forward lean | Height var | Best for |
|---|---|---|---|---|---|---|
| Normal run | 10 | 80% | 2 frames | 12° | ±8% | Everyday running |
| Excited run | 8 | 90% | 3 frames | 15° | ±12% | Joyful sprints |
| Play chase | 10 | 85% | 2 frames | 10° + 20° twist | ±6% | Tag / hide-and-seek |
| Small sprint | 6 | 95% | 3 frames | 20° | ±10% | Short bursts only |

---

## Safety Guidelines

- **No aggressive running** — no furious expressions, no angry chasing
- **No frantic arm flailing** — arms should pump, not windmill
- **No violent collisions** — if two characters run toward each other, they slow down before contact
- **Sprint limit** — 2 seconds maximum at 95% speed; deceleration required
- **Expression check** — all running characters must have a neutral-to-happy expression
- **No running toward danger** — characters only run toward positive things

---

## Per-Character Run Modifications

### Lily Bunny
- Normal/excited: ears stream backward, dress billows, ±5% extra height bounce
- Play chase: ears rotate with head turn, one ear may flop over an eye
- Sprint: ears fully horizontal, dress lifted

### Penelope Pig
- Normal: snout leads, ears flap back, ±2% less bounce (heavier)
- Excited: snort sound implied, curly tail bounces
- Play chase: snout rotated with body, nose wiggling
- Sprint: ground feel of weight — avoid making her look too light

### Ollie Owl
- Run uses half-flown hops — wings half-extended, bounding gait
- Normal: 3 ground contacts + 2 wing-assisted glides per cycle
- Excited: more glide (4 frames), less ground contact
- Play chase: head fully rotated backward while body runs forward — owl specialty
- Sprint: not in character — use excited bound-glide instead

### Ellie Elephant
- No sprint — use excited fast walk (run is out of character for elephant)
- Normal run: 8 frames per stride, heavier feel, trunk curls up
- Play chase: trunk extended forward, ears out, playful trumpet
- Maximum speed: excited run at 70% — elephant never hits 90%+

### Tippy Mouse
- All runs are proportionally faster — multiply speed by 1.3×
- Sprint: 3 frames per stride, looks like a blur of motion
- Play chase: tail straight back, whiskers forward
- Excited: tiny squeak implied, bounding leaps

### Waddles Penguin
- Run is a "fast waddle" — wings out, side-to-side exaggerated
- Normal run: 6 frames per stride, ±12% lateral sway, 8° forward lean
- No sprint — maximum is excited run at 80%
