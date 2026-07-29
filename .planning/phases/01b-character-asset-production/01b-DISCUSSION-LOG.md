# Phase 1b: Character Asset Production — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-29
**Phase:** 1b-Character-Asset-Production
**Areas discussed:** Execution environment & backend, Asset production sequencing, Expression/pose spec alignment, Review cadence & approval workflow

---

## Execution Environment & Backend

| Option | Description | Selected |
|--------|-------------|----------|
| Local GPU (CLI-based) | Run Flux/SDXL locally via Python/diffusers. Full control, no recurring API costs, but requires GPU availability. | |
| Cloud API (fal.ai/Replicate/BFL) | Use CloudAPIBackend with a provider. No GPU needed, pay per generation, faster iteration. | |
| Hybrid: R&D on cloud, batch on local | Experiment with cloud APIs for prompt discovery and workflow tuning. Run batch production locally once prompts are locked. | ✓ |

**User's choice:** Hybrid, refined further. Research on cloud/free tools → Lock prompts → Local production. Phase 1b goes straight to local ComfyUI + Flux. ComfyUI is the heart of the studio. Cloud APIs are optional adapters only, never mandatory dependencies.

**Follow-up: Phase 1b generation method?** Go straight to local ComfyUI.

**Follow-up: Cloud API provider?** Optional adapter-only. Tier 3 optional plugins. Research tools (Tensor.Art, Playground AI, Civitai, HF Spaces) are Tier 2 for prompt discovery. No production assets from research tools.

---

## Asset Production Sequencing

| Option | Description | Selected |
|--------|-------------|----------|
| Sequential: Ref → Expressions → Poses → Outfits | Lock reference sheets first. Most disciplined but slowest. | |
| Ref first, then parallel per type | Lock reference sheets, then generate expressions, poses, and outfits in parallel. | |
| Single pass: all at once per prompt batch | Use GenerationJob's pipeline to generate all variants in one pass. Fastest but less control. | |

**User's choice:** Progressive Locking Pipeline (Option 4 — not originally listed). Each stage locks a deeper layer: Concept Exploration → Identity Lock (multi-angle reference) → Face Lock (expressions) → Body Lock (poses) → Animation Validation (deferred to Phase 4) → Default Outfit Lock → Accessory Library → Wardrobe Expansion → LoRA Training.

**Notes:** Animation studios don't approve category-by-category — they approve the character incrementally. Animation Validation (testing motion before wardrobe) was a key insight — but deferred to Phase 4 in this context.

**Follow-up: Concept exploration approach?** Silhouettes (20-30) → Face Concepts (20-30) → Color Variations (25-50) → Clothing Concepts (20-30) → Top 10/5/3/1 → Winner → Reproduce locally in ComfyUI. Research tools for exploration, never cloud APIs. User emphasized silhouette exploration as crucial for character recognition.

**Follow-up: Animation Validation in Phase 1b?** Deferred to Phase 4.

---

## Expression & Pose Spec Alignment

| Option | Description | Selected |
|--------|-------------|----------|
| PHASE1.md is source of truth | Update code to match PHASE1.md exactly (23 expressions, 20 poses). | |
| Code is source of truth | Code already tested. Update PHASE1.md to match code. | |
| Merge: PHASE1.md base + code additions | Keep PHASE1.md as base list, add code extras (angry, shy, silly, etc.). | ✓ |

**User's choice:** Merged superset — both PHASE1.md and code expressions/poses are valid.

**Follow-up: Scope for Phase 1b?** Merged superset — all expressions and poses from both sources are valid for Lily Bunny. No deferral of extras.

---

## Review Cadence & Approval Workflow

| Option | Description | Selected |
|--------|-------------|----------|
| Batch per asset group | For each expression/pose/outfit, generate candidates → auto-score → diversity filter → top ~10 in batch → pick winner. | |
| Per-asset individual review | Review each candidate individually side-by-side against reference. More thorough but slower. | |

**User's choice:** Multi-Stage Batch Review Pipeline (Option 3 — not originally listed). Batch Generation (50-100) → Automatic quality scoring → Hard-rule elimination → Duplicate removal → Diversity filtering → Human review (top 10-20) → Side-by-side comparison (top 3-5) → Winner lock.

**Notes:** User emphasized that treating DINOv2 as "the quality score" is the biggest mistake. Multi-metric scoring: Identity 35%, Style 20%, Prompt 15%, Technical 15%, Composition 10%, Diversity 5%. Hard-rule failures (anatomy, safety, artifacts) should never reach human review. Asset-type-specific thresholds.

**Follow-up: Score thresholds?** Adaptive thresholds per asset type. Not a single gate. ≥95% auto-pass, 90-95% human review, 80-90% human review if adds diversity, <80% reject unless rescued, <70% auto-reject.

**Follow-up: Review UI enhancement?** Enhance with larger configurable batch grids (3x3, 4x4) for faster batch review.

---

## the agent's Discretion

No areas were deferred to agent discretion — all four areas received explicit user direction.

## Deferred Ideas

- Animation Validation (video clips for motion testing) → Phase 4
- Inspiration Library (collected references of successful children's character designs) → potential pre-work for future characters
