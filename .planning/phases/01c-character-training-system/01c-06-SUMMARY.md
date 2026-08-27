---
phase: 01c-character-training-system
plan: 06
subsystem: training
tags: [colab, jupyter-notebook, kohya-sd-scripts, flux, lora, accelerate, huggingface, diffusers]

# Dependency graph
requires:
  - phase: 01c-05
    provides: scripts/train_lora.py offline orchestrator (build-dataset / train dry-run / benchmark / versions)
provides:
  - Operator-ready Colab training notebook (11 sections, Phase 4 pattern) for FLUX.1-dev LoRA runs on T4/A100 with VRAM profiles
  - Offline structural smoke suite enforcing notebook invariants + secret-shape guard across all 7 colab notebooks
  - README Character Training runbook: local dry-run evidence chain, operator prerequisites, VRAM profile table, deferred-human note
affects: [phase-4-visual-generation, character-training-followups, verify-work-uat]

# Tech tracking
tech-stack:
  added: [no project deps (C-NODEP); notebook targets ephemeral Colab: kohya sd-scripts pinned @37a1cbbc, accelerate, diffusers, huggingface_hub]
  patterns:
    - Phase-4-mirror notebook pattern (#@title numbered cells, #@param settings forms, run() argv helper, git_sync._basic_auth_header push)
    - VRAM profile selector (a100-24g / t4-16g / t4-12gb-swap16) with compute-capability-driven fp8 fallback (Pitfall 6)
    - Pinned third-party clone (sd-scripts checked out at explicit upstream commit hash)
    - Offline notebook smoke tests: JSON parse + structural markers + secret-shape regex scan, zero execution (C-OFFLINE)

key-files:
  created:
    - colab/AnimationStudio_Colab_Training.ipynb
    - tests/test_colab_notebooks.py
  modified:
    - README.md

key-decisions:
  - "Artifacts kept inside the repo tree (Universe/Characters/Lily Bunny/lora/ + training/) so the sync cell commits safetensors + benchmark report + registry directly (no Drive upload; Universe ships via git)"
  - "sd-scripts pinned to verified upstream main SHA 37a1cbbc5725ed2a3575506e7bd2001c9908ac92 (2026-07-23) — supply-chain pin per T-01c-06b"
  - "Model files sourced from verified HF repos: flux1-dev.safetensors + ae.safetensors from black-forest-labs/FLUX.1-dev (gated), clip_l + t5xxl_fp16 from comfyanonymous/flux_text_encoders (ungated)"
  - "fp8_base auto-forced when compute capability < 8 regardless of selected VRAM profile (Turing bf16 emulation, NaN-trap avoidance)"
  - "Settings form params fixed to #@param (no space) so Colab renders the form; tokens are empty-string placeholders enforced by CI secret-shape scan"

patterns-established:
  - "Notebook-runbook contract: smoke tests assert structural markers AND README runbook presence, so notebook drift breaks CI"
  - "Deferred-human evidence package: local dry-run chain (01c-05) + executable notebook + README handoff = verification_deferred_human for CHAR-07 criterion 2"
  - "Secret hygiene: runtime-only token params; negative scan for ghp_/hf_/xox/AKIA/sk- shapes across every committed notebook"

requirements-completed: [CHAR-07]

coverage:
  - id: D1
    description: "Colab training notebook structure contract enforced by smoke suite (nbformat-4, all 11 sections, empty token params, GPU fail-fast, pinned sd-scripts, accelerate/benchmark/promote/sync stages, next-steps)"
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: "tests/test_colab_notebooks.py#TestNotebookStructuralValidity"
        status: pass
      - kind: unit
        ref: "tests/test_colab_notebooks.py#TestTrainingNotebookStructure"
        status: pass
      - kind: unit
        ref: "tests/test_colab_notebooks.py#TestSecretShapeGuard"
        status: pass
    human_judgment: false
  - id: D2
    description: "README Character Training runbook (local dry-run chain, operator prerequisites, VRAM profiles, deferred-human note)"
    requirement: CHAR-07
    verification:
      - kind: unit
        ref: "tests/test_colab_notebooks.py#TestReadmeRunbook"
        status: pass
    human_judgment: false
  - id: D3
    description: "Operator execution of the notebook on a Colab GPU producing lily-bunny_v1.0.safetensors + benchmark report (CHAR-07 criterion 2, locked deferred-human path)"
    requirement: CHAR-07
    verification: []
    human_judgment: true
    rationale: "Requires a physical GPU operator action on Colab (T4/A100) with gated-model tokens — no build-environment GPU exists; the notebook + dry-run chain (01c-05) are the complete evidence package awaiting operator execution"

# Metrics
duration: 96min
completed: 2026-08-27
status: complete
---

# Phase 01c Plan 06: Colab Training Notebook Summary

**Operator-ready Colab LoRA training notebook (Phase 4 pattern, 11 sections) with VRAM profiles for T4/A100 Flux runs, offline structural smoke tests with a secret-shape guard over all 7 colab notebooks, and a README runbook documenting the local dry-run → Colab-execution handoff**

## Performance

- **Duration:** 96 min
- **Started:** 2026-08-27T11:22:03Z
- **Completed:** 2026-08-27T12:57:35Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- `colab/AnimationStudio_Colab_Training.ipynb` — nbformat-4, thin-phase-mirrored Phase 4 skeleton, 9 code + 2 markdown cells: Settings (#@param, empty token placeholders) → GPU fail-fast → clone/pin sd-scripts @37a1cbbc → 4 gated model downloads → `train_lora.py build-dataset` → `accelerate launch flux_train_network.py` (networks.lora_flux, fp8_base, blocks_to_swap) → 8-sample diffusers generation + `LoRABenchmark`/`IdentityScorerProvider(light=False)` (gate ≥ 0.90 @ full coverage) → registry register/promote → `git_sync._basic_auth_header` push of safetensors + benchmark report + registry.
- `tests/test_colab_notebooks.py` — 61 offline assertions: structural validity + clean execution state across all 7 notebooks, training-notebook content contract, secret-shape guard, README runbook contract. Zero network, zero notebook execution (C-OFFLINE).
- `README.md` — Character Training (Phase 1c) section: local evidence chain table, operator prerequisites, notebook pointer, VRAM profile table, Review-UI promotion prerequisite, `verification_deferred_human` note.
- Full suite: 1833 passed, 5 pre-existing failures in `tests/test_story_engine.py` (universe catalog empty set — C-CATALOGDB known state, out of scope, logged to deferred-items.md).

## Task Commits

Each task was committed atomically:

1. **Task 1: Build the Colab training notebook** - `75e6e295` (feat), `a964abf9` (fix: sample-gen alignment with plan action prose)
2. **Task 2: Notebook smoke tests + README runbook** (TDD) - `2c48d90d` (test RED), `502baeb9` (feat GREEN), `61e4b811` (test: widen deferred-human marker assertion)

_Note: TDD task had multiple commits (test → feat → test-refinement) — RED gate `2c48d90d` failed on the README assertions only (57 notebook/structure assertions passed immediately validating the Task 1 artifact); GREEN `502baeb9` made the suite 61/61._

## Files Created/Modified
- `colab/AnimationStudio_Colab_Training.ipynb` - Operator-ready training notebook (11 sections, VRAM profiles, empty-token settings, pinned sd-scripts)
- `tests/test_colab_notebooks.py` - Offline smoke suite: structural validity + training markers + secret-shape guard + README contract
- `README.md` - Character Training (Phase 1c) runbook section

## Decisions Made
- Artifacts live inside the repo tree (`Universe/Characters/Lily Bunny/lora/` + `training/`) so the sync cell commits safetensors + benchmark report + registry directly — no Drive upload step (A6 verified: Universe ships via git).
- sd-scripts pinned to verified real upstream SHA `37a1cbbc` (main @ 2026-07-23, confirmed via GitHub API) — reproducibility trade documented with bump procedure in notebook comments.
- HF sources verified against the Hub API: `flux1-dev.safetensors`/`ae.safetensors` from gated `black-forest-labs/FLUX.1-dev`; `clip_l.safetensors`/`t5xxl_fp16.safetensors` from ungated `comfyanonymous/flux_text_encoders`.
- fp8_base auto-forced when compute capability < 8 (Pitfall 6): Turing bf16 is emulated and fp16 NaNs on Flux; the t4-16g profile is the notebook default.
- Benchmark evaluates all 8 generated samples; promote runs only when `result.passed` (composite ≥ 0.90 AND weight_coverage ≥ 1.0).
- Settings form uses `#@param` (adjacent) — a `# @param` spacing defect was caught during build validation and fixed before the first commit (Colab would otherwise silently skip form rendering).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Alignment] Sample-generation cell did not match plan action prose**
- **Found during:** Task 1 close-out (full PLAN.md Tasks section read after initial commit)
- **Issue:** The plan's Cell 7 action specifies N=8 samples saved under the dataset output tree; the initial build generated 5 (one per `BenchmarkConfig.test_prompts`) into an out-of-tree directory.
- **Fix:** Regenerated cell 7 to build 8 samples (5 benchmark prompts + 3 visual-review prompts) saved under `{TRAINING_ROOT}/samples`; benchmark evaluates all 8.
- **Files modified:** colab/AnimationStudio_Colab_Training.ipynb
- **Verification:** JSON validation + structural checks re-passed; `tests/test_colab_notebooks.py` GREEN.
- **Committed in:** a964abf9 (Task 1 follow-up)

**2. [Rule 3 - Blocking] Over-strict execution-state assertion on pre-existing base notebook**
- **Found during:** Task 2 RED run
- **Issue:** `AnimationStudio_Colab.ipynb` code cells 4–5 omit the `outputs` key entirely (never-run artifact); my assertion required `outputs == []`, failing on the base notebook.
- **Fix:** Accept `None` (missing key) as equally clean — the invariant is "no embedded executed results", not "key present".
- **Files modified:** tests/test_colab_notebooks.py
- **Verification:** RED suite then failed only on the 4 intended README assertions.
- **Committed in:** 2c48d90d (TEST gate)

**3. [Rule 3 - Blocking] README deferred-human assertion too narrow**
- **Found during:** Task 2 GREEN run (60/61)
- **Issue:** README documents the note as `verification_deferred_human` (underscore form, matching phase records); the test only accepted hyphenated/spaced forms.
- **Fix:** Widened the assertion to accept all three spellings.
- **Files modified:** tests/test_colab_notebooks.py
- **Verification:** 61/61 GREEN.
- **Committed in:** 61e4b811 (GREEN follow-up)

---

**Total deviations:** 3 auto-fixed (3 Rule 3)
**Impact on plan:** All three kept the shipped artifact aligned with the plan's action prose and the repo's real state. No scope creep.

## Issues Encountered
- **Colab form rendering defect:** Settings cell originally used `# @param` (with space) — Colab only renders forms for adjacent `#@param`. Caught in build validation, fixed before the first commit.
- **pytest parametrize `ids` callable misuse:** passing a callable to ids for a two-parameter tuple parametrization applies it per value (regex has no `[0]`) — collection error fixed with an explicit ids list.
- **Class-scoped fixture deprecation warning (PytestRemovedIn10Warning):** moved `training_notebook`/`readme_text` fixtures to module scope.
- **Spurious ` M` on README after normalization:** worktree was byte-identical to the index (`git hash-object` == `:README.md`); the flag was stat-cache staleness from the tree-wide re-touch artifact. Confirmed via hash comparison; README diff contains only the intended 44 added lines.
- **Full-suite failures (pre-existing):** `tests/test_story_engine.py` 5 catalog-integration failures — universe catalog returns an empty set for "Lily Bunny" (C-CATALOGDB known state). Unrelated to Phase 1c files; logged to `deferred-items.md` per scope boundary.
- **Working-tree noise:** ~549 stat-dirty files (PNGs, CRLF-converted sources, stale stat info) from a prior Windows checkout artifact — never staged; documented in `deferred-items.md`.

## User Setup Required

**External services require manual configuration** (operator action on Colab, per plan `user_setup`):
- **huggingface:** accept the FLUX.1-dev gated license (huggingface.co/black-forest-labs/FLUX.1-dev), supply `HF_TOKEN` at run time in the notebook Settings cell (never committed).
- **github:** fine-grained PAT with Contents read+write on AnimationStudio, supplied as `GITHUB_TOKEN` at run time (cell 9 sync).
- **google-colab:** T4 (free tier, fp8 profile, hours-scale) or A100 GPU runtime; CPU/no-GPU runtimes fail fast in cell 2.
- Verification command when the operator completes a run: `ls "Universe/Characters/Lily Bunny/lora/"` shows `lily-bunny_vX.Y.safetensors` + `benchmark_report_vX.Y.md`; `python3 scripts/train_lora.py versions` shows the promoted record.

## Next Phase Readiness
- **Ready:** The complete CHAR-07 criterion 2 evidence package (local dry-run chain from 01c-05 + executable notebook + README handoff) is committed; UAT classifier routes D1/D2 auto-pass and D3 to a human (deferred-human) — recorded via SUMMARY coverage block.
- **Blockers/concerns:** No GPU in the build environment (locked decision). Full-suite 5 pre-existing story_engine catalog failures and the ~549 stat-dirty working-tree files are logged to `deferred-items.md` and belong to the universe/catalog-owner phase.
- **Follow-ups:** Bulk asset promotion alternative for under-20 curated sets; multi-character runs (set `CHARACTER_ID`/`CHARACTER_TITLE`); downstream LoRA consumption in Phase 4 generation.

---
*Phase: 01c-character-training-system*
*Completed: 2026-08-27*

## Self-Check: PASSED

- Files verified present: `colab/AnimationStudio_Colab_Training.ipynb`, `tests/test_colab_notebooks.py`, `01c-06-SUMMARY.md`
- Commits verified in git log: `75e6e295`, `a964abf9`, `2c48d90d`, `502baeb9`, `61e4b811`