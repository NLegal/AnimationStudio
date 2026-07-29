# Cloth & Accessory Motion Guide

## Version 1.0 — AI Nursery Studio

---

## Introduction

Cloth and accessory motion adds life and personality to characters. At AI Nursery Studio, secondary motion is always **gentle, readable, and subordinate to the main action**.

**Golden Rule:** Secondary motion amplitude should be **10-20% of the primary motion amplitude**. It should enhance the primary action, never compete with it.

**Timing Standard:** All frame counts assume 24 fps.

---

## General Rules

| Rule | Specification |
|------|---------------|
| Amplitude | 10-20% of primary motion |
| Delay | 2-6 frames behind primary mover |
| Decay | Motion settles within 8-12 frames after primary stops |
| Curve | Smooth ease-in-out for cloth arcs |
| Priority | Never obscure face, hands, or key action |
| Wind | Consistent direction across scene |
| Multiple elements | Each moves independently, not in lockstep |

---

## Dresses / Skirts

| Property | Value |
|----------|-------|
| Delay from hip movement | 4 frames |
| Sway amplitude | 15% of hip swing |
| Walk cycle pattern | Side-to-side alternating with leg steps |
| Settle time after stop | 3 diminishing bounces, 10 frames total |

**Walk Cycle Behavior:**
```
Frame 0: Hip swings left  →  Hem begins left swing
Frame 4: Hip swings right →  Hem at center (moving left to right)
Frame 8: Hip swings left  →  Hem completes right swing
```

**Rules:**
- Hem traces a gentle arc, not sharp zigzag
- Fabric stays close to body in front, has slight float in back
- When character stops, fabric continues for 3-4 frames then settles
- Sitting: fabric drapes over knees, slight folds visible
- Running: hem lifts slightly, 20% amplitude
- Jumping: fabric rises then falls, soft billow on ascent

---

## Bows (Head Accessories)

| Property | Value |
|----------|-------|
| Bounce delay from head | 2 frames |
| Oscillation loop | 6-frame cycle |
| Amplitude | 12% of head movement |
| Settle time | 6 frames |

**Behavior:**
- Head nod: bow dips down, bounces back with 1 overshoot
- Head shake: bow wobbles side-to-side, 2-3 diminishing sways
- Walk: gentle vertical bob matching step cadence
- Run: more pronounced bounce
- Bow loops/ribbons trail behind with independent 4-frame delay

**Rotation Rules:**
- Bow rotates in opposite direction of head tilt
- Example: head tilts left → bow dips right briefly
- Loop ends of bow have their own gentle bounce
- On complete stop: 2 settling bounces

---

## Tails

| Property | Value |
|----------|-------|
| Delay from body | 3 frames |
| Follow path | Gentle S-curve |
| Amplitude (wag) | 15% of hip motion |
| Amplitude (idle) | 5-8% gentle curl |
| Settle time | 8 frames |

**Oliver Dog — Wagging Tail:**
- Happy: 12-frame full wag cycle, side-to-side
- Excited: 8-frame fast wag, wider amplitude
- Curious: 18-frame slow wag, tentative
- Content: gentle 20-frame sway
- Tail tip has 1.5x the travel of tail base

**Mia Cat — Curling Tail:**
- Content: tail lifts gently with curl at tip, 16-frame curl cycle
- Playful: tip twitches, 8-frame flick cycle
- Alert: tail stands straight up, minimal motion
- Relaxed: tail wraps around body, subtle curl
- Tail puffs on surprise (2 frames), deflates slowly (8 frames)

**Path of Motion (Dog Wag):**
```
Base:      L_____R_____L_____R
Middle:    _L_____R_____L_____R
Tip:       __L_____R_____L_____R
```

**When Sitting or Lying:**
- Tail sweeps ground gently
- Tip may curl up and down
- Minimal amplitude when seated

---

## Scarves

| Property | Value |
|----------|-------|
| Delay from shoulders | 5 frames |
| Wave loop (active) | 8 frames per wave |
| Amplitude | 15% of shoulder movement |
| Settle time | 10 frames |

**Behavior:**
- **Walking:** scarf shifts side-to-side with shoulder movement, 8-frame wave
- **Running:** scarf trails behind shoulder, more pronounced wave
- **Wind:** scarf flows in wind direction, continuous undulation
- **Turning:** scarf whips around body, 5-frame delay, settles gracefully
- **Still:** scarf hangs straight, slight movement from breathing

**Wave Pattern:**
```
Frame 0:  ───  (neutral)
Frame 2:   ─── (shift right)
Frame 4:    ───(peak right)
Frame 6:   ─── (return)
Frame 8:  ───  (neutral)
```

**Rules:**
- Scarf end moves more than scarf middle
- Width of scarf undulates naturally (edges not rigid)
- Scarf never fully wraps face
- Indoor: minimal motion
- Outdoor: consistent wind direction

---

## Balloons

| Property | Value |
|----------|-------|
| Vertical bob cycle | 16 frames full cycle |
| Bob amplitude | 8% of balloon height |
| Horizontal drift | 12 frames per gentle sway |
| String/tether | Soft curve with 3-frame lag |
| Settle time | 8 frames |

**Bob Cycle:**
```
Frame 0:  ●  (center height)
Frame 4:    ● (right, slightly higher)
Frame 8:  ●  (center height)
Frame 12: ●   (left, slightly lower)
Frame 16: ●  (center height)
```

**On String/Tether:**
- String traces a slight curve, not straight line
- When character walks, balloon trails with 6-frame delay
- String length stays constant (no stretching)
- When bumped, balloon recoils then returns to bob (4-frame settle)

**Let Go Behavior:**
1. Character opens hand (2 frames)
2. Balloon drifts upward at 50% speed (variable)
3. Gentle horizontal wobble as it rises
4. Balloons rise to top of scene and exit

---

## Hair

| Property | Value |
|----------|-------|
| Delay from head | 4 frames |
| Wave amplitude | 12% of head movement |
| Settle time | 8 frames |
| Gravity influence | 80% (floats slightly, not heavy) |

**Behavior by Hairstyle:**

| Style | Description | Delay | Amplitude |
|-------|-------------|-------|-----------|
| Short | Follows head shape, minimal bounce | 2 frames | 5% |
| Medium (chin length) | Gentle swing at ends | 3 frames | 10% |
| Long (shoulder+) | Full wave from roots to tips | 4 frames | 15% |
| Pigtails | Each pigtail swings independently | 4 frames | 18% |
| Ponytail | Single mass, sweeps behind head | 4 frames | 15% |
| Curls | Bounce with spring-like motion | 3 frames | 10% |

**Path of Motion (Long Hair on Head Turn):**
```
Head:        ───→  turns right
Hair roots:  ───→  (frame 0-1)
Hair mid:    ───→  (frame 2-3)
Hair tips:   ───→  (frame 4-5)
```

**Rules:**
- Hair flows in direction opposite to head movement
- On quick stop, hair overshoots then rebounds
- Hair settles within 8 frames of stopping
- No individual strand animation — treat as grouped masses
- Hair clips/bows in hair follow head directly, no delay

---

## Ribbons

| Property | Value |
|----------|-------|
| Delay from attachment point | 5 frames |
| Wave cycle | 8-frame continuous loop |
| Amplitude | 18% of attachment movement |
| Settle time | 10 frames |

**Behavior:**
- **Dance ribbon:** traces figure-8 or spiral pattern in air
- **Hair ribbon (trailing):** floats behind head movement
- **Gift ribbon:** lies still unless blown or moved
- **Maypole/ribbon dance:** continuous flowing arc
- **Twirling:** ribbon spirals outward from hand

**Wave Pattern:**
```
Ribbon follows a sine wave from base to tip.
Base moves first, wave propagates toward tip.
Tip has maximum amplitude (200% of base amplitude).
```

**Rules:**
- Ribbon stays relatively flat (no twisting)
- Width remains consistent along length
- The last 20% of ribbon length has the most motion
- Two attached ribbons move in counterpoint

---

## Capes

| Property | Value |
|----------|-------|
| Delay from shoulders | 6 frames |
| Billow cycle | 12 frames |
| Amplitude (walk) | 18% of shoulder movement |
| Amplitude (run) | 30% of shoulder movement |
| Settle time | 12 frames |

**Behavior:**
- **Walking:** cape sways behind, hem traces gentle wave
- **Running:** cape billows outward, flutters
- **Turning:** cape swings around, wraps slightly, then unwraps
- **Stopping:** cape continues forward, then settles back
- **Sitting:** cape drapes around base, spread on ground

**Cape Arc on Turn:**
```
Shoulder turn:  ────────────→ (180°)
Cape start:     ──────────  → (frame 0)
Cape mid:       ────────    → (frame 3-4)
Cape hem:       ──────      → (frame 6)
Cape settle:    ────────────→ (frame 12-14, after full stop)
```

**Rules:**
- Cape hem traces a curved path, not straight line
- Cape interior visible during billow
- Cape settles by falling gently from hem upward
- Clasp at neck stays fixed
- Never obscures face

---

## Aprons

| Property | Value |
|----------|-------|
| Delay from body | 3 frames |
| Amplitude | 8% of body movement |
| Settle time | 6 frames |

**Behavior:**
- **Walking:** apron hem shifts slightly
- **Bending:** apron falls forward, hangs away from body
- **Standing still:** hangs straight, micro-motion from breathing
- **Running:** apron hem flutters slightly

Apron motion is the most subtle of all cloth elements — barely noticeable unless actively looked for.

---

## Cloth Interaction with Environment

| Environment Factor | Effect on Cloth |
|-------------------|-----------------|
| Wind (gentle breeze) | Consistent drift, 15% amplitude |
| Wind (strong gust) | 25% amplitude, 2-second max gust duration |
| Rain | Cloth sticks slightly, heavier feel |
| Water (splashing) | Cloth gets wet spots, slightly heavier (3 frames) |
| Sitting on ground | Fabric spreads, drapes over surface |
| Brushing past objects | Cloth catches briefly, pops free |

---

## Motion Amplitude Reference

| Accessory | Walk Amplitude | Run Amplitude | Idle | Max Amplitude |
|-----------|---------------|---------------|------|---------------|
| Dress hem | 15% | 25% | 2-3% | 40% (spin) |
| Bow (head) | 12% | 18% | 3% | 25% |
| Tail (dog) | 15% | 22% | 5% | 30% (excited) |
| Tail (cat) | 10% | 15% | 8% | 20% |
| Scarf | 15% | 22% | 3% | 35% |
| Balloon | 8% | 12% | 8% (bob) | 25% |
| Hair (long) | 12% | 20% | 3% | 30% |
| Ribbon | 18% | 25% | 2% | 50% (dance) |
| Cape | 18% | 30% | 2% | 45% |
| Apron | 8% | 12% | 2% | 15% |

---

## Quality Checklist

| Check | Pass/Fail |
|-------|-----------|
| Secondary motion amplitude ≤ 20% of primary | ☐ |
| Cloth settles within 8-12 frames of character stop | ☐ |
| No secondary motion obscures face | ☐ |
| Multiple cloth elements move independently | ☐ |
| Motion reads clearly at 24 fps | ☐ |
| Wind direction is consistent throughout scene | ☐ |
| Sitting/draping behavior is appropriate to surface | ☐ |
| Accessories follow body, not lead it | ☐ |
| Each element has appropriate delay | ☐ |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-29 | Initial cloth and accessory motion guide |
