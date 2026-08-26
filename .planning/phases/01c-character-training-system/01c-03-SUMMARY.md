---
phase: 01c-character-training-system
plan: 03
subsystem: training-engine
tags: [kohya, flux, lora, dry-run, accelerate, subprocess]

# Dependency graph
requires:
  - phase: 01c-01
    provides: DatasetBuilder with sidecar captions and valid TOML config
  - phase: 01c-02
    provides: Benchmark weight alignment and IdentityScorerProvider adapter
provides:
  - "First-class dry_run mode on TrainingConfig and KohyaAdapter"
  - "Flux-complete accelerate launch command builder"
  - "Identifier validation (injection-safe character_id/version)"
  - "Inspectable .train_cmd.json artifact for offline proof"
affects: [01c-04, 01c-05, 01c-06]

# Tech tracking
tech-stack:
  added: []
  patterns: [dry-run-first-class-mode, accelerate-launch-wrapper, arglist-invariant]

key-files:
  created: []
  modified:
    - src/training_engine/base.py
    - src/training_engine/kohya_adapter.py
    - tests/test_training_engine.py

key-decisions:
  - "auto-upgrade network_module to networks.lora_flux for Flux models (detected from script name)"
  - "identifier validation uses conservative lowercase alphanumeric pattern — rejects any injection attempt"
  - "dry_run branch wraps mkdir + artifact write in try/except OSError for typed failure on unwritable paths"
  - "accelerate launch with --num_cpu_threads_per_process 1 for Colab 2-vCPU runtimes"

patterns-established:
  - "dry-run-as-first-class-mode: config.dry_run branch in train() reuses registration block verbatim"
  - "identifier-validation: conservative regex before interpolation into filenames or argv"

requirements-completed: [CHAR-07]

coverage:
  - id: D1
    description: "First-class dry_run mode completing training without subprocess spawn"
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: "tests/test_training_engine.py::TestDryRunMode::test_dry_run_no_subprocess"
        status: pass
    human_judgment: false
  - id: D2
    description: "Dry-run produces inspectable .train_cmd.json artifact"
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: "tests/test_training_engine.py::TestDryRunMode::test_dry_run_writes_command_artifact"
        status: pass
    human_judgment: false
  - id: D3
    description: "Dry-run registers version through the normal path"
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: "tests/test_training_engine.py::TestDryRunMode::test_dry_run_registers_version"
        status: pass
    human_judgment: false
  - id: D4
    description: "Identifier validation rejects injection attempts (character_id, version)"
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: "tests/test_training_engine.py::TestDryRunMode::test_dry_run_invalid_character_id_returns_failure"
        status: pass
    human_judgment: false
  - id: D5
    description: "Flux-complete accelerate launch command with lora_flux network, companion models, fp8/cache flags"
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: "tests/test_training_engine.py::TestFluxCommandGeneration"
        status: pass
    human_judgment: false
  - id: D6
    description: "Colab-safe dataloader workers (2) and caption_dropout_rate forwarded"
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: "tests/test_training_engine.py::TestFluxCommandGeneration::test_dataloader_workers_reduced_to_two"
        status: pass
    human_judgment: false

# Metrics
duration: 106min
completed: 2026-08-26
status: complete
---

# Phase 1c Plan 03: Dry-run Mode and Flux Command Builder Summary

**First-class dry_run mode on TrainingConfig/KohyaAdapter with Flux-complete accelerate launch command builder and identifier validation**

## Performance

- **Duration:** 106 min
- **Started:** 2026-08-26T20:28:42Z
- **Completed:** 2026-08-26T22:14:54Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Dry-run is now a first-class engine mode producing registry-valid completions with inspectable .train_cmd.json artifacts, all proven by 9 sentinel-based tests
- `_build_command` emits the complete Flux training contract (accelerate wrapper, lora_flux network, companion models, fp8/cache/memory flags, Colab-safe worker count) as a safe arg-list, with 17 tests covering every flag
- Identifier validation + arg-list invariant make command construction injection-safe

## Task Commits

Each task was committed atomically (TDD RED → GREEN):

1. **Task 1: First-class dry_run mode (G17)** — `91369991` (test), `b1e66c5d` (feat)
2. **Task 2: Flux-complete _build_command (G16)** — `2736c484` (test), `cbbe5d04` (feat)

## Files Created/Modified
- `src/training_engine/base.py` - Added `dry_run: bool = False`, `clip_l_path`, `t5xxl_path`, `ae_path`, `blocks_to_swap` fields to TrainingConfig
- `src/training_engine/kohya_adapter.py` - Dry-run branch in train() with artifact writing and identifier validation; Flux-complete _build_command with accelerate wrapper
- `tests/test_training_engine.py` - 9 dry-run tests + 17 Flux command tests (26 new tests total)

## Decisions Made
- Auto-upgrade `network_module` to `networks.lora_flux` when Flux model detected (script name contains "flux")
- Identifier validation uses conservative regex: `^[a-z0-9][a-z0-9\-_]{0,127}$` for character_id, `^v?[0-9]+\.[0-9]+[a-zA-Z0-9.\-_]*$` for version
- Dry-run mkdir + artifact write wrapped in `try/except OSError` for typed failure on unwritable paths
- `accelerate launch --num_cpu_threads_per_process 1` for Colab 2-vCPU runtimes

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None — all tasks completed without blockers.

## Known Stubs

None — all planned functionality fully wired and tested.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Dry-run mode complete and tested — Plan 01c-04 (scripts/train_lora.py orchestrator) can use dry_run=True for offline orchestration
- Flux command builder ready for Colab notebook (Plan 01c-06)
- All 40 training engine tests pass offline; 1745 full-suite tests pass (5 pre-existing story-engine failures unrelated)

---
*Phase: 01c-character-training-system*
*Completed: 2026-08-26*

## Self-Check: PASSED

All files exist, all 4 commit hashes verified, test counts confirmed (9 dry-run + 17 Flux command + 40 total).

