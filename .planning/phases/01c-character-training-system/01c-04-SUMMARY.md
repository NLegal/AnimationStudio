---
phase: 01c-character-training-system
plan: 04
subsystem: training_engine
tags: [versioning, json-sidecar, persistence, idempotent, promote]

# Dependency graph
requires:
  - phase: 01c-01
    provides: DatasetBuilder, min/max bounds, baselines copy, .txt sidecars
  - phase: 01c-02
    provides: Benchmark weight alignment, IdentityScorerProvider, threshold 0.90
provides:
  - JsonVersionStore for corruption-isolated JSON sidecar persistence
  - Store-backed VersionRegistry with hydrate-on-construct / persist-on-mutate
  - Idempotent registration on (character_id, version)
  - promote() for post-hoc production promotion (G10)
  - load_registry() factory convenience
affects: [01c-05, 01c-06]

# Tech tracking
tech-stack:
  added: []
  patterns: [json-sidecar-store, atomic-write-temp-replace, idempotent-registration]

key-files:
  created:
    - src/training_engine/version_store.py
  modified:
    - src/training_engine/versioning.py
    - src/training_engine/__init__.py
    - tests/test_lora_training.py

key-decisions:
  - "JSON sidecar chosen over catalog.db migration per locked A3 — corruption-isolated persistence"
  - "Idempotent registration replaces in-place on (character_id, version) match — no duplicate records"
  - "promote() uses flip-target-only semantics — does not un-promote others, preserving audit trail"

patterns-established:
  - "JSON sidecar store: atomic temp+replace writes with tolerant parse for crash resilience"
  - "Registry store seam: load-on-construct, persist-on-mutate — zero overhead when store=None"

requirements-completed: [CHAR-07]

coverage:
  - id: D1
    description: JsonVersionStore persists and hydrates version records with atomic writes"
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: tests/test_lora_training.py::TestJsonVersionStore
        status: pass
    human_judgment: false
  - id: D2
    description: Store-backed VersionRegistry hydrates on construction, persists on mutation
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: tests/test_lora_training.py::TestVersionRegistryPersistence
        status: pass
    human_judgment: false
  - id: D3
    description: Idempotent registration replaces in-place on (character_id, version) match
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: tests/test_lora_training.py::TestVersionRegistryPersistence::test_idempotent_register_replaces_existing
        status: pass
    human_judgment: false
  - id: D4
    description: promote() flips record to production, persists, raises on unknown
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: tests/test_lora_training.py::TestVersionRegistryPromotion
        status: pass
    human_judgment: false

# Metrics
duration: 47min
completed: 2026-08-26
status: complete
---

# Phase 1c Plan 04: Version Store & Promotion Summary

**JSON sidecar persistence with atomic writes, idempotent registry, and post-hoc promote() for the train-v0.x → benchmark → promote-v1.0 flow**

## Performance

- **Duration:** 47 min
- **Started:** 2026-08-26T23:10:52Z
- **Completed:** 2026-08-26T23:58:23Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Created JsonVersionStore: corruption-isolated JSON sidecar store with atomic writes (temp+replace), tolerant parse (skips corrupt entries), and missing-file safety
- Extended VersionRegistry with optional store parameter: hydrate-on-construct, persist-on-mutate seam; default in-memory behavior unchanged (51 baseline tests preserved)
- Made registration idempotent on (character_id, version): re-registering replaces in-place instead of duplicating (Pitfall 5)
- Added promote(character_id, version) for post-hoc production promotion: flip-target-only semantics preserves audit trail of all historically promoted versions
- load_registry() factory convenience function for hydrated registry construction

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: failing tests for JsonVersionStore and store-backed registry** - `c1118c9d` (test)
2. **Task 1 GREEN: JsonVersionStore + idempotent registry + promote()** - `0f96f98a` (feat)
3. **Task 2 RED: promotion round-trip, error, and field-preservation tests** - `66fddc77` (test)

**Plan metadata:** (pending — docs commit)

## Files Created/Modified
- `src/training_engine/version_store.py` - JsonVersionStore (atomic JSON sidecar store) and load_registry() factory
- `src/training_engine/versioning.py` - Store-backed VersionRegistry with idempotent register() and promote()
- `src/training_engine/__init__.py` - Re-exports JsonVersionStore, load_registry
- `tests/test_lora_training.py` - 18 new tests across 3 new test classes (TestJsonVersionStore, TestVersionRegistryPersistence, TestVersionRegistryPromotion)

## Decisions Made
- JSON sidecar chosen over catalog.db migration per locked A3 — corruption-isolated persistence avoids touching the corrupted production database
- Idempotent registration replaces in-place on (character_id, version) match — prevents duplicate records from repeated dry-runs (Pitfall 5)
- promote() uses flip-target-only semantics — does not un-promote other versions, preserving a complete audit trail of every promoted version
- Store seam pattern: load-on-construct, persist-on-mutate — zero filesystem overhead when store=None preserves backward compatibility

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- VersionRegistry is now durable and idempotent — ready for train_lora.py orchestrator (01c-05)
- promote() enables the full train-v0.x → benchmark-pass → promote-v1.0 production flow
- catalog.db remains untouched (C-CATALOGDB constraint satisfied)
- All 117 training engine tests pass offline with zero regressions

## Self-Check: PASSED

All key files exist, all 3 commits verified in git log, 117 training engine tests pass with 0 regressions.

---
*Phase: 01c-character-training-system*
*Completed: 2026-08-26*
