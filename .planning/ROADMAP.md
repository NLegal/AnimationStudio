# Roadmap: AI Nursery Rhyme Studio

## Overview

An AI-powered animation production pipeline that generates unlimited, high-quality Cocomelon-style nursery rhyme videos with consistent characters, reusable assets, and automated workflows. The roadmap builds the studio from the ground up: first the character system infrastructure (the factory), then character asset production, world assets, content generation and visual production, followed by pipeline infrastructure and operations at scale with batch production, multi-language, and multi-platform publishing.

## Phase Numbering — Reconciled (M-01, 2026-09-11)

The repository's authoritative roadmap is the **canonical 12-phase document set** at the repo root: `PHASE1.md` … `PHASE12.md`. The earlier GSD roadmap used its own numbering (1, 1b, 1c, 2–6, 7, 8) that diverged from the canonical docs — most damagingly, GSD "Phase 7 (music backend)" and "Phase 8 (music pipeline)" share numbers with canonical **Phase 7 — Production Planning & Storyboard System** and **Phase 8 — AI Image Generation**, which caused the N-14 pointer bug in the training notebook.

GSD **execution tracks** are a separate axis from canonical phase numbers. Executed tracks map into the canonical structure as follows:

| GSD execution track | Canonical phase |
|--------------------|-----------------|
| 01-character-universe | Phase 1 (Universe Creation & Character Bible) |
| 01b-character-asset-production | Phase 1 (asset production) |
| 01c-character-training-system | Phase 1 (LoRA training) |
| 07-music-generation-backend-integration | Phase 5 (Audio Bible & Music Production) |
| 08-music-generation-pipeline-wiring | Phase 5 (Audio Bible & Music Production) |

This roadmap is presented using the canonical 12-phase numbering.

## Phases

- [x] **Phase 1: Universe Creation & Character Bible** (`PHASE1.md`) — the factory that creates characters: database, schema, prompt engine, provider abstraction, job system, asset versioning, CLI, API, documentation templates (GSD tracks 01, 01b, 01c executed)
- [ ] **Phase 2: World Building & Environment Bible** (`PHASE2.md`) — reusable world locations, environments, lighting variants, weather, maps, and location library (no GSD plans yet; `scripts/generate_phase2_world.py` implemented)
- [ ] **Phase 3: Global Asset Library & Production Kit** (`PHASE3.md`) — reusable props and production kit (no GSD plans yet; `scripts/generate_phase3_assets.py` implemented)
- [ ] **Phase 4: Animation Bible & Motion System** (`PHASE4.md`) — animation rules, cycle library, expressions, gestures, camera/transitions, physics (no GSD plans yet; `src/animation_bible`/`src/animation` implemented)
- [x] **Phase 5: Audio Bible & Music Production System** (`PHASE5.md`) — songs, voices, dialogue, SFX/ambience, mixing, mastering, localization (GSD tracks 07, 08 executed)
- [ ] **Phase 6: Story Engine & Narrative Intelligence System** (`PHASE6.md`) — story/theme/plot/dialogue/song/curriculum generation (no GSD plans yet; `src/story_engine` implemented)
- [ ] **Phase 7: Production Planning & Storyboard System** (`PHASE7.md`) — episodes, scenes, shots, manifests, continuity, render queue (no GSD plans yet; `src/production` implemented)
- [ ] **Phase 8: AI Image Generation & Visual Asset Pipeline** (`PHASE8.md`) — consistency, model roles, prompt versioning, thumbnails (no GSD plans yet; `src/image_generation` implemented)
- [ ] **Phase 9: AI Animation Pipeline & Motion Generation System** (`PHASE9.md`) — character/crowd/scene motion, camera, lipsync, lighting, physics, image-to-video (`src/animation` + `src/video_generation` implemented)
- [ ] **Phase 10: Post-Production, Video Editing & Mastering System** (`PHASE10.md`) — timeline, editing, color, subtitles, QC, exports (no GSD plans yet; `src/post_production` implemented)
- [ ] **Phase 11: Publishing, Distribution & Channel Management System** (`PHASE11.md`) — metadata, compliance, scheduling, localization, analytics, channels (no GSD plans yet; `src/publishing` implemented)
- [ ] **Phase 12: Studio Automation, AI Orchestration & Autonomous Production Platform** (`PHASE12.md`) — orchestrator, workflow, agents, tasks, scheduler, quality gate, security (`src/studio` implemented)

## Phase Details

### Phase 1: Universe Creation & Character Bible (canonical `PHASE1.md`)

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

**GSD execution — track 01 (Character System Infrastructure):** 5/5 plans executed
**GSD execution — track 01b (Character Asset Production):** 5/5 plans executed
**GSD execution — track 01c (Character Training System):** 6/6 plans executed (LoRA dry-run chain verified offline; production LoRA v1.0 training is the deferred operator GPU/Colab run, CHAR-07 criterion 2)

Plans (track 01):

- [x] 01-01-PLAN.md — Foundation & Tracer: project setup, data models, asset repository (SQLite), generation engine ABC, identity scoring, prompt builder, end-to-end tracer, test infrastructure
- [x] 01-02-PLAN.md — Identity Engine: 7 scoring plugins (DINOv2 40%, CLIP 20%, Color 10%, Part 10%, Pose 5%, Expression 5%, Style 10%), Brand Score, diversity filter, tests
- [x] 01-03-PLAN.md — Generation Engine & Pipeline: 5 concrete backends (Flux, SDXL, Pony, CloudAPI, ComfyUI), JobQueue, GenerationJob orchestrator, tests
- [x] 01-04-PLAN.md — Prompt Builder Expansion, Training Engine (Kohya SS adapter), Human Review UI (FastAPI + Jinja2), tests
- [x] 01-05-PLAN.md — Lily Bunny Character Creation: complete bio.md, prompt templates, style guide, brand color palette, negative prompt standards, Universe Library structure

Plans (track 01b, Wave 1):

- [x] 01b-01-PLAN.md — Pipeline Enhancements Tracer: update expression/pose lists, add lineage to AssetModel, fix ColorVerificationPlugin palette loading
- [x] 01b-02-PLAN.md — Review UI Wiring + Configurable Grids: wire action handlers, add 3x3/4x4 batch grids
- [x] 01b-03-PLAN.md — ComfyUI Workflow Templates: Flux API-format workflow JSONs, type-specific template loading

Plans (track 01b, Wave 2 — blocked on Wave 1 completion):

- [x] 01b-04-PLAN.md — Production Run: Identity Lock + Face Lock (reference sheets + expressions)

Plans (track 01b, Wave 3 — blocked on Wave 2 completion):

- [x] 01b-05-PLAN.md — Production Run: Body Lock + Wardrobe Expansion (poses + outfits)

Plans (track 01c):

- [x] 01c-01-PLAN.md — Dataset curation & builder completion (.txt sidecars, schema-valid TOML, 20–40 bounds, find_curated two-state query)
- [x] 01c-02-PLAN.md — Benchmark ↔ identity-engine bridge (D-06 plugin weights, threshold 0.90, coverage-honest gate, IdentityScorerProvider)
- [x] 01c-03-PLAN.md — KohyaAdapter Flux contract + first-class dry-run mode
- [x] 01c-04-PLAN.md — Version persistence (sidecar JSON store) + promote()
- [x] 01c-05-PLAN.md — scripts/train_lora.py offline orchestrator (--dry-run enforced, curate/build/train/benchmark/versions)
- [x] 01c-06-PLAN.md — Colab training notebook (Phase 4 pattern) + operator docs

### Phase 2: World Building & Environment Bible (canonical `PHASE2.md`)

**Goal**: Reusable world with named locations, environments with seasonal/time-of-day/weather variants, props library, vehicle library, and camera reference library.
**Depends on**: Phase 1
**Requirements**: ASST-01, ASST-02, ASST-03, ASST-04
**Status**: Defined (`PHASE2.md`), implemented via `scripts/generate_phase2_world.py` (mock backend; real backends swap in via `--backend`). No GSD plans authored yet — see TODOPROJECT backlog.
**Plans**: TBD

### Phase 3: Global Asset Library & Production Kit (canonical `PHASE3.md`)

**Goal**: Reusable prop libraries, reference sheets, production-kit documentation, and the global asset catalog.
**Depends on**: Phase 1, Phase 2
**Requirements**: ASST-03, ASST-04 (asset library portion)
**Status**: Defined (`PHASE3.md`), implemented via `scripts/generate_phase3_assets.py` (mock backend). No GSD plans authored yet — see TODOPROJECT backlog.
**Plans**: TBD

### Phase 4: Animation Bible & Motion System (canonical `PHASE4.md`)

**Goal**: Animation rules, cycle library, expressions/blinks/gestures, camera and transition system, physics, and prompt templates for motion.
**Depends on**: Phase 1
**Requirements**: ANIM-01–ANIM-04 (definitions), animation-bible conventions
**Status**: Defined (`PHASE4.md`), code in `src/animation_bible` with doc↔code consistency tests (`test_animation_bible.py`). No GSD plans authored yet.
**Plans**: TBD

### Phase 5: Audio Bible & Music Production System (canonical `PHASE5.md`)

**Goal**: The studio's audio identity — songs, character voices, narration, dialogue, SFX/foley, ambience, mixing, mastering, and localization. Music is generated from lyrics via ACE-Step with Suno as a quality fallback, including beat-timed scene planning.
**Depends on**: Phase 1
**Requirements**: STORY-01–STORY-04 (lyrics/story), MUSC-01–MUSC-04, VOIC-01–VOIC-03, LIPS-01–LIPS-04, SUBS-01–SUBS-03, EDIT-01–EDIT-04, THMB-01–THMB-03
**Status**: Defined (`PHASE5.md`); **GSD execution — track 07 (Music Generation Backend): 2/2 plans executed; track 08 (Music Generation Pipeline Wiring): 2/2 plans executed.** Remaining audio-bible surface (voices/lipsync/subs/assembly) tracked in TODOPROJECT.
**Plans (track 07):**

- [x] 07-01-PLAN.md — Core layer tracer: package scaffold, Pydantic models, MusicGenerationBackend protocol + typed exception taxonomy, category→params mapping (locked research table), stdlib transport seam, deterministic MockBackend, offline test suite
- [x] 07-02-PLAN.md — AceStepBackend REST adapter (fake-transport contract suite), Suno stub + experimental wrapper, get_backend registry with MUSIC_BACKEND env resolution, scripts/generate_phase7.py CLI (--dry-run zero-network), Audio/Music README + manual live-smoke checklist

**Plans (track 08, Wave 1):**

- [x] 08-01-PLAN.md — Script + manifest core: extend scripts/generate_phase5.py with `--generate` mode (backend alias normalization, 24-category batch, `<category>-<topic-slug>-<seed>` file layout, crash-safe atomic manifest with resume-skip by request signature), tests/test_generate_phase5.py (TestGenerationMode / TestBatchGeneration / TestManifest), Audio/Music/README.md live-smoke line

**Plans (track 08, Wave 2 — blocked on Wave 1 completion):**

- [x] 08-02-PLAN.md — Review UI music hooks (GET /music page + nav link, POST /music/prompt pure preview, POST /music/generate single-song BackgroundTasks jobs reusing script-tier manifest helpers, GET /api/music/jobs polling, music_backend DI kwarg) + tests/test_review_ui_music.py + colab/AnimationStudio_Colab_Phase5.ipynb + PHASE5_STATUS.md update

### Phase 6: Story Engine & Narrative Intelligence System (canonical `PHASE6.md`)

**Goal**: LLM-powered narrative intelligence — story, theme, plot, dialogue, song, and curriculum generation with validation and continuity.
**Depends on**: Phase 1
**Requirements**: STORY-01–STORY-04
**Status**: Defined (`PHASE6.md`), code in `src/story_engine`. No GSD plans authored yet.
**Plans**: TBD

### Phase 7: Production Planning & Storyboard System (canonical `PHASE7.md`)

**Goal**: Episodes, scenes, shots, manifests, continuity validation, the render queue, and quality checks.
**Depends on**: Phase 1, Phase 6
**Requirements**:Storyboard/planning surface of STORY-04
**Status**: Defined (`PHASE7.md`), code in `src/production` + Phase 7 Colab notebook (`colab/AnimationStudio_Colab_Phase7.ipynb`). No GSD plans authored yet.
**Plans**: TBD

### Phase 8: AI Image Generation & Visual Asset Pipeline (canonical `PHASE8.md`)

**Goal**: Character-consistent keyframe images and visual assets via ConsistencyManager, model roles, prompt versioning, thumbnails, and upscaling.
**Depends on**: Phase 1, Phase 4
**Requirements**: IMG-01–IMG-04
**Status**: Defined (`PHASE8.md`), code in `src/image_generation` + Phase 8 Colab notebook (`colab/AnimationStudio_Colab_Phase8.ipynb`). No GSD plans authored yet.
**Plans**: TBD

### Phase 9: AI Animation Pipeline & Motion Generation System (canonical `PHASE9.md`)

**Goal**: Image-to-video clips (5–10s per storyboard panel), upscaling, and frame interpolation. Wan 2.2 primary, LTX 2.3 fallback.
**Depends on**: Phase 8
**Requirements**: ANIM-01–ANIM-04
**Status**: Defined (`PHASE9.md`), code in `src/animation` + `src/video_generation` (image-to-video protocol + Wan ComfyUI + cloud adapters, 2026-09-11). No GSD plans authored yet.
**Plans**: TBD

### Phase 10: Post-Production, Video Editing & Mastering System (canonical `PHASE10.md`)

**Goal**: Automated timeline assembly, editing, transitions, color, karaoke subtitles, QC, and multi-aspect-ratio exports.
**Depends on**: Phase 9, Phase 5
**Requirements**: EDIT-01–EDIT-04, SUBS-01–SUBS-03, THMB-01–THMB-03
**Status**: Defined (`PHASE10.md`), code in `src/post_production`. No GSD plans authored yet.
**Plans**: TBD

### Phase 11: Publishing, Distribution & Channel Management System (canonical `PHASE11.md`)

**Goal**: Metadata, compliance, scheduling, localization, analytics, and multi-platform channel publishing.
**Depends on**: Phase 10
**Requirements**: MLNG-01–MLNG-03, PUB-01–PUB-04
**Status**: Defined (`PHASE11.md`), code in `src/publishing`. No GSD plans authored yet.
**Plans**: TBD

### Phase 12: Studio Automation, AI Orchestration & Autonomous Production Platform (canonical `PHASE12.md`)

**Goal**: The autonomous production platform — orchestrator, episode workflow factory, tasks, agents, scheduler, quality gates, and security.
**Depends on**: Phases 1–11
**Requirements**: INFR-01–INFR-05, BAT-01–BAT-05, QC-01–QC-03
**Status**: Defined (`PHASE12.md`), code in `src/studio` (`PipelineOrchestrator`, `EpisodeWorkflowFactory`, `TaskQueue`, `WorkerPool`, `QualityGate`). No GSD plans authored yet.
**Plans**: TBD

## Progress

**Execution Order:** Canonical phase order 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12. GSD execution tracks are mapped into the canonical structure per the table above (01/01b/01c → Phase 1; 07/08 → Phase 5).

| Phase | Status | GSD plans | Completed |
|-------|--------|-----------|-----------|
| 1. Universe Creation & Character Bible | Complete | 16/16 (01+01b+01c) | 2026-08-27 |
| 2. World Building & Environment Bible | Defined — no GSD plans | — | - |
| 3. Global Asset Library & Production Kit | Defined — no GSD plans | — | - |
| 4. Animation Bible & Motion System | Implemented — no GSD plans | — | - |
| 5. Audio Bible & Music Production System | Music tracks complete | 4/4 (07+08) | 2026-08-25 |
| 6. Story Engine & Narrative Intelligence | Implemented — no GSD plans | — | - |
| 7. Production Planning & Storyboard System | Implemented — no GSD plans | — | - |
| 8. AI Image Generation & Visual Asset Pipeline | Implemented — no GSD plans | — | - |
| 9. AI Animation Pipeline & Motion Generation | Implemented — no GSD plans | — | - |
| 10. Post-Production, Video Editing & Mastering | Implemented — no GSD plans | — | - |
| 11. Publishing, Distribution & Channel Mgmt | Implemented — no GSD plans | — | - |
| 12. Studio Automation & AI Orchestration | Implemented — no GSD plans | — | - |

> Notes: Phases 2–12 beyond the executed tracks above are implemented via the direct backlog (`TODOPROJECT.md` + `colab/` notebooks) rather than GSD plan documents; the canonical phase docs (`PHASE*.md`) are the source of truth for scope. Phase 5's non-music surface (voices/lipsync/subs/assembly/export) remains open in TODOPROJECT. GPU-compute and real-backend execution for Phases 8/9/10 are deferred-hardware items (C-01/C-03, N-15).