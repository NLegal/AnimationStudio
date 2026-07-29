# Animation Style Guide

## AI Nursery Studio — Master Animation Standard v1.0

---

## Animation Philosophy

Movement in every AI Nursery Studio production must feel:

| Quality | Meaning |
|---|---|
| **Playful** | Bouncy, light, joyful energy in every motion |
| **Soft** | Gentle curves, no sharp or mechanical movement |
| **Rounded** | Arcs and circles dominate; no straight-line linear motion |
| **Energetic** | Alive and responsive, never sluggish or flat |
| **Safe** | Nothing violent, aggressive, or frightening |
| **Readable** | Clear poses; a 3-year-old can understand what is happening |
| **Slightly exaggerated** | Cartoon stretch on impact, anticipation before action |
| **Preschool-friendly** | Slow enough to follow, bright enough to engage |

---

## Frame Rate Standard

| Setting | Value | Notes |
|---|---|---|
| **Master framerate** | 24 fps | Cinematic standard; all cycles authored at 24 fps |
| **Export option** | 30 fps | For platforms requiring 30 fps (TV, YouTube) |
| **Conversion** | Frame-blend on export; do not re-time the animation |
| **Consistency** | Every cycle must loop seamlessly at both 24 fps and 30 fps |

---

## Motion Principles

### Anticipation

Every action is preceded by a wind-up. A jump begins with a crouch. A point begins with a pull-back. Anticipation frames inform the audience what is coming.

- Minimum anticipation: 2 frames
- Standard anticipation: 3–4 frames
- Exaggerated (comedy): 6–8 frames

### Follow-Through

Body parts continue moving after the main action stops. A bunny's ears keep bouncing after she lands. A dress settles after a spin.

- Follow-through decay: 3–5 frames after the primary pose
- Never cut motion abruptly — ease out to zero

### Squash-and-Stretch

Volume is preserved; shape deforms to communicate weight and impact.

- Squash on landing: 80% height, 120% width
- Stretch on reaching: 110% height, 90% width
- Return to rest within 4 frames

### Secondary Motion

Smaller elements respond to the primary action.

- Hair, ears, tails, bows, ribbons, dress hems
- Delay onset by 1–3 frames behind the main body
- Settle with a fade oscillation (damping ratio ~0.7)

---

## Character Motion Principles

Every character requires the following reusable cycles:

| # | Cycle | Purpose |
|---|---|---|
| 1 | **Idle** | Breathing, blinking, weight shifts — character is never frozen |
| 2 | **Walk** | Slow, normal, happy skip, fast, careful, tiptoe |
| 3 | **Run** | Normal, excited, play chase, small sprint |
| 4 | **Jump** | Standing, hop, skip, joy, puddle, dance |
| 5 | **Sit** | From standing to seated, seated idle, stand back up |
| 6 | **Stand** | From seated to standing, standing pose |
| 7 | **Dance** | Side-to-side, circle, clap, spin, march, freeze, ribbon |
| 8 | **Wave** | Arm raised, palm open, gentle side-to-side |
| 9 | **Clap** | Hands meet at chest height, 8-frame loop |
| 10 | **Hug** | Arms open → wrap → squeeze → release (24 frames) |
| 11 | **Point** | Arm extends, finger directs, 12 frames |
| 12 | **Reading** | Hold book, turn pages, head tracking, 48-frame loop |
| 13 | **Sleeping** | Slow breathing, closed eyes, body relaxed, 60-frame loop |
| 14 | **Singing** | Mouth shapes, gentle head sway, chest rise, 24-frame loop |

---

## Quality Standards

Every animation pass must satisfy:

- [ ] Smooth motion — no pops, hits, or linear stutters
- [ ] Consistent character proportions — no limb stretching beyond tolerance
- [ ] Correct facial expressions — emotion matches the scene
- [ ] Natural blinking — every 4–6 seconds, 100 ms closure
- [ ] Soft body movement — arcs, not straight lines
- [ ] Child-friendly pacing — holds are 1.5× longer than adult animation
- [ ] Stable camera — no handheld shake, no rapid zooms
- [ ] Proper interaction with objects — hands align to contact points
- [ ] Secondary motion present — ears, tails, clothing follow
- [ ] Matches studio style — playful, soft, rounded, energetic, safe, readable

---

## Movement Vocabulary

### Body Language

| Expression | Pose |
|---|---|
| Happy | Shoulders back, chin up, arms slightly out |
| Sad | Shoulders slumped, head down, arms limp |
| Curious | Head tilted, leaning forward, one foot forward |
| Scared | Hands near face, stepping back, wide eyes |
| Proud | Chest out, hands on hips, chin up |
| Tired | Heavy eyelids, slow movement, head drooping |
| Excited | Bouncing, arms up, weight on toes |
| Thinking | Hand on chin, looking up, slow pace |

### Locomotion

| Move | Description |
|---|---|
| Walk | Heel-toe contact, arm swing opposite to legs |
| Run | Forward lean, airborne moment, arms pump |
| Tiptoe | Heels up, arms out for balance, lean forward |
| Skip | Hop-step pattern, arms up, bouncy |
| March | High knees, arms pump, rhythmic |
| Slide | Feet never cross, sideways motion, slow |
| Crawl | Hands and knees, slow, exploratory |

### Gesture

| Gesture | Timing |
|---|---|
| Wave | 8 frames per arc, 3 arcs minimum |
| Point | 6 frames extend, 4 frames hold, 6 frames retract |
| Thumbs up | 8 frames raise, 4 frames hold |
| High five | 10 frames (wind-up, slap, rebound) |
| Clap | 4 frames open, 2 frames together, 4 frames open |
| Hug | 24 frames (arms open 10, wrap 6, squeeze 4, release 4) |

---

## How Motion Differs Between Character Types

### Bouncy Bunny (high-energy, lightweight)

- Frames per walk step: 6 (fast pace even at normal speed)
- Vertical bounce: visible in every step (±8% height)
- Arm swing: exaggerated, elbows loose
- Ears: 2-frame delay follow-through on every head movement
- Idle: constant micro-bouncing, ear twitches every 3 seconds
- Squash-and-stretch: prominent on every landing

### Sluggish Turtle (slow, deliberate, heavy)

- Frames per walk step: 16 (minimum; slow is 24)
- Vertical bounce: nearly zero (±2% height)
- Arm swing: minimal, elbows close to body
- Shell: heavy — body moves first, shell drags by 4 frames
- Idle: slow breathing, eye blinks last 200 ms, head retraction occasionally
- Squash-and-stretch: minimal — mostly on hard landings only

### Waddling Penguin (medium speed, side-to-side)

- Frames per walk step: 10
- Lateral sway: prominent (±10% width shift per step)
- Arms (flippers): held out, slight lift on opposite step
- Vertical bounce: moderate (±5% height)
- Idle: weight shift every 4 seconds, flipper adjustment

### Gentle Elephant (heavy, careful, soft)

- Frames per walk step: 14
- Foot lift: low — feet barely leave the ground
- Trunk: 4-frame delay on all head motion
- Body: massive feel, slow acceleration and deceleration
- Idle: slow trunk curl, ear flap every 8 seconds

### Tiny Mouse (quick, light, nervous)

- Frames per walk step: 6 (tiny legs, fast)
- Vertical bounce: high (±12% height)
- Idle: constant whisker twitching, head darting
- Arms: held close, small quick gestures
- Stop: comes to full stop in 2 frames from any speed

### Wise Owl (stately, sharp turns)

- Frames per walk step: 12
- Head rotation: independent of body — can rotate 180°
- Idle: head tilt every 5 seconds, slow blink (nictitating membrane)
- Wings: held folded, slight lift for balance
- Motion style: smooth glides interrupted by quick head snaps
