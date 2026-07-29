# Walk Cycle Standards

## AI Nursery Studio — Locomotion Reference v1.0

---

## General Walk Principles

- All walk cycles loop seamlessly (frame 0 = frame N)
- Arms swing opposite to legs (natural humanoid gait)
- Characters with tails/sway accessories delay those by 2–3 frames behind the body
- Vertical bobbing varies by character weight class
- Eye gaze remains forward unless specified

---

## Slow Walk

A relaxed, meandering pace — exploring, not rushing.

| Parameter | Value |
|---|---|
| Frame count | 12 frames per step (24 per full stride) |
| Speed | 30% of maximum character speed |
| Description | Gentle, small steps, low energy. Used when exploring or tired. |
| Body position | Upright, slight lean forward (±2°) |
| Arm position | Soft elbows, gentle swing — arc of ±15° from rest |
| Leg position | Short stride — feet lift max 3% of character height |
| Character height variation | ±3% per step (very low bounce) |
| Easing curve | Smooth step — no sharp transitions |

---

## Normal Walk

The default gait for everyday movement.

| Parameter | Value |
|---|---|
| Frame count | 8 frames per step (16 per full stride) |
| Speed | 50% of maximum character speed |
| Description | Natural, confident, neutral. Default movement mode. |
| Body position | Upright, natural posture, slight forward lean (±4°) |
| Arm position | Natural swing — arc of ±25° from rest |
| Leg position | Medium stride — feet lift max 6% of character height |
| Character height variation | ±5% per step (moderate bounce) |
| Easing curve | Smooth step with slight ease at toe-off |

Heel contacts first, weight rolls to toe, push-off provides forward momentum.

---

## Happy Skip

A joyful, bouncy gait — the character is having a good time.

| Parameter | Value |
|---|---|
| Frame count | 6 frames per step (12 per full stride) |
| Speed | 70% of maximum character speed |
| Description | Hopping step pattern, arms up or pumping, big smile. Used for good news. |
| Body position | Leaning back slightly (±3°) to counterbalance the bounce |
| Arm position | Arms up (elbows bent 90°), pumping up-and-down, arc ±35° |
| Leg position | One leg extends forward, other tucks under, airborne moment |
| Character height variation | ±12% — significant bounce with an airborne hang-time of 2 frames |
| Easing curve | Bounce ease — fast up, slow down, hang at apex |

The skip has a distinct "hop" at the transition — one foot lands while the other lifts into the next skip. This is the bounciest standard walk cycle.

---

## Fast Walk

Purposeful, energized walking — late for something, or very excited to arrive.

| Parameter | Value |
|---|---|
| Frame count | 6 frames per step (12 per full stride) |
| Speed | 75% of maximum character speed |
| Description | Bigger strides, more arm swing, determined expression. |
| Body position | Forward lean (±8°) — body is "chasing" the feet |
| Arm position | Extended swing — arc of ±35° from rest, elbows straighter |
| Leg position | Long stride — feet lift max 8% of character height |
| Character height variation | ±6% per step |
| Easing curve | Ease in/out with linear mid-section |

Although fast, this is still walking — one foot stays on the ground at all times. If both feet leave the ground, it becomes a run.

---

## Careful Walk

Tiptoeing around something delicate — or trying not to wake someone.

| Parameter | Value |
|---|---|
| Frame count | 16 frames per step (32 per full stride) |
| Speed | 20% of maximum character speed |
| Description | Tiny steps, arms slightly out for balance, cautious expression. |
| Body position | Upright, tense — leaning back slightly (±2°) |
| Arm position | Arms held out to sides (±20° from rest) — balance position |
| Leg position | Very short stride — feet lift max 2% of character height, toe points down |
| Character height variation | ±2% per step (nearly flat) |
| Easing curve | Smooth step — slow, deliberate, no bounce |

The character is in "stealth mode." Knees bend more than usual. The foot placement is deliberate — toe touches first, then heel lowers slowly.

---

## Tiptoe

Reaching for something high, or trying to be quiet.

| Parameter | Value |
|---|---|
| Frame count | 14 frames per step (28 per full stride) |
| Speed | 25% of maximum character speed |
| Description | Heels off ground, arms up or reaching up, leaning forward |
| Body position | Forward lean (±10°), torso extended upward |
| Arm position | Arms raised above shoulders (±45°) — reaching or balancing |
| Leg position | Knees bent, weight on balls of feet, heels up 5% of character height |
| Character height variation | ±4% per step |
| Easing curve | Smooth step with gentle rise and fall |

The tiptoe gait is distinct from the careful walk — the character is literally on their toes, reaching upward. The body stretches tall, making the character appear 5–8% taller than normal.

---

## Per-Character Walk Style Notes

### Lily Bunny (Bouncy)

| Gait | Modifications |
|---|---|
| Slow walk | Ears bounce with 3-frame delay; tail wiggles; every 4th step has a micro-hop |
| Normal walk | ±8% vertical bounce (above standard); arms swing wider; ears trail behind |
| Happy skip | ±15% bounce (above standard); ears flop up and down; bow bounces |
| Fast walk | Ears stream backward; dress hem bounces; tail bobbles |
| Careful walk | Ears perk up (alert); nose twitches at each step |
| Tiptoe | Ears point up and forward; arms extended; nose twitching |

### Penelope Pig (Gentle)

| Gait | Modifications |
|---|---|
| Slow walk | ±2% bounce; snout leads; tail jiggles |
| Normal walk | ±4% bounce; ears flap gently; belly jiggles |
| Happy skip | ±8% bounce; snout up; curly tail bounces |
| Fast walk | ±5% bounce; ears back; trotting motion |
| Careful walk | ±1% bounce; nose wiggling; very deliberate |
| Tiptoe | ±3% bounce; snout lifted; ears perked |

### Ollie Owl (Stately)

| Gait | Modifications |
|---|---|
| Slow walk | ±1% bounce; head rotates independently scanning; wings slightly out |
| Normal walk | ±3% bounce; head tracks forward; wings at sides |
| Happy skip | Not in character — use excited fast walk instead (±4% bounce) |
| Fast walk | ±4% bounce; head stays steady (compensated); wings half-extended |
| Careful walk | ±1% bounce; head rotates 180° scanning; minimal movement |
| Tiptoe | ±2% bounce; wings half-open for balance; head tilted |

### Ellie Elephant (Heavy)

| Gait | Modifications |
|---|---|
| Slow walk | ±1% bounce; trunk sways 4-frame delay; heavy footfall |
| Normal walk | ±2% bounce; trunk swings opposite to legs; ear flaps |
| Happy skip | Use excited fast walk — skip is out of character (±3% bounce, trunk curls up) |
| Fast walk | ±3% bounce; earth-shaking presence; trunk bounces |
| Careful walk | ±1% bounce; trunk curls in; ears alert; very slow foot placement |
| Tiptoe | Not in character (anatomically implausible) — use careful walk |

### Tippy Mouse (Quick)

| Gait | Modifications |
|---|---|
| Slow walk | ±5% bounce; whiskers constant twitch; tail high |
| Normal walk | ±8% bounce; quick steps; tail streams behind |
| Happy skip | ±14% bounce; tiny hops; arms pumping; tail bounces |
| Fast walk | ±10% bounce; very quick; looks like scampering |
| Careful walk | ±3% bounce; whiskers forward; tail low; nose twitching |
| Tiptoe | ±6% bounce; tail up; whiskers extended; leaning far forward |

### Waddles Penguin (Side-to-Side)

| Gait | Modifications |
|---|---|
| Slow walk | ±6% lateral sway; flippers out 30°; beak slightly open |
| Normal walk | ±10% lateral sway; flippers rise on opposite step; beak forward |
| Happy skip | ±14% lateral sway; flippers flap; body wiggles |
| Fast walk | ±8% lateral sway; rapid waddle; flippers pumping |
| Careful walk | ±4% lateral sway; flippers out for balance; neck extended |
| Tiptoe | ±5% lateral sway; flippers up; neck stretched tall |
