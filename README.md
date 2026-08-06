# AI Nursery Rhyme Studio

A fully AI-powered production pipeline for generating unlimited, high-quality,
Cocomelon-style nursery rhyme videos with consistent characters, reusable
assets, and minimal manual work — from story to publishing.

## Status

All 12 phases implemented and audited. **1435 tests** (1432 passing; the
3 slow universe-seed/review-UI tests pass in isolation but exceed the 30s
global timeout under full-suite load).

| Phase | System | Module |
|-------|--------|--------|
| 1 | Universe Creation & Character Bible | `models`, `identity_engine` |
| 2 | World Building & Environment Bible | `identity_engine` |
| 3 | Global Asset Library & Production Kit | `asset_repository` |
| 4 | Animation Bible & Motion System | `generation_engine`, `prompt_builder` |
| 5 | Audio Bible & Music Production System | `training_engine` |
| 6 | Story Engine & Narrative Intelligence | `story_engine` |
| 7 | Production Planning & Storyboard System | `production` |
| 8 | AI Image Generation & Visual Asset Pipeline | `image_generation` |
| 9 | AI Animation Pipeline & Motion Generation | `animation` |
| 10 | Post-Production, Editing & Mastering | `post_production` |
| 11 | Publishing, Distribution & Channel Management | `publishing` |
| 12 | Studio Automation & AI Orchestration | `studio` |

## Project Structure

```
src/
├── models/                   # Data models (Character, Asset, GenerationOutput)
├── identity_engine/          # Weighted identity scoring + 7 plugins + brand score
├── asset_repository/         # SQLite-backed asset CRUD + migrations
├── generation_engine/        # 5 backends: Flux, SDXL, Pony, Cloud API, ComfyUI
├── prompt_builder/           # Template system + variants + negative prompts
├── training_engine/          # Kohya SS LoRA adapter + dataset builder + benchmark
├── story_engine/             # Narrative intelligence: story/theme/plot/dialogue/song/curriculum
├── production/               # Episodes, scenes, shots, manifests, continuity, render queue
├── image_generation/         # ConsistencyManager, model roles, prompt versioning, thumbnails
├── animation/                # Character/crowd/scene animation, camera, lipsync, lighting, physics
├── post_production/          # Timeline, editing, transitions, color, subtitles, QC, exports
├── publishing/               # Metadata, compliance, scheduling, localization, analytics, channels
├── studio/                   # Orchestrator, workflow, agents, tasks, scheduler, quality gate, security
├── universe/                 # Catalog parsing + seeding + batch generation (characters/worlds/props)
├── review_ui/                # FastAPI + Jinja2 web UI for asset review & generation
└── pipeline/                 # JobQueue + GenerationJob orchestrator + diversity filter
```

## Installation

```bash
pip install -e ".[dev]"
```

Optional extras:
- `pip install -e ".[scoring]"` — aesthetics predictor + OpenCV for scoring plugins
- `pip install -e ".[comfyui]"` — ComfyUI backend support

## Running Tests

```bash
# Full suite (quiet)
python -m pytest tests/ -q

# Verbose with failure short-report
python -m pytest tests/ -v --tb=short

# Stop at first failure
python -m pytest tests/ -x --quiet
```

Expected: **1435 tests** (1432 passing; 3 slow seed/review tests exceed the
30s global timeout under full-suite load but pass in isolation). Optional
dependencies (`torch`, `cv2`, `timm`,
aesthetics predictor) are lazily loaded — the suite passes without them via
mock/fallback values.

### Test coverage by module

| File | Covers |
|------|--------|
| `test_studio.py` | Orchestrator, workflow, agents, tasks, quality, security, recovery, backup, plugins, dashboards, API |
| `test_publishing.py` | Metadata, compliance, scheduling, localization, analytics, archive, channels, lifecycle |
| `test_post_production.py` | Timeline, editing, color, subtitles, QC, exports, localization, archive |
| `test_animation.py` | Character/crowd/scene motion, camera, lipsync, lighting, physics, render, validation |
| `test_image_generation.py` | Consistency, model roles, prompt versioning, thumbnail, upscaler, validator |
| `test_story_engine.py` | Story/theme/plot/dialogue/song/curriculum generation, validation, continuity |
| `test_production.py` | Episodes, scenes, shots, manifests, continuity, render queue, QC |
| `test_story_to_production_integration.py` | End-to-end story → production flow |
| `test_prompt_builder.py` | Template expansion, age/rotation/lighting variants + environment/vehicle/background templates |
| `test_animation_bible.py` | Animation Bible & Motion System — cycle library, expressions, blinks, gestures, camera/transitions, physics, prompt templates, doc↔code consistency |
| `test_audio_bible.py` | Audio Bible & Music Production System — song categories/structure/durations, voice profiles, dialogue, pronunciation, SFX/foley/ambience, mixing/mastering, localization, prompt templates, doc↔code consistency |
| `test_generation_engine.py` | Backend ABC compliance, lazy loading, graceful errors |
| `test_identity_engine.py` | IdentityScorer wiring, weighted composition, DiversityFilter |
| `test_scoring_plugins.py` | All 7 plugins — protocol compliance, degradation without torch/cv2 |
| `test_asset_repository.py` | SQLite CRUD, schema migrations |
| `test_training_engine.py` | Kohya SS adapter, environment validation |
| `test_lora_training.py` | Dataset builder, versioning, benchmark |
| `test_review_ui.py` | Review app routes |
| `test_review_ui_generation.py` | UI generation panel, seeding, per-category detail pages |
| `test_universe_catalog.py` | Universe/World/Assets markdown parsing (39 chars, 9 zones, 130 locations, 20 vehicles, 26 backgrounds, 1,523 props) |
| `test_universe_seed.py` | Idempotent, self-healing seeding keyed by permanent asset_id |
| `test_batch_generator.py` | Prompt building + mock end-to-end batch generation (incl. prop variants) |
| `test_character_bio.py` | Lily Bunny bio schema validation |

## Running the Review UI

The Review UI is a FastAPI app with server-rendered HTML for reviewing
generated character assets.

```bash
uvicorn src.review_ui:create_app --factory --reload --port 8000
```

Then open http://localhost:8000.

By default the app wires itself to the SQLite database (`catalog.db` in the
working directory), auto-seeds the universe catalog on first load, and uses
the mock generation backend — so the dashboard lists the provisioned
characters/environments/props immediately and the Generate panel works with
no extra configuration.  To run against a specific database, start from the
directory that contains it, or pass an explicit `asset_repo`/`character_repo`
to `create_app()`.

**Available routes:**

| Route | Page |
|-------|------|
| `/` | Dashboard — characters, environments, props, jobs, generate panel, activity log |
| `/character/{id}` | Character detail — bio + assets grouped by type |
| `/review/{id}?asset_type=` | Side-by-side review with Brand Scores |
| `/review/{id}?asset_type=&batch=true` | 2×2 batch compare mode |
| `POST /approve/{id}` | Approve a candidate |
| `POST /reject/{id}` | Reject with reason |
| `POST /regenerate/{id}` | Queue similar regeneration |
| `POST /promote/{id}` | Promote to production |
| `POST /generate` | Queue a background generation batch (scope/item/backend) |
| `POST /seed` | Seed the universe catalog from the markdown docs (idempotent) |
| `/logs` | Recent activity log entries (JSON, polled by the dashboard) |

## Universe Generation

The Phase 1–3 universe content (39 character bios, 9 world zones, **1,523
reusable props** across 20 asset categories) lives as markdown under
`Universe/`, `World/`, and `Assets/`. Two scripts turn those documents into a
populated, reviewable studio database — no GPU required (a deterministic mock
backend is the default).

```bash
# 1. Seed the catalog from the markdown docs (idempotent, self-healing)
python scripts/seed_universe.py --db catalog.db

# 2. Generate candidates with the mock backend (no hardware)
python scripts/generate_universe.py --scope characters --backend mock --count 8
python scripts/generate_universe.py --scope environments --backend mock --count 4
python scripts/generate_universe.py --scope props --backend mock --count 4 --limit 20

# 3. Preview the exact prompts without generating
python scripts/generate_universe.py --scope all --prompt-only --limit 3

# 4. Generate then start the Review UI against the same database
python scripts/generate_universe.py --scope all --backend mock --serve --port 8000
```

### Phase 3 — Global Asset Library & Production Kit

The reusable production prop library (12,184 approved assets: references,
turnaround views, material/color variants, and lighting studies for all 1,523
props) is produced and maintained by the Phase 3 pipeline:

```bash
# Generate every prop variant (idempotent — existing variants are skipped)
python scripts/generate_phase3_assets.py --db catalog.db \
    --count 2 --shortlist 1 --fast-scoring --jobs 8

# Export PNGs to Assets/<Category>/{references,views,materials,colors,lighting}/
python scripts/export_assets.py --db catalog.db --scope props

# Compose labeled reference sheets and approve the whole library
python scripts/build_asset_sheets.py --db catalog.db
python scripts/finalize_phase1.py --db catalog.db --all
```

The library lands at `Assets/<CategoryDir>/{references,views,materials,colors,
lighting}/` with a composed reference sheet per prop under
`Assets/ReferenceSheets/<CategoryDir>/`. Supporting production kit docs live in
`Assets/` (`Assets/Metadata/METADATA_GUIDE.md`,
`Assets/ReferenceSheets/{Scale,Color,Material}/*.md`,
`Assets/PromptTemplates/`, `Assets/NegativePrompts/`). See `PHASE3_STATUS.md`.

Real backends swap in via `--backend`:

| Backend | Notes |
|---------|-------|
| `mock` | Deterministic placeholder images — works offline, ideal for tests/UI |
| `comfyui` | Requires ComfyUI at `localhost:8188` with Flux installed (`--comfyui-url`) |
| `cloud` | Requires `FAL_API_KEY` / `REPLICATE_API_KEY` / `BFL_API_KEY` (`--provider`) |

The UI generation panel (dashboard → **Generate Assets**) queues the same
pipeline in the background: prompt → generate → identity score → diversity
filter → shortlist. Generated candidates land in the database and appear under
"Pending Review" for approval.

## Phase 1 Character Library

`scripts/generate_phase1_library.py` produces the full Phase 1 per-character
library from `PHASE1.md` — reference sheets, every expression, every pose,
every wardrobe outfit, turnarounds, and lighting studies — for every character:

```bash
# Generate the complete library for all 39 characters (mock backend)
python scripts/generate_phase1_library.py --fast-scoring --jobs 12

# Subset / filters
python scripts/generate_phase1_library.py --characters "Lily Bunny" --asset-types expressions
python scripts/generate_phase1_library.py --asset-types turnarounds,lighting

# Preview prompts only
python scripts/generate_phase1_library.py --prompt-only --limit 3

# Real backends
python scripts/generate_phase1_library.py --backend comfyui
python scripts/generate_phase1_library.py --backend cloud --provider fal
```

`--fast-scoring` skips the torch-backed scoring plugins (DINOv2/CLIP), which
are the runtime bottleneck and add nothing for deterministic mock placeholders
(≈60× faster on CPU).

The pipeline stores images in SQLite but not on disk. Two scripts turn the
database into the *organized asset repository* PHASE1.md requires:

```bash
# Reproduce each asset's PNG from its prompt+seed and record file_path
python scripts/export_assets.py --db catalog.db --scope characters

# Composite the turnarounds into a labeled model sheet per character
python scripts/build_model_sheets.py --db catalog.db

# Promote assets to "approved" (--all = full library; default = best reference)
python scripts/finalize_phase1.py --db catalog.db --all
```

Assets land under `Universe/Characters/<Name>/{references,expressions,poses,
outfits,turnarounds,lighting}` plus `Universe/ModelSheets/<Name>_model_sheet.png`.
Only the mock backend is reproducible offline — real-backend assets should have
a real `file_path` already recorded by the generation run.

### Windows command wrappers

Every `scripts/*.py` entry point ships a thin PowerShell + batch wrapper
(`scripts\<name>.ps1` / `scripts\<name>.bat`) that delegates to the generic
runner (`scripts\py.ps1` / `scripts\py.bat`). The runner resolves Python in
this order and runs the script from the project root:

1. `$env:PYTHON` (or `%PYTHON%`) — explicit override,
2. the Python 3.14 install in the user AppData layout
   (`C:\Users\<you>\AppData\Local\Programs\Python\Python314\python3.exe`,
   then `python.exe`), i.e. no PATH setup needed,
3. `python` / `python3` on PATH.

So the Windows command for any script is either the wrapper or the runner:

```powershell
# wrapper (PowerShell) / batch (cmd)
.\scripts\generate_phase1_library.ps1 --fast-scoring --jobs 12
scripts\generate_phase1_library.bat --fast-scoring --jobs 12

# generic runner — same thing, script name first
.\scripts\py.ps1 seed_universe --db catalog.db
scripts\py.bat export_assets --db catalog.db --scope all
```

### Run Phase 1 from scratch (both platforms)

The full Phase 1 pipeline, in order. These are the only commands you need.

**Windows (PowerShell):**

```powershell
cd <project-root>

# 0. Install (one-time)
.\scripts\py.ps1 -m pip install -e ".[dev]"

# 1. Seed the catalog from the markdown docs (idempotent)
.\scripts\seed_universe.ps1 --db catalog.db

# 2. Generate the complete Phase 1 library for all 39 characters
.\scripts\generate_phase1_library.ps1 --fast-scoring --jobs 12

# 3. Write PNGs to the asset repository + record file_path
.\scripts\export_assets.ps1 --db catalog.db --scope characters

# 4. Composite turnarounds into model sheets
.\scripts\build_model_sheets.ps1 --db catalog.db

# 5. Approve the library (--all = full library; default = best reference)
.\scripts\finalize_phase1.ps1 --db catalog.db --all

# 6. Review everything in the web UI
uvicorn src.review_ui:create_app --factory --reload --port 8000
#    → open http://localhost:8000
```

> `.\scripts\py.ps1 -m pip …` forwards `-m`/`pip` to the resolved Python;
> `py.bat` supports the same (`scripts\py.bat -m pip install -e ".[dev]"`).

**macOS / Linux (bash):**

```bash
cd <project-root>

python3 -m pip install -e ".[dev]"
python3 scripts/seed_universe.py --db catalog.db
python3 scripts/generate_phase1_library.py --fast-scoring --jobs 12
python3 scripts/export_assets.py --db catalog.db --scope characters
python3 scripts/build_model_sheets.py --db catalog.db
python3 scripts/finalize_phase1.py --db catalog.db --all
uvicorn src.review_ui:create_app --factory --reload --port 8000
```

> `--fast-scoring` skips the torch-backed DINOv2/CLIP plugins (≈60× faster) —
> fine for the mock pipeline. Drop it when scoring real generated images.

### Local generation (ComfyUI + Flux)

ComfyUI is the optional R&D backend for real (non-placeholder) images. Install
it plus the Q4 GGUF Flux model set with the platform setup script:

**Windows (PowerShell):**

```powershell
.\scripts\setup_comfyui_flux.ps1                  # install + download (~14GB)
.\scripts\setup_comfyui_flux.ps1 -Serve           # start the server on :8188 (CUDA)
.\scripts\setup_comfyui_flux.ps1 -Serve -Cpu      # CPU-only machines only
.\scripts\generate_phase1_library.ps1 --backend comfyui --comfyui-url http://localhost:8188
```

If PowerShell blocks the script, bypass for this session first:
`Set-ExecutionPolicy -Scope Process Bypass`.

**macOS / Linux (bash):**

```bash
bash scripts/setup_comfyui_flux.sh                # install + download (~14GB)
bash scripts/setup_comfyui_flux.sh --serve        # start the server on :8188
python3 scripts/generate_phase1_library.py --backend comfyui
```

The script clones ComfyUI into `tools/comfyui/` and downloads the GGUF model
set at the exact paths the workflow templates reference: the Flux unet
(`models/checkpoints/flux1-dev-Q4_K_S.gguf`), the text encoders
(`models/clip/clip_l.safetensors`, `models/clip/t5xxl_fp16.safetensors`), and
the VAE (`models/vae/ae.safetensors`). Workflows load them through the
`UnetLoaderGGUF` / `DualCLIPLoader` / `VAELoader` nodes (this requires the
`ComfyUI-GGUF` custom node, which the script does not install — add it to
`tools/comfyui/custom_nodes/` if missing).

We use the GGUF-quantized unet instead of the fp8 safetensors because fp8
weights have no CPU kernel in torch: on CPU-only installs (Intel/AMD iGPU
boxes ship a CPU-only torch build) ComfyUI crashes with a Windows access
violation while loading the checkpoint. GGUF loads as int4/bf16 and runs on
plain CPU. The server starts with CUDA by default when torch reports a GPU
(seconds per image); pass `-Cpu` (Windows) / `--cpu` (Linux) only on CPU-only
machines, where you should expect minutes per image and prefer the cloud
backends instead.

### Google Colab (GPU, optional)

Prefer real GPU hardware? Run the same ComfyUI pipeline on a Colab T4
(16 GB VRAM, free tier) with the included notebook:

```bash
# in the colab/ directory of this repo
colab/AnimationStudio_Colab.ipynb
```

The notebook clones the repo, installs ComfyUI, downloads the model into a
Drive-side cache, starts the server, runs Phase-1 generation, exports real
PNGs into your Drive, and launches the Review UI behind a LocalTunnel link.
Open it from GitHub via `colab.research.google.com -> File -> Open notebook ->
GitHub`, set `REPO_URL` in Cell 1, pick a GPU runtime, then `Runtime -> Run all`.

Branches pin the model flavor (the notebook selects it via its `BRANCH` cell):

| Branch | Model | Where it runs |
| --- | --- | --- |
| `master` | Q4 GGUF (`flux1-dev-Q4_K_S.gguf` + encoders/VAE, ~14 GB) | CPU box (Iris Xe), also T4 |
| `colab-gpu` | fp8 Flux bundle (`flux1-dev.safetensors`, ~12 GB) | Colab T4/L4/A100 |

Keep the free-tier scope small (`--count 2 --shortlist 1`, a couple of asset
types) — a T4 takes ~2 min per 1024×1024 image.

### Cloud generation (optional)

Set keys in `.env` (copy from `.env.example`), then use `--backend cloud`:

```powershell
# Windows (PowerShell)
$env:FAL_API_KEY = "<key>"          # or set in .env
.\scripts\generate_phase1_library.ps1 --backend cloud --provider fal
```

```bash
# macOS / Linux
FAL_API_KEY=<key> python3 scripts/generate_phase1_library.py --backend cloud --provider fal
```

Providers: `fal`, `replicate` (`REPLICATE_API_KEY`), `bfl` (`BFL_API_KEY`).

## Phase 2 World Library

`scripts/generate_phase2_world.py` builds the Phase 2 world library from the
zone bibles in `World/` — every named location (130 `ENV_*` seeds from the 9
zone docs), every vehicle (20), and every background layer (26) — with the
variant asset types PHASE2.md requires:

| Asset type | Variants | Count |
|------------|----------|-------|
| `exterior` | 7-view Home Library set for Residential homes; front view elsewhere | 280 |
| `interior` | varied room per location (living room, kitchen, classroom, …) | 130 |
| `season` | spring / summer / autumn / winter | 520 |
| `time_of_day` | morning / noon / golden_hour / night | 520 |
| `weather` | sunny / cloudy / rain / snow | 520 |
| `camera` | 10 angles (hero locations only) | 90 |
| `vehicle` | front + side | 40 |
| `background` | 1 per layer | 26 |

```bash
# Generate the complete world library (mock backend)
python scripts/generate_phase2_world.py --fast-scoring --jobs 12

# Subset / filters
python scripts/generate_phase2_world.py --zone Residential --asset-types seasons,weather
python scripts/generate_phase2_world.py --asset-types camera --zone Beach --count 1

# Preview prompts only
python scripts/generate_phase2_world.py --prompt-only --limit 3

# Real backends
python scripts/generate_phase2_world.py --backend comfyui
python scripts/generate_phase2_world.py --backend cloud --provider fal
```

Prompts are built with the zone-aware world style block and the shared
`ENVIRONMENT_NEGATIVE` (plus per-zone negatives) — see
`World/PromptTemplates/Environment/*.md`. Turn the database into the organized
`World/` repository:

```bash
# Reproduce each world asset's PNG from its prompt+seed and record file_path
python scripts/export_assets.py --db catalog.db --scope all

# Composite labeled environment + vehicle reference sheets
python scripts/build_world_sheets.py --db catalog.db

# Promote the library to "approved"
python scripts/finalize_phase1.py --db catalog.db --all
```

Assets land under `World/<Zone>/{exteriors,interiors,seasons,time_of_day,
weather,camera}/`, `World/Vehicles/`, and `World/Backgrounds/`, plus 150
reference sheets in `World/ReferenceSheets/`.

### Run Phase 2 from scratch (both platforms)

**Windows (PowerShell):**

```powershell
cd <project-root>

# 1. Seed the catalog from the markdown docs (idempotent)
.\scripts\seed_universe.ps1 --db catalog.db

# 2. Generate the complete world library (all 130 locations + vehicles + backgrounds)
.\scripts\generate_phase2_world.ps1 --fast-scoring --jobs 12

# 3. Write PNGs to the world asset repository + record file_path
.\scripts\export_assets.ps1 --db catalog.db --scope all

# 4. Composite labeled reference sheets
.\scripts\build_world_sheets.ps1 --db catalog.db

# 5. Approve the library
.\scripts\finalize_phase1.ps1 --db catalog.db --all

# 6. Review everything in the web UI
uvicorn src.review_ui:create_app --factory --reload --port 8000
```

**macOS / Linux (bash):**

```bash
cd <project-root>

python3 scripts/seed_universe.py --db catalog.db
python3 scripts/generate_phase2_world.py --fast-scoring --jobs 12
python3 scripts/export_assets.py --db catalog.db --scope all
python3 scripts/build_world_sheets.py --db catalog.db
python3 scripts/finalize_phase1.py --db catalog.db --all
uvicorn src.review_ui:create_app --factory --reload --port 8000
```

> `--fast-scoring` skips the torch-backed DINOv2/CLIP plugins (≈60× faster) —
> fine for the mock pipeline. Drop it when scoring real generated images.

For real images, use the same ComfyUI / cloud setup as Phase 1 above with
`--backend comfyui` / `--backend cloud` on `generate_phase2_world.py`.


## Production Pipeline API

The production layer exposes a FastAPI-style endpoint specification
(`src/production/api.py`) covering episodes, scenes, shots, manifests, prompt
generation, continuity validation, the render queue, and quality checks
(`POST /api/episodes`, `GET /api/render-queue`, `POST /api/quality-check`, …).

## Manual Validation

```bash
# 1. Verify core imports (no torch/cv2 required)
python -c "from src.models.schemas import CharacterModel; print('models OK')"
python -c "from src.identity_engine import IdentityScorer; print('identity engine OK')"
python -c "from src.generation_engine import FluxBackend; print('backends OK')"
python -c "from src.studio import PipelineOrchestrator; print('orchestrator OK')"
python -c "from src.publishing import PublishingEngine; print('publishing OK')"

# 2. Smoke-test the full pipeline in one line
python -c "
from src.story_engine import EpisodeGenerator
from src.production import ProductionPipeline
from src.studio import PipelineOrchestrator
orchestrator = PipelineOrchestrator(); orchestrator.setup_defaults()
orchestrator.create_pipeline('smoke-001')
print('pipeline smoke test OK')
"

# 3. Start UI and check all 3 pages render
uvicorn src.review_ui:create_app --factory --port 8000 &
curl -s http://localhost:8000/ | head -5
curl -s http://localhost:8000/character/test-char | head -5
curl -s http://localhost:8000/review/test-char | head -5
kill %1 2>/dev/null
```

## Architecture

```
[Story Engine] → [Production Planning] → [Image Generation] → [Animation]
        ↓                ↓                       ↓                ↓
   Curriculum      Episodes/Shots/       Consistency &       Character/Crowd/
   Validation      Manifests/QC         Model Roles          Scene Motion
        ↓                ↓                       ↓                ↓
        └────────[ Post-Production: Edit → Color → Subtitles → QC → Export ]────────┐
                                                                                    ↓
                       [ Publishing: Metadata → Compliance → Schedule → Localize → Publish ]
                                                                                    ↓
                   [ Studio Orchestration: Workflow → Tasks → Agents → Quality → Ops Dashboard ]
```

Each phase is an independent department. The Phase 12 `PipelineOrchestrator`
ties them together into an autonomous production platform: `EpisodeWorkflowFactory`
builds an 8-step workflow (story → storyboard → images → animation → edit → qc →
publish), `TaskQueue` schedules work, `WorkerPool` assigns it, `QualityGate`
validates every domain, and the event bus drives hand-offs.

## Environment

Copy `.env.example` to `.env` and set API keys for cloud generation backends.
The system works without any keys — local backends (Flux, SDXL, Pony) will warn
about missing `torch` and use mock/fallback values during testing.
