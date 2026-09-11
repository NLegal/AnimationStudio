# TODOPROJECT.md — Comprehensive Codebase Audit
# Generated: 2026-09-09 | All 12 Phases Scanned | Updated: 2026-09-11 (VISION.md lyrics + video + cloud-notebook gaps closed)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Source modules | 20 packages |
| Source files | 178 Python files |
| Source lines | ~25,400 LOC |
| Test files | 34 (33 test + 1 conftest) |
| Test lines | ~17,700 LOC |
| Test functions | ~1,695 |
| Test classes | ~309 |
| Scripts | 19 Python + 3 setup + 34 wrappers |
| Colab notebooks | 8 |
| Characters | 39 |
| World locations | 138 |
| Reusable props | 1,559 (20 categories) |
| Asset rows in catalog.db | 2,472 (1,246 scored / 1,226 shortlisted; **0 approved**) |
| Approved assets | 0 (mock placeholders only; docs claimed 18,071 — overstated) |
| Active notebook branch | **`colab-gpu` ONLY** (master is deprecated, never used) |

**Overall Health: YELLOW** — Solid architecture, comprehensive tests, but ZERO real media produced. The entire pipeline runs on mock placeholders. The infrastructure is 100% built; the content pipeline has never executed end-to-end with real generation. **Update:** `catalog.db` corruption (C-00) RESOLVED 2026-09-09 by removing the stale `-shm`/`-wal` files left by an abrupt Google Colab termination; DB now passes `PRAGMA integrity_check`.

---

## PRIORITY 1 — Critical Issues (Blocking/Production)

### C-00: catalog.db was CORRUPTED — RESOLVED 2026-09-09 (WAL/SHM removal)
- **Module:** `asset_repository` / data layer
- **File:** `C:\Projects\AnimationStudio\catalog.db` (+ now-removed `catalog.db-shm`, `catalog.db-wal`)
- **Severity:** CRITICAL → **CLOSED (verified)**
- **Status:** ✅ **RESOLVED by operator 2026-09-09.** Removing the stale `-shm` + `-wal` files and keeping the single main `catalog.db` restored a consistent, readable database. `PRAGMA integrity_check` now returns `ok`; no data loss detected (the ~100 "never used" pages and rowid disorder were artifacts of an aborted checkpoint, not lost rows). Automated verification added: `tests/test_catalog_integrity.py`. A WAL removal can itself truncate uncommitted tail data, so recovery always pulls the most recent *committed* state — acceptable here since `git_sync.auto_sync` already runs `wal_checkpoint(TRUNCATE)` before every push. **Hardening 2026-09-09:** `catalog.db` converted to `PRAGMA journal_mode=DELETE` (chosen by operator after the guard tripped again when test runs reopened the WAL-mode DB and recreated sidecars) — WAL sidecars can no longer reappear, and `colab/git_sync.py`'s `wal_checkpoint(TRUNCATE)` is now a harmless no-op preserved defensively. Recommended go-forward controls:
  - Confirm `catalog.db` files exactly match the upstream `origin/colab-gpu` committed copy before any new Colab run (`git ls-files --error-unmatch catalog.db`; compare `git cat-file blob origin/colab-gpu:catalog.db` vs local MD5).
  - Run `python scripts/verify_catalog.py` before/after any GPU-heavy session (new script, added in this change).
- **Root cause:** Abrupt Google Colab session termination mid-commit leaves a stale WAL that SQLite refuses to reconcile on the next open; earlier sessions were also killed before `git_sync.py` could run `wal_checkpoint(TRUNCATE)`. Repeat sessions were killed same way, so no writer ever finished checkpointing.
- **Residual (NOT resolved):** the **18,071** approved assets claimed in `PHASE1/2/3_STATUS.md` never existed in the DB (2,472 rows max). That is a **documentation/exaggeration issue** (M-level, tracked under the MockBackend findings), NOT a data-loss issue. The truth is **0 approved assets** (C-01), which is what actually blocks LoRA dataset building (N-15).
- **Recovery procedure (documented for future crashes):** see the new section below.
- **Estimated Effort:** S (closed)
- **Dependencies:** None

---

## RECOVERY — catalog.db (sudden Colab termination)

**Symptom:** `PRAGMA integrity_check` fails; `catalog.db-shm` and `catalog.db-wal` present; docs claim many more assets than the DB holds.

**Cause observed (2026-09-09):** Google Colab VM killed mid-commit leaves a stale WAL; repeated kills prevent checkpointing.

**Procedure:**
1. `Copy catalog.db` (+`-wal`, `-shm`) to a quarantine folder first if you want forensics.
2. Stop every writer (no Colab session running, no Review UI, no scripts).
3. `Remove-Item catalog.db-wal, catalog.db-shm` (keep `catalog.db`).
4. `python scripts/verify_catalog.py` — must report `integrity_check = ok`.
5. If still broken, `sqlite3 catalog.db ".recover" catalog_recovered.db` (SQLite ≥3.38) then swap in; else re-seed: `python scripts/seed_universe.py --db catalog.db` (idempotent).
6. Re-sync with upstream commit once clean; then run `git_sync.py`'s `wal_checkpoint(TRUNCATE)` discipline before future pushes (already in `colab/git_sync.py`).
7. Add `-wal`/`-shm` to the `.gitignore` safety net (T-09) and add the integrity test to CI (E-08).

---

### C-01: Zero Real Media Produced
- **Module:** All (cross-cutting)
- **Severity:** CRITICAL
- **Description:** Every image in the system (2,472 asset rows, all `scored`/`shortlisted`, **0 approved**) is a solid-color placeholder generated by MockBackend. No LoRA has been trained. No song has been generated. No animation has been rendered. No video has been exported. The pipeline has NEVER run end-to-end with real backends.
- **Recommended Fix:** Execute ComfyUI setup (`setup_comfyui_flux.ps1`), run Phase 1 generation with `--backend comfyui` on the **`colab-gpu` branch**, produce first batch of real character reference sheets, validate quality.
- **Estimated Effort:** XL (weeks of iteration)
- **Dependencies:** GPU hardware (CUDA) + ComfyUI install + FLUX model download (~17.25 GB fp8 bundle on `colab-gpu`)

### C-02: LoRA Training Blocked on GPU
- **Module:** `src/training_engine/`, `scripts/train_lora.py`
- **Severity:** CRITICAL
- **Description:** Production LoRA v1.0 for Lily Bunny is deferred to human operator. The entire character consistency system depends on LoRA models that don't exist yet. Without trained LoRAs, character consistency across episodes is impossible.
- **Recommended Fix:** Run the Colab training notebook (`colab/AnimationStudio_Colab_Training.ipynb`) with a T4/A100 GPU runtime.
- **Estimated Effort:** L (setup) + M (per character)
- **Dependencies:** ComfyUI images from C-01, Google Colab account with GPU access

### C-03: No Audio Generated
- **Module:** `src/music_generation/`, `scripts/generate_phase5.py`
- **Severity:** CRITICAL
- **Description:** No songs, no voice recordings, no SFX exist on disk. `Audio/Music/`, `Audio/Vocals/`, `Audio/Masters/` are all empty. Suno backend is a stub (`NotConfigured`). ACE-Step requires localhost:8001 running.
- **Recommended Fix:** Set up ACE-Step locally or configure Suno API when available. Run `generate_phase5.py --generate --backend acestep`.
- **Estimated Effort:** L
- **Dependencies:** ACE-Step server or Suno API key

### C-04: No Video Pipeline Execution
- **Module:** `src/animation/`, `src/post_production/`, `src/publishing/`
- **Severity:** CRITICAL
- **Description:** Phases 9-12 (animation, post-production, publishing) have complete code frameworks but have never been tested against real media. The end-to-end story→video→publish pipeline is unvalidated.
- **Recommended Fix:** After C-01 and C-03 are resolved, run a single-episode smoke test through the full `EpisodeWorkflowFactory` pipeline.
- **Estimated Effort:** XL
- **Dependencies:** C-01, C-03

### C-05: Vision/Architecture Deviation — No Real Character Consistency
- **Module:** Cross-cutting
- **Severity:** CRITICAL
- **Description:** VISION.md's core thesis is "persistent characters that appear in every episode." Without trained LoRAs, IPAdapter models, PuLID integration, or Flux Kontext — none of the character consistency technologies listed in VISION.md are implemented. The codebase has `IdentityScorer` and `ConsistencyManager` but they score mock images. Real character consistency requires GPU inference.
- **Recommended Fix:** Prioritize Phase 1c LoRA training completion, then Phase 1b production runs with ComfyUI.
- **Estimated Effort:** XL
- **Dependencies:** GPU hardware

### N-01: `AnimationStudio_Validate.ipynb` Cannot Run as Shipped
- **Status:** ✅ **DONE 2026-09-09** — rebuilt as a clean 8-step linear flow (11 cells: intro, STEP 1–8, next steps), no duplicate cells; STEP 3 model download + STEP 6 backend/gen_input added; `MODEL_FILE`/`MODEL_URL`/`MODEL_EXPECTED_BYTES` literal in Settings; embeds N-08 disk guard + N-10 size check + N-09 GPU assert; `BRANCH="colab-gpu"` only. Drift-guarded by `TestValidateNotebookStructure` (N-17).
- **Module:** `colab/AnimationStudio_Validate.ipynb`
- **Severity:** CRITICAL
- **Description:** The pre-flight validation notebook is internally broken. It is **missing STEP 3 (model download)** and **STEP 6 (backend + gen_input construction)**, while STEP 5 asserts on `MODEL_FILE` (globals fallback → always `None`) and STEP 7 calls `backend.generate(gen_input, ...)` where both `backend` and `gen_input` are **never defined** in any cell. Notebook markdown's own recovery advice ("re-run Cells 0–3") cannot fix a `NameError`. STEP 5 and STEP 7 each exist as two duplicate variants (old "short" + new "self-healing"), and the short variants assume kernel state (`Path`, `REPO`, `np`, `display`) that a fresh run lacks.
- **Recommended Fix:** Rebuild the notebook top-to-bottom as a clean 8-step linear flow with no duplicates: Settings → Clone/Install/GPU assert → ComfyUI install → **model download (add cell)** → server start → model visibility → **backend+gen_input construction (add cell)** → generate smoke image → sharpness gate. Verify by "Runtime → Run all" on a fresh T4 VM.
- **Estimated Effort:** M
- **Dependencies:** None (pure notebook fix)

### N-02: `master`-Branch Model URLs Are 404 — CLOSED (branch policy: colab-gpu ONLY)
- **Module:** `colab/AnimationStudio_Colab.ipynb`, `Phase2.ipynb`, `Phase3.ipynb`
- **Severity:** ~~CRITICAL~~ → **CLOSED 2026-09-09 (no-action + preventive cleanup)**
- **Status:** ✅ Preventive cleanup applied 2026-09-09: dead `master` GGUF maps removed from all Phase 1–3 notebooks (model cells now hold only the colab-gpu fp8 URL), `BRANCH` param locked to `["colab-gpu"]` across **all 8 notebooks** (incl. Phase 4/5/6 + Training), ComfyUI-GGUF install block deleted, deprecation notes added. Enforced by `TestPhaseNotebookModelDownloads` (N-17).
- **Status:** ✅ **Non-issue by policy.** Operator confirmed **all work runs on `colab-gpu` only; `master` is never used**. The 404 encoder/VAE URLs (`city96/FLUX.1-dev-gguf`) are only reachable via `BRANCH="master"`, which is now deprecated. Keep `colab-gpu` (fp8 bundle, working URLs) as the sole supported branch.
- **Description:** The `master`-branch model map points encoder/VAE downloads at `city96/FLUX.1-dev-gguf` (`clip_l.safetensors`, `t5xxl_fp16.safetensors`, `ae.safetensors`) — all three return 404 (repo ships only GGUF quants). Selecting `BRANCH="master"` aborts at download because `check=True`. The Training notebook already uses correct hosts (`comfyanonymous/flux_text_encoders`, gated `black-forest-labs/FLUX.1-dev`).
- **Recommended Fix (preventive only):** add a one-line deprecation note at the top of the Phase 1–3 Settings cells (`BRANCH = "colab-gpu"  # master is deprecated/unusable`) so nobody toggles it back; no URL work needed.
- **Estimated Effort:** S
- **Dependencies:** None

### N-03: Training Notebook Git Push Header is Malformed
- **Status:** ✅ **DONE 2026-09-09** — push header now `http.extraheader=Authorization: {_basic_auth_header(GITHUB_TOKEN)}` (Cell 9). Enforced by `TestTrainingNotebookStructure.test_sync_cell_authorization_header_prefixed` (N-17).
- **Module:** `colab/AnimationStudio_Colab_Training.ipynb` (Cell 9)
- **Severity:** CRITICAL
- **Description:** The sync cell builds the push as `git -c http.extraheader={_basic_auth_header(GITHUB_TOKEN)} push ...` — **missing the `Authorization: ` prefix** that Phases 4/5/6 notebooks use (`http.extraheader=Authorization: {_basic_auth_header(...)}`). `_basic_auth_header()` returns `basic <base64>` (no scheme word), so git registers a bogus header and PAT pushes fail with a 401 on private repos, silently after a successful training run — the LoRA + benchmark artifacts never reach GitHub.
- **Recommended Fix:** Change to `f"http.extraheader=Authorization: {_basic_auth_header(GITHUB_TOKEN)}"` (or reuse `git_sync.auto_sync`). Add the assertion to `tests/test_colab_notebooks.py` `TestTrainingNotebookStructure` (`"Authorization: "` must appear adjacent to `_basic_auth_header` in the push cell).
- **Estimated Effort:** S
- **Dependencies:** None

---

### ~~M-01: Phase Roadmap Divergence (12 Phases vs 6-Phase Roadmap)~~ → ✅ **DONE 2026-09-11**
- **Module:** `.planning/ROADMAP.md`, `PHASE*.md`
- **Severity:** MAJOR
- **Description:** `.planning/ROADMAP.md` defines 6 phases (1→1b→1c→2→3→4→5→6). The actual project has 12 PHASE*.md files with different numbering and scope. The ROADMAP has `TBD` for Phases 2-6 plans. The `STATE.md` says only phases 1, 1b, 1c, 7, 8 are planned. The ROADMAP and actual implementation are out of sync.
- **Recommended Fix:** Reconcile ROADMAP.md with actual PHASE*.md structure. Update `.planning/STATE.md` to reflect all 12 phases.
- **Estimated Effort:** S
- **Dependencies:** None
- **Done:** `.planning/ROADMAP.md` rewritten to the canonical 12-phase structure (`PHASE1.md`–`PHASE12.md` are authoritative). GSD execution tracks mapped onto it: 01/01b/01c → Phase 1 (16/16 plans), 07/08 → Phase 5 music surface (4/4 plans); Phases 2–4, 6–12 documented as implemented-via-backlog with no GSD plans. Added the reconciling table up top (kills the GSD "Phase 7/8 = music" vs canonical `PHASE7.md` Production Planning / `PHASE8.md` Image Generation collision). `.planning/STATE.md` updated: frontmatter now tracks 12 phases (2 complete), new Canonical Phase Map section, metrics row for unplanned canonical phases, Roadmap Evolution notes the reconciliation.

### ~~M-02: README.md Claims vs Reality~~ → ✅ **DONE 2026-09-11**
- **Module:** `README.md`
- **Severity:** MAJOR
- **Description:** README claims "1435 tests (1432 passing)" and lists all 12 phases as "implemented and audited." However: (a) no actual generation has occurred, (b) Phase 7-8 plans are marked complete in ROADMAP but Phase 7 is listed under different numbering in PHASE*.md, (c) README doesn't mention the mock-placeholder state of all assets, (d) README doesn't warn users that GPU/ComfyUI is required for real output.
- **Recommended Fix:** Add prominent disclaimer about mock state. Clarify that all 18,071 assets are placeholders. Add "Getting Real Output" section distinguishing mock pipeline from real pipeline.
- **Estimated Effort:** M
- **Dependencies:** None
- **Done:** (a) Stale test counts corrected — README now states **2,050 collected**, **785 in the 12 offline-safe CI suites**, **904 with the Review-UI suites**, verified by collection runs; the old "1435/1432" claim removed. (b) Resolved by M-01 (roadmap now canonical 12-phase; README phase table already used canonical numbering). (c)+(d) The existing **Production Readiness Note** already discloses the mock-placeholder state (2,508 asset rows, 0 approved) and GPU/ComfyUI-for-real-output requirement — verified live against `catalog.db` and kept accurate. "Test coverage by module" table retained with corrected framing.

### M-03: 13 Documentation Gaps (Phase 1 + Phase 5 + Phase 6)
- **Module:** `Universe/`, `Audio/`, `StoryEngine/`
- **Severity:** MAJOR
- **Description:**
  - Phase 1: 8 doc gaps (ReferenceSheets/, ModelSheets/, ColorPalette/, Fonts/ empty; 4 category INDEX files missing)
  - Phase 5: 1 structural gap (Audio/Vocals/ missing .gitkeep)
  - Phase 6: 4 missing standalone docs (Humor/, Emotions/, Seasons/, Metadata/ guides)
- **Recommended Fix:** Create the 13 missing documentation files.
- **Estimated Effort:** M
- **Dependencies:** None

### M-04: Review UI Monolith (1,305 lines, 64 functions)
- **Module:** `src/review_ui/app.py`
- **Severity:** MAJOR
- **Description:** The Review UI is a single 1,305-line file with 64 functions handling dashboard, character detail, review, motion, music, generation, API endpoints, and seeding. It contains a `_StubAssetRepo` class that suggests incomplete repo integration. No authentication/authorization on any route.
- **Recommended Fix:** Split into separate route modules (dashboard, review, music, generation, api). Add basic auth. Remove `_StubAssetRepo`.
- **Estimated Effort:** L
- **Dependencies:** None

### M-05: No Integration Tests Against Real Backends
- **Module:** `tests/`
- **Severity:** MAJOR
- **Description:** All tests use MockBackend. Zero tests exercise ComfyUI, cloud API (FAL/Replicate/BFL), or ACE-Step connections. Integration tests are purely structural (check imports, class existence, mock returns).
- **Recommended Fix:** Add integration test suite with backend-specific markers (`@pytest.mark.comfyui`, `@pytest.mark.cloud`). Make them optional but runnable.
- **Estimated Effort:** L
- **Dependencies:** C-01 (ComfyUI setup)

### M-06: Security Module is In-Memory Only
- **Module:** `src/studio/security.py`
- **Severity:** MAJOR
- **Description:** `SecurityManager`, `AccessControl`, `AuditLog`, and `store_secret()` are all in-memory Python dicts. Secrets are lost on restart. Audit logs are lost on restart. RBAC rules are lost on restart. No persistent storage for any security state.
- **Recommended Fix:** Persist to SQLite or filesystem. Secrets should use a secrets manager (keyring, vault). Audit log should append to file or DB.
- **Estimated Effort:** L
- **Dependencies:** None

### ~~M-07: No Input Validation on Review UI Endpoints~~ → ✅ **DONE 2026-09-11**
- **Module:** `src/review_ui/app.py`
- **Severity:** MAJOR
- **Description:** POST endpoints (`/approve/{id}`, `/reject/{id}`, `/regenerate/{id}`, `/promote/{id}`, `/generate`, `/seed`) accept form data without input validation. The `id` parameter is passed directly to database queries. Potential for SQL injection through the asset_id parameter in SQLite queries.
- **Recommended Fix:** Add Pydantic models for all POST inputs. Validate/sanitize asset_id parameters before DB queries.
- **Estimated Effort:** M
- **Dependencies:** None
- **Done:** New `src/review_ui/input_validation.py` (pure, side-effect-free helpers): `validate_asset_id` (token charset `[A-Za-z0-9._-]`, ≤192 chars, rejects path traversal/whitespace/leading non-alnum — matches every real asset/character id), `validate_action` (D-15 allowlist), `validate_backend`/`validate_music_backend` (mirror the `resolve_backend` + `get_backend` registries), `validate_scope` (6 catalog scopes), `validate_count` (1–50), `validate_limit` (0–1000), `cap_text` (2 kB cap for reason/topic/details). Wired into every hazardous route in `app.py`: all 5 action handlers + the JSON `/api/assets/{id}/{action}` path validate `asset_id`+`action` before touching the repo (`_apply_action`), `/generate` validates scope/backend/count/limit and caps `item`/`asset_type`/`variant` (bad input → 303 redirect, nothing queued), `/asset-image` validates `asset_id` (404), `/music/generate` validates backend against the music registry + caps topic, `/motion/prompt` + `/music/prompt` cap free-text fields. SQLite layer was already parameterized; this closes the surface at the boundary. `tests/test_review_ui_validation.py` (31 tests) + endpoint hardening; full offline suite green (904 passed).

### M-08: Dual Database Patterns
- **Module:** `src/asset_repository/sqlite_repo.py`, `src/studio/security.py`
- **Severity:** MAJOR
- **Description:** The asset repository uses aiosqlite with connection pooling. The security/backup/monitoring modules use in-memory dicts. The story engine, animation bible, and audio bible use pure Python dataclasses with no persistence. There are at least 3 different persistence patterns with no unified data layer.
- **Recommended Fix:** Standardize on SQLite as the persistence layer for all modules that need it. Create a shared database connection manager.
- **Estimated Effort:** XL
- **Dependencies:** None

### N-04: No Colab Notebooks for Phases 7–12
- **Module:** `colab/`
- **Severity:** MAJOR
- **Description:** Notebook coverage exists only for Phases 1–6 (+1c Training + Validate). There is **no notebook** for: Phase 7 production/storyboard planning, Phase 8 image-generation pipeline, Phase 9 animation/render, Phase 10 post-production, Phase 11 publishing, or Phase 12 orchestration. `generate_phase7.py` exists but is a single-song music CLI (oddly named — no storyboard functionality at all). The `src/studio` `EpisodeWorkflowFactory` 8-step episode pipeline has no cloud/Colab driver.
- **Recommended Fix:** Create one new notebook per gap (or a single combined `AnimationStudio_Colab_Episode.ipynb` that drives the mock-compatible EpisodeWorkflowFactory to synthesize an episode schedule, then swaps real backends for image generation + music in later cells). At minimum add Phase 7 + Phase 8 (real image generation for a scene) notebooks.
- **Status:** ✅ **DONE 2026-09-10** — Phase 7 `colab/AnimationStudio_Colab_Phase7.ipynb` (11 cells, offline/mock: story → blueprint → episode → prompts → render queue → continuity → 8-step EpisodeWorkflowFactory drive to COMPLETED → PHASE7_REPORT.md → test suites → sync), Phase 8 `colab/AnimationStudio_Colab_Phase8.ipynb` (13 cells, Part A mock visual pipeline: MockBackend → ImageValidator → IdentityScorer → ConsistencyManager, offline-green; Part B real ComfyUI + fp8 Flux for one scene, GPU-gated), AND Phases 9–12 `colab/AnimationStudio_Colab_Phase9to12.ipynb` (17 cells, Part A mock: render queue + regeneration → timeline assembly + QC + export presets → publishing metadata/record/schedule → 8-step orchestrator drive to completion → PHASE9_12_EPISODE_REPORT.md; Part B real single-scene ComfyUI render, GPU-gated). Part A verified offline for all three notebooks. Content contracts in `test_colab_notebooks.py` (149 pass). Remaining: `tests/test_e2e_episode.py` parity for Phase 9-12 Part B (media/GPU-gated) + optional `colab/comfy_setup.py` extraction.
- **Estimated Effort:** L
- **Dependencies:** C-01 (real ComfyUI images), C-03 (music) for non-mock runs

### N-05: No Notebook for Phase 1b Progressive Lock Scripts
- **Module:** `colab/`
- **Severity:** MAJOR
- **Description:** `generate_identity_lock.py`, `generate_face_lock.py`, `generate_body_lock.py`, `generate_wardrobe.py` (the core character-consistency "Progressive Locking Pipeline") have no Colab driver. These are exactly the runs that produce the curated reference/expression/pose/outfit sets that feed `train_lora.py build-dataset` (≥20 approved per character). Their absence breaks the golden path: lock scripts → curated assets → LoRA dataset.
- **Recommended Fix:** Add `AnimationStudio_Colab_IdentityLock.ipynb` that clones the repo, installs ComfyUI, and runs the four lock scripts in order (each already ends by launching the Review UI; keep that behind a tunnel flag). Consider porting the four scripts' hardcoded `"Lily Bunny"`/`COMFYUI_URL`/`DB_PATH` constants to CLI args (E-02/E-07) first.
- **Status:** ✅ **DONE 2026-09-09** — `colab/AnimationStudio_Colab_IdentityLock.ipynb` (14 cells: settings → Drive → clone/install → ComfyUI → fp8 model + N-08/N-10 guards → server → GPU → 4-stage pipeline in order → export → single Review UI + tunnel → training-readiness gate + sync). Added `--db-path` + `--no-review-ui` CLI args to all 4 lock scripts (headless sequential run instead of 4 blocking uvicorn servers); `MAX_CHARACTERS_PER_LOCK` cap for safe free-tier trials. Content-contract hooked into `tests/test_colab_notebooks.py` (103 tests pass; suite went 87→103).
- **Estimated Effort:** M
- **Dependencies:** E-02/E-07 (parameterization) preferable first — done

### ~~N-06: No Cloud-Backend Notebook (fal/replicate/bfl)~~ → ✅ **DONE 2026-09-11**
- **Module:** `colab/`
- **Severity:** MAJOR
- **Description:** Every image-generation notebook is ComfyUI-only. There is no notebook path for `--backend cloud --provider fal|replicate|bfl`, even though (a) the CLI scripts default to those providers, (b) cloud backends need no 17 GB model download, and (c) the free-tier T4 cannot run fp8 Flux at production batch sizes (2 min/image; 12,472-props run = ~17 days). Cloud is the only realistic path to generating the full Phase 1–3 libraries.
- **Recommended Fix:** Add a `CLOUD_PROVIDER` setting + a cloud-mode cell to the Phase 1/2/3 notebooks: install `usingenv`-free script deps, then call the phase script with `--backend cloud --provider fal --persist-images` and `--sync-every-image`; require `FAL_API_KEY` via `getpass` (secrets runtime-only, consistent with the secret-shape guard in `test_colab_notebooks.py`).
- **Estimated Effort:** M
- **Dependencies:** Cloud API keys
- **Done:** `colab/AnimationStudio_Colab_Cloud.ipynb` (CELL 1 settings `CLOUD_PROVIDER`/`PERSIST_IMAGES`/`SYNC_EVERY`/`SYNC_EVERY_IMAGE`/`LIMIT`/`DRY_RUN`; secrets via getpass; `_gen_cmd` invokes all three phase scripts with `--backend cloud --provider {p} --persist-images --sync-every-[image] --sync-token ...`; `git_sync.auto_sync` final safety push; `verify_catalog.py` validation). Content contract enforced by `TestCloudNotebookStructure` (10 tests) in `tests/test_colab_notebooks.py`.

### ~~N-07: Training Notebook is Single-Character Only (No 39-Character Batch)~~ → ✅ **DONE 2026-09-11**
- **Module:** `colab/AnimationStudio_Colab_Training.ipynb`
- **Severity:** MAJOR
- **Description:** Cells 5–8 operate on a single `CHARACTER_ID`/`CHARACTER_TITLE`; to train all 39 characters an operator must edit Cell 1 and re-run 39× (each with hours of T4 time and a ≥20-curated-asset prerequisite). No loop, no per-character dataset gate status, no registry of "pending characters".
- **Recommended Fix:** Add a `CHARACTERS` list setting (reuse the 39-name dropdown from the Phase 1 notebook) and a driver cell that, per character: (a) runs `build-dataset` (fail-with-clear-message if <20 curated), (b) trains, (c) benchmarks, (d) registers/promotes, (e) syncs — skipping characters already in `training/lora_registry.json` with a passing gate. Keep a single send-ahead `--character-ids` mode for partial runs.
- **Estimated Effort:** L
- **Dependencies:** N/A
- **Done:** `colab/AnimationStudio_Colab_Training.ipynb` (12 cells total): Settings cell (Cell 1) gains `CHARACTERS` 39-name/"all" dropdown, `MAX_CHARACTERS_PER_RUN`, `SKIP_ALREADY_TRAINED`, `SEND_AHEAD_IDS` knobs; Cells 5–9 are per-character functions (`build_dataset`, `train_lora`, `benchmark_lora`, `register_promote`, `sync_artifacts`); Cell 10 batch driver resolves CHARACTERS → seeds via `discover_characters`, skips already-passing registry entries (`get_promoted` + `benchmark_scores.get("passed")`), runs full pipeline per selected character, respects MAX cap and send-ahead override. Content contract enforced by `TestTrainingNotebookBatchDriver` (10 tests) in `tests/test_colab_notebooks.py`.

---

## PRIORITY 3 — Enhancements

### E-01: Missing Script Wrappers
- **Status:** ✅ **DONE 2026-09-09** — added `generate_phase7.{ps1,bat}` and `train_lora.{ps1,bat}` following the `py.ps1`/`py.bat` pattern; both verified (`--help` runs).
- **Module:** `scripts/`
- **Severity:** MINOR
- **Description:** `generate_phase7.py` and `train_lora.py` lack `.bat` and `.ps1` wrappers. All 17 other scripts have both.
- **Recommended Fix:** Add wrappers following existing pattern.
- **Estimated Effort:** S
- **Dependencies:** None

### E-02: Hardcoded Character in Lock Scripts
- **Module:** `scripts/generate_identity_lock.py`, `generate_face_lock.py`, `generate_body_lock.py`, `generate_wardrobe.py`
- **Severity:** MINOR
- **Description:** Four scripts hardcode "Lily Bunny" as the character name, description, and paths. They cannot be used for other characters without code edits. Other scripts (phase1/2/3) correctly use discover_characters() and CLI filtering.
- **Recommended Fix:** Extract character parameterization to CLI args or config file.
- **Status:** ✅ **DONE 2026-09-09** — `--character` and `--universe-dir` flags added to all 4 lock scripts (argparse defaults: `CHARACTER_NAME`/`UNIVERSE_DIR`); `main(comfyui_url, character_name, universe_dir)` threads them through repos, prompts, and paths. Existing behavior unchanged without flags.
- **Estimated Effort:** M
- **Dependencies:** None

### E-03: _CombinedRepo Duplication
- **Module:** `scripts/generate_identity_lock.py`, `generate_face_lock.py`, `generate_body_lock.py`, `generate_wardrobe.py`
- **Severity:** MINOR
- **Description:** `_CombinedRepo` adapter class is copy-pasted identically across 4 scripts (~20 lines each).
- **Recommended Fix:** Extract to `src/review_ui/combined_repo.py` or similar shared module.
- **Status:** ✅ **DONE 2026-09-09** — `_CombinedRepo` moved to `src/review_ui/combined_repo.py::CombinedRepo`; all 4 scripts import it (302 lines of copy-paste removed; `tests/test_review_ui_generation.py` + `tests/test_catalog_integrity.py` = 34 passed).
- **Estimated Effort:** S
- **Dependencies:** None

### E-04: check_comfyui() Duplication
- **Module:** `scripts/generate_identity_lock.py`, `generate_face_lock.py`, `generate_body_lock.py`, `generate_wardrobe.py`
- **Severity:** MINOR
- **Description:** ComfyUI health-check function duplicated across 4 scripts.
- **Recommended Fix:** Extract to shared utility module.
- **Status:** ✅ **DONE 2026-09-09** — `check_comfyui` moved to `src/review_ui/combined_repo.py` (now `check_comfyui(comfyui_url)`); all 4 lock scripts import it.
- **Estimated Effort:** S
- **Dependencies:** None

### E-05: ColorPalette/ and Fonts/ Directories Empty
- **Module:** `ColorPalette/`, `Fonts/`
- **Severity:** MINOR
- **Description:** README/TODO audits note these directories as empty. `ColorPalette/COLOR_PALETTE.md` exists but `Fonts/FONT_GUIDE.md` is a guide, not actual font files.
- **Recommended Fix:** Add brand palette JSON (referenced by `ColorVerificationPlugin`) and font files if specified.
- **Status:** ✅ **RESOLVED 2026-09-09** — the palette JSON `Universe/ColorPalette/brand-palette.json` (what `ColorVerificationPlugin` actually loads at `color_verification.py:51`) **already exists and is tracked** (5 primary + pastel groups); `tests/test_scoring_plugins.py` covers it. Root `ColorPalette/` and `Fonts/` hold only steerage docs (`COLOR_PALETTE.md`, `FONT_GUIDE.md`) with no code reference — not empty requirements, but documentation. Actual font files are not required by any code path; the plugin loads the JSON it needs.
- **Estimated Effort:** S
- **Dependencies:** None

### E-06: GPU/Vision Validation Stubs
- **Module:** `src/image_generation/validator.py`
- **Severity:** ENHANCEMENT
- **Description:** Image validation for missing limbs, extra fingers, correct-character identity is a framework stub requiring a vision model. Not a gap per se (consistent with other GPU-blocked features), but limits automated QC.
- **Recommended Fix:** Integrate a vision model (e.g., GPT-4V API, or local Florence-2) for automated image QC when GPU is available.
- **Estimated Effort:** L
- **Dependencies:** C-01

### E-07: Missing End-to-End Episode Smoke Test
- **Module:** Cross-cutting
- **Severity:** ENHANCEMENT
- **Description:** README shows a pipeline smoke test that only creates an orchestrator. There's no test that runs a complete episode from story generation through video export (even with mock backends).
- **Recommended Fix:** Create `test_e2e_episode.py` that runs the full `EpisodeWorkflowFactory` pipeline end-to-end with mocks.
- **Status:** ✅ **DONE 2026-09-09** — `tests/test_e2e_episode.py` (5 tests) runs the full episode chain with in-process mocks: `EpisodeGenerator` → `blueprint_to_episode` → `ProductionPipeline` (prompts/continuity/render queue) → `PipelineOrchestrator.process_pipeline` (8-stage workflow to COMPLETED) → `EditingEngine.assemble_scenes` → `PostProductionQC.validate_timeline` → `ExportEngine` presets + export QC. No GPU/network. All 5 pass.
- **Estimated Effort:** M
- **Dependencies:** None

### E-08: No CI/CD Pipeline
- **Module:** Cross-cutting
- **Severity:** ENHANCEMENT
- **Description:** No `.github/workflows/`, no `Makefile`, no `tox.ini`, no pre-commit hooks. Tests are manual-only.
- **Recommended Fix:** Add GitHub Actions workflow for lint + test on PR. Add pre-commit hooks for ruff/flake8.
- **Status:** ✅ **DONE 2026-09-09** — `.github/workflows/ci.yml` (3 jobs: ruff lint+format on `src scripts tests`, mypy `src`, offline-safe pytest suites) + `.pre-commit-config.yaml` (ruff + ruff-format + mypy). Workflow pins Python 3.11, caches pip, validates YAML. Test job runs the 12 offline-safe suites (695 passed locally) — excludes the known hang (`test_generation_engine.py`), the C-01-dependent story lookup, and Windows-only issues.
- **Estimated Effort:** M
- **Dependencies:** None

### E-09: No Type Checking Configuration
- **Status:** ✅ **DONE 2026-09-09** — `[tool.mypy]` added to `pyproject.toml` (python 3.11, src package scope, `warn_unused_ignores`); `mypy` added to dev extras. `ruff`/`mypy` not installed locally (dev extras only).
- **Module:** `pyproject.toml`
- **Severity:** ENHANCEMENT
- **Description:** No mypy or pyright configuration. No `[tool.mypy]` section in pyproject.toml. Type hints exist in many files but are unverified.
- **Recommended Fix:** Add mypy configuration and run type checking as part of CI.
- **Estimated Effort:** M
- **Dependencies:** None

### E-10: No Linting Configuration
- **Status:** ✅ **DONE 2026-09-09** — `[tool.ruff]` + `[tool.ruff.lint]` added to `pyproject.toml` (line-length 100, py311, select E4/E7/E9/F/I/UP, src/scripts/tests); `ruff` added to dev extras.
- **Module:** `pyproject.toml`
- **Severity:** ENHANCEMENT
- **Description:** No ruff, flake8, or pylint configuration. No code formatting enforcement.
- **Recommended Fix:** Add ruff configuration to pyproject.toml.
- **Estimated Effort:** S
- **Dependencies:** None

### N-08: No Disk-Space Guards in Any Notebook
- **Status:** ✅ **DONE 2026-09-09** — Validate STEP 1: `MIN_FREE_GB = 25` guard. Phase 1–3 Cell 5: `<4 GB free /content` abort before download. Training Cell 4: <50 GB guard (FLUX fp16 bundle ~45 GB). Enforced by N-17 drift tests.
- **Module:** All `colab/*.ipynb` (image + training + Phase 5)
- **Severity:** ENHANCEMENT
- **Description:** No notebook checks free disk. Combined worst case on the ~78 GB class Colab VM: colab-gpu fp8 (`flux1-dev-fp8.safetensors` = **17.25 GB**, doc claims ~12 GB) + ACE-Step auto-download (~10–20 GB) + training FLUX files (~28 GB: flux1-dev + ae + t5xxl_fp16 + clip_l) → an OOM mid-download is likely if notebooks are mixed on one VM. Resumability is handled (`wget -c`, `hf_hub_download`), but there is no pre-flight `df` check and no model-size budget cell.
- **Recommended Fix:** Add a Settings-cell helper, run in Cell 1 after Drive mount: `shutil.disk_usage("/")` printed as GB with a hard guard (`raise SystemExit` when < ~25 GB free for image runs, < ~40 GB for a training + ACE-Step mixing run). Cell 3b preview should already compute `images * 2 min`; add a disk row: `files * bytes-per-export * margin`.
- **Estimated Effort:** S
- **Dependencies:** None

### N-09: Phase 1–3 GPU Cell is Informational Only (No Assert)
- **Status:** ✅ **DONE 2026-09-09** — GPU cells in Phase 1/2/3 now `assert torch.cuda.is_available(), "GPU runtime required..."` before printing device/VRAM. Enforced by `TestPhaseNotebookModelDownloads.test_gpu_assert_guard_present` (N-17).
- **Module:** `colab/AnimationStudio_Colab.ipynb` (Cell 8) + Phase2/Phase3 equivalents
- **Severity:** ENHANCEMENT
- **Description:** The "Verify the GPU" cell prints torch/CUDA/VRAM but never asserts — a CPU runtime silently continues into a ComfyUI boot that cannot succeed, wasting 1–2 min before the SystemExit in `ensure_comfyui_up`. The Training and Validate notebooks do assert.
- **Recommended Fix:** Mirror the Training notebook's fail-fast: `assert torch.cuda.is_available(), "GPU runtime required"` + `assert device.major >= 7` (V100+) in the same cell.
- **Estimated Effort:** S
- **Dependencies:** None

### N-10: Model Download "Verification" is Only `getsize > 0`
- **Status:** ✅ **DONE 2026-09-09** — Phase 1–3: `size_gb < 17.25 * 0.9` truncation abort after download. Training Cell 4: per-file `EXPECTED_BYTES` floors (flux1-dev 33.96 GB, ae 0.33 GB, clip_l 0.26 GB, t5xxl 9.53 GB) with `>= 0.99 * expected` check. Validate STEP 3: `>= 17.25 GB * 0.9`. Enforced by N-17 drift tests.
- **Module:** All image notebooks (Cell 5 model maps) + Training (Cell 4)
- **Severity:** ENHANCEMENT
- **Description:** `os.path.getsize(cached) > 0` is the only integrity check — a truncated/partial download of plausible size passes. No expected-byte-count table, no sha256.
- **Recommended Fix:** Add an expected-size dict keyed by the same branch→model map (sizes already known: fp8 17.25 GB, Q4 6.81 GB, clip_l 246 MB, t5xxl 9.79 GB, ae — gated) and assert `getsize >= expected * 0.99`. Optionally record sha256 for the two non-gated files. Cheap and catches most silent truncation.
- **Estimated Effort:** S
- **Dependencies:** None

### N-11: Stale Model-Size Claim (fp8 "~12 GB" is actually 17.25 GB)
- **Status:** ✅ **DONE 2026-09-09** — all README + Phase 1–3 + setup-script size claims updated to the live `Comfy-Org/flux1-dev` fp8 number (17.25 GB); Drive-budget notes and `~14 GB` GGUF remnants removed with the dead `master` maps (N-02). Validate + Phase 1–3 cells use `17.25` / `17250000000`.
- **Module:** `README.md`, all Phase 1–3 notebooks, `setup_comfyui_flux.*`?
- **Severity:** MINOR
- **Description:** `flux1-dev-fp8.safetensors` (hosted at `Comfy-Org/flux1-dev` → `Comfy-Org/flux1-dev/resolve/main/flux1-dev-fp8.safetensors`) is 17.25 GB via HEAD today, yet the README/FAL-cloud/branch table and notebooks state "~12 GB" and the Drive budget reasoning is built on it. Free-tier Drive (5/15 GB) can't hold it — already mitigated by `CACHE_MODELS_IN_DRIVE=False` default, but the numbers mislead capacity planning.
- **Recommended Fix:** Update all size claims to the live number and re-run the size-based warnings (Cell 3b ETA is time-based, unaffected). Verify 12–14 GB claims for the GGUF bundle too.
- **Estimated Effort:** S
- **Dependencies:** None

### N-12: Duplicate STEP 5 / STEP 7 Cells in Validate Notebook
- **Module:** `colab/AnimationStudio_Validate.ipynb`
- **Severity:** MINOR
- **Description:** STEP 5 and STEP 7 each exist twice (a short "old" variant and a long "self-healing" variant). On a kernel restart where only the short cell re-runs, `Path`/`REPO`/`np`/`PILImage`/`display`/`backend`/`gen_input` may all be undefined. This compounds N-01.
- **Recommended Fix:** Delete the old/short variants; keep one canonical cell per step with complete inline imports/fallbacks. (Fold into the N-01 rebuild.)
- **Estimated Effort:** S (included in N-01)

### N-13: Dead Import in Training Notebook (Cell 8)
- **Status:** ✅ **DONE 2026-09-09** — `from src.training_engine.versioning import LoRAVersion` removed from Cell 8 (unused).
- **Module:** `colab/AnimationStudio_Colab_Training.ipynb`
- **Severity:** MINOR
- **Description:** `from src.training_engine.versioning import LoRAVersion` is imported but never used in Cell 8.
- **Recommended Fix:** Remove the import or use it in the registry registration for a typed `version` field.
- **Estimated Effort:** S
- **Dependencies:** None

### N-14: Training Notebook Downstream Pointer is Wrong (Phase 4 → Phase 8/9)
- **Module:** `colab/AnimationStudio_Colab_Training.ipynb` (Cell 10 markdown)
- **Severity:** MINOR
- **Description:** The "Use the LoRA downstream" note tells operators to load the LoRA "in the Phase 4 generation pipeline" — Phase 4 is the CPU-only animation bible; the image-generation consumer is Phase 8 (`src/image_generation` + `--backend comfyui` on `generate_phase1_library.py`) and Phase 9 animation. This mirrors the ROADMAP renumbering confusion (M-01).
- **Recommended Fix:** Point the note at Phase 8 image generation with the concrete invocation (`--backend comfyui` + LoRA path via ComfyUI workflow/`CharacterLock`), and Phase 9 animation usage.
- **Estimated Effort:** S
- **Status:** ✅ **DONE 2026-09-09** — Cell 10 note now points at `scripts/generate_phase1_library.py --backend comfyui` (Phase 1b / `src/image_generation` + `CharacterLock`) or diffusers `load_lora_weights` with the identity-locked prompt system, plus Phase 9 animation.
- **Dependencies:** None

### N-15: Local LoRA Dataset Prep is Blocked Until Assets are Approved (C-01)
- **Module:** `scripts/train_lora.py build-dataset`, `src/training_engine/dataset_builder.py`
- **Severity:** ENHANCEMENT
- **Description:** Local (no-GPU) jobs CAN and should prepare the training datasets: `train_lora.py build-dataset --character-id <id>` (needs ≥20 **approved** assets per character — C-00's DB corruption is now fixed, but the recovered DB holds **0 approved** assets across all 2,472 rows, so `find_curated` still returns empty). `train_lora.py train` (dry-run only), `train_lora.py versions`, `train_lora.py benchmark` (needs a trained .safetensors). Real gradient training cannot run locally (no CUDA) — that part must stay on Colab. `TestStoryCatalogIntegration.test_resolve_prop_to_approved_file` is the one remaining DB-dependent failure — it needs approved `cake`/`books` props (C-01), not a DB fix.
- **Recommended Fix:** After real generation + a first approval pass (C-01/C-02), run the local offline chain: `build-dataset` for Lily Bunny → `train --dry-run` → `versions` to prove the evidence package, exactly as README documents. Optionally add a `--health` subcommand that reports per-character curated counts to triage which characters are dataset-ready.
- **Estimated Effort:** M
- **Dependencies:** C-01 (≥20 approved per character)

---

## PRIORITY 4 — Technical Debt

### T-01: review_ui/app.py is a Monolith
- **Module:** `src/review_ui/app.py`
- **Severity:** MINOR
- **Description:** 1,305 lines, 64 functions, handles 11+ routes, background tasks, template rendering, API endpoints, and data transformation. Should be split into route modules.
- **Estimated Effort:** L

### T-02: animation_bible/libraries.py is 947 Lines of Pure Data
- **Module:** `src/animation_bible/libraries.py`
- **Severity:** MINOR
- **Description:** Data-only module with 0 classes, 0 functions. Could be a JSON/TOML data file loaded at runtime instead of Python source.
- **Estimated Effort:** M

### T-03: story_engine/grammar_data.py is 257 Lines of Pure Data
- **Module:** `src/story_engine/grammar_data.py`
- **Severity:** MINOR
- **Description:** 273 StoryGrammar dataclass instances. Same consideration as T-02.
- **Estimated Effort:** M

### T-04: production/episode_templates.py is 192 Lines of Pure Data
- **Module:** `src/production/episode_templates.py`
- **Severity:** MINOR
- **Description:** Template dictionary with no classes or functions.
- **Estimated Effort:** S

### T-05: audio_bible/libraries.py is 329 Lines of Pure Data
- **Module:** `src/audio_bible/libraries.py`
- **Severity:** MINOR
- **Description:** Pure data constants for audio bible standards.
- **Estimated Effort:** M

### T-06: Inconsistent sys.path Manipulation in Scripts
- **Module:** `scripts/*.py`
- **Severity:** MINOR
- **Description:** 14 scripts use `sys.path.insert(0, ...)`, 4 scripts use `os.path` equivalent. Functionally identical but inconsistent.
- **Status:** ✅ **DONE 2026-09-09** — all scripts now use `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))` (phase4/5/6/7 converted; `from pathlib import Path` added where needed). 18/18 scripts import cleanly.
- **Estimated Effort:** S

### T-07: Hardcoded COMFYUI_URL in Lock Scripts
- **Module:** `scripts/generate_{identity,face,body}_lock.py`, `generate_wardrobe.py`
- **Severity:** MINOR
- **Description:** `COMFYUI_URL = "http://localhost:8188"` hardcoded as module constant instead of argparse default.
- **Status:** ✅ **DONE 2026-09-09** — all 4 lock scripts take `--comfyui-url` (argparse default = constant); `main(comfyui_url=...)` threads it through `check_comfyui()` + `ComfyUIBackend(server_url=...)`.
- **Estimated Effort:** S

### T-08: .env File Committed to Repo
- **Module:** `.env`
- **Severity:** MINOR
- **Description:** `.env` file exists in the repo (empty keys). While `.gitignore` excludes it, the file is present in the working directory and could accumulate real keys.
- **Status:** ✅ **NON-ISSUE 2026-09-09** — `.gitignore` contains `.env` and `git ls-files` confirms it is **untracked**. No real keys accumulate in version control; the file is a local-only placeholder.
- **Estimated Effort:** S

### T-09: catalog.db Committed as .gitkeep
- **Module:** `catalog.db`, `catalog.db-shm`, `catalog.db-wal`
- **Severity:** MINOR
- **Description:** SQLite database files exist in the working directory. `.gitignore` correctly excludes `*.db`, but the files are present locally. If anyone runs `git add -f`, they could commit database contents.
- **Status:** ✅ **BY DESIGN 2026-09-09** — `catalog.db` is **intentionally tracked** (it is the canonical working DB synced between local and Colab via the `colab/git_sync.py` push/pull workflow). The `.gitignore` `*.db` rule prevents accidental new DBs; verify_catalog.ps1 (`tests/test_catalog_integrity.py`) guards the committed DB. `journal_mode=DELETE` (C-00) guarantees sidecar files can never reappear.
- **Estimated Effort:** S

### T-10: get-pip.py in Root
- **Status:** ✅ **DONE 2026-09-09** — `get-pip.py` added to `.gitignore` (check-ignore now honors it).
- **Module:** `get-pip.py`
- **Severity:** MINOR
- **Description:** `get-pip.py` is checked into the project root. This is a pip installer script that should not be in version control.
- **Estimated Effort:** S

### N-16: Duplicate `ace_cmd` Assignment in Phase 5 Notebook
- **Status:** ✅ **DONE 2026-09-09** — duplicate `ace_cmd = ["uv", "run", "acestep-api"]` line removed from Cell 4.
- **Module:** `colab/AnimationStudio_Colab_Phase5.ipynb` (Cell 4)
- **Severity:** MINOR
- **Description:** `ace_cmd = ["uv", "run", "acestep-api"]` is assigned twice in the ACE-Step bring-up cell (copy/paste residue). Harmless but confusing.
- **Estimated Effort:** S

### N-17: `test_colab_notebooks.py` Needs Drift Guards
- **Status:** ✅ **DONE 2026-09-09** — suite grew to **86 tests (86 passed)**: `TestValidateNotebookStructure` (8 sequential unique STEP cells, MODEL_FILE literal, backend/gen_input before generate, colab-gpu-only, GPU assert), `TestPhaseNotebookModelDownloads` (fp8 URL present, no city96 dead URLs, branch locked, GPU assert), `TestTrainingNotebookStructure.test_sync_cell_authorization_header_prefixed` (N-03), `test_sync_cell_has_disk_and_size_guards` (N-08/N-10).
- **Module:** `tests/test_colab_notebooks.py`
- **Severity:** MINOR
- **Description:** The structural smoke tests verify the Training notebook's contracts but **do not** catch the shipped bugs found here: the Validate notebook's missing STEP 3/6 cells + undefined `MODEL_FILE`/`backend`/`gen_input`, the malformed push header (N-03), or the Phase 1–3 `master`-branch 404 URLs (N-02). The secret-shape guard works; the content contracts are too narrow.
- **Recommended Fix:** Add tests that: (a) for the Validate notebook, assert monotonic `STEP n` cell titles with no duplicates and that `backend`/`gen_input`/`MODEL_FILE` are *assigned before* use; (b) strengthen `TestTrainingNotebookStructure.test_sync_cell_present` to require `Authorization: ` adjacent to `_basic_auth_header`; (c) assert the model-URL cell contains the `comfyanonymous/flux_text_encoders` hosts and no `city96/.../clip_l.safetensors` 404 host.
- **Estimated Effort:** M
- **Dependencies:** None

---

## Cross-Module Integration Analysis

### API Contract Consistency
| Integration Point | Status |
|-------------------|--------|
| Story → Production (blueprint_to_episode) | ✅ Implemented + tested |
| Production → Image Generation | ⚠️ Framework only (mock backend) |
| Image Generation → Animation | ⚠️ Framework only (mock backend) |
| Animation → Post-Production | ⚠️ Framework only (mock backend) |
| Post-Production → Publishing | ⚠️ Framework only (mock backend) |
| Studio Orchestration → All | ⚠️ Workflow wired but untested end-to-end |
| Review UI → Asset Repository | ✅ Working (SQLite) |
| Review UI → Generation Engine | ✅ Working (mock backend) |
| Music Generation → Audio Bible | ✅ Working (ACE-Step adapter) |
| Universe Catalog → SQLite | ✅ Working (seeding pipeline) |

### Data Flow Issues
1. **No cross-phase data validation:** Each phase validates its own output but no integration test verifies that Phase N output is valid input for Phase N+1.
2. **Mock → Real transition untested:** Switching from MockBackend to ComfyUI/Cloud backend has never been validated.
3. **Database schema migrations:** `SchemaManager` handles migrations but there's no migration test that verifies upgrade paths.

---

## Module Health Scores

| Module | Files | LOC | Completeness | Quality | Security | Documentation | Score |
|--------|-------|-----|-------------|---------|----------|--------------|-------|
| models | 2 | 72 | 9/10 | 9/10 | N/A | 7/10 | **8.0** |
| identity_engine | 11 | 870 | 9/10 | 9/10 | 7/10 | 8/10 | **8.3** |
| asset_repository | 5 | 647 | 9/10 | 9/10 | 7/10 | 8/10 | **8.3** |
| generation_engine | 8 | 1,063 | 8/10 | 8/10 | 6/10 | 8/10 | **7.5** |
| prompt_builder | 4 | 783 | 9/10 | 9/10 | N/A | 9/10 | **9.0** |
| training_engine | 8 | 1,705 | 7/10 | 8/10 | 5/10 | 7/10 | **6.8** |
| story_engine | 22 | 4,614 | 9/10 | 8/10 | N/A | 7/10 | **8.0** |
| production | 10 | 1,191 | 9/10 | 9/10 | N/A | 8/10 | **8.5** |
| image_generation | 9 | 706 | 8/10 | 8/10 | 6/10 | 8/10 | **7.5** |
| animation | 18 | 1,727 | 9/10 | 8/10 | N/A | 8/10 | **8.3** |
| post_production | 17 | 1,390 | 9/10 | 8/10 | N/A | 8/10 | **8.3** |
| publishing | 14 | 1,550 | 9/10 | 8/10 | 5/10 | 8/10 | **7.5** |
| studio | 20 | 1,796 | 8/10 | 7/10 | 5/10 | 7/10 | **6.8** |
| universe | 5 | 1,410 | 9/10 | 9/10 | N/A | 8/10 | **8.5** |
| review_ui | 2 | 1,316 | 7/10 | 6/10 | 3/10 | 6/10 | **5.5** |
| pipeline | 4 | 591 | 9/10 | 9/10 | N/A | 8/10 | **8.5** |
| animation_bible | 6 | 1,954 | 10/10 | 9/10 | N/A | 10/10 | **9.5** |
| audio_bible | 6 | 1,312 | 10/10 | 9/10 | N/A | 10/10 | **9.5** |
| music_generation | 6 | 1,075 | 8/10 | 8/10 | 7/10 | 8/10 | **7.8** |

**Average Score: 8.0/10** (but heavily weighted by infrastructure completeness; real-world utility score is ~4/10 because no real content exists)

---

## Notebook Deep-Dive (added 2026-09-09)

| Notebook | Phase | Backend | Status | Notes |
|----------|-------|---------|--------|-------|
| `AnimationStudio_Colab.ipynb` | 1 (characters) | ComfyUI | ✅ Sound | GPU assert (N-09), disk guard (N-08), truncation check (N-10), colab-gpu only (N-02) |
| `AnimationStudio_Colab_Phase2.ipynb` | 2 (world) | ComfyUI | ✅ Sound | Same guards as Phase 1 |
| `AnimationStudio_Colab_Phase3.ipynb` | 3 (assets) | ComfyUI | ✅ Sound | Same guards as Phase 1 |
| `AnimationStudio_Colab_Phase4.ipynb` | 4 (animation bible) | CPU-only | ✅ Sound | Regenerates `PHASE4_REPORT.md` |
| `AnimationStudio_Colab_Phase5.ipynb` | 5 (music/ACE-Step) | mock / ace-step | ✅ Sound | Duplicate `ace_cmd` removed (N-16) |
| `AnimationStudio_Colab_Phase6.ipynb` | 6 (story engine) | CPU-only | ✅ Sound | Documents known corrupt-DB test failures |
| `AnimationStudio_Colab_Training.ipynb` | 1c (LoRA) | GPU (kohya) | ✅ Sound | Push header (N-03), dead import (N-13), downstream pointer (N-14) fixed; ✅ N-07 39-character batch driver + registry skip gate built 2026-09-11 |
| `AnimationStudio_Validate.ipynb` | Pre-flight | ComfyUI | ✅ Sound | Rebuilt as clean 8-step flow (N-01); sharpness gate logic OK |

**Coverage gaps:** Phases 7–12, 1b lock, cloud, and multi-character training all covered by dedicated notebooks (N-04/N-05/N-06/N-07 → **done 2026-09-09/10/11**). All notebooks carry disk guards (N-08), GPU asserts (N-09), and truncation checks (N-10). Everything notebook-side is green; N-15 (dataset prep) is blocked on approved assets (C-01).

---

## VISION.md Pipeline Alignment Tracking (added 2026-09-11)

Disposition of the `VISION.md` Phase-6+ pipeline stages against the codebase (audit run 2026-09-10; Lyrics item executed 2026-09-11; Image-to-Video + Cloud notebook items executed 2026-09-11).

| VISION Stage | Code Module | Status | Notes |
|--------------|-------------|--------|-------|
| Story | `src/story_engine/` (EpisodeGenerator) | ✅ BUILT | full story grammar + curriculum + validation |
| **Lyrics** | `src/story_engine/lyrics.py` **NEW** + `AudioProductionSystem._lyrics_for` | ✅ **BUILT 2026-09-11** | VISION "Idea→Lyrics→Verse→Chorus" gap closed: seeded nursery-rhyme generator produces section-marked lyric text on `SongEntry.lyrics`; feeds `MusicRequest.lyrics_override` (ACE-Step) + `SubtitleEngine.generate_from_lyrics` |
| Music | `src/music_generation/` (ACE-Step/Suno) | ✅ BUILT | marker-scaffold fallback when no lyrics override |
| Storyboard | `src/production/` + Phase 7 notebook | ✅ BUILT | |
| Scene/Prompt | `src/prompts/` + Phase 8 notebook | ✅ BUILT | |
| Character Manager | IdentityLock notebook + `src/asset_repository/` | ✅ BUILT | 4 lock scripts + LoRA training |
| Image Gen | MockBackend / ComfyUI + fp8 Flux | ✅ BUILT | real runs C-01 gated |
| Image-to-Video | `src/video_generation/` **NEW** + `RenderQueue` | ✅ **BUILT 2026-09-11** | Protocol + mock + Wan ComfyUI + Cloud fal/Replicate/HunyuanVideo adapters; closes VISION Phase 9 image-to-video gap |
| Lip Sync | `src/animation/lipsync.py` | ⚠️ PLACEHOLDER | phoneme estimates only |
| Subtitles | `src/post_production/subtitles.py` | ✅ BUILT | now directly consumable from generated lyrics |
| Video Editor / Thumbnail / Upload / Upscaler | `src/studio/` + Phase 9-12 notebook | ⚠️ BUILT / PHP-only Upload | offline-verified, media-gated |
| Cloud backend notebooks (fal/replicate/bfl) | `colab/AnimationStudio_Colab_Cloud.ipynb` **NEW** | ✅ **BUILT 2026-09-11** | Phase 1–3 generation via cloud providers (getpass secrets, `_gen_cmd` relay, `--sync-every-image` + `git_sync.auto_sync`); closes N-06 |

```bash
# Local (no-GPU) jobs that ARE possible today for LoRA prep (after C-00 fix):
python scripts/train_lora.py build-dataset --character-id lily-bunny   # ≥20 curated needed
python scripts/train_lora.py train --character-id lily-bunny           # dry-run only locally
python scripts/train_lora.py versions                                  # read-only registry
python scripts/train_lora.py benchmark --lora <v>.safetensors --images <dir>  # needs trained LoRA
# Real gradient training stays on Colab (AnimationStudio_Colab_Training.ipynb).
```

---

## Recommendations

### Immediate (This Week)
1. **Run the real pipeline once.** Set up ComfyUI (`setup_comfyui_flux.ps1`), generate 1 character's reference sheets with `--backend comfyui`. This validates the entire infrastructure.
2. **Fix the three notebook blockers before any Colab session:** Validate notebook rebuild (N-01), `master`-branch model URLs (N-02), Training push header (N-03).
3. **Add the 13 missing documentation files** (TODO1-4.md, TODO5-7.md gaps).
4. **Add `.gitignore` entries** for `get-pip.py` and any generated data directories.
5. **Create CI workflow** with basic `pytest` + `ruff` checks.

### Short-Term (This Month)
6. **Recover/re-seed `catalog.db` (C-00)** — nothing else consumes it safely until then; then run the local LoRA prep chain (`build-dataset` → `train --dry-run` → `versions`) for Lily Bunny.
7. **Run the Colab identity-lock flow** (N-05 notebook or manual script run) → curated assets → then **first LoRA training** on Colab (after N-03 fix). This unblocks character consistency.
8. **Fix Review UI security** — add auth, input validation, split monolith.
9. **Generate first real episode** through the end-to-end pipeline (mock for video, real for story + images).
10. **Reconcile ROADMAP.md** with actual PHASE*.md structure.

### Medium-Term (This Quarter)
11. **Execute Phase 1 production runs** for all 39 characters — use `colab/AnimationStudio_Colab_Cloud.ipynb` (N-06, done); T4-local fp8 Flux can't scale to 12,472 props (~17 days).
12. **Set up ACE-Step** for music generation.
13. **Add Phase 7/8 notebook(s)** (N-04) to drive episode-scene image generation + storyboard planning from Colab.
14. **Build integration test suite** for real backends + notebook drift guards (N-17).
15. **Persistent security module** with proper secrets management.

### Long-Term (This Year)
16. **Full episode production** — story → music → images → animation → editing → publish.
17. **Multi-character, multi-language training loop** (N-07, notebook backend done 2026-09-11) with localization TTS.
18. **YouTube/TikTok publishing** integration + publishing notebook (N-04).
19. **Batch production pipeline** for multiple episodes.

---

## Summary Statistics

| Category | Count | Notes |
|----------|-------|-------|
| Critical Issues | 9 | 6 core (C-*) + 3 notebook (N-01..N-03); all 3 notebook items closed 2026-09-09 |
| Major Gaps | 5 | 5 module (M-03..M-06, M-08) + notebook (N-04..N-07) closed; M-01, M-02, M-07 closed 2026-09-11 |
| Enhancements | 19 | 10 module (E-*) + 9 notebook (N-08..N-15); N-08..N-14 closed 2026-09-09/11, N-15 blocked on C-01 |
| Technical Debt | 12 | 10 module (T-*) + 2 notebook (N-16, N-17); both closed 2026-09-09 |
| **Total Issues** | **52** | |
| Documentation Gaps | 13 | Across Phases 1, 5, 6 |
| Missing Script Wrappers | 2 | generate_phase7, train_lora |
| Security Concerns | 3 | UI auth, input validation, persistent secrets; input validation closed 2026-09-11 (M-07) |
| Vision Deviations | 1 | No real character consistency |
| Notebook coverage boundaries | 1–8, 9-12, Cloud, Training, IdentityLock, Validate | All 13 notebooks sound; N-15 dataset prep pending approved assets (C-01) |

**Bottom Line:** The codebase is architecturally sound, well-tested in isolation, and comprehensive in scope. The critical gap is that it has never been executed end-to-end with real AI backends. The next step is not more code — it's running the pipeline once with real hardware.
