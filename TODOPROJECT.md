# TODOPROJECT.md — Comprehensive Codebase Audit
# Generated: 2026-09-09 | All 12 Phases Scanned | Updated: 2026-09-12 (full-module deep audit — see "Deep Audit 2026-09-12")

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

### ~~M-03: 13 Documentation Gaps (Phase 1 + Phase 5 + Phase 6)~~ → ✅ **VERIFIED CLOSED 2026-09-12**
- **Module:** `Universe/`, `Audio/`, `StoryEngine/`
- **Severity:** MAJOR
- **Description:**
  - Phase 1: 8 doc gaps (ReferenceSheets/, ModelSheets/, ColorPalette/, Fonts/ empty; 4 category INDEX files missing)
  - Phase 5: 1 structural gap (Audio/Vocals/ missing .gitkeep)
  - Phase 6: 4 missing standalone docs (Humor/, Emotions/, Seasons/, Metadata/ guides)
- **Recommended Fix:** Create the 13 missing documentation files.
- **Estimated Effort:** M
- **Dependencies:** None
- **Done:** Audit 2026-09-12 verified all 13 items are now present with real content: `Universe/ReferenceSheets/CHARACTER_REFERENCE_GUIDE.md`, `Universe/ModelSheets/MODEL_SHEET_GUIDE.md`, `Universe/ColorPalette/brand-palette.json`, `Universe/{Community,Families,Fantasy,Friends}/INDEX.md`, `Audio/Vocals/.gitkeep`, `StoryEngine/{Humor,Emotions,Seasons,Metadata}/*_GUIDE.md` — all exist (committed 2026-07-28/30 in `07ab57cc`/`64b5bb60`); Fonts guide lives at root `Fonts/FONT_GUIDE.md` (61 lines) with `Universe/Fonts/` holding only `.gitkeep` (acceptable — no code path reads it). The M-03 ticket was stale: the gap list predated those commits.

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

## Deep Audit 2026-09-12 (full-module scan — every src/ module, UI deep dive, all 13 notebooks validated)

Performed a full-module audit scanning all **20 src packages (~27,000 LOC, 200+ py files)**, all 36 test files, all 13 Colab notebooks, CI, config, and every PHASE/VISION/doc claim. Findings below are **new or sharpened** since 2026-09-11; previously-tracked items (C-*, M-*, N-*, T-*, E-*) remain assigned.

### A-01 (CRITICAL): No real-media consumer path exists — post-generation modules flip status instead of executing
- **Module:** `animation`, `post_production`, `publishing`, `studio`
- **Evidence:** `animation/render.py` `RenderQueue/RenderPipeline` is a pure state machine (`process_next()` marks RENDERING, no renderer invoked); `post_production/exports.py:88` only returns preset dicts (no encode/ffmpeg/file write); `post_production/color.py:107` `apply()` ignores input & returns a canned dict; `publishing/publishing.py:59` `publish()` flips an enum (no YouTube/upload client); `studio/orchestrator.py:71` `execute_ready_steps()` immediately marks tasks COMPLETED without executing; `studio/resources.py:120` RenderFarm moves `_pending→_rendered` without rendering; `studio/api.py:24` `StudioAPI.call()` returns a dict (no HTTP server); `animation/regeneration.py:68` always returns `regenerated=True`; `post_production/enhancement.py` frame_interpolation never calls RIFE.
- **Impact:** Today the ONLY path that can produce real media is `video_generation` (`WanVideoBackend`/`CloudVideoBackend` — real ComfyUI/fal/Replicate REST clients). Everything downstream is planning/framework code. End-to-end "episode" runs are simulations (test_e2e_episode.py), and tests explicitly assert only wiring.
- **Recommended fix:** This is the single most important gap vs. the VISION. Stage the work: (1) prove one real image (ComfyUI/cloud), (2) prove one real i2v clip, (3) wire a real ffmpeg export step that consumes clips, (4) attach a real uploader (YouTube Data API) behind a config flag. Do NOT build more frameworks until the chain produces bytes.
- **Effort:** XL · **Dependencies:** C-01 (GPU/cloud), C-04
- **Status:** **Stage 3 partially FIXED 2026-09-12 (real-media consumer path).** `post_production` now has a byte-producing export stage: new `src/post_production/export_executor.py` + `ExportEngine.export()` — `FfmpegExportExecutor` concatenates clip files, re-encodes to the preset resolution/fps/bitrate, muxes audio stems, and writes a real MP4 (subprocess ffmpeg + ffprobe duration probe); `ConcatExportExecutor` is the offline byte-copy fallback that still writes a real file; resolver honors explicit `executor=` → `FFMPEG_EXECUTOR` env (`auto`/`ffmpeg`/`mock`) → auto (ffmpeg if installed, else concat). **16 new tests** (registry modes, input/audio validation, offline byte-copy, real ffmpeg transcode from generated `testsrc` clips, 2-clip concat, audio-stem mux, missing-binary/missing-stem errors) — full `test_post_production.py` = 184 passed. Remaining A-01 stages: (1) prove one real image, (2) prove one real i2v clip — both C-01 (GPU/cloud) gated; (4) YouTube/cloud uploader behind a config flag — `publishing.py` still only flips `status→PUBLISHED` (VISION Phase 14 unmet). `animation/render.py`, `studio/*` and `publishing/*` remain framework state machines.

### A-02 (MAJOR): "AI" story engine is template/rule-based, not LLM — documentation overstates capability
- **Module:** `story_engine`, `lyrics.py`
- **Evidence:** Zero LLM imports anywhere in `src/` (no openai/httpx/requests/transformers-LLM usage). `EpisodeGenerator` = `random.choice` over hardcoded banks; title/description are f-string templates; dialogue = canned phrase tables; `LyricsGenerator` = template-bank picker (`_VERSE_BANKS`/`_CHORUS_BANKS`) with seeded `random.Random`. Deterministic per seed, combinatorial.
- **Status:** **Lyric-key mismatch FIXED 2026-09-12** (`lyrics.py` `_SONG_TYPE_ALIASES` maps `color→colors`, `animal→animals`; 3 regression tests added). The **core LLM-vs-template gap remains OPEN** (VISION Phase 6 story generator).
- **Impact:** Any reader of VISION.md / README ("AI story generation") expects generative output. The system is a variant/template engine — fine as scaffolding, mislabeled as AI. Remaining `topic` param of `LyricsGenerator.generate` is still **unused** (documented, S).
- **Recommended fix:** Either (a) integrate a real LLM adapter (OpenAI/Anthropic/transformers) behind the `EpisodeGenerator` Protocol with the template engine as the offline fallback, or (b) re-scope docs to "rule-based generative scaffolding".
- **Effort:** L (LLM) or M (re-scope)

### A-03 (MAJOR): `audio_bible` produces zero audio — TTS/voice engines named but never invoked
- **Module:** `audio_bible/production.py`, `animation/lipsync.py`, `music_generation`
- **Evidence:** `AudioProductionSystem.plan_episode` builds an `AudioPlan` (voice briefs, lip-sync tracks, SFX name lists) but never calls Kokoro/XTTS/Piper (referenced only as strings); lip-sync is a letter→mouth heuristic mapper; no orchestra wiring feeds `AudioPlan.songs[].lyrics` → `MusicRequest.lyrics_override` automatically (music_generation and audio_bible are disconnected).
- **Recommended fix:** Add a TTS adapter + wire `AudioPlan → music_generation`; at minimum document the disconnect.
- **Effort:** L
- **Status:** **FIXED 2026-09-12 (voice adapter + wiring; lip-sync heuristic unchanged).** (1) **New `src/voice_generation/` package** mirroring `music_generation`: Pydantic `VoiceRequest/VoiceStatus/VoiceResult`; `@runtime_checkable VoiceGenerationBackend` protocol; typed taxonomy (`VoiceBackendError`/`NotConfigured`/`BackendUnavailable`/`GenerationFailed`); `get_backend` registry (env `TTS_BACKEND`, default `mock`); `backend_for_engine` mapping the bible's approved engines (Kokoro → real adapter, XTTS v2 → refusing stub citing CPML R&D-only, Piper → refusing stub citing GPL gate, unknown → mock); `build_voice_request` deriving voice code per character (seed map incl. Narrator `af_heart`, Lily Bunny `af_sarah`, Ben Bear `am_michael`, …) + pace per speech-speed label; deterministic offline `MockBackend` (seed chain: request.seed → ctor.seed → stable (speaker,text) hash); real `KokoroBackend` (lazy `pip install kokoro>=0.9.4 soundfile`, presence gate at submit, KPipeline synthesis + resample to requested rate). (2) **`AudioProductionSystem` wiring** (production.py): `synth_voice(text, character, *, backend_name/seed/brief)` — explicit backend wins, else bible engine with license-gate fallback (Kokoro if installed, else offline mock) so the CPU-only pipeline always produces voice; `synth_plan_voices(plan)` synthesizes every dialogue clip (voice_code/duration_s per line); `music_request_for(song)` bridges `SongEntry.lyrics → MusicRequest.lyrics_override` (lazy import keeps the audio_bible → music_generation dependency one-way). (3) **`scripts/generate_phase7.py`** now accepts `--lyrics` / `--lyrics-file` (explicit `lyrics_override`). **Added `tests/test_voice_generation.py` — 50 offline tests** (models, bible-aware request assembly, engine resolution, mock determinism/seed-chain/sample-rate, Kokoro presence+validation+scripted-pipeline path, Piper/XTTS refusal surfaces, file persistence, production wiring, phase7 CLI lyrics dry-runs). Remaining: lip-sync stays phoneme-estimate (no audio alignment — VISION's LatentSync/MuseTalk), and real Kokoro output is unproven until the engine is installed on operator hardware (C-01-gated).

### A-04 (MAJOR): UI has zero authentication/authorization + open-redirect via referer + unbounded API limit
- **Module:** `src/review_ui/app.py`
- **Evidence:** No auth on ANY route (POST `/approve/`, `/reject/`, `/promote/`, `/regenerate/`, `/generate`, `/seed`, `/api/assets/...` are all unauthenticated; any webpage can drive state changes/GPU jobs if the UI is reachable — it is, via LocalTunnel in the Colab notebooks). `_get_referer` (app.py:1387) redirects to the raw `referer` header (open-redirect). `GET /api/candidates` `limit=Query(50)` had no `ge/le` bounds (M-07 validated `/generate` but not this).
- **Status:** **FIXED 2026-09-12.** (1) **Limit bounded** — `limit=Query(50, ge=1, le=500)` + 422 regression test. (2) **Token auth** — `create_app(ui_token=...)` optional gate; all 10 POST routes (`/motion/prompt`, `/music/prompt`, `/music/generate`, `/generate`, `/seed`, `/approve/`, `/reject/`, `/regenerate/`, `/promote/`, `/api/assets/...`) accept `?token=` or `X-UI-Token` header, 401 otherwise; GETs stay public so the UI remains browsable; default `ui_token=None` keeps local runs unchanged. (3) **Open-redirect closed** — `_get_referer` only accepts a same-origin absolute URL (host:port must match the server) or a local `/path` (not `//host`); scheme-relative `//host`, `javascript:`/other schemes, and malformed values like `:::` fall back to `/`. (4) **Notebook tunnels secured** — the 6 UI-launch notebooks (Colab, IdentityLock, Phase2, Phase3, Phase8, Phase9to12) now generate a per-run `secrets.token_urlsafe(18)` token, pass it via `ui_token=UI_TOKEN`, and print the tunnel URL with `?token=<token>` appended. **Added `tests/test_review_ui_security.py` — 33 tests** (token gate on every POST route × wrong/correct token/header, GETs public, referer allowlist incl. foreign-host, javascript:, scheme-relative, garbage, same-host, relative-path).
- **Impact:** If the tunnel URL leaks or is guessed, an attacker can mutate the production DB and queue expensive batches. Local tool → medium risk; tunneled → critical.
- **Recommended fix:** Add a simple token auth (header/query `?token=` generated at startup, default off behind a flag) + CSRF, and replace referer redirects with explicit success/error responses or a bounded internal referer allowlist.
- **Effort:** M

### A-05 (MAJOR): `comfy_backend` failure paths & hardcoded node IDs (core real-backend bug — blocks C-01)
- **Module:** `src/generation_engine/comfy_backend.py`
- **Evidence:** Undefined-variable `NameError`s in ComfyUI failure paths (fallback confirmations reference names that don't exist when the server errors); hardcoded workflow node IDs (e.g. `"8"`) make the backend brittle to template changes.
- **Status:** **FIXED 2026-09-12.** (1) REST generate now handles terminal HTTP errors, validation-error bodies, and missing `prompt_id` with structured `metadata["error"]` (was `KeyError: 'prompt_id'`); history poll treats failed `status_str` (`error`/`failed`) jobs as failures, tolerates transient poll errors, and skips failed image views without aborting. (2) Node-role IDs centralized into `_NODE_KSAMPLER`/`_NODE_POSITIVE_CLIP`/`_NODE_NEGATIVE_CLIP`/`_NODE_LATENT`/`_NODE_LOADER` constants. **Added `tests/test_comfy_backend.py` — 9 offline failure-path tests** (refused / HTTP 500 / validation-body / non-dict body / failed history / view failure / success / load-model nonfatal) — the audit's recommended "unit-test the failure paths (mock transport that raises)" was previously missing.
- **Recommended fix:** Next hardening when C-01 setup begins: integration-test against a real (or containerized) ComfyUI with a live template export.
- **Effort:** M

### A-06 (MAJOR): Cloud video backend corrupts request metadata + masks failures
- **Module:** `src/video_generation/cloud.py`
- **Evidence:** After download, `seed=0, frames=0` were set (request metadata lost); transient-poll swallows `GenerationFailed→running`, masking persistent API errors until the 900s deadline.
- **Status:** **FIXED 2026-09-12.** (1) **Seed/frames preservation** — `submit()` stashes the `VideoInput` per job_id; both `_download_fal`/`_download_replicate` echo `request.seed`/`request.frames` (regression test added). (2) **Transient-vs-terminal poll** — `_poll_fal`/`_poll_replicate` now catch only `BackendUnavailable` (timeout/reset/DNS) and keep returning `"running"`; a `GenerationFailed` (persistent HTTP 4xx/5xx or malformed body from the status endpoint) propagates immediately so the persistence loop surfaces it instead of masking it as `"running"` until the 900s deadline. **Added 5 regression tests** (transient→running ×2 providers, persistent→raise ×2 providers, and a `generate()`-level test proving a persistent HTTP error aborts on the first poll).
- **Recommended fix:** Preserve seed/frames from the request; distinguish transient (network) vs terminal (GenerationFailed) when retrying.
- **Effort:** S/M

### E-21 (ENHANCEMENT): `UpscalingPipeline` is PIL resize, misnamed as AI; validator "has_seed" is hardcoded True
- **Module:** `src/image_generation/upscaler.py`, `validator.py:62`
- **Evidence:** `upscale_to_4k()` = `Image.resize(LANCZOS)` — no Real-ESRGAN/GFPGAN; `"has_seed": True` is hard-coded (no seed field checked). `ReferenceImageManager` leaks file handles (`Image.open` never closed).
- **Recommended fix:** Rename docs to "high-res resize"; wire Real-ESRGAN when GPU available; check seed; use context managers.
- **Effort:** S/M

### E-22 (ENHANCEMENT): README/PROJECT.md still contain stale claims
- **Evidence:**
  - README §Phase 3 says "12,472 approved assets" — **false**; catalog.db has **2,508 rows, 0 approved** (README's own Production note says the correct number — internal contradiction).
  - README "Available routes" table omits `/motion`, `/music`, `/api/assets/...`, `/asset-image/{id}`, `/api/overview`, `/api/jobs`, `/api/candidates`, `/api/music/jobs`.
  - PROJECT.md says "Colab notebooks: 8" — there are **13**; "review_ui: 1,316 LOC / 2 files" — actually 4 files (~1,546 LOC incl. app.py 1,520); DB row count "2,472" — stale (2,508); `video_generation` package is missing from the module inventory table entirely.
  - `.env.example` documents only 4 vars but code reads `ACESTEP_BASE_URL`, `ACESTEP_API_KEY`, `MUSIC_BACKEND`, `KOHYA_SS_PATH`, `VIDEO_BACKEND`, `CUDA_VISIBLE_DEVICES` (in setup scripts), `FAL/REPLICATE/BFL_API_KEY`.
  - CI's test job runs only the 12 offline-safe suites (785) and skips the 5 Review-UI suites (≈119 more, 904 total) for environment/stability reasons documented in README; acceptable, but note review_ui validation now makes them safe to add if desired.
- **Recommended fix:** Fix the README Phase-3 "12,472" claim; refresh PROJECT.md module inventory (LOC, file counts, notebook count, add video_generation); align `.env.example`.

### A-07 (OBSERVATION): Simulation-shade consistency across the codebase (9/20 modules)
- Pattern: Protocol/base + typed errors + in-memory registry + factory is clean and testable, but engines consistently return canned dicts/metadata/flags that "describe" results instead of producing them (`regenerate()→regenerated=True`, `apply()→"applied"`, `compliance.check→True` rubber-stamps, `publish()→PUBLISHED`). This is the root of most "gap" findings and is **structurally fine** — it makes the whole system mock-testable — but the naming/expectation gap should be surfaced in README (which already does so in the Production Readiness Note). Compliance layer offering hard-coded PASS booleans is the one genuinely misleading part.

### Notebook validation result (2026-09-12) — ALL 13 sound
- Re-ran import-resolution over every cell in every notebook: every `src.*` / `scripts.*` / `colab/comfy_helpers`, `colab/git_sync` reference resolves to a real file; each notebook has real (non-stub) code cells (no `pass`-only, no TODO stubs — only the Validate notebook contains one intentional TODO marker); GPU/disk/size guards present; `colab-gpu`-only enforced. Verdict matches the existing "ALL 13 notebooks sound" table below. The 13 include: base Colab, Cloud, IdentityLock, Phase2–Phase8, Phase9to12, Training, Validate.

### Revised module health scores (deep audit 2026-09-12)

| Module | Files | LOC | Complete | Quality | Security | Docs | Tests |
|---|---|---|---|---|---|---|---|
| models | 2 | 72 | 9 | 9 | – | 7 | 7 |
| identity_engine | 11 | 870 | 9 | 8 | 7 | 8 | 8 |
| asset_repository | 5 | 647 | 9 | 9 | 7 | 8 | 8 |
| generation_engine | 8 | 1063 | 7 | 7 | 6 | 8 | 7 |
| prompt_builder | 4 | 783 | 9 | 9 | – | 9 | 8 |
| training_engine | 8 | 1705 | 7 | 8 | 5 | 7 | 8 |
| story_engine | 23 | 4824 | 8 | 7 | 6 | 5 | 8 |
| production | 10 | 1291 | 8 | 8 | – | 7 | 8 |
| image_generation | 9 | 666 | 6 | 7 | 7 | 6 | 8 |
| animation | 18 | 1691 | 3 | 6 | 7 | 4 | 7 |
| video_generation | 7 | 913 | 6 | 7 | 8 | 9 | 6 |
| post_production | 18 | 1649 | 3 | 6 | 7 | 5 | 7 |
| publishing | 14 | 1358 | 3 | 6 | 5 | 5 | 7 |
| studio | 20 | 1710 | 3 | 5 | 4 | 6 | 7 |
| universe | 5 | 1410 | 9 | 9 | – | 8 | 8 |
| review_ui | 4 | 1546 | 7 | 7 | 3 | 7 | 8 |
| pipeline | 4 | 591 | 8 | 8 | – | 8 | 7 |
| animation_bible | 6 | 1954 | 8 | 8 | 7 | 8 | 7 |
| audio_bible | 6 | 1341 | 6 | 8 | 7 | 8 | 8 |
| music_generation | 6 | 1075 | 7 | 9 | 9 | 9 | 9 |
| voice_generation | 7 | 796 | 7 | 8 | 7 | 8 | 9 |

**Overall: YELLOW→RED for real-media readiness.** Infrastructure quality is high (tests, docs, structure excellent); **real-content production readiness is ~2/10** — the only genuinely real media path is `video_generation` cloud/Wan, and even it is unproven end-to-end. Everything above the generation layer is framework code today.

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
| post_production | 18 | 1,649 | 9/10 | 8/10 | N/A | 8/10 | **8.3** |
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

## VISION.md Pipeline Alignment Tracking (added 2026-09-11; refreshed 2026-09-12 against Deep Audit A-01..A-03, E-21)

Disposition of the `VISION.md` "Final Architecture" pipeline + named tool-stack stages against the codebase. **Bottom line: 11/13 stages exist structurally; 2 are genuinely NOT implemented (Lip Sync = phoneme heuristic only, Upload = status-flip only); Story and Upscaler diverge from VISION's letter (rule-based vs LLM, PIL vs Real-ESRGAN); Video Editor keeps timeline/editing as data structures but now has a real ffmpeg export stage (A-01 stage 3, 2026-09-12).**

| VISION Stage | Code Module | Status | Notes |
|--------------|-------------|--------|-------|
| **Story (Phase 6)** | `src/story_engine/` (EpisodeGenerator) | ⚠️ **DIVERGES** | **A-02:** template/rule-based grammar engine, NOT an AI/LM story generator (zero LLM imports anywhere in `src/`); conversation-style inputs are templated context, not prompts |
| **Lyrics** | `src/story_engine/lyrics.py` **NEW** + `AudioProductionSystem._lyrics_for` | ✅ **BUILT 2026-09-11** | seeded nursery-rhyme generator → `SongEntry.lyrics` → `MusicRequest.lyrics_override` (ACE-Step) + `SubtitleEngine.generate_from_lyrics`. Known bug A-02: song_types `"color"/"animal"` never match bank keys `"colors"/"animals"` → silent fallback to generic `educational`; `topic` param unused |
| Music (Phase 4) | `src/music_generation/` (ACE-Step/Suno) | ✅ BUILT | ACE-Step real (in-memory mock default); Suno stub (API-shape only) |
| **Voices / TTS (Phase 5)** | `src/voice_generation/` **NEW** + `audio_bible/production.py` wiring | ✅ **BUILT 2026-09-12** | **A-03 closed:** TTS adapter package (mock default + real Kokoro `af_*`/`am_*` codes + Piper/XTTS license stubs); `AudioProductionSystem.synth_voice`/`synth_plan_voices`; voice codes seeded per character (Narrator `af_heart`, Lily `af_sarah`, …); real Kokoro output C-01-gated (CPU-capable) |
| Storyboard (Phase 7) | `src/production/` + Phase 7 notebook | ✅ BUILT | |
| Scene Planner / Prompt (Phase 6/8) | `src/prompts/` + Phase 8 notebook | ✅ BUILT | |
| Character Manager | IdentityLock notebook + `src/asset_repository/` | ✅ BUILT | 4 lock scripts + LoRA training (gradient gated) |
| Image Gen (Phase 8) | MockBackend / ComfyUI + fp8 Flux | ✅ BUILT | real runs C-01 gated |
| Image-to-Video (Phase 9) | `src/video_generation/` **NEW** + `RenderQueue` | ✅ **BUILT 2026-09-11** | Protocol + mock + Wan ComfyUI + Cloud fal/Replicate/HunyuanVideo adapters |
| **Lip Sync (Phase 10)** | `src/animation/lipsync.py` | ⚠️ **PLACEHOLDER / DIVERGES** | letter→phoneme heuristic only; VISION's LatentSync/MuseTalk/Hallo/SadTalker named but have no adapter seam (A-03); output is phoneme estimate, no audio+video alignment |
| Subtitles (Phase 12) | `src/post_production/subtitles.py` | ✅ BUILT | consumable directly from generated lyrics |
| **Video Editor (Phase 11)** | `src/post_production/` editing/timeline models + `export_executor.py` | ⚠️ **PARTIAL** | **A-01 stage 3 (2026-09-12):** timeline/editing remain data structures (no VISION's DaVinci Resolve), but `ExportEngine.export()` now consumes clip files and writes **real MP4 bytes** — ffmpeg concat → preset re-encode (resolution/fps/bitrate) → audio-stem mux (`FFMPEG_EXECUTOR=auto\|ffmpeg\|mock`; offline byte-copy `ConcatExportExecutor` fallback) |
| Thumbnail (Phase 13) | `src/image_generation/thumbnail.py` + `publishing/thumbnail` | ✅ BUILT | functional compositing |
| **Upscaler (Best-Stack)** | `src/image_generation/upscaler.py` | ⚠️ **DIVERGES** | **E-21:** VISION names Real-ESRGAN; implementation is PIL LANCZOS resize |
| **Upload (Phase 14)** | `src/publishing/publishing.py` | ❌ **NOT IMPLEMENTED** | **A-01:** `PublishingEngine.publish()` only flips `status → PUBLISHED` + stores a manually-passed `video_url`; **no YouTube/TikTok/Instagram/Facebook/Pinterest client exists** (note in table previously said "PHP-only Upload") — VISION Phase 14 is wholly unmet |
| Cloud backend notebooks (fal/replicate/bfl) | `colab/AnimationStudio_Colab_Cloud.ipynb` **NEW** | ✅ **BUILT 2026-09-11** | Phase 1–3 generation via cloud providers; closes N-06 |

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
| Critical Issues | 9 | 6 core (C-*) + 3 notebook (N-01..N-03); all closed 2026-09-09; **A-01 adds "no real-media consumer path"** |
| Major Gaps | 4 | M-04..M-06, M-08 open; M-01, M-02, M-07 closed 2026-09-11, M-03 VERIFIED CLOSED 2026-09-12; A-02..A-06 added 2026-09-12 |
| Enhancements | 19 | 10 module (E-*) + 9 notebook (N-08..N-15); most closed; E-21, E-22 added 2026-09-12 |
| Technical Debt | 12 | 10 module (T-*) + 2 notebook (N-16, N-17); all closed 2026-09-09 |
| Deep Audit 2026-09-12 | 6 | A-01..A-06 findings (see Deep Audit section); **A-01 stage-3 export stage** (real ffmpeg bytes-producing executor + offline fallback), A-02 lyric-key, A-03 TTS adapter+lyrics wiring, A-04 limit+auth+referer, A-05 comfy failure paths, A-06 seed/frames+poll semantics **fixed 2026-09-12** |
| **Total Issues** | **58** | |
| Documentation Gaps | 13 | Verified ALL CLOSED 2026-09-12 (M-03) |
| Security Concerns | 3 | UI auth, input validation, persistent secrets; input validation closed 2026-09-11 (M-07); UI auth now A-04 |
| Vision Deviations | 1 | No real character consistency |
| Notebook coverage boundaries | 1–8, 9-12, Cloud, Training, IdentityLock, Validate | ALL 13 notebooks sound (re-verified 2026-09-12); N-15 dataset prep pending approved assets (C-01) |

**Bottom Line:** The codebase is architecturally sound, well-tested in isolation, and comprehensive in scope. The critical gap is that it has never been executed end-to-end with real AI backends — and the deep audit (2026-09-12) shows the modules BELOW image/video generation are planning/framework code that do not yet consume or produce real media. The next step is not more code — it is (1) proving one real image, (2) proving one real i2v clip, (3) wiring a real ffmpeg export, then running the pipeline once with real hardware.
