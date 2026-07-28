# Phase 1: Character Universe & Bible — Context

**Gathered:** 2026-07-28
**Status:** Ready for planning

**Important:** This phase was rephrased from the ROADMAP.md original. ROADMAP.md had Phase 1 as "Pipeline Infrastructure & Architecture Foundation" — the user explicitly chose to build Character Universe first, followed by World (Phase 2), Assets (Phase 3), then Infrastructure. The ROADMAP needs updating to reflect this reordering.

<domain>
## Phase Boundary

Create 20 reusable characters with complete documentation — the permanent character IP library for the studio. Every character gets reference sheets, expression library, pose library, outfit variants, model sheets, and prompt templates. LoRA training for each character. No songs, no videos, no animation — character assets only.

**Roster:** 4 mains (Lily, Ben, Daisy, Charlie) + 5 family (Mom, Dad, Grandma, Grandpa, Baby) + 5 friends (Cat, Dog, Elephant, Monkey, Cow) + 3 community (Teacher, Doctor, Firefighter) + 3 fantasy (Dragon, Unicorn, Dinosaur) = 20 total. One-by-one full completion, Lily Bunny first.
</domain>

<decisions>
## Implementation Decisions

### Character Roster & Production Order
- **D-01:** 20 characters across 5 categories (4 mains, 5 family, 5 friends, 3 community, 3 fantasy). — **Reversibility:** reversible
- **D-02:** One-by-one full completion. Finish Lily entirely before starting Ben. — **Reversibility:** reversible
- **D-03:** Lily Bunny is the first character. Sets the visual standard for all others. — **Reversibility:** reversible

### Creation Workflow
- **D-04:** Hybrid pipeline: Generate 50–100 candidates → Technical auto-scoring (CLIP, aesthetics, DINOv2) → Diversity filter (cluster similar images) → Human review (5–15 finalists) → Lock winner. — **Reversibility:** reversible
- **D-05:** Custom Brand Score system: weighted composite (Prompt accuracy 20%, Character consistency 20%, Technical quality 15%, Facial appeal 15%, Child friendliness 10%, Color harmony 10%, Silhouette recognizability 5%, Style consistency 5%). — **Reversibility:** reversible
- **D-06:** 7-layer identity scoring pipeline: DINOv2 (40%) + CLIP (20%) + Color Verification (10%) + Part Verification (10%) + Pose Verification (5%) + Expression Verification (5%) + Style Verification (10%). — **Reversibility:** costly — sub-scores become dependencies for downstream scoring consumers
- **D-07:** Identity scoring implemented as plugin-based Python package (`identity_engine/`). Importable as `from identity import IdentityScorer`. Core engine → Python SDK → REST API (future). — **Reversibility:** one-way — the plugin API becomes a published contract
- **D-08:** ComfyUI for R&D/lab (prompt discovery, workflow design, model testing). Python/diffusers for production factory. Never confuse the two roles. — **Reversibility:** reversible
- **D-09:** Generation Engine with pluggable model adapters (FluxBackend, SDXLBackend, PonyBackend). Full adapter architecture from day one. — **Reversibility:** one-way — adapter interfaces become a published contract

### LoRA Strategy
- **D-10:** "Train Early, Retrain Once" lifecycle. Stage A: Lock identity → 20–40 curated references → train Production LoRA v1.0. Stage B: After hundreds of approved assets → retrain Master LoRA v2.0 (benchmarked against v1.0 before promotion). — **Reversibility:** reversible — LoRAs are files, can be retrained anytime
- **D-11:** LoRAs versioned like software releases (v0.1 → v0.5 → v1.0 → v1.5 → v2.0). — **Reversibility:** reversible

### Asset Storage
- **D-12:** 3-layer storage: Pipeline Workspace (temp/job-based) → SQLite Catalog (metadata) → Universe Library (PHASE1.md folder structure, approved-only). — **Reversibility:** one-way — the SQLite schema becomes a data contract
- **D-13:** SQLite for metadata: characters, assets, jobs, prompts, models, LoRAs, scores, versions, training runs. Filesystem for binary assets only. — **Reversibility:** costly — migrating to PostgreSQL later is planned
- **D-14:** Repository pattern (`AssetRepository` interface with SQLite implementation) for future PostgreSQL migration. — **Reversibility:** one-way — repository interface is a published contract
- **D-15:** Asset lifecycle states: Draft → Generated → Scored → Shortlisted → Approved → Production → Archived. — **Reversibility:** reversible
- **D-16:** Only approved assets enter the permanent Universe Library. Rejected assets stay in job workspace. — **Reversibility:** reversible

### Design Approval
- **D-17:** Simple web UI for human review. Side-by-side reference sheet and candidate comparison. Brand Score + all 7 sub-scores. Visual drift warnings. Expandable generation metadata. Batch compare mode. Actions: Approve, Approve & Promote, Needs Refinement, Regenerate Similar, Reject, Compare. Review history and audit trail. — **Reversibility:** reversible

### LoRA Training
- **D-18:** Training Engine abstraction with adapter pattern. Phase 1: Kohya SS adapter behind the interface. Training lifecycle with versioned datasets and identity-score benchmarking. — **Reversibility:** one-way — training adapter interface becomes a published contract

### Generation Toolchain
- **D-19:** Python/diffusers for batch production via Generation Engine. ComfyUI for R&D. Python owns job queue, prompt builder, seed generator, generation, scoring, database, metadata, versioning, and exports. — **Reversibility:** costly — migrating from direct diffusers to model adapters later would be disruptive
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Character Universe Vision
- `PHASE1.md` — Original vision document for character universe creation (contains character design rules, expression list, pose list, outfit list, workflow steps, file structure, prompt templates)

### Project Context
- `.planning/PROJECT.md` — Studio mission, core value (character consistency and reusability), key decisions
- `.planning/REQUIREMENTS.md` — Full requirements traceability (INFR-01 through INFR-05 for original Phase 1, CHAR-01 through CHAR-09 relevant for this rephased Phase 1)
- `.planning/ROADMAP.md` — Current roadmap (needs updating to reflect rephasing)
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — this is a greenfield project with zero source code. Everything in this phase is being built from scratch.

### Established Patterns
- None — no existing codebase patterns to follow. This phase establishes the patterns that all downstream phases will follow.

### Integration Points
- No existing system to integrate with. This phase creates the foundational architecture (Generation Engine, Identity Engine, Asset Storage) that later phases will use.

**Key architectural note:** Since this is the first phase of a greenfield project, the decisions made here become the patterns that all downstream phases must follow. The adapter/wrapper patterns (GenerationEngine, IdentityScorer, AssetRepository) are designed specifically to prevent lock-in and enable model/backend swapping.
</code_context>

<specifics>
## Specific Ideas
- "Think like Pixar" — build a permanent character universe, not individual videos
- Cocomelon-inspired visual style (colorful, rounded shapes, oversized eyes, soft lighting, vibrant colors, high saturation, Pixar-quality rendering)
- Character design rules from PHASE1.md: large head, large bright eyes, small rounded nose, simple friendly mouth, soft body proportions, oversized rounded feet
- Color palette restrictions: primary (Blue, Yellow, Pink, Green, Orange) + pastel variants. Avoid dark and neon colors.
- Never mix styles; consistency builds a recognizable brand
</specifics>

<deferred>
## Deferred Ideas
- Pipeline Infrastructure & Architecture Foundation — moved to after Phase 3 (World & Assets)
- Pipeline runtime, checkpoint/resume, model routing, configurable stage interfaces — all deferred to the Infrastructure phase
</deferred>

---

*Phase: 1-Character-Universe*
*Context gathered: 2026-07-28*
