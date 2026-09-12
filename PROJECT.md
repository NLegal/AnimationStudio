# PROJECT.md — AI Nursery Rhyme Studio
# Last Updated: 2026-09-12 (full-module deep audit)

---

## Overview

An AI-powered animation production pipeline for generating Cocomelon-style
nursery rhyme videos with consistent characters, reusable assets, and
automated workflows. Built as a modular 12-phase system where each phase
is an independent department.

**Core Value:** Character consistency and asset reusability across every
episode. Build once, reuse forever.

---

## Architecture

```
Story Engine → Production Planning → Image Generation → Animation
       ↓              ↓                     ↓              ↓
  Curriculum    Episodes/Shots/       Consistency &     Character/Crowd/
  Validation    Manifests/QC         Model Roles        Scene Motion
       ↓              ↓                     ↓              ↓
       └──────── Post-Production: Edit → Color → Subtitles → QC → Export ────────┐
                                                                                  ↓
                    Publishing: Metadata → Compliance → Schedule → Localize → Publish
                                                                                  ↓
                Studio Orchestration: Workflow → Tasks → Agents → Quality → Dashboard
```

---

## Module Inventory

| Module | Package | LOC | Files | Purpose |
|--------|---------|-----|-------|---------|
| Data Models | `src/models/` | 72 | 2 | CharacterModel, AssetModel, GenerationJobRequest, ScoringResult |
| Identity Engine | `src/identity_engine/` | 870 | 11 | 7 scoring plugins + BrandScore + DiversityFilter |
| Asset Repository | `src/asset_repository/` | 647 | 5 | SQLite CRUD + migrations + asset paths |
| Generation Engine | `src/generation_engine/` | 1,063 | 8 | 5 backends: Flux, SDXL, Pony, Cloud, ComfyUI |
| Prompt Builder | `src/prompt_builder/` | 783 | 4 | Template system + age/rotation/lighting variants |
| Training Engine | `src/training_engine/` | 1,705 | 8 | Kohya SS LoRA adapter + dataset builder + benchmark + versioning |
| Story Engine | `src/story_engine/` | 4,614 | 22 | Curriculum, themes, dialogue, song, narrative, validation |
| Production | `src/production/` | 1,191 | 10 | Episodes, scenes, shots, manifests, continuity, API |
| Image Generation | `src/image_generation/` | 706 | 9 | ConsistencyManager, model roles, thumbnails, validation |
| Animation | `src/animation/` | 1,727 | 18 | Character/crowd/scene, camera, lipsync, physics, render |
| Post-Production | `src/post_production/` | 1,390 | 17 | Timeline, editing, color, subtitles, QC, exports |
| Publishing | `src/publishing/` | 1,550 | 14 | Metadata, compliance, scheduling, localization, analytics |
| Studio | `src/studio/` | 1,796 | 20 | Orchestrator, workflow, agents, tasks, security, dashboard |
| Universe | `src/universe/` | 1,410 | 5 | Catalog parsing, seeding, batch generation |
| Review UI | `src/review_ui/` | 1,546 | 4 | FastAPI + Jinja2 web UI |
| Pipeline | `src/pipeline/` | 591 | 4 | JobQueue, GenerationJob, DiversityFilter |
| Video Generation | `src/video_generation/` | 913 | 7 | Mock / Wan ComfyUI / Cloud (fal, Replicate, Hunyuan) i2v backends |
| Animation Bible | `src/animation_bible/` | 1,954 | 6 | Motion system + cycle libraries + prompt templates |
| Audio Bible | `src/audio_bible/` | 1,312 | 6 | Music/voice standards + production system |
| Music Generation | `src/music_generation/` | 1,075 | 6 | ACE-Step + Suno adapters + mock backend |
| **TOTAL** | | **~25,400** | **178** | |

---

## Key Numbers

| Metric | Count |
|--------|-------|
| Characters defined | 39 |
| World zones | 10 |
| World locations | 138 |
| Reusable props | 1,559 (20 categories) |
| Approved assets (mock) | 0 (DB holds 2,508 scored/shortlisted rows; "18,071" doc claim overstated) |
| Animation motion types | 21 |
| Facial expressions | 13 |
| Gestures | 23 |
| Song categories | 24 |
| Voice profiles | 11 |
| SFX cataloged | 110 |
| Learning objectives | 72 |
| Curriculum areas | 25 |
| Export presets | 8 platforms |
| Target languages | 6 (en/es/fr/de/zh/ja) |
| Source LOC | ~25,400 |
| Test LOC | ~17,700 |
| Test functions | ~1,695 |
| Scripts | 19 Python + 3 setup |
| Colab notebooks | 13 |

---

## Phase Status

| Phase | Name | Code | Tests | Real Output |
|-------|------|------|-------|-------------|
| 1 | Universe Creation & Character Bible | Complete | 394+ | Mock only |
| 1b | Character Asset Production | Complete | 50+ | Mock only |
| 1c | Character Training System | Complete (dry-run) | 77+ | No LoRA trained |
| 2 | World Building & Environment Bible | Complete | 17+ | Mock only |
| 3 | Global Asset Library & Production Kit | Complete | 23+ | Mock only |
| 4 | Animation Bible & Motion System | Complete | 48+ | N/A (standards only) |
| 5 | Audio Bible & Music Production | Complete | 40+ | No audio generated |
| 6 | Story Engine & Narrative Intelligence | Complete | 80+ | Validated (no media) |
| 7 | Production Planning & Storyboard | Complete | 64+ | Validated (no media) |
| 8 | AI Image Generation Pipeline | Complete | 82+ | Mock only |
| 9 | AI Animation Pipeline | Complete | 151+ | Framework only |
| 10 | Post-Production & Mastering | Complete | 168+ | Framework only |
| 11 | Publishing & Distribution | Complete | 211+ | Framework only |
| 12 | Studio Automation & Orchestration | Complete | 222+ | Framework only |

---

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `FAL_API_KEY` | No | fal.ai cloud image generation |
| `REPLICATE_API_KEY` | No | Replicate cloud image generation |
| `BFL_API_KEY` | No | BFL cloud image generation |
| `CUDA_VISIBLE_DEVICES` | No | GPU selection (default: 0) |
| `ACESTEP_API_KEY` | No | ACE-Step music generation |

---

## Key Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| D-01 | 39 characters (not 10-20) | Exceeded target for richer world |
| D-06 | 7-layer identity scoring | Multi-dimensional consistency |
| D-18 | Lineage as JSON in SQLite | Non-destructive iteration tracking |
| D-18 | SQLite for metadata, filesystem for binaries | Simple, portable, migration-ready |
| D-03 | Mock backend as default | Enables development without GPU |
| D-05 | Plugin-based scoring architecture | Extensible, testable |
| A3 | JSON sidecar for LoRA versions | Corruption-isolated persistence |
| — | Dry-run by default for training | Prevents accidental GPU usage |
| — | Application factory pattern (create_app) | Testable Review UI |

---

## Known Gaps (refreshed 2026-09-12 — see TODOPROJECT.md for authoritative list)

### Critical
1. Zero real media produced (catalog.db holds 2,508 asset rows, **0 approved** — no real images yet)
2. **No real-media consumer path**: post-generation modules (animation, post-production, publishing, studio) flip statuses instead of executing; only `video_generation` has real REST backends (Wan/Cloud) (TODOPROJECT A-01)
3. No LoRA trained (character consistency system is code-only)
4. No audio generated (audio_bible produces plans only; ACE-Step/Suno are the only real paths, both unproven live) (A-03)
5. No video pipeline execution (animation/post-production/publishing unvalidated)

### Major
6. "AI" story engine is template/rule-based, not LLM (A-02)
7. UI has zero authentication/authorization + open-redirect via referer (A-04)
8. 13 documentation gaps (Phases 1, 5, 6) — **all verified closed 2026-09-12** (M-03)
9. Review UI monolith (1,520-line app.py) — M-04 open
10. No integration tests against real backends — M-05 open (blocked on approved assets)
11. Security module is in-memory only (lost on restart) — M-06 open
12. ComfyUI backend failure-path NameErrors + hardcoded node IDs (A-05)
13. Dual persistence patterns (SQLite vs in-memory vs pure Python) — M-08 open

---

*See TODOPROJECT.md for complete prioritized issue list with file paths and fix recommendations. See SUMMARY.md for executive summary.*
