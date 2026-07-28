# Phase 1: Character Universe & Bible — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-28
**Phase:** 1-Character-Universe
**Areas discussed:** Character roster priority, Creation workflow automation, LoRA timing, Asset storage approach, Design approval gate, Image generation toolchain

---

## Character Roster Priority

| Option | Description | Selected |
|--------|-------------|----------|
| Core 4 mains + family | Lily, Ben, Charlie, Daisy + Mom, Dad, Grandma, Grandpa, Baby | |
| All 4 mains + family + top friends | Core 9 + 3-4 friends | |
| Full 20 characters | As many as possible toward the 20 target | ✓ |

**User's choice:** Full 20 characters
**Notes:** User wants the full target of 20 characters, not a smaller initial set.

| Option | Description | Selected |
|--------|-------------|----------|
| 4 mains + 5 family + 5 friends + 3 community + 3 fantasy | The full spread across categories | ✓ |
| All 4 mains + 5 family + 8 friends + 3 fantasy | Focus on friends over community | |
| 4 mains + 4 family + 4 friends + 4 community + 4 fantasy | Equal spread across categories | |

**User's choice:** 4 mains + 5 family + 5 friends + 3 community + 3 fantasy
**Notes:** Mains: Lily, Ben, Daisy, Charlie. Family: Mom, Dad, Grandma, Grandpa, Baby. Friends: Cat, Dog, Elephant, Monkey, Cow. Community: Teacher, Doctor, Firefighter. Fantasy: Dragon, Unicorn, Dinosaur.

| Option | Description | Selected |
|--------|-------------|----------|
| One-by-one full completion | Finish Lily entirely before starting Ben | ✓ |
| Batch by stage | Concept all 20 → select all → then generate expressions | |
| Batch mains, then one-by-one | Generate all 4 mains in parallel, then supporting one by one | |

**User's choice:** One-by-one full completion

| Option | Description | Selected |
|--------|-------------|----------|
| Lily Bunny first | Main character, sets the benchmark | ✓ |
| Ben Bear first | Start simpler to validate workflow | |

**User's choice:** Lily Bunny first

---

## Creation Workflow Automation

| Option | Description | Selected |
|--------|-------------|----------|
| Generate 100+, auto-score with CLIP | Bulk generation, auto-scoring, hand-pick | |
| Iterative small batches | 10-15 at a time, refine prompts | |
| Hybrid | 50+, auto-score to top 5, manual selection | ✓ |

**User's choice:** Full hybrid pipeline detailed by user: Generate 50-100 → Technical Validation → Diversity Filter → Human Review (5-15 finalists) → Lock Winner. Plus custom Brand Score system.
**Notes:** User designed a comprehensive pipeline including CLIP similarity scoring, aesthetic scoring, DINOv2 character consistency, composition checks, diversity clustering, and a custom Brand Score with weighted metrics.

| Option | Description | Selected |
|--------|-------------|----------|
| Build scoring pipeline now | Implement all scoring now | ✓ |
| Manual first, automate later | Manual selection first | |

**User's choice:** Build scoring pipeline now

| Option | Description | Selected |
|--------|-------------|----------|
| DINOv2 embeddings | SOTA for visual similarity | |
| CLIP embedding distance | General baseline | |
| Both — ensemble | Weighted combination | |

**User's choice:** 7-layer identity scoring: DINOv2 (40%) + CLIP (20%) + Color Verification (10%) + Part Verification (10%) + Pose Verification (5%) + Expression Verification (5%) + Style Verification (10%). Plugin-based architecture.

| Option | Description | Selected |
|--------|-------------|----------|
| Python + diffusers | HuggingFace diffusers library | |
| ComfyUI API | ComfyUI as backend service | |
| Both | Diffusers primary, ComfyUI for exploration | |

**User's choice:** ComfyUI for R&D/lab, Python/diffusers for production. GenerationEngine with pluggable model adapters.

| Option | Description | Selected |
|--------|-------------|----------|
| Python module first | IdentityScorer class in a Python package | |
| API service from day one | /identity/score endpoint | |

**User's choice:** Python package (identity_engine/) with plugin architecture. Core engine → Python SDK → REST API (future).

| Option | Description | Selected |
|--------|-------------|----------|
| Full adapter architecture now | GenerationEngine with concrete backends | ✓ |
| Direct diffusers with skeleton | Simple adapter, backends later | |

**User's choice:** Full adapter architecture now

---

## LoRA Timing

| Option | Description | Selected |
|--------|-------------|----------|
| Train after full approval | Train LoRA after all assets are done | |
| Train first, then generate | Train LoRA on concept art, use for all subsequent generation | ✓ |
| Skip LoRAs for Phase 1 | IPAdapter + prompt engineering only | |

**User's choice:** "Train Early, Retrain Once" — Stage A (Production LoRA v1.0 after 20-40 curated references), Stage B (Master LoRA v2.0 after hundreds of approved assets)
**Notes:** User designed a two-stage lifecycle. LoRA versioned like software releases (v0.1 → v0.5 → v1.0 → v1.5 → v2.0). LoRA retrained only when benchmarked improvement over previous version.

| Option | Description | Selected |
|--------|-------------|----------|
| ComfyUI-FluxTrainer | Visual node-based training | |
| Kohya SS / sd-scripts | Command-line training | ✓ |
| AI Toolkit / diffusers train | HuggingFace training scripts | |

**User's choice:** Kohya SS as training adapter behind a Training Engine abstraction. All training metadata versioned.

---

## Asset Storage Approach

| Option | Description | Selected |
|--------|-------------|----------|
| Filesystem only | PHASE1.md folder structure | |
| SQLite + filesystem | SQLite for metadata, files on disk | ✓ |
| Filesystem + JSON index | JSON manifest per character | |

**User's choice:** SQLite + Filesystem. SQLite for metadata (characters, assets, jobs, prompts, models, LoRAs, scores, versions, training runs). Filesystem for binary assets.

| Option | Description | Selected |
|--------|-------------|----------|
| PHASE1.md layout exactly | Human-friendly folder structure | |
| Pipeline-dictated layout | Organized by type then character | |
| Hybrid | Both, with SQLite bridging | ✓ |

**User's choice:** 3-layer storage: Pipeline Workspace (temp/job-based) → SQLite Catalog → Universe Library (PHASE1.md structure, approved-only). Asset lifecycle states (Draft → Generated → Scored → Shortlisted → Approved → Production → Archived).

| Option | Description | Selected |
|--------|-------------|----------|
| Repository pattern now | Abstract AssetRepository interface | ✓ |
| Direct SQLite | Simple sqlite3 calls | |

**User's choice:** Repository pattern from day one for future PostgreSQL migration.

---

## Design Approval Gate

| Option | Description | Selected |
|--------|-------------|----------|
| CLI review tool | Python CLI, fastest to build | |
| Simple web UI | Lightweight HTML page with scores | ✓ |
| Markdown review sheet | Editable markdown file | |

**User's choice:** Simple web UI — but evolved into a Professional Asset Approval Dashboard.

| Option | Description | Selected |
|--------|-------------|----------|
| Image + Brand Score + top 3 sub-scores | Quick decision | |
| Full score breakdown | All sub-scores + pass/fail per layer | |
| Image + scores + context | Side-by-side reference comparison | ✓ |

**User's choice:** Rich approval dashboard: side-by-side reference and candidate, Brand Score + 7 sub-scores, visual drift warnings, expandable metadata, batch compare mode, rich actions (Approve, Approve & Promote, Needs Refinement, Regenerate Similar, Reject, Compare), review history.

---

## Image Generation Toolchain

Covered within Creation Workflow Automation section. Resolved decisions:
- ComfyUI for R&D, Python/diffusers for production
- GenerationEngine with pluggable model adapters
- Python owns job queue, prompt builder, seed generator, generation, scoring, database, metadata, versioning, and exports

---

## Deferred Ideas

- Pipeline Infrastructure & Architecture Foundation — moved to after Phase 3 (World Building + Asset Library)
