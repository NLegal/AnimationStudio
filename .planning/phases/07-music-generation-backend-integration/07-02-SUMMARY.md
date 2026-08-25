---
phase: 07-music-generation-backend-integration
plan: 02
subsystem: music-generation
tags: [music, ace-step, suno-stub, backend-registry, cli, offline-first, error-mapping]
requires:
  - src/music_generation/backends.py plan-01 seams (DEFAULT_TRANSPORT pinned post_json/get_json/get_bytes, _sleep/_monotonic/_urlopen, exception taxonomy, resolve_music_params)
  - src/audio_bible/prompts.py (build_music_prompt caption authority)
provides:
  - AceStepBackend (src/music_generation/ace_step.py) — locked REST adapter: POST /v1/music/generate, GET /v1/jobs/{id}, GET /v1/audio?path=<encoded>, Bearer auth (ctor arg > ACESTEP_API_KEY), health probe with root fallback on 404-only
  - SunoBackend refusing stub + SunoWrapperBackend experimental/default-disabled (src/music_generation/suno.py), zero HTTP code in module
  - _BACKENDS lazy-hook registry + get_backend(name=None) factory honoring MUSIC_BACKEND env with safe "mock" default (backends.py)
  - Completed package exports incl. AceStepBackend/SunoBackend/SunoWrapperBackend/get_backend/build_music_request
  - scripts/generate_phase7.py CLI (--backend/--category/--topic/--seed/--out/--dry-run; dial-free dry-run; mock real-mode; typed-failure exit 1)
  - Audio/Music/README.md — env table, precedence, error taxonomy, MANUAL live-smoke checklist
affects:
  - Phase 8 wiring points: pipeline MUSIC_BACKEND resolution, Review UI hooks, Colab notebook (all consume get_backend + MusicRequest/Result surface unchanged)
tech-stack:
  added: []
  patterns:
    - adapter-side _typed_transport_call normalization so injected fakes raising raw URLError/HTTPError surface the same locked map as the real seam
    - registry as dict of LAZY import hooks (circular-import guard); wrapper deliberately unregistered (assumption-delta invariant)
    - fail-loud no-dial guards installed on seam functions AND DEFAULT_TRANSPORT attributes prove CLI dry-run is dial-free
    - health-probe degradation matrix: NotConfigured→False immediately; BackendUnavailable→False immediately; only endpoint-missing/malformed falls back to root probe
key-files:
  created:
    - src/music_generation/ace_step.py
    - src/music_generation/suno.py
    - scripts/generate_phase7.py
    - Audio/Music/README.md
  modified:
    - src/music_generation/backends.py
    - src/music_generation/__init__.py
    - tests/test_music_generation.py
key-decisions:
  - "Error map enforced at BOTH layers: plan-01 seam mapping retained plus adapter-side normalization so fake transports raising raw urllib errors produce identical typed exceptions (behavior rows demand URLError->BackendUnavailable through backend.submit/generate)"
  - "Health probe falls back to root GET ONLY when /v1/jobs/health is missing/malformed (404-class); connection-level failures and auth rejections degrade to False without a second probe"
  - "Content-type validation degrades to best-effort warning through the pinned bytes-only transport surface — audio bytes accepted as opaque binary exactly per threat T7-02-T mitigation"
  - "build_music_request re-exported from package __init__ completing the public surface the CLI consumes"
  - "Root README.md untouched — all music documentation lives under Audio/Music/ per repo convention (scoping call recorded per plan output note)"
requirements-completed: []
duration: 2h 2m
completed: 2026-08-25T04:41:38Z
status: complete
coverage:
  - deliverable: "get_backend resolves ace-step/suno/mock; MUSIC_BACKEND default; unknown raises listing choices"
    verification:
      - kind: test
        ref: "tests/test_music_generation.py#TestAceStepAdapter::test_registry_resolves_ace_step_and_mock"
        status: pass
      - kind: test
        ref: "tests/test_music_generation.py#TestErrorMapping::test_get_backend_honors_music_backend_env + test_get_backend_defaults_to_mock_without_env + test_unknown_name_raises_listing_valid_choices"
        status: pass
    human_judgment: false
  - deliverable: "AceStepBackend locked REST contract end-to-end over scripted fake transport (URLs, Bearer ctor>env, payload golden values, caps, seed echo)"
    verification:
      - kind: test
        ref: "tests/test_music_generation.py#TestAceStepAdapter (21 tests incl. happy path, bearer resolution order, Bedtime golden payload, lyrics override cap, caption truncation)"
        status: pass
    human_judgment: false
  - deliverable: "Locked error map end-to-end: URLError→BackendUnavailable, 401/403→NotConfigured, failed/malformed/deadline→GenerationFailed naming job id+elapsed"
    verification:
      - kind: test
        ref: "tests/test_music_generation.py#TestErrorMapping::test_deadline_expiry_names_job_id_and_elapsed (+8 further matrix tests)"
        status: pass
    human_judgment: false
  - deliverable: "Suno refusal stub (locked message from all four entry points) + experimental wrapper unreachable via registry"
    verification:
      - kind: test
        ref: "tests/test_music_generation.py#TestSunoStub (7 tests incl. registry invariant and no-HTTP-code source guard)"
        status: pass
    human_judgment: false
  - deliverable: "Token never leaks into exceptions or logs across the full failure matrix (threat T7-02-I)"
    verification:
      - kind: test
        ref: "tests/test_music_generation.py#TestErrorMapping::test_token_never_leaks"
        status: pass
  - deliverable: "CLI dry-run prints request JSON with provably zero dials (guards never trip); exit 0 without credentials; generic fallback works"
    verification:
      - kind: test
        ref: "tests/test_music_generation.py#TestPhase7Cli (7 tests incl. fail-loud triple-guard + DEFAULT_TRANSPORT attribute guards)"
        status: pass
      - kind: command
        ref: "python3 scripts/generate_phase7.py --dry-run --category Bedtime --topic 'sleepy moon' → exit 0, stdout parses as JSON, duration_s==120"
        status: pass
    human_judgment: false
  - deliverable: "Mock real-mode writes valid RIFF WAV under --out; suno exits 1 with refusal on stderr, no traceback; unknown backend lists choices"
    verification:
      - kind: test
        ref: "tests/test_music_generation.py#TestPhase7Cli::test_real_mode_mock_writes_wav_and_summary (+suno refusal +unknown backend tests)"
        status: pass
    human_judgment: false
  - deliverable: "Docs carry C5 env table, error taxonomy, numbered manual live-smoke checklist with exact VALIDATION smoke command"
    verification:
      - kind: command
        ref: "Audio/Music/README.md exists (4430 bytes) containing all three env vars, taxonomy table, checklist steps 1–5 incl. exact smoke command"
        status: pass
    human_judgment: true
    rationale: "Doc content checked by grep/read during execution rather than an automated assertion; verifier should spot-check the checklist matches 07-VALIDATION.md row wording."
  - deliverable: "Constraint gates C1/C2/C4 + repo-root catalog.db byte-identical across suite runs"
    verification:
      - kind: command
        ref: "! grep -rqiE '\\bimage' src/music_generation/ scripts/generate_phase7.py && ! grep -qrE 'sqlite3|import requests' src/music_generation/ scripts/generate_phase7.py"
        status: pass
      - kind: command
        ref: "md5sum catalog.db before/after full suites == acfb604a75657e99b2682ce3c73ec65b"
        status: pass
      - kind: command
        ref: "python3 -m pytest tests/ -q → 1636 passed; only failures are the 5 pre-existing story_engine catalog tests recorded in deferred-items.md (zero music_generation references; present in pre-Phase-7 baseline)"
        status: pass
    human_judgment: true
    rationale: "Full-suite greenness judged against the documented baseline: 5 failed are the exact deferred-items family (fail in isolation too); the previously flaky review_ui file passed this round. No NEW failures attributable to plan 07-02."
---

# Phase 7 Plan 02: Real Adapters, Registry, CLI & Live-Smoke Docs Summary

**Production ACE-Step 1.5 REST adapter speaking the locked contract over an injectable transport, a loud-refusing Suno stub plus default-disabled experimental wrapper, env-driven `get_backend` registry with safe mock default, a provably dial-free `--dry-run` CLI, and operator docs carrying the one manual live-smoke checklist — all evidenced offline by 51 new pytest cases.**

## Accomplishments

- **Tracer slice (Task 1, commits `e0816826` RED + `b6543871` GREEN)**: `AceStepBackend` duck-typing the protocol via `generate = MusicGenerationBackend.generate`; submit composes bible-authoritative captions (`build_music_prompt`, hard-truncated 512) and category-scaffold lyrics (marker regex join, truncated 4096) into the verbatim RESEARCH §2 payload (audio_duration/bpm/key_scale/time_signature/seed/thinking=False/model); poll passes status strings straight to `MusicStatus.state` with progress defaults (0.0 pending / 1.0 completed), carries failed-server text, remembers audio paths under `audio_path`/`path`/`output`; download percent-encodes the remembered path into `GET {base}/v1/audio?path=…`, performing one poll first if needed; credential resolution constructor > `ACESTEP_API_KEY`, base URL constructor > `ACESTEP_BASE_URL` > `http://localhost:8001`, model validated against turbo|sft; `_BACKENDS` lazy-hook registry + `get_backend(name=None)` with `MUSIC_BACKEND` env fallback and unknown-name error listing valid choices.
- **Failure surface (Task 2, commits `44a68dd6` RED + `8b1ca711` GREEN)**: full LOCKED §2 matrix proven through the real adapter via `_typed_transport_call` normalization (raw `URLError`→`BackendUnavailable`, `HTTPError` 401/403→`NotConfigured`, everything else mapped identically to the seam); malformed/non-dict bodies and unknown status strings wrap as `GenerationFailed`; deadline expiry names job id + elapsed; `SunoBackend` refuses from all four entry points with the verbatim locked citation; `SunoWrapperBackend(SunoBackend)` flagged `EXPERIMENTAL = True` with the disabled-by-default suffix and deliberately absent from the registry (invariant tested for both direct and env-driven resolution); `test_token_never_leaks` sweeps every scenario's raised reprs AND captured log records for the dummy key.
- **CLI + docs (Task 3, commit `6c962767`)**: `scripts/generate_phase7.py` mirrors the generate_phase5 skeleton (shebang, Reproduction block showing BOTH offline dry-run and live smoke commands, sys.path bootstrap, argparse help style, boolean exit contract wired through `sys.exit(main())`); dry-run prints resolved-request JSON with zero backend construction; real mode writes `<category>-<topic-slug>-<seed>.wav` under `--out` only and prints the backend/job/bytes/path summary; `MusicBackendError` subclasses exit 1 with stderr message, no traceback spill. `Audio/Music/README.md` joins the AUDIO_BIBLE doc family: quickstart per mode, C5 environment table, flag>env>mock precedence, operator-facing error taxonomy table, determinism note, and the five-step MANUAL live-smoke checklist transcribed from 07-VALIDATION.md (CI/pytest never require the service).
- **Verification**: module suite 86 passed (<5 s); TestAceStepAdapter 21, TestErrorMapping 10, TestSunoStub 7, TestPhase7Cli 7 new cases; direct `--dry-run` invocation parses as JSON with duration_s==120; C1/C2/C4 greps clean; `catalog.db` md5 byte-identical across two full-suite runs.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Golden-payload test built its request bypassing category duration resolution**
- **Found during:** Task 1 GREEN
- **Issue:** The test constructed bare `MusicRequest(category="Bedtime", …)` whose default `duration_s=60`, then asserted the adapter sent 120 — but the adapter's locked contract is `audio_duration == request.duration_s` (resolution belongs to `build_music_request`). Test expectation contradicted the documented data flow.
- **Fix:** Test now builds the request via `build_music_request("Bedtime", …)` (the production composition path) and asserts `request.duration_s == 120` first.
- **Files modified:** tests/test_music_generation.py
- **Commit:** b6543871

**2. [Rule 1 - Bug] Health-probe root fallback fired on connection failures**
- **Found during:** Task 1 GREEN
- **Issue:** First implementation fell back to the root probe on ANY non-auth `MusicBackendError` — including `BackendUnavailable`. Plan language scopes the root fallback to "if that 404s"; probing again after a connection refusal wastes the timeout budget and misreports unreachable services.
- **Fix:** `is_configured()` now returns False immediately on `NotConfigured` (auth rejection) and `BackendUnavailable` (connection failure); only endpoint-missing/malformed responses (`GenerationFailed` class) trigger the single root-probe fallback.
- **Files modified:** src/music_generation/ace_step.py
- **Commit:** b6543871

**3. [Rule 3 - Blocking] `build_music_request` not importable from the package root**
- **Found during:** Task 3
- **Issue:** Plan 01 shipped `build_music_request` in `backends.py` but never re-exported it from `src/music_generation/__init__.py`; the CLI consumes it as part of "the public surface" (Task 3 read_first names it explicitly).
- **Fix:** Added `build_music_request` to the package imports and `__all__`.
- **Files modified:** src/music_generation/__init__.py
- **Commit:** 6c962767

### Interpretation Notes (not defects)

- **Content-type check via bytes-only transport:** the pinned `get_bytes` surface returns bare bytes with no headers, so the action's "log-and-continue if content-type is not audio/*" is implemented best-effort — a warning fires only when the transport object exposes headers (richer fakes); plain-bytes transports accept opaque binary, exactly the threat T7-02-T mitigation ("audio bytes accepted as opaque binary with content-type warning only"). Covered by design review; no behavior row required it.
- **Registry MUSIC_BACKEND handling landed with the tracer** (Task 1 GREEN) because the factory signature includes it; Task 2 contributed the dedicated env-resolution tests rather than new production code.

### Out-of-Scope Discoveries (logged, not fixed)

Unchanged from 07-01: the same 5 pre-existing `tests/test_story_engine.py` catalog-integration failures appear in full-suite runs (they fail in isolation too and reference nothing from `src/music_generation`); they remain recorded in `.planning/phases/07-music-generation-backend-integration/deferred-items.md`. This round the previously-flaky `tests/test_review_ui_generation.py` passed under full-suite ordering.

**Total deviations:** 3 auto-fixed (2× Rule 1 test/design corrections, 1× Rule 3 public-surface completion). **Impact:** none on the LOCKED RESEARCH §2–§5 contracts — all fixes align implementation/tests with the already-locked behavior.

## Authentication Gates

None — fully offline plan; the ACE-Step live smoke is documented as a manual checklist, never executed here by design.

## Known Stubs

None. `SunoBackend` is a specified refusal stub (its production behavior IS refusing loudly per RESEARCH §4 / COVERAGE.md Surface 2 opt-out), not a placeholder-for-later; `SunoWrapperBackend` is a documented integration point that is intentionally default-disabled.

## Notes for Phase 8

- Wire pipelines through `get_backend(None)` so `MUSIC_BACKEND` drives selection with the safe `mock` default; construct `requests` via `build_music_request(category, topic, seed=…)`.
- `MUSIC_BACKEND=mock` makes the whole pipeline runnable offline/deterministic (same seed ⇒ byte-identical WAV).
- `SunoBackend` raising `NotConfigured` is the expected UX for any Suno-routed job; catch `MusicBackendError` subclasses at job level for status surfacing.
- The manual live-smoke checklist (Audio/Music/README.md) remains the ONLY real-audio step; nothing in CI generates audio.

## Self-Check: PASSED

All four created files exist on disk (`ace_step.py`, `suno.py`, `generate_phase7.py`, `Audio/Music/README.md`); three modified files verified in git; commits `e0816826`, `b6543871`, `44a68dd6`, `8b1ca711`, `6c962767` verified in git log; `python3 -m pytest tests/test_music_generation.py -q` green (86 passed); direct CLI dry-run exits 0 parsing as JSON with duration_s 120; constraint greps clean; catalog.db md5 unchanged.
