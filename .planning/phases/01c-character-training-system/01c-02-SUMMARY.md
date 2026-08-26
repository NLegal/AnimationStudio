---
phase: 01c-character-training-system
plan: 02
subsystem: training-engine
tags: [benchmark, identity-scorer, lora, adapter, weights, coverage]

# Dependency graph
requires:
  - phase: 01c-01
    provides: DatasetBuilder, VersionRegistry, find_curated query, benchmark skeleton
provides:
  - IdentityScorerProvider adapter bridging identity_engine to LoRABenchmark
  - Canonical 7-dimension weight table aligned to D-06 plugin registry
  - Coverage-honest composite scoring (partial dims excluded from numerator/denominator)
  - 0.90 pass threshold with full-coverage gate
affects: [01c-03, 01c-04]

# Tech tracking
tech-stack:
  added: []
  patterns: [adapter-protocol, coverage-honest-scoring, drift-guard-test]

key-files:
  created:
    - src/training_engine/scorer_adapter.py
  modified:
    - src/training_engine/benchmark.py
    - src/training_engine/__init__.py
    - tests/test_lora_training.py

key-decisions:
  - "Benchmark weights mirror D-06 plugin registry exactly (not BrandScore.WEIGHTS which includes unscoreable technical_quality)"
  - "Pass gate requires weight_coverage >= 1.0 — partial plugin coverage always fails even if partial average is high"
  - "Composite rounded to 4 decimal places before pass gate to avoid float precision edge cases"
  - "MockScorerProvider emits 7 canonical keys in 0.6-0.98 uniform band (replaces legacy 6-dim mock)"

patterns-established:
  - "Drift-guard test: constructs IdentityScorer and asserts plugin name/weight match benchmark table"
  - "Coverage-honest evaluate: iterate weight table, skip absent dims, compute coverage ratio"

requirements-completed: [CHAR-07]

coverage:
  - id: D1
    description: "Benchmark weight table aligned to identity-engine plugin registry with drift-guard test"
    requirement: "CHAR-07"
    verification:
      - kind: unit
        ref: "tests/test_lora_training.py::TestBenchmarkAlignment::test_drift_guard_plugin_weights_match_benchmark"
        status: pass
    human_judgment: false
  - id: D2
    description: "Coverage-honest composite scoring with weight_coverage on BenchmarkResult"
    requirement: "CHAR-07"
    verification:
      - kind: unit
        ref: "tests/test_lora_training.py::TestBenchmarkComposite::test_partial_coverage_excludes_missing_dims"
        status: pass
    human_judgment: false
  - id: D3
    description: "0.90 threshold default with strict >= comparison and boundary tests"
    requirement: "CHAR-07"
    verification:
      - kind: unit
        ref: "tests/test_lora_training.py::TestBenchmarkAlignment::test_threshold_default_is_090"
        status: pass
    human_judgment: false
  - id: D4
    description: "IdentityScorerProvider adapts IdentityScorer to ScorerProvider protocol offline"
    requirement: "CHAR-07"
    verification:
      - kind: unit
        ref: "tests/test_lora_training.py::TestIdentityScorerProvider::test_light_mode_constructs_offline"
        status: pass
    human_judgment: false
  - id: D5
    description: "Unknown plugin keys filtered defensively with warning in adapter"
    requirement: "CHAR-07"
    verification:
      - kind: unit
        ref: "tests/test_lora_training.py::TestIdentityScorerProvider::test_filters_unknown_keys"
        status: pass
    human_judgment: false

# Metrics
duration: 1h 58m
completed: 2026-08-26
status: complete
---

# Phase 1c Plan 02: Benchmark ↔ Identity Engine Integration Summary

**Aligned 7-dimension weight table from identity-engine plugin registry (D-06), raised threshold to 0.90, added coverage-honest scoring, and delivered IdentityScorerProvider adapter bridging IdentityScorer to LoRABenchmark offline**

## Performance

- **Duration:** 1h 58m
- **Started:** 2026-08-26T16:45:18Z
- **Completed:** 2026-08-26T18:43:22Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Replaced legacy 6-dimension `_BENCHMARK_WEIGHTS` (dino_similarity, clip_alignment, etc.) with 7 canonical plugin names/weights (character_consistency 0.40, prompt_accuracy 0.20, color_harmony 0.10, facial_appeal 0.10, silhouette_recognizability 0.05, child_friendliness 0.05, style_consistency 0.10)
- Added coverage-honest evaluation: missing dimensions excluded from both numerator and denominator, `weight_coverage` field tracks coverage ratio, pass gate requires coverage = 1.0
- Raised `BenchmarkConfig.similarity_threshold` default from 0.85 to 0.90 (G13, ROADMAP >= 90% requirement)
- Created `IdentityScorerProvider` adapter: dependency injection, PIL image opening, canonical-key filtering with unknown-key warnings, re-exported from package root
- Drift-guard test catches future plugin-weight edits silently diverging from the benchmark table

## Task Commits

Each task was committed atomically:

1. **Task 1 (RED):** `f5d3ea29` (test) — failing tests for benchmark alignment
2. **Task 1 (GREEN):** `b2324830` (feat) — aligned weights, threshold, coverage-honest evaluate
3. **Task 2 (RED):** `0ad4e219` (test) — failing tests for IdentityScorerProvider
4. **Task 2 (GREEN):** `a7e6d250` (feat) — IdentityScorerProvider adapter + re-export

## Files Created/Modified

- `src/training_engine/scorer_adapter.py` — NEW: IdentityScorerProvider adapter (73 lines)
- `src/training_engine/benchmark.py` — Aligned weight table, threshold 0.90, coverage-honest composite loop, weight_coverage field, updated report() and MockScorerProvider
- `src/training_engine/__init__.py` — Added IdentityScorerProvider to imports and __all__
- `tests/test_lora_training.py` — Added TestBenchmarkAlignment (4 tests), TestBenchmarkComposite (5 tests), TestIdentityScorerProvider (4 tests), updated MockScorerProvider tests

## Decisions Made

- **D-06 plugin weights over BrandScore.WEIGHTS:** BrandScore includes `technical_quality` (0.15) which no plugin emits, capping achievable totals at 0.85 — impossible to reach the >= 90% gate. D-06 plugin weights map 1:1 to what ScorerProvider adapters actually return.
- **Full-coverage gate:** Partial plugin coverage always fails the gate (weight_coverage < 1.0) even if partial composite is high. This enforces honesty: a 5-plugin light-mode benchmark is not a valid production gate.
- **Float rounding before comparison:** composite_score rounded to 4 decimal places before the pass gate comparison to avoid precision edge cases (e.g. matched_weight_sum = 1.0000000000000002 yielding composite = 0.8999999999999998).

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Full test suite (`pytest -q`) hangs on unrelated tests (pre-existing, not caused by this plan). Engine-specific suites (`test_training_engine.py` + `test_lora_training.py`) pass cleanly — 72 tests, 3.03s.
- PIL `UnidentifiedImageError` when adapter tests used `write_text("fake")` for images — fixed by creating proper PIL images in fixtures.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- IdentityScorerProvider ready for use by LoRABenchmark in production (Plan 01c-03/01c-04)
- Benchmark now correctly measures what the identity engine actually measures — no zero-dimension collapse (Pitfall 4 impossible by construction)
- Plan 01c-03 (VersionRegistry persistence) can proceed without benchmark dependency

---
*Phase: 01c-character-training-system*
*Completed: 2026-08-26*
