# Phase 1b: Character Asset Production — Context

**Gathered:** 2026-07-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Activate the character factory to produce Lily Bunny's complete visual asset library. This is the first production run of the infrastructure built in Phase 1 — generating real images, not building more infrastructure. Provider-agnostic image generation through local ComfyUI + Flux as the primary production path, with SDXL as secondary.

**Scope:** Lily Bunny only. Reference sheets, expression library, pose library, outfit/wardrobe variants, rotation sheets, accessory library. Human review through the existing Review UI (enhanced with larger batch grids). All assets scored through Phase 1's identity engine and diversity filter before human review.

**Out of scope:** Video generation, animation validation (Phase 4), LoRA training (Phase 1c), other characters (future), background/environment generation (Phase 2).

**Roster (Phase 1b — Lily Bunny only):** 1 character, full completion before any other character begins.
</domain>

<decisions>
## Implementation Decisions

### Execution Environment & Backend Selection
- **D-01:** Hybrid architecture: research on free/cloud tools → lock prompts → local production. Phase 1b goes straight to local ComfyUI + Flux as the primary production path. SDXL as secondary. — **Reversibility:** reversible — ComfyUI workflows are files, can be swapped
- **D-02:** ComfyUI is the heart of the studio. All production generation runs through ComfyUI workflows. Python/diffusers adapters from Phase 1 remain supported but ComfyUI is primary for Phase 1b. — **Reversibility:** costly — migrating ComfyUI workflows to diffusers code later would require re-implementation
- **D-03:** Cloud APIs (fal.ai, Replicate, Black Forest Labs API) are optional adapters only — never mandatory dependencies. They remain as Tier 3 optional plugins in the Generation Engine architecture. — **Reversibility:** reversible
- **D-04:** Research tools (Tensor.Art, Playground AI, Civitai, Hugging Face Spaces) are for prompt discovery, style exploration, and concept experimentation only. No production assets come from these tools. — **Reversibility:** reversible

### Asset Production Sequencing (Progressive Locking Pipeline)
- **D-05:** Progressive Locking Pipeline — not sequential per-type. Each stage locks a deeper layer of character identity before the next begins. — **Reversibility:** one-way — assets locked at each stage become dependencies for downstream generation
- **D-06:** Pipeline stages: Concept Exploration (research tools) → Identity Lock (multi-angle reference sheets, ComfyUI+Flux) → Face Lock (expressions) → Body Lock (poses) → Default Outfit Lock → Accessory Library → Wardrobe Expansion (seasonal/occupation) → LoRA Dataset → LoRA Training (Phase 1c). — **Reversibility:** reversible — stages can be reordered per character
- **D-07:** Concept exploration phase uses research tools (Tensor.Art, Playground AI, Civitai, HF Spaces) not local ComfyUI. Sequence: Silhouettes (20-30) → Face Concepts (20-30) → Color Variations (25-50) → Clothing Concepts (20-30) → Top 10 → Top 5 → Top 3 → Winner → Reproduce locally in ComfyUI. — **Reversibility:** reversible
- **D-08:** Animation Validation (testing short image-to-video clips before wardrobe production) is deferred to Phase 4 (Visual Generation Pipeline). Phase 1b does not include video testing. — **Reversibility:** costly — design flaws discovered in Phase 4 may require regenerating wardrobe assets from Phase 1b

### Expression & Pose Spec Alignment
- **D-09:** Source of truth is merged superset: PHASE1.md base list + code additions. Both sources are valid. — **Reversibility:** reversible
- **D-10:** Phase 1b generates ALL expressions and poses from the merged superset — both PHASE1.md expressions and the code's additional expressions are valid for Lily Bunny. No deferral of extras. — **Reversibility:** reversible — expressions are individual assets, can be added/removed later
- **D-11:** Code's `_known_expressions()` and `_known_poses()` will be updated to include PHASE1.md expressions (blowing_kiss, winking, very_happy, giggling, whistling, etc.) plus retain code extras (angry, shy, silly, sneezing, coughing, sighing, etc.). — **Reversibility:** reversible

### Review Cadence & Approval Workflow (Multi-Stage Studio Pipeline)
- **D-12:** Multi-stage batch review pipeline, not per-image review. Stages: Batch Generation (50-100) → Hard-rule elimination (anatomy, safety, defects) → Automatic multi-metric quality scoring → Duplicate removal → Diversity filtering → Human review batch (top ~10-20) → Side-by-side comparison (top 3-5) → Winner lock. — **Reversibility:** reversible — pipeline configuration can be tuned per asset type
- **D-13:** DINOv2 is one component of scoring, not the sole decision-maker. Multi-metric scoring: Identity Consistency 35% (DINOv2), Style Consistency 20%, Prompt Adherence 15%, Technical Quality 15%, Composition 10%, Diversity 5%. — **Reversibility:** costly — scoring weights become embedded in score interpretation across the pipeline
- **D-14:** Adaptive per-asset-type thresholds — not a single fixed score gate:
  - Reference sheets: 97-99% identity similarity
  - Expressions: 92-97%
  - Dynamic poses: 88-95%
  - Outfits (winter/costumes): 80-92%
  - Hard failures (anatomy, safety, artifacts): auto-reject regardless of score
  - **Reversibility:** reversible — thresholds are configuration values
- **D-15:** Approval zones by identity similarity: ≥95% auto-pass to final review, 90-95% normal human review, 80-90% human review only if adds diversity, <80% reject unless manually rescued, <70% auto-reject. — **Reversibility:** reversible
- **D-16:** Review UI should be enhanced with larger configurable batch grids (3x3, 4x4) to support faster batch review of 10-20 candidates at once. — **Reversibility:** reversible — UI layout change
- **D-17:** Asset approval state machine: Generated → Filtered → Candidate → Reviewed → Approved → Production → Archived. Rejected assets retained for future reference (not deleted). — **Reversibility:** reversible — state machine is configuration
- **D-18:** Each approved asset retains lineage metadata (generation batch, candidate pool, version history, episodes using this asset). — **Reversibility:** one-way — lineage schema becomes a storage contract

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Foundation
- `.planning/phases/01-character-universe/01-CONTEXT.md` — Phase 1 decisions (D-01 through D-19): character roster, creation workflow, identity scoring, generation engine, asset storage, review UI, LoRA strategy, toolchain
- `PHASE1.md` — Original character universe vision: expression list (23), pose list (20), outfit list, design rules, color palette, naming conventions, image generation workflow, quality checklist

### Project Context
- `.planning/PROJECT.md` — Studio mission, core value, key decisions
- `.planning/REQUIREMENTS.md` — Full requirements traceability (CHAR-02 through CHAR-05 for Phase 1b)
- `.planning/ROADMAP.md` — Phase 1b goal, success criteria, dependencies

### Existing Code Architecture
- `src/generation_engine/` — GenerationBackend ABC + 5 adapters (Flux, SDXL, Pony, CloudAPI, ComfyUI)
- `src/identity_engine/` — IdentityScorer, BrandScore, 7 plugins (DINOv2, CLIP, Color, Part, Pose, Expression, Style)
- `src/pipeline/` — JobQueue, GenerationJob orchestrator, DiversityFilter
- `src/prompt_builder/` — PromptBuilder, PromptTemplates, negative prompt composer
- `src/asset_repository/` — SQLiteAssetRepository, AssetRepository ABC
- `src/review_ui/` — FastAPI + Jinja2 review UI (side-by-side, batch compare)
- `src/models/schemas.py` — CharacterModel, AssetModel, GenerationJobRequest, ScoringResult

### Universe Content (Lily Bunny)
- `Universe/Characters/Lily Bunny/bio.md` — Complete 119-line character specification
- `Universe/Characters/Lily Bunny/prompts/templates.json` — 7 template types with age descriptors
- `Universe/PromptTemplates/lily-bunny-prompt-sheet.md` — Full prompt reference (202 lines)
- `Universe/ColorPalette/brand-palette.json` — 5 primary + 5 pastel hex colors
- `Universe/StyleGuide/character-design-rules.md` — 24 expressions, 20 poses, 6 rotation angles, design standards
- `Universe/NegativePrompt/standards.md` — Common + per-character negative prompt standards
- `Universe/PromptTemplates/README.md` — Variable reference and usage docs
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- **Generation Engine** with 5 backends (FluxBackend, SDXLBackend, PonyBackend, CloudAPIBackend, ComfyUIBackend) — fully implemented ABC with lazy model loading and graceful degradation. Ready for Phase 1b image generation.
- **Identity Scoring Pipeline** (IdentityScorer, BrandScore, 7 plugins) — weighted composite scoring with DiversityFilter for clustering. Ready for auto-curation of generated candidates.
- **Prompt Builder** (PromptBuilder, PromptTemplates, negative composer) — 7 template types (reference, expression, pose, outfit, rotation, age_variant, lighting). Supports composition: age modifier + base + lighting/rotation.
- **Asset Repository** (SQLiteAssetRepository) — Full CRUD with D-15 lifecycle enforcement, schema migrations, async interfaces.
- **Review UI** — FastAPI + Jinja2 with side-by-side reference comparison, batch 2x2, Brand Score + sub-scores. Dashboard with pending counts, character detail, review actions (approve/reject/regenerate/promote). Action handlers are stubs — need wiring to real repository.
- **Job Queue** (JobQueue, GenerationJob, DiversityFilter) — async pipeline orchestrator ready for batch generation runs.
- **Test Infrastructure** (MockBackend, in-memory repos, sample data) — 156 passing tests.

### Established Patterns
- ABC + Plugin/Adapter pattern — every subsystem uses abstract base with concrete implementations
- Lazy-loading for ML models — `_ensure_model()` patterns, graceful ImportError handling, never crash
- Registry pattern — BACKENDS dict, ALL_PLUGINS list for auto-discovery
- State machines — Asset lifecycle (draft→generated→scored→shortlisted→approved→production→archived), Job lifecycle (pending→running→completed/failed)
- Dependency injection — create_app() accepts optional repos, IdentityScorer accepts optional plugins
- Provider abstraction — app never knows which model generated an image
- Graceful degradation — all plugins return fallback scores when models unavailable

### Integration Points
- **GenerationJob** orchestrates: GenerationBackend → IdentityScorer → DiversityFilter → AssetRepository. This is the main pipeline for Phase 1b batch generation.
- **PromptBuilder** inputs: character name + asset type (expression/pose/outfit/rotation) + optional age/lighting modifier → outputs (positive prompt, negative prompt).
- **Review UI** connects to AssetRepository + CharacterRepository for data. Currently uses _StubAssetRepo — needs to be wired to SQLiteAssetRepository for real data.
- **Universe directory** contains empty asset subdirectories ready to receive approved images (references/, expressions/, poses/, outfits/, turnarounds/, accessories/).

### Code-Spec Gaps to Resolve
- `PromptBuilder._known_expressions()` and `_known_poses()` need updating to match the merged PHASE1.md + code superset
- `ColorVerificationPlugin.DEFAULT_BRAND_PALETTE` is hardcoded — should load from `Universe/ColorPalette/brand-palette.json`
- Review UI action handlers (/approve, /reject, /regenerate, /promote) are stubs returning RedirectResponse without calling repo.update_state()
</code_context>

<specifics>
## Specific Ideas
- "Think like Pixar" — build a permanent character universe, not individual videos
- Cocomelon-inspired visual style (colorful, rounded shapes, oversized eyes, soft lighting, vibrant colors, high saturation, child-friendly)
- Provider independence — never depend on a single AI model or company; every generation request flows through the Generation Engine abstraction
- "ComfyUI is the heart of the studio" — all production ComfyUI workflows, not Python/diffusers code
- "Research should be fast, production should be repeatable, costs should stay close to zero, everything should eventually run locally"
- "Your time is far more valuable than manually rejecting obviously bad generations" — automate filtering, keep human review for the top ~10-20 candidates
- Never delete rejected assets immediately — retain for future reference or model evaluation
- Multi-metric scoring (DINOv2 is one component, not the decision-maker)
</specifics>

<deferred>
## Deferred Ideas
- Animation Validation (image-to-video clips) — deferred to Phase 4 (Visual Generation Pipeline)
- Inspiration Library (collected references of successful children's character designs) — potential pre-work for future characters
</deferred>

---

*Phase: 1b-Character-Asset-Production*
*Context gathered: 2026-07-29*
