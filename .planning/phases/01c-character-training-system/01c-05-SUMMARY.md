---
phase: 01c-character-training-system
plan: 05
subsystem: training_engine
tags: [cli, orchestration, dry-run, curation, benchmark, versions]

# Dependency graph
requires:
  - phase: 01c-01
    provides: DatasetBuilder sidecars/schema-valid TOML/bounds, find_curated, baselines copy
  - phase: 01c-02
    provides: Benchmark weight alignment, IdentityScorerProvider, threshold 0.90, weight_coverage
  - phase: 01c-03
    provides: TrainingConfig.dry_run, Flux-complete _build_command
  - phase: 01c-04
    provides: JsonVersionStore, load_registry(), idempotent registry, promote()
provides:
  - scripts/train_lora.py CLI: build-dataset / train / benchmark / versions subcommands
  - Offline-provable end-to-end deferred-human evidence chain (zero subprocess spawns)
  - Curation dedupe (one best image per variant, highest brand score) + max cap
  - Local real-training refusal policy naming the Colab notebook
affects: [01c-06]

# Tech tracking
tech-stack:
  added: []
  patterns: [argparse-subcommand-cli, script-bootstrap-sys-path, subprocess-sentinel-guarded-tests]

key-files:
  created:
    - scripts/train_lora.py
    - tests/test_train_lora_script.py
  modified:
    - src/training_engine/kohya_adapter.py

key-decisions:
  - "train registers only post-completion via the adapter — no placeholder pre-seeding"
  - "versions subcommand strictly read-only — never creates, registers, or promotes"
  - "Real training refused locally by policy — Colab notebook is the exclusive GPU path"
  - "Dry-run supersedes validate_environment (kohya_adapter) so offline proof needs no KOHYA_SS_PATH"

patterns-established:
  - "CLI orchestration: argparse subcommands + global flags before subcommand + sys.path bootstrap"
  - "Subprocess-sentinel test guard proving C-OFFLINE (zero spawns) across the whole suite"

requirements-completed: [CHAR-07]

coverage:
  - id: E1
    description: build-dataset produces bounded dataset with variant dedupe and sidecars
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: tests/test_train_lora_script.py::TestTrainLoraBuildDataset
        status: pass
    human_judgment: false
  - id: E2
    description: train --dry-run registers durable version evidence with zero subprocess spawn
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: tests/test_train_lora_script.py::TestTrainLoraTrain
        status: pass
    human_judgment: false
  - id: E3
    description: Local real training refused by policy — Colab named as exclusive GPU path
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: tests/test_train_lora_script.py::TestTrainLoraTrain::test_train_without_dry_run_exits_nonzero
        status: pass
    human_judgment: false

# Metrics
duration: 90min
completed: 2026-08-26
status: complete
---

# Phase 1c Plan 05: Training Orchestration CLI Summary

**scripts/train_lora.py — one command proving the entire offline training-evidence chain: curate → dry-run train → benchmark → versions**

## Performance

- **Duration:** ~90 min
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Created `scripts/train_lora.py` with four subcommands following `export_assets.py`/`generate_phase5.py` conventions (sys.path bootstrap, argparse, reproduction header, exit codes 0/1)
- `build-dataset`: curates approved/production assets via `find_curated`, dedupes to one best image per variant (highest brand_score, stable id tie-break), caps at max_images, builds bounded Kohya dataset with .txt sidecars and baselines/
- `train`: refuses real training locally (exits 1 naming the Colab notebook); `--dry-run` computes the next version via `recommend_next`, runs `KohyaAdapter.train`, writes the `.train_cmd.json` artifact, and persists a version record durably
- `benchmark`: requires explicit `--images` (G14), feeds `LoRABenchmark` via `IdentityScorerProvider(light=True)`, honors weight-coverage advisory, exit code reflects `result.passed`
- `versions`: strictly read-only listing of persisted records
- Curation lives in the orchestration layer (never inside DatasetBuilder) per the research anti-pattern; identifier validation guards path/argv interpolation (T-01c-05a)

## Task Commits

1. **Task 1 RED: failing offline test suite for train_lora CLI** - `18555d09` (test)
2. **Task 1/2 GREEN: train_lora CLI implementation + test fixes** - `a3e7cab1` (feat)

## Files Created/Modified
- `scripts/train_lora.py` - CLI orchestrator (new)
- `tests/test_train_lora_script.py` - 8 offline integration tests, subprocess-sentinel guarded (new)
- `src/training_engine/kohya_adapter.py` - dry-run supersedes validate_environment so offline proof needs no KOHYA_SS_PATH

## Deviations from Plan
- Plan referenced a `build_entries_from_assets` helper that does not exist; constructed `DatasetEntry` objects directly from curated asset dicts instead
- Fixed test CLI ergonomics to the standard argparse layout (global flags before the subcommand)
- Added a character-existence check to `train` so unknown characters fail loudly rather than fabricating a version record

## Issues Encountered
- `find_curated` is async — wrapped in `asyncio.run` at the CLI boundary
- KohyaAdapter checked `validate_environment` before the dry-run branch, blocking offline dry-run proof; moved env check to real-path-only

## User Setup Required
None - fully offline-proof.

## Next Phase Readiness
- Complete offline evidence chain proven with zero subprocess spawns — only the GPU itself remains (Colab operator action, 01c-06)
- Version registry durable and idempotent; dry-run evidence survives sessions
- All 145 engine/script tests pass; full suite 1772 pass with 5 pre-existing corrupt-catalog failures unchanged

## Self-Check: PASSED
All key files exist, commits verified, offline chain proven, no new regressions.
