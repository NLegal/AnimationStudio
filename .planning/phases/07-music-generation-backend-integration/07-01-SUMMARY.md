---
phase: 07-music-generation-backend-integration
plan: 01
subsystem: music-generation
tags: [music, backend-protocol, pydantic, urllib, deterministic-mock, offline-first]
requires:
  - src/audio_bible/prompts.py (build_music_prompt, category_negative authority)
  - src/models/schemas.py (Pydantic v2 conventions mirrored)
provides:
  - MusicRequest / MusicStatus / MusicResult models (src/music_generation/models.py)
  - MusicGenerationBackend @runtime_checkable Protocol + default generate() loop (backends.py)
  - Typed exception taxonomy: MusicBackendError, NotConfigured, BackendUnavailable, GenerationFailed
  - CategoryMusicParams + CATEGORY_MUSIC_PARAMS + resolve_music_params + build_music_request + music_negative_prompt
  - Transport seam: _post_json/_get_json/_get_bytes + _urlopen/_sleep/_monotonic seams + DEFAULT_TRANSPORT
  - Deterministic MockBackend (byte-identical same-seed WAV data structures)
affects:
  - Plan 07-02 (AceStepBackend/SunoBackend/SunoWrapperBackend/get_backend registry/CLI consume protocol, error map, DEFAULT_TRANSPORT)
  - Phase 8 wiring points (pipeline mode, Review UI hooks, Colab notebook)
tech-stack:
  added: []
  patterns:
    - runtime_checkable typing.Protocol over ABC (duck-typed conformance, no inheritance)
    - module-level patchable seams (_sleep/_urlopen/_monotonic) for zero-wait offline tests
    - submit→poll→download async-job lifecycle with doubling backoff capped x8 and monotonic deadline
    - Pydantic v2 Literal enums + Field bounds mirroring src/models/schemas.py
key-files:
  created:
    - src/music_generation/__init__.py
    - src/music_generation/models.py
    - src/music_generation/backends.py
    - src/music_generation/mock.py
    - tests/test_music_generation.py
  modified: []
key-decisions:
  - "Protocol default generate() reused by duck-typed backends via class-level assignment (`generate = MusicGenerationBackend.generate`) because Protocol defaults are NOT inherited structurally — AceStepBackend in 07-02 must do the same"
  - "_urlopen is a tuple-aware wrapper (not a bare alias): fakes/tests assert the full (5,30) connect/read timeout tuple at the seam while the wrapper flattens it to the single socket timeout stdlib urlopen actually supports"
  - "Concrete-backend result metadata convention: BACKEND_NAME/AUDIO_FORMAT class attrs + _effective_seed instance attr set in submit(); generate() falls back to class name/'wav'/request.seed-or-0"
  - "Duration defaults within RESEARCH §3 band (planner discretion): Alphabet 75 s, Numbers 75 s, Colors 60 s, Animals 80 s, Bedtime pinned 120 s"
requirements-completed: []
duration: 2h 51m
completed: 2026-08-24T23:49:17Z
status: complete
coverage:
  - deliverable: "Deterministic end-to-end generation (same seed ⇒ byte-identical WAV)"
    verification:
      - kind: test
        ref: "tests/test_music_generation.py#TestMockBackend::test_generate_end_to_end_deterministic"
        status: pass
      - kind: test
        ref: "tests/test_music_generation.py#TestMockBackend::test_different_seeds_produce_different_bytes"
        status: pass
    human_judgment: false
  - deliverable: "Protocol conformance WITHOUT inheritance (isinstance true, MRO clean)"
    verification:
      - kind: test
        ref: "tests/test_music_generation.py#TestProtocolAndExceptions::test_mock_backend_isinstance_without_inheritance"
        status: pass
    human_judgment: false
  - deliverable: "Pydantic model surface: defaults, bounds, invalid-state ValidationError"
    verification:
      - kind: test
        ref: "tests/test_music_generation.py#TestMockBackend::test_model_defaults_and_validation"
        status: pass
    human_judgment: false
  - deliverable: "Category mapping locked table (Bedtime 66/F major/3/4/intro-scaffold/120s et al.)"
    verification:
      - kind: test
        ref: "tests/test_music_generation.py#TestCategoryMapping::test_bedtime_golden_values"
        status: pass
      - kind: test
        ref: "tests/test_music_generation.py#TestCategoryMapping::test_all_category_rows_match_research_table"
        status: pass
      - kind: test
        ref: "tests/test_music_generation.py#TestCategoryMapping::test_unknown_category_falls_back_to_generic_row"
        status: pass
    human_judgment: false
  - deliverable: "Caption authority delegated to audio bible (≤512 chars, keyword present, negative-prompt delegation)"
    verification:
      - kind: test
        ref: "tests/test_music_generation.py#TestCategoryMapping::test_caption_property_via_bible_builder"
        status: pass
      - kind: test
        ref: "tests/test_music_generation.py#TestCategoryMapping::test_music_negative_prompt_delegates_to_bible"
        status: pass
    human_judgment: false
  - deliverable: "Transport seam request shape + RESEARCH §2 error map at single choke point"
    verification:
      - kind: test
        ref: "tests/test_music_generation.py#TestTransportSeam (12 tests incl. 401/403→NotConfigured, URLError→BackendUnavailable, malformed JSON→GenerationFailed, header-leak guard)"
        status: pass
    human_judgment: false
  - deliverable: "generate() hardening: 1s→2s doubling backoff (cap x8), monotonic deadline, failed-terminal error text"
    verification:
      - kind: test
        ref: "tests/test_music_generation.py#TestGenerateOrchestration (patched _sleep/_monotonic seams, zero real waiting)"
        status: pass
    human_judgment: false
  - deliverable: "Constraint gates C1/C2/C4 (no image terms, no sqlite3, stdlib-only transport) + package import"
    verification:
      - kind: command
        ref: "! grep -qrE 'sqlite3|import requests' src/music_generation/ && ! grep -qrqi '\\bimage' src/music_generation/"
        status: pass
      - kind: command
        ref: "python3 -c 'import sys; sys.path.insert(0,\".\"); import src.music_generation'"
        status: pass
    human_judgment: false
  - deliverable: "Repo-root asset-catalog database byte-identical across suite runs"
    verification:
      - kind: command
        ref: "md5sum catalog.db before/after full suite == acfb604a75657e99b2682ce3c73ec65b"
        status: pass
    human_judgment: false
  - deliverable: "Full repo suite green offline (wave gate)"
    human_judgment: true
    rationale: "python3 -m pytest tests/ -q ran twice during execution: 1584 passed with 6 failures ALL pre-existing (story_engine catalog integration fails in isolation too; review_ui_generation passes 26/26 in isolation; zero references to music_generation; identical families present in the pre-change baseline run). Verifier should confirm no NEW failures vs .planning/phases/07-music-generation-backend-integration/deferred-items.md."
---

# Phase 7 Plan 01: Music Generation Core Layer Summary

**Provider-agnostic music-generation core: runtime-checkable backend protocol, typed exception taxonomy, locked category→parameter table anchored on the Phase 5 bible, stdlib transport seam with mapped errors, and a seed-deterministic mock proven end-to-end offline by 35 pytest cases.**

## Accomplishments

- **Tracer slice (Task 1, commit `cd42eb8b`)**: `MusicRequest`/`MusicStatus`/`MusicResult` Pydantic v2 models; `@runtime_checkable MusicGenerationBackend` Protocol with default submit→poll→download `generate()` loop that MockBackend satisfies **without inheritance**; typed exceptions (`NotConfigured`/`BackendUnavailable`/`GenerationFailed` under `MusicBackendError`) with raise-condition docstrings per RESEARCH §2; `MockBackend` synthesizing tiny structurally-valid RIFF/WAV payloads (44-byte canonical header, 8 kHz mono 16-bit PCM data structures — no audio rendering) with byte-identical same-seed determinism; `_sleep`/`_urlopen` seams.
- **Locked category mapping (Task 2, commit `2bef605e`)**: `CATEGORY_MUSIC_PARAMS` verbatim from RESEARCH §3 (Alphabet 110/C/4/4, Numbers 116/D/4/4, Colors 108/G/4/4 bridge scaffold, Animals 120/C/4/4, Bedtime 66/F major/3/4 `[instrumental intro]` scaffold pinned 120 s); case-insensitive `resolve_music_params` with slug-keyword generic fallback returning defensive copies; `build_music_request` resolves category duration only — caption authority stays with `src.audio_bible.prompts.build_music_prompt`; `music_negative_prompt` pure delegation to `category_negative`.
- **Transport + orchestration hardening (Task 3, commit `841808e2`)**: `_post_json`/`_get_json`/`_get_bytes` routing every call through the `_urlopen` seam with URL/method/headers/(5,30) timeout tuple; RESEARCH §2 error map at the single choke point; strict JSON-object decoding; `DEFAULT_TRANSPORT` with PINNED `post_json`/`get_json`/`get_bytes` attribute names for plan 07-02; hardened `generate()` with doubling backoff via `_sleep` (base→×8 cap), monotonic deadline via `_monotonic` (timeout_s=300, message names job id + elapsed), server error text carried on failed terminal states; Authorization values provably absent from exception messages (threat T7-01-I test).
- **Verification**: 35 offline tests across `TestMockBackend`, `TestCategoryMapping`, `TestProtocolAndExceptions`, `TestTransportSeam`, `TestGenerateOrchestration`; phase quick command <10 s (timeout budget 30 s); constraint gates C1–C4 grep-clean; `catalog.db` md5 unchanged across suite runs.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `issubclass` acceptance check impossible for runtime-checkable Protocols**
- **Found during:** Task 1 (RED phase)
- **Issue:** Plan acceptance criterion asserted `assert not issubclass(MockBackend, MusicGenerationBackend)`. On every supported Python, `issubclass()` against a `@runtime_checkable` Protocol is *structural* (member presence), so it returns True even with zero inheritance — the criterion could never pass and would misreport correct code as broken.
- **Fix:** Assert the actual intent via the MRO: `assert MusicGenerationBackend not in MockBackend.__mro__` alongside `isinstance(...)` being True.
- **Files modified:** tests/test_music_generation.py
- **Commit:** cd42eb8b

**2. [Rule 3 - Blocking] `_urlopen` bare alias conflicted with tuple-timeout contract**
- **Found during:** Task 3 implementation
- **Issue:** Task 1 defined `_urlopen = urllib.request.urlopen`, but Task 3's locked behavior requires the `(5, 30)` connect/read tuple to reach the seam — which stdlib urlopen rejects at production time (TypeError on tuple timeout). Literal alias + literal tuple = broken real network calls; dropping the tuple would violate the pinned seam contract that plan 07-02 fakes assert.
- **Fix:** `_urlopen(request, timeout)` became a tuple-aware wrapper preserving the seam signature and contract (fakes still see the tuple) while flattening connect+read to the single socket timeout stdlib supports.
- **Files modified:** src/music_generation/backends.py
- **Commit:** 841808e2

### Out-of-Scope Discoveries (logged, not fixed)

Full-suite runs surface failures in `tests/test_story_engine.py` (catalog integration; fail even in isolation) and `tests/test_review_ui_generation.py` (order-dependent; 26/26 pass in isolation). Both families pre-date this plan (present in the pre-change baseline), reference nothing from `src/music_generation`, and are recorded in `.planning/phases/07-music-generation-backend-integration/deferred-items.md`.

**Total deviations:** 2 auto-fixed (2× Rule 1/3 bug-blocker fixes above). **Impact:** none on design intent — both fixes preserve the LOCKED RESEARCH §2–§5 contracts exactly while keeping production paths valid; the issubclass fix corrects an untestable-as-written criterion.

## Authentication Gates

None — this plan is fully offline; no credentials or external services involved.

## Known Stubs

None. The mock backend's WAV synthesis is its specified production behavior (deterministic offline placeholder per RESEARCH §4/mock_backend precedent), not a placeholder-for-later.

## Notes for Plan 07-02

- Reuse the default orchestration loop via class-level assignment: `generate = MusicGenerationBackend.generate` (Protocol defaults are not inherited structurally).
- Consume `DEFAULT_TRANSPORT` as `self._transport.post_json/.get_json/.get_bytes` (names PINNED); inject fakes by monkeypatching module seam `src.music_generation.backends._urlopen` (records url/method/lowercased headers/data/timeout tuple).
- Set `BACKEND_NAME` ("ace-step"/"suno"), `AUDIO_FORMAT`, and `self._effective_seed` in `submit()` to populate `MusicResult` metadata.
- Error map is already centralized: connection-level → `BackendUnavailable`, 401/403 → `NotConfigured`, failed/malformed → `GenerationFailed`; never embed Authorization/header values in messages (T7-01-I, extended by T7-02-I for Bearer serialization).
- Env surface for adapters: `ACESTEP_API_KEY`, `ACESTEP_BASE_URL` (default `http://localhost:8001`), `MUSIC_BACKEND`.

## Self-Check: PASSED

All five created files exist on disk; commits `cd42eb8b`, `2bef605e`, `841808e2` verified in git log; `python3 -m pytest tests/test_music_generation.py -q` green (35 passed); package imports cleanly; constraint greps clean.
