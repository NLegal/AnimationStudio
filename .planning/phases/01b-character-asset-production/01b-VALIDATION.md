---
phase: 01b
slug: character-asset-production
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-29
---

# Phase 01b — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 |
| **Config file** | pyproject.toml (tool.pytest.ini_options) |
| **Quick run command** | `pytest tests/ -x --timeout=30` |
| **Full suite command** | `pytest tests/ --timeout=60 -v` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x --timeout=30`
- **After every plan wave:** Run `pytest tests/ --timeout=60 -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01b-01 | 01 | 1 | CHAR-02 | T-01b-01 / — | N/A | unit | `pytest tests/test_prompt_builder.py::TestAssetTypeTemplates::test_reference_prompt -x` | ✅ | ⬜ pending |
| 01b-02 | 01 | 1 | CHAR-03 | T-01b-02 / — | N/A | unit | `pytest tests/test_prompt_builder.py::TestAssetTypeTemplates::test_expression_prompt -x` | ✅ | ⬜ pending |
| 01b-03 | 01 | 1 | CHAR-04 | T-01b-03 / — | N/A | unit | `pytest tests/test_prompt_builder.py::TestAssetTypeTemplates::test_pose_prompt -x` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_prompt_builder.py` — add test cases for merged expression list
- [ ] `tests/test_prompt_builder.py` — add test for `_known_expressions()` and `_known_poses()` returning correct merged sets
- [ ] `tests/test_asset_repository.py` — add test for lineage metadata field (D-18 compliance)
- [ ] `tests/test_generation_job.py` — add test for ComfyUIBackend integration (or mock verification)
- [ ] `tests/test_review_ui.py` — add test for grid size parameterization (D-16)

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| ComfyUI+Flux generated images pass identity scoring | CHAR-02/03/04/05 | Requires real GPU/ComfyUI instance with Flux models | Run generation pipeline, inspect scoring output CSV, verify >=90% DINOv2 consistency |
| Human review approval of generated assets | CHAR-02/03/04/05 | Subjective visual quality check | Open Review UI, verify batch grid display, approve/reject candidates |

*If none: "All phase behaviors have automated verification."*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
