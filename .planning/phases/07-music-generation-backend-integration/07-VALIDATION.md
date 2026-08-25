---
phase: 7
slug: music-generation-backend-integration
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: false
created: 2026-08-21
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest >=8.0 (`asyncio_mode=auto`, `timeout=30`) |
| **Config file** | `pyproject.toml` `[tool.pytest.ini_options]` |
| **Quick run command** | `python -m pytest tests/test_music_generation.py -x -q` |
| **Full suite command** | `python -m pytest tests/ -q` |
| **Estimated runtime** | ~15 s (phase tests) / ~120 s (full suite) |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_music_generation.py -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -q`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | P01-T1 MockBackend deterministic byte-identical same-seed WAV offline | — | N/A (no secrets in mock) | unit | `python -m pytest tests/test_music_generation.py::TestMockBackend -x -q` | ✅ (created in task) | ✅ green |
| 07-01-02 | 01 | 1 | P01-T3 Category parameters resolve per locked RESEARCH §3 table | — | N/A | unit | `python -m pytest tests/test_music_generation.py::TestCategoryMapping -q` | ✅ | ✅ green |
| 07-01-03 | 01 | 1 | P01-T2 Protocol runtime-checkable (isinstance, no inheritance) + P01-T5 tests green offline <30s, zero network I/O | — | N/A | unit (determinism) | `python -m pytest tests/test_music_generation.py::TestMockBackend -q && python -m pytest tests/test_music_generation.py -q` | ✅ | ✅ green |
| 07-02-01 | 02 | 2 | P02-T2 AceStep REST contract: Bearer auth (ctor>env), caption≤512, lyrics≤4096, payload golden values | T7-01 / T7-02 | Bearer token read from env/constructor only; never logged/serialized; header values absent from exception messages | contract (fake transport) | `python -m pytest tests/test_music_generation.py::TestAceStepAdapter -q` | ✅ | ✅ green |
| 07-02-02 | 02 | 2 | P02-T3 Locked error map end-to-end: connection→BackendUnavailable, 401/403→NotConfigured, failed/malformed→GenerationFailed; P02-T1 get_backend registry env resolution | T7-01 / T7-02 | No network in tests; errors mapped to typed exceptions; token never leaks (test_token_never_leaks) | contract | `python -m pytest tests/test_music_generation.py::TestErrorMapping -q` | ✅ | ✅ green |
| 07-02-03 | 02 | 2 | P02-T4 SunoBackend is_configured False, all ops raise NotConfigured; wrapper experimental + unreachable via registry | — | Suno stub refuses all operations; zero HTTP code in module | unit | `python -m pytest tests/test_music_generation.py::TestSunoStub -q` | ✅ | ✅ green |
| 07-02-04 | 02 | 2 | P02-T5 generate_phase7.py --dry-run prints request JSON, zero network I/O, exit 0 | — | CLI --dry-run performs zero network I/O (fail-loud guards on all transport seams) | unit (smoke) | `python -m pytest tests/test_music_generation.py::TestPhase7Cli -q` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*
*Requirement IDs sourced from PLAN must_haves (no REQUIREMENTS.md mapping for Phase 7); success criteria come from ROADMAP Phase 7 goal.*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements.* pytest is installed and
configured; `tests/conftest.py` exists; fake HTTP transports are plain callables/
monkeypatches requiring no extra fixtures beyond what Plan 01 creates inside
`tests/test_music_generation.py`.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live ACE-Step song generation end-to-end (submit→poll→download→audible WAV) | ROADMAP Phase 7 goal | Requires local ACE-Step Studio service + GPU; CI stays offline | Start ACE-Step locally (`localhost:8001`), set `ACESTEP_API_KEY`, run `python scripts/generate_phase7.py --backend ace-step --category Bedtime --topic "sleepy moon" `, confirm WAV file plays and job logs show completed status |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-08-25

---

## Validation Audit 2026-08-25

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 7/7 |
| Escalated | 0 |

All 7 verification map rows have corresponding automated test classes in
`tests/test_music_generation.py` (86 tests total, all passing offline in ~3.5 s).
Requirement IDs populated from PLAN must_haves; threat references added for rows
07-02-01 (T7-01/T7-02 — bearer auth handling) and 07-02-02 (T7-01/T7-02 — error
map + token leak prevention). Manual-only verification (live ACE-Step smoke)
retained as documented checklist in `Audio/Music/README.md`.

Constraint gates verified:
- C1 — no image terms in `src/music_generation/` or `scripts/generate_phase7.py`
- C2 — no `sqlite3` imports; `catalog.db` md5 `acfb604a75657e99b2682ce3c73ec65b` unchanged
- C3 — all tests use fake transports; no network I/O possible in suite
- C4 — stdlib-only transport (`import requests` grep-clean)

VERIFICATION.md score: 10/10 truths verified, 9/9 artifacts verified, 6/6
key links verified, 2/2 requirements (MUSC-01, MUSC-02) satisfied.
