---
phase: 01b
plan: 02
completed_at: "2026-07-29T05:35:00Z"
duration: ~45min
tasks_total: 2
tasks_completed: 2
state: complete
---

## Plan 01b-02: Review UI Wiring — Summary

**Objective:** Wire Review UI action handlers to real SQLiteAssetRepository and add configurable batch grid sizes.

### Tasks

1. **Wire Review UI action handlers to SQLiteAssetRepository with D-15 lifecycle transitions** — Replaced four stub action handlers with real implementations:
   - `/approve`: shortlisted → approved via `repo.update_state()`
   - `/reject`: scored/shortlisted → draft with optional reason logging
   - `/regenerate`: JobQueue entry with nearby seeds [seed±1,±3,±5]
   - `/promote`: two-step shortlisted → approved → production
   - Added `NotFoundError` and `ValueError` error handling (catch → redirect)
   - Added `_get_referer(request)` helper, `Request` parameter to all handlers
   - Added optional `job_queue` parameter to `create_app()` factory
   - Kept `_StubAssetRepo` as fallback

2. **Add configurable batch grid sizes (3x3, 4x4) per D-16** — Added `grid` Query parameter to review_page route (default 2x2):
   - Normalises unrecognised grid values to 2x2
   - Updated starlette TemplateResponse calls to `(request, name, context)` API
   - Disabled Jinja2 cache (`cache_size=0`) for starlette 1.3.1 compat
   - Added grid selector UI with 2x2/3x3/4x4 buttons in review.html
   - Added `.grid-3x3` and `.grid-4x4` CSS classes with responsive breakpoints
   - Created `TestReviewGridSizes` test class (6 tests)

### Self-Check: PASSED

- All 6 grid tests pass
- Handler implementations verified against lifecycle transitions per D-15

### Key Files

- `src/review_ui/app.py` — wired action handlers + grid query parameter
- `src/review_ui/templates/review.html` — dynamic grid classes, grid selector UI
- `src/review_ui/static/style.css` — grid-columns classes
- `tests/test_review_ui.py` — TestReviewGridSizes (6 tests)
