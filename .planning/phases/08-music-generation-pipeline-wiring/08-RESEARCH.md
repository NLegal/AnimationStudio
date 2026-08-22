# Phase 8: Music Generation Pipeline Wiring - Research

**Researched:** 2026-08-22
**Domain:** Internal wiring of the Phase 7 music-generation backend layer into the studio CLI (`scripts/generate_phase5.py`), Review UI (FastAPI), Colab notebook, and status docs
**Confidence:** HIGH (codebase patterns verified by direct inspection; external ACE-Step facts CITED from official sources)

## Summary

Phase 8 is a **pure wiring phase** — no new libraries, no new protocols, no REST contract changes. It consumes the locked `src/music_generation/` surface defined by the committed Phase 7 plans and connects it to four existing integration points: the Phase 5 report script, the FastAPI Review UI, the Colab notebook family, and `PHASE5_STATUS.md`. Every pattern this phase needs already exists in the codebase as a verified precedent: the `/motion` page + `POST /motion/prompt` pure-preview route pair (Phase 4 hooks in `src/review_ui/app.py:951–999`), the `BackgroundTasks` fire-and-forget batch pattern (`POST /generate`, app.py:1086–1111), the Colab notebook skeleton (`colab/AnimationStudio_Colab_Phase4.ipynb`, 9 cells, CPU-only offline run), and the script conventions of `scripts/generate_phase5.py` itself.

**⚠️ Critical sequencing fact:** `src/music_generation/` **does not exist yet** — Phase 7 plans (07-01, 07-02) are committed as planning docs only; git history shows zero implementation commits after `phase4`. This research therefore treats the Phase 7 public API surface as **locked-by-plan-contract** (verified verbatim from 07-01-PLAN.md / 07-02-PLAN.md must_haves and task actions). Phase 8 can be *planned* against that surface today, but **execution must be ordered after Phase 7 completes**. Every import listed below resolves once 07-02 lands.

**Primary recommendation:** Build three vertical deliverables in dependency order — (1) extend `generate_phase5.py` with a manifest-driven `--generate` mode that reuses the exact `build_music_request` → `backend.generate()` → `<category>-<topic-slug>-<seed>.wav` conventions of `scripts/generate_phase7.py`; (2) mirror the motion-page pattern for Review UI music hooks (`GET /music`, `POST /music/prompt` pure preview, `POST /music/generate` via BackgroundTasks + JobQueue tracking); (3) create `colab/AnimationStudio_Colab_Phase5.ipynb` mirroring the Phase 4 notebook's 9-cell structure plus an ACE-Step service-install cell for GPU runtimes. Update `PHASE5_STATUS.md` last.

## Carried Constraints (from ROADMAP Phase 7/8 briefs — treated as locked)

No CONTEXT.md exists for this phase (discuss-phase not run). These constraints carried through Phase 7 and bind Phase 8 equally; they come from the ROADMAP phase goals and Phase 7 plan Hard Constraints C1–C6 [VERIFIED: 07-01/07-02 plans]:

- **C2 (catalog.db):** The repo-root asset-catalog SQLite database is NEVER opened, written, or imported by music-generation code, CLIs, UI routes, or tests. Song artifacts live on disk under `Audio/Music/` with their own JSON manifest — explicitly NOT asset rows.
- **Offline-first:** ACE-Step is an EXTERNAL local service at `http://localhost:8001` (env-overridable) that our code never starts, installs, or requires. CI/tests never need it.
- **Mock default:** `get_backend(None)` resolves `MUSIC_BACKEND` env, falling back to `"mock"` — every wired entry point inherits this safe offline default.
- **Suno stays a stub:** `SunoBackend.is_configured()` is always False; every operation raises `NotConfigured` citing `.planning/research/MUSIC-GENERATION.md`. The experimental `SunoWrapperBackend` is unreachable through `get_backend` (locked invariant).
- **C4 (no new dependencies):** stdlib `urllib.request` transport only; pyproject.toml untouched. This phase adds ZERO packages.
- **C3 (tests offline):** No network I/O in tests — fake transport injection + fail-loud guards; no real audio generated anywhere in CI.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Batch song generation + manifest | Script tier (`scripts/generate_phase5.py`) | `src/music_generation/` backend layer | Batch orchestration, file layout, resume logic are operator-workflow concerns; actual generation stays behind the protocol |
| Music prompt preview | Frontend server (`review_ui/app.py` route) | Jinja2 template | Pure computation (bible prompt + params), rendered server-side like `POST /motion/prompt` — no DB, no network |
| Generation job queueing/status | Frontend server (`review_ui`) | In-memory `JobQueue` + `BackgroundTasks` | Mirrors existing `/generate` panel; jobs are ephemeral, results persist as files+manifest, never catalog.db |
| Offline ACE-Step run on Colab | Notebook cell (subprocess) | External ACE-Step service process | Service installs/runs in its own checkout/env; studio code talks to it over localhost HTTP only |
| Status documentation | Repo docs (`PHASE5_STATUS.md`) | — | Human-readable evidence trail, updated last |

## Standard Stack

### Core (all already installed — zero additions)

| Component | Version (verified local) | Purpose | Why Standard |
|-----------|--------------------------|---------|--------------|
| Python | 3.13.5 | Runtime (repo requires >=3.11) | `[VERIFIED: python3 --version]` |
| fastapi | 0.140.13 | Review UI routes + BackgroundTasks | `[VERIFIED: pip import]` existing dep |
| jinja2 | 3.1.6 | `music.html` template | `[VERIFIED: pip import]` existing dep |
| pydantic | 2.13.4 | MusicRequest/MusicResult models (Phase 7) | `[VERIFIED: pip import]` existing dep |
| uvicorn | 0.51.0 | Runs `src.review_ui:create_app --factory` | `[VERIFIED: pip import]` existing dep |
| pytest (+asyncio auto mode, 30 s timeout) | suite green locally | Test runner; config in pyproject `[tool.pytest.ini_options]` | `[VERIFIED: full-suite run this session]` |

### Consumed Phase 7 surface (locked contract — verify existence at execution time)

| Symbol | Source module | Contract notes |
|--------|---------------|----------------|
| `MusicRequest(category, topic="", duration_s=60[10–600], vocals="female lead vocal, children's choir", lyrics_override=None, seed=None, tags=[])` | `src.music_generation` | Pydantic v2; exactly seven fields [VERIFIED: 07-01 plan Task 1] |
| `MusicResult(request, audio: bytes, format: "wav"\|"mp3", job_id, backend, seed)` | `src.music_generation` | audio bytes written verbatim to disk [VERIFIED: 07-01 plan] |
| `build_music_request(category, topic="", *, vocals=…, mood="", seed=None, lyrics_override=None, tags=None, duration_s=None)` | `src.music_generation.backends` | Resolves category duration defaults (Alphabet 75, Numbers 75, Colors 60, Animals 80, Bedtime 120, generic 60); captions NOT baked in [VERIFIED: 07-01 plan Task 2] |
| `resolve_music_params(category)` → `CategoryMusicParams(bpm, key_scale, time_signature, lyric_structure, duration_s, caption_keyword)` | `src.music_generation.backends` | Case-insensitive; generic fallback row for unknown categories [VERIFIED: 07-01 plan] |
| `music_negative_prompt(category)` | `src.music_generation.backends` | Delegates to `audio_bible.prompts.category_negative(include_base=True)` [VERIFIED: 07-01 plan] |
| `get_backend(name=None, **kwargs)` | `src.music_generation` | Registry keys `"ace-step"`, `"suno"`, `"mock"`; None → `MUSIC_BACKEND` env → `"mock"`; unknown raises `MusicBackendError` listing valid names [VERIFIED: 07-02 plan Task 1] |
| `AceStepBackend(api_key=None, base_url=None, model=None, transport=None)` | `src.music_generation` | Credential order ctor > `ACESTEP_API_KEY` env; base falls back to `ACESTEP_BASE_URL` then `http://localhost:8001` [VERIFIED: 07-02 plan Task 1] |
| `MusicBackendError`, `NotConfigured`, `BackendUnavailable`, `GenerationFailed` | `src.music_generation` | Typed failure taxonomy; Suno raises NotConfigured always [VERIFIED: 07-01/02 plans] |
| `AudioBible().list_song_categories()` → 24 names | `src.audio_bible.bible` | Verified present: Alphabet … Dance Songs [VERIFIED: bible.py:51 + libraries.py:70–95] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Extending `generate_phase5.py` | New `generate_phase8.py` script | ROADMAP explicitly says "extend generate_phase5.py"; keeps one Phase-5 entrypoint whose verification mode keeps working unchanged |
| Celery/RQ/arq job workers | FastAPI `BackgroundTasks` + in-memory `JobQueue` | Existing house pattern; single-operator localhost tool; adding a broker violates the no-new-deps constraint |
| Writing songs into catalog.db | JSON manifest under `Audio/Music/` | Locked constraint C2 — catalog.db untouched; MUSIC-GENERATION.md §Risks #3 prescribes manifest+sidecar |
| `requests`/`httpx` in tests | `fastapi.testclient.TestClient` + fake transports | Already-used patterns; no new deps |

**Installation:** NONE. `pyproject.toml` must remain byte-identical after this phase (grep-gate).

## Package Legitimacy Audit

> No external packages are installed in this phase (constraint C4). The Package Legitimacy Gate has nothing to audit — same disposition as Phase 7 plans recorded ("zero packages installed … nothing to audit").

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| *(none — zero installs)* | — | — | — | — | — | n/a |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

Note: the Colab notebook clones the EXTERNAL `ACE-Step-1.5` service repo onto the Colab VM at runtime. That is operator-machine setup (like the ComfyUI install in the Phase 1 notebook), not a project dependency; it never enters pyproject.toml or CI.

## Architecture Patterns

### System Architecture Diagram

```
                         OPERATOR ENTRY POINTS
 ┌──────────────────┐  ┌───────────────────────┐  ┌─────────────────────────┐
 │ scripts/         │  │ Review UI (FastAPI)   │  │ colab/…Colab_Phase5     │
 │ generate_phase5  │  │ GET /music            │  │ .ipynb (Colab VM)       │
 │ .py --generate   │  │ POST /music/prompt    │  │                         │
 └────────┬─────────┘  │ POST /music/generate  │  └───────────┬─────────────┘
          │            │ GET /api/music/jobs   │              │ subprocess:
          │            └────────┬──────────────┘              │ python scripts/
          │                     │ BackgroundTasks             │ generate_phase5.py
          │                     ▼                             │ --generate --backend ace-step
          │            ┌──────────────────┐                   │
          └────────────►  get_backend()   ◄───────────────────┘
                        │  (registry)      │
                        └───┬──────┬───────┘
             "ace-step"     │      │ "mock"
                            ▼      ▼
        ┌────────────────────┐  ┌──────────────────────┐
        │ AceStepBackend     │  │ MockBackend           │
        │ submit/poll/downld │  │ deterministic WAV     │
        └─────────┬──────────┘  └──────────┬───────────┘
                  │ urllib (transport seam)│ (no I/O)
                  ▼                        │
        http://localhost:8001              │
        (EXTERNAL ACE-Step service         │
         — never started by us)            │
                  │                        │
                  ▼                        ▼
        ┌─────────────────────────────────────────────┐
        │ Audio/Music/                                │
        │   <category>-<topic-slug>-<seed>.wav files  │
        │   manifest.json (incremental, crash-safe)   │
        └─────────────────────────────────────────────┘
                  (catalog.db NEVER touched)
```

Primary trace: operator runs `--generate` → categories resolved from `AudioBible.list_song_categories()` (24) → `build_music_request` per category → backend.generate() → bytes written + manifest updated after each song → exit code reflects failures.

### Pattern 1: Extend-in-place script with orthogonal modes
**What:** `--generate` switches generate_phase5.py from verification/report mode into generation mode; without it, behavior is byte-compatible with today's report run (the Colab notebook and PHASE5_STATUS Reproduction block depend on it).
**When to use:** Any script that gains a second operational mode while keeping CI/report consumers stable.
**Example:**
```python
# Source: scripts/generate_phase5.py:39-45 (existing argparse) extended
parser.add_argument("--generate", action="store_true",
                    help="Generate songs (default: verify + write PHASE5_REPORT.md)")
parser.add_argument("--backend", default=None,
                    help="ace-step | suno | mock (default: MUSIC_BACKEND env, else mock)")
```

### Pattern 2: Motion-page mirror for Review UI hooks
**What:** One `GET` page + one pure-computation `POST` preview route + one `BackgroundTasks` action route, sharing a `_music_page_context()` helper — the exact shape of `/motion`, `/motion/prompt`, `/generate`.
**When to use:** Adding any phase's browse/preview/generate surface to the Studio UI.
**Evidence:** `src/review_ui/app.py:951–999` (motion page + prompt preview: form → `build_animation_prompt()` → re-render template with `prompt_result`; docstring states "no database writes and no image generation"), `app.py:1086–1127` (`background_tasks.add_task(...)` then `RedirectResponse(referer, 303)`).

### Pattern 3: Incremental crash-safe manifest (batch resume)
**What:** Manifest JSON rewritten (atomically: temp file + os.replace) after EVERY completed song; each entry records the full request signature so a re-run skips identical already-done work.
**When to use:** Long batches against a slow local service where interruption is likely (24 × 30–120 s songs).
**Key fields per entry:** `file, category, topic, seed, backend, format, bytes, duration_s, bpm, key_scale, time_signature, job_id, generated_at`.

### Anti-Patterns to Avoid
- **Blocking synchronous generation inside a FastAPI request handler:** an ace-step song blocks up to `timeout_s=300`; a 24-song batch would exceed any HTTP timeout. Use `BackgroundTasks` (house precedent) + polling endpoint.
- **Persisting music jobs/assets in catalog.db:** violates locked C2. JobQueue is constructed WITHOUT a repository everywhere it appears in review_ui (in-memory only).
- **Baking captions into the batch builder:** captions must flow from `audio_bible.prompts.build_music_prompt` via the Phase 7 adapters — never re-implemented in the script/UI layer (locked RESEARCH §3 decision from Phase 7).
- **Importing `src.music_generation` at module top of review_ui/app.py before Phase 7 lands:** use function-local imports inside routes/handlers (app.py already lazy-imports heavy modules, e.g. `from src.universe.batch_generator import resolve_backend` inside functions, lines 279, 1041).
- **Regenerating the whole report inside generation mode unconditionally:** keep modes orthogonal; `--generate` writes songs+manifest, optionally still writing the report only when verification also requested.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Request assembly (params/captions/lyrics scaffold) | Category tables or prompt strings in phase5 script / UI | `build_music_request` + `resolve_music_params` + adapter-side caption composition | Values are LOCKED by Phase 7 RESEARCH §3; duplicating them invites drift |
| Deterministic test audio | Custom WAV synthesizer in Phase 8 tests | `MockBackend` (seeded RIFF/WAV synthesis) | Already proven byte-deterministic by 07-01 tracer |
| Job lifecycle state machine | Ad-hoc dict of statuses | `src.pipeline.job_queue.JobQueue.create_job/update_status/get_job/list_jobs` | Existing validated transitions pending→running→completed/failed |
| HTTP calls to ACE-Step | New client code in script/UI | `backend.generate()` (protocol default loop w/ backoff+deadline) | Backoff/timeout/error-mapping hardening shipped in 07-01 Task 3 |
| Notebook git push plumbing | New sync code | `colab/git_sync.py::_basic_auth_header` / Cell-7 inline pattern | Battle-tested PAT handling (basic auth, x-access-token form) |

**Key insight:** Phase 8 contains almost zero novel algorithmic surface — its risk is *drift* from locked Phase 7 contracts and *misplacement* of responsibilities (e.g., touching catalog.db, blocking requests). Reuse is the whole game.

## Common Pitfalls

### Pitfall 1: Backend name mismatch — ROADMAP says `acestep`, registry key is `ace-step`
**What goes wrong:** ROADMAP Phase 8 specifies flags `--backend acestep|suno|mock`; the Phase 7 registry (`get_backend`) resolves `"ace-step"` / `"suno"` / `"mock"` and raises `MusicBackendError` on anything else.
**Why it happens:** Prose naming vs registry naming drifted between roadmap writing and plan locking.
**How to avoid:** The phase5 CLI should normalize aliases before calling `get_backend` — accept both `"acestep"` and `"ace-step"` (map → `"ace-step"`); help text lists all accepted spellings.
**Warning signs:** `MusicBackendError: unknown backend 'acestep' (valid: ace-step, suno, mock)` in manual runs.

### Pitfall 2: Duration-label vs duration-seconds mismatch
**What goes wrong:** The audio bible speaks in labels (`Micro 30 / Short 60 / Standard 120 / Feature 180 / Long 300` — libraries.py:109–115) while Phase 7's `build_music_request` resolves its own per-category seconds (75/75/60/80/120, generic 60).
**How to avoid:** In generation mode, default to `build_music_request(category, topic, seed=…)` with `duration_s=None` so LOCKED category params apply; offer an optional explicit `--duration-s` override only. Do NOT try to translate bible duration labels into the request unless a flag demands it — and if you do, validate against the bible tempo/duration tables and record the choice in SUMMARY.
**Warning signs:** Manifest durations that contradict `CATEGORY_MUSIC_PARAMS` golden values; report-mode briefs (Standard=120 s) disagreeing with generated files.

### Pitfall 3: Blocking the event loop / HTTP request with real generation
**What goes wrong:** Calling `backend.generate()` synchronously inside a route handler stalls uvicorn up to 300 s per song.
**How to avoid:** `BackgroundTasks.add_task(...)` + JobQueue status + polling endpoint (`GET /api/music/jobs`). Mock backend completes near-instantly so tests stay fast; TestClient executes background tasks after the response, letting assertions check final state without sleeps.
**Warning signs:** TestClient hangs; UI requests timing out with ace-step selected.

### Pitfall 4: Accidental catalog.db coupling
**What goes wrong:** Reusing the review UI's default `create_app()` wiring gives music routes a SQLite-backed repo and tempts asset-row writes.
**How to avoid:** Music routes never touch `repo`/`char_repo`; construct the music backend via `get_backend` (or injected param) independently; keep manifest as the sole persistence. Grep-gate: no `sqlite3` import added by phase files.
**Warning signs:** catalog.db mtime changes during test runs.

### Pitfall 5: Suno selection producing raw tracebacks
**What goes wrong:** Operator picks suno (UI dropdown or CLI flag); every call raises `NotConfigured`.
**How to avoid:** Catch `MusicBackendError` at both entry points: CLI prints reason to stderr + exit 1 (generate_phase7.py precedent); UI marks job failed and surfaces message via activity log/status endpoint — never a 500.
**Warning signs:** Stack traces in uvicorn output; non-zero unexpected exits.

### Pitfall 6: Non-atomic manifest writes during long batches
**What goes wrong:** Crash mid-write corrupts manifest.json, losing resume state for all songs.
**How to avoid:** Write to `manifest.json.tmp` then `os.replace()`; append entries incrementally after each song completes.
**Warning signs:** JSON decode errors on resume.

### Pitfall 7: Notebook installs ACE-Step into the studio environment
**What goes wrong:** ACE-Step 1.5 wants Python 3.11–3.12 and heavy deps (torch stack); mixing into one env risks breaking the studio install (repo pins torch>=2.13, diffusers>=0.39).
**How to avoid:** Clone ACE-Step-1.5 to `/content/ACE-Step-1.5` with its own venv (`uv sync` or `pip install -e .` in isolation); keep studio install light (`pip install -e . --no-deps` + few wheels, exactly like Colab Phase 4 Cell 2). Studio talks to the service over HTTP only.
**Warning signs:** pip resolver conflicts during Cell "install" on Colab.

## Code Examples

### Generation mode core loop (script tier)
```python
# Source: composition of scripts/generate_phase7.py Task-3 semantics
# (07-02 plan) + scripts/generate_phase5.py skeleton
from src.audio_bible import AudioBible
from src.music_generation import (
    MusicBackendError, build_music_request, get_backend,
)

BACKEND_ALIASES = {"acestep": "ace-step", "suno": "suno", "mock": "mock"}

def _slug(text: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in text.lower()).strip("-")

def generate_songs(backend_name, categories, topic_fn, out_dir, force=False):
    name = BACKEND_ALIASES.get((backend_name or "").lower(), backend_name or "mock")
    backend = get_backend(name)                 # MUSIC_BACKEND env -> mock fallback
    manifest_path = os.path.join(out_dir, "manifest.json")
    manifest = load_manifest(manifest_path)     # {"version": 1, "songs": [...]}
    failures = []
    for category in categories:                 # AudioBible().list_song_categories()
        request = build_music_request(
            category, topic=topic_fn(category)) # duration from locked params
        fname = f"{_slug(category)}-{_slug(request.topic) or 'song'}-{request.seed or 0}.wav"
        entry = find_entry(manifest, fname)
        if entry and not force and entry_matches(entry, request, name):
            continue                            # idempotent resume skip
        try:
            result = backend.generate(request)  # submit->poll->download w/ backoff
        except MusicBackendError as exc:        # NotConfigured/BackendUnavailable/
            failures.append((category, str(exc)))  # GenerationFailed
            continue
        path = os.path.join(out_dir, fname)
        with open(path, "wb") as fh:            # C2: only ever under Audio/Music/
            fh.write(result.audio)
        upsert_entry(manifest, {
            "file": fname, "category": category, "topic": request.topic,
            "seed": result.seed, "backend": result.backend,
            "format": result.format, "bytes": len(result.audio),
            "duration_s": request.duration_s, "job_id": result.job_id,
            "generated_at": now_iso(),
        })
        atomic_write_manifest(manifest_path, manifest)
    return failures                             # exit 1 if any
```

### Review UI hook trio (mirroring motion pattern)
```python
# Source: shapes verified at src/review_ui/app.py:951-999 (motion page +
# prompt preview) and :1086-1111 (POST /generate BackgroundTasks)
@app.get("/music", response_class=HTMLResponse)
async def music_page(request: Request):
    return templates.TemplateResponse(request, "music.html", _music_page_context())

@app.post("/music/prompt", response_class=HTMLResponse)
async def music_prompt(request: Request):
    """Pure preview: caption + negative + resolved params + request JSON.
    No database writes and NO network calls (motion/prompt precedent)."""
    form = await request.form()
    category = str(form.get("category", "Alphabet"))
    topic = str(form.get("topic", "")).strip() or f"{category.lower()} fun"
    req = build_music_request(category, topic)           # lazy import inside fn
    params = resolve_music_params(category)
    return templates.TemplateResponse(request, "music.html", _music_page_context(
        preview={
            "request_json": req.model_dump_json(indent=2),
            "caption": build_music_prompt(category, topic),   # bible-authoritative
            "negative": music_negative_prompt(category),
            "params": params.model_dump(),
        }, form_values={"category": category, "topic": topic}))

@app.post("/music/generate")
async def music_generate(request: Request, background_tasks: BackgroundTasks,
                          category: str = Form("Alphabet"),
                          topic: str = Form(""), backend: str = Form("")):
    job = jq.create_job(character_id="music", job_type="music",
                        config={"category": category, "backend": backend})
    jq.update_status(job.id, "running")
    background_tasks.add_task(_run_music_job, job.id, category, topic, backend)
    return RedirectResponse(url="/music", status_code=303)

async def _run_music_job(job_id, category, topic, backend_name):
    try:
        backend = get_backend(backend_name or None)      # env/mock default
        result = backend.generate(build_music_request(category, topic))
        # ... write WAV + manifest under Audio/Music/ (never repo) ...
        jq.update_status(job_id, "completed")
    except MusicBackendError as exc:
        logger.error("Music job %s failed: %s", job_id, exc)  # activity buffer
        jq.update_status(job_id, "failed")
```

### Colab notebook cell — ACE-Step service bring-up (GPU runtime)
```python
# Source: install commands CITED from github.com/ACE-Step/ACE-Step-1.5 README;
# structure mirrors colab/AnimationStudio_Colab_Phase4.ipynb Cells 2/4
#@title 4. Install & start the local ACE-Step service (GPU runtime)
import os, subprocess, sys, time, urllib.request

ACE_DIR = "/content/ACE-Step-1.5"
if not os.path.isdir(ACE_DIR):
    run(["git", "clone",
         "https://github.com/ACE-Step/ACE-Step-1.5.git", ACE_DIR])
# isolated service env (service wants py3.11-3.12; keeps studio env untouched)
subprocess.run(["uv", "sync"], cwd=ACE_DIR, check=True)
os.environ["ACESTEP_API_KEY"] = "colab-local-key"
os.environ["ACESTEP_BASE_URL"] = "http://127.0.0.1:8001"
server = subprocess.Popen(
    ["uv", "run", "acestep-api"], cwd=ACE_DIR)   # REST API on :8001 (CITED: README)
for _ in range(120):                              # models (~10-20 GB) download on
    try:                                          # first start — allow minutes
        urllib.request.urlopen(
            f"{os.environ['ACESTEP_BASE_URL']}/v1/jobs/health", timeout=2)
        break
    except Exception:
        time.sleep(5)
# then: run([sys.executable, "scripts/generate_phase5.py",
#            "--generate", "--backend", "acestep"])
```
CPU-runtime fallback: skip this cell entirely and run `--backend mock --generate` (offline verification mode mirrors the whole Phase 4 notebook).

## Deliverable Deep-Dives (the six planning questions, answered)

### D1. `generate_phase5.py` generation mode — exact shape

**Flags** (all verified against existing conventions):
| Flag | Default | Notes |
|------|---------|-------|
| `--generate` | off | Switch to generation mode; without it the script behaves exactly as today (report mode must stay byte-compatible — Colab Phase 5 + PHASE5_STATUS Reproduction depend on it) |
| `--backend` | `None` → `MUSIC_BACKEND` env → `"mock"` | Accept `acestep`/`ace-step`/`suno`/`mock`; normalize alias per Pitfall 1 |
| `--category` | `"all"` | Repeatable or comma-list; validated against `AudioBible().list_song_categories()` (24 names); unknown → error listing valid names (mirrors Colab Phase 1 Cell 3b scope validation) |
| `--topic` | `"{category.lower()} fun"` | Matches existing report-mode topic convention (script line 58) |
| `--seed` | None | Base seed; when unset let `build_music_request`/backend resolve (result.seed recorded in manifest) |
| `--duration-s` | None | Optional override; default = LOCKED category params |
| `--out` | `Audio/Music` | mkdir -p; ONLY output location (C2) |
| `--force` | off | Regenerate even when a matching manifest entry exists |

**Manifest schema** (`Audio/Music/manifest.json`): `{"version": 1, "songs": [entry...]}` where entry = `{file, category, topic, seed, backend, format, bytes, duration_s, bpm, key_scale, time_signature, job_id, generated_at}`. Single shared manifest (not per-song sidecars) chosen because batch resume checks are O(1) lookups and MUSIC-GENERATION.md §Risks #3 prescribes "Audio/Music/** + JSON sidecar" without mandating granularity.

**File layout:** `Audio/Music/<category-slug>-<topic-slug>-<seed>.<format>` — reusing generate_phase7.py's naming convention verbatim (07-02 Task 3: `<category lowercased>-<topic slugified or "song">-<effective seed>.<format>`). Format extension comes from `MusicResult.format` ("wav"/"mp3").

**Batch semantics:** iterate resolved categories → build request → `backend.generate()` → write bytes → upsert manifest entry → atomic manifest rewrite after EVERY song. Exit 0 only if zero failures (and doc-check still passes when report mode also ran).

**Idempotency/resume:** skip a song when manifest contains an entry with same `file` whose `backend`, `seed`, `topic`, `duration_s` match the freshly built request and the file exists on disk with the recorded byte count. `--force` bypasses. This makes interrupted Colab sessions resumable (mirrors `wget -c` philosophy of the Phase 1 notebook).

### D2. Review UI hooks

Verified integration points:
- **Routes to add** inside `create_app()` (closure pattern, app.py:608+): `GET /music`, `POST /music/prompt`, `POST /music/generate`, `GET /api/music/jobs`. Nav link `<a href="/music">Music</a>` added to `base.html` navbar (app.py templates/base.html:15–19 shows Dashboard/Motion links).
- **Template:** new `src/review_ui/templates/music.html` extending `base.html` (motion.html is the structural model: standards panel → prompt-builder form → results panel). Context helper `_music_page_context()` mirrors `_motion_page_context()` (app.py:833).
- **Job mechanism:** BackgroundTasks + JobQueue — both already exist and are injected/testable. JobQueue jobs use `job_type="music"`; `character_id` field carries `"music"` sentinel (it's an unvalidated string). Jobs stay in-memory: `jq = job_queue or JobQueue()` never receives a repo for music paths → C2 safe.
- **Synchronous vs polling:** polling. ACE-step songs run tens of seconds–minutes each; mock completes instantly (tests fast). `GET /api/music/jobs` returns `[{id, status, category, error?, file?}]`; studio.js-style fetch polling or plain meta-refresh both acceptable at this UI's sophistication level (motion page uses no JS at all).
- **create_app DI:** add `music_backend=None` kwarg (default resolves via lazy `get_backend(None)` on first music route hit). Tests inject MockBackend or rely on env-free default. Keep ALL `src.music_generation` imports function-local until Phase 7 exists (house lazy-import style).

### D3. Colab notebook pattern (what Phase 5's notebook mirrors)

Phase 4 notebook structure (9 cells, verified by reading the JSON):
0. markdown intro (scope table, "no GPU needed", steps)
1. Settings (`REPO_URL`, `BRANCH`, `SYNC_TO_GITHUB`, `GIT_NAME`, `GIT_EMAIL`, `GITHUB_TOKEN`)
2. Clone repo + install studio (`pip install -e . --no-deps` + light deps list)
3. Preview bible scope (pure-python library counts)
4. Regenerate PHASE4_REPORT.md via `scripts/generate_phase4.py`
5. Run phase test suites
6. Review report (display Markdown)
7. Sync refreshed artifacts (git push w/ PAT basic-auth header, else files.download)
8. Next steps markdown

Phase 5 notebook = same skeleton + one inserted GPU cell:
| Cell | Content |
|---|---|
| 0 | intro: offline ACE-Step run; CPU runtime gets verification/mock mode; GPU runtime gets real songs |
| 1 | Settings + `RUN_REAL_GENERATION` boolean + `ACESTEP_MODEL` choice |
| 2 | clone + install studio (identical to Phase 4 Cell 2) |
| 3 | preview 24 song categories (`AudioBible().list_song_categories()`) |
| 4a | *(GPU path)* install/start ACE-Step service in `/content/ACE-Step-1.5`, health-wait (code example above) |
| 4b | run `scripts/generate_phase5.py --generate --backend <acestep\|mock>` |
| 5 | run `pytest tests/test_audio_bible.py tests/test_music_generation.py -q` |
| 6 | review manifest.json + report excerpt |
| 7 | sync: git add `Audio/Music/ PHASE5_REPORT.md` + push/download (Cell-7 PAT pattern) |

ACE-Step service facts for cell comments [CITED: github.com/ACE-Step/ACE-Step-1.5 README]: install `git clone` + `uv sync`; REST server launch `uv run acestep-api` serving `http://localhost:8001` (matches `ACESTEP_BASE_URL` default); API auth `--enable-api --api-key KEY --port 8001`; models auto-download (~10–20 GB) to the service checkout on first start — Colab disk, NEVER Drive (mirrors Flux-model policy in the Phase 1 notebook intro). VRAM from vendor `gpu_config.py` [CITED: acestep/gpu_config.py]: DiT turbo weights 4.7 GB, XL 9.0 GB, + VAE 0.33 + text encoder 1.2 + CUDA ctx 0.5; T4's 15 GB usable VRAM runs turbo comfortably and XL with CPU offload.

### D4. `PHASE5_STATUS.md` update targets

Current claims that change:
- Line ~64–67 "Notes/Caveats": *"audio rendering is left to the AI platforms with prompts built by this package"* → now false for ACE-Step/mock paths; revise to describe wired generation with backend selection.
- "Reproduction" block: add `--generate` examples (mock offline one-liner + documented live-smoke pointer to Audio/Music/README.md checklist).
- New section "## Music Generation Wiring (Phase 8)": deliverables table rows for script generation mode, Review UI hooks, Colab notebook, manifest inventory (song count, backends exercised), test counts added.
- Deliverables table gains a row referencing `Audio/Music/manifest.json` as the artifact inventory source.

### D5. Test strategy (fully offline)

- No real audio, no network, no catalog.db mutation anywhere in CI (constraint set C1/C2/C3).
- Script tests: new `tests/test_generate_phase5.py` following `test_generate_phase3_assets.py` conventions (import script module, unit-test helpers + in-process `main([...])` runs against tmp_path out dirs with mock backend). Fail-loud transport guards prove dry paths dial-free (07-02 precedent).
- UI tests: extend `tests/test_review_ui_*` family (new class or `test_review_ui_music.py`) using the established `sqlite_app` fixture + `TestClient`; assert `/music` renders, prompt-preview returns caption+params without any transport guard trip, generate endpoint enqueues job and (after TestClient flushes background task) job reaches completed with WAV under tmp out dir, suno selection yields failed job not a 500.
- Manifest logic: golden tests for schema shape, resume-skip decision (same signature skips; changed seed regenerates; --force overrides), atomic-write crash simulation (tmp leftover ignored).
- Notebook: NOT executed in CI (manual operator surface, like all prior notebooks); its correctness is covered indirectly because every command it shells out to is itself tested.

### D6. Risks / open questions for the planner
See Open Questions below — headline risks: Phase 7 execution ordering (blocking), acestep/ace-step naming (decide alias policy), duration-label policy (recommend locked defaults), BackgroundTasks ephemerality across restarts (accept + document).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Suno assumed reachable via wrapper APIs | Official API still absent (early-access cohort only); stub stays refusing | confirmed 2026-08 research (.planning/research/MUSIC-GENERATION.md) | Phase 8 ships suno flag but it always refuses gracefully; no behavior expected |
| ACE-Step v1 (`pip install ace-step`, Gradio-first) | ACE-Step 1.5 repo with dedicated REST API server (`acestep-api`, port 8001) | 2026 | Notebook installs the 1.5 repo; matches locked REST contract §2 |
| Manual VRAM sizing | Vendor auto-tiering (`gpu_config.py` tiers incl. 16 GB tier6a offload split) | current | Notebook needs no manual offload flags for T4/turbo; document optional knob only |

**Deprecated/outdated:**
- Legacy `pip install ace-step` PyPI package = v1 model line — do NOT use in the notebook; the 1.5 GitHub repo is authoritative.
- `python -m acestep.api_server` (research-doc form) still works, but README-canonical launch is `uv run acestep-api`.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Phase 7 will be executed (unchanged) before Phase 8 execution begins; its plan contracts hold verbatim | Summary / Standard Stack | Every import fails; plans need rework against actual drift |
| A2 | Planners may accept `acestep` as CLI alias mapping to registry key `ace-step` | Pitfall 1 / D1 | Minor UX inconsistency; harmless either way |
| A3 | Generation mode defaults durations from LOCKED category params rather than bible labels | Pitfall 2 / D1 | Songs shorter/different than report-mode briefs imply; cosmetic inconsistency |
| A4 | In-memory JobQueue + BackgroundTasks acceptable for single-operator UI jobs (lost on restart) | D2 | Operator confusion after restart; acceptable at current ops maturity |
| A5 | Colab free-tier T4 sufficient for turbo-model song batches | D3 | Batch slow/OOM on XL without offload; mitigation documented (offload knob, mock fallback) |
| A6 | `uv` available on Colab VMs for the isolated service env (or pip fallback works) | D3 | Cell fails; pip-install fallback documented inline |
| A7 | Manifest single-file JSON preferred over per-song sidecars | D1 | Only affects resume ergonomics; trivially refactorable |

## Open Questions

1. **Should generation mode also refresh PHASE5_REPORT.md?**
   - What we know: modes kept orthogonal keeps report consumers stable; but operators like one-command runs.
   - Recommendation: keep orthogonal; optionally add `--with-report` later. Planner decides flag surface.
2. **UI generate scope: single song per click or category-batch?**
   - What we know: `/generate` panel batches images; ace-step batch of 24 could run an hour+ in one background task.
   - Recommendation: single-song (one category per submit) for UI v1; full batching stays the script/notebook's job.
3. **Does `GET /api/music/jobs` reuse `/api/jobs` filtering instead of a new endpoint?**
   - What we know: `/api/jobs` already lists JobQueue contents (app.py:688).
   - Recommendation: reuse with `job_type=music` filter param if trivially supported; else new endpoint.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.11+ | everything | ✓ | 3.13.5 | — |
| pytest (+timeout, asyncio auto) | test suite | ✓ | 9.1.1 (system) | `.venv` lacks pytest — use system python3 |
| fastapi/uvicorn/jinja2/pydantic | Review UI hooks | ✓ | 0.140.13 / 0.51.0 / 3.1.6 / 2.13.4 | — |
| ACE-Step local service | live smoke only | ✗ (by design) | — | MockBackend everywhere; manual checklist doc |
| Google Colab GPU (T4+) | notebook real-generation cell | ✗ (operator machine) | — | CPU-runtime mock/dry-run mode built into notebook design |
| git + GitHub PAT | notebook sync cell | operator-dependent | — | files.download fallback (Cell 7 pattern) |

**Missing dependencies with no fallback:** none blocking development/testing — the entire phase is executable offline.
**Missing dependencies with fallback:** ACE-Step service (mock), Colab GPU (CPU mode), PAT (zip download).

## Validation Architecture

Test infrastructure summary: pytest 9.1.1 with `asyncio_mode=auto`, `testpaths=["tests"]`, 30 s per-test timeout (pyproject `[tool.pytest.ini_options]`). Baseline this session: **1550 passed / 5 failed in ~152 s** — the 5 failures are pre-existing `tests/test_story_engine.py` catalog-integration tests that depend on local `catalog.db` contents ("Main Family Home" row absent from current DB; they `pytest.skip` when the DB is absent). Unrelated to music generation; do not let Phase 8 plans claim "full suite 100% green" — use "green except the 5 known story-engine catalog failures" or fix expectations accordingly.

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 (system python3.13; `.venv` has no pytest) |
| Config file | pyproject.toml `[tool.pytest.ini_options]` |
| Quick run command | `python3 -m pytest tests/test_music_generation.py tests/test_generate_phase5.py tests/test_review_ui_music.py -q` |
| Full suite command | `python3 -m pytest tests/ -q` (~152 s) |

### Per-Deliverable Verification Map

| Deliverable | Verified by | Environment |
|---|---|---|
| generate_phase5.py generation mode (flags, alias normalization, category validation) | unit: `tests/test_generate_phase5.py` — argparse surface, alias map, unknown-category error, scope preview counts = 24 | offline CI |
| Batch loop + file layout | integration w/ MockBackend into `tmp_path` out dir: correct `<category>-<topic>-<seed>.wav` filenames, RIFF magic on bytes, exit codes 0/1 by failure count | offline CI |
| Manifest schema + atomic writes + resume skip | golden tests: schema keys/version, same-signature skip, changed-seed regen, `--force`, tmp-file crash leftover ignored | offline CI |
| catalog.db isolation (C2) | grep-gate `! rg -q sqlite3 <phase files>` + DB byte-identity before/after suite (07 precedent) | offline CI |
| Review UI `/music` page + nav link | TestClient GET asserts template renders, categories listed | offline CI |
| `POST /music/prompt` pure preview | fail-loud transport guards never trip; caption contains bible keyword; params match LOCKED golden values (Bedtime 66/3/4/F major) | offline CI |
| `POST /music/generate` + job lifecycle | TestClient with injected mock backend: job pending→completed, WAV written under tmp out, manifest updated; suno selection → failed job + error message, no 500 | offline CI |
| `GET /api/music/jobs` polling endpoint | TestClient JSON shape assertions | offline CI |
| Colab notebook | NOT CI-executed (manual operator artifact); every shell-out target is itself tested; JSON validity check possible (`python -c "import json;json.load(open(...))"`) | manual |
| PHASE5_STATUS.md accuracy | report-mode run still exits 0 and reproduces documented commands; human review of new section vs actual artifacts | offline + human |
| Live ACE-Step smoke | existing manual checklist in Audio/Music/README.md (from Phase 7) extended with one `--generate --backend ace-step --category Bedtime` line | operator machine ONLY |

### Recommended Plan Structure

Two plans (single wave each), sequential — mirrors Phase 7's split rhythm:

- **Plan 08-01** — Script + manifest core: extend `scripts/generate_phase5.py` (`--generate` mode, flags, batch loop, manifest module-level helpers, resume logic), new `tests/test_generate_phase5.py`. Depends-on: [] (programs against locked Phase 7 contracts).
- **Plan 08-02** — UI + notebook + docs: Review UI music hooks (routes/template/nav/DI + `tests/test_review_ui_music.py`), `colab/AnimationStudio_Colab_Phase5.ipynb`, `PHASE5_STATUS.md` update. Depends-on: ["08-01"] (UI background task reuses script-tier manifest writer helpers to avoid duplication).

Dependency chain: 08-02 → 08-01. No parallel waves needed (small phase).

### Sampling Rate
- **Per task commit:** quick command above (< 30 s target)
- **Per wave merge:** full suite `python3 -m pytest tests/ -q`
- **Phase gate:** full suite green (modulo the 5 pre-existing story-engine failures) before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_generate_phase5.py` — does not exist yet (script currently untested)
- [ ] `tests/test_review_ui_music.py` (or class in existing review_ui test file)
- Framework install: none — infra complete

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | N/A — localhost single-operator tool |
| V3 Session Management | no | N/A — no user sessions |
| V4 Access Control | no | Single-operator; routes unauthenticated like all existing ones |
| V5 Input Validation | yes | Pydantic models (`MusicRequest` bounds duration_s 10–600), Literal enums, argparse choices, category allow-list from bible |
| V6 Cryptography | no | No crypto; PAT handled via git http.extraheader only at runtime (never stored/logged — git_sync pattern) |
| V7 Error Handling/Logging | yes | `MusicBackendError` caught at all boundaries; messages never embed credentials (Phase 7 token-leak test precedent) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Path traversal via crafted topic/category in output filename | Tampering/Elevation | Slugify both components (alnum+dash) before joining under fixed `Audio/Music/`; reject empty slugs |
| Secret leakage in logs/manifest/errors | Info Disclosure | ACESTEP_API_KEY read env-only inside backend; manifest records seed/job_id/backend but never headers/keys; caplog leak test precedent carried forward |
| DoS via unbounded batch in UI request | Denial of Service | UI submits single songs; batches live in CLI/notebook; protocol deadline timeout_s=300 caps any song |
| Malicious/malformed service responses | Tampering | Already mitigated inside AceStepBackend (strict stdlib JSON, typed errors) — Phase 8 adds no new parsing |
| catalog.db corruption | Tampering | C2 grep-gate + byte-identity check (unchanged from Phase 7 verification) |

## Sources

### Primary (HIGH confidence — direct codebase inspection this session)
- `scripts/generate_phase5.py` — full read (192 lines): argparse skeleton, report mode, exit contract
- `src/review_ui/app.py` — create_app DI (:231–320), motion page/prompt (:951–999), /generate BackgroundTasks (:1086–1127), JobQueue wiring (:308)
- `src/audio_bible/bible.py` + `libraries.py` — list_song_categories (24 verified names), SONG_DURATIONS, CATEGORY_TEMPO, build_music_brief
- `src/pipeline/job_queue.py` — full state machine
- `.planning/phases/07-…/07-01-PLAN.md`, `07-02-PLAN.md` — locked API surface (must_haves verbatim)
- `colab/AnimationStudio_Colab_Phase4.ipynb` (9 cells) + `AnimationStudio_Colab.ipynb` (GPU patterns) + `colab/git_sync.py`
- `tests/test_generate_phase3_assets.py`, `test_review_ui_generation.py`, `conftest.py` — test conventions
- Full-suite baseline run: 1550 passed / 5 pre-existing failures / ~152 s

### Secondary (MEDIUM confidence — official vendor sources via WebSearch)
- [CITED: github.com/ACE-Step/ACE-Step-1.5 README] install (`git clone` + `uv sync`), launch (`uv run acestep-api`, :8001), auth flags, model auto-download, .env knobs, Python 3.11–3.12 recommendation
- [CITED: github.com/ace-step/ACE-Step-1.5 blob/main/acestep/gpu_config.py] VRAM table (DiT turbo 4.7 GB / XL 9.0 GB / LM tiers) and GPU tier configs incl. 16 GB tier6a offload split
- [CITED: pypi.org/project/ace-step] legacy v1 pip package exists (do not use for 1.5)

### Tertiary (LOW confidence — seam-classified websearch, cached)
- Colab free-tier T4 = 15 GB usable VRAM (ECC reservation); public Kaggle notebook demonstrates AceStep 1.5 XL Turbo on T4 [ASSUMED-grade corroboration]

## Metadata

**Confidence breakdown:**
- Integration surfaces & patterns: HIGH — every route/template/script/test convention read directly this session
- Phase 7 API contract: HIGH as *plan-locked text*; execution-dependent until 07 lands
- ACE-Step Colab ops facts: MEDIUM — vendor README/source cited, but Colab-runtime behavior (uv availability, python version) not executable here

**Research date:** 2026-08-22
**Valid until:** ~2026-09-21 (internal wiring; recheck only if Phase 7 plans change)

## RESEARCH COMPLETE

**Key findings for the orchestrator:** (1) This is a pure-wiring phase with zero new dependencies; every needed pattern has a verified in-repo precedent (motion-page hooks, BackgroundTasks panel, Phase 4 notebook skeleton, phase7 CLI conventions). (2) BLOCKER-ADJACENT: Phase 7 code does not exist yet — planning proceeds against its plan-locked API, but execution must follow Phase 7 completion. (3) Three decisions flagged for the planner: acestep/ace-step flag aliasing, duration policy (locked category defaults recommended), and UI job granularity (single-song recommended). (4) Full-suite baseline is 1550 passed with exactly 5 pre-existing catalog.db-state failures in test_story_engine.py — unrelated, but plans must not promise a naive "100% green".
