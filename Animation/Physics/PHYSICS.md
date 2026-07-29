# Stylized Physics Rules

## Version 1.0 — AI Nursery Studio

---

## Core Philosophy

Physics at AI Nursery Studio prioritize **stylized appeal over realism**. Every physical behavior is designed to be:

- **Child-friendly** — never violent, scary, or unpredictable
- **Predictable** — children can anticipate what happens next
- **Readable** — physics are clear and easy to follow
- **Soft** — rounded, gentle, forgiving motion
- **Fun** — slightly exaggerated for entertainment value

The guiding question: *Does this feel safe and understandable for a 3-year-old?*

---

## Gravity

| Property | Setting | Notes |
|----------|---------|-------|
| Strength | 85% of real gravity | Characters float slightly on jumps |
| Jump arc | Extended peak hold (4-6 frames at apex) | Gives children time to see the moment |
| Fall speed | 70% of real fall speed | Never feels dangerous or fast |
| Landing | Soft compression, 2-3 frame cushion | Knees bend deeply, no hard impact |

**Character Gravity:**
- Characters weigh approximately 60-70% of realistic body weight
- Anticipation crouch before jumps: 4 frames
- Apex hang time: 4-6 frames of near-stillness
- Landing cushion: 4 frames of leg compression

**Object Gravity:**
- Objects fall at 75% of realistic acceleration
- Light objects (paper, leaves) fall at 60%
- Heavy objects (blocks, books) fall at 80%

---

## Weight

| Object Type | Perceived Weight | Behavior |
|-------------|------------------|----------|
| Small toys | Very light | Single hand lift, quick motion |
| Books, blocks | Light | Two hands optional, easy lift |
| Furniture | Moderate | Push with effort, slide smoothly |
| Large objects | Moderate | Multiple characters may work together |

**Rules:**
- Objects feel manageable for small characters
- No object is too heavy for a character to lift with effort
- Weight is shown through body mechanics, not through slow speed alone
- Characters show effort expression (strain face, small grunt) for heavier items

---

## Bounce

| Type | Behavior | Duration |
|------|----------|----------|
| Ball bounce | 3 diminishing bounces, 50% height loss per bounce | 18 frames (8+6+4) |
| Character landing | 2-3 diminishing vertical bobs | 12 frames (6+4+2) |
| Object drop bounce | 2 small bounces if object is bouncy | 10 frames (6+4) |
| Soft surface (bed) | 1-2 gentle wobbles after landing | 8 frames |

**Bounce Decay Formula:**
```
Bounce 1: 100% of initial height/force
Bounce 2: 50%
Bounce 3: 25%
Bounce 4: 0% (settle)
```

**Implementation Notes:**
- Use ease-out curve on bounce ascent
- Use ease-in curve on bounce descent
- No infinite bouncing
- Characters may add small "whoa" expression on bounce

---

## Impact

| Impact Type | Visual Response | Duration |
|-------------|-----------------|----------|
| Gentle bump | Small recoil, blink | 4 frames |
| Walk into object | Stop, look, rub head, smile | 12 frames |
| Object collision | Soft compression, settle | 6 frames |
| Character collision | Both characters bounce apart, sit | 16 frames |
| Fall onto ground | Spread-eagle, 2-frame pause, get up | 24 frames total |

**Rules:**
- No violent reactions (no flying backward, no spin-outs)
- Impacts are followed by a pause to assess
- Characters may say "Oops" or "Uh oh"
- Pain is never shown — only surprise or mild frustration

---

## Falling

| Fall Type | Behavior | Frames |
|-----------|----------|--------|
| Trip | Stumble forward, catch balance, recover | 16 |
| Slip | Feet go forward, land sitting, look around, stand | 24 |
| Drop from height | Float down (parachute effect), land softly | varies |
| Slide down | Smooth descent, sit at bottom | varies |

**Philosophy:**
- Falls are **comedic and safe**, never scary
- Characters always land softly or are caught
- Height limit: never fall more than character's own height
- Falls end with character sitting, not lying prone (unless asleep)
- Getting up takes 8-12 frames

---

## Stacking

| Property | Behavior |
|----------|----------|
| Block stacking | Blocks align easily, slight wiggle on placement |
| Stack wobble | Gentle 4-frame oscillation after placement |
| Stack stability | Stacks stay steady up to 8 blocks |
| Stack collapse | Blocks "whoosh" apart safely, no pieces fly aggressively |

**Block Stacking Animation:**
- Each block placed: +2 frame settle time
- Wobble amplitude: 2-3 degrees, decaying
- Stack collapse: blocks slide apart or tip gently over (3-4 frames)
- No block breaks on collapse

---

## Rolling

| Property | Behavior |
|----------|----------|
| Ball roll speed | Moderate, child-friendly pace |
| Deceleration | Soft ease-out over 12-24 frames |
| Surface friction | Gentle slowdown on grass/rug |
| Slope rolling | Steady speed, slight bobble |
| Stop | 2-3 small back-and-forth rocks |

**Rolling Motion Curve:**
- Ease-in (4 frames), steady roll (variable), ease-out (8-12 frames)
- Balls may hit small obstacles and redirect gently
- No aggressive bouncing or wild trajectories

---

## Swinging

| Property | Behavior |
|----------|----------|
| Pendulum style | Gentle arc, no aggressive pumping |
| Decay rate | 10% amplitude loss per swing |
| Full swing cycle | 24-30 frames |
| Swing start | Small push from ground or character |
| Swing stop | Gradual slow over 3-4 cycles |

**Swing Arc:**
- Max angle: 45 degrees from vertical
- Ease-in-out curve throughout arc
- Chain/rope follows with slight trailing curve
- Character leans with motion

---

## Splashing

| Property | Behavior |
|----------|----------|
| Water drops | Stylized round drops, 4-6 per splash |
| Ripple pattern | 3 concentric rings expanding outward |
| Ripple expansion | 12 frames from center to edge |
| Water rise | Gentle arc, drops catch light |

**Splash Sequence:**
1. Contact: water surface deforms (2 frames)
2. Rise: water column rises (3 frames)
3. Crown: drops separate at top (3 frames)
4. Fall: drops descend (4 frames)
5. Ripples: rings expand and fade (12 frames)

No large water explosions. Puddle splashes are small and contained.

---

## Breaking

**Rule: Objects NEVER break violently.**

| Situation | Behavior |
|-----------|----------|
| Object dropped | Bounces, does not break |
| Object knocked over | Tips, lands on side, remains intact |
| "Break" needed for story | Object comes apart in 2-3 large pieces, safely |
| Glass/cup | Flexible material, dents rather than shatters |
| Crayon snapped | Two clean halves, rounded edges |

For narrative "breakage":
- Pieces separate slowly over 4-6 frames
- No sharp edges visible
- Sound effect is a soft "pop" not a "crash"
- Pieces can be put back together easily

---

## Timing Curves

| Motion Type | Curve | Usage |
|-------------|-------|-------|
| Approach reach | Ease-out | Arm extending toward object |
| Withdraw | Ease-in | Arm returning to neutral |
| Most motion | Ease-in-out | Walk cycles, head turns, bends |
| Bounce | Custom ease-out with overshoot | Landing, ball bounce |
| Anticipation | Ease-in (backward) | Pre-jump crouch, wind-up |
| Follow-through | Custom ease-out | Arm settling after throw |
| Elastic | Ease-in-out with overshoot | Hair bounce, tail wag |

**Default Curve Parameters:**
- Ease-in-out: smooth S-curve, 0% at start, 100% at end
- Hold at key poses: 2-4 frames for readability
- No linear motion unless mechanical

---

## Anticipation

| Action | Anticipation Frames | Description |
|--------|--------------------|-------------|
| Jump | 4 | Crouch, arms back, eyes up |
| Throw | 3 | Wind-up, weight shift back |
| Reach | 2 | Eyes look at target, shoulder starts |
| Stand up | 3 | Rock forward, hands on knees |
| Sit down | 3 | Hands reach behind, bend knees |
| Turn head | 2 | Eyes move first, then head, then torso |

**Rule:** Every action has at least 2 frames of anticipation. The bigger the action, the more anticipation.

---

## Follow-Through

| Action | Follow-Through Frames | Description |
|--------|----------------------|-------------|
| Throw complete | 5 | Arm continues arc after release |
| Kick | 4 | Leg continues forward after ball contact |
| Jump landing | 4 | Knees compress, arms settle |
| Point | 3 | Arm extends past target, settles back |
| Stop walking | 4 | Upper body continues forward, then settles |

**Rule:** Every action has 3-6 frames of follow-through. Body parts settle sequentially, not simultaneously.

---

## Overlap

| Body Part | Delay from Main Motion | Motion Type |
|-----------|----------------------|-------------|
| Ears (Lily) | 3 frames | Flop/bounce after head move |
| Tail (Oliver, Mia) | 3 frames | S-curve follow behind body |
| Dress hem | 4 frames | Sway behind hip motion |
| Long hair | 4 frames | Bounce after head stop |
| Scarf/scarf ends | 6 frames | Wave after shoulder move |
| Bow on head | 2 frames | Bobble on top of head |

**Overlap Formula:**
```
Main Body Part: 100% motion, frame 0
Secondary Part: 80% motion, frame +2
Tertiary Part: 60% motion, frame +4
Settle: 40% motion, frame +6
```

---

## Object-Specific Physics

| Object | Physics Behavior |
|--------|-----------------|
| Ball | Bounces 3 times, rolls with deceleration |
| Block | Placed with wobble, slides with friction |
| Paper | Flutters, drifts, lightest weight |
| Cup | Stable when placed, tilts when bumped |
| Book | Slides open, pages turn with gentle flip |
| Pencil | Rolls when dropped, stops quickly |
| Toy car | Rolls with push, decelerates naturally |
| Balloon | Bobs upward, gentle side drift |
| Flower pot | Stable, wobbles on placement |
| Watering can | Tilts, water pours in arc |

---

## Environmental Physics

| Element | Behavior |
|---------|----------|
| Grass | Sways gently, flattens slightly under feet |
| Water | Gentle ripples, no violent waves |
| Leaves | Drift down, swirl in wind, settle softly |
| Snow | Floats down, accumulates in soft mounds |
| Bubbles | Rise slowly, pop gently after 3-5 seconds |
| Rain | Soft streaks, gentle pitter-patter, no storms |
| Wind | Objects sway, hair/ribbons trail, gentle |

---

## Summary Reference

| Physics Element | Keyword | Value |
|-----------------|---------|-------|
| Gravity | Lighter | 85% real |
| Fall speed | Slower | 70% real |
| Bounce decay | Quick | 50% per bounce |
| Anticipation | Minimum | 2-3 frames |
| Follow-through | Extended | 4-6 frames |
| Overlap delay | Sequential | 2-6 frames |
| Impact | Soft | No violence |
| Breaking | Never | Come apart safely |
| Weight | Light | Child-manageable |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-29 | Initial stylized physics rules documentation |
