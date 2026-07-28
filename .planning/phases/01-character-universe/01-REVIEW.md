# Phase 1: Character Universe & Bible — Plan Review

**Reviewer:** gsd-plan-checker
**Date:** 2026-07-28
**Status:** BLOCK — plans cannot achieve phase goal as written

---

## Verdict: BLOCK

**Rationale:** The 5 plans build excellent pipeline infrastructure (generation engine, identity engine, asset repository, training engine, review UI) and produce Lily Bunny's documentation, but they **do not generate a single character image or train a single LoRA**. The phase goal requires "20 permanent characters with complete documentation — reference sheets, expression libraries, pose libraries, outfit variants, model sheets, prompt templates, and LoRA training." After executing all 5 plans, zero reference sheets, zero expressions, zero poses, zero outfits, and zero LoRAs will exist. Only 1 of 20 characters gets documented (Lily Bunny bio.md). The infrastructure is necessary but the execution artifacts that define "done" for this phase are absent.

---

## Requirement Coverage

| Requirement | Plans Claiming It | What's Actually Delivered | Status |
|-------------|------------------|---------------------------|--------|
| **CHAR-01** Persistent Character Database | 01-01, 01-02, 01-05 | SQLite schema + repository ABC + SQLiteCharacterRepository | ✅ Covered |
| **CHAR-02** Character reference sheet generation | 01-02, 01-03, 01-05 | Generation backends exist, prompt templates exist, but **zero reference sheets generated** (MockBackend only, no GPU/cloud execution) | ⚠️ Infrastructure exists, no output |
| **CHAR-03** Expression library | 01-03, 01-04, 01-05 | Prompt templates for 22 expressions exist in docs, but **zero expression images generated** | ⚠️ Infrastructure exists, no output |
| **CHAR-04** Pose library | 01-03, 01-04, 01-05 | Prompt templates for 20 poses exist, but **zero pose images generated** | ⚠️ Infrastructure exists, no output |
| **CHAR-05** Outfit/wardrobe variants | 01-03, 01-04, 01-05 | Prompt templates for 12+ outfits exist, but **zero outfit images generated** | ⚠️ Infrastructure exists, no output |
| **CHAR-06** Personality profiles, relationships, catchphrases, emotion matrix | 01-01, 01-02, 01-05 | Lily Bunny bio.md has all required sections | ✅ Covered (1 of 20 characters) |
| **CHAR-07** LoRA training pipeline | 01-04 | TrainingBackend ABC + KohyaAdapter exist, but **zero LoRAs trained** (gracefully fails without GPU) | ⚠️ Infrastructure exists, no output |
| **CHAR-08** Reusable prompt templates and negative prompt standards | 01-01, 01-04, 01-05 | PromptBuilder + templates.json + lily-bunny-prompt-sheet.md + NegativePrompt/standards.md | ✅ Covered |
| **CHAR-09** Age progression variants | 01-04, 01-05 | Age variant templates exist in PromptTemplates, age progression documented in bio.md | ✅ Covered (templates only, no images) |

**Coverage verdict:** All 9 CHAR requirements have plans claiming them, but 6 of 9 require generated images/LoRAs that the plans cannot produce. CHAR-02/03/04/05/07 deliver infrastructure but not the actual assets the requirements call for.

---

## Decision Coverage

| Decision | Plans | Reflected? | Notes |
|----------|-------|-----------|-------|
| **D-01:** 20 characters, 5 categories | 01-05 | ✅ | Universe category directories created (Characters, Families, Friends, Community, Fantasy) |
| **D-02:** One-by-one full completion | 01-05 | ✅ | Lily Bunny done first; other characters have empty directories only |
| **D-03:** Lily Bunny first character | 01-05 | ✅ | Complete bio.md, prompt templates, style guide |
| **D-04:** Hybrid pipeline (generate→score→filter→review→lock) | 01-01, 01-02, 01-03 | ✅ | Full pipeline infrastructure built |
| **D-05:** Brand Score system (8 weights) | 01-01 | ✅ | BrandScore class with exact weights from decision |
| **D-06:** 7-layer identity scoring | 01-02 | ✅ | All 7 plugins with correct weights |
| **D-07:** Plugin-based Python package | 01-01, 01-02 | ✅ | identity_engine/ package with ScoringPlugin protocol |
| **D-08:** ComfyUI for R&D, diffusers for production | 01-03 | ✅ | ComfyUIBackend marked R&D-only; diffusers-based backends for production |
| **D-09:** Generation Engine with pluggable adapters | 01-01, 01-03 | ✅ | GenerationBackend ABC + 5 concrete backends |
| **D-10:** "Train Early, Retrain Once" lifecycle | 01-04 | ✅ | TrainingConfig, versioned datasets, benchmark scores |
| **D-11:** LoRA versioned like software | 01-04 | ✅ | version field in TrainingConfig, TrainingResult |
| **D-12:** 3-layer storage | 01-01, 01-05 | ✅ | Pipeline Workspace (workspace/), SQLite Catalog (catalog.db), Universe Library (Universe/) |
| **D-13:** SQLite for metadata | 01-01 | ✅ | SQLiteAssetRepository with full schema |
| **D-14:** Repository pattern | 01-01 | ✅ | AssetRepository ABC + SQLiteAssetRepository |
| **D-15:** Asset lifecycle states | 01-01, 01-04 | ✅ | States defined in AssetModel; transitions enforced in Review UI |
| **D-16:** Only approved assets enter Universe Library | 01-05 | ⚠️ | Universe Library gets docs/directories, but no pipeline for approving assets exists yet |
| **D-17:** Simple web UI for human review | 01-04 | ✅ | FastAPI + Jinja2 with all specified features (side-by-side, scores, actions, batch compare) |
| **D-18:** Training Engine with adapter pattern | 01-04 | ✅ | TrainingBackend ABC + KohyaAdapter |
| **D-19:** Python/diffusers for batch production | 01-03 | ✅ | diffusers-based backends, Python job queue, seed generator |

**Coverage verdict:** All 19 locked decisions are reflected in the plans. Good traceability. D-16 is partially implemented (Universe Library structure exists but no automated approval pipeline routes assets into it).

---

## Findings

### BLOCKER: Phase goal not achievable — zero character images, zero LoRAs, 1 of 20 characters documented

**Dimension:** Requirement Coverage / Goal-Backward Verification
**Plans:** 01-01 through 01-05 (systemic)
**Severity:** BLOCKER
**Description:**
The 5 plans build comprehensive pipeline infrastructure (generation engine, identity engine, asset repository, training engine, review UI, prompt builder) and create documentation for Lily Bunny. However, when all plans execute, the following phase deliverables will NOT exist:

1. **Zero reference sheet images** for any character (CHAR-02: "front, 3/4, profile, back angles")
2. **Zero expression images** for any character (CHAR-03: "20+ expressions")
3. **Zero pose images** for any character (CHAR-04: "15+ poses")
4. **Zero outfit images** for any character (CHAR-05: "12+ outfits")
5. **Zero trained LoRAs** for any character (CHAR-07)
6. **Zero generated images total** — MockBackend is used for testing but never for production output
7. **19 of 20 characters undocumented** — only Lily Bunny has a bio.md

The ROADMAP success criteria require:
- "Multi-angle reference sheets are **generated** for each character and **stored** in the permanent Universe library" — ❌ No reference sheets generated
- "Expression libraries (20+ expressions) **exist per character**" — ❌ No expression images exist
- "A Production LoRA (v1.0) is **trained** for each character" — ❌ No LoRAs trained

The infrastructure (generation backends, scoring, job queue) works correctly but is never pointed at a real image generation task. The CloudAPIBackend wrapper exists in Plan 01-03 but no task calls it to produce character images. Plan 01-05 (Lily Bunny) creates documentation and `.gitkeep` placeholder directories but never invokes the pipeline to fill them.

**Root cause:** The plans separate "build the pipeline" from "run the pipeline." They complete the former but omit the latter. The MockBackend (intended for GPU-free testing) becomes the de facto sole backend because no task configures cloud API keys and executes a real generation job.

**Fix options (pick one):**

**Option A — Add execution tasks (recommended):**
Add a Plan 01-06 (or extend 01-05) that:
1. Configures CloudAPIBackend with environment variables for fal.ai or Replicate API
2. Executes the GenerationJob pipeline for Lily Bunny: generate 50-100 candidates → score → diversity filter → save to SQLite
3. Launches the Review UI for human approval
4. After approval, generates reference sheets, expressions, poses, outfits via the pipeline
5. Documents the LoRA training setup (actual training needs GPU, but the dataset preparation pipeline should be executed)
6. Repeats for Ben Bear (at minimum starting the second character to validate the one-by-one workflow)

**Option B — Explicitly scope-reduce the phase:**
If cloud API keys are unavailable and no GPU machine exists, then:
1. Rename the phase to "Phase 1a: Character Pipeline Infrastructure & Bible Foundation"
2. Update ROADMAP success criteria to reflect "pipeline ready" rather than "assets exist"
3. Add a follow-up phase "Phase 1b: Character Asset Generation" that executes the pipeline when GPU is available
4. Document that current scope is infrastructure + documentation, with asset generation deferred

**Option C — Add cloud generation as a manual review step:**
Add a task to Plan 01-05 that:
1. Documents how to configure cloud API keys (already in .env.example)
2. Provides a CLI command `python -m pipeline.generate_lily` that runs the full generation pipeline
3. Includes acceptance criteria that the operator has run this and verified output

---

### WARNING: 7 scoring plugins vs 8 Brand Score dimensions — mapping gap

**Dimension:** Task Completeness / Research Alignment
**Plans:** 01-01, 01-02
**Severity:** WARNING
**Description:**
The plans create 7 identity scoring plugins (DINOv2 40%, CLIP 20%, Color 10%, Part 10%, Pose 5%, Expression 5%, Style 10%) with weights summing to 100%. The BrandScore (D-05) has 8 dimensions with different weights: prompt_accuracy 20%, character_consistency 20%, technical_quality 15%, facial_appeal 15%, child_friendliness 10%, color_harmony 10%, silhouette_recognizability 5%, style_consistency 5%.

The expected mappings are:
- DINOv2 plugin → `character_consistency` ✓
- CLIP plugin → `prompt_accuracy` ✓
- ColorVerification → `color_harmony` ✓
- StyleVerification → `style_consistency` ✓
- PartVerification → likely `silhouette_recognizability` (not clear)
- PoseVerification → likely `child_friendliness` (not clear)
- ExpressionVerification → likely `facial_appeal` (not clear)

But `technical_quality` (15% weight) has no dedicated plugin — the simple-aesthetics-predictor from RESEARCH.md is listed as an optional `[scoring]` dependency but has no corresponding plugin file. The plans also never clarify how `facial_appeal` is computed (is it expression_verify, or a separate scoring dimension?).

**Fix:** Either add a `technical_quality` plugin using the aesthetics predictor (install via optional `[scoring]` deps), or document how these 8 Brand Score dimensions map to the 7 plugin outputs (e.g., facial_appeal = weighted average of expression + pose scores).

---

### INFO: 20 files in Plan 01-01 — exceeds recommended threshold

**Dimension:** Scope Sanity
**Plan:** 01-01
**Severity:** INFO
**Description:**
Plan 01-01 modifies 20 files. This is above the 15+ blocker threshold. However, 8 of these are `__init__.py` stubs (2-5 lines each), so the actual engineering work is concentrated in ~12 substantive files. The task breakdown (3 tasks) is well-structured. This is an observation, not a change request, but the planner should consider whether the foundation work could be split into 2 Wave 1 plans.

**Note:** Plan 01-05 creates 19 files, but 12 are `.gitkeep` files and 3 are short markdown docs, so it's similarly inflated.

---

### INFO: 19 remaining characters have no detailed plan coverage

**Dimension:** Goal-Backward Verification / Scope Sanity
**Plan:** 01-05
**Severity:** INFO
**Description:**
The CONTEXT.md explicitly decided on "Full 20 characters" and "One-by-one full completion. Finish Lily entirely before starting Ben." Plan 01-05 fully documents Lily Bunny but only creates empty category directories for the remaining 19 characters. This is consistent with the one-by-one approach — the infrastructure is designed for all 20, and Lily is the first. However, the phase goal says "20 permanent characters" and the ROADMAP says Phase 1 has 5 plans. With only 1 character documented and no generation tasks, extending Phase 1 with additional character plans may be needed if cloud/GPU generation becomes available.

---

### INFO: State machine test — data flow gap

**Dimension:** Task Completeness
**Plan:** 01-01, Task 3
**Severity:** INFO
**Description:**
Plan 01-01 Task 3 tests the state transition `test_state_transition_validity` with `draft→generated→scored→shortlisted→approved→production→archived`. However, the test only validates state transitions at the data layer (SQLite). It does not test that the state machine interacts correctly with the actual pipeline — e.g., that `GenerationJob` changes state from `draft` to `generated` after calling a backend, or that the Review UI's approve button triggers `scored→shortlisted`. This is acceptable for Wave 1 since GenerationJob and Review UI are in Waves 2-3, but the integration between state and orchestration should be covered in Wave 2/3 tests.

---

## Wave Dependency & Execution Analysis

| Plan | Wave | Depends On | Files Modified | Tasks | Valid? |
|------|------|-----------|----------------|-------|--------|
| 01-01 | 1 | [] | 20 (12 substantive) | 3 | ✅ |
| 01-02 | 1 | [] | 9 | 3 | ✅ |
| 01-03 | 2 | [01-01] | 9 | 3 | ✅ |
| 01-04 | 2 | [01-01] | 11 | 3 | ✅ |
| 01-05 | 3 | [01-02, 01-03, 01-04] | 19 (7 substantive) | 3 | ✅ |

**Dependency graph:** Acyclic ✅
**Wave assignments:** Correct ✅
**Parallel execution (Wave 1):** 01-01 and 01-02 have no file overlap ✅
**Parallel execution (Wave 2):** 01-03 and 01-04 have no file overlap ✅
**Total tasks:** 15 (3 per plan) ✅

---

## Research Alignment

| Research Finding | Plan Coverage | Status |
|-----------------|--------------|--------|
| No GPU — use cloud API backends, MockBackend for testing | 01-03: CloudAPIBackend, MockBackend, graceful degradation everywhere | ✅ |
| Python/diffusers for production, ComfyUI for R&D | 01-03: ComfyUIBackend marked R&D-only, diffusers backends | ✅ |
| SQLite for metadata, filesystem for binaries | 01-01: SQLiteAssetRepository, filesystem paths | ✅ |
| FastAPI + Jinja2 for review UI | 01-04: FastAPI app with Jinja2 templates | ✅ |
| Kohya SS for LoRA training | 01-04: Training Engine ABC + KohyaAdapter | ✅ |
| Adapter architecture for all backends | 01-01/03/04: ABCs for Generation, Repository, Training | ✅ |
| color-palette-extractor [SUS] flagged | 01-02: Falls back to sklearn KMeans | ✅ |
| Pitfall 4: Not designing for GPU-less development | All: MockBackend, graceful degradation, CPU device default | ✅ |

---

## Validation Alignment

**VALIDATION.md Wave 0 Requirements coverage:**

| Wave 0 Requirement | Creating Plan | Status |
|--------------------|--------------|--------|
| `tests/conftest.py` — shared fixtures | 01-01, Task 2 | ✅ |
| `tests/test_identity_engine.py` — all plugin tests | 01-02, Task 2 | ✅ |
| `tests/test_generation_engine.py` — adapter interface, mock backend | 01-03, Task 3 | ✅ |
| `tests/test_asset_repository.py` — schema, CRUD, state transitions | 01-01, Task 3 | ✅ |
| `tests/test_prompt_builder.py` — all template types | 01-04, Task 1 | ✅ |
| `tests/test_training_engine.py` — adapter interface | 01-04, Task 2 | ✅ |

**Nyquist Compliance check:**
- All tasks have `<automated>` verify commands ✅
- No watch-mode flags ✅
- No 3 consecutive tasks without verify (all tasks verified) ✅
- No MISSING references (all test files are created within their plans) ✅
- Feedback latency under 30s ✅

---

## AGENTS.md Compliance

**Dimension 10:** SKIPPED (no AGENTS.md found in project root)

---

## Architectural Tier Compliance

**Dimension 7c:** All capabilities are assigned to the correct architectural tiers per RESEARCH.md's Architectural Responsibility Map ✅
- Image generation → Generation Engine (Python/diffusers) ✅
- Identity scoring → Identity Engine ✅
- Asset metadata → SQLite Catalog ✅
- Human review UI → Web App (FastAPI) ✅
- LoRA training → Training Engine (Kohya SS) ✅

---

## Cross-Plan Data Contracts

**Dimension 9:** No conflicting data transformations detected across plans. Each subsystem owns its data transformations:
- AssetRepository → all plans use the same Pydantic models from `src/models/schemas.py` ✅
- GenerationOutput → consumed by scoring pipeline, saved via AssetRepository ✅
- PromptBuilder outputs → consumed by GenerationJob orchestrator ✅

---

## Verification Command Format Sanity

No `^` anchor issues, no `2>/dev/null || echo` swallowing, no hard-coded count assertions detected ✅

---

## Summary

### What's Excellent
- **Architecture:** Adapter patterns, repository pattern, plugin-based scoring — all properly designed for long-term maintainability
- **Decision traceability:** All 19 D-* decisions are reflected in plan tasks
- **Testing strategy:** Comprehensive test infrastructure with MockBackend for GPU-free testing
- **Graceful degradation:** Every ML-dependent component handles missing GPU/API keys gracefully
- **Documentation templates:** Lily Bunny's bio.md, prompt templates, style guide, color palette are production-quality

### What's Blocking
- **No character images generated:** Zero reference sheets, expressions, poses, or outfits will exist after plan execution
- **No LoRAs trained:** The training pipeline exists but cannot execute without GPU
- **1 of 20 characters documented:** Phase goal requires all 20 characters
- **Pipeline infrastructure built but never executed:** The CloudAPIBackend, GenerationJob orchestrator, and IdentityScorer are never used to produce actual deliverables

### Recommendation

**This phase needs significant revision to be achievable.** The core problem is that the plans build the factory but never start production. The recommended fix path:

1. **Extend Plan 01-05 (or add Plan 01-06):** Add tasks that configure the CloudAPIBackend with API keys, execute the generation pipeline for Lily Bunny through the full workflow (generate → score → diversity filter → review → approve), and produce reference sheets, expressions, poses, and outfits. Train the Production LoRA v1.0 via Kohya SS (or cloud LoRA trainer).

2. **Add character generation plans:** Since the ROADMAP says 5 plans but only 1 character is documented, either add plans for remaining characters or explicitly document the scope limitation.

3. **Address scoring-to-BrandScore mapping:** Clarify how the 7 scoring plugins map to the 8 Brand Score dimensions. Add a technical_quality plugin or document the mapping.

**Return to planner for revision.** This is a BLOCK, not a PASS.
