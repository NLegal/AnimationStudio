---
phase: 01b-character-asset-production
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/prompt_builder/builder.py
  - src/models/schemas.py
  - src/asset_repository/sqlite_repo.py
  - src/identity_engine/plugins/color_verification.py
  - tests/test_prompt_builder.py
  - tests/test_asset_repository.py
autonomous: true
requirements:
  - CHAR-02
  - CHAR-03
  - CHAR-04
user_setup: []
must_haves:
  truths:
    - PromptBuilder._known_expressions() returns the merged PHASE1.md + code superset (32 unique expressions: 23 from PHASE1.md + 9 code extras — including blowing_kiss, winking, very_happy, giggling, whistling, angry, shy, silly, sneezing, coughing, sighing)
    - PromptBuilder._known_poses() returns the merged PHASE1.md + code superset (20 unique poses including hugging, holding_hands, pointing, clapping, waving, kneeling)
    - AssetModel has a lineage field that round-trips through SQLite persistence
    - ColorVerificationPlugin loads brand palette from Universe/ColorPalette/brand-palette.json
    - All existing tests pass after changes
  artifacts:
    - src/prompt_builder/builder.py (updated expression and pose sets)
    - src/models/schemas.py (lineage field added to AssetModel)
    - src/asset_repository/sqlite_repo.py (lineage column in assets table, updated _row_to_asset and save)
    - src/identity_engine/plugins/color_verification.py (palette loaded from file)
    - tests/test_prompt_builder.py (new test cases for merged expression/pose lists)
    - tests/test_asset_repository.py (new test for lineage metadata persistence)
  key_links:
    - PromptBuilder._known_expressions() feeds PromptBuilder.build() which routes to templates.expression() — merged list must match what templates.expression() appends to prompt text.
    - ColorVerificationPlugin DEFAULT_BRAND_PALETTE is referenced in __init__ as default — file-load fallback must not change the constructor signature.
    - AssetModel lineage dict must serialize to JSON for SQLite TEXT column and deserialize back to dict on read.
---

<objective>
Update the character factory's prompt builder with the merged expression/pose list, add lineage tracking to the asset storage, and fix the color verification plugin to load the brand palette from the filesystem. These are the foundational code changes needed before production image generation can begin.

Purpose: Close all code-spec gaps identified in RESEARCH.md that would cause incorrect outputs or missing metadata during production runs.
Output: Updated PromptBuilder with complete expression/pose sets, AssetModel with lineage field and SQLite migration, ColorVerificationPlugin with filesystem palette loading, plus updated tests.
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

# Source files to read before modifying
@src/prompt_builder/builder.py
@src/models/schemas.py
@src/asset_repository/sqlite_repo.py
@src/identity_engine/plugins/color_verification.py
@Universe/ColorPalette/brand-palette.json
@tests/test_prompt_builder.py
@tests/test_asset_repository.py
@tests/conftest.py
</context>

<tasks>

<task type="tracer" tdd="true">
  <name>Tracer: Update _known_expressions() to merged PHASE1.md + code superset with end-to-end pipeline integration test</name>
  <files>
    src/prompt_builder/builder.py,
    tests/test_prompt_builder.py
  </files>
  <read_first>
    @src/prompt_builder/builder.py (lines 115-134, _known_expressions and _known_poses),
    @PHASE1.md (lines 518-567 — expression list),
    @src/prompt_builder/templates.py (lines 79-86 — expression() template to verify how expression names appear in prompts),
    @.planning/phases/01b-character-asset-production/01b-CONTEXT.md (D-09, D-10, D-11),
    @tests/test_prompt_builder.py (existing test patterns),
    @tests/conftest.py (fixtures available)
  </read_first>
  <behavior>
    - Test 1: PromptBuilder._known_expressions() returns all 32 unique expressions from merged superset:
      PHASE1.md expressions (23): neutral, happy, very_happy, laughing, giggling, smiling, excited, surprised, confused, thinking, curious, sleepy, yawning, crying, sad, scared, embarrassed, proud, determined, singing, whistling, blowing_kiss, winking
      Code extras (9, none overlapping): angry, shy, silly, sneezing, coughing, sighing, tired, worried, disgusted
      Total merged set = 32 expressions (23 from PHASE1.md + 9 code extras)
      Verify with: assert known == {expected_set}
    - Test 2: Every expression in the merged list produces a valid prompt containing the expression name AND character name
    - Test 3: Unknown expression name logs a WARNING but still produces valid prompt (best-effort behavior preserved)
    - Test 4: Integration test: GenerationJob with MockBackend + updated PromptBuilder processes an expression generation successfully end-to-end (build prompt → generate mock image → score → save)
  </behavior>
  <action>
    Update `PromptBuilder._known_expressions()` to return the merged superset of PHASE1.md + code expression names per D-09/D-10/D-11.

    **Source sets to merge (case-insensitive dedup):**

    PHASE1.md (lines 522-562): Neutral, Happy, Very Happy, Laughing, Giggling, Smiling, Excited, Surprised, Confused, Thinking, Curious, Sleepy, Yawning, Crying, Sad, Scared, Embarrassed, Proud, Determined, Singing, Whistling, Blowing Kiss, Winking — 23 expressions.

    Code extras (builder.py lines 118-124): angry, shy, silly, sneezing, coughing, sighing, tired, worried, disgusted — 9 extras.

    Merge rules: lowercase, unique. PHASE1.md expressions map to snake_case: "Blowing Kiss" → "blowing_kiss". Overlaps (happy, sad, surprised, scared, sleepy, singing, laughing, crying, excited, confused, tired, thinking, yawning) are deduplicated.

    Final merged set (32 expressions):
    neutral, happy, very_happy, laughing, giggling, smiling, excited, surprised, confused, thinking, curious, sleepy, yawning, crying, sad, scared, embarrassed, proud, determined, singing, whistling, blowing_kiss, winking, angry, shy, silly, sneezing, coughing, sighing, tired, worried, disgusted

    Remove any expressions from the code that are NOT in this merged list (check _known_expressions() current return for any unlisted items).

    Create a new test class `TestMergedExpressionList` in test_prompt_builder.py:
    - `test_merged_expression_count`: `_known_expressions()` returns exactly 32.
    - `test_expression_includes_phase1_additions`: asserts blowing_kiss, winking, very_happy, giggling, whistling are in the set.
    - `test_expression_retains_code_extras`: asserts angry, shy, silly, sneezing, coughing, sighing are in the set.
    - `test_every_expression_produces_valid_prompt`: parametrize over all 32 expressions, verify each produces a prompt via builder.build() with asset_type="expression".
    - `test_best_effort_unknown_expression_warning`: verify unknown expression name logs warning and still produces valid prompt (migrate existing test_unknown_expression_warning to this class).

    **Do NOT modify** `_known_poses()` in this task — that is handled in Task 3.
    **Do NOT modify** `PromptTemplates` — the templates already accept any expression name string.

    CRITICAL: The integration test proving end-to-end flow uses existing `conftest.py` fixtures (MockBackend, in_memory_db). Create a test class `TestEndToEndExpressionPipeline` that:
    - Creates a PromptBuilder with the updated list
    - Creates a GenerationJob with MockBackend, IdentityScorer (uses MockScorerPlugin), in-memory SQLiteAssetRepository
    - Creates a JobQueue job for one expression variant ("happy")
    - Runs execute()
    - Asserts the job completed, at least one asset was saved with state="shortlisted"
    - This proves the full pipeline works with the updated expression list
  </action>
  <verify>
    <automated>pytest tests/test_prompt_builder.py::TestMergedExpressionList --timeout=30 -x -v</automated>
    <automated>pytest tests/test_prompt_builder.py::TestEndToEndExpressionPipeline --timeout=30 -x -v</automated>
  </verify>
  <done>
    - `_known_expressions()` returns exactly 32 expressions (all 23 PHASE1.md additions + all 9 code extras)
    - Every expression produces a valid prompt with character name
    - Integration test proves full GenerationJob pipeline works end-to-end with updated expression list
    - All existing tests in test_prompt_builder.py still pass (except those superseded by new tests)
  </done>
  <acceptance_criteria>
    - `_known_expressions()` returns set of 32 strings
    - "blowing_kiss", "winking", "very_happy", "giggling", "whistling" are present
    - "angry", "shy", "silly", "sneezing", "coughing", "sighing" are present
    - Integration test with GenerationJob + MockBackend + SQLiteAssetRepository completes with at least 1 shortlisted asset
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Add lineage metadata field to AssetModel and SQLite schema</name>
  <files>
    src/models/schemas.py,
    src/asset_repository/sqlite_repo.py,
    tests/test_asset_repository.py
  </files>
  <read_first>
    @src/models/schemas.py (lines 21-41 — AssetModel full definition),
    @src/asset_repository/sqlite_repo.py (lines 150-281 — SQLiteAssetRepository class),
    @.planning/phases/01b-character-asset-production/01b-CONTEXT.md (D-18 decision),
    @.planning/phases/01b-character-asset-production/01b-RESEARCH.md (line 115: "AssetModel missing lineage field"),
    @tests/test_asset_repository.py (existing test patterns, especially test_json_serialization and test_state_transition_validity)
  </read_first>
  <action>
    Per D-18: "Each approved asset retains lineage metadata (generation_batch, candidate_pool, version_history, episodes using this asset)."

    **Schema changes:**

    1. Add `lineage` field to `AssetModel` in schemas.py:
    ```python
    lineage: Optional[dict] = Field(
        default=None,
        description="Lineage metadata per D-18: generation_batch, candidate_pool, version_history, episode_usage"
    )
    ```

    2. Add `lineage TEXT` column to the `assets` table in `SQLiteAssetRepository._init_schema()`:
    ```sql
    lineage TEXT DEFAULT NULL
    ```
    Use an ALTER TABLE migration with IF NOT EXISTS check since the table already exists.

    3. Update `_row_to_asset()` to deserialize lineage:
    ```python
    lineage=json.loads(row["lineage"]) if row.get("lineage") else None,
    ```

    4. Update `save()` to serialize lineage:
    ```python
    json.dumps(record.lineage) if record.lineage else None,
    ```
    Add `lineage` to the INSERT column list and parameter tuple.

    5. Create an `_apply_migrations()` method in `SQLiteAssetRepository` that checks if the `lineage` column exists and adds it via ALTER TABLE if missing. Call this from `_init_schema()` after `CREATE TABLE`. This ensures backward compatibility with existing databases.

    **Test updates:**
    - Add `test_lineage_metadata_roundtrip()` to test_asset_repository.py: Create AssetModel with lineage dict `{"generation_batch": "batch-001", "candidate_pool": 50, "version_history": []}`, save to SQLiteAssetRepository, retrieve, assert lineage dict matches.

    - Do NOT require a schema migration reset — the ALTER TABLE approach means existing Phase 1 databases are updated in-place.

    **Do NOT modify** existing test assertions or remove existing test methods. Only add new column and tests.
  </action>
  <verify>
    <automated>pytest tests/test_asset_repository.py::test_lineage_metadata_roundtrip --timeout=15 -x -v</automated>
    <automated>pytest tests/test_asset_repository.py --timeout=30 -x</automated>
  </verify>
  <done>
    - AssetModel has a lineage Optional[dict] field
    - SQLite assets table has lineage TEXT column
    - Lineage round-trips correctly through save() and _row_to_asset()
    - Existing asset repository tests all pass
    - _apply_migrations() handles existing databases without error
  </done>
  <acceptance_criteria>
    - `AssetModel` has `lineage: Optional[dict] = None` field
    - SQLite assets table has `lineage` column (checked via PRAGMA table_info)
    - Dict round-trips with JSON serialization intact
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Update _known_poses() to merged superset and fix ColorVerificationPlugin palette loading</name>
  <files>
    src/prompt_builder/builder.py,
    src/identity_engine/plugins/color_verification.py,
    tests/test_prompt_builder.py,
    tests/test_scoring_plugins.py
  </files>
  <read_first>
    @src/prompt_builder/builder.py (lines 126-134 — _known_poses()),
    @PHASE1.md (lines 576-618 — pose list),
    @src/identity_engine/plugins/color_verification.py (lines 17-23 — DEFAULT_BRAND_PALETTE, lines 74-123 — class, lines 99-101 — palette selection),
    @Universe/ColorPalette/brand-palette.json (lines 4-9 — primary colors),
    @.planning/phases/01b-character-asset-production/01b-CONTEXT.md (D-09, D-10, D-11),
    @.planning/phases/01b-character-asset-production/01b-RESEARCH.md (lines 109-111 — gaps for poses and color plugin),
    @tests/test_prompt_builder.py (existing test patterns),
    @tests/test_scoring_plugins.py (existing test patterns if any)
  </read_first>
  <action>
    **Part A: Update _known_poses()**
    
    PHASE1.md poses (lines 578-618): Standing, Walking, Running, Jumping, Skipping, Sitting, Kneeling, Dancing, Sleeping, Reading, Writing, Pointing, Clapping, Waving, Hugging, Holding Hands, Playing, Swimming, Flying, Sliding — 20 poses.
    
    Code extras (builder.py lines 129-134): hopping, eating, drinking, drawing, crawling, hiding, stretching, bouncing — 8 extras.
    
    Overlaps: standing, running, jumping, sitting, dancing, walking, sleeping, skipping, sliding are in both.
    
    Merge rules: lowercase, unique. "Holding Hands" → "holding_hands". "Skipping", "Sliding" overlap.
    
    Final merged set (20 poses, keeping all PHASE1.md original 20 + any code extras NOT in the PHASE1.md list):
    
    From PHASE1.md: standing, walking, running, jumping, skipping, sitting, kneeling, dancing, sleeping, reading, writing, pointing, clapping, waving, hugging, holding_hands, playing, swimming, flying, sliding
    Code extras NOT in PHASE1.md: hopping, eating, drinking, drawing, crawling, hiding, stretching, bouncing
    
    Total merged: 28 poses (20 from PHASE1.md + 8 code extras)
    
    Update the set in _known_poses() accordingly.
    
    Add test class `TestMergedPoseList` in test_prompt_builder.py:
    - `test_merged_pose_count`: asserts exactly 28 poses.
    - `test_pose_includes_phase1_additions`: asserts hugging, holding_hands, pointing, clapping, kneeling in set.
    - `test_pose_retains_code_extras`: asserts hopping, eating, drinking, drawing, crawling, hiding, stretching, bouncing in set.
    - `test_every_pose_produces_valid_prompt`: parametrize over all 28 poses.
    
    **Part B: Fix ColorVerificationPlugin palette loading**
    
    Current: `DEFAULT_BRAND_PALETTE` is hardcoded RGB tuples (lines 17-23). The `score()` method uses `DEFAULT_BRAND_PALETTE` when no reference image is provided (line 100).
    
    Fix: Add a module-level function `_load_brand_palette_from_file()` that:
    - Reads `Universe/ColorPalette/brand-palette.json` relative to the project root
    - Extracts hex values from the `primary` group (pink, blue, yellow, green, orange)
    - Converts hex strings to RGB tuples
    - Falls back to DEFAULT_BRAND_PALETTE if file not found or parse error
    
    Replace the direct `DEFAULT_BRAND_PALETTE` reference in `score()` with a call to this function. Keep `DEFAULT_BRAND_PALETTE` as the fallback constant.
    
    Cache the loaded palette as a class-level `_cached_palette` so filesystem reads happen at most once per process.
    
    Add a test to test_scoring_plugins.py (or create one if the file is minimal):
    - `test_color_plugin_loads_palette_from_file`: Verify the plugin loads colors from brand-palette.json.
    - `test_color_plugin_fallback_on_missing_file`: Temporarily point to a non-existent path and verify DEFAULT_BRAND_PALETTE is used as fallback.
    - `test_color_plugin_scores_with_loaded_palette`: Verify score() returns a value in [0,1] using the file-loaded palette.
  </action>
  <verify>
    <automated>pytest tests/test_prompt_builder.py::TestMergedPoseList --timeout=30 -x -v</automated>
    <automated>pytest tests/test_scoring_plugins.py::TestColorVerificationPlugin --timeout=30 -x -v</automated>
  </verify>
  <done>
    - `_known_poses()` returns exactly 28 poses including all PHASE1.md poses + code extras
    - Every pose produces a valid prompt with character name
    - ColorVerificationPlugin loads brand palette from Universe/ColorPalette/brand-palette.json
    - Falling back to DEFAULT_BRAND_PALETTE when file is absent
    - All tests pass
  </done>
  <acceptance_criteria>
    - `_known_poses()` returns set of 28 strings
    - "hugging", "holding_hands", "pointing", "clapping", "kneeling" are present
    - "hopping", "eating", "drinking", "drawing", "crawling", "hiding", "stretching", "bouncing" are present
    - ColorVerificationPlugin.score() returns float in [0,1] using palette from brand-palette.json
  </acceptance_criteria>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Code → Filesystem (palette.json) | Reading Universe/ColorPalette/brand-palette.json from Python code — local filesystem access only |
| Python → SQLite | Local process database — no network boundary crossed |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-01b-01 | Tampering | ColorVerificationPlugin file read | low | accept | Palette file is version-controlled in the repo; only local reads from a fixed path. Malicious palette file would affect scoring but not execute code. |
| T-01b-02 | Tampering | SQLite lineage column | low | accept | Lineage data is written by pipeline code only (not user-submitted). SQLite queries use parameterized placeholders (already verified in sqlite_repo.py). |
| T-01b-03 | Information Disclosure | AssetModel lineage serialization | low | accept | Lineage data is internal metadata (generation batch IDs, version history). No PII or secrets. |
| T-01b-SC | Tampering | pip package installs | high | mitigate | No new package installs in this plan. All dependencies already in pyproject.toml. Verify via `pip list` before running if any install occurs. |
</threat_model>

<verification>
1. `pytest tests/test_prompt_builder.py --timeout=30 -x -v` — all expression/pose list tests pass
2. `pytest tests/test_asset_repository.py --timeout=30 -x` — lineage tests pass  
3. `pytest tests/test_scoring_plugins.py --timeout=30 -x -v` — color plugin tests pass
4. Existing conftest.py fixtures are NOT modified (MockBackend, in_memory_db, etc.)
5. No new external dependencies introduced
</verification>

<success_criteria>
1. PromptBuilder._known_expressions() returns 32 expressions with all PHASE1.md additions and code extras
2. PromptBuilder._known_poses() returns 28 poses with all PHASE1.md additions and code extras
3. AssetModel has lineage Optional[dict] field that persists through SQLite
4. ColorVerificationPlugin loads palette from Universe/ColorPalette/brand-palette.json with file-not-found fallback
5. All 3 new test classes pass (TestMergedExpressionList, TestMergedPoseList, TestColorVerificationPlugin)
6. Integration test proves GenerationJob + MockBackend pipeline works with updated lists
</success_criteria>

<output>
Create `.planning/phases/01b-character-asset-production/01b-01-SUMMARY.md` when done.
</output>
