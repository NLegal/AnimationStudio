# Roadmap: AI Nursery Rhyme Studio

## Overview

An AI-powered animation production pipeline that generates unlimited, high-quality Cocomelon-style nursery rhyme videos with consistent characters, reusable assets, and automated workflows. The roadmap builds the studio from the ground up: first the character system infrastructure (the factory), then character asset production, world assets, content generation and visual production, followed by pipeline infrastructure and operations at scale with batch production, multi-language, and multi-platform publishing.

## Phases

- [ ] **Phase 1: Character System Infrastructure & Bible Foundation** - The factory that creates characters: database, schema, prompt engine, provider abstraction, job system, asset versioning, CLI, API, documentation templates (5 plans)
- [ ] **Phase 1b: Character Asset Production** - First production run using the factory: Lily Bunny reference sheets, expressions, poses, outfits (provider-agnostic cloud image generation)
- [ ] **Phase 1c: Character Training System** - LoRA training infrastructure and first training runs for all characters
- [ ] **Phase 2: World Building & Environment Bible** - Reusable world locations, environments, lighting variants, weather, maps, and location library
- [ ] **Phase 3: Story & Music Pipeline** - LLM-powered story and lyric generation, AI music production with beat-timed scene planning
- [ ] **Phase 4: Visual Generation Pipeline** - Character-consistent image generation followed by image-to-video animation with quality gates
- [ ] **Phase 5: Audio-Visual Assembly & Export** - Lip-sync, TTS voices, karaoke subtitles, video editing/assembly, and thumbnail generation
- [ ] **Phase 6: Operations & Publishing** - Batch production, multi-language pipeline, cost tracking, and multi-platform publishing

## Phase Details

### Phase 1: Character System Infrastructure & Bible Foundation

**Goal**: Build the factory that creates characters — character database, API, prompt engine, provider-agnostic generation abstraction, job system, asset versioning, CLI tools, and complete documentation templates. No character images generated in this phase; the infrastructure is designed to produce unlimited characters starting in Phase 1b.
**Depends on**: Nothing (first phase)
**Requirements**: CHAR-01, CHAR-06, CHAR-08, CHAR-09
**Success Criteria** (what must be TRUE):

  1. Character database (SQLite) with structured schema for identity, appearance, personality, clothing, expressions, poses, relationships, voice, and animation rules
  2. Provider-agnostic image generation abstraction layer with 5 adapters (Flux, SDXL, Pony, CloudAPI, ComfyUI), adapter architecture, and graceful no-GPU degradation
  3. Generation jobs system with JobQueue, orchestrator, and typed output contracts for reference sheets, expressions, poses, outfits, accessories, and LoRA datasets
  4. Asset versioning with non-destructive iteration, identity tracking, rollback support, and lifecycle state machine (draft → generated → scored → shortlisted → approved → production → archived)
  5. Prompt engine with reusable templates, negative prompt standards, and age variant support
  6. Identity scoring engine with 7-layer plugin architecture (DINOv2, CLIP, Color, Part, Pose, Expression, Style) and Brand Score weighted composite
  7. CLI tools for character creation (`nursery character create`, `nursery character generate`)
  8. REST API for character management, asset generation, and asset retrieval
  9. Character Bible template, style guide, color palette documentation, and asset naming convention

**Plans**: 5/5 plans executed

Plans:

- [x] 01-01-PLAN.md — Foundation & Tracer: project setup, data models, asset repository (SQLite), generation engine ABC, identity scoring, prompt builder, end-to-end tracer, test infrastructure
- [x] 01-02-PLAN.md — Identity Engine: 7 scoring plugins (DINOv2 40%, CLIP 20%, Color 10%, Part 10%, Pose 5%, Expression 5%, Style 10%), Brand Score, diversity filter, tests
- [x] 01-03-PLAN.md — Generation Engine & Pipeline: 5 concrete backends (Flux, SDXL, Pony, CloudAPI, ComfyUI), JobQueue, GenerationJob orchestrator, tests
- [x] 01-04-PLAN.md — Prompt Builder Expansion, Training Engine (Kohya SS adapter), Human Review UI (FastAPI + Jinja2), tests
- [x] 01-05-PLAN.md — Lily Bunny Character Creation: complete bio.md, prompt templates, style guide, brand color palette, negative prompt standards, Universe Library structure

### Phase 1b: Character Asset Production

**Goal**: Activate the character factory to produce Lily Bunny's complete asset library — reference sheets, expressions, poses, outfits. Provider-agnostic: runs on whatever image generation provider is configured (fal.ai, Replicate, BFL API, local SDXL).
**Depends on**: Phase 1
**Requirements**: CHAR-02, CHAR-03, CHAR-04, CHAR-05
**Success Criteria** (what must be TRUE):

  1. Lily Bunny multi-angle reference sheets (front, 3/4, profile, back) are generated and stored in the Universe Library
  2. Lily Bunny expression library (24+ expressions) exists with generated images per the merged PHASE1.md + code expression list
  3. Lily Bunny pose library (20+ poses) exists with generated images per the merged PHASE1.md + code pose list
  4. Lily Bunny outfit/wardrobe variants (12+ outfits) exist with generated images
  5. All produced assets pass identity scoring (DINOv2 consistency >= 90%) and human review before entering the permanent library

**Plans**: 5 plans

Plans:

- [ ] 01b-01-PLAN.md — Pipeline Enhancements Tracer: update expression/pose lists, add lineage to AssetModel, fix ColorVerificationPlugin palette loading
- [ ] 01b-02-PLAN.md — Review UI Wiring + Configurable Grids: wire action handlers, add 3x3/4x4 batch grids
- [ ] 01b-03-PLAN.md — ComfyUI Workflow Templates: Flux API-format workflow JSONs, type-specific template loading
- [ ] 01b-04-PLAN.md — Production Run: Identity Lock + Face Lock (reference sheets + expressions)
- [ ] 01b-05-PLAN.md — Production Run: Body Lock + Wardrobe Expansion (poses + outfits)

### Phase 1c: Character Training System

**Goal**: LoRA training infrastructure, dataset building pipeline, and production LoRA training for all characters. Requires GPU access (local CUDA or cloud training provider).
**Depends on**: Phase 1
**Requirements**: CHAR-07
**Success Criteria** (what must be TRUE):

  1. LoRA dataset builder pipeline extracts curated images from approved character assets
  2. Production LoRA v1.0 is trained for Lily Bunny (20-40 curated reference images)
  3. LoRA versioning system matches software release conventions (v0.1 → v1.0 → v2.0)
  4. LoRA quality benchmark compares generated images against identity scorer baseline

**Plans**: TBD

### Phase 2: World Building & Environment Bible

**Goal**: Reusable world with named locations, environments with seasonal/time-of-day/weather variants, props library, vehicle library, and camera reference library.
**Depends on**: Phase 1
**Requirements**: ASST-01, ASST-02, ASST-03, ASST-04
**Success Criteria** (what must be TRUE):

  1. A named world map with 8+ zones (Residential, Downtown, Education, Recreation, Nature, Farm, Beach, Fantasy) exists with named locations
  2. 30-50 permanent environments with exterior/interior, seasonal variants (4 seasons), time-of-day variants (morning, noon, golden hour, night), and weather variants (sunny, cloudy, rain, snow)
  3. Modular prop library (indoor, outdoor, transportation, holiday), vehicle library, and camera-angle reference library are stored in the asset catalog
  4. Environment prompt templates and negative prompt standards are documented and reusable

**Plans**: TBD

### Phase 3: Story & Music Pipeline

**Goal**: Stories, lyrics, and music are generated from a theme/idea input, producing a timed scene plan that becomes the structural blueprint for all downstream visual production.
**Depends on**: Phase 1
**Requirements**: STORY-01, STORY-02, STORY-03, STORY-04, MUSC-01, MUSC-02, MUSC-03, MUSC-04
**Success Criteria** (what must be TRUE):

  1. A complete story with scene structure, educational goals, and character mapping is generated from a theme/idea input via LLM
  2. Singable lyrics with verse/chorus structure, meter, and rhyme scheme are generated from the story
  3. A scene breakdown with timing (scene count, duration per scene) is produced from the lyrics
  4. Storyboard descriptions (shot list, camera directions, continuity notes) are generated from the scene breakdown
  5. Music (instrumental + vocal track) is generated from lyrics via ACE-Step pipeline, with Suno API as a quality fallback, including beat-timed scene planning from the generated song duration

**Plans**: TBD

### Phase 4: Visual Generation Pipeline

**Goal**: Character-consistent keyframe images and animated video clips are generated from storyboard scenes with quality gates preventing expensive compute waste.
**Depends on**: Phase 2, Phase 3
**Requirements**: IMG-01, IMG-02, IMG-03, IMG-04, ANIM-01, ANIM-02, ANIM-03, ANIM-04
**Success Criteria** (what must be TRUE):

  1. Character-consistent keyframe images are generated from scene descriptions using the character prompt system (Flux + PuLID + Face LoRA + ControlNet) with >90% face consistency
  2. Generated keyframes pass automatic quality checks (face similarity score, CLIP score) before proceeding — low-scoring images are flagged for review or regeneration
  3. Video clips (5-10 seconds each) are generated from keyframe images using Wan 2.2 as the primary model, with LTX 2.3 as a speed-optimized fallback
  4. Final video clips are upscaled (to 4K) and frame-interpolated (to 60fps) for smooth, high-quality output

**Plans**: TBD

### Phase 5: Audio-Visual Assembly & Export

**Goal**: A complete, polished video exists with lip-synced singing characters, distinct TTS voices, karaoke subtitles, and platform-optimized exports with thumbnails.
**Depends on**: Phase 3, Phase 4
**Requirements**: VOIC-01, VOIC-02, VOIC-03, LIPS-01, LIPS-02, LIPS-03, LIPS-04, SUBS-01, SUBS-02, SUBS-03, EDIT-01, EDIT-02, EDIT-03, EDIT-04, THMB-01, THMB-02, THMB-03
**Success Criteria** (what must be TRUE):

  1. Characters have distinct TTS voices (Kokoro) with multi-voice support (narrator, main characters, supporting) and warm/expressive children's content voice profiles
  2. Lip-sync animation aligns mouth shapes to sung vocals at word-level accuracy using LatentSync (MuseTalk as fallback), working correctly for sustained sung notes
  3. Subtitles with karaoke-style word highlighting (ASS format with karaoke fill tags) and child-friendly typography (large fonts, high contrast) are generated from lyrics
  4. The video timeline is assembled in DaVinci Resolve with music track aligned to video cuts, transitions applied, and exports in 16:9, 9:16, and 1:1 aspect ratios
  5. Thumbnails are auto-generated from video content with multiple CTR-scored variants in a child-safe, character-consistent style

**Plans**: TBD

### Phase 6: Operations & Publishing

**Goal**: The pipeline scales to batch production, multi-language localization, and automated publishing — turning the single-video pipeline into a production studio.
**Depends on**: Phase 5
**Requirements**: MLNG-01, MLNG-02, MLNG-03, BAT-01, BAT-02, BAT-03, BAT-04, BAT-05, PUB-01, PUB-02, PUB-03, PUB-04
**Success Criteria** (what must be TRUE):

  1. Batch production runs from a CSV/spreadsheet input, processing multiple episodes sequentially with resume support for interrupted runs
  2. Per-episode quality check gates (automated scoring) block failed episodes from proceeding, with cost tracking and asset version audit trails available per batch run
  3. Multi-language versions are produced by swapping audio + subtitle tracks (video is reused without regeneration), with localized TTS and karaoke subs per target language
  4. Multi-language episodes publish with platform-native language support to the correct regional YouTube/TikTok destinations
  5. Videos publish to YouTube (video + shorts), TikTok, and Instagram with platform-optimized formatting, auto-generated metadata (title, description, tags, chapters)

**Plans**: TBD

## Progress

**Execution Order:** Phases execute in numeric order: 1 → 1b → 1c → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Character System Infrastructure & Bible Foundation | 5/5 | Complete | 2026-07-28 |
| 1b. Character Asset Production | 0/5 | Planning | - |
| 1c. Character Training System | 0/0 | Not started | - |
| 2. World Building & Environment Bible | 0/0 | Not started | - |
| 3. Story & Music Pipeline | 0/0 | Not started | - |
| 4. Visual Generation Pipeline | 0/0 | Not started | - |
| 5. Audio-Visual Assembly & Export | 0/0 | Not started | - |
| 6. Operations & Publishing | 0/0 | Not started | - |
