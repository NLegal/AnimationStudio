---
phase: 01b-character-asset-production
plan: 04
type: execute
wave: 2
depends_on:
  - 01b-01
  - 01b-02
  - 01b-03
files_modified:
  - Universe/Characters/Lily Bunny/references/
  - Universe/Characters/Lily Bunny/expressions/
  - scripts/generate_identity_lock.py
  - scripts/generate_face_lock.py
autonomous: false
requirements:
  - CHAR-02
  - CHAR-03
user_setup:
  - service: ComfyUI
    why: "All image generation runs through local ComfyUI + Flux"
    env_vars: []
    dashboard_config:
      - task: "Verify ComfyUI is running at http://localhost:8188"
      - task: "Verify Flux model weights are installed (flux1-dev.safetensors in ComfyUI/models/checkpoints/)"
      - task: "Start Review UI: uvicorn src.review_ui.app:create_app() --port 8000 --reload"
must_haves:
  truths:
    - Lily Bunny multi-angle reference sheets (front, 3/4, profile, back) exist in Universe/Characters/Lily Bunny/references/ with state="production"
    - Lily Bunny expression library (32 expressions from merged list) exists in Universe/Characters/Lily Bunny/expressions/ with state="production"
    - Each approved asset has lineage metadata populated (generation_batch, candidate_pool)
    - All assets passed the D-12 multi-stage pipeline: generation → scoring → diversity filtering → human review → winner lock
    - Approved reference sheets have identity similarity ≥ 95% (D-15 threshold)
    - Approved expressions have identity similarity ≥ 90% (D-15 threshold)
    - Cloud APIs are optional adapters only — never mandatory dependencies per D-03
    - Each stage locks a deeper layer of character identity per D-05 (Progressive Locking Pipeline)
    - Scoring uses multi-metric weights per D-13: Identity Consistency 35%, Style Consistency 20%, Prompt Adherence 15%, Technical Quality 15%, Composition 10%, Diversity 5%
  artifacts:
    - Universe/Characters/Lily Bunny/references/ (front.png, 3_4.png, profile.png, back.png — 4 approved reference sheets)
    - Universe/Characters/Lily Bunny/expressions/ (32 expressions × 1-3 winning images each)
    - scripts/generate_identity_lock.py (orchestration script for reference sheet generation)
    - scripts/generate_face_lock.py (orchestration script for expression generation)
  key_links:
    - Reference sheets establish the identity baseline for all downstream scoring — they define what "Lily Bunny looks like" for DINOv2 similarity comparison
    - Expressions use the approved front reference sheet as the reference image for identity scoring
    - Human review checkpoints are blocking — generation output must be evaluated before proceeding
---

<objective>
Execute the first two stages of the Progressive Locking Pipeline (D-05, D-06) for Lily Bunny: Identity Lock (multi-angle reference sheets) and Face Lock (23 expressions). This is the first production run using ComfyUI + Flux as the primary production path per D-01 (SDXL is secondary). Per D-03, cloud APIs are optional adapters only — never mandatory. Concept exploration (research tools per D-07) was a separate pre-production step; this plan executes local ComfyUI production generation only.

Purpose: Establish Lily Bunny's canonical reference images and complete expression library, passing through the full generation → scoring → diversity filtering → human review → winner lock pipeline.
Output: Approved reference sheets and expression images in the Universe Library with proper lineage metadata.
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

# Previous plans (dependencies)
@.planning/phases/01b-character-asset-production/01b-01-SUMMARY.md
@.planning/phases/01b-character-asset-production/01b-02-SUMMARY.md
@.planning/phases/01b-character-asset-production/01b-03-SUMMARY.md

# Source files
@scripts/generate_identity_lock.py
@scripts/generate_face_lock.py
@src/pipeline/generation_job.py
@src/pipeline/job_queue.py
@src/pipeline/diversity_filter.py
@src/generation_engine/comfy_backend.py
@src/generation_engine/base.py
@src/prompt_builder/builder.py
@src/identity_engine/scorer.py
@src/asset_repository/sqlite_repo.py
@src/models/schemas.py
@Universe/Characters/Lily Bunny/bio.md
@Universe/Characters/Lily Bunny/prompts/templates.json
</context>

<tasks>

<task type="auto">
  <name>Create reference sheet generation orchestration script and run Identity Lock stage</name>
  <files>
    scripts/generate_identity_lock.py,
    Universe/Characters/Lily Bunny/references/
  </files>
  <read_first>
    @src/pipeline/generation_job.py (full — understand GenerationJob.execute()),
    @src/pipeline/job_queue.py (Job, JobQueue),
    @src/generation_engine/comfy_backend.py (ComfyUIBackend, _build_workflow with asset_type),
    @src/prompt_builder/builder.py (PromptBuilder.build(), updated _known_expressions and _known_poses),
    @src/identity_engine/scorer.py (IdentityScorer, MockScorerPlugin),
    @src/asset_repository/sqlite_repo.py (SQLiteAssetRepository),
    @src/models/schemas.py (AssetModel, AssetModel.lineage),
    @Universe/Characters/Lily Bunny/bio.md (character specification),
    @.planning/phases/01b-character-asset-production/01b-CONTEXT.md (D-06 stages, D-12 batch review, D-14 thresholds, D-15 approval zones, D-07: concept exploration uses research tools for discovery only — this plan executes local ComfyUI production generation)
  </read_first>
  <action>
    **Precondition check:** Before running, verify ComfyUI is reachable at http://localhost:8188. Run:
    ```python
    import requests
    try:
        r = requests.get("http://localhost:8188/", timeout=5)
        r.raise_for_status()
    except Exception:
        print("ComfyUI not reachable at localhost:8188. Start ComfyUI first.")
        exit(1)
    ```
    If ComfyUI is not running, guide the user to start it and re-run.

    **Step 1: Create `scripts/generate_identity_lock.py`**
    
    This script orchestrates multi-angle reference sheet generation for Lily Bunny. It:
    
    1. Initializes all pipeline components:
       - ComfyUIBackend(server_url="http://localhost:8188")
       - PromptBuilder()
       - IdentityScorer() (uses MockScorerPlugin if torch unavailable — real scoring requires GPU)
       - SQLiteAssetRepository(db_path="catalog.db")
       - DiversityFilter(n_clusters=5)
       - GenerationJob(backend, prompt_builder, scorer, repo, diversity)
    
    2. Sets up character data from Lily Bunny bio:
       - name="Lily Bunny", species="rabbit"
       - appearance="white fur, pink ears, big blue eyes"
       - outfit="pink dress with white lace, blue bow"
       - style="Pixar-quality, Cocomelon-inspired, bright colorful nursery world"
    
    3. Defines 4 reference angles:
       ```python
       angles = [
           {"name": "front", "angle": "front", "count": 80, "shortlist_size": 10},
           {"name": "3_4", "angle": "3/4", "count": 80, "shortlist_size": 10},
           {"name": "profile", "angle": "profile", "count": 80, "shortlist_size": 10},
           {"name": "back", "angle": "back", "count": 80, "shortlist_size": 10},
       ]
       ```
    
    4. For each angle:
       - Generates N candidates via GenerationJob (uses ComfyUIBackend with asset_type="reference_sheet")
        - Scores with IdentityScorer using multi-metric scoring per D-13 (Identity Consistency 35%, Style Consistency 20%, Prompt Adherence 15%, Technical Quality 15%, Composition 10%, Diversity 5%)
        - Runs DiversityFilter to select top candidates
       - Saves scored assets to SQLiteAssetRepository with:
         - lineage = {"generation_batch": batch_id, "candidate_pool": count, "version_history": [], "asset_type": "reference"}
         - state transitions: draft → generated → scored → shortlisted
    
    5. Prints summary: total generated, scored, shortlisted per angle
    
    6. Starts the Review UI server for human review phase:
       ```python
       import uvicorn
       from src.review_ui.app import create_app
       app = create_app(asset_repo=repo)
       uvicorn.run(app, host="127.0.0.1", port=8000)
       ```
       (Runs in a subprocess or the script prints instructions to start it)
    
    **Step 2: Execute the script**
    
    Run `python scripts/generate_identity_lock.py` to generate the reference sheet candidates.
    
    This will take approximately 80 images × 4 angles × ~10s per image = ~53 minutes of generation time (with Flux on GPU). Each image is generated sequentially through ComfyUI.
    
    **Step 3: Human review checkpoint**
    
    After generation completes, the operator reviews candidates in the Review UI:
    - Navigate to http://localhost:8000/review/{lily-bunny-id}?asset_type=reference&batch=true&grid=4x4
    - Review top 10 candidates per angle
    - Compare side-by-side with approved references (none yet for identity lock — first-generation)
    - Select winner for each angle via Approve & Promote (shortlisted → approved → production)
    - For reference sheets, use D-15 approval zones: ≥95% identity similarity recommended
    
    **Step 4: Approved assets**
    - Approved assets with state="production" are considered "Identity Locked"
    - The file_path stores the location in Universe/Characters/Lily Bunny/references/{angle}.png
    - These approved reference sheets become the reference images for all downstream scoring in Face Lock and Body Lock stages
  </action>
  <verify>
    <automated>python -c "from scripts.generate_identity_lock import *" 2>&1 | head -5 || echo "Script exists, import test"</automated>
    <automated>ls Universe/Characters/Lily\ Bunny/references/ 2>&1</automated>
    <human-check>Open Review UI at http://localhost:8000. Verify reference sheet candidates appear for Lily Bunny. Approve/reject candidates. Verify approved assets show state="production".</human-check>
  </verify>
  <done>
    - scripts/generate_identity_lock.py exists and is runnable
    - Reference sheet generation completed: 50-100 candidates per angle × 4 angles
    - Human review completed: winners selected for front, 3/4, profile, back
    - Approved reference images stored in Universe/Characters/Lily Bunny/references/
    - Each approved asset has state="production" and lineage populated
  </done>
  <acceptance_criteria>
    - 4 approved reference sheet images in Universe/Characters/Lily Bunny/references/ (front.png, 3_4.png, profile.png, back.png)
    - Each has AssetModel.state == "production" and AssetModel.lineage populated
    - Human confirmed visual quality and identity consistency of all 4 angles
  </acceptance_criteria>
  <reversibility rating="one-way">Identity Lock sets the canonical reference images. All downstream scoring (expressions, poses, outfits) uses these as identity baselines. Changing them later requires re-scoring all downstream assets.</reversibility>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Checkpoint: Verify reference sheet winners</name>
  <what-built>Reference sheet generation candidates for Lily Bunny (front, 3/4, profile, back). The GenerationJob pipeline produced candidate images scored by IdentityScorer and selected by DiversityFilter.</what-built>
  <how-to-verify>
    1. Open Review UI at http://localhost:8000
    2. Navigate to Lily Bunny → Review references (batch mode, 4x4 grid)
    3. Verify candidates display with Brand Scores and visual drift indicators
    4. For each angle (front, 3/4, profile, back):
       - Review top 10 candidates
       - Select the best candidate by clicking "Approve"  
       - Verify the state transitions through the pipeline
    5. Confirm that approved images show in the Character Detail page with state indicators
  </how-to-verify>
  <resume-signal>Type "approved" to confirm reference sheet winners are locked, or describe any issues found.</resume-signal>
</task>

<task type="auto">
  <name>Create expression generation orchestration script and run Face Lock stage</name>
  <files>
    scripts/generate_face_lock.py,
    Universe/Characters/Lily Bunny/expressions/
  </files>
  <read_first>
    @scripts/generate_identity_lock.py (pattern to follow),
    @src/pipeline/generation_job.py,
    @src/models/schemas.py (AssetModel.lineage),
    @Universe/Characters/Lily Bunny/bio.md,
    @.planning/phases/01b-character-asset-production/01b-CONTEXT.md (D-09 merged expression list, D-10 generate ALL, D-14 expression thresholds: 92-97%),
    @.planning/phases/01b-character-asset-production/01b-RESEARCH.md (lines 55-59 — CHAR-03 details)
  </read_first>
  <action>
    **Precondition:** Reference sheets must be approved (Identity Lock complete). The approved front reference sheet is used as the reference image for identity scoring in expression generation.

    **Step 1: Create `scripts/generate_face_lock.py`**
    
    Same pattern as generate_identity_lock.py but for expressions:
    
    1. Initialize same pipeline components (ComfyUIBackend, PromptBuilder, IdentityScorer, SQLiteAssetRepository, DiversityFilter, GenerationJob)
    
    2. Load the approved front reference sheet path for use as scoring reference:
       ```python
       # Find approved reference from the asset repository
       approved_refs = repo.find_approved(character_id, "reference")
       front_ref = [a for a in approved_refs if a.variant == "front"][0]
       reference_image_path = front_ref.file_path
       ```
    
     3. Use `PromptBuilder._known_expressions()` at runtime to get the merged set (32 expressions: 23 from PHASE1.md + 9 code extras, per D-09/D-10 updated in Plan 01b-01).
    
    4. For each expression:
       - Generates 50-80 candidates (ComfyUIBackend, asset_type="expression")  
        - Scores with IdentityScorer using multi-metric scoring per D-13 (Identity Consistency 35%, Style Consistency 20%, Prompt Adherence 15%, Technical Quality 15%, Composition 10%, Diversity 5%) with the front reference sheet as reference image
        - Runs DiversityFilter to select top 10-15
       - Shortlisted assets saved with:
         - lineage = {"generation_batch": batch_id, "candidate_pool": count, 
                       "version_history": [], "reference_asset_id": front_ref.id, "asset_type": "expression"}
    
    5. Estimated generation time: 32 expressions × 60 images × ~8s = ~4.3 hours
    
    **Step 2: Batch execution strategy**
    
    To avoid overwhelming ComfyUI (single-threaded, Pitfall 4):
    - Process expressions sequentially (one at a time)
    - Use the script's own loop, not nested async jobs
    - Log progress after each expression (e.g., "Expression 5/32: 'surprised' — 60 generated, 15 shortlisted")
    - Handle failures per-expression so one failed variant doesn't block the rest
    
    **Step 3: Human review checkpoint**
    
    After all expressions are generated, review through the Review UI:
    - http://localhost:8000/review/{lily-bunny-id}?asset_type=expression&batch=true&grid=4x4
    - For each expression: review top 10-15, select winner
    - D-14 threshold: 92-97% identity similarity for expressions
    - Use Approve (shortlisted → approved) or Reject (shortlisted → draft for retry)
    
    **Step 4: Approved assets**
    - Winners stored to Universe/Characters/Lily Bunny/expressions/{expression_name}.png
    - Each winner gets two promotions: approved → production
  </action>
  <verify>
    <automated>python -c "from scripts.generate_face_lock import *" 2>&1 | head -5 || echo "Script exists, import test"</automated>
    <automated>ls Universe/Characters/Lily\ Bunny/expressions/ 2>&1</automated>
    <human-check>Open Review UI. Verify expression candidates appear for each of the 32 expressions. Approve/reject. Verify state transitions.</human-check>
  </verify>
  <done>
    - scripts/generate_face_lock.py exists and is runnable
    - All 32 expressions from merged list generated with 50-80 candidates each
    - Human review completed for all expressions
    - Approved expression images in Universe/Characters/Lily Bunny/expressions/
    - Each approved asset has state="production" and lineage populated with reference_asset_id
  </done>
  <acceptance_criteria>
    - Approved expression images in Universe/Characters/Lily Bunny/expressions/ (one per expression)
    - Each has AssetModel.state == "production" and AssetModel.lineage.reference_asset_id pointing to the front reference sheet
    - Human confirmed visual quality and expression accuracy for every variant
  </acceptance_criteria>
  <reversibility rating="costly">Expression images depend on the Identity Lock reference sheets. Re-doing reference sheets later would require re-scoring and potentially regenerating all expression assets.</reversibility>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Checkpoint: Verify expression winners</name>
  <what-built>All expression generation candidates for Lily Bunny (32 expressions from merged list). Each expression has 10-15 shortlisted candidates scored by IdentityScorer and selected by DiversityFilter.</what-built>
  <how-to-verify>
    1. Open Review UI at http://localhost:8000
    2. Navigate to Lily Bunny → Review expressions (batch mode, 4x4 grid)
     3. For each expression variant (32 total):
       - Verify candidates display with Brand Scores
       - Compare against the front reference sheet shown in the left panel
       - Select the best candidate by clicking "Approve" or "Approve & Promote"
       - If no candidate is acceptable, click "Regenerate Similar" to queue a new batch with nearby seeds
    4. Verify approved expressions show in the character detail page grouped under "Expressions"
  </how-to-verify>
  <resume-signal>Type "expressions approved" to confirm all expression winners are locked, or describe issues found.</resume-signal>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Pipeline → ComfyUI REST API | HTTP localhost:8188 — workflow JSON submitted, images returned |
| Pipeline → Filesystem | Generated images written to Universe/Characters/Lily Bunny/*/ |
| Pipeline → SQLite | Metadata written to catalog.db via parameterized queries |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-01b-10 | Tampering | ComfyUI workflow submission | medium | accept | Workflows are predefined JSON files from version control — not user-submitted. ComfyUI is localhost-only (127.0.0.1:8188). |
| T-01b-11 | Information Disclosure | Generated images on filesystem | low | accept | Images are character assets for animation production — no sensitive data. Filesystem is local. |
| T-01b-12 | Denial of Service | Long-running generation | low | accept | 4+ hours of sequential ComfyUI jobs. This is expected production runtime. Timeout handling in GenerationJob prevents hung queues. Each variant has independent error handling. |
| T-01b-13 | Spoofing | Generated image quality validation | medium | mitigate | All candidates pass through IdentityScorer and DiversityFilter before human review. D-14 thresholds provide automatic quality gates. Human review is the final authority. |
| T-01b-SC | Tampering | No new pip package installs | low | accept | All dependencies already in pyproject.toml or stdlib. ComfyUI is external process. |
</threat_model>

<verification>
1. ComfyUI is reachable at localhost:8188 before generation starts
2. Approved reference sheets exist in Universe/ with state="production"
3. Approved expressions exist in Universe/ with state="production"
4. Each approved asset has populated lineage field
5. Identity scores for reference sheets ≥ 0.95 (per D-15 auto-pass threshold)
6. Identity scores for expressions ≥ 0.90 (per D-15 expression threshold)
</verification>

<success_criteria>
1. 4 approved multi-angle reference sheets (front, 3/4, profile, back) in Universe Library
2. 32 approved expression images in Universe Library (one per merged expression)
3. All approved assets have state="production" and lineage populated
4. Reference sheet identity scores ≥ 0.95
5. Expression identity scores ≥ 0.90
6. Human review completed for all assets
</success_criteria>

<output>
Create `.planning/phases/01b-character-asset-production/01b-04-SUMMARY.md` when done.
</output>
