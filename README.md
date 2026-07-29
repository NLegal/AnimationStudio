# AI Nursery Rhyme Studio — Character System

Character consistency & asset reusability across every episode.

## Project Structure

```
src/
├── models/schemas.py           # Data models (Character, GenerationOutput, etc.)
├── asset_repository/           # SQLite-backed asset CRUD + migrations
├── generation_engine/          # 5 backends: Flux, SDXL, Pony, Cloud API, ComfyUI
├── identity_engine/            # Weighted scoring pipeline + 7 plugins + diversity filter
│   └── plugins/                # DINOv2(40%), CLIP(20%), Color, Part, Pose, Expression, Style
├── pipeline/                   # JobQueue + GenerationJob orchestrator
├── prompt_builder/             # Template system + variants + negative prompts
├── training_engine/            # Kohya SS LoRA training adapter
└── review_ui/                  # FastAPI + Jinja2 web UI for asset review
```

## Running the UI

The Review UI is a FastAPI app with server-rendered HTML.

```bash
# Install dependencies
pip install -e ".[dev]"

# Start the review server
uvicorn src.review_ui:create_app --factory --reload --port 8000
```

Then open http://localhost:8000.

The app starts with an in-memory stub (no database required). Dashboard, character detail, and side-by-side review pages all render with placeholder data. To inject real data, pass an `asset_repo` to `create_app()`.

**Available routes:**

| Route | Page |
|-------|------|
| `/` | Dashboard — character list with pending counts |
| `/character/{id}` | Character detail — bio + assets grouped by type |
| `/review/{id}?asset_type=` | Side-by-side review with Brand Scores |
| `/review/{id}?asset_type=&batch=true` | 2×2 batch compare mode |
| `POST /approve/{id}` | Approve a candidate |
| `POST /reject/{id}` | Reject with reason |
| `POST /regenerate/{id}` | Queue similar regeneration |
| `POST /promote/{id}` | Promote to production |

## Validating the Work

### Run all tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run full suite
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ -v --tb=short -x
```

Expected: **156 tests passing** (8 warnings for optional deps `torch`, `cv2`).

### CI-friendly check

```bash
python -m pytest tests/ -x --quiet
```

### What's tested

| File | Tests |
|------|-------|
| `test_scoring_plugins.py` | All 7 plugins — protocol compliance, graceful degradation without torch/cv2 |
| `test_identity_engine.py` | IdentityScorer wiring, weighted composition, DiversityFilter clustering |
| `test_asset_repository.py` | SQLite CRUD, schema migrations |
| `test_generation_engine.py` | Backend ABC compliance, lazy loading, graceful error handling |
| `test_prompt_builder.py` | Template expansion, age/rotation/lighting variants |
| `test_training_engine.py` | Kohya SS adapter, environment validation |
| `test_character_bio.py` | Lily Bunny bio schema validation (9 tests) |

### Manual validation

```bash
# 1. Verify imports (all modules load without torch/cv2)
python -c "from src.models.schemas import Character; print('models OK')"
python -c "from src.identity_engine import IdentityScorer; print('identity engine OK')"
python -c "from src.generation_engine import FluxBackend; print('backends OK')"

# 2. Start UI and check all 3 pages render
uvicorn src.review_ui:create_app --factory --port 8000 &
curl -s http://localhost:8000/ | head -5
curl -s http://localhost:8000/character/test-char | head -5
curl -s http://localhost:8000/review/test-char | head -5
kill %1 2>/dev/null

# 3. Verify project structure is intact
python -c "
from src.pipeline import JobQueue, GenerationJob, DiversityFilter
from src.prompt_builder import PromptBuilder
from src.training_engine import KohyaSSAdapter
from src.asset_repository import SQLiteAssetRepository
print('All pipeline modules OK')
"
```

### Environment

Copy `.env.example` to `.env` and set API keys for cloud generation backends. The system works without any keys — local backends (Flux, SDXL, Pony) will warn about missing `torch` and use mock/fallback values during testing.

## Architecture

```
[PromptBuilder] → [GenerationBackend] → [IdentityScorer]
                                          ↓
                              [DiversityFilter]
                                          ↓
                              [AssetRepository]
                                          ↓
                              [Review UI] ← human
```

The pipeline runs as a `GenerationJob` — each variant goes through generate → score → filter → save → shortlist. Partial failures are isolated per variant.
