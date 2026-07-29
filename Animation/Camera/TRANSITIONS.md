# Scene Transition Library

## Version 1.0 — AI Nursery Studio

---

## Introduction

Transitions at AI Nursery Studio are **gentle guides** that help children understand when a scene changes. Every transition should feel smooth and predictable. The goal is clarity, not spectacle.

**Core Principles:**
- Transitions serve story comprehension
- Children should never feel disoriented by a scene change
- Speed matches preschool pacing (slower than adult content)
- Style is consistent across episodes
- Flashy effects distract — stay simple

**Duration Standard:** All frame counts at 24 fps.

---

## Transition Library

---

### Cross Dissolve

| Property | Specification |
|----------|---------------|
| **Duration** | 12-16 frames (0.5-0.67 seconds) |
| **Description** | First scene fades out while second scene fades in, overlapping in the middle |
| **Opacity Curve** | Linear cross-fade: Scene A 100%→0%, Scene B 0%→100% |
| **When to Use** | Standard scene change, time passing, location change |

**Usage Rules:**
- Default transition — use unless another transition is specifically called for
- Not for changes within the same continuous scene (use cut)
- Not for rapid back-and-forth between locations

**Opacity Progression:**
```
Frame  0: Scene A 100% | Scene B 0%
Frame  4: Scene A 75%  | Scene B 25%
Frame  8: Scene A 50%  | Scene B 50%
Frame 12: Scene A 25%  | Scene B 75%
Frame 16: Scene A 0%   | Scene B 100%
```

---

### Fade to Black

| Property | Specification |
|----------|---------------|
| **Duration** | 16 frames (0.67 seconds) |
| **Description** | Scene fades to solid black screen, holds black for 8-12 frames, then next scene begins |
| **Opacity Curve** | Scene fades linearly to black (100%→0% over 16 frames) |
| **When to Use** | End of a story segment, end of episode, significant time passage |

**Usage Rules:**
- Indicates a clear break in the story
- Always followed by fade from black on next segment
- Hold on black: 8-12 frames (provides pause for children)
- Use maximum 2-3 times per episode

**Progression:**
```
Frame  0: Scene visible (100%)
Frame  4: Scene fading (75%)
Frame  8: Scene fading (50%)
Frame 12: Scene fading (25%)
Frame 16: Black (0%)
Hold:     Black (0%) for 8-12 frames
```

---

### Fade from Black

| Property | Specification |
|----------|---------------|
| **Duration** | 12 frames (0.5 seconds) |
| **Description** | Screen starts black, scene fades in to full visibility |
| **Opacity Curve** | Scene appears linearly from black (0%→100% over 12 frames) |
| **When to Use** | Beginning of a story segment after fade to black |

**Usage Rules:**
- Pairs with Fade to Black
- Faster than fade-out (12 frames vs 16 frames)
- 0 hold frames — scene begins immediately after fade completes

**Progression:**
```
Frame  0: Black (0%)
Frame  4: Scene appearing (25%)
Frame  8: Scene appearing (75%)
Frame 12: Scene visible (100%)
```

---

### Fade to White

| Property | Specification |
|----------|---------------|
| **Duration** | 12 frames (0.5 seconds) |
| **Description** | Scene fades to solid white screen, holds for 6-8 frames |
| **Opacity Curve** | Scene fades linearly to white (100%→0% over 12 frames) |
| **When to Use** | Dream sequence, memory/flashback, imagination scene, fantasy |

**Usage Rules:**
- Must be motivated by story (dream, memory, imagination)
- Return from white using Fade from White (same structure)
- White is soft and warm, not harsh
- Use maximum 1 time per episode

**Progression:**
```
Frame 0: Scene visible (100%)
Frame 4: Scene fading (67%)
Frame 8: Scene fading (33%)
Frame 12: White (0%)
Hold:   White for 6-8 frames
```

---

### Gentle Slide

| Property | Specification |
|----------|---------------|
| **Duration** | 16 frames (0.67 seconds) |
| **Description** | Current scene slides out as next scene slides in, moving same direction |
| **Direction** | Left to right (default), right to left, up, or down |
| **Easing** | Smooth ease-in-out |
| **When to Use** | Scene-to-scene within same location or time continuum |

**Movement Options:**
| Direction | Visual Effect | Best For |
|-----------|---------------|----------|
| Left to right | Scene slides right, next scene follows from left | Moving forward in story |
| Right to left | Scene slides left, next scene follows from right | Returning, backtracking |
| Up | Scene slides up, next scene rises from bottom | Revealing new area |
| Down | Scene slides down, next scene descends from top | Looking down at something |

**Usage Rules:**
- Both scenes move in parallel (no one scene stays still)
- Use when characters move to adjacent space (room to room)
- Not for large time jumps

**Progression (Left to Right):**
```
Frame  0: Scene A at center (100%) | Scene B off-screen right
Frame  4: Scene A shifting left      | Scene B entering from right
Frame  8: Both scenes split screen   | Scene B 50%, Scene A 50%
Frame 12: Scene A exiting left       | Scene B at center (75%)
Frame 16: Scene A gone               | Scene B at center (100%)
```

---

### Wipe

| Property | Specification |
|----------|---------------|
| **Duration** | 12 frames (0.5 seconds) |
| **Description** | A line moves across the screen revealing the next scene, pushing the current scene away |
| **Direction** | Left to right or right to left |
| **Easing** | Linear |
| **When to Use** | Change of location, passage of time, parallel action |

**Directions:**
| Direction | Effect | Use |
|-----------|--------|-----|
| Left to right | Wipe line moves left→right | Standard location change |
| Right to left | Wipe line moves right→left | Returning to previous location |

**Usage Rules:**
- Faster than cross dissolve — use for brisk scene changes
- Wipe line is a straight vertical edge
- No decorative patterns or shapes on wipe edge
- Use maximum 2 times per episode
- Not for emotional transitions (use dissolve)

**Progression (Left to Right):**
```
Frame  0: Scene A fills frame
Frame  4: Wipe line at 33% — Scene B visible on left
Frame  8: Wipe line at 67% — Scene B fills left 2/3
Frame 12: Wipe line exits right — Scene B fills frame
```

---

### Storybook Page Turn

| Property | Specification |
|----------|---------------|
| **Duration** | 20 frames (0.83 seconds) |
| **Description** | Scene curls from right side like a book page, revealing next scene underneath |
| **Easing** | Custom page-curve ease |
| **When to Use** | Optional stylistic transition — reinforces storybook theme |

**Progression:**
```
Frame  0: Scene A flat (page flat)
Frame  4: Right edge of scene curls upward, shadow beneath
Frame  8: Page lifts to 45°, Scene B peeking at bottom
Frame 12: Page at 90°, Scene B half visible
Frame 16: Page at 135°, Scene B mostly visible
Frame 20: Page completes turn, Scene B flat (100%)
```

**Usage Rules:**
- Stylistic choice — use consistently or not at all
- If used, apply to ALL episode transitions for consistency
- Page turns left to right (standard book direction)
- Can use gentle page curl sound effect
- Corner of page may have slight shadow for depth

---

### Match Cut

| Property | Specification |
|----------|---------------|
| **Duration** | 0 frames matching + 8 frames dissolve (0.33 seconds) |
| **Description** | Two visually similar compositions matched in shape/position; one dissolves into the other |
| **Easing** | Linear dissolve after match frame |
| **When to Use** | Thematic connection between two scenes, clever visual transitions |

**Match Cut Examples:**
| Scene A (End) | Scene B (Start) | Connection |
|---------------|-----------------|------------|
| Ball shape | Sun/moon shape | Round objects |
| Character's eye | Window shape | Circular framing |
| Block tower | Building | Vertical structure |
| Spiral drawing | Snail shell | Spiral shape |
| Puddle | Lake | Water body |

**Progression:**
```
Frame 0: Scene A ends on match composition
Frame 2: Scene A → Scene B dissolve begins
Frame 6: Dissolve midpoint — both scenes visible
Frame 8: Scene B fully established
```

**Usage Rules:**
- Both frames must share a clear visual similarity
- Match should be obvious enough for a preschooler to notice
- Use maximum 1 time per episode
- The dissolve portion is fast (8 frames)
- Not for standard transitions — special use only

---

### Iris Out / Iris In

| Property | Specification |
|----------|---------------|
| **Duration** | 12 frames (0.5 seconds) each direction |
| **Description** | Scene shrinks to a circle (iris out) or expands from a circle (iris in) |
| **Easing** | Smooth ease-out for iris out, ease-in for iris in |
| **When to Use** | Emphasis on a character, end of a story moment, focused attention |

**Iris Out (Closing):**
```
Frame  0: Full scene visible
Frame  4: Circle mask begins closing from edges
Frame  8: Circle reduces to character's face area
Frame 12: Circle closes to a point (black)
Hold:     Black for 6 frames
```

**Iris In (Opening):**
```
Frame  0: Black screen, small circle opening
Frame  4: Circle expands, character's face visible
Frame  8: Circle expands to full frame width
Frame 12: Full scene visible
```

**Usage Rules:**
- Circle is always centered on character's face or key object
- Circle has soft edges (not sharp mask)
- Use maximum 1 time per episode
- Pairs well with end of emotional moment

---

### Cut (No Transition)

| Property | Specification |
|----------|---------------|
| **Duration** | 0 frames |
| **Description** | Instant change between shots — no transition effect |
| **Easing** | N/A |
| **When to Use** | Within the same continuous scene |

**Usage Rules:**
- Default for shot-to-shot changes within a scene
- Only use when spatial continuity is maintained
- Not for location changes (use dissolve or other transition)

---

## Transition Selection Guide

| Scenario | Recommended Transition |
|----------|----------------------|
| New scene, new location | Cross Dissolve (12-16 frames) |
| New scene, same location | Cross Dissolve or Gentle Slide |
| End of story segment | Fade to Black (16 frames) |
| Start of story segment | Fade from Black (12 frames) |
| Dream / imagination | Fade to White (12 frames) |
| Adjacent rooms | Gentle Slide (16 frames) |
| Location change (brisk) | Wipe (12 frames) |
| Thematic connection | Match Cut (8 frames dissolve) |
| Character emphasis (end) | Iris Out (12 frames) |
| Character emphasis (start) | Iris In (12 frames) |
| Within same scene | Cut (0 frames) |
| Storybook style | Page Turn (20 frames) |

---

## Transition Speed Reference

| Transition | Total Duration | Frames (24 fps) | Speed Feel |
|------------|---------------|-----------------|------------|
| Cut | 0 frames | 0 | Instant |
| Match Cut | 8 frames | 8 | Fast |
| Wipe | 12 frames | 12 | Brisk |
| Fade to White | 12 frames | 12 | Gentle |
| Fade from Black | 12 frames | 12 | Gentle |
| Cross Dissolve | 12-16 frames | 12-16 | Standard |
| Gentle Slide | 16 frames | 16 | Smooth |
| Fade to Black | 16 frames | 16 | Deliberate |
| Iris Out/In | 12 frames | 12 | Focused |
| Storybook Page Turn | 20 frames | 20 | Stylized |

---

## Transition Sequencing

### Episode Opening
```
Fade from Black (12 frames) → Establishing Shot
```

### Standard Scene Sequence
```
[Scene 1] → Cross Dissolve (16 frames) → [Scene 2]
```

### Story Segment Close
```
[Final shot of segment] → Fade to Black (16 frames) → [8-12 frame hold] → Fade from Black (12 frames) → [Next segment]
```

### Episode Closing
```
[Final shot] → Fade to Black (16 frames) → [8-12 frame hold] → End Credits
```

---

## Forbidden Transitions

| Transition | Reason for Exclusion |
|------------|---------------------|
| Flash cut | Too fast for preschool comprehension |
| Random/split wipe | Too distracting |
| 3D flip/rotate | Disorienting |
| Strobe/flicker | Seizure risk |
| Swirl/spiral | Disorienting |
| Zoom burst | Too aggressive |
| Glitch/digital artifact | Fragments the image |
| Explosion/particle burst | Too violent |
| Page peel (3D curl) | Overly complex |
| Radial wipe | Unfocused |
| Checkerboard | Distracting pattern |

---

## Quality Checklist

| Check | Pass/Fail |
|-------|-----------|
| Transition matches story context | ☐ |
| Duration is appropriate (12-16 frames default) | ☐ |
| No more than 2-3 fades to black per episode | ☐ |
| No forbidden transitions used | ☐ |
| Match cut has clear visual similarity | ☐ |
| Page turn is consistent if used stylistically | ☐ |
| Iris is centered on meaningful subject | ☐ |
| Within-scene changes use cuts, not dissolves | ☐ |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-29 | Initial scene transition library |
