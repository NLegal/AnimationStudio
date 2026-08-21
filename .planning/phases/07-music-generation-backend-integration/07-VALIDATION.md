---
phase: 7
slug: music-generation-backend-integration
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
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
| 07-01-01 | 01 | 1 | TBD | — | N/A | unit | `python -m pytest tests/test_music_generation.py -x -q` | ❌ W0 (created in task) | ⬜ pending |
| 07-01-02 | 01 | 1 | TBD | — | N/A | unit | `python -m pytest tests/test_music_generation.py::TestCategoryMapping -q` | ❌ W0 | ⬜ pending |
| 07-01-03 | 01 | 1 | TBD | — | N/A | unit (determinism) | `python -m pytest tests/test_music_generation.py::TestMockBackend -q` | ❌ W0 | ⬜ pending |
| 07-02-01 | 02 | 2 | TBD | T7-01 | Bearer token read from env only; never logged/serialized | contract (fake transport) | `python -m pytest tests/test_music_generation.py::TestAceStepAdapter -q` | ❌ W0 | ⬜ pending |
| 07-02-02 | 02 | 2 | TBD | T7-02 | No network in tests; errors mapped to typed exceptions | contract | `python -m pytest tests/test_music_generation.py::TestErrorMapping -q` | ❌ W0 | ⬜ pending |
| 07-02-03 | 02 | 2 | TBD | — | Suno stub refuses all operations | unit | `python -m pytest tests/test_music_generation.py::TestSunoStub -q` | ❌ W0 | ⬜ pending |
| 07-02-04 | 02 | 2 | TBD | — | CLI --dry-run performs zero network I/O | unit | `python -m pytest tests/test_music_generation.py::TestPhase7Cli -q` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*
*Requirement IDs are TBD (no REQUIREMENTS mapping for Phase 7); success criteria come from the ROADMAP Phase 7 goal.*

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

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
