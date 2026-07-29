# Production Planning Engine — Little Learning Town Studios

## Overview

The Production Planning Engine transforms a completed story into a **production-ready blueprint**. It answers one question:

> **"Exactly what needs to be generated?"**

Rather than immediately calling AI models, every episode is first decomposed into a structured production plan that every downstream system can understand. This is the equivalent of a film studio's **pre-production department**.

No animation begins until Phase 7 is complete.

## Philosophy

**Plan first. Generate second.**

Animation is expensive. AI generation is expensive. Rendering is expensive. Regenerating scenes wastes time and money.

Every shot must be intentional.

## Production Hierarchy

Everything follows this hierarchy. Never generate directly from an episode — always generate from individual shots.

```
Series
  ↓
Season
  ↓
Episode
  ↓
Act
  ↓
Scene
  ↓
Shot
  ↓
Frame Sequence
```

## Pipeline Diagram

```
Episode
  ↓
Production Plan
  ↓
Scene Breakdown
  ↓
Shot Breakdown
  ↓
Asset Assignment
  ↓
Camera Assignment
  ↓
Animation Assignment
  ↓
Audio Assignment
  ↓
Generation Queue
  ↓
Rendering Queue
```

## How to Use This System

### Workflow for Producers

1. **Create an Episode Manifest** — Define episode-level metadata (ID, title, duration, characters, locations, assets).
2. **Decompose the Story** — Break the story into acts, then scenes. Each scene has one purpose and one location.
3. **Break Scenes into Shots** — Decompose each scene into individual camera shots with defined purposes.
4. **Assign Cameras** — For every shot, specify camera type, movement, and position.
5. **Assign Characters** — For every shot, specify which characters are visible, their emotions, clothing, and actions.
6. **Assign Assets** — For every shot, reference assets by their production IDs (props, environment, lighting, weather).
7. **Generate Prompts** — The system builds prompts from templates using shot data. Prompts are never hardcoded.
8. **Queue Render Tasks** — Every shot becomes a render queue task. Independent shots can render in parallel.
9. **Run Quality Gates** — Every shot must pass visual, character, environment, animation, audio, and continuity QA.
10. **Approve and Render** — Only approved shots advance to final rendering.

## Key Components

### Episode Manifest
YAML metadata that drives the entire pipeline. Defines episode ID, title, duration, target age, learning goals, characters, locations, and asset inventory.

### Scene Structure
Every scene has exactly one purpose and one location. Scene metadata includes: ID, title, purpose, duration, characters, location, learning objective, dialogue, song references, interactive moments, animation notes, camera notes, asset list, mood, and transition.

### Shot Planning
Each scene is divided into individual shots. Shot types include: Establishing, Wide, Medium, Close-up, Extreme Close-up, Overhead, Side, Tracking, Follow, POV, Reaction, Cutaway, and Transition.

### Camera Planning
Cameras are assigned before generation. Movement types: Static, Pan Left, Pan Right, Tilt, Push In, Pull Out, Orbit, Track, Follow, Crane, Zoom. Children's content favors slow, stable movement.

### Timing System
Everything is timeline-based. A master timeline with timestamps drives every department. All dialogue, music, and animation events are synchronized to this timeline.

### Character Assignment
Every shot specifies: which characters appear, visibility, speaking/singing status, walking/running/dancing actions, interactions, emotion, clothing, and accessories. No assumptions are made.

### Asset Assignment
Every shot references assets by their production IDs. No free-form asset creation during production. Examples: `CHAR_LILY_001`, `ENV_PLAYGROUND_001`, `PROP_BALLOON_RED_004`.

### Prompt Generation
The storyboard never directly contains prompts. A prompt generator reads shot metadata and combines prompt templates (character, environment, animation, camera, lighting, rendering) into final prompts. This allows changing AI models without rewriting storyboards.

## Production Tokens

Production data is represented using structured YAML tokens for consistent automation and validation.

```yaml
Character: CHAR_LILY_001
Location: ENV_PLAYGROUND_001
Camera: CAM_TRACK_003
Lighting: LIGHT_SUNRISE
Emotion: HAPPY_04
Animation: RUN_LOOP_02
Weather: CLEAR
Season: SPRING
```

## Quality Gates

Every shot must pass these gates before advancing:

| Gate | Description |
|------|-------------|
| Visual QA | Image quality, lighting, composition |
| Character QA | Character appearance, clothing, proportions |
| Environment QA | Environment matches assigned ID and variant |
| Animation QA | Animation plays correctly, no clipping |
| Audio QA | Audio sync, clarity, no distortion |
| Continuity QA | Consistency across shots (clothing, props, weather) |
| Prompt QA | Prompt matches shot specification |
| Rendering QA | Resolution, format, output standards |

## Continuity Engine

Automatically verifies across shots and scenes:
- Correct clothing and accessories
- Correct weather and lighting
- Correct character age and appearance
- Correct location and props
- Correct time of day

Prevents continuity errors before rendering.

## Parallel Production

Independent shots render simultaneously:

```
Scene 1
  ↓
Shot 1   Shot 2   Shot 3   Shot 4
  ↓        ↓        ↓        ↓
  └────────┴────────┴────────┘
              ↓
          Merge
              ↓
       Scene Complete
```

This maximizes GPU utilization and speeds up production.

## Pre-Generation Checklist

Before generation begins, confirm:
- [ ] Episode manifest complete
- [ ] Timeline approved
- [ ] Story decomposed into scenes
- [ ] All shots defined
- [ ] Cameras assigned
- [ ] Characters assigned
- [ ] Assets assigned
- [ ] Animation references assigned
- [ ] Audio synchronized
- [ ] Prompt templates resolved
- [ ] Render queue generated
- [ ] Quality gates configured
- [ ] Continuity validation passed
