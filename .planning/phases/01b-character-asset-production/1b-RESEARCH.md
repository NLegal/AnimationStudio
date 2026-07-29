# Phase 1b: Character Asset Production — Research

**Researched:** 2026-07-29
**Domain:** Character asset image generation pipeline — ComfyUI + Flux production, identity scoring, batch review
**Confidence:** HIGH

## Summary

Phase 1b activates the character factory built in Phase 1 to produce Lily Bunny's complete visual asset library. The existing infrastructure (Generation Engine, Identity Scorer, Prompt Builder, Asset Repository, Job Queue, Review UI) is fully implemented and ready for production use. The key shift from Phase 1 is that **ComfyUI + Flux becomes the primary production path** (not Python/diffusers as originally designed in D-08/D-19) — the `ComfyUIBackend` already exists but needs Flux-specific workflow JSON templates for multi-angle reference sheets, expression portraits, pose full-bodies, and outfit variants.

The pipeline is: **JobQueue → PromptBuilder → ComfyUIBackend(Flux) → IdentityScorer(7 plugins) → DiversityFilter → SQLiteAssetRepository → ReviewUI(enhanced batch grids) → Human approval → Universe Library**. Phase 1b is a **production run**, not infrastructure building — the factory exists, now we run it.

**Primary recommendation:** Use the existing `GenerationJob` orchestrator with `ComfyUIBackend` pointed at local ComfyUI + Flux. Create Flux-optimized API-format workflow JSON files for each asset type (reference, expression, pose, outfit). Run iterative batch generation with the D-12 multi-stage review pipeline (50-100 candidates → auto-score → diversity filter → human review top 10-20 → winner lock).

## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Execution Environment & Backend Selection
- **D-01:** Hybrid architecture: research on free/cloud tools → lock prompts → local production. Phase 1b goes straight to local ComfyUI + Flux as the primary production path. SDXL as secondary. — **Reversibility:** reversible
- **D-02:** ComfyUI is the heart of the studio. All production generation runs through ComfyUI workflows. Python/diffusers adapters from Phase 1 remain supported but ComfyUI is primary for Phase 1b. — **Reversibility:** costly
- **D-03:** Cloud APIs (fal.ai, Replicate, Black Forest Labs API) are optional adapters only — never mandatory dependencies. — **Reversibility:** reversible
- **D-04:** Research tools (Tensor.Art, Playground AI, Civitai, Hugging Face Spaces) are for prompt discovery, style exploration, and concept experimentation only. No production assets come from these tools. — **Reversibility:** reversible

#### Asset Production Sequencing (Progressive Locking Pipeline)
- **D-05:** Progressive Locking Pipeline — not sequential per-type. Each stage locks a deeper layer of character identity before the next begins. — **Reversibility:** one-way
- **D-06:** Pipeline stages: Concept Exploration → Identity Lock (multi-angle reference sheets, ComfyUI+Flux) → Face Lock (expressions) → Body Lock (poses) → Default Outfit Lock → Accessory Library → Wardrobe Expansion → LoRA Dataset → LoRA Training (Phase 1c). — **Reversibility:** reversible
- **D-07:** Concept exploration phase uses research tools not local ComfyUI. — **Reversibility:** reversible
- **D-08:** Animation Validation deferred to Phase 4. Phase 1b does not include video testing. — **Reversibility:** costly

#### Expression & Pose Spec Alignment
- **D-09:** Source of truth is merged superset: PHASE1.md base list + code additions. — **Reversibility:** reversible
- **D-10:** Phase 1b generates ALL expressions and poses from the merged superset. — **Reversibility:** reversible
- **D-11:** Code's `_known_expressions()` and `_known_poses()` will be updated to include PHASE1.md expressions plus retain code extras. — **Reversibility:** reversible

#### Review Cadence & Approval Workflow
- **D-12:** Multi-stage batch review pipeline: Batch Generation (50-100) → Hard-rule elimination → Auto multi-metric quality scoring → Duplicate removal → Diversity filtering → Human review batch (top ~10-20) → Side-by-side comparison (top 3-5) → Winner lock. — **Reversibility:** reversible
- **D-13:** DINOv2 is one component of scoring, not the sole decision-maker. Multi-metric scoring: Identity Consistency 35% (DINOv2), Style Consistency 20%, Prompt Adherence 15%, Technical Quality 15%, Composition 10%, Diversity 5%. — **Reversibility:** costly
- **D-14:** Adaptive per-asset-type thresholds: Reference sheets 97-99%, Expressions 92-97%, Dynamic poses 88-95%, Outfits 80-92%. — **Reversibility:** reversible
- **D-15:** Approval zones: ≥95% auto-pass, 90-95% normal review, 80-90% diversity-only, <80% reject, <70% auto-reject. — **Reversibility:** reversible
- **D-16:** Review UI enhanced with larger configurable batch grids (3x3, 4x4). — **Reversibility:** reversible
- **D-17:** Asset approval state machine: Generated → Filtered → Candidate → Reviewed → Approved → Production → Archived. — **Reversibility:** reversible
- **D-18:** Each approved asset retains lineage metadata (generation batch, candidate pool, version history, episodes using this asset). — **Reversibility:** one-way

### The agent's Discretion
(From CONTEXT.md — no explicit discretion items listed beyond what decisions delegate)

### Deferred Ideas (OUT OF SCOPE)
- Animation Validation (image-to-video clips) — deferred to Phase 4
- Inspiration Library — potential pre-work for future characters

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CHAR-02 | Character reference sheet generation (front, 3/4, profile, back angles) | ComfyUI + Flux identity-lock workflow via rotated multi-angle generation. Existing PromptBuilder has `reference_sheet()` template with angle parameter. Use **Flux Klein multi-angle workflow** pattern for backward-view inference. D-14 threshold: 97-99% identity similarity. |
| CHAR-03 | Expression library (happy, sad, surprised, singing, sleepy, etc.) | 23 expressions from merged PHASE1.md + code superset. `PromptBuilder.expression()` template supports all. Generate 50-100 candidates per expression, score via IdentityScorer, diversity-filter, top 10-20 for human review. D-14 threshold: 92-97%. |
| CHAR-04 | Pose library (standing, running, jumping, sitting, dancing, etc.) | 20 poses from merged PHASE1.md + code superset. `PromptBuilder.pose()` template supports all. Use full-body generation in ComfyUI workflow. D-14 threshold: 88-95%. |
| CHAR-05 | Outfit/wardrobe variants (default, winter, rain, pajamas, holiday, etc.) | 12+ outfits from Lily Bunny bio. `PromptBuilder.outfit()` template supports outfit_variant param. Outfits are more lenient — D-14 threshold: 80-92%. |

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Reference sheet generation | Generation Engine (ComfyUIBackend) | PromptBuilder | ComfyUI generates images from prompt templates; PromptBuilder constructs the Flux-optimized prompts |
| Expression generation | Generation Engine (ComfyUIBackend) | PromptBuilder | Same pattern — prompts built from templates, sent to ComfyUI Flux |
| Pose generation | Generation Engine (ComfyUIBackend) | PromptBuilder | Full-body prompts via pose template, ComfyUI produces candidates |
| Outfit generation | Generation Engine (ComfyUIBackend) | PromptBuilder | Outfit variant prompts via outfit template |
| Quality scoring | IdentityScorer (7 plugins) | BrandScore compositor | Auto-scores every candidate: DINOv2, CLIP, Color, Part, Pose, Expression, Style |
| Diversity filtering | DiversityFilter (pipeline module) | IdentityScorer | K-Means clustering on pixel features, picks best-scored from each cluster |
| Asset storage | SQLiteAssetRepository | Filesystem | Metadata in SQLite, binary images in Universe directory |
| Human review | ReviewUI (FastAPI + Jinja2) | AssetRepository | Web UI shows scored candidates in configurable grid layouts |
| Approve/promote/reject actions | ReviewUI action handlers | AssetRepository | POST handlers call repo.update_state() for lifecycle transitions |
| Concept exploration (pre-production) | Research tools (Civitai, etc.) | ComfyUI (for final reproduction) | D-07: Research tools for prompt discovery only; final production in local ComfyUI |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| ComfyUI | latest (v0.23+) | Production image generation engine | D-02: "ComfyUI is the heart of the studio" — Flux model execution via REST API |
| Flux (FLUX.1-dev / FLUX.2 Klein) | latest | Primary image generation model | Best-in-class prompt following, character consistency, multi-angle support |
| Python 3.11+ | 3.13.5 | Pipeline orchestration runtime | All studio infrastructure (GenerationJob, IdentityScorer, etc.) is Python |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| FastAPI | >=0.115 | Review UI backend (already installed) | Phase 1 Review UI — no changes needed |
| Jinja2 | >=3.1 | HTML template rendering (already installed) | Review UI templates — needs grid enhancement |
| SQLite (aiosqlite) | >=0.20 | Metadata repository (already installed) | Asset + character storage |
| scikit-learn | >=1.6 | Diversity filter clustering (already installed) | K-Means clustering for candidate deduplication |
| Pillow | >=11.0 | Image handling (already installed) | Image loading, resizing, saving |
| numpy | >=2.0 | Array operations (already installed) | Embedding computations, feature vectors |
| pydantic | >=2.0 | Schema validation (already installed) | Data contracts |
| websocket-client | latest | ComfyUI WebSocket tracking [ASSUMED] | Real-time job progress instead of HTTP polling |
| requests | latest | ComfyUI REST API calls (built-in Python) | HTTP communication with ComfyUI |
| pycomfyapi | >=0.1 | Optional ComfyUI Python API [ASSUMED] | Alternative to raw REST — provides full graph API |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| ComfyUI + Flux | Python/diffusers FluxBackend | D-08/D-19 originally set diffusers for production, but D-02 flipped to ComfyUI as primary. ComfyUI workflows are files (portable, shareable) vs. code (requires re-deploy). Diffusers remains as secondary fallback. |
| Flux | SDXL | SDXL ecosystem has larger LoRA community but less prompt adherence. SDXL is secondary backup per D-01. |
| HTTP polling | WebSocket | WebSocket gives near-real-time progress; HTTP polling simpler but adds ~1s latency per batch. Use WebSocket for production, polling for scripts. |

### Key Gaps in Existing Code
| Gap | File | Fix Required |
|-----|------|-------------|
| `_known_expressions()` outdated | `src/prompt_builder/builder.py` line 116 | Add PHASE1.md expressions (blowing_kiss, winking, very_happy, giggling, whistling, etc.) + retain code extras (angry, shy, silly, sneezing, coughing, sighing, etc.) |
| `_known_poses()` mismatched | `src/prompt_builder/builder.py` line 127 | Update to match character-design-rules.md pose list (20 poses including hugging, holding_hands, pointing, clapping, etc.) |
| `ColorVerificationPlugin.DEFAULT_BRAND_PALETTE` hardcoded | `src/identity_engine/plugins/color_verification.py` | Load from `Universe/ColorPalette/brand-palette.json` |
| Review UI action handlers are stubs | `src/review_ui/app.py` lines 197-222 | Wire /approve, /reject, /regenerate, /promote to SQLiteAssetRepository.update_state() |
| Batch grid size fixed at 2x2 | `src/review_ui/templates/review.html` line 130 | Parameterize to support 3x3 and 4x4 grid layouts per D-16 |
| No ComfyUI workflow files | `src/generation_engine/comfy_workflow.json` | Create Flux-specific API-format workflow JSON for each asset type |
| AssetModel missing "lineage" field | `src/models/schemas.py` | Add lineage metadata (generation_batch, candidate_pool, version_history) per D-18 |

## Package Legitimacy Audit

> **Note:** This phase primarily uses existing installed packages. ComfyUI runs as an external process (not a Python package). Flux model weights are downloaded by ComfyUI. No new Python packages need to be installed from pip for this phase — the existing `pyproject.toml` dependencies cover all needs.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| websocket-client | PyPI | 12+ yrs | 100M+/wk | github.com/websocket-client/websocket-client | OK | Approved (add to dev deps if needed) |
| requests | PyPI | 12+ yrs | 1B+/wk | github.com/psf/requests | OK | Already stdlib-compatible |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
User/Operator
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│                    Production Pipeline                        │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐  │
│  │ JobQueue │──▶│Generation│──▶│Identity  │──▶│Diversity │  │
│  │          │   │   Job    │   │  Scorer  │   │  Filter  │  │
│  └──────────┘   └────┬─────┘   └──────────┘   └────┬─────┘  │
│                      │                              │        │
│                      ▼                              ▼        │
│              ┌──────────────┐              ┌──────────────┐  │
│              │PromptBuilder │              │ BrandScore   │  │
│              │  (templates) │              │ (composite)  │  │
│              └──────┬───────┘              └──────────────┘  │
│                     │                                        │
│                     ▼                                        │
│              ┌──────────────┐                                │
│              │ ComfyUI +    │                                │
│              │   Flux       │                                │
│              │ REST API :8188│                                │
│              └──────┬───────┘                                │
│                     │                                        │
│                     ▼                                        │
│              ┌──────────────┐                                │
│              │  ComfyUI     │  ▼                             │
│              │  Workflow    │──▶ AI model (Flux/FLUX.2)      │
│              │  JSON file    │  generates images              │
│              └──────────────┘                                │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                   Storage Layer                               │
│  ┌────────────────────┐    ┌──────────────────────────────┐  │
│  │ SQLiteAssetRepo    │    │  Universe/Characters/Lily/   │  │
│  │ (metadata: IDs,    │◀──▶│  references/expressions/     │  │
│  │  scores, states)   │    │  poses/outfits/accessories/  │  │
│  └────────────────────┘    └──────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                   Human Review Layer                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Review UI (FastAPI + Jinja2 templates)               │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────┐ │  │
│  │  │Dashboard │  │Character │  │  Batch   │  │Winner │ │  │
│  │  │          │  │  Detail  │  │ Compare  │  │ Lock  │ │  │
│  │  │          │  │          │  │ 3x3/4x4  │  │       │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └───────┘ │  │
│  │  Actions: /approve | /reject | /regenerate | /promote │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  Universe Library      │
              │  (approved assets)     │
              └────────────────────────┘
```

### Recommended Project Structure
```
src/
├── generation_engine/     # 5 backends (Flux, SDXL, Pony, CloudAPI, ComfyUI)
│   ├── base.py           # ABC + GenerationInput/Output
│   ├── comfy_backend.py  # ComfyUI REST API client (primary for Phase 1b)
│   ├── comfy_workflow.json  # <-- NEEDS CREATION: Flux API-format workflow
│   └── ...
├── identity_engine/       # 7 scoring plugins + BrandScore
├── pipeline/              # JobQueue, GenerationJob, DiversityFilter
├── prompt_builder/        # PromptBuilder, PromptTemplates, negative
├── asset_repository/      # SQLiteAssetRepository + ABCs
├── models/schemas.py      # Pydantic data contracts
└── review_ui/             # FastAPI + Jinja2
    ├── app.py             # Routes + action handlers (stubs → wire)
    └── templates/
        └── review.html    # <-- NEEDS ENHANCEMENT: configurable grid sizes

Universe/
└── Characters/
    └── Lily Bunny/
        ├── references/    # <-- target for approved reference sheets
        ├── expressions/   # <-- target for approved expressions
        ├── poses/         # <-- target for approved poses
        ├── outfits/       # <-- target for approved outfits
        ├── prompts/       # templates.json (already exists)
        └── turnarounds/   # rotation sheets
```

### Pattern 1: Progressive Locking Pipeline
**What:** Assets are generated in a specific order (D-06) where each stage locks a layer of character identity before the next begins. Reference sheets first (identity lock), then expressions (face lock), then poses (body lock), then outfit + accessories. Each stage uses the previous stage's approved assets as reference for identity scoring.
**When to use:** Every character production run. Start at Concept Exploration, work through Identity Lock → Face Lock → Body Lock → Default Outfit → Accessories → Wardrobe Expansion.
**Example:**
```python
# Phase 1b ordering:
stages = [
    "concept_exploration",  # D-07: research tools only
    "identity_lock",        # Multi-angle reference sheets (ComfyUI+Flux)
    "face_lock",            # 23 expressions
    "body_lock",            # 20 poses
    "default_outfit_lock",  # Lily's signature pink dress
    "accessory_library",    # Props like backpack, book, balloon
    "wardrobe_expansion",   # 12+ outfit variants
]
```

### Pattern 2: ComfyUI Workflow-as-Template
**What:** Each asset type gets a dedicated API-format workflow JSON file. These are loaded by `ComfyUIBackend._build_workflow()`, parameterized (prompt, seed, dimensions injected), then submitted to ComfyUI REST API. Workflow files are version-controlled alongside code.
**When to use:** Always for production generation. Never hand-code workflow JSON.
**Example:**
```python
# ComfyUI workflow template for expression generation
workflow = {
    "3": {"class_type": "KSampler", "inputs": {
        "seed": 42, "steps": 25, "cfg": 3.5,
        "sampler_name": "euler", "scheduler": "normal",
        "denoise": 1.0, "model": ["4", 0],
        "positive": ["6", 0], "negative": ["7", 0],
        "latent_image": ["5", 0]}},
    "4": {"class_type": "CheckpointLoaderSimple",
          "inputs": {"ckpt_name": "flux1-dev.safetensors"}},
    "5": {"class_type": "EmptyLatentImage",
          "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
    "6": {"class_type": "CLIPTextEncode",
          "inputs": {"text": "", "clip": ["4", 1]}},
    "7": {"class_type": "CLIPTextEncode",
          "inputs": {"text": "", "clip": ["4", 1]}},
    "8": {"class_type": "VAEDecode",
          "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
    "9": {"class_type": "SaveImage",
          "inputs": {"filename_prefix": "comfy", "images": ["8", 0]}},
}
```
**Note for Flux:** Flux uses `cfg: 1.0` (not 7.0), negative prompt typically empty, and for Flux.1 Schnell only 1-4 steps. For Flux.1 Dev use 20-28 steps. Flux.2 Klein supports multi-angle from single reference. Workflow must be exported as **API format** (not GUI format) from ComfyUI.

### Anti-Patterns to Avoid
- **Submitting GUI-format workflow JSON to /prompt:** GUI format includes node positions/colors and will fail with `node_errors`. Always use "Save (API Format)" export from ComfyUI.
- **Polling /history without timeout:** A failed prompt will never appear in history. Always wrap polling with a timeout (e.g., 300s) and call `/interrupt` on timeout.
- **Running concurrent workflows on one ComfyUI instance:** ComfyUI is single-threaded. Use sequential submission with WebSocket tracking.
- **Generating all asset types before human review:** Batch generate 50-100, auto-score, diversity-filter, THEN human review. Don't generate all candidates before the first review pass.
- **Hardcoding checkpoint filenames in workflow JSON:** Parameterize model names or validate they match the target ComfyUI environment.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Identity consistency scoring | Custom feature extractor | DINOv2 (existing plugin, 40% weight) | DINOv2 captures fine-grained structural correspondences better than CLIP [CITED: arxiv.org paper 2311.10093]. Already implemented as DINOv2ScoringPlugin. |
| Image similarity clustering | Custom clustering algorithm | scikit-learn MiniBatchKMeans (existing) | Already implemented in DiversityFilter. Handles 50-100 images efficiently. |
| Multi-view character turnaround | Single-view generation | Flux-klein multi-angle workflow (ComfyUI) | Dedicated community workflows generate front/3/4/profile/back from one reference [CITED: civitai.com/models/2642426]. |
| Batch generation management | Custom queue system | Existing JobQueue + GenerationJob | Already built in Phase 1. GenerationJob orchestrates prompt→generate→score→filter→save pipeline. |
| Negative prompt composition | Manual strings | build_negative_prompt() | Already in src/prompt_builder/negative.py. Composes COMMON_NEGATIVE + STYLE_NEGATIVE + custom. |
| Asset lifecycle state enforcement | Custom state machine | SQLiteAssetRepository.update_state() | _VALID_TRANSITIONS dict enforces D-15 lifecycle. Already implemented. |

**Key insight:** The factory was built in Phase 1. Almost everything needed to orchestrate Phase 1b already exists. The work is: (1) create Flux workflow JSON templates, (2) update expression/pose lists, (3) fix code-spec gaps (ColorVerificationPlugin hardcoded palette, Review UI stub handlers), (4) enhance batch grids, (5) run the pipeline.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Pipeline runtime | ✓ | 3.13.5 | — |
| pip | Package mgmt | ✓ | 25.1.1 | — |
| fastapi | Review UI | ✓ | 0.140.13 | — |
| uvicorn | Review UI server | ✓ | 0.51.0 | — |
| jinja2 | Review UI templates | ✓ | 3.1.6 | — |
| pydantic | Data contracts | ✓ | 2.13.4 | — |
| Pillow | Image handling | ✓ | 12.3.0 | — |
| numpy | Array operations | ✓ | 2.5.1 | — |
| scikit-learn | Diversity filter | ✓ | 1.9.0 | — |
| aiosqlite | Asset repository | ✓ | 0.22.1 | — |
| pytest | Testing | ✓ | 9.1.1 | — |
| torch | DINOv2/CLIP plugins | ✗ | — | MockScorerPlugin for testing; real plugins need GPU/torch install |
| diffusers | Flux backend (Python) | ✗ | — | ComfyUIBackend (primary) doesn't need diffusers |
| transformers | CLIP plugin | ✗ | — | DINOv2ScoringPlugin falls back to 0.0 gracefully |
| websocket-client | ComfyUI WebSocket | ✗ | — | Can use HTTP polling fallback |
| pycomfyapi | ComfyUI SDK | ✗ | — | Raw REST API fallback (already implemented) |
| ComfyUI server | Production generation | ✗ | — | Must be installed separately (git clone + models) |
| Flux model weights | Production generation | ✗ | — | Must be downloaded via ComfyUI Manager |

**Missing dependencies with no fallback:**
- ComfyUI server (must be installed and running on localhost:8188)
- Flux model weights (flux1-dev.safetensors or Flux.2 Klein — must be placed in ComfyUI models directory)

**Missing dependencies with fallback:**
- torch, diffusers, transformers — only needed for real ML scoring plugins. MockScorerPlugin works for pipeline testing. Production scoring requires GPU + torch install.
- websocket-client — HTTP polling fallback (less efficient but works)
- pycomfyapi — raw REST API fallback (already implemented in ComfyUIBackend)

## Common Pitfalls

### Pitfall 1: ComfyUI API Workflow JSON Format Mismatch
**What goes wrong:** Posting a GUI-format workflow JSON to `/prompt` returns `node_errors` because GUI format includes node positions/colors that the API endpoint doesn't understand.
**Why it happens:** ComfyUI has two JSON formats: GUI (with positions, colors, collapsed states) and API (stripped to `class_type` + `inputs` + connections). Users export the wrong format.
**How to avoid:** Always use **File → Export Workflow (API Format)** from ComfyUI settings (enable Dev Mode first). Verify the JSON uses numeric string keys ("3", "4") with only `class_type` and `inputs` fields.
**Warning signs:** `400 Bad Request` with `node_errors` key in response.

### Pitfall 2: Flux-Specific Sampling Parameters
**What goes wrong:** Flux models fail silently or produce garbage when using SDXL sampling parameters.
**Why it happens:** Flux.1 Dev requires `cfg: 3.5` (not 7.0), Flux.1 Schnell uses 1-4 steps, and Flux ignores negative prompts (leave CLIPTextEncode empty). Flux.2 Klein requires `cfg: 1.0` exactly.
**How to avoid:** Create separate workflow JSON files per model with correct defaults. The `ComfyUIBackend._build_workflow()` injects prompt/seed/dimensions but the workflow template must have correct model-specific params.
**Warning signs:** Output images are garbled, over-saturated, or don't follow the prompt.

### Pitfall 3: DINOv2 Similarity Threshold Misinterpretation
**What goes wrong:** DINOv2 cosine similarity scores below 0.5 for same-character images leads to "failed identity" false negatives.
**Why it happens:** DINOv2 is sensitive to lighting, shadows, and pose changes [CITED: github.com/facebookresearch/dinov2/issues/147]. Same character in different lighting can score 0.4-0.6. The D-14 thresholds (97-99% for references) may be too aggressive for DINOv2.
**How to avoid:** Validate D-14 thresholds with real ComfyUI+Flux outputs. Tune based on empirical distribution. Consider DINOv2 scores > 0.5 as "same identity" for research purposes [VERIFIED: arxiv.org paper 2311.10093, DINOv2 GitHub issue 147]. The D-14 thresholds should be treated as initial configuration values (reversible per D-14).
**Warning signs:** High rejection rate of visually consistent characters in scoring pipeline.

### Pitfall 4: One ComfyUI Instance Can't Parallelize
**What goes wrong:** Multiple concurrent generation requests to the same ComfyUI instance get serialized, but WebSocket events from different prompt_ids get mixed up.
**Why it happens:** ComfyUI is single-process, single-GPU, single-threaded execution. Two simultaneous `/prompt` calls are serialized server-side, but without distinct `client_id`, WebSocket events become untraceable.
**How to avoid:** Submit jobs sequentially. Always use a unique `client_id` per session. Use the `JobQueue` to manage submission order. Wait for one batch to complete before submitting the next.
**Warning signs:** Increasing queue depth at `/queue`, mismatched results.

### Pitfall 5: Asset State Transition Errors
**What goes wrong:** Calling `update_state(asset_id, "approved")` on an asset in "scored" state raises `ValueError` because the transition `scored → approved` skips "shortlisted".
**Why it happens:** D-15 lifecycle is: `draft → generated → scored → shortlisted → approved → production → archived`. The `_VALID_TRANSITIONS` dict enforces this strictly.
**How to avoid:** Follow the complete lifecycle. The review UI approve button should transition `shortlisted → approved`, not `scored → approved`. The /promote endpoint does two-step: `shortlisted → approved → production`.
**Warning signs:** `ValueError: Invalid state transition` in repo layer.

## Code Examples

### Example 1: Running a Generation Job with ComfyUIBackend
```python
# Source: Existing GenerationJob orchestrator + ComfyUIBackend
from src.generation_engine import ComfyUIBackend
from src.prompt_builder import PromptBuilder, CharacterPrompt
from src.identity_engine import IdentityScorer
from src.pipeline import JobQueue, GenerationJob, DiversityFilter
from src.asset_repository.sqlite_repo import SQLiteAssetRepository

# Setup
backend = ComfyUIBackend(server_url="http://localhost:8188")
backend.load_model()  # Validates connectivity (non-fatal if unreachable)

prompt_builder = PromptBuilder()
scorer = IdentityScorer()  # Will use MockScorerPlugin if torch unavailable
repo = SQLiteAssetRepository(db_path="catalog.db")
diversity = DiversityFilter(n_clusters=5)
job_runner = GenerationJob(backend, prompt_builder, scorer, repo, diversity)

# Create job for Lily Bunny expressions
jq = JobQueue()
job = jq.create_job(
    character_id="lily-bunny-uuid",
    job_type="expression",
    config={
        "variants": [
            {"name": "happy", "expression": "happy"},
            {"name": "sad", "expression": "sad"},
            # ... all 23 expressions
        ],
        "count": 50,          # Generate 50 candidates per expression
        "shortlist_size": 5,  # Top 5 per expression for human review
    }
)

# Execute
result = await job_runner.execute(job)
print(f"Generated: {result['total_generated']}, "
      f"Shortlisted: {len(result['shortlisted_ids'])}")
```

### Example 2: Review UI — Enhanced Batch Grid with Configurable Size
```python
# Source: app.py route (enhanced from existing stub)
@app.get("/review/{character_id}", response_class=HTMLResponse)
async def review_page(
    character_id: str,
    request: Request,
    asset_type: str = Query("expression"),
    batch: bool = Query(False),
    grid: str = Query("2x2"),  # NEW: configurable grid size
):
    # ... existing character resolution ...
    
    # Parse grid dimensions
    grid_cols = {"2x2": 2, "3x3": 3, "4x4": 4}.get(grid, 2)
    grid_rows = {"2x2": 2, "3x3": 3, "4x4": 4}.get(grid, 2)
    grid_total = grid_cols * grid_rows
    
    # Limit candidates to grid capacity in batch mode
    candidates_for_grid = candidates[:grid_total] if batch else candidates
    
    return templates.TemplateResponse(
        request, "review.html", {
            "page": "review",
            "character": character,
            "asset_type": asset_type,
            "candidates": candidates_for_grid,
            "batch_mode": batch,
            "grid_cols": grid_cols,     # Passed to template
            "grid_rows": grid_rows,
        }
    )
```

### Example 3: Wired Action Handler (Approve)
```python
# Source: app.py (replacing stub)
@app.post("/approve/{asset_id}")
async def approve_asset(asset_id: str):
    """Approve: shortlisted → approved."""
    try:
        await repo.update_state(asset_id, "approved")
        logger.info("Asset %s approved", asset_id)
    except (NotFoundError, ValueError) as exc:
        logger.warning("Approve failed for %s: %s", asset_id, exc)
    return RedirectResponse(
        url=request.headers.get("referer", "/"),
        status_code=303
    )
```

### Example 4: ComfyUI WebSocket Polling (for production batch tracking)
```python
# Source: Adapted from ComfyUI API developer guides [CITED: aifoss.dev, runflow.io]
import json, uuid, time
import websocket
import requests

SERVER = "127.0.0.1:8188"
CLIENT_ID = str(uuid.uuid4())

def generate_with_ws(workflow: dict, timeout: int = 300) -> dict:
    """Submit workflow to ComfyUI and wait for completion via WebSocket."""
    ws = websocket.WebSocket()
    ws.connect(f"ws://{SERVER}/ws?clientId={CLIENT_ID}")
    
    # Submit
    payload = {"prompt": workflow, "client_id": CLIENT_ID}
    r = requests.post(f"http://{SERVER}/prompt", json=payload, timeout=10)
    r.raise_for_status()
    prompt_id = r.json()["prompt_id"]
    
    # Wait for completion
    start = time.monotonic()
    while True:
        if time.monotonic() - start > timeout:
            requests.post(f"http://{SERVER}/interrupt")
            raise TimeoutError(f"Job {prompt_id} timed out after {timeout}s")
        
        raw = ws.recv()
        if not isinstance(raw, str):
            continue  # Skip binary preview frames
        msg = json.loads(raw)
        if msg["type"] == "executing":
            data = msg["data"]
            if data["node"] is None and data["prompt_id"] == prompt_id:
                break  # null node = graph finished
    
    ws.close()
    
    # Retrieve outputs
    history = requests.get(
        f"http://{SERVER}/history/{prompt_id}", timeout=10
    ).json()
    return history.get(prompt_id, {})
```

### Example 5: ColorVerificationPlugin — Loading Palette from File
```python
# Source: fix for hardcoded palette
import json
from pathlib import Path

def _load_brand_palette() -> dict:
    """Load brand palette from Universe/ColorPalette/brand-palette.json."""
    palette_path = Path(__file__).parent.parent.parent.parent / "Universe" / "ColorPalette" / "brand-palette.json"
    if palette_path.exists():
        with open(palette_path) as f:
            data = json.load(f)
        colors = {}
        for group in ("primary", "pastel"):
            for name, info in data.get(group, {}).items():
                colors[name] = info.get("hex", "")
        return colors
    return DEFAULT_PALETTE  # Fallback
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Python/diffusers for production (Phase 1 D-08/D-19) | ComfyUI + Flux for production (Phase 1b D-02) | Phase 1b discuss-phase | All generation now flows through ComfyUI REST API, not Python model loading. Means ComfyUI must be running at generation time. |
| DINOv2 as primary identity scorer | Multi-metric scoring: DINOv2 35%, Style 20%, Prompt 15%, Quality 15%, Composition 10%, Diversity 5% | D-13 (Phase 1b) | DINOv2 is no longer the sole decision-maker. Reduces false rejects from lighting/pose sensitivity. |
| 2x2 batch grid (Phase 1) | Configurable 3x3, 4x4 batch grids | D-16 (Phase 1b) | Enables faster human review: 9-16 candidates visible at once instead of 4. |

**Deprecated/outdated:**
- `PromptBuilder._known_expressions()` — 22 expressions (code-only). Needs merge with PHASE1.md 23 expression list. Both sources are valid per D-09.
- `PromptBuilder._known_poses()` — 20 poses (code-only). Needs merge with PHASE1.md 20 poses.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | ComfyUI server will be available at localhost:8188 during Phase 1b execution | Standard Stack | Generation pipeline cannot run without ComfyUI. Must install ComfyUI + Flux models before execution. |
| A2 | Flux model weights (flux1-dev.safetensors or Flux.2 Klein) will be in ComfyUI models directory | Standard Stack | Generation fails or produces wrong outputs. Workflow JSON references non-existent checkpoint names. |
| A3 | websocket-client package can be installed via pip | Environment Availability | Fall back to HTTP polling (slower but works). No blocking issue. |
| A4 | DINOv2 cosine similarity ≥ 0.5 indicates same-character identity | Common Pitfalls (Pitfall 3) | If D-14 thresholds (97-99%) are too aggressive, auto-reject may discard valid candidates. Thresholds are configurable per D-14 reversibility. |
| A5 | The merged expression/pose lists (PHASE1.md + code extras) produce valid Flux prompts | Architecture Patterns | New expressions like "blowing_kiss" and "giggling" may not be understood by Flux equally. PromptBuilder warns on unknown names but still produces valid prompts (best-effort pattern). |
| A6 | Flux.1 Dev requires ≥16GB VRAM for full precision; fp8 brings to ~10GB | Environment Availability | If GPU has <10GB VRAM, Flux.1 Dev won't run. Fall back to SDXL (secondary) or Flux.1 Schnell (1-4 step, lower quality). |

## Open Questions

1. **What VRAM does the target machine have?**
   - What we know: ComfyUI + Flux.1 Dev requires 16GB+ (full precision) or ~10GB (fp8). Flux.2 Klein 4B Q4 runs on 4GB.
   - What's unclear: Available GPU/VRAM on the production machine.
   - Recommendation: Identify GPU specs before finalizing Flux model variant. Document in Environment Availability.

2. **How will ComfyUI be installed and configured?**
   - What we know: ComfyUIBackend connects to a running ComfyUI server. Existing code has default template.
   - What's unclear: Whether ComfyUI is already installed, whether it uses Flux.1 Dev or Flux.2 Klein, model paths.
   - Recommendation: This may be part of a separate infrastructure setup or was covered in Phase 1. Verify ComfyUI availability.

3. **What are the correct Flux sampling parameters for character consistency?**
   - What we know: Flux.1 Dev: cfg=3.5, steps=20-28; Flux.2 Klein: cfg=1.0; Flux.1 Schnell: steps=1-4.
   - What's unclear: Optimal params for Cocomelon-style character generation specifically.
   - Recommendation: Start with community-recommended defaults, tune during concept exploration.

4. **Is a dedicated consistency LoRA or ControlNet needed for Lily Bunny before Phase 1c?**
   - What we know: Phase 1c trains the Production LoRA. Phase 1b generates assets without LoRA.
   - What's unclear: Whether Flux can maintain consistent identity across 23 expressions without LoRA.
   - Recommendation: Test identity consistency with pure Flux first. If scores are too low, consider creating a minimal face reference via ControlNet/IP-Adapter in the ComfyUI workflow.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 |
| Config file | pyproject.toml (tool.pytest.ini_options) |
| Quick run command | `pytest tests/ -x --timeout=30` |
| Full suite command | `pytest tests/ --timeout=60 -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CHAR-02 | Reference sheet prompt generation | unit | `pytest tests/test_prompt_builder.py::TestAssetTypeTemplates::test_reference_prompt -x` | ✅ |
| CHAR-03 | Expression prompt generation (updated list) | unit | `pytest tests/test_prompt_builder.py::TestAssetTypeTemplates::test_expression_prompt -x` | ✅ (needs update for merged expression list) |
| CHAR-04 | Pose prompt generation (updated list) | unit | `pytest tests/test_prompt_builder.py::TestAssetTypeTemplates::test_pose_prompt -x` | ✅ (needs update for merged pose list) |
| CHAR-05 | Outfit prompt generation | unit | `pytest tests/test_prompt_builder.py::TestAssetTypeTemplates::test_outfit_prompt -x` | ✅ |
| All | GenerationJob orchestrates pipeline | integration | `pytest tests/test_generation_engine.py -x` | ✅ |
| All | Asset state lifecycle transitions | unit | `pytest tests/test_asset_repository.py -x` | ✅ |
| All | Identity scoring (DINOv2, CLIP, etc.) | integration | `pytest tests/test_identity_engine.py -x` | ✅ |
| D-18 | Lineage metadata in asset model | unit | (new test needed) | ❌ Wave 0 |
| D-16 | Review UI configurable batch grids | integration | (new test needed) | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_prompt_builder.py -x --timeout=30`
- **Per wave merge:** `pytest tests/ --timeout=60 -v`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_prompt_builder.py` — add test cases for merged expression list (blowing_kiss, winking, very_happy, giggling, whistling, etc.) and merged pose list (hugging, holding_hands, pointing, clapping, etc.)
- [ ] `tests/test_prompt_builder.py` — add test for `_known_expressions()` and `_known_poses()` returning correct merged sets
- [ ] `tests/test_asset_repository.py` — add test for lineage metadata field (D-18 compliance)
- [ ] `tests/test_generation_job.py` — add test for ComfyUIBackend integration (or mock verification)
- [ ] `tests/test_review_ui.py` — add test for grid size parameterization (D-16)
- [Framework install] pytest is already installed and configured

## Security Domain

> Required when `security_enforcement` is enabled. Config has `nyquist_validation: true` but no explicit `security_enforcement: false`. Including security analysis.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Review UI is internal-facing (localhost); no auth needed. |
| V3 Session Management | no | Review UI is stateless (each request is independent) |
| V4 Access Control | no | Single-operator internal tool |
| V5 Input Validation | yes | Pydantic v2 schemas enforce all API contracts; SQLite uses parameterized queries |
| V6 Cryptography | no | No stored secrets; no encryption needed for local assets |

### Known Threat Patterns for {Python + ComfyUI}

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| ComfyUI unauthenticated API exposed to network | Tampering | Default ComfyUI binds to 127.0.0.1 only. If exposing remotely, use reverse proxy with API key auth [CITED: runflow.io] |
| Malicious workflow JSON injection | Tampering | Pipeline controls workflow JSON (not user-submitted). If user-submitted workflows are ever allowed, whitelist `class_type` values [CITED: runflow.io] |
| SQL injection | Tampering | All SQLite queries use `?` parameterized placeholders (verified in sqlite_repo.py) |
| Filesystem path traversal | Information Disclosure | Asset file paths use UUID-based naming. Universe directory structure is fixed. |

## Sources

### Primary (HIGH confidence)
- [VERIFIED: codebase inspection] - Phase 1 codebase at `/workspace/AnimationStudio/src/` — all 5 backends, 7 scoring plugins, prompt builder, asset repository, review UI, job queue, diversity filter, generation job orchestrator
- [VERIFIED: Phase 1 context] - D-01 through D-19 decisions from `.planning/phases/01-character-universe/01-CONTEXT.md`
- [VERIFIED: Phase 1b context] - D-01 through D-18 decisions from `.planning/phases/01b-character-asset-production/01b-CONTEXT.md`
- [CITED: eastondev.com/blog/ai/20260724-comfyui-api-batch-automation] - ComfyUI API batch automation guide, July 2026
- [CITED: aifoss.dev/blog/comfyui-api-tutorial-2026] - ComfyUI API tutorial, June 2026
- [CITED: runflow.io/blog/comfyui-api-developer-guide] - ComfyUI API developer guide, April 2026
- [CITED: civitai.com/models/2642426] - Flux Klein multi-angle reference sheet workflow, May 2026
- [CITED: arxiv.org/html/2311.10093v4] - DINOv2 for identity consistency evaluation in diffusion models

### Secondary (MEDIUM confidence)
- [CITED: github.com/facebookresearch/dinov2/issues/147] - DINOv2 sensitivity to lighting/shadow conditions
- [CITED: arxiv.org/html/2511.08087] - VLM-based identity preservation evaluation (CLIP vs DINOv2 comparisons)

### Tertiary (LOW confidence)
- [ASSUMED] - websocket-client package availability
- [ASSUMED] - Flux.1 Dev VRAM requirements (16GB full precision, 10GB fp8)
- [ASSUMED] - DINOv2 cosine similarity threshold of 0.5 for same-character identity

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all tools verified by codebase inspection or official docs
- Architecture: HIGH — patterns derived from existing codebase and established decisions
- Pitfalls: HIGH — ComfyUI API pitfalls documented by multiple authoritative sources
- Code examples: HIGH — adapted from existing codebase with verified extensions

**Research date:** 2026-07-29
**Valid until:** 2026-08-28 (30 days — stable Python/ComfyUI ecosystem)
