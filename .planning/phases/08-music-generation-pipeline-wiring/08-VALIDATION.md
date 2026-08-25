---
phase: 8
slug: music-generation-pipeline-wiring
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-08-22
---

# Phase 8 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 (`asyncio_mode=auto`, `testpaths=["tests"]`, per-test timeout 30 s) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `python3 -m pytest tests/test_generate_phase5.py tests/test_review_ui_music.py tests/test_music_generation.py -x -q` |
| **Full suite command** | `python3 -m pytest tests/ -q` (~152 s) |
| **Estimated runtime** | ~20 s (phase tests) / ~152 s (full suite) |

**Baseline note:** full suite is 1550 passed / 5 pre-existing failures in `tests/test_story_engine.py` (local `catalog.db` state; they skip when DB absent). Unrelated to music generation — plans must claim "green except the 5 known story-engine catalog failures", never a naive "100% green".

---

## Sampling Rate

- **After every task commit:** Run quick command above (< 30 s target)
- **After every plan wave:** Run `python3 -m pytest tests/ -q`
- **Before `/gsd-verify-work`:** Full suite must be green modulo the 5 known story-engine failures
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

Task IDs below are the anticipated mapping (Phase 8 has two plans, sequential). Plans must align task IDs to this table or update it in the same commit.

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 08-01-01 | 01 | 1 | ROADMAP goal (generation mode) | T8-01 | slugified filename components; no path traversal | unit | `python3 -m pytest tests/test_generate_phase5.py -x -q` | ✅ | ✅ green |
| 08-01-02 | 01 | 1 | batch loop + file layout | T8-02 | catalog.db byte-identity before/after suite | integration (MockBackend) | `python3 -m pytest tests/test_generate_phase5.py::TestBatchGeneration -q` | ✅ | ✅ green |
| 08-01-03 | 01 | 1 | manifest schema + atomic write + resume | T8-02 | manifest records seed/job_id/backend, never keys/headers | golden/unit | `python3 -m pytest tests/test_generate_phase5.py::TestManifest -q` | ✅ | ✅ green |
| 08-02-01 | 02 | 2 | `/music` page + nav link | — | N/A (unauthenticated single-operator, matches existing routes) | unit (TestClient) | `python3 -m pytest tests/test_review_ui_music.py -x -q` | ✅ | ✅ green |
| 08-02-02 | 02 | 2 | `POST /music/prompt` pure preview | T8-03 | fail-loud transport guards never trip on preview | unit (TestClient) | `python3 -m pytest tests/test_review_ui_music.py::TestMusicPrompt -q` | ✅ | ✅ green |
| 08-02-03 | 02 | 2 | `POST /music/generate` job lifecycle + `GET /api/music/jobs` | T8-04 | suno selection → failed job, not HTTP 500; single-song submits cap DoS | integration (injected mock backend) | `python3 -m pytest tests/test_review_ui_music.py::TestMusicGenerate -q` | ✅ | ✅ green |
| 08-02-04 | 02 | 2 | notebook JSON validity + PHASE5_STATUS accuracy | — | notebook shells only at tested targets | structural + report-mode run | `python3 -c "import json;json.load(open('colab/AnimationStudio_Colab_Phase5.ipynb'))" && python3 scripts/generate_phase5.py` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*
*Requirement IDs are TBD (no REQUIREMENTS mapping for Phase 8); success criteria come from the ROADMAP Phase 8 goal.*

---

## Wave 0 Requirements

- [x] `tests/test_generate_phase5.py` — does not exist yet (script currently untested); stubs created inside owning tasks
- [x] `tests/test_review_ui_music.py` — new file for UI hook tests
- [x] Framework install: none — infra complete

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live ACE-Step song generation end-to-end via CLI batch mode (`--generate --backend ace-step --category Bedtime`) produces audible WAV + manifest entry | ROADMAP Phase 8 goal | Requires local ACE-Step Studio service + GPU; CI stays offline | Start ACE-Step locally (`localhost:8001`), set `ACESTEP_API_KEY`, run `python3 scripts/generate_phase5.py --generate --backend ace-step --category Bedtime --topic "sleepy moon"`; confirm the flat-layout file `Audio/Music/bedtime-sleepy-moon-<seed>.wav` plays and manifest.json gains one entry (file layout per RESEARCH D1 / plan 08-01); extend Audio/Music/README.md live-smoke checklist with this command |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated (2026-08-25)

---

## Validation Audit 2026-08-25

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

**Result:** All 7 tasks verified — automated commands exist, test files exist, tests pass green (33 + 25 = 58 phase tests). Structural notebook check passes. Report-mode C4 compat confirmed. Manual-only: live ACE-Step smoke (1 row). No new test files generated.
