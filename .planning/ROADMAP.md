# Roadmap: AI Nursery Rhyme Studio

## Overview

An AI-powered animation production pipeline that generates unlimited, high-quality Cocomelon-style nursery rhyme videos with consistent characters, reusable assets, and automated workflows. The roadmap builds the studio from the ground up: first the pipeline architecture foundation, then the persistent character and asset system (the core differentiator), followed by story/music content generation, visual production, audio-visual assembly, and finally operations at scale with batch production, multi-language, and multi-platform publishing.

## Phases

- [ ] **Phase 1: Pipeline Infrastructure & Architecture Foundation** - Staged DAG pipeline with typed contracts, asset versioning, model routing, and checkpointing
- [ ] **Phase 2: Character & Asset System** - Persistent character database with LoRA training, reference sheets, expression/pose/outfit libraries, and reusable world assets
- [ ] **Phase 3: Story & Music Pipeline** - LLM-powered story and lyric generation, AI music production with beat-timed scene planning
- [ ] **Phase 4: Visual Generation Pipeline** - Character-consistent image generation followed by image-to-video animation with quality gates
- [ ] **Phase 5: Audio-Visual Assembly & Export** - Lip-sync, TTS voices, karaoke subtitles, video editing/assembly, and thumbnail generation
- [ ] **Phase 6: Operations & Publishing** - Batch production, multi-language pipeline, cost tracking, and multi-platform publishing

## Phase Details

### Phase 1: Pipeline Infrastructure & Architecture Foundation
**Goal**: A modular, staged DAG pipeline exists with typed contracts, asset versioning, model routing, and checkpoint/resume capability — the architectural backbone that every downstream stage plugs into.
**Depends on**: Nothing (first phase)
**Requirements**: INFR-01, INFR-02, INFR-03, INFR-04, INFR-05
**Success Criteria** (what must be TRUE):
  1. A pipeline stage can be defined with typed input/output contracts (Pydantic models) and registered in the orchestrator
  2. A DAG of stages executes end-to-end with data flowing correctly through typed contracts between stages
  3. If any stage fails, the pipeline resumes from the failed stage — not from the start — with full state recovery
  4. Assets can be stored with 4-property versioning (identity, non-destructive iteration, current version, rollback) and rollback works correctly
  5. The model routing layer can switch between compatible AI models with circuit breaker failover when a model call fails
**Plans**: TBD

### Phase 2: Character & Asset System
**Goal**: Characters and reusable world assets are created, stored, trained, and universally referenceable — the studio's foundational IP library that compounds in value over every episode.
**Depends on**: Phase 1
**Requirements**: CHAR-01, CHAR-02, CHAR-03, CHAR-04, CHAR-05, CHAR-06, CHAR-07, CHAR-08, CHAR-09, ASST-01, ASST-02, ASST-03, ASST-04
**Success Criteria** (what must be TRUE):
  1. Character identity records exist with structured fields (name, description, personality, relationships, catchphrases, emotion matrix, age progression variants)
  2. Multi-angle reference sheets (front, 3/4, profile, back) are generated for any character in the database
  3. Expression libraries (12+ expressions including singing mouth shapes), pose libraries, and outfit/wardrobe variants can be created and browsed per character
  4. A character LoRA can be trained (with pose/lighting diversity enforced) and applied via reusable prompt templates to generate consistent character images
  5. Background locations (5+ environments, each with multiple lighting variants) and props are stored, tagged, searched, and versioned in the asset library
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

**Execution Order:** Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Pipeline Infrastructure & Architecture Foundation | 0/0 | Not started | - |
| 2. Character & Asset System | 0/0 | Not started | - |
| 3. Story & Music Pipeline | 0/0 | Not started | - |
| 4. Visual Generation Pipeline | 0/0 | Not started | - |
| 5. Audio-Visual Assembly & Export | 0/0 | Not started | - |
| 6. Operations & Publishing | 0/0 | Not started | - |
