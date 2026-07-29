---
phase: 01b-character-asset-production
plan: 05
type: execute
wave: 3
depends_on:
  - 01b-04
files_modified:
  - Universe/Characters/Lily Bunny/poses/
  - Universe/Characters/Lily Bunny/outfits/
  - scripts/generate_body_lock.py
  - scripts/generate_wardrobe.py
autonomous: false
requirements:
  - CHAR-04
  - CHAR-05
user_setup:
  - service: ComfyUI
    why: "All image generation runs through local ComfyUI + Flux"
    env_vars: []
    dashboard_config:
      - task: "Verify ComfyUI is still running at http://localhost:8188"
      - task: "Verify Review UI is running at http://localhost:8000"
must_haves:
  truths:
    - Lily Bunny pose library (20 poses from merged list) exists in Universe/Characters/Lily Bunny/poses/ with state="production"
    - Lily Bunny outfit/wardrobe variants (12+ from bio) exist in Universe/Characters/Lily Bunny/outfits/ with state="production"
    - Each approved asset has lineage metadata (generation_batch, candidate_pool, reference_asset_id pointing to front reference)
    - All assets passed multi-stage pipeline: generation → scoring → diversity filtering → human review → winner lock
    - Approved poses have identity similarity ≥ 0.88 (D-14 dynamic pose threshold)
    - Approved outfits have identity similarity ≥ 0.80 (D-14 outfit threshold)
    - Each stage locks a deeper layer of character identity per D-05 (Progressive Locking Pipeline)
    - Animation Validation (image-to-video testing) is deferred to Phase 4 per D-08 — Phase 1b does not include video testing
    - Scoring uses multi-metric weights per D-13: Identity Consistency 35%, Style Consistency 20%, Prompt Adherence 15%, Technical Quality 15%, Composition 10%, Diversity 5%
  artifacts:
    - Universe/Characters/Lily Bunny/poses/ (20+ pose images)
    - Universe/Characters/Lily Bunny/outfits/ (12+ outfit images)
    - scripts/generate_body_lock.py (orchestration script for pose generation)
    - scripts/generate_wardrobe.py (orchestration script for outfit generation)
  key_links:
    - Poses use the approved front reference sheet (from Identity Lock) as identity scoring reference
    - Outfits use the approved front reference sheet as identity scoring reference AND specify clothing variant in the prompt
    - Body Lock depends on Face Lock expressions completing first (progressive pipeline per D-06)
---

<objective>
Execute stages 3 and 4 of the Progressive Locking Pipeline (D-05, D-06) for Lily Bunny: Body Lock (20 poses) and Wardrobe Expansion (12+ outfit variants). This completes the character asset production run, all using ComfyUI + Flux as the primary production path per D-01 (SDXL secondary). Each stage locks a deeper layer of character identity per D-05.

Purpose: Generate and approve Lily Bunny's complete pose and outfit libraries, passing through the full generation → scoring → diversity filtering → human review → winner lock pipeline.
Output: Approved pose and outfit images in the Universe Library, completing Phase 1b asset production.
</objective>

<execution_context>
@/root/.config/opencode/gsd-core/workflows/execute-plan.md
@/root/.config/opencode/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/01b-character-asset-production/01b-CONTEXT.md
@.planning/phases/01b-character-asset-production/01b-RESEARCH.md

# Previous plan summaries (dependencies)
@.planning/phases/01b-character-asset-production/01b-01-SUMMARY.md
@.planning/phases/01b-character-asset-production/01b-02-SUMMARY.md
@.planning/phases/01b-character-asset-production/01b-03-SUMMARY.md
@.planning/phases/01b-character-asset-production/01b-04-SUMMARY.md

# Source files
@scripts/generate_body_lock.py
@scripts/generate_wardrobe.py
@src/pipeline/generation_job.py
@src/pipeline/diversity_filter.py
@src/generation_engine/comfy_backend.py
@src/prompt_builder/builder.py
@src/identity_engine/scorer.py
@src/asset_repository/sqlite_repo.py
@Universe/Characters/Lily Bunny/bio.md
@.planning/phases/01b-character-asset-production/01b-RESEARCH.md (CHAR-04: pose details, CHAR-05: outfit details)
</context>

<tasks>

<task type="auto">
  <name>Create pose generation orchestration script and run Body Lock stage</name>
  <files>
    scripts/generate_body_lock.py,
    Universe/Characters/Lily Bunny/poses/
  </files>
  <read_first>
    @scripts/generate_identity_lock.py (pattern to follow — same orchestration structure),
    @scripts/generate_face_lock.py (pattern — expression batch approach),
    @src/prompt_builder/builder.py (updated _known_poses() from Plan 01b-01),
    @src/pipeline/generation_job.py,
    @src/generation_engine/comfy_backend.py,
    @.planning/phases/01b-character-asset-production/01b-CONTEXT.md (D-06 Body Lock stage, D-14 pose threshold: 88-95%),
    @PHASE1.md (lines 576-618 — pose list reference)
  </read_first>
  <action>
    **Precondition checks:**
    1. ComfyUI reachable at http://localhost:8188
    2. Identity Lock reference sheets approved and in Universe/Characters/Lily Bunny/references/
    3. Face Lock (expressions) approved — this is a sequential dependency in the progressive pipeline
    
    **Step 1: Create `scripts/generate_body_lock.py`**
    
    Same orchestration pattern as generate_face_lock.py, adapted for poses:
    
    1. Initialize pipeline components (ComfyUIBackend, PromptBuilder, IdentityScorer, SQLiteAssetRepository, DiversityFilter, GenerationJob)
    
    2. Load approved front reference sheet as scoring reference (same pattern as expression generation)
    
    3. Get the merged pose list from `PromptBuilder._known_poses()` at runtime:
       - After Plan 01b-01, this returns 28 poses
       - PHASE1.md base: standing, walking, running, jumping, skipping, sitting, kneeling, dancing, sleeping, reading, writing, pointing, clapping, waving, hugging, holding_hands, playing, swimming, flying, sliding (20)
       - Code extras: hopping, eating, drinking, drawing, crawling, hiding, stretching, bouncing (8)
    
    4. For each pose:
       - Generate 50-80 candidates via ComfyUIBackend with asset_type="pose" (uses 768x1344 dimensions for full-body)
        - Score with IdentityScorer using multi-metric scoring per D-13 (Identity Consistency 35%, Style Consistency 20%, Prompt Adherence 15%, Technical Quality 15%, Composition 10%, Diversity 5%) with the front reference as identity reference
        - DiversityFilter top 10-15
       - Shortlisted assets saved with:
         - lineage = {"generation_batch": batch_id, "candidate_pool": count,
                       "reference_asset_id": front_ref.id, "asset_type": "pose"}
    
    5. Sequential processing (one pose at a time, ComfyUI is single-threaded)
    
    6. Progress logging after each pose
    
    7. Estimated generation time: 28 poses × 60 images × ~8s = ~3.7 hours
    
    **Step 2: Execute the script**
    
    Run `python scripts/generate_body_lock.py`
    
    **Step 3: Human review checkpoint**
    
    - Open Review UI at http://localhost:8000/review/{lily-bunny-id}?asset_type=pose&batch=true&grid=4x4
    - D-14 threshold for dynamic poses: 88-95% identity similarity
    - Select winners: Approve (shortlisted → approved) or promote (shortlisted → approved → production)
    - For poses that had no acceptable candidates: tag for regeneration with adjusted prompt
    
    **Step 4: Approved assets**
    - Winners stored to Universe/Characters/Lily Bunny/poses/{pose_name}.png
  </action>
  <verify>
    <automated>python -c "from scripts.generate_body_lock import *" 2>&1 | head -5 || echo "Script exists, import test"</automated>
    <automated>ls Universe/Characters/Lily\ Bunny/poses/ 2>&1</automated>
    <human-check>Open Review UI. Verify pose candidates. Approve best pose for each variant. Verify state transitions.</human-check>
  </verify>
  <done>
    - scripts/generate_body_lock.py exists and is runnable
    - All 20+ poses from merged list generated with 50-80 candidates each
    - Human review completed for all poses
    - Approved pose images in Universe/Characters/Lily Bunny/poses/
    - Each approved asset has state="production" and lineage populated
  </done>
  <acceptance_criteria>
    - Approved pose images in Universe/Characters/Lily Bunny/poses/ (one per approved pose)
    - Each with AssetModel.state == "production" and lineage.reference_asset_id set
    - Identity scores ≥ 0.88 for all approved poses
    - Human confirmed body proportions and pose accuracy for every variant
  </acceptance_criteria>
  <reversibility rating="costly">Pose library depends on reference sheets for identity scoring. Outfit generation in the next task depends on pose library for body understanding.</reversibility>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Checkpoint: Verify pose winners</name>
  <what-built>All 20+ pose generation candidates for Lily Bunny. Each pose has 10-15 shortlisted candidates scored by IdentityScorer and selected by DiversityFilter.</what-built>
  <how-to-verify>
    1. Open Review UI at http://localhost:8000
    2. Navigate to Lily Bunny → Review poses (batch mode, 4x4 grid)
    3. For each pose variant (20+ total):
       - Compare candidates against the front reference sheet (left panel)
       - Evaluate: body proportions correct, character recognizable, pose distinguishable
       - Select best candidate via "Approve & Promote"
    4. Verify approved poses show in character detail
  </how-to-verify>
  <resume-signal>Type "poses approved" to confirm all pose winners are locked, or describe issues found.</resume-signal>
</task>

<task type="auto">
  <name>Create outfit generation orchestration script and run Wardrobe Expansion stage</name>
  <files>
    scripts/generate_wardrobe.py,
    Universe/Characters/Lily Bunny/outfits/
  </files>
  <read_first>
    @scripts/generate_body_lock.py (pattern),
    @Universe/Characters/Lily Bunny/bio.md (outfit list from character bio),
    @src/prompt_builder/builder.py (outfit prompt generation),
    @src/prompt_builder/templates.py (outfit() template method),
    @.planning/phases/01b-character-asset-production/01b-CONTEXT.md (D-06 Wardrobe Expansion stage, D-14 outfit threshold: 80-92%),
    @PHASE1.md (lines 666-706 — clothing library reference)
  </read_first>
  <action>
    **Precondition checks:**
    1. ComfyUI reachable at localhost:8188
    2. Identity Lock reference sheets approved (for identity scoring reference)
    3. Body Lock (poses) completed — outfits use the approved poses as body reference
    
    **Step 1: Create `scripts/generate_wardrobe.py`**
    
    Same orchestration as generate_body_lock.py but for outfits:
    
    1. Initialize pipeline components
    
    2. Load approved front reference sheet as scoring reference
    
    3. Define outfit variants from Lily Bunny bio.md and PHASE1.md clothing library:
       ```python
       outfits = [
           "pink dress with white lace, blue bow",     # Default (already locked)
           "winter coat with scarf, mittens, boots",    # Winter
           "yellow rain jacket, rain boots, umbrella",  # Rain
           "pajamas with bunny print, slippers",        # Pajamas
           "swimsuit, floaties, beach hat",             # Swimming
           "princess costume, tiara, sparkly dress",    # Princess
           "doctor costume, stethoscope, white coat",   # Doctor
           "firefighter costume, helmet, yellow coat",  # Firefighter
           "astronaut suit, helmet, space backpack",    # Astronaut
           "farmer outfit, overalls, straw hat",        # Farmer
           "chef outfit, apron, chef hat",              # Chef
           "teacher outfit, glasses, cardigan",         # Teacher
           "police officer uniform, hat, badge",        # Police
           "construction vest, hard hat, tools",        # Construction
           "halloween witch costume, hat, broom",       # Halloween
           "christmas dress, santa hat, ornaments",     # Christmas
           "sports uniform, jersey, sneakers",          # Sports
       ]
       ```
       Total: 17 outfit variants (including the default which may already exist)
    
    4. For each outfit:
       - Generate 50-80 candidates via ComfyUIBackend with asset_type="outfit" (768x1344 full-body)
        - Score with IdentityScorer using multi-metric scoring per D-13 (Identity Consistency 35%, Style Consistency 20%, Prompt Adherence 15%, Technical Quality 15%, Composition 10%, Diversity 5%) using front reference for identity — note: outfits have lower identity similarity thresholds per D-14 (80-92%) because clothing changes alter appearance
       - DiversityFilter top 10-15
       - Shortlisted assets saved with:
         - lineage = {"generation_batch": batch_id, "candidate_pool": count,
                       "reference_asset_id": front_ref.id, "asset_type": "outfit"}
       - Note: The PromptBuilder.outfit() template replaces the character's outfit with the variant description, so the prompt explicitly describes the clothing
    
    5. Outfits have the most lenient identity similarity thresholds (D-14: 80-92%) because:
       - Winter coats, costumes, and uniforms significantly change silhouette
       - DINOv2 is sensitive to clothing shape changes
       - Human review is the primary quality gate for outfits
    
    6. Sequential processing (one outfit at a time)
    
    7. Estimated generation time: 17 outfits × 60 images × ~8s = ~2.3 hours
    
    **Step 2: Execute the script**
    
    Run `python scripts/generate_wardrobe.py`
    
    **Step 3: Human review checkpoint**
    
    - Open Review UI at http://localhost:8000/review/{lily-bunny-id}?asset_type=outfit&batch=true&grid=4x4
    - D-14 threshold: 80-92% for outfits
    - Key evaluation criteria:
      - Does Lily Bunny still look like Lily Bunny despite the outfit change?
      - Is the outfit rendered correctly and recognizable?
      - Is the character's face, fur, and head consistent with reference?
    - Approve winners
    
    **Step 4: Approved assets**
    - Winners stored to Universe/Characters/Lily Bunny/outfits/{outfit_name}.png
  </action>
  <verify>
    <automated>python -c "from scripts.generate_wardrobe import *" 2>&1 | head -5 || echo "Script exists, import test"</automated>
    <automated>ls Universe/Characters/Lily\ Bunny/outfits/ 2>&1</automated>
    <human-check>Open Review UI. Verify outfit candidates. Approve best outfit for each variant. Verify state transitions.</human-check>
  </verify>
  <done>
    - scripts/generate_wardrobe.py exists and is runnable
    - All 12+ outfit variants generated with 50-80 candidates each
    - Human review completed for all outfits
    - Approved outfit images in Universe/Characters/Lily Bunny/outfits/
    - Each approved asset has state="production" and lineage populated
  </done>
  <acceptance_criteria>
    - Approved outfit images in Universe/Characters/Lily Bunny/outfits/ (one per outfit variant)
    - Each with AssetModel.state == "production" and lineage populated
    - Identity scores ≥ 0.80 for all approved outfits (lower threshold per D-14)
    - Human confirmed outfit accuracy and character consistency for every variant
  </acceptance_criteria>
  <reversibility rating="reversible">Outfits are the final stage in the progressive pipeline. They depend on all previous stages but can be regenerated independently as long as reference sheets remain locked.</reversibility>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Checkpoint: Verify outfit winners</name>
  <what-built>All 12+ outfit/wardrobe generation candidates for Lily Bunny. Each outfit has 10-15 shortlisted candidates scored by IdentityScorer and selected by DiversityFilter.</what-built>
  <how-to-verify>
    1. Open Review UI at http://localhost:8000
    2. Navigate to Lily Bunny → Review outfits (batch mode, 4x4 grid)
    3. For each outfit variant (12+ total):
       - Compare candidates against the front reference sheet
       - Key checks: Is Lily still recognizable? Is the outfit accurate? Is it child-friendly Cocomelon style?
       - Approval zones per D-15:
         - ≥95% identity similarity → auto-pass
         - 80-95% → normal human review
         - 70-80% → review only if adds diversity
         - <70% → reject
       - Approve best candidates
    4. Verify approved outfits show in character detail
  </how-to-verify>
  <resume-signal>Type "outfits approved" to complete Phase 1b asset production, or describe issues found.</resume-signal>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Pipeline → ComfyUI REST API | HTTP localhost:8188 |
| Pipeline → Filesystem | Generated images written to Universe/Characters/Lily Bunny/poses/ and /outfits/ |
| Pipeline → SQLite | Metadata written to catalog.db |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-01b-14 | Tampering | ComfyUI workflow submission | medium | accept | Same as T-01b-10. Workflows are predefined, ComfyUI is localhost-only. |
| T-01b-15 | Information Disclosure | Generated pose/outfit images on filesystem | low | accept | Character assets for animation production — no sensitive data. |
| T-01b-16 | Spoofing | Identity scoring with lenient outfit thresholds | medium | mitigate | D-14 explicitly lowers outfit threshold to 80-92% (decision, not bug). Human review is the final quality gate. Low identity scores for outfits generate a warning badge in Review UI. |
| T-01b-17 | Denial of Service | Long sequential generation (~6 hours total for this plan) | low | accept | Expected production runtime. Each variant has independent error handling. The scripts log progress and can be resumed. |
| T-01b-SC | Tampering | No new pip package installs | low | accept | All dependencies already available. |
</threat_model>

<verification>
1. ComfyUI is reachable at localhost:8188 before generation starts
2. Approved reference sheets exist before pose/outfit generation (Identity Lock prerequisite)
3. Approved poses exist in Universe/ with state="production"
4. Approved outfits exist in Universe/ with state="production"
5. Each approved asset has populated lineage field
6. Identity scores ≥ 0.88 for poses, ≥ 0.80 for outfits (per D-14 thresholds)
7. All 4 asset types from Phase 1b exist: references, expressions, poses, outfits
</verification>

<success_criteria>
1. 20+ approved pose images in Universe/Characters/Lily Bunny/poses/
2. 12+ approved outfit images in Universe/Characters/Lily Bunny/outfits/
3. All approved assets have state="production" and lineage populated
4. Phase 1b complete: Lily Bunny reference sheets, expressions, poses, and outfits all approved in Universe Library
5. Human review completed for all assets across all 4 stages
</success_criteria>

<output>
Create `.planning/phases/01b-character-asset-production/01b-05-SUMMARY.md` when done.
</output>
