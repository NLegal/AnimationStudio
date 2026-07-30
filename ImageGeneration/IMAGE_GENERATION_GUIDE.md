# AI Image Generation & Visual Asset Pipeline Guide

> **Version:** 1.0
> **Phase:** 8
> **Purpose:** Production-ready image generation framework for consistent, reusable visual assets

## Overview

Phase 8 builds the AI image generation pipeline that transforms planned content (storyboards, episodes, characters) into production-ready visual assets. This is the bridge between pre-production planning and actual animation.

### Pipeline Flow

```
Episode Package → Storyboard → Shot Package → Prompt Builder
    → Reference Injection → Image Generation → Quality Validation
    → Image Library → Animation Pipeline
```

### Generation Hierarchy

Images are always generated in a predictable order to minimize inconsistencies:

1. **Universe** — global style and color consistency
2. **Characters** — identity-locked character renders
3. **Environment** — location backgrounds with lighting
4. **Assets** — props and objects
5. **Scene** — character + environment + assets combined
6. **Shot** — camera-specific framing
7. **Image** — final rendered frame
8. **Animation** — sequence of frames

## Directory Structure

```
ImageGeneration/
├── Characters/             — Per-character image library
│   ├── LilyBunny/
│   ├── BenBear/
│   ├── CharlieFox/
│   ├── DaisyDuck/
│   └── .gitkeep
├── Expressions/            — Expression sheets per character
├── Poses/                  — Pose library (reusable across episodes)
├── Environments/           — Location renders with lighting/weather variations
├── Assets/                 — Prop and object renders
├── Scenes/                 — Combined character + environment compositions
├── Storyboards/            — Storyboard frame renders
├── References/             — Reference images for consistency
│   ├── Characters/
│   ├── Environments/
│   ├── Assets/
│   ├── Poses/
│   ├── Expressions/
│   ├── ColorPalettes/
│   └── StyleSheets/
├── PromptTemplates/        — Reusable prompt templates by category
├── NegativePrompts/        — Standardized negative prompt components
├── LoRAs/                  — Trained LoRA weights
├── Embeddings/             — Textual inversion embeddings
├── Outputs/                — Generated output images
│   ├── Approved/           — QC-passed, production-ready images
│   └── Rejected/           — Failed QC, kept for reference
└── Metadata/               — Per-image metadata records (JSON/YAML)
```

## Prompt Architecture

Every generation prompt is composed from these components:

```
Subject + Character + Action + Environment + Camera + Lighting
    + Mood + Style + Rendering + Quality Modifiers
```

### Prompt Templates

Reusable templates exist for each generation type:
- `PROMPT_CHAR_V1` — Character portrait/reference
- `PROMPT_ENV_V5` — Environment render
- `PROMPT_ASSET_V2` — Asset/Prop render
- `PROMPT_SCENE_V9` — Full scene composition

### Prompt Versioning

Every prompt is version-controlled. IDs follow the convention:
`PROMPT_{CATEGORY}_V{NUMBER}` where CATEGORY is the first 5 characters
of the uppercase category name.

Example: `PROMPT_CHARA_V1`, `PROMPT_ENVIR_V5`, `PROMPT_ASSET_V3`

Historical prompts are never overwritten — each revision increments.

## Image Validation

Every generated image must pass these checks before entering the Approved library:

| Check | Description |
|-------|-------------|
| Format | Must be RGB or RGBA (no grayscale, indexed, CMYK) |
| Dimensions | Width/height between 64px and 8192px |
| Aspect ratio | Max dimension ratio ≤ 4:1 |
| Resolution standard | ≥ 1024px on shortest side |
| Metadata complete | All required fields populated |
| Correct character | Identity matches requested character |
| Approved colors | Within brand color palette |
| No artifacts | Free from deformities, extra limbs, etc. |

## Code Implementation

The image generation framework lives in `src/image_generation/`:

| Module | Purpose |
|--------|---------|
| `metadata.py` | ImageMetadata dataclass with 20+ fields |
| `validator.py` | ImageValidator for format, dimensions, metadata checks |
| `upscaler.py` | UpscalingPipeline with multiple resampling methods |
| `thumbnail.py` | ThumbnailGenerator for 9+ platform presets |
| `reference_manager.py` | ReferenceImageManager for character/environment/asset refs |
| `prompt_versioning.py` | PromptVersionManager for prompt version control |

## Backend Integration

The existing `src/generation_engine/` provides the actual model backends:

| Backend | Purpose | Status |
|---------|---------|--------|
| `FluxBackend` | Production quality — FLUX.1-dev | Framework ready (GPU required) |
| `SDXLBackend` | Batch/bulk — SDXL | Framework ready (GPU required) |
| `PonyBackend` | Stylized/expressions — Pony Diffusion | Framework ready (GPU required) |
| `ComfyUIBackend` | R&D/experimental — ComfyUI API | Framework ready (ComfyUI server required) |
| `CloudAPIBackend` | Cloud generation — fal.ai/Replicate/BFL | Framework ready (API key required) |

## Quality Checklist

Every image in the production library should satisfy:

- [ ] Correct character identity
- [ ] Approved costume
- [ ] Correct proportions
- [ ] Approved color palette
- [ ] Correct environment
- [ ] Correct lighting
- [ ] Proper camera framing
- [ ] No visual artifacts
- [ ] No unwanted text or logos
- [ ] Child-friendly appearance
- [ ] Matches studio style
- [ ] Metadata complete
- [ ] Version tracked
- [ ] Approved for animation

## Automation Interfaces

The pipeline exposes these automation endpoints:

| Endpoint | Purpose |
|----------|---------|
| `POST /generate/image` | Generate images from prompt package |
| `POST /generate/character` | Generate character-specific images |
| `POST /generate/environment` | Generate environment renders |
| `POST /generate/assets` | Generate asset/prop images |
| `POST /generate/storyboard` | Generate storyboard frames |
| `POST /validate/image` | Run validation checks on an image |
| `POST /approve/image` | Approve image for production use |
| `POST /upscale/image` | Upscale image to target resolution |

## Dataset Growth Strategy

Every approved image becomes training data for future model improvements:

```
Approved Characters → Reference Library → Future LoRA Updates
    → Higher Consistency → Lower Production Cost
```

The dataset is one of the studio's most valuable assets. Each generated image is versioned, cataloged with full metadata, and preserved for reprocessing with future model improvements.
