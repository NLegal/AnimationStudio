---
phase: 01b-character-asset-production
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - src/review_ui/app.py
  - src/review_ui/templates/review.html
  - src/review_ui/static/style.css
autonomous: true
requirements:
  - CHAR-02
  - CHAR-03
  - CHAR-04
  - CHAR-05
user_setup: []
must_haves:
  truths:
    - POST /approve/{asset_id} transitions asset state per D-15 lifecycle (shortlisted → approved)
    - POST /reject/{asset_id} transitions asset state back to draft with optional reason
    - POST /regenerate/{asset_id} creates a new generation job with nearby seeds
    - POST /promote/{asset_id} transitions shortlisted → approved → production (two-step)
    - /review/{character_id}?grid=3x3 displays 9 candidates in a 3-column grid
    - /review/{character_id}?grid=4x4 displays 16 candidates in a 4-column grid
    - Error responses (404, invalid transition) return RedirectResponse with status_code=303 (no crash)
  artifacts:
    - src/review_ui/app.py (wired action handlers + grid query parameter)
    - src/review_ui/templates/review.html (dynamic grid classes, grid selector UI)
    - src/review_ui/static/style.css (grid-columns-3 and grid-columns-4 classes)
  key_links:
    - Action handlers call SQLiteAssetRepository.update_state() — must use correct lifecycle transitions per D-15
    - /approve transitions shortlisted → approved; /promote transitions shortlisted → approved → production (two-step)
    - /reject transitions scored/shortlisted → draft (enables regeneration)
    - Grid CSS classes applied to .batch-grid element via dynamic class binding
---

<objective>
Wire the Review UI's action handlers to the real SQLiteAssetRepository (replacing stubs) and add configurable batch grid sizes (3x3, 4x4) per D-16. These are the final code changes needed before production generation runs can flow through human review.

Purpose: Enable operators to approve/reject/promote generated assets through the Review UI and review up to 16 candidates at once in configurable batch grids.
Output: Wired Review UI with real lifecycle transitions and responsive batch grid layouts.
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

# Source files
@src/review_ui/app.py
@src/review_ui/templates/review.html
@src/review_ui/static/style.css
@src/asset_repository/sqlite_repo.py
@src/models/schemas.py
@tests/conftest.py
</context>

<tasks>

<task type="auto">
  <name>Wire Review UI action handlers to SQLiteAssetRepository with D-15 lifecycle transitions</name>
  <files>
    src/review_ui/app.py
  </files>
  <read_first>
    @src/review_ui/app.py (lines 192-223 — action handler stubs, lines 31-58 — _StubAssetRepo, lines 64-79 — create_app),
    @src/asset_repository/sqlite_repo.py (lines 225-236 — update_state method, lines 35-43 — _VALID_TRANSITIONS),
    @.planning/phases/01b-character-asset-production/01b-CONTEXT.md (D-15: approval zones, D-17: state machine, D-18: lineage),
    @.planning/phases/01b-character-asset-production/01b-RESEARCH.md (lines 112, 350-353 — Pitfall 5 on state transitions, lines 433-447 — code example for wired handler)
  </read_first>
  <action>
    Replace the four stub action handlers with real implementations that call the injected `repo.update_state()`.

    The `create_app()` factory already accepts an `asset_repo` parameter. The stub handlers currently return `RedirectResponse(url="/")` with no side effects.

    **/approve/{asset_id}** (D-15: shortlisted → approved):
    - Call `await repo.update_state(asset_id, "approved")`
    - Catch `NotFoundError` (asset ID not found) — return RedirectResponse with status 303
    - Catch `ValueError` (invalid transition) — return RedirectResponse with status 303
    - On success, also set `approved_at = datetime.now()` if the repo supports it. The current SQLiteAssetRepository.update_state() does not update approved_at — add a `Lineage` note in the asset lineage if present, or just call update_state.
    - Return `RedirectResponse(url=referer, status_code=303)` where referer is from `request.headers.get("referer", "/")`

    **/reject/{asset_id}** (D-17: scored/shortlisted → draft for regeneration):
    - Accept optional `reason` form field
    - Call `await repo.update_state(asset_id, "draft")`
    - Log the reason if provided
    - Catch NotFoundError, ValueError → redirect with 303
    - Return RedirectResponse

    **/regenerate/{asset_id}** (D-04: queue new job with nearby seeds):
    - Retrieve the asset via `await repo.get(asset_id)`
    - If found and has `seed`, create a new job in JobQueue with seeds = [seed-5, seed-3, seed-1, seed+1, seed+3, seed+5]
    - If no seed or no asset, just redirect
    - Return RedirectResponse
    - **Note:** This is a best-effort convenience action. The actual generation runner processes the queue. Just create the JobQueue entry.

    **/promote/{asset_id}** (D-15: shortlisted → approved → production two-step):
    - Call `await repo.update_state(asset_id, "approved")`
    - Then immediately call `await repo.update_state(asset_id, "production")`
    - Catch errors on either step
    - Return RedirectResponse

    **Important changes to the route functions:**
    - Add `request: Request` parameter to all four handlers to read the referer header
    - Import `NotFoundError` from `src.asset_repository.sqlite_repo` (add to imports section)
    - Use proper error handling — never crash, always redirect

    **Add a helper method `_get_referer(request)`** that returns `request.headers.get("referer", "/")` for clean redirects.

    **Keep `_StubAssetRepo`** as fallback (the app still works without injecting a real repo). Do not remove it.

    Add a `logger` import at the top of the file if not present:
    ```python
    import logging
    logger = logging.getLogger(__name__)
    ```

    Do NOT modify any route other than the four action handlers.
    Do NOT modify the dashboard, character_detail, or review_page routes.
  </action>
  <verify>
    <automated>pytest tests/ -x --timeout=60 -v -k "review or asset_repository" 2>&1 | head -50</automated>
    <automated>pytest tests/ --timeout=60 -x -v 2>&1 | tail -20</automated>
  </verify>
  <done>
    - POST /approve/{asset_id} transitions shortlisted → approved via repo.update_state()
    - POST /reject/{asset_id} transitions scored/shortlisted → draft via repo.update_state()
    - POST /regenerate/{asset_id} creates a new JobQueue job with nearby seeds
    - POST /promote/{asset_id} transitions shortlisted → approved → production (two calls)
    - Errors (404, bad transition) produce RedirectResponse (not crash)
    - All existing tests still pass
  </done>
  <acceptance_criteria>
    - Four POST handlers call repo.update_state() with correct transitions
    - /approve uses "approved", /reject uses "draft", /promote uses "approved" then "production"
    - NotFoundError and ValueError caught → RedirectResponse returned
    - No changes to GET routes or template rendering
  </acceptance_criteria>
</task>

<task type="auto">
  <name>Add configurable batch grid sizes (3x3, 4x4) to Review UI per D-16</name>
  <files>
    src/review_ui/app.py,
    src/review_ui/templates/review.html,
    src/review_ui/static/style.css,
    tests/test_review_ui.py
  </files>
  <read_first>
    @src/review_ui/app.py (lines 129-190 — review_page route),
    @src/review_ui/templates/review.html (lines 125-151 — batch compare mode template),
    @src/review_ui/static/style.css (lines 550-563 — .batch-grid CSS, lines 592-608 — responsive),
    @.planning/phases/01b-character-asset-production/01b-CONTEXT.md (D-16),
    @.planning/phases/01b-character-asset-production/01b-RESEARCH.md (lines 113, 399-430 — code example for grid config, lines 551-553 — test gap for grid size)
  </read_first>
  <action>
    **Part A: Route update (app.py)**

    Add `grid: str = Query("2x2")` parameter to the `review_page()` function signature.

    Parse grid dimensions:
    ```python
    grid_config = {"2x2": (2, 2, 4), "3x3": (3, 3, 9), "4x4": (4, 4, 16)}
    grid_cols, grid_rows, grid_capacity = grid_config.get(grid, (2, 2, 4))
    ```

    Add grid params to the template context:
    ```python
    "grid_cols": grid_cols,
    "grid_rows": grid_rows,
    "grid_capacity": grid_capacity,
    "current_grid": grid,
    ```

    Update the candidate slicing in batch mode (line 130 currently slices `[:4]`):
    ```python
    candidates_for_grid = candidates[:grid_capacity] if batch else candidates
    ```

    Update the "Batch Compare" link to include current grid size:
    ```python
    href="/review/{{ character.id }}?asset_type={{ asset_type }}&batch=true&grid={{ current_grid }}"
    ```

    Add grid size selector buttons in the review controls section:
    ```html
    <div class="grid-selector">
      <span class="grid-label">Grid:</span>
      <a href="/review/{{ character.id }}?asset_type={{ asset_type }}&batch=true&grid=2x2" 
         class="btn btn-sm {% if current_grid == '2x2' %}btn-active{% endif %}">2x2</a>
      <a href="/review/{{ character.id }}?asset_type={{ asset_type }}&batch=true&grid=3x3" 
         class="btn btn-sm {% if current_grid == '3x3' %}btn-active{% endif %}">3x3</a>
      <a href="/review/{{ character.id }}?asset_type={{ asset_type }}&batch=true&grid=4x4" 
         class="btn btn-sm {% if current_grid == '4x4' %}btn-active{% endif %}">4x4</a>
    </div>
    ```

    **Part B: Template update (review.html)**

    Replace the fixed `candidates[:4]` slicing in the batch grid section (line 130) with `candidates[:grid_capacity]`.

    Change the batch-grid CSS class from static to dynamic:
    ```html
    <div class="batch-grid grid-{{ current_grid }}">
    ```

    Update candidate loop to iterate over all candidates (not just first 4):
    ```html
    {% for card in candidates[:grid_capacity] %}
    ```

    **Part C: CSS update (style.css)**

    Add CSS for the three grid sizes:
    ```css
    .batch-grid { display: grid; gap: 1rem; }

    .grid-2x2 { grid-template-columns: 1fr 1fr; }
    .grid-3x3 { grid-template-columns: 1fr 1fr 1fr; }
    .grid-4x4 { grid-template-columns: 1fr 1fr 1fr 1fr; }
    ```

    Remove the old `.batch-grid` rule that had fixed `grid-template-columns: 1fr 1fr` (line 551-555) since this is replaced by the dynamic classes.

    Add styling for the grid selector UI:
    ```css
    .grid-selector { display: flex; align-items: center; gap: 0.25rem; }
    .grid-label { font-size: 0.85rem; color: var(--text-secondary); margin-right: 0.25rem; }
    .btn-active { background: var(--blue-dark); color: white; border-color: var(--blue-dark); }
    ```

    Ensure batch cards scale appropriately for smaller grid cells at 3x3 and 4x4:
    - Batch cards at 3x3 should have smaller placeholder images (min-height: 150px)
    - Batch cards at 4x4 should have smaller still (min-height: 120px)
    - Use a CSS class on .batch-grid: `.grid-3x3 .batch-card .placeholder-img { min-height: 150px; }`
    - `.grid-4x4 .batch-card .placeholder-img { min-height: 120px; }`

    **Part D: Responsive behavior**
    - At 2x2: 2 columns (existing behavior)
    - At 3x3: 3 columns on desktop, 1 column on mobile (max-width: 768px)
    - At 4x4: 4 columns on desktop, 2 columns on tablet, 1 on mobile
    **Part E: Add test file for grid size parameterization**
    
    Create `tests/test_review_ui.py` with a `TestReviewGridSizes` class using FastAPI TestClient:
    - `test_grid_2x2_default`: GET /review/{char_id}?asset_type=expression&batch=true → grid=2x2 (default), verify template context has grid_cols=2, grid_capacity=4
    - `test_grid_3x3`: GET /review/{char_id}?asset_type=expression&batch=true&grid=3x3 → grid_cols=3, grid_capacity=9
    - `test_grid_4x4`: GET /review/{char_id}?asset_type=expression&batch=true&grid=4x4 → grid_cols=4, grid_capacity=16
    - `test_grid_invalid_fallback`: GET /review/{char_id}?grid=5x5 → falls back to 2x2 default
    - `test_grid_non_batch_ignores_grid`: GET /review/{char_id}?grid=4x4 with batch=false → grid param ignored, normal display
    
    Use the existing `conftest.py` fixtures for TestClient setup (follow patterns from other test files). The Review UI uses `create_app()` which can accept an `asset_repo` parameter — use the in-memory repo fixture.
    
    Mock character and asset data as needed (follow existing test patterns from test_review_ui.py patterns or test_asset_repository.py).
  </action>
  <verify>
    <automated>pytest tests/test_review_ui.py::TestReviewGridSizes --timeout=30 -x -v</automated>
  </verify>
  <done>
    - /review/{character_id}?asset_type=expression&batch=true&grid=3x3 displays 9 candidates in 3 columns
    - /review/{character_id}?asset_type=expression&batch=true&grid=4x4 displays 16 candidates in 4 columns
    - /review/{character_id}?asset_type=expression&batch=true&grid=2x2 (default) displays 4 candidates in 2 columns
    - Grid selector buttons (2x2, 3x3, 4x4) appear in review controls in batch mode
    - Active grid button is visually highlighted
    - Batch card images scale proportionally with grid size
  </done>
  <acceptance_criteria>
    - `grid` query param accepted (default "2x2", valid values "2x2"/"3x3"/"4x4")
    - Grid size controls the number of candidates displayed (4/9/16) and column count (2/3/4)
    - Responsive CSS: mobile collapses to single column
    - All existing tests pass
  </acceptance_criteria>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Browser → Review UI (HTTP) | Localhost-only traffic — no network exposure |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-01b-04 | Tampering | Review UI POST actions | low | accept | Actions are POST handlers that call repo.update_state() with validated transitions. Error handling catches bad transitions. Single-operator internal tool on localhost. |
| T-01b-05 | Information Disclosure | Redirect URL in referer header | low | accept | Redirect uses request.headers.get("referer", "/") — no sensitive data in URLs (asset IDs are UUIDs, not sequential). |
| T-01b-06 | Denial of Service | Regenerate action creates unlimited JobQueue entries | low | accept | Regenerate is a convenience action that creates at most 6 seeds per call. No rate limiting needed for internal tool. |
| T-01b-SC | Tampering | No new package installs | low | accept | No pip installs in this plan. |
</threat_model>

<verification>
1. All existing tests pass: `pytest tests/ --timeout=60 -x -v`
2. Review UI action handlers produce correct state transitions
3. Grid sizes properly restrict candidate display count
</verification>

<success_criteria>
1. Four POST handlers wired to real SQLiteAssetRepository.update_state() calls
2. Grid parameter controls column count and candidate count in batch mode
3. CSS dynamically adjusts placeholder image sizes per grid size
4. All existing tests pass
</success_criteria>

<output>
Create `.planning/phases/01b-character-asset-production/01b-02-SUMMARY.md` when done.
</output>
