---
phase: 01b-character-asset-production
plan: 01
subsystem:
  - prompt_builder
  - asset_repository
  - identity_engine/plugins
tags: [expression-merge, pose-merge, lineage-metadata, color-plugin, tdd]
requires: []
provides:
  - Merged expression list (32 items)
  - Merged pose list (28 items)
  - AssetModel lineage field
  - File-based brand palette loading
affects:
  - src/prompt_builder/builder.py — expression + pose sets expanded
  - src/models/schemas.py — AssetModel gains lineage field
  - src/asset_repository/sqlite_repo.py — schema migration for lineage column
  - src/identity_engine/plugins/color_verification.py — file-based palette loading
  - tests/ — 3 new test classes (74 new tests)
tech-stack:
  added: []
  patterns:
    - ALTER TABLE IF NOT EXISTS migration pattern for SQLite
    - Class-level result caching for filesystem reads
    - TDD RED/GREEN cycle for feature rollout
key-files:
  created: []
  modified:
    - src/prompt_builder/builder.py
    - src/models/schemas.py
    - src/asset_repository/sqlite_repo.py
    - src/identity_engine/plugins/color_verification.py
    - tests/test_prompt_builder.py
    - tests/test_asset_repository.py
    - tests/test_scoring_plugins.py
decisions:
  - D-18 lineage captured as Optional[dict] — JSON serialized to SQLite TEXT column with ALTER TABLE migration
  - ColorVerificationPlugin palette loaded from Universe/ColorPalette/brand-palette.json with class-level _cached_palette
  - DEFAULT_BRAND_PALETTE retained as fallback constant, constructor signature unchanged
  - Expression/pose merge uses lowercase set union — PHASE1.md canonical, code extras preserved
metrics:
  duration: ~45 min
  completed_date: 2026-07-29
  task_count: 3
  commit_count: 4
  tests_added: 74
  tests_total: 230
status: complete
---

# Phase 01b Plan 01: Expression/Pose Merge + Lineage Metadata + Color Plugin Fix

## One-liner

Updated `PromptBuilder` with merged expression (32) and pose (28) lists superseding both PHASE1.md and code sources, added `lineage: Optional[dict]` to `AssetModel` with SQLite ALTER TABLE migration, and rewired `ColorVerificationPlugin` to load the brand palette from `Universe/ColorPalette/brand-palette.json` with class-level caching and `DEFAULT_BRAND_PALETTE` fallback. All 230 tests pass.

## Tasks Summary

**Tracer (Task 1)** — TDD RED/GREEN cycle for merged expression list:
1. RED commit `34391f9`: Failing tests for merged 32-expression set
2. GREEN commit `776ba87`: Implementation + integration test proving GenerationJob pipeline works end-to-end with MockBackend
- **Verification:** `TestMergedExpressionList` (36 tests) + `TestEndToEndExpressionPipeline` (1 test) — 37 total, all passing

**Auto Task 2** — Lineage metadata on AssetModel + SQLite:
3. Commit `2acbeb4`: Added `lineage: Optional[dict]` field, `lineage TEXT` column via ALTER TABLE, `_apply_migrations()`, `_row_to_asset()` deserialization, `save()` serialization.
- **Verification:** `test_lineage_metadata_roundtrip` + `test_apply_migrations_lineage_column` — 2 tests, all passing

**Auto Task 3** — Pose merge + ColorVerificationPlugin palette loading:
4. Commit `32a4284`: Updated `_known_poses()` to merged 28-pose set + rewired `ColorVerificationPlugin` to load palette from filesystem with caching.
- **Part A verification:** `TestMergedPoseList` (31 tests) — all passing
- **Part B verification:** `TestColorVerificationPlugin` (4 tests) — all passing

## Verification Results

| Command | Result |
|---------|--------|
| `pytest tests/` | 230 passed (9 warnings, all expected) |
| `test_prompt_builder.py` | 89 passed (all expression + pose + pipeline tests) |
| `test_asset_repository.py` | 13 passed (including lineage tests) |
| `test_scoring_plugins.py` | 55 passed (including color plugin tests) |

No existing tests regressed. No conftest.py fixtures were modified.

## Success Criteria Fulfilled

| Criterion | Status |
|-----------|--------|
| `_known_expressions()` returns 32 expressions (23 PHASE1.md + 9 code extras) | ✅ |
| `_known_poses()` returns 28 poses (20 PHASE1.md + 8 code extras) | ✅ |
| `AssetModel` has `lineage: Optional[dict]` persisting through SQLite | ✅ |
| `ColorVerificationPlugin` loads palette from `brand-palette.json` with fallback | ✅ |
| All 3 new test classes pass | ✅ |
| Integration test proves GenerationJob + MockBackend pipeline works | ✅ |

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — all code is production-ready. No hardcoded placeholders, empty data flows, or TODO comments.

## Threat Flags

None — no new security-relevant surface introduced. Palette file reads are local-only from a fixed, version-controlled path. SQLite operations use parameterized placeholders. No new package dependencies.

## TDD Gate Compliance

✅ RED gate: `test(01b-01): add failing test for merged expression list` — 34391f9
✅ GREEN gate: `feat(01b-01): implement merged expression list` — 776ba87

## Commits

| Hash | Type | Message |
|------|------|---------|
| 34391f9 | test | add failing test for merged expression list |
| 776ba87 | feat | implement merged expression list |
| 2acbeb4 | feat | add lineage metadata to AssetModel and SQLite schema |
| 32a4284 | feat | update _known_poses() and fix ColorVerificationPlugin palette loading |

## Self-Check: PASSED

All created files verified on disk. All commits confirmed via `git log`. All 230 tests passing.
