---
phase: 08-music-generation-pipeline-wiring
plan: 02
subsystem: review-ui
tags: [music, review-ui, colab, template, background-jobs, prompt-preview]

# Dependency graph
requires:
  - phase: 08-music-generation-pipeline-wiring
    plan: 01
    provides: "scripts/generate_phase5.py manifest helpers (load_manifest, upsert_entry, atomic_write_manifest, song_filename)"
  - phase: 07-music-generation-backend-integration
    provides: src/music_generation/ package (MusicGenerationBackend protocol, AceStepBackend, SunoBackend stub, MockBackend, get_backend registry, build_music_request, resolve_music_params, MusicBackendError taxonomy)
  - phase: 01-character-universe
    provides: src/audio_bible/bible.py AudioBible facade, build_music_prompt, category_negative
provides:
  - "Review UI music page (GET /music): 24-category params table, prompt builder, generate form, recent jobs panel"
  - "POST /music/prompt: pure bible-conformant preview with sticky form (no side effects)"
  - "POST /music/generate: single-song background job lifecycle (create → running → completed/failed)"
  - "GET /api/music/jobs: JSON status list for music generation jobs"
  - "Colab Phase 5 notebook (10 cells): settings, clone+install, 24-category preview, ACE-Step service, generate, tests, review, sync, next steps"
  - "PHASE5_STATUS.md: 4 new deliverables rows, mock reproduction line, Music Generation Wiring section"
  - "tests/test_review_ui_music.py: 25 tests (TestMusicPage 7, TestMusicPrompt 10, TestMusicGenerate 8)"
affects: [PHASE5_STATUS.md — wired generation pipeline documented, colab/AnimationStudio_Colab_Phase5.ipynb — Phase 5 notebook family member]

# Tech tracking
tech-stack:
  added: []
  patterns: [background-task job lifecycle, DI music_backend/music_dir on create_app, template preview via context dict, sticky form values, isolated venv for external service in notebook]

key-files:
  created: [src/review_ui/templates/music.html, tests/test_review_ui_music.py, colab/AnimationStudio_Colab_Phase5.ipynb]
  modified: [src/review_ui/app.py, src/review_ui/templates/base.html, PHASE5_STATUS.md]

key-decisions:
  - "Worker _run_music_job resolves backend as: if backend_name truthy -> get_backend(backend_name), elif music_backend is not None -> use injected, else -> get_backend(None) — needed so suno selection properly routes to SunoBackend"
  - "Manifest helpers imported at module level from scripts/generate_phase5.py (deliberate cross-tier import pattern, PATTERNS Divergence #2)"
  - "POST /music/prompt is pure preview: no background tasks, no DB writes, no network — just build_music_prompt + category_negative + resolve_music_params composed into a context dict"
  - "Notebook Cell 4 uses isolated uv venv for ACE-Step service (Pitfall 7) with pip fallback; never mixes ACE-Step deps into studio env"
  - "ACESTEP_MODEL setting added to notebook but not yet consumed by generate_phase5.py — reserved for future --model flag (no behavioral change)"
---

# Phase 8 Plan 02: Review UI Music Wiring Summary

Wire Phase 7 music-generation backends into Review UI (`GET /music`, `POST /music/prompt`, `POST /music/generate`, `GET /api/music/jobs`), Colab notebook, and PHASE5_STATUS docs. Tracer-first TDD: tracer → expansion → documentation finalizer.

## Tasks

| Task | Type | Description | Commit |
|------|------|-------------|--------|
| 1a | tracer (TDD) | Music page + generate route + API polling + background worker | `42572818` |
| 2 | auto (TDD) | POST /music/prompt pure preview with sticky form | `aeec77c1` |
| 3 | auto | Colab notebook (10 cells) + PHASE5_STATUS.md wiring docs | `a66802f4` |

## Key Artifacts

### Review UI Routes
- `GET /music` — browse page with 24-category params table, prompt builder, generate form, recent jobs
- `POST /music/prompt` — pure preview: bible-conformant caption, negative prompt, resolved params. No side effects.
- `POST /music/generate` — single-song background job via `_run_music_job` worker
- `GET /api/music/jobs` — JSON status list: `[{id, status, category, error, file}]`

### Music Page Template (`music.html`)
Extends `base.html` with Music nav link (PHASE 1-5 badge). Four panels: category params table, prompt builder form (`/music/prompt`), generate form (`/music/generate`), recent jobs table.

### Background Worker (`_run_music_job`)
Creates WAV + manifest entry using shared helpers from `scripts/generate_phase5.py`. Backend resolution: `backend_name` truthy → `get_backend(backend_name)`, elif `music_backend` injected → use it, else → `get_backend(None)`. `MusicBackendError` boundary marks job as failed.

### Colab Notebook (10 cells)
| Cell | Content |
|------|---------|
| 0 | Markdown intro: CPU mock mode / GPU real songs |
| 1 | Settings: `RUN_REAL_GENERATION` boolean + `ACESTEP_MODEL` choice |
| 2 | Clone + install (Phase 4 pattern, adapted closing print) |
| 3 | Preview 24 song categories (`AudioBible().list_song_categories()`) |
| 4 | ACE-Step service: isolated uv venv, health-wait loop, pip fallback |
| 5 | Generate: `--backend ace-step` or `--backend mock` gated on `RUN_REAL_GENERATION` |
| 6 | Tests: audio_bible + music_generation + generate_phase5 + review_ui_music |
| 7 | Review: manifest.json summary + report excerpt |
| 8 | Sync: `Audio/Music/ PHASE5_REPORT.md` via PAT push or `files.download` |
| 9 | Next steps markdown |

### PHASE5_STATUS.md Changes
- 4 new deliverables rows: generation-mode script, Review UI hooks, Colab notebook, manifest inventory
- Extended Reproduction block with `--generate --backend mock` offline example
- New `## Music Generation Wiring (Phase 8)` section with tier responsibilities table
- Stale "audio rendering is left to the AI platforms" caveat rewritten

## Test Coverage

`tests/test_review_ui_music.py` — **25 tests** (all offline):

| Class | Tests | What it covers |
|-------|-------|----------------|
| TestMusicPage | 7 | GET /music renders, nav link, active state, 24 categories, params table, generate form, backend select |
| TestMusicPrompt | 10 | Golden values (66 BPM/F major/3/4/120s), caption bible-conformant, negative nonempty, request JSON, sticky form, blank topic default, purity proof, unknown category graceful |
| TestMusicGenerate | 8 | Mock redirect, job completes, WAV on disk, manifest entry, suno redirect-not-500, suno job failed, API jobs shape |

Constraint guards: C2 (no sqlite3 in music routes), C3 (fail-loud transport guards autouse), C5 (suno yields failed job not 500), C6 (env isolation autouse fixture).

## Verification

- Full suite: **1694 passed, 5 failed** (pre-existing story-engine catalog failures, unrelated)
- `python3 -c "import json;json.load(open('colab/AnimationStudio_Colab_Phase5.ipynb'))"` exits 0
- `python3 scripts/generate_phase5.py --docs-dir Audio --out /tmp/...` exits 0 (C4 report-mode compat)
- Notebook: no deprecated `pip install ace-step` v1, no `pyproject.toml` mutation
