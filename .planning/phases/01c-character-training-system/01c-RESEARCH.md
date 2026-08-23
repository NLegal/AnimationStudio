# Phase 1c: Character Training System - Research

**Researched:** 2026-08-23
**Domain:** LoRA training infrastructure (Python/SQLite offline engine + Kohya ss-scripts on Colab GPU)
**Confidence:** HIGH (codebase gaps verified module-by-module; Kohya contract cited from official sd-scripts docs)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Production Training Reality**
- Build `colab/AnimationStudio_Colab_Training.ipynb` mirroring the existing Phase 4 notebook pattern; the real training run is an operator action on a T4/A100 Colab runtime
- Success criterion "production LoRA v1.0 trained" is satisfied by notebook + proven dry-run path locally, then recorded as `verification_deferred_human` at verify time (no blocking on GPU availability)

**Dataset Source & Curation**
- Training images come from the asset repository filtered to lifecycle state `approved`/`production` for the target character
- Captions follow the existing `DatasetConfig` trigger-word convention (trigger word + descriptor sidecar `.txt` per image)
- Keep existing `DatasetConfig` min/max bounds (20–40 images per ROADMAP)

**Versions & Benchmark**
- No placeholder registry versions — `VersionRegistry` entries are created only by completed real or dry-run trainings
- Benchmark pass threshold reuses identity-engine Brand Score default weights with ≥ 90% consistency requirement per ROADMAP

### the agent's Discretion
- Module layout, CLI surface shape, and test structure follow existing codebase conventions

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CHAR-07 | LoRA training pipeline for character consistency (ComfyUI-FluxTrainer or SDXL-based) | Existing `src/training_engine/` covers ABC/adapter/builder/versioning/benchmark skeletons; research identifies exact gaps: `.txt` sidecars, invalid TOML key, dimension-name mismatch between benchmark and identity engine, in-memory-only registry, zero approved-state assets, missing Flux-specific Kohya flags |
</phase_requirements>

## Summary

Phase 1c does NOT start from zero. All five `src/training_engine/` modules exist and 51 tests pass (`tests/test_training_engine.py` = 14 tests, `tests/test_lora_training.py` = 37 tests; verified locally in 3.43 s). The real work is **gap-closing and integration**: (1) the dataset builder writes captions into a custom `metadata.json` but never writes the `.txt` caption sidecars that Kohya's DreamBooth-style datasets require, and it emits an **invalid TOML key** (`caption_metadata_file`) that sd-scripts' schema validator rejects outright; (2) the benchmark's weight table keys do not match the identity engine's plugin names — plugging the real `IdentityScorer` in today would yield a composite of ~0 because every lookup misses; (3) `VersionRegistry` is in-memory only — the `lora_models` SQL table is defined in `migrations.py` but no runtime code calls `SchemaManager`, so the live `catalog.db` lacks the table and nothing persists version records; (4) the production DB has **zero assets in `approved`/`production` state**, so the locked "filter to approved/production" curation rule yields an empty dataset until a promotion step runs; and (5) `KohyaAdapter._build_command()` omits every Flux-specific requirement (`accelerate launch`, `networks.lora_flux`, `--clip_l/--t5xxl/--ae`, memory flags) that the real Colab run depends on.

Two environment blockers shape planning: the live `catalog.db` is **corrupted** ("database disk image is malformed" on scans/sorts; indexed point-lookups still work — `find_by_character('lily-bunny-uuid')` returned all 164 records cleanly), and there is **no GPU** (nvidia-smi absent), which the locked decisions already absorb via the Colab deferred-verification path.

**Primary recommendation:** Plan three waves — Wave 1 fixes DatasetBuilder (sidecars + valid TOML + min/max bounds + curated-state query) and the identity-engine↔benchmark adapter (name remap + weight alignment + 0.90 threshold) in parallel; Wave 2 adds VersionRegistry persistence (+`promote()`) and a `scripts/train_lora.py` orchestrator with `--dry-run`; Wave 3 delivers the Colab training notebook mirroring the Phase 4 pattern plus docs. Keep everything stdlib-only offline; GPU work lives exclusively in the notebook.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Curated-image extraction & dataset build | API/Backend (`src/training_engine/dataset_builder.py`) | Database (`asset_repository` query) | Pure filesystem transform; repo supplies filtered records |
| Lifecycle-state curation filter | API/Backend (`sqlite_repo` / thin wrapper) | — | SQL-level filtering matches existing `find_approved` pattern |
| Identity scoring baseline | API/Backend (`src/identity_engine`) | — | Plugins own scoring; benchmark consumes via protocol adapter |
| Benchmark evaluation & report | API/Backend (`src/training_engine/benchmark.py`) | — | Offline scoring over provided images; no generation inside engine |
| Version registration/persistence | Database (`lora_models` table / registry store) | API/Backend (`versioning.py`) | Durable records; domain logic stays in dataclasses |
| Actual LoRA training | External service (Colab GPU runtime) | Local dry-run (`kohya_adapter`) | No GPU locally; subprocess path only exercised remotely |
| Artifact sync after training | Client/Operator (Colab notebook cells) | git (`colab/git_sync.py`) | Mirrors Phase 4 notebook sync pattern |

## Gap Analysis (method-by-method vs ROADMAP criteria)

Verified by reading every module of `src/training_engine/` and cross-checking against tests and the live database. `[VERIFIED: codebase]` tags mean confirmed by direct inspection this session.

### Criterion 1 — Dataset builder pipeline extracts curated approved images

**Exists:** `DatasetBuilder.build()` copies images into `train/` + `val/`, shuffles with seed, splits (min 1 val enforced when split > 0), writes `metadata.json` + `dataset_config.toml`. `build_entries_from_assets(assets)` maps repo dicts → `DatasetEntry`. Tested: happy paths pass. `[VERIFIED: codebase]`

| # | Gap | Evidence |
|---|-----|----------|
| G1 | **No `.txt` caption sidecars written.** Captions go only into `metadata.json`. Kohya DreamBooth-style subsets read `caption_extension = '.txt'` files sitting next to each image. CONTEXT locked decision explicitly requires "trigger word + descriptor sidecar `.txt` per image". | `_copy_and_caption()` at dataset_builder.py L126–168 writes no sidecar `[VERIFIED: codebase]` |
| G2 | **Invalid TOML key `caption_metadata_file`.** sd-scripts' voluptuous schema raises `extra keys not allowed`; DreamBooth subsets take `image_dir` (+ optional `class_tokens`, `caption_extension`), fine-tuning subsets take `metadata_file`. Current TOML would fail validation before training starts. Also `caption_prefix = ""` is emitted bare (schema expects string type — works, but pointless). | Generated at dataset_builder.py L188–209; schema at kohya-ss/sd-scripts `library/config_util.py` SUBSET/DATASET schemas [CITED: github.com/kohya-ss/sd-scripts/blob/main/docs/config_README-en.md] |
| G3 | **val/ registered as a training subset** (`num_repeats = 1` under the same dataset): validation images are *trained on*. sd-scripts has native `validation_split` (dataset-level option, with `validation_seed`). Either drop the manual val split in favor of native `validation_split`, or keep manual split but exclude `val/` from subsets. | dataset_builder.py L200–207; `DATASET_ASCENDABLE_SCHEMA` includes `validation_split`, `validation_seed` [CITED: sd-scripts config_util.py] |
| G4 | **No lifecycle-state filtering anywhere in training_engine.** `build_entries_from_assets()` trusts pre-filtered input. Repo surface: `find_approved(character_id, asset_type)` filters `state='approved'` only, requires `asset_type`. Precedent for two-state filter: Review UI wrapper treats `("approved", "production")` as curated (review_ui/app.py L208–213); `export_assets.py --states` defaults to `"shortlisted,approved,production"`. Need either a new repo query (`state IN ('approved','production')`) or caller-side filtering over `find_by_character`. | sqlite_repo.py L349–358 [VERIFIED: codebase] |
| G5 | **Zero curated assets exist.** Live DB state distribution: 935 `scored`, 923 `shortlisted`, **0 approved, 0 production**. Lily Bunny: 164 records (32 expr + 28 pose + 12 outfit + 7 reference + 3 lighting, each ×2 states), 0 curated. Strict locked filter ⇒ empty dataset until promotion happens. All 164 file_paths resolve on disk (relative to repo root); prompts stored per record. | Queried live catalog.db this session [VERIFIED: environment] |
| G6 | **No min/max bounds in `DatasetConfig`.** CONTEXT says "keep existing min/max bounds (20–40)" — **no such fields exist** (only `output_dir/resolution/validation_split/repeat_count/shuffle_seed/caption_prefix/caption_suffix`). The 20–40 range lives only in ROADMAP prose. Phase must ADD `min_images`/`max_images` enforcement (fail or hard-cap with warning). Discrepancy flagged as Assumption A1. | dataset_builder.py L27–38 [VERIFIED: codebase] |
| G7 | Duplicate candidates per variant (same variant scored+shortlisted pairs, e.g. `angry_s438116070.png` scored vs `angry_s1924173694.png` shortlisted) — curation needs a selection rule (e.g. highest brand_score per variant) so one variant ≠ multiple near-identical training images. | DB rows inspected [VERIFIED: environment] |

### Criterion 3 — Versioning matches software release conventions

**Exists:** `LoRAVersion` (parse `v{major}.{minor}`, ordering, `is_production`/`is_experimental`, bump major/minor), `VersionRegistry.register/get_versions/get_latest/get_promoted/get_production_candidates/recommend_next/from_db_records`. Fully tested including immutability and sort order v0.1 < v1.0 < v2.0. Convention already matches software releases. `[VERIFIED: codebase]`

| # | Gap | Evidence |
|---|-----|----------|
| G8 | **In-memory only.** `self._records: dict[str, list[VersionRecord]]` — no persistence. `from_db_records()` exists as a hydrator but nothing reads/writes a store. | versioning.py L141–143 [VERIFIED: codebase] |
| G9 | **`lora_models` table defined but never created.** `_SCHEMA_SQL` in `migrations.py` includes `lora_models (id, character_id, version, file_path, training_config, benchmark_scores, trained_at, promoted)` — exact field match with `VersionRecord`. But `SchemaManager.run_migrations()` has **zero callers**; `SQLiteAssetRepository._init_schema` creates only characters/assets. Live catalog.db contains just those two tables (verified). Constraint says catalog.db schema untouched unless migration explicitly planned ⇒ planner must explicitly decide: apply the already-written migration vs sidecar store (JSON or dedicated sqlite file). Given catalog.db corruption (see E1), a **separate store is lower-risk**. | migrations.py L49–58; grep shows SchemaManager referenced nowhere else [VERIFIED: codebase]; live DB table list [VERIFIED: environment] |
| G10 | **No `promote(character_id, version)` method** — `promoted` is register-time-only. Production flow (train v0.x dry-runs → promote v1.0 after benchmark pass) needs post-hoc promotion. | versioning.py L144–205 [VERIFIED: codebase] |

### Criterion 4 — Benchmark compares against identity scorer baseline

**Exists:** `LoRABenchmark.evaluate(lora_path, character_id, test_images)` scores provided images vs optional `baseline_dir/{character_id}/` images using injected `ScorerProvider`; weighted composite, per-dimension breakdown, improvement %, markdown `report()`. `_derive_version` parses `{character}_v{X.Y}.safetensors`. MockScorerProvider deterministic. Tested. `[VERIFIED: codebase]`

| # | Gap | Evidence |
|---|-----|----------|
| G11 | **Dimension-name mismatch (critical).** Benchmark `_BENCHMARK_WEIGHTS` keys: `dino_similarity, clip_alignment, color_consistency, pose_accuracy, expression_match, style_consistency`. Identity-engine plugin `name` attrs: `character_consistency` (DINOv2 w=0.40), `prompt_accuracy` (CLIP w=0.20), `color_harmony` (w=0.10), `facial_appeal` (Part w=0.10), `silhouette_recognizability` (Pose w=0.05), `child_friendliness` (Expression w=0.05), `style_consistency` (w=0.10). Only `style_consistency` overlaps ⇒ naive adapter yields six dimensions scored 0.0 → composite ≈ 0.075·style. Adapter MUST remap names; see Architecture Patterns. | benchmark.py L148–155; plugins grep of name/weight attrs [VERIFIED: codebase] |
| G12 | **Weights match neither identity-engine table.** Locked decision: "reuses identity-engine Brand Score default weights." Two candidate canonical tables exist in-repo: plugin weights (D-06, sum 1.00: 0.40/0.20/0.10/0.10/0.05/0.05/0.10) and `BrandScore.WEIGHTS` (D-05: prompt_accuracy .20, character_consistency .20, technical_quality .15, facial_appeal .15, child_friendliness .10, color_harmony .10, silhouette .05, style .05 — sums 1.00 but includes `technical_quality` which NO plugin emits, capping achievable total at 0.85). Recommendation (A2): adopt D-06 plugin weights for the benchmark composite — they map 1:1 onto what `ScorerProvider` adapters can actually return. Flag for discuss/planner confirmation. | brand_score.py L22–31; scorer.py L69–81; plugin attrs [VERIFIED: codebase] |
| G13 | **Threshold 0.85 ≠ required ≥ 90%.** `BenchmarkConfig.similarity_threshold: float = 0.85`. Must become 0.90 (or be overridden at call sites — better: change default, update tests). | benchmark.py L41 [VERIFIED: codebase] |
| G14 | **`_generate_test_images` is a documented stub** returning `[]` with a warning. Offline dry-run therefore MUST supply `test_images=` (dataset/curated images serve as the identity-proxy baseline); the Colab notebook generates real post-training samples and passes them. | benchmark.py L321–345 [VERIFIED: codebase] |
| G15 | **Baseline directory convention undefined.** `_load_baseline_images` reads `{baseline_dir}/{character_id}/` — nobody populates it yet. Pre-LoRA approved reference sheets are the natural baseline source (copy N curated refs into `baselines/lily-bunny/` during dataset build). | benchmark.py L347–370 [VERIFIED: codebase] |

### Criterion 2 — Production LoRA v1.0 (deferred-human path)

**Exists:** `KohyaAdapter.train()` builds arg-list command (no shell=True), runs subprocess, registers version on success, returns typed failures for env-not-ready/nonzero-exit/missing-interpreter. `validate_environment()` warns-but-passes without GPU (dry-run friendly). Tested with mocked subprocess. `[VERIFIED: codebase]`

| # | Gap | Evidence |
|---|-----|----------|
| G16 | **Command not Flux-complete.** Missing: `accelerate launch` wrapper (uses bare `sys.executable`); `network_module` default `networks.lora` (Flux requires `networks.lora_flux`); `--clip_l`, `--t5xxl`, `--ae` paths (three separate model files); `--save_model_as=safetensors`; Flux specifics `--guidance_scale=1.0 --timestep_sampling=flux_shift --model_prediction_type=raw --sdpa --gradient_checkpointing --fp8_base --cache_text_encoder_outputs(_to_disk)`; misleading comment claims "resolution passed as width x height" but resolution actually comes from the TOML (fine — fix comment); `caption_dropout_rate` config field never forwarded. Also `--max_data_loader_n_workers 8` is too heavy for Colab's 2-vCPU T4 runtime (use 0–2). | kohya_adapter.py L258–301 [VERIFIED: codebase]; flag list [CITED: mintlify.com/kohya-ss/sd-scripts/training/lora-flux] |
| G17 | **No strict/dry-run mode.** `validate_environment()` returns True when KOHYA_SS_PATH exists even without GPU (advisory warning, comment admits "--dry-run / --check flag" is future work). Local orchestration must guarantee subprocess is NEVER invoked without an explicit override — a `dry_run: bool = False` on TrainingConfig/KohyaAdapter that stops after writing config artifacts is the cleanest fit with locked decision "no placeholder registry versions… created only by completed real or dry-run trainings" (so dry-run registration IS allowed). | kohya_adapter.py L56–79 [VERIFIED: codebase] |

## Standard Stack

### Core (all already project dependencies — ZERO new packages)

| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| Python stdlib (sqlite3, json, pathlib, argparse, subprocess) | 3.13.5 runtime | Persistence, CLI, sidecars, dry-run | Project constraint: stdlib-only unless already in pyproject [VERIFIED: pyproject.toml + STATE history] |
| pytest / pytest-asyncio / pytest-timeout | 9.1.1 installed | Test suite (asyncio_mode=auto, timeout=30) | Existing 51-test baseline extends in place [VERIFIED: pyproject + run] |
| Pillow | ≥11 (dep present) | Any image validation in builder/tests | Already imported by conftest/engine ecosystem [VERIFIED: pyproject] |
| numpy | ≥2.0 (dep present) | Benchmark averaging | Already imported inside benchmark.evaluate [VERIFIED: codebase] |

### Supporting (Colab-runtime-only — never local deps)

| Component | Purpose | When Used |
|-----------|---------|-----------|
| kohya-ss/sd-scripts (git clone in notebook) | `flux_train_network.py` trainer | Notebook cell 2–3, GPU runtime only |
| accelerate, fp8/bf16 torch stack | Trainer requirements | Pulled by sd-scripts requirements in notebook |
| FLUX.1-dev single-file weights + `ae.safetensors` + `t5xxl_fp16.safetensors` + `clip_l.safetensors` | Four required model files (HF gated — needs HF token param) | Notebook download cell [CITED: sd-scripts FLUX LoRA guide] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Separate JSON/SQLite version store | Apply `SchemaManager` migration to catalog.db | Migration honors original design intent but touches a corrupted DB; sidecar store isolates risk. Either is defensible — planner picks one explicitly |
| Native sd-scripts `validation_split` | Manual train/val dirs (current) | Native keeps val out of training automatically; manual split currently trains on val (G3) |
| DreamBooth `.txt` style | Fine-tuning `metadata_file` JSON style | `.txt` sidecars are the locked CONTEXT convention and simplest to inspect/debug |

**Installation:** none — no new packages. (Notebook installs happen inside the ephemeral Colab runtime, outside project scope.)

**Package Legitimacy Audit:** Not applicable — this phase installs no new packages (stdlib + existing pyproject deps only). Colab-side installs (sd-scripts et al.) occur in the operator's throwaway runtime and are covered by notebook documentation, not the project dependency tree.

## Architecture Patterns

### System Architecture Diagram

```
 [Universe Library PNGs]          [catalog.db (corrupt; indexed reads OK)]
        │ 164 Lily assets,              │ find_by_character(idx) OK
        │ prompts in DB                 │ state IN (approved,production) → 0 rows!
        ▼                               ▼
 ┌─────────────────────────────────────────────────────────┐
 │ scripts/train_lora.py  (--dry-run offline orchestrator) │
 │  1. curate: repo query → dedupe per variant             │
 │     → cap 20–40 (min/max bounds)                        │
 │  2. DatasetBuilder.build()                              │
 │     • copy images → train/                              │
 │     • write {image}.txt sidecar captions                │
 │     • write VALID Kohya TOML (image_dir, .txt ext)      │
 │     • copy refs → baselines/{char}/                     │
 │  3. benchmark pre-baseline (ScorerProvider)             │
 │  4a. dry-run: emit TrainingConfig JSON, register        │
 │      v-next as dry-run record                           │
 │  4b. real (GPU only): KohyaAdapter.train(subprocess)    │
 └──────────────┬───────────────────────┬──────────────────┘
                ▼                       ▼
   [VersionRegistry store]      [LoRABenchmark.evaluate(test_images)]
   (persisted, promote())       composite ≥ 0.90 → eligible for promote()
                │                       │
                └───────────┬───────────┘
                            ▼
        [colab/AnimationStudio_Colab_Training.ipynb]  ← operator, T4/A100
         settings→GPU check→clone/install sd-scripts→download models(HF tok)
         →build dataset (repo code)→accelerate flux_train_network
         →generate samples→benchmark→register/promote→sync safetensors+report
```

Trace: curated assets → dataset dir → (local: dry-run artifacts + baseline benchmark) or (Colab: trained `.safetensors` + sample images) → benchmark verdict → persisted version record → promoted v1.0.

### Recommended Project Structure

```
src/training_engine/
├── base.py               # unchanged contracts (+ maybe dry_run flag on TrainingConfig)
├── dataset_builder.py    # FIX: .txt sidecars, valid TOML, min/max bounds, baselines copy
├── kohya_adapter.py      # FIX: Flux-complete command, strict dry_run mode
├── versioning.py         # ADD: promote(), persistence-backed registry (store seam)
├── benchmark.py          # FIX: aligned weights/threshold; keep ScorerProvider protocol
└── scorer_adapter.py     # NEW: IdentityScorerProvider (wraps identity_engine)
scripts/
└── train_lora.py         # NEW: argparse orchestrator (build-dataset/train/benchmark/versions, --dry-run)
colab/
└── AnimationStudio_Colab_Training.ipynb   # NEW: mirrors Phase 4 notebook pattern
tests/
├── test_lora_training.py     # extend existing suites
├── test_training_engine.py
└── test_train_lora_script.py # NEW: CLI-level tests (offline)
```

### Pattern 1: ScorerProvider adapter with dimension remapping

**What:** Thin class implementing `score_identity(image_path, reference_path, character_id) -> dict[str, float]` by opening the image(s) with PIL, delegating to `IdentityScorer.score_all(image, reference=ref)`, and renaming keys from plugin names to the benchmark's canonical dimension names (or vice versa — pick ONE direction; renaming benchmark keys onto plugin names is cleaner since weights then come straight from the plugins).

**When to use:** Every non-mock benchmark invocation.

**Example:**
```python
# Source: derived from src/training_engine/benchmark.py ScorerProvider protocol
#         and src/identity_engine/scorer.py score_all signature
class IdentityScorerProvider:
    """Adapts identity_engine.IdentityScorer to benchmark.ScorerProvider."""

    _DIM_MAP = {  # plugin name -> benchmark dimension
        "character_consistency": "dino_similarity",
        "prompt_accuracy": "clip_alignment",
        "color_harmony": "color_consistency",
        "facial_appeal": None,          # no benchmark equivalent — drop or extend weights
        "silhouette_recognizability": "pose_accuracy",
        "child_friendliness": "expression_match",
        "style_consistency": "style_consistency",
    }

    def __init__(self, light: bool = True):
        self._scorer = IdentityScorer(light=light)  # light=True skips torch plugins

    def score_identity(self, image_path, reference_path=None, character_id=None):
        img = Image.open(image_path)
        ref = Image.open(reference_path) if reference_path else None
        raw = self._scorer.score_all(img, reference=ref)
        return {mapped: s for name, s in raw.items()
                if (mapped := self._DIM_MAP.get(name))}
```
⚠️ Decide the weight-table question (G12/A2) BEFORE writing the map — if benchmark adopts D-06 plugin weights directly, skip renaming and align `_BENCHMARK_WEIGHTS` to plugin names instead (fewer moving parts; recommended). Note `light=True` drops DINOv2/CLIP (torch-heavy) — fine for offline tests, but the ≥90% gate on real data should run full plugins on Colab or a CPU-capable subset; document which.

### Pattern 2: Dry-run as a first-class mode (not a mock hack)

Locked decisions allow registry entries from "completed real or dry-run trainings". Implement dry-run inside the engine, not the test layer:

```python
# Source: derived from kohya_adapter.train() control flow + CONTEXT.md decision
@dataclass
class TrainingConfig:
    ...
    dry_run: bool = False   # True → never invoke subprocess; write config artifacts

def train(self, config: TrainingConfig) -> TrainingResult:
    if not self.validate_environment():
        return TrainingResult(..., success=False)
    cmd = self._build_command(config)
    if config.dry_run:
        (config.output_path).mkdir(parents=True, exist_ok=True)
        (config.output_path / f"{config.character_id}_{config.version}.train_cmd.json") \
            .write_text(json.dumps(cmd, indent=2))
        # proceed to registry registration exactly like the real path
    else:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    ...
```

### Pattern 3: Notebook mirrors Phase 4 skeleton (9-cell shape)

Existing Phase 4 notebook cells: 1 Settings (repo URL/branch/PAT `#@param`s) → 2 clone+`pip install -e . --no-deps`+light deps → 3 preview scope (no generation) → 4 regenerate report → 5 run test suites → 6 review → 7 sync via `colab/git_sync.py` → 8 next-steps markdown. `[VERIFIED: colab/AnimationStudio_Colab_Phase4.ipynb inspected]`

Training notebook deltas: add **Cell 0/GPU check** (`nvidia-smi`, `torch.cuda.is_available()`, fail-fast with clear message); install cell adds `git clone kohya_ss/sd-scripts` + requirements; insert **dataset build cell** (runs repo `scripts/train_lora.py --build-dataset` against cloned repo — Universe Library ships in git so no Drive upload needed if assets are committed); **model download cell** (4 HF files, gated → `HF_TOKEN` param); **training cell** (`accelerate launch flux_train_network.py …` with VRAM-profile flags); **sample+benchmark cell** (generate N samples with diffusers pipeline + LoRA, feed to `LoRABenchmark` with `IdentityScorerProvider(light=False)`, print `report()`); sync cell additionally commits `Universe/Characters/Lily Bunny/lora/*.safetensors` + benchmark report. Reuse `git_sync._basic_auth_header`.

**T4 vs A100 profile (cite in notebook comments):** 24 GB: batch 2 basic · 16 GB (T4): batch_size 1 + `--blocks_to_swap=8` (+ fp8_base) · 12 GB: swap 16 + AdamW8bit. **T4/Turing has no native bf16** — fp16 NaNs on Flux; use `mixed_precision bf16 + --fp8_base` (emulated, slow ≈5 s/it @512px) or prefer A100 (native bf16). Expect hours-scale runtime on free Colab; watch session limits. [CITED: mintlify.com/kohya-ss/sd-scripts/training/lora-flux; github.com/kohya-ss/sd-scripts/issues/1595; huggingface.co/blog/flux-qlora]

### Anti-Patterns to Avoid

- **Training on your validation set:** current TOML mounts `val/` as `num_repeats=1` subset (G3). Fix before any real run.
- **Filtering in the wrong layer:** don't re-implement state filtering inside DatasetBuilder; query the repository (SQL `IN` or caller-side predicate over `find_by_character`) and hand builder clean entries — matches existing `find_approved`/export_assets patterns.
- **Placeholder version rows:** never seed `v0.1` without a completed real/dry-run behind it (locked decision; also why `recommend_next` exists — compute, then register post-run).
- **Committing secrets:** notebook HF_TOKEN/GITHUB_TOKEN params stay empty in-repo; document where they live.
- **Heavy deps in unit path:** never import torch/sd-scripts in `src/training_engine` tests — keep the mock-provider/offline boundary that makes 51 tests run in 3.4 s.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Semver parse/compare/bump | Custom regex scattered in scripts | `LoRAVersion` (exists, tested) | Ordering, production/experimental semantics already correct |
| Weighted composite + baseline delta | New scoring math | `LoRABenchmark.evaluate/report` | Baseline/improvement/report formatting done; only weights/threshold need alignment |
| Kohya TOML schema knowledge | Guessing keys from blog posts | Keys cited from official config_README + config_util schemas | `extra keys not allowed` fails fast at runtime on Colab — expensive iteration loop |
| SQLite migrations plumbing | Ad-hoc ALTERs in scripts | `migrations.SchemaManager` pattern (if catalog.db route chosen) | Versioned `_schema_version` bookkeeping already written |
| Git artifact sync from Colab | Custom auth/push code | `colab/git_sync.py` helpers | Proven in Phase 4 notebook |

**Key insight:** This phase is 80% closing integration gaps in code that already exists and follows tested conventions — resist rewriting modules; extend them.

## Common Pitfalls

### Pitfall 1: Empty dataset from the locked approved/production filter
**What goes wrong:** Builder returns 0 images; criterion 1 silently "passes" its unit tests (fixtures fabricate approved rows) while the real run produces nothing.
**Why it happens:** Live DB has zero approved/production assets (all 1858 sit at scored/shortlisted).
**How to avoid:** Add an explicit curation/promotion step BEFORE dataset build (Review UI `/approve/{id}` + `/promote` routes already implement scored→shortlisted→approved→production advancement via `_advance_to`); make the builder raise a clear error listing counts per state when below `min_images`.
**Warning signs:** `BuildResult.num_images == 0`; "Image not found" warnings absent while num low.

### Pitfall 2: Corrupted catalog.db breaks scan queries at execution time
**What goes wrong:** `SELECT … GROUP BY/ORDER BY` over assets raises `sqlite3.DatabaseError: database disk image is malformed`; indexed point lookups still work (verified: `find_by_character` returned 164 rows cleanly).
**Why:** Main db file has out-of-order rowids and hundreds of orphaned pages; a 4.1 MB `-wal` from Aug 15 sits beside an Aug 21 main file (stale-WAL suspicion). Tests use `:memory:` so nothing catches this.
**How to avoid:** Prefer index-covered queries in new code; consider a recovery step (`sqlite3 .recover` equivalent via `conn.backup()` — verified working this session producing a readable 1858-row copy) or rebuilding from `scripts/export_assets.py` manifests. Do NOT let the phase depend on GROUP BY over assets.
**Warning signs:** queries that worked in dev failing on the shared db; integrity_check reporting rowid errors.

### Pitfall 3: Invalid Kohya TOML discovered only on Colab
**What goes wrong:** `caption_metadata_file` key → voluptuous `extra keys not allowed` crash 10 minutes into a precious GPU session.
**How to avoid:** Validate generated TOML against the documented schema offline (unit test asserting exact allowed keys per section); keep a tiny TOML-fixture test mirroring config_README examples.
**Warning signs:** any TOML key not present in the official option tables (general/dataset/subset scopes).

### Pitfall 4: Benchmark composite collapses with the real scorer
**What goes wrong:** Adapter plugged in → five of six dimensions read missing keys → composite ≈ 0.07 → everything fails threshold.
**How to avoid:** Land the name-alignment (G11) and weight-table decision (G12/A2) in the same task; unit-test the adapter against a frozen fixture dict of plugin outputs.
**Warning signs:** `dimensions` entries with score 0.0 despite plausible inputs.

### Pitfall 5: Registry entries lost between sessions / double-registration
**What goes wrong:** In-memory registry forgets v0.1 after process exit; next dry-run re-registers duplicate rows.
**How to avoid:** Persisted registry with uniqueness on (character_id, version); hydrate-on-construct; idempotent `register`.
**Warning signs:** repeated identical `recommend_next` results across runs.

### Pitfall 6: T4 bf16 trap in the notebook
**What goes wrong:** fp16 mixed precision NaNs loss immediately on Turing; naive bf16 setting crawls or OOMs differently than docs assume.
**How to avoid:** Ship explicit VRAM profiles (see Pattern 3) with `fp8_base` on ≤16 GB; default the notebook to detect `torch.cuda.get_device_capability()` (< 8 → fp8 path) and print expected step-time.
**Warning signs:** loss=NaN in first 20 steps; OOM at latent caching.

## Runtime State Inventory

Not a rename/refactor phase — formal inventory omitted. Environment-state findings that affect execution are captured under Common Pitfalls (Pitfall 2: corrupted catalog.db + stale WAL; G9: `lora_models` table absent from live DB) and Environment Availability below.

## Code Examples

### Valid minimal Kohya TOML (DreamBooth style, what the fixed builder must emit)
```toml
# Source: github.com/kohya-ss/sd-scripts docs/config_README-en.md (official example, adapted)
[general]
shuffle_caption = true
caption_extension = ".txt"
keep_tokens = 1
enable_bucket = true
min_bucket_reso = 256
max_bucket_reso = 2048

[[datasets]]
resolution = 1024
batch_size = 1            # 16GB profile; 2 on 24GB
validation_split = 0.1    # native hold-out — replaces manual val/ subset
validation_seed = 42

  [[datasets.subsets]]
  image_dir = "/content/AnimationStudio/training/lily-v1/train"
  num_repeats = 1
```

### Caption sidecar pair (what build() writes per image)
```text
training/lily-v1/train/0001_angry_s438116070.png
training/lily-v1/train/0001_angry_s438116070.txt
```
```
lily bunny, angry expression, portrait, Big bright green eyes, soft white fur with light pink inner ears, high quality, detailed, Pixar-style
```
(trigger word first — survives `shuffle_caption=true` via `keep_tokens=1`; descriptor sourced from record.prompt per locked trigger-word convention.)

### Flux-complete training command skeleton (notebook / `_build_command`)
```bash
# Source: mintlify.com/kohya-ss/sd-scripts/training/lora-flux (official guide, 16GB profile)
accelerate launch --num_cpu_threads_per_process 1 sd-scripts/flux_train_network.py \
  --pretrained_model_name_or_path models/flux1-dev.safetensors \
  --clip_l models/clip_l.safetensors --t5xxl models/t5xxl_fp16.safetensors \
  --ae models/ae.safetensors \
  --dataset_config training/lily-v1/dataset_config.toml \
  --output_dir training/lily-v1/output --output_name lily-bunny_v1.0 \
  --save_model_as safetensors --network_module networks.lora_flux \
  --network_dim 32 --network_alpha 32 --learning_rate 1e-4 \
  --optimizer_type AdamW8bit --lr_scheduler constant \
  --max_train_epochs 10 --mixed_precision bf16 --save_precision bf16 --seed 42 \
  --gradient_checkpointing --sdpa --fp8_base --blocks_to_swap 8 \
  --cache_latents --cache_latents_to_disk \
  --cache_text_encoder_outputs --cache_text_encoder_outputs_to_disk \
  --guidance_scale 1.0 --timestep_sampling flux_shift --model_prediction_type raw \
  --max_data_loader_n_workers 2
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| SDXL U-Net LoRA (`networks.lora`) | Flux DiT LoRA (`networks.lora_flux`, separate AE/CLIP-L/T5-XXL files, flow-matching flags) | sd-scripts FlUX support 2024 | TrainingConfig defaults and `_build_command` predate this; must target Flux path per base_model default |
| Full-precision training | fp8_base + block swapping + cached TE outputs | 2024–2025 | Makes 16 GB T4 feasible; notebook must encode profiles |
| Manual train/val folders | Native `validation_split` in dataset TOML | sd-scripts config schema | Removes val-trained-on bug class |

**Deprecated/outdated:**
- Diffusers-format subfolder weights for Flux training (single-file `flux1-dev.safetensors` required) [CITED: sd-scripts FLUX LoRA guide]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | "Existing DatasetConfig min/max bounds (20–40)" do not exist in code — phase must ADD them | Gap G6 / Constraints | Planner assumes fields exist, skips enforcement; dataset size drifts outside ROADMAP range |
| A2 | Canonical benchmark weights = D-06 identity-plugin weights (not `BrandScore.WEIGHTS`, not current `_BENCHMARK_WEIGHTS`) — needs explicit confirm at plan/discuss | Gap G12 | Composite measures something different from "identity-engine Brand Score"; ≥90% gate becomes ambiguous. Note BrandScore table's `technical_quality` (0.15) is unreachable by any plugin, capping totals at 0.85 |
| A3 | catalog.db recovery strategy: prefer isolated sidecar registry store + index-safe queries over repairing catalog.db in-phase | Pitfall 2, G9 | If planner instead migrates catalog.db, corruption may resurface as flaky failures |
| A4 | Shortlisted→approved promotion happens as operator Review UI action before dataset build (routes already exist) rather than bulk-script promotion | Pitfall 1 | If auto-promotion is chosen instead, human-review guarantee from Phase 1b is bypassed |
| A5 | Curation policy: one best image per variant (highest brand_score), asset types = reference/expressions/poses/outfits, capped to 40 | Gap G7 | Different mix (e.g. include duplicates, portraits-only) changes dataset character |
| A6 | Universe Library images are committed to git so the Colab clone gets the dataset without Drive upload | Notebook design | If PNGs are gitignored, notebook needs a Drive/gdown step — verify `git ls-files "Universe/**/*.png"` count at plan time |
| A7 | `IdentityScorer(light=True)` (numpy/PIL plugins only) suffices for offline dry-run benchmarks; full-weight gate runs on Colab | Pattern 1 | Light-mode scores omit DINOv2/CLIP dims → light composite isn't comparable to the ≥90% production gate unless weights renormalize |

## Open Questions

1. **Which weight table is the "identity-engine Brand Score default"?**
   - What we know: three coexisting tables (D-06 plugin weights; `BrandScore.WEIGHTS` incl. unscoreable `technical_quality`; benchmark's legacy six-dim table).
   - What's unclear: which one the ≥90% gate legally binds to.
   - Recommendation: adopt D-06 plugin weights (1:1 with scorer output); confirm in discuss-phase (A2).
2. **Persistence home for version records**
   - What we know: `lora_models` schema exists but is never applied; catalog.db is corrupt; constraint forbids silent schema drift.
   - What's unclear: migrate catalog.db explicitly vs sidecar store.
   - Recommendation: dedicated `lora_registry.sqlite` (or JSON) via a storage seam on `VersionRegistry`; revisit consolidation later.
3. **Promotion mechanics for the 164 Lily assets**
   - What we know: Review UI approve/promote routes advance states correctly.
   - What's unclear: whether operator promotes interactively (slow, ~40 clicks) or a reviewed bulk action is acceptable.
   - Recommendation: leave interactive as default; note bulk alternative in plan checkpoint.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | everything | ✓ | 3.13.5 | — |
| pytest stack | validation | ✓ | pytest 9.1.1 (asyncio auto, timeout 30) | — |
| PIL / numpy | builder/benchmark | ✓ (pyproject deps) | — | — |
| nvidia-smi / CUDA | real training | ✗ | — | Colab T4/A100 (locked decision) — success criterion 2 recorded `verification_deferred_human` |
| sqlite3 CLI | db recovery | ✗ | — | Python `sqlite3` module (`backup()` verified working on a copy) |
| kohya sd-scripts | training | ✗ locally (by design) | — | Notebook clones it in-cell |
| Healthy catalog.db | dataset query | ⚠️ CORRUPT (indexed reads OK, scans fail) | — | Recovered copy via `conn.backup()`; index-safe queries |

**Missing dependencies with no fallback:** none blocking — GPU absence is absorbed by the locked deferred-verification path.
**Missing dependencies with fallback:** sqlite3 CLI (Python module), GPU (Colab).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (+pytest-asyncio auto, pytest-timeout 30) |
| Config file | `pyproject.toml [tool.pytest.ini_options]` (testpaths=tests) |
| Quick run command | `python3 -m pytest tests/test_training_engine.py tests/test_lora_training.py -q` (~3.4 s, 51 passing today) |
| Full suite command | `python3 -m pytest -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CHAR-07-a | Sidecar `.txt` written per image; trigger word first | unit | `pytest tests/test_lora_training.py::TestDatasetBuilder -q` | ✅ (extend class) |
| CHAR-07-a | TOML passes schema: only documented keys; val not a training subset | unit (fixture-assert) | `pytest tests/test_lora_training.py -k toml -q` | ❌ Wave 0/new test |
| CHAR-07-a | min/max bounds enforce 20–40 (error under min, cap above max) | unit | `pytest tests/test_lora_training.py -k bounds -q` | ❌ new test |
| CHAR-07-a | Curated filter returns approved∪production only (in-memory repo seeded both states) | unit async | `pytest tests/test_lora_training.py -k curated -q` | ❌ new test |
| CHAR-07-b (deferred-human) | Dry-run train: no subprocess invoked; config artifact written; registry entry created | unit (monkeypatch subprocess.run sentinel) | `pytest tests/test_training_engine.py -k dry -q` | ❌ new test |
| CHAR-07-c | promote() flips record; persisted registry survives round-trip; unique (char,ver) | unit | `pytest tests/test_lora_training.py::TestVersionRegistry -q` | ✅ (extend class) |
| CHAR-07-d | Adapter maps plugin dims→benchmark dims; zero unmapped-drop surprises | unit (frozen plugin-output fixture) | `pytest tests/test_lora_training.py -k adapter -q` | ❌ new test |
| CHAR-07-d | Weights aligned + threshold 0.90; composite math sanity vs known fixture | unit | `pytest tests/test_lora_training.py::TestLoRABenchmark -q` | ✅ (update expectations) |
| CHAR-07 | CLI `scripts/train_lora.py --dry-run` end-to-end offline (tmp db + tmp images) | integration | `pytest tests/test_train_lora_script.py -q` | ❌ Wave 0/new file |
| CHAR-07 | Notebook structural validity (valid ipynb JSON, GPU cell present, no tokens committed) | smoke | `pytest tests/test_colab_notebooks.py -q` (pattern: parse json, assert cell titles) | ❌ new test (mirror any existing notebook test if present) |

### Sampling Rate
- **Per task commit:** quick command above (engine suites)
- **Per wave merge:** full suite `python3 -m pytest -q`
- **Phase gate:** full suite green + dry-run artifact inspection before `/gsd-verify-work`; criterion 2 marked `verification_deferred_human` pending operator Colab run

### Wave 0 Gaps
- [ ] `tests/test_lora_training.py` additions: toml-schema, bounds, curated-filter, adapter, updated-threshold cases
- [ ] `tests/test_train_lora_script.py` — CLI integration (offline, tmp dirs)
- [ ] Fixture: frozen plugin-output dict + tiny valid/invalid TOML fixtures
- [ ] No framework install needed (stack present)

### Recommended Plan Structure (waves / dependency chain)

**Wave 1** (parallel — independent modules):
- Plan 01c-1: DatasetBuilder completion — `.txt` sidecars (trigger-word convention), schema-valid TOML (drop `caption_metadata_file`; native `validation_split` or val-exclusion), `min_images=20/max_images=40` enforcement, baselines copy, curated-state query surface (repo method or wrapper honoring `approved|production`), empty-dataset error. Tests: sidecar/toml/bounds/curated.
- Plan 01c-2: Benchmark ↔ identity engine integration — `IdentityScorerProvider` adapter, weight-table alignment (resolve A2), `similarity_threshold=0.90`, update MockScorerProvider dims to match canonical names (keeps determinism tests meaningful). Tests: adapter fixture, threshold/composite updates.

**Wave 2** (depends on Wave 1):
- Plan 01c-3: VersionRegistry persistence + `promote()` + `scripts/train_lora.py` orchestrator (subcommands build-dataset/train/benchmark/versions; `--dry-run` default-off but mandatory for local train; KohyaAdapter `dry_run` mode + Flux-complete `_build_command` fix lands here or in 01c-1's sibling task). Tests: registry round-trip, dry-run sentinel, CLI integration.

**Wave 3** (depends on Wave 2):
- Plan 01c-4: `colab/AnimationStudio_Colab_Training.ipynb` (GPU-check, sd-scripts setup, HF model downloads, VRAM profiles T4/A100, dataset build from repo, accelerate train, sample-gen + benchmark, register/promote, git_sync of safetensors+report) + docs/status update (PHASE1C_STATUS.md or equivalent, README pointers).

### Constraint Reminders (for planner)
- Offline-first tests: no GPU/network in pytest; subprocess only behind mocked/dry-run seams
- catalog.db schema untouched unless a migration is an explicit planned task (G9 forces an explicit choice; corruption argues for isolation)
- Stdlib-only for new imports; Pillow/numpy/pytest allowed (existing deps)
- No placeholder registry versions — only post-real/post-dry-run registration
- ≥ 0.90 threshold; 20–40 image bounds; approved/production filter — all locked
- Success criterion 2 verification: notebook + local dry-run evidence → `verification_deferred_human`

## Security Domain

> security_enforcement not disabled in config — included.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V5 Input Validation | yes | Path resolution before fs ops (already in kohya_adapter); sanitize character_id before filename interpolation; validate TOML values are schema-typed |
| V3 Session Management | no (no sessions) | — |
| V2 Authentication | no (offline engine) | Notebook tokens (HF/GitHub PAT) are operator-supplied params — never committed |
| V4 Access Control | no | Single-operator tooling |
| V6 Cryptography | no | No crypto introduced; safetensors integrity via checksum note in registry (optional) |
| V14 Config | yes | Command construction stays arg-list (never shell=True) — preserve existing invariant |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Shell injection via crafted character_id/version into subprocess args | Tampering/Elevation | Arg-list exec (already); reject ids matching `[^a-z0-9-]` at config layer |
| Path traversal via repo-supplied file_path | Tampering | `Path.resolve()` + ensure result under expected roots before copy |
| Secret leakage through notebook cells | Information Disclosure | Empty-token params in committed ipynb; runtime-only entry; .gitignore artifacts dir |
| Corrupt DB silent partial reads | Tampering/DoS | Integrity-check or backup() recovery before batch curation; fail loudly on DatabaseError |

## Sources

### Primary (HIGH confidence)
- Codebase inspection (this session): all 5 training_engine modules, sqlite_repo.py, migrations.py, identity_engine (scorer/brand_score/plugins), review_ui/app.py approval routes, tests (51 passing run executed), live catalog.db probes, Phase 4 notebook cells, export_assets.py argparse conventions
- Official sd-scripts docs: config_README-en.md + library/config_util.py schemas (TOML keys, validation_split, extra-keys rejection); FLUX LoRA training guide (flags, model files, VRAM table)

### Secondary (MEDIUM confidence)
- WebSearch results citing the above official sources (brave provider; classify-confidence LOW→overridden by direct citation of official pages)
- sd-scripts issue #1595 (Turing bf16/fp8 behavior); huggingface.co/blog/flux-qlora (T4 feasibility, ~hours runtime)

### Tertiary (LOW confidence)
- None material; Colab session-limit specifics left as operator-facing documentation notes [ASSUMED]

## Metadata

**Confidence breakdown:**
- Gap analysis: HIGH — every claim verified by reading code and querying live DB this session
- Kohya contract: HIGH for cited keys/flags (official repo docs); MEDIUM for exact VRAM numbers (community-reported)
- Notebook design: MEDIUM — mirrors proven Phase 4 pattern; GPU-cell details validated against docs but not executed (no GPU)
- Environment risks (DB corruption): HIGH confidence in diagnosis; recovery approach ASSUMED (A3)

**Research date:** 2026-08-23
**Valid until:** 2026-09-22 (stable domain; sd-scripts flags re-check if notebook slips >30 days)

## RESEARCH COMPLETE

**Key findings for orchestrator:**
1. **51 tests green baseline confirmed** (3.4 s) — this phase closes gaps, doesn't scaffold: 17 numbered gaps identified across the four success criteria, each mapped to owner module.
2. **Three hard blockers found:** (a) generated Kohya TOML uses invalid key `caption_metadata_file` → schema rejection on Colab; (b) benchmark weight-table keys don't match identity-engine plugin names → real scorer yields ~0 composite; (c) zero `approved`/`production` assets exist (all 1858 at scored/shortlisted) → locked filter yields empty dataset until promotion.
3. **Environment hazard:** live `catalog.db` is corrupt (scans fail, indexed reads fine); `lora_models` table defined in migrations.py but never applied — persistence needs an explicit, corruption-aware decision (sidecar store recommended, logged as A3).
4. **CONTEXT discrepancy:** "existing DatasetConfig min/max bounds (20–40)" don't exist in code — must be added (A1); weight-table ambiguity logged as A2 for discuss-phase confirmation.
5. **Deferred-human path is viable:** no GPU locally (confirmed), but KohyaAdapter command is not Flux-complete (missing `accelerate launch`, `networks.lora_flux`, ae/clip_l/t5xxl files, fp8/blocks_to_swap profiles) — Wave 2/3 tasks cover the fix plus the mirrored 9-cell training notebook with T4-vs-A100 VRAM profiles.
