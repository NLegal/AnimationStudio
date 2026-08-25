# Phase 7 — Deferred Items (out-of-scope discoveries)

Logged per executor scope-boundary rules: pre-existing issues unrelated to the
current task's changes are recorded here, not fixed.

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Pre-existing test failures | `tests/test_story_engine.py::TestStoryCatalogIntegration` (4 tests: resolve_location, resolve_prop, universe_characters, generator_enriches_blueprint) + `TestExpandedCharacterRoster::test_catalog_info_resolves_lily` fail in full-suite runs AND in isolation; zero references to `src/music_generation`; order/state-dependent around repo-root catalog state | Open — pre-dates Phase 7 | 07-01 execution (2026-08-24) |
| Pre-existing test flakiness | `tests/test_review_ui_generation.py` fails 1 test under full-suite ordering but passes 26/26 in isolation; baseline run before this plan already showed an ERROR in this same file | Open — pre-dates Phase 7 | 07-01 execution (2026-08-24) |

Evidence: baseline full-suite run captured BEFORE any Phase 7 change showed
`5 failed, 1549 passed, 1 error` with the same two files implicated. After plan
07-01: `6 failed, 1584 passed` (+35 new passing music-generation tests, zero
regressions attributable to this plan). `catalog.db` md5 byte-identical
before/after suite runs (`acfb604a75657e99b2682ce3c73ec65b`).
