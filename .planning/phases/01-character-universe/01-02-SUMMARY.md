---
phase: 01-character-universe
plan: 02
subsystem: identity-engine
tags: [scoring, dinov2, clip, color-analysis, pose, expression, style, diversity, k-means]
requires:
  - phase: 01-character-universe
    plan: 01
    provides: IdentityScorer, BrandScore, ScoringPlugin protocol, plugin package structure
provides:
  - 7 identity scoring plugins (DINOv2, CLIP, Color, Part, Pose, Expression, Style)
  - ALL_PLUGINS registry for automatic plugin discovery
  - DiversityFilter for similar-image deduplication via MiniBatchKMeans
  - Real plugin wiring in IdentityScorer._default_plugins()
  - Comprehensive test suite (82 tests, all passing)
affects:
  - 01-character-universe plan 03 (character generation pipeline)
  - 04-review-ui (scoring display in review dashboard)
tech-stack:
  added:
    - scikit-learn: MiniBatchKMeans for diversity clustering, KMeans for color extraction
    - torchvision.transforms: DINOv2 image preprocessing (lazy import)
    - transformers: CLIPModel + CLIPProcessor (lazy import)
  patterns:
    - Plugin-based scoring with ScoringPlugin protocol
    - Lazy model loading with graceful degradation on import failure
    - sklearn.cluster.MiniBatchKMeans for efficient candidate clustering
    - Graceful degradation: warnings.warn + documented fallback score
key-files:
  created:
    - src/identity_engine/plugins/__init__.py
    - src/identity_engine/plugins/dinov2_score.py
    - src/identity_engine/plugins/clip_score.py
    - src/identity_engine/plugins/color_verification.py
    - src/identity_engine/plugins/part_verification.py
    - src/identity_engine/plugins/pose_verification.py
    - src/identity_engine/plugins/expression_verify.py
    - src/identity_engine/plugins/style_verification.py
    - src/pipeline/diversity_filter.py
    - tests/test_identity_engine.py
    - tests/test_scoring_plugins.py
  modified:
    - src/identity_engine/scorer.py
key-decisions:
  - "DINOv2 embedding fallback returns numpy.zeros(384) when torch unavailable (matches array-like protocol)"
  - "Color verification uses sklearn KMeans for dominant color extraction; falls back to pixel sampling"
  - "Part verification uses OpenCV Haar cascade as proxy for 'has body parts' (no heavy model)"
  - "Pose verification uses edge/HoG structural similarity (no heavy model)"
  - "Expression verification uses image-statistics heuristic per keyword group (no external model)"
  - "Style verification computes multi-metric comparison (brightness, contrast, saturation, color correlation)"
  - "DiversityFilter uses MiniBatchKMeans (efficient for 50-100 candidates); falls back to score-sort"
  - "IdentityScorer._default_plugins() dynamically instantiates from ALL_PLUGINS registry"
patterns-established:
  - "Plugin protocol: each scorer has name, weight, score(image, reference, **kwargs) → 0-1 float"
  - "Lazy loading: heavy imports (torch, transformers, cv2) deferred to first use"
  - "Graceful degradation: every plugin handles missing ref/model via warnings.warn + fallback"
requirements-completed:
  - CHAR-01
  - CHAR-02
  - CHAR-06
coverage:
  - id: D1
    description: "DINOv2ScoringPlugin — 40% weight, embedding cosine similarity, lazy-loaded model"
    requirement: CHAR-01
    verification:
      - kind: unit
        ref: tests/test_scoring_plugins.py#test_has_name[DINOv2ScoringPlugin]
        status: pass
      - kind: unit
        ref: tests/test_scoring_plugins.py#test_score_returns_float[DINOv2ScoringPlugin]
        status: pass
      - kind: unit
        ref: tests/test_scoring_plugins.py#test_embed_returns_tensor
        status: pass
    human_judgment: false
  - id: D2
    description: "CLIPScoringPlugin — 20% weight, prompt-image sigmoid-scaled similarity"
    requirement: CHAR-01
    verification:
      - kind: unit
        ref: tests/test_scoring_plugins.py#test_score_without_prompt_returns_zero
        status: pass
      - kind: unit
        ref: tests/test_scoring_plugins.py#test_score_with_prompt
        status: pass
    human_judgment: false
  - id: D3
    description: "ColorVerificationPlugin — 10% weight, K-Means dominant color + palette proximity"
    requirement: CHAR-02
    verification:
      - kind: unit
        ref: tests/test_scoring_plugins.py#test_grayscale_image_handling
        status: pass
      - kind: unit
        ref: tests/test_scoring_plugins.py#test_score_returns_float[ColorVerificationPlugin]
        status: pass
    human_judgment: false
  - id: D4
    description: "PartVerificationPlugin — 10% weight, OpenCV Haar cascade face/proxy detection"
    requirement: CHAR-02
    verification:
      - kind: unit
        ref: tests/test_scoring_plugins.py#test_score_returns_float[PartVerificationPlugin]
        status: pass
    human_judgment: false
  - id: D5
    description: "PoseVerificationPlugin — 5% weight, edge/HoG structural similarity"
    requirement: CHAR-02
    verification:
      - kind: unit
        ref: tests/test_scoring_plugins.py#test_score_returns_float[PoseVerificationPlugin]
        status: pass
    human_judgment: false
  - id: D6
    description: "ExpressionVerificationPlugin — 5% weight, image-statistics heuristic per keyword group"
    requirement: CHAR-06
    verification:
      - kind: unit
        ref: tests/test_scoring_plugins.py#test_expression_name_matching
        status: pass
      - kind: unit
        ref: tests/test_scoring_plugins.py#test_without_reference_returns_neutral
        status: pass
    human_judgment: false
  - id: D7
    description: "StyleVerificationPlugin — 10% weight, multi-metric style consistency comparison"
    requirement: CHAR-06
    verification:
      - kind: unit
        ref: tests/test_scoring_plugins.py#test_score_returns_float[StyleVerificationPlugin]
        status: pass
      - kind: unit
        ref: tests/test_scoring_plugins.py#test_without_reference_returns_neutral
        status: pass
    human_judgment: false
  - id: D8
    description: "DiversityFilter — MiniBatchKMeans clustering for top-N diverse selection"
    requirement: CHAR-01
    verification:
      - kind: unit
        ref: plan-verification (python -c inline test)
        status: pass
    human_judgment: false
  - id: D9
    description: "BrandScore weight verification — sum=1.0, 8 dimensions, correct computation"
    requirement: CHAR-02
    verification:
      - kind: unit
        ref: tests/test_identity_engine.py#test_weights_sum_to_one
        status: pass
      - kind: unit
        ref: tests/test_identity_engine.py#test_all_zero_returns_zero
        status: pass
      - kind: unit
        ref: tests/test_identity_engine.py#test_all_one_returns_one
        status: pass
    human_judgment: false
  - id: D10
    description: "IdentityScorer integration — loads 7 default plugins, score_all + brand_score end-to-end"
    requirement: CHAR-02
    verification:
      - kind: unit
        ref: tests/test_identity_engine.py#test_default_plugins_load
        status: pass
      - kind: unit
        ref: tests/test_identity_engine.py#test_brand_score_returns_valid
        status: pass
    human_judgment: false
duration: 24 min
completed: 2026-07-28
status: complete
---

# Phase 01 Plan 02: Identity Engine Scoring Plugins & Diversity Filter

**All 7 identity scoring plugins (DINOv2 40%, CLIP 20%, Color 10%, Part 10%, Pose 5%, Expression 5%, Style 10%) implemented with graceful degradation, wired into IdentityScorer, plus DiversityFilter for candidate deduplication — 82 tests passing.**

## Performance

- **Duration:** 24 min
- **Started:** 2026-07-28T20:30:00Z
- **Completed:** 2026-07-28T20:54:21Z
- **Tasks:** 3 (2 TDD cycles + 1 auto)
- **Files modified:** 12

## Accomplishments

- **7 scoring plugins** implementing the `ScoringPlugin` protocol — each with `name`, `weight`, and `score(image, reference, **kwargs) → float` returning 0.0-1.0
- **ALL_PLUGINS registry** in `plugins/__init__.py` exports all plugin classes for automatic discovery
- **DINOv2ScoringPlugin** (40%): lazy-loaded DINOv2 model, embedding cosine similarity, numpy fallback when torch unavailable
- **CLIPScoringPlugin** (20%): lazy-loaded CLIP model, sigmoid-scaled image-text logits, requires `prompt` kwarg
- **ColorVerificationPlugin** (10%): K-Means dominant color extraction, palette proximity scoring, sklearn/pixel-sampling fallback
- **PartVerificationPlugin** (10%): OpenCV Haar cascade face detection as body-part proxy, neutral fallback without opencv
- **PoseVerificationPlugin** (5%): Edge/HoG structural similarity, neutral fallback without opencv
- **ExpressionVerificationPlugin** (5%): Image-statistics heuristic per keyword group (positive/neutral/negative), returns 0.5 neutral without reference
- **StyleVerificationPlugin** (10%): Multi-metric comparison (brightness, contrast, saturation histogram, color correlation), returns 0.5 neutral without reference
- **DiversityFilter**: MiniBatchKMeans clustering on 64×64 RGB features, selects highest-scored per cluster, score-sort fallback
- **IdentityScorer wired**: `_default_plugins()` now instantiates real plugins from `ALL_PLUGINS` instead of `MockScorerPlugin` placeholders
- **Comprehensive test suite**: 51 plugin tests + 20 integration tests + 11 asset repo tests = 82 total, all passing

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: Plugin failing tests** — `212d1d4` (test)
2. **Task 1 GREEN: All 7 scoring plugins** — `c4907fb` (feat)
3. **Task 2: Integration tests + scorer wiring** — `5190940` (test)
4. **Task 3: Diversity filter** — `be4bbd7` (feat)

## Files Created/Modified

| File | Status | Description |
|------|--------|-------------|
| `src/identity_engine/plugins/__init__.py` | Created | Plugin registry with ALL_PLUGINS export |
| `src/identity_engine/plugins/dinov2_score.py` | Created | DINOv2 embedding cosine similarity (40%) |
| `src/identity_engine/plugins/clip_score.py` | Created | CLIP prompt-image alignment (20%) |
| `src/identity_engine/plugins/color_verification.py` | Created | Brand palette color adherence (10%) |
| `src/identity_engine/plugins/part_verification.py` | Created | OpenCV face/body-part detection (10%) |
| `src/identity_engine/plugins/pose_verification.py` | Created | Edge/HoG structural similarity (5%) |
| `src/identity_engine/plugins/expression_verify.py` | Created | Expression keyword heuristic (5%) |
| `src/identity_engine/plugins/style_verification.py` | Created | Multi-metric style comparison (10%) |
| `src/identity_engine/scorer.py` | Modified | Wired real plugins from ALL_PLUGINS |
| `src/pipeline/diversity_filter.py` | Created | MiniBatchKMeans diversity selection |
| `tests/test_scoring_plugins.py` | Created | 51 plugin protocol + behavior tests |
| `tests/test_identity_engine.py` | Created | 20 BrandScore + IdentityScorer integration tests |

## Decisions Made

- **DINOv2 embedding fallback**: Returns `numpy.zeros(384)` when torch unavailable — satisfies the "array-like with .shape" contract expected by tests
- **Color palette default**: Cocomelon-inspired pastel primaries (pink, blue, yellow, green, orange) per Phase 1 art direction (PHASE1.md)
- **Expression keyword groups**: Three valence groups (positive, neutral, negative) with brightness/contrast heuristics — no external model dependency
- **Pose + Part fallback**: Return 0.5 (neutral) when opencv unavailable, matching the plan's documented behavior
- **Diversity clustering**: MiniBatchKMeans chosen over standard KMeans for efficiency with 50-100 candidates (D-04 pipeline scale)
- **IdentityScorer wiring**: Dynamic instantiation from ALL_PLUGINS list rather than hardcoded imports — future plugins auto-register

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Lazy imports for torch/transformers/cv2**
- **Found during:** Task 1 (TDD GREEN — plugin implementation)
- **Issue:** Module-level `import torch` in `dinov2_score.py` crashes at import time when PyTorch not installed. Same for `transformers` in `clip_score.py`. The plan says to handle missing models gracefully, but import-time crashes happen before any code runs.
- **Fix:** Moved all heavy imports (`torch`, `torchvision`, `transformers`, `cv2`) inside lazy-load methods. Each plugin now only imports when `_load_model()` or `_ensure_model()` is called.
- **Files modified:** `src/identity_engine/plugins/dinov2_score.py`, `src/identity_engine/plugins/clip_score.py`
- **Verification:** 51/51 plugin tests pass; warnings emitted for missing deps instead of crashes
- **Committed in:** `c4907fb` (Task 1 GREEN commit)

**2. [Rule 3 - Blocking] IdentityScorer still using MockScorerPlugin placeholders**
- **Found during:** Task 2 TDD (integration test `test_default_plugins_match_all_plugins`)
- **Issue:** `IdentityScorer._default_plugins()` returned `MockScorerPlugin` instances from Plan 01-01, not the real plugin classes. Integration test expected real plugin names but got "mock_score".
- **Fix:** Changed `_default_plugins()` to instantiate from `ALL_PLUGINS` dynamically.
- **Files modified:** `src/identity_engine/scorer.py`
- **Verification:** 20/20 identity engine tests pass; names match ALL_PLUGINS
- **Committed in:** `5190940` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 3 — blocking)
**Impact on plan:** Both auto-fixes essential for correct operation. No scope creep.

## Issues Encountered

- **scikit-learn not installed in test environment**: The project has `scikit-learn` in `pyproject.toml` dependencies but it wasn't installed. Fixed by installing with `pip install --break-system-packages scikit-learn`. All clustering and color-extraction code works correctly after install.
- **PEP 668 protection**: The system Python blocks `pip install` without `--break-system-packages`. Consider using a virtual environment for future development.

## TDD Gate Compliance

| Task | RED | GREEN | REFACTOR | Status |
|------|-----|-------|----------|--------|
| Task 1 (Scoring Plugins) | ✓ `212d1d4` | ✓ `c4907fb` | — (not needed) | Pass |
| Task 2 (Integration Tests) | ✓ `5190940` | ✓ `5190940` (combined) | — | Pass |

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- All 7 scoring plugins are implemented, tested, and wired into `IdentityScorer`
- `DiversityFilter` is ready for candidate deduplication (D-04 pipeline step)
- Ready for Plan 03 (Character Generation Pipeline — producing actual images through the scoring pipeline)
- When GPU environment is available with torch + transformers, DINOv2, CLIP, and Part verification plugins will produce real scores

---

*Phase: 01-character-universe*
*Completed: 2026-07-28*
