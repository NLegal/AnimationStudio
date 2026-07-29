# Animation Bible — Little Learning Town Studios

### Version 1.0

---

## Overview

Welcome to the **Little Learning Town Studios Animation Bible**. This document is the master reference for every animation decision made in the studio.

**Phase 4** establishes how everything moves. Characters, environments, and assets are complete. This phase standardizes movement, facial acting, timing, camera behavior, and physical interactions. Every animation produced by the studio follows these rules to maintain a consistent, recognizable style.

**Animation Philosophy:** Movement should feel playful, soft, rounded, energetic, safe, readable, slightly exaggerated, and easy for young children (ages 2-5) to follow. Avoid fast, jerky, or chaotic motion.

---

## Quick Reference

| Parameter | Standard Value |
|---|---|
| Frame rate | 24 fps (cinematic) |
| Export rate | 30 fps (platform alternate) |
| Blink rate | 6-15 blinks per minute (every 4-10 seconds) |
| Blink duration | 2-4 frames |
| Walk cycle | 8 frames per step (normal) / 12 frames per step (slow) |
| Run cycle | 6 frames per step |
| Dance loop | 24 frames (4-beat) / 48 frames (full rotation) |
| Idle breathing | 24-30 frames per breath cycle |
| Child-friendly pause | 2-3 seconds between key actions |

---

## Key Principles

| Principle | Description |
|---|---|
| **Playful** | Movement should feel fun and joyful. Exaggerate slightly beyond real life. |
| **Soft** | No sharp or mechanical motion. Use ease-in/ease-out on all movements. |
| **Rounded** | Curved motion paths, not straight lines. Circular arm swings, curved head turns. |
| **Energetic** | Characters have life energy. They bounce, sway, and move with purpose. |
| **Safe** | Nothing scary, violent, or aggressive. Even "chase" scenes feel gentle. |
| **Readable** | A 2-year-old should understand what's happening at a glance. |
| **Slightly exaggerated** | Big expressions, clear gestures, readable poses. Not subtle. |
| **Child-friendly pacing** | Slow enough to follow, fast enough to hold attention. |

---

## Table of Contents

### Core Standards

| Section | File | Description |
|---|---|---|
| **This Bible** | `ANIMATION_BIBLE.md` | Master index, quick reference, key principles |
| **Animation Philosophy** | `PHASE4.md` (root) | Full Phase 4 objectives and philosophy |

### Character Motion

| Section | File | Description |
|---|---|---|
| **Motion Standards** | `Animation/Motion/` | Walk cycles, run cycles, jump library, idle animation standards |
| **Facial Animation** | `Animation/Facial/` | Smile levels, eye openness, eyebrow positions, lip shapes, emotion intensity scale (1-5) |
| **Eye Animation** | `Animation/Facial/` | Blink frequency, blink duration, eye tracking, eye contact rules |
| **Mouth Animation** | `Animation/Facial/` | Talking, singing, laughing, yawning, whispering, breathing mouth shapes |
| **Hand Gestures** | `Animation/Gestures/` | Wave, point, thumbs up, high five, hug, clap, hold, pick up, put down, throw, catch |
| **Body Animation** | `Animation/Motion/` | Full body motion standards for all character types |

### Interaction & Physics

| Section | File | Description |
|---|---|---|
| **Interactions** | `Animation/Interactions/` | Open door, eat, drink, kick, throw, catch, build, draw, brush teeth, wash hands, plant, feed, pet, ride |
| **Physics Rules** | `Animation/Physics/` | Stylized physics: light objects, predictable motion, soft bounces, no violent behavior |
| **Cloth & Accessories** | `Animation/Physics/` | Secondary motion: dress sway, bow bounce, tail follow, scarf flutter, balloon float |

### Camera & Timing

| Section | File | Description |
|---|---|---|
| **Camera Language** | `Animation/Camera/` | Establishing, wide, medium, close-up, over-the-shoulder, tracking, push-in, pan, tilt |
| **Scene Transitions** | `Animation/Timing/` | Cross dissolve, fade, wipe, match cut, storybook page turn, slide |
| **Timing Standards** | `Animation/Timing/` | Pacing guidelines for preschool audience, shot length standards |

### Prompt Library

| Section | File | Description |
|---|---|---|
| **Animation Prompts** | `Animation/PromptTemplates/animation-prompts.md` | Walk cycles (6), run cycles (3), dance loops (4), facial expressions (6), interactions (8), scene types (4) |
| **Negative Prompts** | `Animation/NegativePrompts/animation-negatives.md` | Motion problems, facial problems, style problems, technical problems, composition problems, per-type negatives |

### Quality Control

| Section | File | Description |
|---|---|---|
| **Quality Checklist** | `Animation/QUALITY_CHECKLIST.md` | Pre-generation checks, post-generation checks, rejection criteria, per-type checklists, sign-off procedure |

---

## How to Use This Bible

### For New Animators

1. **Start here** — Read the Key Principles above to understand our studio's animation philosophy.
2. **Read PHASE4.md** in the root directory for the full phase context.
3. **Review the Quick Reference** table for baseline technical specs.
4. **Find your shot type** in the Table of Contents and open the corresponding section.
5. **Select a prompt template** from `Animation/PromptTemplates/animation-prompts.md`.
6. **Prepare negative prompts** from `Animation/NegativePrompts/animation-negatives.md`.
7. **Run QC** against `Animation/QUALITY_CHECKLIST.md` before delivering.

### For Returning Animators

- Use the **Quick Reference** table at the top of this page for rapid lookup.
- Consult the **Table of Contents** to navigate directly to the section you need.
- Always run **QC Sign-Off** before delivery.

### For Reviewers

- Use the **Rejection Criteria** in `Animation/QUALITY_CHECKLIST.md` for automatic fails.
- Verify animation type matches the template used.
- Check that negative prompts were applied.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-07-29 | Animation Department | Initial release — Phase 4 complete |

---

*Document maintained by Little Learning Town Studios — Animation Department*
