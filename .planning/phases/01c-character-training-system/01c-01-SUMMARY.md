---
phase: 01c-character-training-system
plan: 01
subsystem: training-engine
tags: [kohya, dataset-builder, caption-sidecar, toml-schema, asset-repository, curated-query]

# Dependency graph
requires:
  - phase: 01b-character-asset-production
    provides: approved/production lifecycle assets in catalog.db
provides:
  - find_curated two-state repository query (approved + production)
  - schema-valid Kohya TOML with native validation_split
  - .txt caption sidecar per training image (trigger-word first)
  - 20-40 image bounds enforcement with per-state error messages
  - baselines/{character_id}/ directory population for benchmark
affects: [01c-02, 01c-03, 01c-04, 01c-05]

# Tech tracking
tech-stack:
  added: []
  patterns: [tomllib-schema-validation, path-containment-check, trigger-word-sidecar]

key-files:
  created: []
  modified:
    - src/asset_repository/sqlite_repo.py
    - src/training_engine/dataset_builder.py
    - src/training_engine/kohya_adapter.py
    - tests/test_asset_repository.py
    - tests/test_lora_training.py

key-decisions:
  - "find_curated returns list[AssetModel] ordered by brand_score DESC for deterministic caller deduplication"
  - "Bounds enforcement sits in DatasetBuilder.build(), not the adapter — adapter passes min_images=0"
  - "Baselines copy limited to 10 reference images per the plan spec"

patterns-established:
  - "Sidecar convention: .txt file adjacent to each image, body = trigger-word prefix + descriptor + suffix, survives shuffle_caption via keep_tokens=1"
  - "TOML schema validation: only documented sd-scripts keys emitted, val never mounted as training subset"

requirements-completed: [CHAR-07]

coverage:
  - id: D1
    description: find_curated two-state repository query returns approved/production rows with optional asset_type filter"
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: tests/test_asset_repository.py::test_find_curated_returns_approved_and_production
        status: pass
      - kind: unit
        ref: tests/test_asset_repository.py::test_find_curated_filters_by_asset_type
        status: pass
      - kind: unit
        ref: tests/test_asset_repository.py::test_find_curated_unknown_character_returns_empty
        status: pass
      - kind: unit
        ref: tests/test_asset_repository.py::test_find_curated_returns_brand_score
        status: pass
    human_judgment: false
  - id: D2
    description: Every training image has a .txt caption sidecar starting with the trigger word"
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: tests/test_lora_training.py::TestDatasetBuilder::test_sidecar_txt_per_image
        status: pass
    human_judgment: false
  - id: D3
    description: Generated TOML validates against documented Kohya sd-scripts schema with only documented keys and native validation_split"
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: tests/test_lora_training.py::TestDatasetBuilder::test_toml_valid_with_tomllib
        status: pass
    human_judgment: false
  - id: D4
    description: 20-40 image bounds enforced — error below minimum with per-state counts, truncation above maximum with warning"
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: tests/test_lora_training.py::TestDatasetBuilder::test_bounds_below_min_raises_value_error
        status: pass
      - kind: unit
        ref: tests/test_lora_training.py::TestDatasetBuilder::test_bounds_above_max_truncates
        status: pass
      - kind: unit
        ref: tests/test_lora_training.py::TestDatasetBuilder::test_bounds_custom_limits
        status: pass
    human_judgment: false
  - id: D5
    description: Reference-type curated assets copied into baselines/{character_id}/ matching LoRABenchmark._load_baseline_images convention"
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: tests/test_lora_training.py::TestDatasetBuilder::test_baselines_copy
        status: pass
      - kind: unit
        ref: tests/test_lora_training.py::TestDatasetBuilder::test_baselines_capped_at_10
        status: pass
      - kind: unit
        ref: tests/test_lora_training.py::TestDatasetBuilder::test_baselines_skips_non_reference
        status: pass
    human_judgment: false

duration: 165min
completed: 2026-08-26
status: complete
---

# Phase 01c Plan 01: Dataset Curation & Builder Completion Summary

**find_curated two-state query (approved/production), schema-valid Kohya TOML with native validation_split, .txt caption sidecars with trigger-word prefix, 20–40 image bounds, baselines directory population**

## Performance

- **Duration:** 165 min
- **Started:** 2026-08-26T13:03:49Z
- **Completed:** 2026-08-26T15:49:44Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Added `find_curated(character_id, asset_types?)` two-state repository query returning assets in `approved` or `production` lifecycle state, with deterministic ordering by brand_score
- Rewrote `_write_kohya_config` to emit only documented sd-scripts TOML keys — eliminates the `caption_metadata_file` schema rejection (G2) that would kill Colab training runs
- Added `.txt` caption sidecar per training image with trigger-word-first body surviving `shuffle_caption=true` via `keep_tokens=1`
- Implemented 20–40 image bounds enforcement — ValueError below minimum with per-state count breakdown, truncation + warning above maximum
- Added baselines copy: reference-type assets populate `baselines/{character_id}/` matching `LoRABenchmark._load_baseline_images` convention (capped at 10)
- Replaced val-as-training-subset with native `validation_split`/`validation_seed` (G3) — validation images are no longer trained on
- Added path containment check (T-01c-01a) — paths escaping their declared root are skipped with warning

## Task Commits

Each task was committed atomically:

1. **Task 1: Add find_curated two-state repository query (G4)** — `98528a3f` (test), `464e24ea` (feat)
2. **Task 2: DatasetBuilder correctness — sidecars, TOML, bounds, baselines** — `bdca9761` (test), `6349f22a` (feat)

## Files Created/Modified

- `src/asset_repository/sqlite_repo.py` — Added `find_curated()` async method with two-state IN clause and optional asset_type filter
- `src/training_engine/dataset_builder.py` — Sidecar writing, valid TOML, bounds enforcement, baselines copy, path containment
- `src/training_engine/kohya_adapter.py` — `build_dataset` passes min_images=0/max=infinite (bounds at orchestrator level)
- `tests/test_asset_repository.py` — 4 new tests for find_curated
- `tests/test_lora_training.py` — 8 new tests for sidecars, TOML, bounds, baselines; updated existing tests for sidecar-aware file counts

## Decisions Made

- find_curated returns `list[AssetModel]` (not dicts) consistent with `find_approved`, ordered by `brand_score DESC, id` for deterministic caller deduplication
- Bounds enforcement lives in `DatasetBuilder.build()`, not the adapter — the adapter passes `min_images=0` since it's a convenience wrapper
- Baselines copy limited to 10 reference images per plan spec

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Updated test_build_train_val_split for sidecar-aware file counts**
- **Found during:** Task 2 (GREEN phase)
- **Issue:** `test_build_train_val_split` counted `iterdir()` entries in train/val dirs — after adding sidecars, 8 images produce 16 files (8 .png + 8 .txt)
- **Fix:** Changed assertion to count `.png` and `.txt` files separately, updated total counts
- **Files modified:** tests/test_lora_training.py
- **Verification:** All 79 tests pass
- **Committed in:** 6349f22a

**2. [Rule 1 - Bug] Updated existing tests to use min_images=0**
- **Found during:** Task 2 (GREEN phase)
- **Issue:** Existing tests create small datasets (1-10 images) that trigger the new min_images=20 default bounds check
- **Fix:** Added `min_images=0` to existing test DatasetConfig instances; bounds tests use explicit custom limits
- **Files modified:** tests/test_lora_training.py
- **Verification:** All 79 tests pass
- **Committed in:** 6349f22a

**3. [Rule 3 - Blocking] Updated kohya_adapter.build_dataset to pass min_images=0**
- **Found during:** Task 2 (GREEN phase)
- **Issue:** `KohyaAdapter.build_dataset` created `DsConfig` with default `min_images=20`, causing its integration tests to fail with small datasets
- **Fix:** Adapter passes `min_images=0, max_images=999999` — bounds enforcement is the orchestrator's responsibility
- **Files modified:** src/training_engine/kohya_adapter.py
- **Verification:** test_build_dataset_returns_config_path passes
- **Committed in:** 6349f22a

---

**Total deviations:** 3 auto-fixed (2 bugs, 1 blocking)
**Impact on plan:** All auto-fixes necessary for test compatibility with new features. No scope creep.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- find_curated is ready for the dataset orchestrator (01c-05) and the benchmark bridge (01c-02)
- Schema-valid TOML ensures Colab training runs won't hit `extra keys not allowed` on sd-scripts startup
- .txt sidecars follow the locked trigger-word convention
- Baselines directory is populated for benchmark comparison
- 79 tests pass offline (no GPU, no network) — ready for next plan

---
*Phase: 01c-character-training-system*
*Completed: 2026-08-26*
