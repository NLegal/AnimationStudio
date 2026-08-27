# Deferred Items — Phase 01c (Character Training System)

Out-of-scope discoveries logged during plan execution (never fixed here).

## Pre-existing full-suite failures (tests/test_story_engine.py)

**Status:** open — pre-existing, unrelated to Phase 1c files.

Full-suite run on 2026-08-27 (`python3 -m pytest -q`: 1833 passed, 5 failed)
fails 5 catalog-integration tests in `tests/test_story_engine.py`:

- `TestExpandedCharacterRoster::test_catalog_info_resolves_lily`
- `TestStoryCatalogIntegration::test_resolve_location_from_catalog`
- `TestStoryCatalogIntegration::test_resolve_prop_to_approved_file`
- `TestStoryCatalogIntegration::test_universe_characters_from_catalog`
- `TestStoryCatalogIntegration::test_generator_enriches_blueprint`

Root observation: `test_universe_characters_from_catalog` asserts `"Lily Bunny" in names`
but the universe catalog returns an empty set — consistent with the known
corrupted/underseeded `catalog.db` (C-CATALOGDB) and/or universe seeding state.
No Phase 1c file (training notebook JSON, `tests/test_colab_notebooks.py`,
README Character Training section) is imported by `story_engine` or these tests;
the failures reproduce independently of Phase 1c changes.

Owner: the phase that owns `src/universe/` + `src/story_engine/` catalog
integration (Phase 6 story engine work) or a dedicated catalog-repair plan.

## Pre-existing working-tree noise (environment artifact, untracked change)

The working tree carries ~549 stat-dirty files (re-touched `Assets/*.png`,
CRLF-converted README/tests/scripts/src files, mode 100755 on several scripts,
stale stat info on `catalog.db`, `VISION.md`, `Universe/`, `World/`). These are
pre-checkout artifacts of a Windows CRLF checkout and are **not** staged or
committed by Phase 1c. `README.md`'s index blob hash matches the worktree
(`a6fac7e0`) after Phase 1c normalized it to LF; it was already byte-identical
before the Phase 1c edit.