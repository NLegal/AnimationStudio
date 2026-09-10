# Scoping: N-05 IdentityLock Notebook + N-04 Phase 7/8 Notebooks

Scoped 2026-09-09. Both items are MAJOR and land in `colab/`. N-05 is
**unblocked** (E-02 parameterization + E-07 driver + E-08 CI landed). N-04
Phase 7 is unblocked (storyboard + episode scheduling are movie-free); N-04
Phase 8 partial runs unblocked, full runs still gated on C-01 (approved
images) / C-03 (music).

**Status 2026-09-09:** N-05's two script-gap edits (`--db-path`,
`--no-review-ui` on all 4 lock scripts) are DONE in commit `a196d578`; the
`AnimationStudio_Colab_IdentityLock.ipynb` notebook (14 cells) ships with a
9-test content contract in `test_colab_notebooks.py`. N-04 **Phase 7**
notebook (`AnimationStudio_Colab_Phase7.ipynb`, 11 cells, offline/mock:
story → blueprint → episode → prompts → render queue → continuity → 8-step
workflow → PHASE7_REPORT.md → tests → sync) is DONE, verified offline
(8 scenes / 27 shots / 27 prompts / 0 continuity issues / 8-of-8 workflow
steps + 117 notebook tests). Remaining in this scope: N-04 Phase 8 notebook
(Part A mock + Part B GPU).

---

## N-05 — AnimationStudio_Colab_IdentityLock.ipynb  (Effort M)

**One new notebook driving the Progressive Locking Pipeline.**

### Pipeline facts
- Four scripts, in strict order (each feeds the next):
  `generate_identity_lock.py` -> `generate_face_lock.py` ->
  `generate_body_lock.py` -> `generate_wardrobe.py`
- This is the golden path into LoRA: lock scripts -> curated set (>=20
  approved/character) -> `train_lora.py build-dataset`.
- E-02 already parameterized all four: `--comfyui-url`, `--character`,
  `--universe-dir` (defaults preserve Lily Bunny).
- E-03/E-04 moved the shared `_CombinedRepo` + `check_comfyui` into
  `src/review_ui/combined_repo.py` (single source of truth).
- **Gap found during scoping:** `DB_PATH = "catalog.db"` is still a
  hardcoded constant in all 4 lock scripts. Notebook must control it
  (Drive mount vs local), so **add `--db-path` CLI arg first** (small
  script edit, mirrors E-02 pattern).
- **Gap found during scoping:** every script ends with a *blocking*
  `uvicorn.run(app, ..., port=8000)` review-UI launch
  (`127.0.0.1:8000`). Blocks cell execution and collides if 2 scripts run
  in one session. Add a `--no-review-ui` flag so cells run headless and
  the UI is started once (by the notebook) behind a tunnel.

### Proposed cell layout (mirrors `AnimationStudio_Colab.ipynb`)
1. **Settings** — `CHARACTER_ID`, `CHARS_PER_LOCK=0` (0 = all 39),
   `COMFYUI_URL`, `REPO_URL`/`REPO_BRANCH=colab-gpu`, Drive options.
2. **Mount Drive** (catalog.db home; reuse the git_sync pattern).
3. **Clone repo + install the studio** (same pip block as Phase 1 note).
4. **Start ComfyUI server** (reuse auto-restart helper pattern) + GPU check.
5. **Dry-run preview** — iterate characters, show which curated sets are
   missing, confirm scope before spending GPU.
6. **Run lock scripts in order** — one cell per script; per-character loop;
   each cell `--comfyui-url`, `--character`, `--universe-dir`,
   `--db-path`, `--no-review-ui`. Uses `--dry-run` first? -> not yet
   supported; add later if needed.
7. **Launch Review UI + tunnel** once (single `uvicorn` + cloudflared/tunnel).
8. **Export PNGs** (into Colab file tree) + **sync approved assets** (git push).
9. **Gate check** — count approved assets/character; print the training
   dataset readiness table (>=20 approved).

### Dependency: small script edit (part of this item)
- `--db-path` on all 4 lock scripts (+ update the E-02 test that asserts CLI
  args exist, if it enumerates argparse flags).
- `--no-review-ui` / `--review-ui-port` on all 4.
- Keep defaults backward-compatible (Lily, catalog.db, UI on).
- Update e2e/CLI test count accordingly.

### Notebook tests to add (extend `tests/test_colab_notebooks.py`)
- Cell 0 settings contain `CHARACTER_ID` / `COMFYUI_URL`.
- The 4 lock-script cells each invoke `--comfyui-url`, `--character`,
  `--universe-dir`, `--db-path`, `--no-review-ui`.
- No colab secret pattern exceptions.

### Verification
- 4 lock scripts: `--help` shows new flags; offline dry-run adds
  `--dry-run` if quick (else verified by tests only).
- Notebook loads; notebook-consistent pattern checks pass offline.
- Gate table renders in mock review run.

---

## N-04 — Phase 7 + Phase 8 notebook (Effort L, "at minimum" slice)

**Add 2 notebooks; defer Phase 9-12 combined Episode notebook as follow-up.**

### Phase 7 — `AnimationStudio_Colab_Phase7Storyboard.ipynb`
- **WHAT:** Production planning & storyboard scheduling (movie-free; not the
  music CLI — that is the misnamed `generate_phase7.py`, unchanged).
- **Drivers (all mock-compatible, proven by E-07):**
  - `EpisodeGenerator()` (src/story_engine/generator.py) — episode blueprint.
  - `blueprint_to_episode()` (src/production/blueprint_adapter.py).
  - `ProductionPipeline().generate_prompts(ep)` — scene/shot prompt rows.
  - `EpisodeWorkflowFactory().build_episode_workflow(episode_id)` — the
    8-step episode workflow (src/studio/workflow.py).
  - `PipelineOrchestrator().process_pipeline(...)` — drives to COMPLETED.
- **Cells:** settings -> clone/install -> generate episode blueprint ->
  preview schedule table -> build workflow -> orchestrate (mocked) ->
  export `PHASE7_REPORT.md` -> sync.
- **Verification:** reuses mock backends; 5 e2e-style assertions borrowed
  from `tests/test_e2e_episode.py`; offline green (no GPU).

### Phase 8 — `AnimationStudio_Colab_Phase8Images.ipynb`
- **WHAT:** AI image generation & visual asset pipeline for a scene.
- **Drivers:** `src/image_generation/*` (consistency, reference_manager,
  validator, upscaler, thumbnail), `src/generation_engine` backends, and
  the existing Phase-1 notebook's ComfyUI install/server/download cells
  (copy the proven cells rather than re-derive).
- **Two-part structure:**
  - **Part A (mock)** — build a scene, generate images through
    `MockBackend`, run identity scoring + consistency check, approve into
    catalog. Offline-green; exercises the full visual-pipeline code.
  - **Part B (real)** — ComfyUI install + fp8 Flux download + server start,
    then generate a **single scene** (not full library) with scoring gate.
  - **NOTE:** reused ComfyUI cells must be refactored into importable
    helpers or duplicated; decide during execution (prefer shared
    `colab/` python fragment imported by cells, e.g. `colab/comfy_setup.py`).
- **Verification:** Part A offline via mocks; Part B gated on `--backend
  comfyui` being reachable + C-01 pending (runs only if a scene image set
  exists).

### Deferred (same N-04 ticket, later workstream)
- Phase 9 (animation/render) notebook — needs C-01 + C-03 media.
- Phase 10 (post), Phase 11 (publish), Phase 12 (orchestration) — the
  "combined Episode notebook" from the ticket's recommendation; schedule
  after Phase 7 notebook proves the driver cells.

---

## Decision needed before execution
1. N-04 Phase 8 Part B: keep a **single Phase8 notebook with mock+real
   sections**, or split into **2 files** (mock-only always-green vs
   real, GPU-gated)? Recommend single file with Part A/B.
2. N-04 Phase 7/8 + N-05 all land as **separate notebooks** (4 new files in
   `colab/`) vs combined files? Recommend separate.
3. Shared ComfyUI setup: refactor into `colab/comfy_setup.py` now, or copy
   cells verbatim in this pass (accept duplication) and refactor later?
   Recommend the shared fragment (avoids 3 copies).

## Sequencing proposal
1. **W1:** N-05 + its small script edits (`--db-path`, `--no-review-ui`) +
   notebook tests. (Unblocked, highest leverage for C-01.)
2. **W2:** N-04 Phase 7 storyboard notebook (offline, mock drivers).
3. **W3:** N-04 Phase 8 notebook (Part A mock offline; Part B on GPU).
4. **Deferred:** Phase 9/10/11/12 combined Episode notebook.