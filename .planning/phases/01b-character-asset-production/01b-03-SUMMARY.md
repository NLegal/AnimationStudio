---
phase: 01b-character-asset-production
plan: 03
subsystem: generation_engine
tags: [comfyui, flux, workflow-templates, api-format, tdd]
requires:
  - phase: 01b-01
    provides: Merged expression/pose lists, lineage metadata
  - phase: 01b-02
    provides: Wired Review UI action handlers, configurable batch grids
provides:
  - 4 Flux-optimized API-format ComfyUI workflow JSON templates
  - Type-specific workflow template loading in ComfyUIBackend
  - 3-level fallback chain for workflow loading
  - 5 new workflow loading tests
affects:
  - src/generation_engine/comfy_backend.py — type-aware template loading
  - src/generation_engine/workflows/ — new workflow JSON files
  - tests/test_generation_engine.py — TestComfyUIWorkflowLoading test class
tech-stack:
  added: []
  patterns:
    - Type-specific workflow JSON per asset type
    - ComfyUI API-format workflow (numeric string keys, class_type + inputs only)
    - 3-level fallback chain: type-specific → legacy file → built-in default
key-files:
  created:
    - src/generation_engine/workflows/reference_sheet.json
    - src/generation_engine/workflows/expression.json
    - src/generation_engine/workflows/pose.json
    - src/generation_engine/workflows/outfit.json
  modified:
    - src/generation_engine/comfy_backend.py
    - tests/test_generation_engine.py
key-decisions:
  - "Flux-optimized params (cfg=3.5, empty negative, steps=25) in all workflow templates"
  - "1024x1024 for reference sheets and expressions; 768x1344 for poses and outfits"
  - "Backend accepts optional asset_type parameter — non-breaking change (default '')"
  - "3-level fallback: type-specific workflow JSON → legacy comfy_workflow.json → built-in _DEFAULT_WORKFLOW_TEMPLATE preserves backward compatibility"
requirements-completed:
  - CHAR-02
  - CHAR-03
  - CHAR-04
  - CHAR-05
coverage:
  - id: D1
    description: "4 Flux-optimized API-format ComfyUI workflow JSON templates"
    requirement: CHAR-02
    verification:
      - kind: unit
        ref: tests/test_generation_engine.py#TestComfyUIWorkflowLoading::test_load_expression_workflow
        status: pass
      - kind: unit
        ref: tests/test_generation_engine.py#TestComfyUIWorkflowLoading::test_load_reference_sheet_workflow
        status: pass
      - kind: unit
        ref: tests/test_generation_engine.py#TestComfyUIWorkflowLoading::test_load_pose_workflow
        status: pass
    human_judgment: false
  - id: D2
    description: "Type-specific workflow template loading with 3-level fallback chain"
    requirement: CHAR-03
    verification:
      - kind: unit
        ref: tests/test_generation_engine.py#TestComfyUIWorkflowLoading::test_load_fallback_on_unknown_type
        status: pass
      - kind: unit
        ref: tests/test_generation_engine.py#TestComfyUIWorkflowLoading::test_prompt_injection_into_loaded_workflow
        status: pass
    human_judgment: false
duration: 18min
completed: 2026-07-29
status: complete
---

# Phase 01b Plan 03: ComfyUI Workflow Templates — Summary

**Flux-optimized API-format ComfyUI workflow JSON templates for 4 asset types (reference sheet, expression, pose, outfit) with type-specific template loading in ComfyUIBackend**

## Performance

- **Duration:** 18 min
- **Started:** 2026-07-29T05:50:00Z
- **Completed:** 2026-07-29T06:08:00Z
- **Tasks:** 2 (1 auto, 1 TDD)
- **Files modified:** 6

## Accomplishments

- Created 4 Flux-optimized ComfyUI API-format workflow JSON templates (reference_sheet, expression, pose, outfit) in `src/generation_engine/workflows/`
- All workflows use Flux-optimized params: cfg=3.5, steps=25, euler/normal, empty negative prompt
- reference_sheet and expression use 1024x1024 (portrait/square); pose and outfit use 768x1344 (full-body ~9:16)
- Updated ComfyUIBackend with type-specific `_load_workflow_template(asset_type)` with 3-level fallback chain (type-specific → legacy file → built-in default)
- Updated `generate()`, `_build_workflow()`, `_generate_rest()`, `_generate_pycomfy()` to accept optional `asset_type` parameter
- Added 5 tests in TestComfyUIWorkflowLoading (TDD RED/GREEN cycle)
- All 241 tests pass (0 regressions)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create Flux API-format workflow JSON templates for all 4 asset types** - `65195e9` (feat)
2. **Task 2 (RED): Add failing test for type-specific workflow loading** - `ca2c69d` (test)
3. **Task 2 (GREEN): Implement type-specific workflow template loading** - `922bbef` (feat)

**Plan metadata:** (committed below)

## Files Created/Modified

### Created
- `src/generation_engine/workflows/reference_sheet.json` — Multi-angle reference sheet workflow (1024x1024, cfg=3.5, lily-reference prefix)
- `src/generation_engine/workflows/expression.json` — Expression portrait workflow (1024x1024, cfg=3.5, lily-expression prefix)
- `src/generation_engine/workflows/pose.json` — Full-body pose workflow (768x1344, cfg=3.5, lily-pose prefix)
- `src/generation_engine/workflows/outfit.json` — Outfit/wardrobe variant workflow (768x1344, cfg=3.5, lily-outfit prefix)

### Modified
- `src/generation_engine/comfy_backend.py` — Added `_WORKFLOW_DIR`, updated `_load_workflow_template(asset_type)`, `_build_workflow(input, asset_type)`, `generate(input, asset_type)`, `_generate_rest(input, asset_type)`, `_generate_pycomfy(input, asset_type)`
- `tests/test_generation_engine.py` — Added `TestComfyUIWorkflowLoading` with 5 tests

## Decisions Made

- **Flux-optimized params:** All workflow templates use cfg=3.5, steps=25, empty negative prompt per RESEARCH.md Pitfall 2. This is correct for Flux.1 Dev.
- **Dimension defaults:** 1024x1024 for reference sheets and expressions (square/portrait); 768x1344 for poses and outfits (portrait full-body ~9:16). Injected at runtime by `_build_workflow()`.
- **Backward compatibility:** The `asset_type` parameter defaults to `""` (empty string), so existing callers of `generate()`, `_build_workflow()`, etc. continue to work unchanged.
- **3-level fallback chain:** Type-specific workflow → `comfy_workflow.json` file → `_DEFAULT_WORKFLOW_TEMPLATE` built-in. This ensures that users can add a single `comfy_workflow.json` for all types, or individual type-specific files, or rely on the built-in default.

## Deviations from Plan

None — plan executed exactly as written.

## TDD Gate Compliance

✅ RED gate: `test(01b-03): add failing tests for type-specific ComfyUI workflow loading` — ca2c69d
✅ GREEN gate: `feat(01b-03): implement type-specific ComfyUI workflow template loading` — 922bbef
✅ No REFACTOR needed (implementation is clean and follows plan exactly)

## Verification Results

| Command | Result |
|---------|--------|
| `python3 -c "import json; ..."` — 4 workflow files valid JSON | ✅ PASS |
| `pytest tests/test_generation_engine.py::TestComfyUIWorkflowLoading -x -v` | ✅ 5 passed |
| `pytest tests/ --timeout=60 -x` | ✅ 241 passed |

## Self-Check: PASSED

All created workflow JSON files verified on disk. All commits confirmed via `git log`. All 241 tests pass.
