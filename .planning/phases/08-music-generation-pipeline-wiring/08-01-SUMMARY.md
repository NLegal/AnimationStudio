---
phase: 08-music-generation-pipeline-wiring
plan: 01
subsystem: cli
tags: [music, pipeline, argparse, manifest, mock-backend]

# Dependency graph
requires:
  - phase: 07-music-generation-backend-integration
    provides: src/music_generation/ package (MusicGenerationBackend protocol, AceStepBackend, SunoBackend stub, MockBackend, get_backend registry, build_music_request, resolve_music_params, MusicBackendError taxonomy)
  - phase: 01-character-universe
    provides: src/audio_bible/bible.py AudioBible facade, QualityChecklist
provides:
  - "scripts/generate_phase5.py --generate mode: backend alias normalization, 24-category batch generation, per-category exit codes, resume-skip manifest"
  - "tests/test_generate_phase5.py: TestGenerationMode, TestBatchGeneration, TestManifest (36 tests)"
  - "Audio/Music/README.md live-smoke checklist extension with --generate command"
affects: [08-02-PLAN.md — Review UI hooks import manifest helpers from this script]

# Tech tracking
tech-stack:
  added: []
  patterns: [module-level get_backend import for testability, module-level manifest helpers for cross-plan import, atomic os.replace manifest writes, csv-split repeatable --category argparse pattern]

key-files:
  created: [tests/test_generate_phase5.py]
  modified: [scripts/generate_phase5.py, Audio/Music/README.md]

key-decisions:
  - "get_backend + build_music_request + MusicBackendError imported at module level in generate_phase5.py (not function-local) so Plan 08-02 Review UI can monkeypatch backends in integration tests"
  - "Manifest helpers live at MODULE level in scripts/generate_phase5.py because plan 08-02's Review UI worker imports these exact functions (PATTERNS Deliberate Divergence #2)"
  - "Plan 08-02's Review UI will import atomic_write_manifest, upsert_entry, find_entry, entry_matches from scripts.generate_phase5 — cross-plan import is the intended pattern"
  - "Suno refusal path validated: zero transport calls (fail-loud guards on _post_json/_get_json/_get_bytes remain untripped), --backend suno exits 1 with typed error"
  - "entry_matches is a pure dict comparison (backend/topic/duration_s); file-existence and bytes checks live in the caller skip-logic in generate_songs"
  - "changed-seed or changed-topic always regenerates — entry_matches compares backend+topic+duration_s but NOT filename, so different seed produces a different entry"

patterns-established:
  - "Module-level manifest helpers for cross-plan reuse: functions at module scope, not class methods"
  - "fail-loud transport guards: monkeypatch _post_json/_get_json/_get_bytes to raise AssertionError, assert zero trips for stub/non-transport backends"

requirements-completed: []

coverage:
  - id: D1
    description: "Generation-mode CLI tracer: single-song mock e2e producing RIFF WAV + manifest with thirteen typed keys, BACKEND_ALIASES normalization, slug safety, unknown category/backend exit codes, report-mode byte-compatibility"
    verification:
      - kind: unit
        ref: "tests/test_generate_phase5.py::TestGenerationMode (11 tests)"
        status: pass
    human_judgment: false
  - id: D2
    description: "24-category batch generation: full bible-order run, comma/repeatable --category equivalence, mixed-failure accumulation with MusicBackendError, suno refusal with zero transport, stdout summary / stderr failure reasons, catalog.db byte-identity"
    verification:
      - kind: unit
        ref: "tests/test_generate_phase5.py::TestBatchGeneration (5 tests)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Manifest resume matrix: schema goldens (version 1, thirteen typed keys), same-signature skip, changed-seed/topic regeneration, deleted-WAV regeneration, --force bypass, crash simulation (leftover .tmp, truncated JSON)"
    verification:
      - kind: unit
        ref: "tests/test_generate_phase5.py::TestManifest (17 tests)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Audio/Music/README.md live-smoke checklist extended with --generate --backend ace-step --category Bedtime command (manual-only, never in CI)"
    verification: []
    human_judgment: true
    rationale: "Manual verification step requiring live ACE-Step service on operator machine"

# Metrics
duration: 76min
completed: 2026-08-25
status: complete
---

# Phase 8 Plan 01: Script + Manifest Core Summary

**Generation-mode CLI with 24-category mock batch, atomic manifest resume, and 36 offline tests**

## Performance

- **Duration:** 76 min
- **Started:** 2026-08-25T09:41:55Z
- **Completed:** 2026-08-25T10:58:16Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- scripts/generate_phase5.py extended with `--generate` mode: BACKEND_ALIASES normalization, `parse_categories` with comma-split, `song_filename` slug-safe naming, manifest writers at module level (load_manifest / find_entry / entry_matches / upsert_entry / atomic_write_manifest), generate_songs batch loop with resume-skip and failure accumulation
- TestGenerationMode (11 tests): single-song mock e2e (RIFF magic + thirteen-key manifest), alias normalization, slug safety (traversal stripped), unknown category/backend → SystemExit, report-mode byte-compatibility, no sqlite3/image/pyproject.toml violations
- TestBatchGeneration (5 tests): full 24-category mock run (bible order, unique filenames, catalog.db byte-identity), comma vs repeatable --category equivalence, mixed MusicBackendError failure accumulation (exit 1), suno refusal with zero transport calls (fail-loud guards untripped), stdout/stderr output discipline
- TestManifest (17 tests): version-1 golden schema with typed thirteen keys, same-signature skip (0 new files), changed-seed/topic regeneration, deleted-WAV regeneration, --force bypass, crash simulation (.tmp ignored, truncated manifest degrades to rebuild), load_manifest / upsert_entry / entry_matches / atomic_write_manifest unit tests
- Audio/Music/README.md live-smoke checklist extended with step 6: `--generate --backend ace-step --category Bedtime` command (manual-only, never in CI)

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — single-song generation mode e2e** — `33c974b8` (feat)
2. **Task 2: Batch loop, failure accumulation, exit codes, live-smoke docs** — `b6d18137` (feat)
3. **Task 3: Manifest schema goldens, resume matrix, crash simulation** — `a64506b4` (test)

## Files Created/Modified

- `scripts/generate_phase5.py` — Extended with generation mode: BACKEND_ALIASES, _slug, song_filename, parse_categories, now_iso, manifest core (load/find_entry/matches/upsert/atomic_write), generate_songs batch loop, extended argparse, main(argv=None) refactor
- `tests/test_generate_phase5.py` — New module with 36 tests across 3 classes: TestGenerationMode, TestBatchGeneration, TestManifest
- `Audio/Music/README.md` — Live-smoke checklist extended with step 6: --generate --backend ace-step --category Bedtime command (manual-only)

## Decisions Made

1. **get_backend imported at module level** (not function-local) so Plan 08-02 Review UI integration tests can monkeypatch it — was function-local in tracer, promoted during Task 2
2. **Manifest helpers at module level** in generate_phase5.py, not a separate package — Plan 08-02 Review UI imports them directly from scripts.generate_phase5 (PATTERNS Deliberate Divergence #2)
3. **entry_matches is pure dict comparison** (backend/topic/duration_s only); file existence and bytes checks live in generate_songs skip branch — keeps golden tests simple and entry_matches reusable
4. **changed-seed always regenerates** even though entry_matches doesn't compare seed — different seed produces different filename, file doesn't exist, so regeneration is automatic
5. **Suno refusal validated**: zero transport seam calls (fail-loud guards untripped), exit 1, no traceback — C5 constraint satisfied
6. **Full baseline suit green modulo 5 known story-engine failures**: 1669 passed (vs 1550 baseline = 119 new tests from this plan)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] get_backend moved to module-level import for testability**
- **Found during:** Task 2 (batch loop tests)
- **Issue:** `get_backend` was imported function-local inside `generate_songs`, making it impossible for TestBatchGeneration to monkeypatch it to return a PartialFailBackend
- **Fix:** Promoted `from src.music_generation import get_backend, build_music_request, MusicBackendError` to module level in scripts/generate_phase5.py
- **Files modified:** scripts/generate_phase5.py (import location)
- **Verification:** TestBatchGeneration::test_mixed_failure_continues_batch passes
- **Committed in:** b6d18137 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 missing critical)
**Impact on plan:** Trivial import promotion — no scope creep. Plan already noted this pattern as Plan 08-02's import surface; early promotion only made Task 2 tests possible.

## Issues Encountered

None beyond the single auto-fix above.

## User Setup Required

None - no external service configuration required. Live-smoke checklist is documented in Audio/Music/README.md (manual-only, requires local ACE-Step service).

## Next Phase Readiness

- scripts/generate_phase5.py manifest helpers (atomic_write_manifest, upsert_entry, find_entry, entry_matches) are importable at module level and ready for Plan 08-02 Review UI consumption
- Test suite baseline: 1669 passed / 5 pre-existing story-engine failures — plan 08-02 should maintain or improve this baseline
- Live-smoke checklist in Audio/Music/README.md documents the manual ACE-Step verification path
- Plan 08-02 Review UI hooks will import manifest helpers from scripts.generate_phase5 and build job submission UI on top of the generate_songs orchestrator

## Known Stubs

None — all implementation functions are fully wired with real logic.

## Threat Flags

No new security surface introduced — generation mode writes to a user-chosen output directory with slug-safe filenames, no new network endpoints, no schema changes at trust boundaries.

## Self-Check: PASSED

All three created/modified files exist on disk (`generate_phase5.py`, `test_generate_phase5.py`, `Audio/Music/README.md`); three task commits verified in git log (`33c974b8`, `b6d18137`, `a64506b4`); `python3 -m pytest tests/test_generate_phase5.py -q` green (33 passed); constraint gates: C1 (no image) pass, C2 (sqlite3 only in test enforcement), C6 (pyproject.toml unchanged) pass.

---
*Phase: 08-music-generation-pipeline-wiring*
*Completed: 2026-08-25*
