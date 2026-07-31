# TODO — Phase 8–10 Audit Gaps

Audit of PHASE8.md, PHASE9.md, PHASE10.md against the implemented code in
`src/image_generation/`, `src/animation/`, and `src/post_production/`.
Spec-mandated systems that were missing or stubbed are documented below with
the fix that closes each gap.

---

## Phase 8 — AI Image Generation & Visual Asset Pipeline

### Complete
- `src/generation_engine/` — FLUX/SDXL/Pony/ComfyUI/Cloud backends (framework-ready stubs)
- `src/pipeline/generation_job.py` — batch generation (50–100 candidates → scoring → diversity → shortlist)
- `src/prompt_builder/` — prompt composition engine (Subject+Character+Action+Environment+Camera+Lighting+Mood+Style+Rendering+Quality)
- `src/image_generation/` — metadata, validator, upscaler, thumbnail, reference manager, prompt versioning
- `src/identity_engine/` — character consistency scoring
- `ImageGeneration/` storage structure (Characters, Expressions, Poses, Environments, Assets, Scenes, Storyboards, References, PromptTemplates, NegativePrompts, LoRAs, Embeddings, Outputs, Metadata)
- IMAGE_GENERATION_GUIDE.md documentation

### Gaps Fixed

| # | Gap | Priority | Type | Fix |
|---|-----|----------|------|-----|
| 1 | Character Locking system missing (reference images, identity LoRA, face consistency, embeddings, approved palette, approved costume set) | HIGH | Code | `src/image_generation/consistency.py` — `CharacterLock` + `ConsistencyManager` |
| 2 | Environment Locking system missing (master image, layout map, lighting presets, weather presets, palette, camera references, object placement rules) | HIGH | Code | `src/image_generation/consistency.py` — `EnvironmentProfile` |
| 3 | Style Locking / style guide enforcement missing (soft lighting, rounded geometry, friendly proportions, pastels, low noise, readable shapes, clean backgrounds) | HIGH | Code | `src/image_generation/consistency.py` — `StyleGuide` |
| 4 | Model Responsibilities table (FLUX / SDXL / Pony) not enforced — no model role lookup | MED | Code | `src/image_generation/model_roles.py` — `ModelRoleManager` |

---

## Phase 9 — AI Animation Pipeline & Motion Generation System

### Complete
- `src/animation/` — planning, motion (21 categories), facial (11 expressions), lip sync, camera (10 motions), physics (5 materials), particles (10 effects), transitions (7 types), lighting (11 conditions), render queue/pipeline, validator, monitoring
- `Animation/` storage structure + ANIMATION_PIPELINE_GUIDE.md

### Gaps Fixed

| # | Gap | Priority | Type | Fix |
|---|-----|----------|------|-----|
| 5 | Eye Animation missing (blink frequency, eye tracking, focus target, reading movement, look-at-speaker/object) | HIGH | Code | `src/animation/character.py` — `EyeAnimationEngine` |
| 6 | Body Animation missing (weight shifts, breathing, secondary motion, arm swing, foot placement, head movement) | HIGH | Code | `src/animation/character.py` — `BodyAnimationEngine` |
| 7 | Secondary Motion missing (hair, bows, clothing, scarves, tails, backpacks, balloons, leaves, grass) | HIGH | Code | `src/animation/character.py` — `SecondaryMotionEngine` |
| 8 | Character Animation Engine (core engine) missing | HIGH | Code | `src/animation/character.py` — `CharacterAnimationEngine` facade |
| 9 | Crowd Engine missing (walk, talk silently, play, wave, read, sit, run, dance; must stay subtle) | HIGH | Code | `src/animation/crowd.py` — `CrowdEngine` |
| 10 | Scene Composition Engine + Scene Rendering pipeline missing (raw → interpolation → enhancement → artifact cleanup → final clip → metadata) | MED | Code | `src/animation/composition.py` — `SceneCompositionEngine` |
| 11 | Regeneration Strategy missing (regenerate only affected clip, never the whole episode) | HIGH | Code | `src/animation/regeneration.py` — `RegenerationEngine` |

---

## Phase 10 — Post-Production, Video Editing & Mastering System

### Complete
- `src/post_production/` — timeline engine, editing/pacing, transitions (9 styles), audio sync, subtitles (SRT/VTT, word timings), graphics (11 templates), intro/outro, thumbnail selection, export presets (8 platforms), QC, archive, localization
- `PostProduction/` storage structure + POST_PRODUCTION_GUIDE.md

### Gaps Fixed

| # | Gap | Priority | Type | Fix |
|---|-----|----------|------|-----|
| 12 | Interactive Elements missing (Can you count?, Pause…, Great job!, Let's clap!, Find the bunny!, Repeat after me!, countdowns) | HIGH | Code | `src/post_production/editing.py` — `InteractiveElementEngine` |
| 13 | `EditingEngine.insert_pause` was an empty stub (`pass`) | HIGH | Code | `src/post_production/editing.py` — implemented gap/event insertion |
| 14 | Color Correction missing (brightness, contrast, saturation, white balance, gamma, exposure) | HIGH | Code | `src/post_production/color.py` — `ColorCorrectionEngine` |
| 15 | Visual Enhancement missing (sharpening, noise reduction, frame interpolation, artifact cleanup, edge refinement) | HIGH | Code | `src/post_production/enhancement.py` — `EnhancementEngine` |
| 16 | Accessibility safe-flashing-limits check missing | MED | Code | `src/post_production/qc.py` — `validate_accessibility` |
| 17 | Analytics Metadata missing (duration breakdown, question count, subtitle count, render time, export size, compression ratio, QC score) | HIGH | Code | `src/post_production/analytics.py` — `PostProductionAnalytics` |
| 18 | Sound Mixing priority omitted Singing and Learning Sounds tracks | MED | Code | `models.py` `AudioTrackType` + `audio_sync.py` priority/levels |
| 19 | Default intro total (14.5 s) exceeded the spec's 5–10 s standard | MED | Code | `intro_outro.py` — defaults reduced to 10.0 s + `is_within_standard()` |

### Notes
- GPU/vision-dependent validation (no missing limbs, no extra fingers, no text,
  correct-character checks) remains a framework stub requiring a vision model,
  consistent with the other GPU-blocked backends.
- "Suggested APIs" in each phase are integration suggestions exposed to the
  automation layer and are covered by Phase 12 orchestration.
