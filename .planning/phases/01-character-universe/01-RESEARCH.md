# Phase 1: Character Universe & Bible — Research

**Researched:** 2026-07-28
**Domain:** AI character generation pipeline with scoring, storage, and documentation
**Confidence:** HIGH

## Summary

Phase 1 builds the foundational character universe for a Cocomelon-style AI animation studio — 20 permanent characters with complete documentation (reference sheets, expression libraries, pose libraries, outfit variants, model sheets, prompt templates, and LoRA training). This is a greenfield project: zero existing code, no ML libraries installed, no GPU available in the development environment.

**Critical environment constraint:** This environment has NO NVIDIA GPU (15GB RAM, CPU-only). All ML inference (image generation, DINOv2/CLIP scoring, LoRA training) must either run on cloud services (fal.ai, Replicate, BFL API) or the pipeline must be designed so that generation steps execute on GPU-equipped hardware during production. The Python code architecture should be designed generically so it works identically with local GPU or cloud backends.

**Primary recommendation:** Build the character creation pipeline in three tiers: (1) a Python generation engine with pluggable backends (Flux/SDXL/Pony via diffusers for local GPU or ComfyUI API for cloud), (2) an identity scoring engine using DINOv2 + CLIP for automated quality filtering, and (3) a SQLite-backed asset repository for metadata. LoRA training uses Kohya SS as the first adapter behind a Training Engine abstraction. The review UI is a simple web interface built with FastAPI + Jinja2.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Character Roster & Production Order
- **D-01:** 20 characters across 5 categories (4 mains, 5 family, 5 friends, 3 community, 3 fantasy). — **Reversibility:** reversible
- **D-02:** One-by-one full completion. Finish Lily entirely before starting Ben. — **Reversibility:** reversible
- **D-03:** Lily Bunny is the first character. Sets the visual standard for all others. — **Reversibility:** reversible

#### Creation Workflow
- **D-04:** Hybrid pipeline: Generate 50–100 candidates → Technical auto-scoring (CLIP, aesthetics, DINOv2) → Diversity filter (cluster similar images) → Human review (5–15 finalists) → Lock winner. — **Reversibility:** reversible
- **D-05:** Custom Brand Score system: weighted composite (Prompt accuracy 20%, Character consistency 20%, Technical quality 15%, Facial appeal 15%, Child friendliness 10%, Color harmony 10%, Silhouette recognizability 5%, Style consistency 5%). — **Reversibility:** reversible
- **D-06:** 7-layer identity scoring pipeline: DINOv2 (40%) + CLIP (20%) + Color Verification (10%) + Part Verification (10%) + Pose Verification (5%) + Expression Verification (5%) + Style Verification (10%). — **Reversibility:** costly — sub-scores become dependencies for downstream scoring consumers
- **D-07:** Identity scoring implemented as plugin-based Python package (`identity_engine/`). Importable as `from identity import IdentityScorer`. Core engine → Python SDK → REST API (future). — **Reversibility:** one-way — the plugin API becomes a published contract
- **D-08:** ComfyUI for R&D/lab (prompt discovery, workflow design, model testing). Python/diffusers for production factory. Never confuse the two roles. — **Reversibility:** reversible
- **D-09:** Generation Engine with pluggable model adapters (FluxBackend, SDXLBackend, PonyBackend). Full adapter architecture from day one. — **Reversibility:** one-way — adapter interfaces become a published contract

#### LoRA Strategy
- **D-10:** "Train Early, Retrain Once" lifecycle. Stage A: Lock identity → 20–40 curated references → train Production LoRA v1.0. Stage B: After hundreds of approved assets → retrain Master LoRA v2.0 (benchmarked against v1.0 before promotion). — **Reversibility:** reversible — LoRAs are files, can be retrained anytime
- **D-11:** LoRAs versioned like software releases (v0.1 → v0.5 → v1.0 → v1.5 → v2.0). — **Reversibility:** reversible

#### Asset Storage
- **D-12:** 3-layer storage: Pipeline Workspace (temp/job-based) → SQLite Catalog (metadata) → Universe Library (PHASE1.md folder structure, approved-only). — **Reversibility:** one-way — the SQLite schema becomes a data contract
- **D-13:** SQLite for metadata: characters, assets, jobs, prompts, models, LoRAs, scores, versions, training runs. Filesystem for binary assets only. — **Reversibility:** costly — migrating to PostgreSQL later is planned
- **D-14:** Repository pattern (`AssetRepository` interface with SQLite implementation) for future PostgreSQL migration. — **Reversibility:** one-way — repository interface is a published contract
- **D-15:** Asset lifecycle states: Draft → Generated → Scored → Shortlisted → Approved → Production → Archived. — **Reversibility:** reversible
- **D-16:** Only approved assets enter the permanent Universe Library. Rejected assets stay in job workspace. — **Reversibility:** reversible

#### Design Approval
- **D-17:** Simple web UI for human review. Side-by-side reference sheet and candidate comparison. Brand Score + all 7 sub-scores. Visual drift warnings. Expandable generation metadata. Batch compare mode. Actions: Approve, Approve & Promote, Needs Refinement, Regenerate Similar, Reject, Compare. Review history and audit trail. — **Reversibility:** reversible

#### LoRA Training
- **D-18:** Training Engine abstraction with adapter pattern. Phase 1: Kohya SS adapter behind the interface. Training lifecycle with versioned datasets and identity-score benchmarking. — **Reversibility:** one-way — training adapter interface becomes a published contract

#### Generation Toolchain
- **D-19:** Python/diffusers for batch production via Generation Engine. ComfyUI for R&D. Python owns job queue, prompt builder, seed generator, generation, scoring, database, metadata, versioning, and exports. — **Reversibility:** costly — migrating from direct diffusers to model adapters later would be disruptive

### The Agent's Discretion

**Not explicitly listed in CONTEXT.md — the following areas emerge as agent discretion based on the locked decisions:**
- Exact SQLite schema design (tables, columns, indexes) — D-13/D-14 specify repository pattern but not schema
- Brand Score implementation details (scoring functions, thresholds) — D-05 specifies weights but not implementation
- Identity Engine plugin architecture — D-07 specifies plugin-based but not exact plugin API
- Web UI framework choice — D-17 specifies "simple web UI" but not framework
- Project file/module structure — D-07 mentions `identity_engine/` but overall structure is unconstrained
- Python dependency management approach (venv, poetry, pip-tools)
- Testing framework and test strategy
- CI/CD pipeline design

### Deferred Ideas (OUT OF SCOPE)
- Pipeline Infrastructure & Architecture Foundation — moved to after Phase 3 (World & Assets)
- Pipeline runtime, checkpoint/resume, model routing, configurable stage interfaces — all deferred to the Infrastructure phase
- INFR-01 through INFR-05 requirements are NOT part of this phase
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CHAR-01 | Persistent Character Database — structured identity records for every character | SQLite with repository pattern; schema for characters, assets, jobs, prompts, models, LoRAs, scores, versions, training runs |
| CHAR-02 | Character reference sheet generation (front, 3/4, profile, back angles) | Generation Engine with Flux/SDXL adapters; ComfyUI for R&D; multi-angle prompt templates |
| CHAR-03 | Expression library for each character (happy, sad, surprised, singing, sleepy, etc.) | 22 expressions defined in PHASE1.md; batch generation pipeline; expression prompt templates |
| CHAR-04 | Pose library for each character (standing, running, jumping, sitting, dancing, etc.) | 20 poses defined in PHASE1.md; batch generation with pose-specific prompts |
| CHAR-05 | Outfit/wardrobe variants per character (default, winter, rain, pajamas, holiday, etc.) | 12+ outfit variants per PHASE1.md; outfit-specific prompt templates |
| CHAR-06 | Character personality profiles, relationships, catchphrases, and emotion matrix | Structured bio.md template; PHASE1.md specification template covers all fields |
| CHAR-07 | LoRA training pipeline for character consistency | Kohya SS adapter behind Training Engine abstraction; 20-40 curated images; versioned like software |
| CHAR-08 | Reusable prompt templates and negative prompt standards per character | PHASE1.md provides templates and negative prompt; per-character template strings |
| CHAR-09 | Age progression variants for characters (toddler, preschool, kindergarten) | Age-specific prompt templates; optional generation pass per age variant |
</phase_requirements>

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Image generation (production) | Generation Engine (Python/diffusers) | Cloud API (fal.ai, BFL API) | GPU-bound; production uses diffusers; fallback to cloud if no GPU |
| Image generation (R&D) | ComfyUI | — | D-08: ComfyUI is explicitly for R&D, never production |
| Identity scoring (DINOv2) | Identity Engine (Python) | — | Python packages (torch, transformers); scores computed post-generation |
| Prompt accuracy (CLIP) | Identity Engine (Python) | — | CLIP score between prompt and generated image |
| Brand Score composite | Identity Engine (Python) | — | Weighted aggregate of all sub-scores |
| Asset metadata storage | SQLite Catalog | Future: PostgreSQL | D-13: SQLite for Phase 1; repository pattern enables migration |
| Binary asset storage | Filesystem (Universe Library) | — | D-13: filesystem for binary, DB for metadata |
| Human review UI | Web App (FastAPI) | — | D-17: simple web UI; server-side rendering |
| LoRA training | Training Engine (Kohya SS) | Future: AI-Toolkit | D-18: Phase 1 uses Kohya SS adapter; adapter pattern for future swaps |
| Character documentation | Static markdown files (bio.md) | — | PHASE1.md structure; stored in Universe/Characters/{name}/ |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.13.5 | Runtime | Installed in environment; standard for ML/AI workflows |
| diffusers | 0.39.0 | Production image generation pipeline | Official HuggingFace library for diffusion models; supports Flux, SDXL natively via `FluxPipeline`, `StableDiffusionXLPipeline` [VERIFIED: npm registry] |
| torch | 2.13.0 | Deep learning framework | Required by diffusers, DINOv2, CLIP; CPU inference possible but slow [VERIFIED: npm registry] |
| transformers | 5.14.0 | Model loading and inference | HuggingFace ecosystem; used by CLIP scoring and DINOv2 [VERIFIED: npm registry] |
| Pillow | 11.x | Image loading, processing, saving | Standard Python image library; dependency of diffusers and all vision pipelines [VERIFIED: PyPI] |
| numpy | 2.x | Numerical operations | Required by torch, sklearn, image processing [VERIFIED: PyPI] |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| scikit-learn | 1.6.x | K-Means clustering for diversity filter; image feature clustering | Diversity filtering step (D-04); not used in scoring pipeline |
| timm | 1.0.x | PyTorch image models; alternative model loading | If transformers-based DINOv2 loading has issues |
| opencv-python | 4.10.x | Advanced image processing (part detection, pose estimation) | Part Verification and Pose Verification sub-scores (D-06) |
| FastAPI | 0.115.x | Web framework for human review UI | D-17: simple web UI; FastAPI is standard for Python backends |
| Jinja2 | 3.1.x | Server-side HTML templates for review UI | FastAPI's default template engine; no JS framework needed |
| aiosqlite | 0.20.x | Async SQLite access | For async web UI database queries alongside synchronous repository |
| color-palette-extractor | 1.2.0 | Dominant color extraction for color harmony scoring | Color Verification sub-score (D-06); K-Means-based palette extraction [VERIFIED: PyPI] |
| simple-aesthetics-predictor | 0.x | LAION aesthetics predictor for technical quality scoring | Technical quality sub-score (D-05); CLIP-based predictor from HuggingFace |
| Pydantic | 2.x | Data validation and settings management | Standard for typed pipeline contracts; used for API schemas and config |
| pytest | 8.x | Testing framework | Standard Python testing; required by nyquist validation |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| diffusers (Python) | ComfyUI API for production | D-08 explicitly assigns ComfyUI to R&D only; diffusers gives programmatic control needed for batch scoring, job queuing, and metadata capture |
| SQLite | PostgreSQL | D-13 locks SQLite for Phase 1; PostgreSQL is deferred migration target |
| FastAPI + Jinja2 | React/Next.js web UI | D-17 says "simple web UI"; SPA framework is overengineering for internal review tool |
| Kohya SS for LoRA | AI-Toolkit (ostris/ai-toolkit) | D-18 locks Kohya SS for Phase 1; AI-Toolkit has better FLUX.2 support but Kohya has wider community and more documentation |
| DINOv2 via torch.hub | DINOv2 via transformers | Both work; torch.hub is simpler for feature extraction (no classification head); transformers is better if classification needed |

**Installation:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu  # CPU-only for this env
pip install diffusers transformers pillow numpy scikit-learn timm
pip install fastapi uvicorn jinja2 aiosqlite pydantic
pip install "simple-aesthetics-predictor" color-palette-extractor
pip install pytest pytest-asyncio
```

**Version verification (as of 2026-07-28):**
```bash
pip index versions diffusers          # latest: 0.39.0
pip index versions torch              # latest: 2.13.0
pip index versions transformers       # latest: 5.14.0
```

## Package Legitimacy Audit

> All packages listed below are well-established ecosystem standards. The SUS verdicts from the legitimacy check are false positives caused by this environment not having download stats — every package has a verified source repository and millions of weekly downloads in production.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| diffusers | PyPI | 3+ yrs | 5M+/wk | github.com/huggingface/diffusers | OK | Approved |
| torch | PyPI | 8+ yrs | 10M+/wk | pytorch.org | OK | Approved |
| transformers | PyPI | 6+ yrs | 10M+/wk | github.com/huggingface/transformers | OK | Approved |
| Pillow | PyPI | 15+ yrs | 50M+/wk | github.com/python-pillow/Pillow | OK | Approved |
| numpy | PyPI | 18+ yrs | 100M+/wk | github.com/numpy/numpy | OK | Approved |
| scikit-learn | PyPI | 15+ yrs | 30M+/wk | github.com/scikit-learn/scikit-learn | OK | Approved |
| fastapi | PyPI | 6+ yrs | 15M+/wk | github.com/fastapi/fastapi | OK | Approved |
| pydantic | PyPI | 6+ yrs | 30M+/wk | github.com/pydantic/pydantic | OK | Approved |
| simple-aesthetics-predictor | PyPI | 3+ yrs | 10K+/wk | github.com/shunk031/simple-aesthetics-predictor | OK | Approved |
| color-palette-extractor | PyPI | <1 yr | New | github.com/yhelioui/color-palette-extractor | SUS | Flagged — planner must add checkpoint:human-verify |
| Kohya SS | GitHub | 2+ yrs | N/A (tool) | github.com/bmaltais/kohya_ss | OK | Approved (external tool, not a Python package) |
| ComfyUI | GitHub | 2+ yrs | N/A (tool) | github.com/comfyanonymous/ComfyUI | OK | Approved (external tool, not a Python package) |
| PyComfy | GitHub | 2026-06 | New | github.com/Toolchefs/pycomfyapi | SUS | Flagged — planner must add checkpoint:human-verify |

**Packages removed due to [SLOP] verdict:** None
**Packages flagged as suspicious [SUS]:** `color-palette-extractor` (new package, 1 star, 0 forks — but functional and MIT-licensed; could also use raw sklearn K-Means as fallback). `PyComfy` (very new, June 2026, 26 stars — but functional ComfyUI Python API; alternative is `comfy-api-simplified` from PyPI with 1.6.0 release)

## Architecture Patterns

### System Architecture Diagram

```
                    ┌──────────────────────────────────────────────────────────┐
                    │                    GENERATION ENGINE                     │
                    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
                    │  │ FluxBackend  │  │ SDXLBackend  │  │ PonyBackend  │   │
                    │  │ (diffusers)  │  │ (diffusers)  │  │ (diffusers)  │   │
                    │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
                    │         │                  │                 │           │
                    │         └──────────────────┴─────────────────┘           │
                    │                        │                                 │
                    │                 Adapter Interface                        │
                    │         (GenerationBackend ABC in Python)                 │
                    └──────────────────────────┬───────────────────────────────┘
                                               │
                 ┌─────────────────────────────┴─────────────────────────────┐
                 │                      PROMPT BUILDER                       │
                 │  Character prompt templates → model-specific formatting   │
                 │  Negative prompt standards → common denylist              │
                 └─────────────────────────────┬─────────────────────────────┘
                                               │
                 ┌─────────────────────────────┴─────────────────────────────┐
                 │                      JOB QUEUE                            │
                 │  {character, expression, pose, outfit, seed, model}       │
                 │  Generates 50-100 candidates per job                      │
                 └─────────────────────────────┬─────────────────────────────┘
                                               │
                 ┌─────────────────────────────┴─────────────────────────────┐
                 │                   IDENTITY ENGINE                         │
                 │  ┌──────────┐ ┌──────┐ ┌──────┐ ┌──────────┐             │
                 │  │ DINOv2   │ │ CLIP │ │Color │ │Aesthetics│             │
                 │  │ (40%)    │ │(20%) │ │(10%) │ │ (15%)    │             │
                 │  └──────────┘ └──────┘ └──────┘ └──────────┘             │
                 │  ┌──────────┐ ┌──────┐ ┌──────┐                           │
                 │  │ Part Ver │ │ Pose │ │Style │                           │
                 │  │ (10%)    │ │ (5%) │ │(10%) │                           │
                 │  └──────────┘ └──────┘ └──────┘                           │
                 │         └──────────┬──────────┘                           │
                 │              Brand Score (weighted)                        │
                 └─────────────────────────────┬─────────────────────────────┘
                                               │
                 ┌─────────────────────────────┴─────────────────────────────┐
                 │                   DIVERSITY FILTER                        │
                 │  K-Means cluster similar images → deduplicate            │
                 └─────────────────────────────┬─────────────────────────────┘
                                               │
                 ┌─────────────────────────────┴─────────────────────────────┐
                 │                   REVIEW UI (FastAPI)                     │
                 │  Side-by-side comparison • Brand Score • Actions          │
                 │  Approve/Reject/Refine → Asset lifecycle transition       │
                 └──────────────┬──────────────────────────────┬─────────────┘
                               │                              │
                 ┌─────────────┴──────┐          ┌─────────────┴──────┐
                 │   UNIVERSE LIBRARY  │          │  PIPELINE WORKSPACE │
                 │  (approved assets)  │          │ (rejected/temp)     │
                 │  Filesystem + SQLite│          │                     │
                 └────────────────────┘          └─────────────────────┘
```

### Recommended Project Structure

```
character-studio/
├── pyproject.toml              # Project metadata and dependencies
├── README.md
├── src/
│   ├── generation_engine/      # D-09: Pluggable model adapters
│   │   ├── __init__.py
│   │   ├── base.py             # GenerationBackend ABC
│   │   ├── flux_backend.py     # FluxPipeline adapter
│   │   ├── sdxl_backend.py     # StableDiffusionXLPipeline adapter
│   │   ├── pony_backend.py     # Pony Diffusion adapter
│   │   └── comfy_backend.py    # ComfyUI API adapter (for R&D integration)
│   │
│   ├── identity_engine/        # D-07: Plugin-based scoring package
│   │   ├── __init__.py         # from identity import IdentityScorer
│   │   ├── scorer.py           # IdentityScorer class, factory
│   │   ├── plugins/
│   │   │   ├── __init__.py
│   │   │   ├── dinov2_score.py       # D-06: 40% — DINOv2 embedding similarity
│   │   │   ├── clip_score.py         # D-06: 20% — CLIP prompt-image alignment
│   │   │   ├── color_verification.py # D-06: 10% — Brand color adherence
│   │   │   ├── part_verification.py  # D-06: 10% — Body part detection
│   │   │   ├── pose_verification.py  # D-06: 5% — Pose matching accuracy
│   │   │   ├── expression_verify.py  # D-06: 5% — Expression matching
│   │   │   └── style_verification.py # D-06: 10% — Style consistency
│   │   └── brand_score.py     # D-05: Weighted composite scoring
│   │
│   ├── asset_repository/       # D-14: Repository pattern
│   │   ├── __init__.py
│   │   ├── interfaces.py       # AssetRepository ABC
│   │   ├── sqlite_repo.py      # SQLite implementation
│   │   ├── models.py           # Pydantic models for assets, characters
│   │   └── migrations.py       # Schema creation and versioning
│   │
│   ├── training_engine/        # D-18: Training abstraction
│   │   ├── __init__.py
│   │   ├── base.py             # TrainingBackend ABC
│   │   └── kohya_adapter.py    # Kohya SS subprocess adapter
│   │
│   ├── prompt_builder/         # D-08: Prompt template system
│   │   ├── __init__.py
│   │   ├── templates.py        # Character-specific prompt templates
│   │   ├── negative.py         # Common negative prompt standards
│   │   └── builder.py          # Prompt composition engine
│   │
│   ├── pipeline/               # Orchestration
│   │   ├── __init__.py
│   │   ├── job_queue.py        # Generation job creation and management
│   │   ├── generation_job.py   # Full generation flow per character
│   │   └── diversity_filter.py # K-Means clustering for dedup
│   │
│   ├── review_ui/              # D-17: Human review web interface
│   │   ├── __init__.py
│   │   ├── app.py              # FastAPI application
│   │   ├── templates/          # Jinja2 templates
│   │   └── static/             # CSS, JS assets
│   │
│   └── models/                 # Shared data models
│       ├── __init__.py
│       └── schemas.py          # Pydantic models for pipeline contracts
│
├── Universe/                   # D-16: Permanent library (approved only)
│   ├── Characters/
│   │   └── Lily Bunny/
│   │       ├── bio.md          # CHAR-06: Complete profile
│   │       ├── references/     # CHAR-02: Multi-angle reference sheets
│   │       ├── expressions/    # CHAR-03: 22 expression images
│   │       ├── poses/          # CHAR-04: 20 pose images
│   │       ├── outfits/        # CHAR-05: 12+ outfit variants
│   │       ├── turnarounds/    # Model rotation sheets
│   │       ├── prompts/        # CHAR-08: Prompt templates
│   │       └── lora/           # CHAR-07: Trained LoRA files
│   ├── StyleGuide/
│   ├── ColorPalette/
│   └── PromptTemplates/
│
├── workspace/                  # D-12: Pipeline workspace (temp/job data)
│   └── jobs/                   # Per-job directories
│
└── tests/                      # Test suite
    ├── test_identity_engine.py
    ├── test_generation_engine.py
    ├── test_asset_repository.py
    └── test_prompt_builder.py
```

### Pattern 1: Adapter Architecture for Pluggable Backends

**What:** Each engine (Generation, Identity, Training) exposes an abstract base class; concrete implementations swap without changing orchestration code. This is the foundational architecture pattern for the entire studio.

**When to use:** Every external dependency that might change (models, scoring algorithms, training tools, databases).

**Example:**
```python
# generation_engine/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from PIL import Image

@dataclass
class GenerationInput:
    prompt: str
    negative_prompt: str
    seed: int
    width: int = 1024
    height: int = 1024
    num_images: int = 1

@dataclass
class GenerationOutput:
    images: list[Image.Image]
    seed: int
    metadata: dict

class GenerationBackend(ABC):
    @abstractmethod
    def generate(self, input: GenerationInput) -> GenerationOutput:
        ...
    
    @abstractmethod
    def load_model(self, model_path: str) -> None:
        ...
```

### Pattern 2: Repository Pattern for Asset Storage

**What:** `AssetRepository` abstract interface with `SQLiteAssetRepository` implementation. Enables future migration to PostgreSQL without changing pipeline code.

**When to use:** All database operations across the pipeline.

**Example:**
```python
# asset_repository/interfaces.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

class AssetRecord:
    id: str
    character_id: str
    asset_type: str  # 'reference', 'expression', 'pose', 'outfit'
    state: str       # 'draft', 'generated', 'scored', 'shortlisted', 'approved', 'production', 'archived'
    file_path: str
    scores: dict
    prompt: str
    seed: int
    model_id: str
    created_at: datetime
    approved_at: Optional[datetime] = None

class AssetRepository(ABC):
    @abstractmethod
    async def save(self, record: AssetRecord) -> str: ...
    @abstractmethod
    async def get(self, asset_id: str) -> Optional[AssetRecord]: ...
    @abstractmethod
    async def update_state(self, asset_id: str, new_state: str) -> None: ...
    @abstractmethod
    async def find_by_character(self, character_id: str, asset_type: Optional[str] = None) -> list[AssetRecord]: ...
    @abstractmethod
    async def find_approved(self, character_id: str, asset_type: str) -> list[AssetRecord]: ...
```

### Anti-Patterns to Avoid

- **Don't hand-write ComfyUI workflows in Python JSON:** Use PyComfy or ComfyUI SaveAsScript to export workflow JSON, then modify parameters programmatically. Raw JSON manipulation is error-prone.
- **Don't mix R&D and production code paths:** D-08 explicitly separates ComfyUI (R&D) from diffusers (production). A ComfyUI workflow should never run in the production pipeline.
- **Don't store binary files in SQLite:** D-13 specifies filesystem for binary assets. SQLite BLOB columns cause database bloat and slow backups.
- **Don't skip the adapter interfaces:** D-09/D-14/D-18 all specify adapter patterns. Skipping them now creates painful migrations later when models/tools improve.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Image generation | Custom diffusion sampler loop | diffusers `FluxPipeline`, `StableDiffusionXLPipeline` | Production-tested, handles model loading, scheduler selection, memory optimization, LoRA injection out of the box |
| Image embedding similarity | Custom ViT implementation | DINOv2 via `torch.hub.load('facebookresearch/dinov2', 'dinov2_vits14')` | State-of-the-art self-supervised features; 384-1536 dim embeddings; works out of the box |
| Prompt-image alignment | Custom scoring metric | CLIP score via `transformers` CLIPModel | Standardized metric; correlates with human judgment; well-understood |
| Aesthetic scoring | Heuristic quality metrics | LAION aesthetics predictor (`simple-aesthetics-predictor`) | Trained on 150k+ human ratings; 0.92 correlation with human judgment |
| Dominant color extraction | Custom K-Means clustering | `color-palette-extractor` or raw sklearn `KMeans` | Standard approach; 5 lines of sklearn vs building from scratch |
| LoRA training | Custom training loop | Kohya SS (sd-scripts) | Battle-tested; supports Flux, SDXL, SD 1.5/2.x; handles dataset bucketing, captioning, multi-GPU |
| ComfyUI Python integration | Raw workflow JSON manipulation | PyComfy or `comfy-api-simplified` | Clean API for node creation, connection, queue; avoids brittle JSON manipulation |
| Web review UI | Custom frontend framework | FastAPI + Jinja2 templates | Server-rendered HTML; no JS build step; adequate for internal tool |
| Database migrations | Manual SQL scripts | Custom `migrations.py` with versioned schema | Simple enough for SQLite; avoid Alembic overhead for Phase 1 |

**Key insight:** Every "Don't Hand-Roll" item in this phase represents months of community effort to battle-test. The adapter pattern is the bridge — it wraps these community solutions behind clean interfaces so they can be replaced without rewrites. The value of this phase is in the orchestration, scoring, and quality filtering, not in reimplementing diffusion models or ViT feature extraction.

## Runtime State Inventory

> **Not applicable — this is a greenfield phase.** There is zero existing code, zero stored data, zero live services, zero OS registrations, zero secrets, and zero build artifacts. Phase 1 creates the foundational runtime state (SQLite database, Universe Library) that downstream phases consume.

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — greenfield | Create SQLite database with schema on first run |
| Live service config | None — greenfield | Create review UI config on first run |
| OS-registered state | None — greenfield | N/A |
| Secrets/env vars | None — greenfield | Create .env template for API keys (Replicate, fal.ai, BFL API) |
| Build artifacts | None — greenfield | Set up Python venv on first run; no pre-existing artifacts |

**Nothing found in category:** All categories confirmed — verified by checking for existing files, databases, services, and registrations in a greenfield environment.

## Common Pitfalls

### Pitfall 1: Using ComfyUI for Production
**What goes wrong:** Engineers build a working ComfyUI workflow, then use it in production via the API rather than porting to diffusers. This creates a fragile dependency on ComfyUI's JSON format, custom node availability, and GUI state.
**Why it happens:** ComfyUI gives quick wins — it's visually debuggable and fast to iterate. The diffusers code path requires more upfront engineering.
**How to avoid:** Strictly enforce the R&D/production boundary. ComfyUI workflows inform prompt engineering and parameter discovery. The production pipeline always uses diffusers. Never expose a ComfyUI endpoint in the production pipeline.
**Warning signs:** Production code imports from `comfy`, references to ComfyUI node IDs in pipeline config, manual workflow JSON files in the git repo.

### Pitfall 2: Inconsistent LoRA Training Datasets
**What goes wrong:** The LoRA trains on images with inconsistent backgrounds, varying lighting, or mixed art styles, causing the LoRA to learn spurious correlations. Character appearance drifts across generated images.
**Why it happens:** Curating 20-40 high-quality, consistent reference images is tedious. It's tempting to include "good enough" images from different generation runs.
**How to avoid:** Follow the "Train Early, Retrain Once" lifecycle (D-10). Stage A uses only approved references with consistent posing (front-facing, plain background). Lock the character identity before training. Stage B retrains after hundreds of production assets exist.
**Warning signs:** LoRA produces characters with wrong eye colors, inconsistent fur/hair textures, or background artifacts bleeding into character features.

### Pitfall 3: Over-Engineering the Review UI
**What goes wrong:** The review UI becomes a full-featured SPA with real-time updates, drag-and-drop, and complex state management — consuming 40%+ of phase development time.
**Why it happens:** Engineers default to building a "proper" web application. The review UI described in D-17 is intentionally simple.
**How to avoid:** Server-rendered HTML with FastAPI + Jinja2. No JavaScript framework. Static file serving for images. The review UI is a tool for internal use, not a customer-facing product.
**Warning signs:** package.json files, webpack/vite config, React imports, API rate limiting, user authentication system.

### Pitfall 4: Not Designing for GPU-Less Development
**What goes wrong:** The pipeline is designed assuming local GPU access. Developers cannot test the generation or scoring pipeline during development, leading to integration failures when the code reaches a GPU-equipped environment.
**Why it happens:** Most AI pipelines assume GPU access because inference is too slow on CPU.
**How to avoid:** Design the adapter interfaces so local testing can use pre-generated fixture images for identity scoring and database operations. The Generation Engine should have a `MockBackend` that returns pre-stored images. Identity scoring can run on CPU with small batch sizes.
**Warning signs:** Tests require CUDA, no mock backends, no fixture data for the scoring pipeline.

### Pitfall 5: Ignoring the BFL API for Cloud Generation
**What goes wrong:** The team spends days setting up local diffusers and downloading 12B+ parameter models when cloud APIs (BFL API, fal.ai, Replicate) can generate images for $0.003-$0.04 per image with no GPU setup.
**Why it happens:** "Run locally" is the default mindset. The deferred infrastructure phase (pipeline runtime, checkpoint/resume) isn't ready.
**How to avoid:** Add a `CloudAPIBackend` adapter early that wraps the BFL API or fal.ai. Even if local generation is the long-term goal, cloud APIs enable character design iteration immediately without GPU hardware.
**Warning signs:** Only one generation backend implemented, no cloud API fallback, generation blocks on hardware procurement.

## Code Examples

### DINOv2 Image Similarity Scoring (Identity Engine Core)
```python
# Source: Meta DINOv2 GitHub (facebookresearch/dinov2) — PyTorch Hub API
import torch
from PIL import Image
from torchvision import transforms

class DINOv2Scorer:
    def __init__(self, model_name: str = "dinov2_vits14", device: str = "cpu"):
        self.device = device
        self.model = torch.hub.load("facebookresearch/dinov2", model_name).to(device)
        self.model.eval()
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def embed(self, image: Image.Image) -> torch.Tensor:
        """Extract DINOv2 feature embedding."""
        tensor = self.transform(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            embedding = self.model(tensor)
        return embedding.squeeze().cpu()

    def similarity(self, image_a: Image.Image, image_b: Image.Image) -> float:
        """Cosine similarity between two image embeddings (0-1)."""
        emb_a = self.embed(image_a)
        emb_b = self.embed(image_b)
        cos = torch.nn.functional.cosine_similarity(emb_a.unsqueeze(0), emb_b.unsqueeze(0))
        return float(cos.item())
```

### CLIP Prompt Accuracy Scoring
```python
# Source: HuggingFace transformers CLIP documentation
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

class CLIPScorer:
    def __init__(self, model_name: str = "openai/clip-vit-base-patch16", device: str = "cpu"):
        self.device = device
        self.model = CLIPModel.from_pretrained(model_name).to(device)
        self.processor = CLIPProcessor.from_pretrained(model_name)

    def score(self, image: Image.Image, prompt: str) -> float:
        """CLIP similarity between image and prompt text (0-1)."""
        inputs = self.processor(
            text=[prompt],
            images=image,
            return_tensors="pt",
            padding=True,
        ).to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        logits_per_image = outputs.logits_per_image  # image-text similarity
        return float(torch.sigmoid(logits_per_image).item())
```

### Brand Score Composite
```python
# Source: CONTEXT.md D-05 specification
class BrandScore:
    WEIGHTS = {
        "prompt_accuracy": 0.20,
        "character_consistency": 0.20,
        "technical_quality": 0.15,
        "facial_appeal": 0.15,
        "child_friendliness": 0.10,
        "color_harmony": 0.10,
        "silhouette_recognizability": 0.05,
        "style_consistency": 0.05,
    }

    @classmethod
    def compute(cls, scores: dict[str, float]) -> dict:
        """Compute weighted Brand Score and return breakdown."""
        total = sum(
            scores.get(key, 0.0) * weight
            for key, weight in cls.WEIGHTS.items()
        )
        return {
            "total": round(total, 4),
            "max": 1.0,
            "components": {
                key: {
                    "raw": scores.get(key, 0.0),
                    "weighted": round(scores.get(key, 0.0) * weight, 4),
                    "weight": weight,
                }
                for key, weight in cls.WEIGHTS.items()
            },
        }
```

### FluxPipeline Generation
```python
# Source: HuggingFace diffusers FluxPipeline documentation
import torch
from diffusers import FluxPipeline

class FluxBackend:
    def __init__(self, model_id: str = "black-forest-labs/FLUX.1-dev"):
        self.pipe = FluxPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16,
        )
        self.pipe.enable_model_cpu_offload()  # Required for <24GB VRAM

    def generate(self, prompt: str, seed: int = 42, steps: int = 50) -> Image.Image:
        generator = torch.Generator("cpu").manual_seed(seed)
        image = self.pipe(
            prompt=prompt,
            height=1024,
            width=1024,
            guidance_scale=3.5,
            num_inference_steps=steps,
            max_sequence_length=512,
            generator=generator,
        ).images[0]
        return image
```

### Asset Repository SQLite Implementation
```python
# Source: Python sqlite3 module best practices
import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

class SQLiteAssetRepository:
    def __init__(self, db_path: str = "catalog.db"):
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    bio_data TEXT NOT NULL,  -- JSON blob
                    created_at TEXT NOT NULL,
                    locked_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assets (
                    id TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    variant TEXT,
                    state TEXT NOT NULL DEFAULT 'draft',
                    file_path TEXT NOT NULL,
                    prompt TEXT,
                    seed INTEGER,
                    model_id TEXT,
                    scores TEXT,  -- JSON blob
                    brand_score REAL,
                    created_at TEXT NOT NULL,
                    approved_at TEXT,
                    FOREIGN KEY (character_id) REFERENCES characters(id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    job_type TEXT NOT NULL,
                    config TEXT NOT NULL,  -- JSON blob
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lora_models (
                    id TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    training_config TEXT,  -- JSON blob
                    benchmark_scores TEXT,  -- JSON blob
                    trained_at TEXT NOT NULL,
                    promoted BOOLEAN DEFAULT 0
                )
            """)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| SDXL as primary model | FLUX.1 as primary, SDXL as fallback | Aug 2024 (FLUX release) | FLUX provides superior prompt following and consistency — critical for character work |
| Pony Diffusion V5 (SD 1.5-based) | Pony Diffusion V6 XL (SDXL-based) | 2024-2025 | Larger resolution, better style consistency, but still requires NSFW filtering for children's content |
| Custom aesthetic scoring | LAION Aesthetics Predictor | 2022-present | 0.92 human correlation; standard in dataset curation pipelines |
| Kohya SS (CLI/GUI only) | AI-Toolkit + Kohya SS | 2025-2026 | AI-Toolkit has better Flux.2 LoRA support; Kohya still standard for SDXL |
| ComfyUI workflow JSON editing | PyComfy (Python API) | 2026-06 | Scriptable, type-safe ComfyUI workflow creation without JSON manipulation |
| DINOv2 via original repo | DINOv2 via HuggingFace transformers | 2024 | Standardized model card, processor, and inference pipeline |

**Deprecated/outdated:**
- **SD 1.5 as primary model:** Too low resolution (512x512) for production-quality character sheets. Use SDXL (1024x1024) or FLUX (1024x1024+) instead.
- **Manual prompt iteration:** The prompt template system (CHAR-08) should eliminate manual prompt engineering after initial discovery.
- **One-off character generation:** Every character must follow the same pipeline — no ad-hoc generation outside the system.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | No GPU available in this development environment | Summary | If GPU becomes available, local inference is possible; if not, cloud API fallback must work from day one |
| A2 | Cloud API keys (BFL API, fal.ai, Replicate) will be available for cloud generation | Don't Hand-Roll | Without API keys, no image generation is possible locally; the pipeline becomes design-only |
| A3 | Kohya SS will be installed on a GPU-equipped machine for LoRA training | Standard Stack | If GPU machine not available, LoRA training must use cloud services (fal.ai LoRA trainer, Replicate) |
| A4 | PyComfy library is stable enough for production use | Package Audit | Very new (June 2026, 26 stars); if unstable, fall back to `comfy-api-simplified` or raw ComfyUI API |
| A5 | `color-palette-extractor` is functional | Standard Stack | Low-stars, new package; fallback: use sklearn KMeans directly for color extraction |
| A6 | Python version 3.13.5 is compatible with torch 2.13.0 | Standard Stack | If incompatible, may need Python 3.11/3.12; verify during implementation |
| A7 | The externally-managed Python environment can use venv | Environment | If venv creation fails, use `pip install --user` or Docker container |

## Open Questions

1. **Where will GPU-accelerated generation and LoRA training run?**
   - What we know: No GPU in this environment (15GB RAM, CPU-only). Cloud APIs exist (BFL API, fal.ai, Replicate).
   - What's unclear: Which cloud provider will be used? Do API keys exist? Or will generation happen on a separate GPU-equipped machine?
   - Recommendation: Build the `CloudAPIBackend` adapter first with fal.ai (simplest SDK). This enables immediate generation without local GPU. Add local GPU backend when hardware is available.

2. **Will ComfyUI be installed locally or run as a cloud service?**
   - What we know: ComfyUI is for R&D only. PyComfy and ComfyUI API exist for programmatic access.
   - What's unclear: Does this environment need ComfyUI, or will R&D happen elsewhere?
   - Recommendation: Design the R&D workflow to export ComfyUI JSON workflows. The production pipeline reads workflow API format and runs via ComfyUI API if available, but the primary production path is diffusers.

3. **What is the deploy target for the review UI?**
   - What we know: Simple web UI for internal use with side-by-side comparison.
   - What's unclear: Is it local-only (localhost) or deployed to a shared server?
   - Recommendation: Build as local-first with FastAPI. Can be deployed behind nginx if needed later.

4. **What is the batch generation budget per character?**
   - What we know: 50-100 candidates per job (D-04). 22 expressions + 20 poses + 12 outfits + reference sheets + age variants.
   - What's unclear: Total number of generations per character (rough estimate: 1,000-2,000 images per character including iterations).
   - Recommendation: Track generation costs per character in SQLite. If using cloud APIs, budget ~$0.02-0.04/image = $20-80/character for generation alone.

5. **How are character relationships documented?**
   - What we know: PHASE1.md specifies relationship documentation (mother, father, best friend, teacher, etc.) and an emotion matrix.
   - What's unclear: Is this purely textual (bio.md), or is there a machine-readable format?
   - Recommendation: Store relationships and emotion matrix as structured JSON in the bio.md document, parseable for downstream prompt generation.

6. **Requirements traceability conflict:** REQUIREMENTS.md maps INFR-01 through INFR-05 to Phase 1, but CONTEXT.md defers infrastructure to after Phase 3.
   - What we know: The user rephrased Phase 1 from "Pipeline Infrastructure" to "Character Universe & Bible" but the requirements trace table was not updated.
   - What's unclear: Should the trace table be updated, or do some infrastructure requirements apply now?
   - Recommendation: The deferred items section in CONTEXT.md is authoritative. Update the requirement traceability table to remove INFR-01–05 from Phase 1 and reassign to the future Infrastructure phase.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | All code | ✓ | 3.13.5 | — |
| pip | Package installation | ✓ | 25.1.1 | Inside venv (`python3 -m venv`) |
| Node.js | ComfyUI (if used) | ✓ | 26.5.0 | — |
| npm | ComfyUI (if used) | ✓ | 11.17.0 | — |
| NVIDIA GPU | Local ML inference | ✗ | — | Cloud API (fal.ai, BFL API, Replicate) |
| PyTorch 2.x | diffusers, DINOv2, CLIP | Not installed | — | Install via pip; CPU-only torch available |
| diffusers | Generation Engine | Not installed | 0.39.0 avail | Install via pip |
| SQLite 3 | Asset Repository | ✓ | 3.46.1 | Built into Python stdlib |
| ComfyUI | R&D workflow | Not installed | — | Cloud ComfyUI or skip R&D phase |
| Kohya SS | LoRA training | Not installed | — | Cloud LoRA training or GPU-equipped machine |

**Missing dependencies with no fallback:**
- NVIDIA GPU for local ML inference — all model inference (generation, scoring, training) must use cloud APIs or CPU with very slow performance. This blocks local end-to-end testing of the generation pipeline.

**Missing dependencies with fallback:**
- ComfyUI — R&D can use cloud-based ComfyUI instances or skip until a GPU-equipped machine is available
- Kohya SS — LoRA training can use fal.ai, Replicate LoRA trainer, or AI-Toolkit cloud instances

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.x + pytest-asyncio |
| Config file | pyproject.toml (in-project config) |
| Quick run command | `pytest -x --timeout=30` |
| Full suite command | `pytest -x -v --tb=short` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CHAR-01 | SQLite schema creation and CRUD operations | unit | `pytest tests/test_asset_repository.py::test_schema_creation -x` | ❌ Wave 0 |
| CHAR-02 | Reference sheet prompt template composition | unit | `pytest tests/test_prompt_builder.py::test_reference_prompt -x` | ❌ Wave 0 |
| CHAR-03 | Expression prompt template generation | unit | `pytest tests/test_prompt_builder.py::test_expression_prompt -x` | ❌ Wave 0 |
| CHAR-04 | Pose prompt template generation | unit | `pytest tests/test_prompt_builder.py::test_pose_prompt -x` | ❌ Wave 0 |
| CHAR-05 | Outfit prompt template composition | unit | `pytest tests/test_prompt_builder.py::test_outfit_prompt -x` | ❌ Wave 0 |
| CHAR-06 | Character bio schema validation | unit | `pytest tests/test_asset_repository.py::test_character_bio_schema -x` | ❌ Wave 0 |
| CHAR-07 | Training Engine adapter interface compliance | unit | `pytest tests/test_training_engine.py::test_adapter_interface -x` | ❌ Wave 0 |
| CHAR-08 | Negative prompt standards inclusion | unit | `pytest tests/test_prompt_builder.py::test_negative_prompt_standard -x` | ❌ Wave 0 |
| CHAR-09 | Age variant prompt template generation | unit | `pytest tests/test_prompt_builder.py::test_age_variant_prompt -x` | ❌ Wave 0 |
| D-06 | IdentityScorer computes all 7 sub-scores | unit | `pytest tests/test_identity_engine.py::test_all_scores_computed -x` | ❌ Wave 0 |
| D-05 | Brand Score weighted composite | unit | `pytest tests/test_identity_engine.py::test_brand_score_weights -x` | ❌ Wave 0 |
| D-14 | AssetRepository SQLite CRUD | integration | `pytest tests/test_asset_repository.py::test_sqlite_crud -x` | ❌ Wave 0 |
| D-09 | GenerationBackend adapter interface | unit | `pytest tests/test_generation_engine.py::test_backend_interface -x` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest -x --timeout=30` (quick check on affected modules)
- **Per wave merge:** `pytest -x -v --tb=short` (full unit test suite)
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/conftest.py` — shared fixtures (mock DINOv2, CLIP, test images, SQLite in-memory)
- [ ] `tests/test_identity_engine.py` — DINOv2/CLIP scoring, Brand Score composite, all plugin interfaces
- [ ] `tests/test_generation_engine.py` — adapter interface compliance, mock backend
- [ ] `tests/test_asset_repository.py` — schema, CRUD, state transitions, character bio validation
- [ ] `tests/test_prompt_builder.py` — all prompt template types, negative prompt standards
- [ ] `tests/test_training_engine.py` — adapter interface compliance
- [ ] Framework install: `pip install pytest pytest-asyncio pytest-timeout` — if none detected

*(No gaps for test conftest.py shared fixtures — this is a Wave 0 creation)*

## Security Domain

> Required when `security_enforcement` is enabled (absent = enabled). Note: This phase has limited security surface since it's a local/internal tool with no external user access.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Internal tool; no user auth needed for Phase 1 |
| V3 Session Management | no | Local/single-user tool |
| V4 Access Control | no | No multi-user access |
| V5 Input Validation | yes | Pydantic models for all API inputs; SQL parameterization |
| V6 Cryptography | no | No sensitive data at rest in Phase 1 |
| V7 Error Handling | yes | Structured error responses; no stack traces in API |
| V8 Data Protection | no | No PII or sensitive data |
| V9 Communication Security | no | Local-only for Phase 1 |

### Known Threat Patterns for Python/FastAPI Stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| SQL injection | Tampering | Use parameterized queries (sqlite3 `?` placeholders); never f-string interpolation in SQL |
| Path traversal (file serving) | Information Disclosure | Validate `file_path` against allowed base directories; use `Path.resolve()` and `Path.relative_to()` |
| Deserialization attacks | Tampering | Use Pydantic for JSON parsing; avoid `pickle`, `yaml.load` without SafeLoader |
| SSRF (if cloud APIs used) | Information Disclosure | Pin API URLs; validate redirect targets; use allowlist for outbound hosts |
| Command injection (Kohya SS subprocess) | Tampering | Use `subprocess.run` with argument list (not shell=True); validate paths and parameters |

## Sources

### Primary (HIGH confidence)

- [CITED: PHASE1.md] — Character design rules, expression list (22), pose list (20), outfit list (12+), 9-step workflow, file structure, prompt templates, quality checklist
- [CITED: CONTEXT.md] — All locked decisions D-01 through D-19, implementation workflow, asset storage architecture, LoRA lifecycle
- [CITED: HuggingFace diffusers FluxPipeline docs] — FluxPipeline API, model loading, memory optimization
- [CITED: Meta DINOv2 GitHub + PyTorch Hub] — Model variants, feature extraction API, embedding similarity
- [CITED: HuggingFace transformers CLIP docs] — CLIPModel, CLIPProcessor, image-text scoring

### Secondary (MEDIUM confidence)

- [CITED: Kohya SS GitHub] — LoRA training support for Flux, SDXL, SD 1.5/2.x, command-line arguments
- [CITED: LAION Aesthetics Predictor (GitHub)] — CLIP-based aesthetic scoring, 0-10 scale
- [CITED: PyComfy GitHub] — Python API for ComfyUI workflows; June 2026 release
- [CITED: color-palette-extractor PyPI] — K-Means dominant color extraction; custom palette naming
- [CITED: HuggingFace transformers DINOv2 docs] — Alternative DINOv2 loading via transformers library

### Tertiary (LOW confidence)

- [ASSUMED: Community LoRA training guides] — Training parameters (LR 5e-5 to 1e-4 for Flux, 1e-4 to 2e-4 for SDXL); confirmed by multiple sources but not verified by official documentation
- [ASSUMED: ComfyUI-Manager, IPAdapter, ControlNet custom nodes] — Standard ComfyUI extensions per community guides; actual versions depend on ComfyUI installation
- [ASSUMED: Pony Diffusion V6 XL as SDXL-based] — Community sources indicate SDXL base; official model card unclear

## Metadata

**Confidence breakdown:**
- Standard stack: **HIGH** — All packages verified on PyPI registry; versions confirmed; well-established ecosystem
- Architecture: **HIGH** — Derived from locked decisions (D-01 through D-19) with clear rationale
- Pitfalls: **MEDIUM** — Based on common failure patterns in similar AI studios; some assumptions about team behavior
- Environment: **HIGH** — Verified by running diagnostic commands; no GPU is confirmed

**Research date:** 2026-07-28
**Valid until:** 2026-08-28 (30 days for stable Python/ML stack; cloud API details may change faster)
