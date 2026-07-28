---
phase: 1
slug: character-universe
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-28
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x + pytest-asyncio |
| **Config file** | pyproject.toml (in-project config) |
| **Quick run command** | `pytest -x --timeout=30` |
| **Full suite command** | `pytest -x -v --tb=short` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest -x --timeout=30`
- **After every plan wave:** Run `pytest -x -v --tb=short`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | 01 | 1 | CHAR-01 | T-1-01 / — | N/A | unit | `pytest tests/test_asset_repository.py::test_schema_creation -x` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | CHAR-02 | T-1-02 / — | N/A | unit | `pytest tests/test_prompt_builder.py::test_reference_prompt -x` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | CHAR-03 | T-1-03 / — | N/A | unit | `pytest tests/test_prompt_builder.py::test_expression_prompt -x` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | CHAR-04 | T-1-04 / — | N/A | unit | `pytest tests/test_prompt_builder.py::test_pose_prompt -x` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | CHAR-05 | T-1-05 / — | N/A | unit | `pytest tests/test_prompt_builder.py::test_outfit_prompt -x` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | CHAR-06 | T-1-06 / — | N/A | unit | `pytest tests/test_asset_repository.py::test_character_bio_schema -x` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | CHAR-07 | T-1-07 / — | N/A | unit | `pytest tests/test_training_engine.py::test_adapter_interface -x` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | CHAR-08 | T-1-08 / — | N/A | unit | `pytest tests/test_prompt_builder.py::test_negative_prompt_standard -x` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | CHAR-09 | T-1-09 / — | N/A | unit | `pytest tests/test_prompt_builder.py::test_age_variant_prompt -x` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | D-06 | T-1-10 / — | N/A | unit | `pytest tests/test_identity_engine.py::test_all_scores_computed -x` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | D-05 | T-1-11 / — | N/A | unit | `pytest tests/test_identity_engine.py::test_brand_score_weights -x` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | D-14 | T-1-12 / — | N/A | integration | `pytest tests/test_asset_repository.py::test_sqlite_crud -x` | ❌ W0 | ⬜ pending |
| TBD | 01 | 1 | D-09 | T-1-13 / — | N/A | unit | `pytest tests/test_generation_engine.py::test_backend_interface -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/conftest.py` — shared fixtures (mock DINOv2, CLIP, test images, SQLite in-memory)
- [ ] `tests/test_identity_engine.py` — DINOv2/CLIP scoring, Brand Score composite, all plugin interfaces
- [ ] `tests/test_generation_engine.py` — adapter interface compliance, mock backend
- [ ] `tests/test_asset_repository.py` — schema, CRUD, state transitions, character bio validation
- [ ] `tests/test_prompt_builder.py` — all prompt template types, negative prompt standards
- [ ] `tests/test_training_engine.py` — adapter interface compliance
- [ ] Framework install: `pip install pytest pytest-asyncio pytest-timeout` — if none detected

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
