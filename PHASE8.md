# Phase 8 — AI Image Generation & Visual Asset Pipeline

## AI Nursery Studio

### Version 2.0

---

# Vision

Everything created so far has been planning.

* Characters
* World
* Assets
* Animation Rules
* Audio
* Story Engine
* Storyboards

Phase 8 is where the studio begins **creating visual content**.

This phase builds a **professional AI image generation pipeline** capable of producing consistent, reusable, production-quality artwork that becomes the foundation for animation.

The objective is **not simply generating pretty pictures**.

The objective is generating **production-ready visual assets**.

---

# Primary Objectives

Build a scalable image generation system capable of producing:

* Characters
* Expressions
* Poses
* Props
* Backgrounds
* Environment variations
* Lighting variations
* Camera angles
* Storyboard frames
* Keyframes
* Promotional artwork
* Thumbnails

Every image should be reusable.

---

# Design Philosophy

Never generate random artwork.

Every generated image must satisfy:

* Character consistency
* Style consistency
* World consistency
* Color consistency
* Scale consistency
* Lighting consistency
* Asset consistency

The image generator is building a production library—not a gallery.

---

# Image Generation Pipeline

```text
Episode Package
        │
        ▼
Storyboard
        │
        ▼
Shot Package
        │
        ▼
Prompt Builder
        │
        ▼
Reference Injection
        │
        ▼
Image Generation
        │
        ▼
Quality Validation
        │
        ▼
Image Library
        │
        ▼
Animation Pipeline
```

---

# Generation Hierarchy

Everything is generated in a predictable order.

Universe

↓

Characters

↓

Environment

↓

Assets

↓

Scene

↓

Shot

↓

Image

↓

Animation

This minimizes inconsistencies.

---

# Supported Generation Types

## Character Portraits

Front

Side

Back

Three-quarter

Close-up

Expression Sheets

Turnarounds

---

## Character Poses

Standing

Walking

Running

Jumping

Sitting

Reading

Pointing

Hugging

Clapping

Sleeping

Dancing

Hundreds of reusable poses should be generated once and reused.

---

## Environment Images

Exterior

Interior

Morning

Afternoon

Evening

Night

Rain

Snow

Fog

Sunset

Holiday Decorations

Each location should support multiple variations.

---

## Asset Images

Every object should have:

Clean View

Perspective View

Interaction View

Lighting Variations

Color Variations

Reference Sheet

---

## Storyboard Frames

Each storyboard shot receives:

One planning frame

One composition frame

One lighting frame

One keyframe

These become references for animation.

---

# Primary AI Models

## FLUX

Primary production model.

Use for:

Characters

Props

Environments

Illustrations

Reference sheets

Highest consistency.

---

## SDXL

Secondary production model.

Use for:

Backgrounds

Environment variations

Experimental concepts

Quick iterations

Large batch generation

---

## Pony Diffusion

Specialized stylized model.

Recommended for:

Cute expressions

Chibi concepts

Playful poses

Character experimentation

Facial emotion exploration

Not recommended as the primary production renderer.

---

# Model Responsibilities

| Model          | Primary Purpose                          |
| -------------- | ---------------------------------------- |
| FLUX           | Final production-quality images          |
| SDXL           | Batch generation, concepts, environments |
| Pony Diffusion | Stylized expression and pose exploration |

Every model has a clearly defined responsibility.

---

# Prompt Builder

Never write prompts manually during production.

Instead

Prompt Template

*

Character Profile

*

Environment Profile

*

Asset Profile

*

Camera Profile

*

Lighting Profile

↓

Final Prompt

---

# Prompt Architecture

```text
Subject

+

Character

+

Action

+

Environment

+

Camera

+

Lighting

+

Mood

+

Style

+

Rendering

+

Quality Modifiers
```

This allows prompt components to evolve independently.

---

# Reference Image System

Every generation should use references whenever possible.

Character Reference

Environment Reference

Asset Reference

Pose Reference

Expression Reference

Color Palette

Style Sheet

Reference-first generation dramatically improves consistency.

---

# Character Locking

Every recurring character should use:

Reference images

Identity LoRA (when available)

Face consistency methods

Character embeddings

Approved color palette

Approved costume set

Never regenerate a character from scratch.

---

# Environment Locking

Every location receives:

Master image

Layout map

Lighting presets

Weather presets

Color palette

Camera reference images

Object placement rules

---

# Style Locking

Every image must follow the Studio Style Guide.

Characteristics:

Soft lighting

Rounded geometry

Friendly proportions

Bright pastel colors

Minimal visual noise

Large readable shapes

Clean backgrounds

Avoid visual clutter.

---

# Camera System

Every generated image specifies:

Camera Height

Lens

Distance

Angle

Framing

Depth of Field

Movement Reference

Reuse the camera standards from Phase 4.

---

# Lighting System

Lighting presets include:

Morning

Sunny

Cloudy

Golden Hour

Indoor Day

Indoor Night

Moonlight

Rain

Snow

Holiday Lights

Lighting should remain consistent within scenes.

---

# Color Management

Use a controlled palette.

Primary colors

Pastels

Warm neutrals

Natural greens

Soft blues

Avoid oversaturated or inconsistent color shifts.

---

# Batch Generation

Generate in batches.

Example

100 expressions

↓

Automatic ranking

↓

Best 20 approved

↓

Added to library

↓

Remaining discarded

Automation saves significant production time.

---

# Image Validation Engine

Automatically verify:

Correct character

Correct clothing

Correct colors

Correct environment

Correct proportions

Correct lighting

No missing limbs

No extra fingers

No artifacts

No text

No watermarks

Only approved images proceed.

---

# Upscaling Pipeline

Master images should support:

Native generation

↓

Upscale

↓

Artifact cleanup

↓

Sharpening

↓

Final archive

Preserve originals for future reprocessing.

---

# Image Metadata

Every image stores:

Image ID

Episode

Scene

Shot

Character IDs

Environment ID

Asset IDs

Prompt Version

Negative Prompt Version

Model

Seed

Sampler

Steps

CFG

Resolution

Aspect Ratio

Generation Date

Revision

Approval Status

---

# Prompt Versioning

Every prompt is version controlled.

Example

PROMPT_CHAR_V1

PROMPT_CHAR_V2

PROMPT_ENV_V5

PROMPT_SCENE_V9

Never overwrite historical prompts.

---

# Folder Structure

```text
ImageGeneration/

Characters/

Expressions/

Poses/

Environments/

Assets/

Scenes/

Storyboards/

References/

PromptTemplates/

NegativePrompts/

LoRAs/

Embeddings/

Outputs/

Approved/

Rejected/

Metadata/
```

---

# Rendering Standards

Working Resolution

1024×1024

1536×1536

2048×2048

Master Archive

4K+

Thumbnail Variants

1280×720

1920×1080

Portrait Variants

1080×1920

Keep master images at the highest practical quality.

---

# Thumbnail Generator

Automatically generate:

YouTube Thumbnail

YouTube Shorts

TikTok

Instagram

Facebook

Website Banner

Every platform receives optimized compositions.

---

# Dataset Growth Strategy

Every approved image becomes training data.

Example

Approved Characters

↓

Reference Library

↓

Future LoRA Updates

↓

Higher Consistency

↓

Lower Production Cost

Your dataset becomes one of the studio's most valuable assets.

---

# Automation Interfaces

Suggested APIs

```text
POST /generate/image

POST /generate/character

POST /generate/environment

POST /generate/assets

POST /generate/storyboard

POST /validate/image

POST /approve/image

POST /upscale/image
```

---

# Quality Checklist

Every generated image should satisfy:

□ Correct character identity

□ Approved costume

□ Correct proportions

□ Approved color palette

□ Correct environment

□ Correct lighting

□ Proper camera framing

□ No visual artifacts

□ No unwanted text or logos

□ Child-friendly appearance

□ Matches studio style

□ Metadata complete

□ Version tracked

□ Approved for animation

---

# Deliverables

At the completion of Phase 8, the studio should contain:

* AI image generation framework
* Prompt composition engine
* Character consistency system
* Environment consistency system
* Style guide enforcement
* Reference image management
* Prompt and model versioning
* Image validation pipeline
* Metadata schema
* Upscaling workflow
* Thumbnail generation system
* Approved production image library

---

# Long-Term Vision

Phase 8 transforms the studio into a **visual content factory**.

Rather than treating AI image generation as isolated prompts, the system becomes a structured production pipeline that creates reusable, versioned, and validated artwork. Every approved image enriches the studio's reference library, improves future generations, and reduces production costs over time.

By separating prompt construction, reference management, generation, validation, and archival, the studio becomes largely independent of any single AI model. Whether future production uses FLUX, SDXL, Pony Diffusion, or newer models, the surrounding pipeline remains stable, ensuring a consistent visual identity across thousands of episodes and many years of content production.
