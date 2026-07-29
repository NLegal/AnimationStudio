# Episode Template Guide

## How to Use the Template Directory Structure

The `TEMPLATE` directory provides a ready-to-copy structure for every new episode. When starting a new episode, copy the entire `TEMPLATE` directory and rename it with your episode ID (e.g., `Episode_S01E001`). Each subdirectory serves a specific role in the production pipeline.

## Directory Structure

```
Episode_S01E001/
├── Manifest/          # Episode manifest YAML — drives the entire pipeline
├── Storyboard/        # Story breakdown, narrative structure, act definitions
├── Timeline/          # Master timing events synchronized to the episode clock
├── Scenes/            # Individual scene files with metadata per scene
├── Shots/             # Individual shot files with full shot metadata
├── Camera/            # Camera assignments, types, and movement plans
├── Animation/         # Animation references, clip IDs, and loop assignments
├── Audio/             # Audio references — dialogue, narration, music, SFX
├── Prompts/           # Generated prompts (never manually edited)
├── Assets/            # Asset manifest — all props, environments, characters
├── RenderQueue/       # Render task queue — one task per shot
├── QC/                # Quality control reports per shot
└── Metadata/          # Production metadata, versions, changelogs
```

## Step-by-Step Episode Production Workflow

### Step 1: Create Episode Manifest
Copy the template and create `Manifest/episode.yaml`. Define episode-level metadata: ID, title, duration, target age, learning goal, characters, locations, and assets. The manifest drives decisions throughout the pipeline.

### Step 2: Decompose Story into Scenes
Break the story into individual scenes. Each scene must have exactly **one purpose** and **one location**. Create one file per scene in `Scenes/`. Typical episode structure: Opening → Introduction → Learning → Adventure → Song → Practice → Celebration → Ending.

### Step 3: Break Scenes into Shots
For each scene, define individual camera shots. Each shot has a specific purpose and type (wide, close-up, reaction, etc.). Create one file per shot in `Shots/`. The number of shots varies per scene but averages 3–5.

### Step 4: Assign Cameras
For every shot, specify camera type, movement, and position. Children's content favors slow, stable movement (static, slow pan). Document camera plans in `Camera/`.

### Step 5: Assign Characters and Assets
For every shot:
- Specify which characters appear, their emotions, clothing, and actions
- Reference all assets by their production IDs
- Assign environment, lighting, and weather
- Document in the shot file's character and asset sections

### Step 6: Generate Prompts
Run the prompt generator. It reads shot metadata and combines prompt templates into final generation prompts. Prompts are written to `Prompts/`. Never manually edit generated prompts — fix the source data and regenerate.

### Step 7: Queue Render Tasks
Each shot becomes a render queue task. Independent shots can render in parallel. Tasks are written to `RenderQueue/`.

### Step 8: Run Quality Gates
Every shot must pass all quality gates: visual, character, environment, animation, audio, continuity, prompt, and rendering QC. Reports are stored in `QC/`.

### Step 9: Approve and Render
Only shots that pass all quality gates advance to final rendering. Failed shots are returned for revision with a QC report explaining the issue.

## Example Episode Production Walkthrough

**Episode:** S01E001 — "Five Colorful Ducks"
**Duration:** 3:12
**Target Age:** 2–5
**Learning Goal:** Primary Colors

1. **Manifest created** with 3 characters (Lily Bunny, Ben Bear, Mama Duck), 1 location (Sunny Pond), and 3 asset types.
2. **Story decomposed** into 6 scenes: Opening, Meet the Ducks, Color Song, Practice Colors, Pond Adventure, Celebration.
3. **Each scene broken** into 3–5 shots, totaling 24 shots.
4. **Cameras assigned**: wide establishing shots, medium dialogue shots, close-up reaction shots.
5. **Characters and assets assigned** per shot. Lily wears pink dress in all scenes. Mama Duck has yellow feathers.
6. **Prompts generated** from templates — 24 unique prompts produced.
7. **Render queue** generated — 24 tasks, 6 groups (one per scene) for parallel rendering.
8. **Quality gates** run — all 24 shots pass visual, character, and continuity checks.
9. **Episode approved** for final render.
