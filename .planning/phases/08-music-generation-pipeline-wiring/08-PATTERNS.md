# Phase 8: Music Generation Pipeline Wiring - Pattern Map

**Mapped:** 2026-08-22
**Files analyzed:** 7 (3 modify, 4 new)
**Analogs found:** 7 / 7 (all files have in-repo analogs; two sub-patterns are plan-locked only — see Caveats)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `scripts/generate_phase5.py` | script (CLI entrypoint) | batch + file-I/O | itself (report mode) + `scripts/generate_phase4.py` conventions | exact for skeleton; generation loop is plan-locked |
| `tests/test_generate_phase5.py` | test | batch/file-I/O, offline | `tests/test_generate_phase3_assets.py` | exact |
| `src/review_ui/app.py` | controller (routes + DI factory) | request-response + event-driven jobs | itself — motion trio (:951–999), `/generate` BackgroundTasks (:1086–1127), `create_app` DI (:231–320) | exact |
| `src/review_ui/templates/music.html` | component (Jinja2 template) | request-response | `src/review_ui/templates/motion.html` | exact |
| `tests/test_review_ui_music.py` | test | request-response, offline TestClient | `tests/test_review_ui_api.py` (motion classes) + `tests/test_review_ui_generation.py` (fixtures) | exact |
| `colab/AnimationStudio_Colab_Phase5.ipynb` | notebook (operator artifact) | subprocess orchestration | `colab/AnimationStudio_Colab_Phase4.ipynb` (9 cells, read this session) | exact; ACE-Step cell has no analog |
| `PHASE5_STATUS.md` | docs (status evidence trail) | static doc | itself | exact |

---

## Pattern Assignments

### 1. `scripts/generate_phase5.py` (script, batch + file-I/O)

**Analog:** its own current report mode (192 lines, fully read). The `--generate` mode extends in place while keeping report behavior byte-compatible.

**Script bootstrap + imports pattern** (lines 12–18):
```python
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.audio_bible import AudioBible, AudioProductionSystem, quality_checklist
```

**Argparse skeleton to extend** (lines 39–45):
```python
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docs-dir", default="Audio",
                        help="Directory containing the Audio/ markdown bibles")
    parser.add_argument("--out", default="PHASE5_REPORT.md",
                        help="Output report path")
    args = parser.parse_args()
```
New flags (`--generate`, `--backend`, `--category`, `--topic`, `--seed`, `--duration-s`, `--out` repurposed or new `--music-dir`, `--force`) follow this exact style: lowercase kebab flags, sensible string defaults, one-line help.

**Root-relative path resolution** (lines 47–50 and 176–178):
```python
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = args.docs_dir
    if not os.path.isabs(docs_dir):
        docs_dir = os.path.join(root, docs_dir)
```
Apply identically to the `--out` music directory (default `Audio/Music`).

**Category iteration + topic convention** (lines 57–61) — reuse verbatim as the batch-loop driver:
```python
    music_briefs = [
        bible.build_music_brief(category=c, topic=f"{c.lower()} fun",
                                duration_label="Standard")
        for c in bible.list_song_categories()
    ]
```
Note the existing default-topic convention `f"{c.lower()} fun"` (line 58) — RESEARCH D1 mandates `--topic` default `"{category.lower()} fun"` to match.

**Output write + exit contract** (lines 176–188):
```python
    out_path = args.out
    if not os.path.isabs(out_path):
        out_path = os.path.join(root, out_path)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"Doc consistency: {...}")
    print(f"Report written:  {out_path}")
    return 0 if doc_report.passed and plan.passed else 1
```
Generation mode must keep the same contract: human-readable stdout summary lines, `return 0` only when zero song failures.

**Divergence from analog:** report mode is pure-computation; generation mode adds backend calls, binary writes under `Audio/Music/` ONLY (C2), and incremental atomic manifest writes (temp file + `os.replace`) — none of which exist in this script today.

---

### 2. `tests/test_generate_phase5.py` (test, offline)

**Analog:** `tests/test_generate_phase3_assets.py` (206 lines, fully read).

**Import-the-script-module pattern including private helpers** (lines 13–26):
```python
from scripts.generate_phase3_assets import (
    ASSET_TYPES,
    LIGHTING_STUDIES,
    VIEWS,
    _color_catalog,
    _material_catalog,
    _parse_asset_types,
    _parse_variants,
    _pick_color,
    _pick_material,
    _tasks,
)
```
Phase 8 equivalent imports `BACKEND_ALIASES`, `_slug`, manifest helpers (`load_manifest`, `upsert_entry`, `find_entry`, `atomic_write_manifest`) directly from `scripts.generate_phase5`.

**Invalid input → SystemExit** (lines 54–61):
```python
def test_parse_asset_types_unknown_raises():
    with pytest.raises(SystemExit):
        _parse_asset_types("bogus")
```
Mirror for unknown `--category` values (must error listing valid names from `AudioBible().list_song_categories()`).

**Baseline-count fixture asserting locked inventory** (lines 29–34):
```python
@pytest.fixture(scope="module")
def props():
    """All 1,559 prop seeds (World/INDEX.md + Assets/Props/INDEX.md)."""
    found = discover_props("World", "Assets")
    assert len(found) == 1559  # PHASE3_STATUS.md baseline
    return found
```
Phase 8 equivalent: assert `len(AudioBible().list_song_categories()) == 24`.

**Docstring convention** (lines 1–9): module docstring names the script under test and enumerates covered concerns — copy this shape.

**Additional conventions from the suite** (RESEARCH D5): integration runs use `main([...])`-style in-process invocation against `tmp_path` out dirs with the mock backend; golden tests pin manifest schema keys/version; resume-skip tests cover same-signature skip / changed-seed regen / `--force`; crash simulation leaves a `.tmp` leftover that must be ignored.

---

### 3. `src/review_ui/app.py` (controller — music routes, nav, DI)

**Analog:** itself. All excerpts verified by full read (1,260 lines).

**create_app DI signature to extend** (lines 231–242):
```python
def create_app(
    asset_repo=None,
    character_repo=None,
    job_queue=None,
    generation_backend=None,
    seed_catalog=None,
    db_path: Optional[str] = "catalog.db",
    universe_dir: str = str(_PROJECT_ROOT / "Universe"),
    world_dir: str = str(_PROJECT_ROOT / "World"),
    assets_dir: str = str(_PROJECT_ROOT / "Assets"),
    persist_generated_images: bool = False,
) -> FastAPI:
```
Add `music_backend=None` kwarg following the same optional-DI style. **Critical divergence (C2):** music routes never touch `repo`/`char_repo`; resolve via lazy `get_backend(music_backend)` on first hit instead of the SQLite fallback block at lines 274–304.

**JobQueue wiring** (line 308):
```python
    jq = job_queue or JobQueue()
```
Music jobs MUST keep this no-repository form (in-memory only). `JobQueue.__init__(self, repository=None)` accepts an optional persistence repo — never pass one for music (verified `src/pipeline/job_queue.py:66–68`).

**Lazy heavy-import house style** (lines 1040–1042 inside `_background_batch`; also 274–281, 532, 836, 976):
```python
        """Run a batch generation in the background and log the summary."""
        from src.universe.batch_generator import resolve_backend
        backend = resolve_backend(backend_name) if backend_name else None
```
ALL `src.music_generation` imports go inside route/handler bodies — Phase 7 code does not exist yet, and even after it lands this is the established style.

**Context-helper mirror target: `_motion_page_context()`** (lines 833–836, 946–949):
```python
    def _motion_page_context(prompt_result: dict | None = None,
                             form_values: dict | None = None) -> dict:
        """Build the Phase 4 Animation Bible browser context."""
        from src.animation_bible import libraries as lib
        ...
            # Prompt builder inputs
            "prompt_templates": sorted(MOTION_PROMPT_TEMPLATES.keys()),
            "camera_styles": sorted(_CAMERA_STYLE_DESCRIPTORS.keys()),
            "negative_prompt": ANIMATION_NEGATIVE_BASE,
            "prompt_result": prompt_result or {},
            "form_values": form_values or {},
        }
        return data
```
Write `_music_page_context(preview=None, form_values=None)` with the same `(result, form_values)` re-render signature; populate categories from `AudioBible().list_song_categories()`, plus preview payload (request JSON, caption via bible prompts, negative prompt, resolved params).

**GET page pattern** (lines 951–956):
```python
    @app.get("/motion", response_class=HTMLResponse)
    async def motion_page(request: Request):
        """Phase 4 — Animation Bible & Motion System library browser."""
        return templates.TemplateResponse(
            request, "motion.html", _motion_page_context()
        )
```

**Pure-preview POST pattern** (lines 958–999) — the model for `POST /music/prompt`:
```python
    @app.post("/motion/prompt", response_class=HTMLResponse)
    async def motion_prompt(request: Request):
        """Build an animation prompt from the bible templates (text only).

        Pure ``build_animation_prompt()`` evaluation — no database writes and
        no image generation.
        """
        form = await request.form()
        character = str(form.get("character", "")).strip() or "Lily Bunny"
        template = str(form.get("template", "")).strip() or "walk"
        ...
        from src.animation_bible.prompts import build_animation_prompt
        prompt = build_animation_prompt(...)
        result = {"prompt": prompt, "character": character, "template": template}
        values = {"character": character, ...}
        return templates.TemplateResponse(
            request, "motion.html",
            _motion_page_context(prompt_result=result, form_values=values),
        )
```
Docstring must state the purity guarantee verbatim-style ("no database writes and no network calls"). Form parsing: `str(form.get(...)).strip()` with inline defaults.

**BackgroundTasks action pattern** (lines 1086–1111) — the model for `POST /music/generate`:
```python
    @app.post("/generate")
    async def generate(
        request: Request,
        background_tasks: BackgroundTasks,
        scope: str = Form("characters"),
        ...
        backend: str = Form("mock"),
    ):
        """Queue a background generation batch for catalog seeds."""
        ...
        background_tasks.add_task(
            _background_batch, scope, item, asset_type, count, backend, variant, limit
        )
        logger.info("Generate queued: scope=%s item=%r count=%s backend=%s", scope, item, count, backend)
        return RedirectResponse(url=_get_referer(request), status_code=303)
```
Referer helper (lines 1133–1135):
```python
    def _get_referer(request: Request) -> str:
        """Extract the referer URL from the request (safe fallback)."""
        return request.headers.get("referer", "/")
```

**Error boundary in background worker** (lines 1057–1079):
```python
            try:
                seeds = _find_seeds(scope_name, item)
            except Exception as exc:
                logger.exception("Generate: seed discovery failed: %s", exc)
                return
            ...
            except Exception as exc:
                logger.exception("Generate: batch run failed: %s", exc)
                return
```
Music worker narrows this to `except MusicBackendError` → mark job `failed` (never a 500); `logger.*` feeds the dashboard activity buffer automatically (`_LogBufferHandler`, lines 119–152, filters `src.*` records).

**Job creation precedent** (regenerate branch, lines 1170–1179):
```python
                job = jq.create_job(
                    character_id=_field(asset, "character_id", ""),
                    job_type=_field(asset, "asset_type", ""),
                    config={"seeds": nearby, "prompt": _field(asset, "prompt", "")},
                )
```
Music variant per RESEARCH D2: `jq.create_job(character_id="music", job_type="music", config={"category": ..., "backend": ...})` then `jq.update_status(job.id, "running")`. Validated transitions are pending→running→completed/failed (`job_queue.py:92–115`; invalid transitions raise `JobError`). `character_id` is an unvalidated string — the `"music"` sentinel is safe.

**JSON polling endpoint pattern** (lines 688–703) — the model for `GET /api/music/jobs`:
```python
    @app.get("/api/jobs")
    async def api_jobs():
        """Live job queue status as JSON."""
        return {
            "jobs": [
                {
                    "id": j.id,
                    "character_id": j.character_id,
                    "job_type": j.job_type,
                    "status": j.status,
                    "count": j.config.get("count", ""),
                    "created_at": j.created_at.isoformat() if j.created_at else "",
                }
                for j in jq.list_jobs(status=None)
            ]
        }
```
Music version filters `jq.list_jobs()` on `job_type == "music"` (or reuses `/api/jobs` with a filter param — planner's Open Question 3) and enriches each entry with `error`/`file` from job config/result.

**Nav link** — `templates/base.html` lines 15–19:
```html
        <nav class="navbar-links">
            <a href="/" class="{% if page == 'dashboard' %}nav-active{% endif %}">Dashboard</a>
            <a href="/motion" class="{% if page == 'motion' %}nav-active{% endif %}">Motion</a>
            <span class="nav-badge">PHASE 1-4</span>
        </nav>
```
Insert `<a href="/music" class="{% if page == 'music' %}nav-active{% endif %}">Music</a>` after the Motion link; templates set `"page": "music"` in context like every other route does.

**Shared manifest writer (divergence):** `_run_music_job`'s file-write + manifest-update step must call the SAME helper functions Plan 08-01 puts in `generate_phase5.py` (import from the scripts module inside the handler) so CLI batch and UI single-song writes share one schema/atomic-write implementation. No existing UI route imports from scripts — this cross-tier import is deliberate (08-02 depends-on 08-01).

---

### 4. `src/review_ui/templates/music.html` (component, server-rendered)

**Analog:** `templates/motion.html` (584 lines, fully read).

**Skeleton header** (lines 1–15):
```html
{% extends "base.html" %}

{% block title %}Motion — Animation Bible &amp; Motion System{% endblock %}

{% block content %}

<div class="entity-header">
  <a href="/" class="btn btn-sm">Back to Dashboard</a>
  <h1>Animation Bible &amp; Motion System</h1>
  <p class="character-meta">
    <strong>Phase 4</strong> &bull;
    Master frame rate: <strong>{{ master_frame_rate }} fps</strong> &bull;
    Export frame rate: <strong>{{ export_frame_rate }} fps</strong>
  </p>
</div>
```

**Prompt-builder section with form-value preservation and result block** (lines 53–100) — copy this structure exactly for the music prompt builder + generate form:
```html
<section class="panel">
  <h2>Animation Prompt Builder</h2>
  <p class="gen-hint">
    Compose a bible-conformant motion prompt from the studio templates.
    Copy the result into any AI backend — nothing is generated or stored here.
  </p>
  <form action="/motion/prompt" method="post" class="prompt-builder-form">
    <div class="prompt-fields">
      <label>Character
        <input type="text" name="character" value="{{ form_values.get('character', 'Lily Bunny') }}" required>
      </label>
      <label>Action Template
        <select name="template">
          {% for t in prompt_templates %}
            <option value="{{ t }}" {% if form_values.get('template', 'walk') == t %}selected{% endif %}>{{ t | title }}</option>
          {% endfor %}
        </select>
      </label>
      ...
    </div>
    <button type="submit" class="btn btn-primary">Build Prompt</button>
  </form>
  {% if prompt_result %}
    <div class="prompt-result">
      <h3>Prompt for {{ prompt_result.character }} &mdash; {{ prompt_result.template | title }}</h3>
      <p class="prompt-text">{{ prompt_result.prompt }}</p>
      <h4>Negative prompt</h4>
      <p class="prompt-text prompt-negative">{{ negative_prompt }}</p>
    </div>
  {% endif %}
</section>
```
Key idioms: `form_values.get('key', 'default')` for sticky forms; `{% if prompt_result %}` conditional result panel; category `<select>` loops over the 24 bible categories exactly like the template select above.

**Library-table sections** (e.g. lines 105–133) for the standards/params panels:
```html
<section class="panel">
  <h2>Motion Cycles ({{ motions | length }})</h2>
  {% if motions %}
    <table class="dashboard-table">
      <thead><tr><th>Cycle</th><th>Frames</th>...</tr></thead>
      <tbody>
        {% for m in motions %}
        <tr><td><strong>{{ m.name }}</strong></td><td>{{ m.frames }}</td>...</tr>
        {% endfor %}
      </tbody>
    </table>
  {% else %}
    <p class="empty-state">No motion cycles loaded.</p>
  {% endif %}
</section>
```
Use for the category-params table (bpm/key_scale/time_signature/duration per category). CSS classes available: `panel`, `dashboard-table`, `badge badge-difficulty`, `tag-list`/`tag`, `standards-card`, `empty-state`, `btn btn-primary`, `prompt-result`, `prompt-negative`.

---

### 5. `tests/test_review_ui_music.py` (test, offline TestClient)

**Analogs:** `tests/test_review_ui_api.py` (route-shape tests) + `tests/test_review_ui_generation.py` (DI fixtures).

**Stub-repo client fixture** (test_review_ui_api.py lines 40–42):
```python
@pytest.fixture
def client():
    return TestClient(create_app(asset_repo=_make_stub_repo()))
```
For music tests the stub repo is unnecessary (music routes ignore repos) — a plain `TestClient(create_app(db_path=str(tmp_path / "m.db")))` or stub-repo client both work; prefer the lightest.

**Page-render test class conventions** (test_review_ui_api.py lines 162–175, 210–217):
```python
class TestMotionPage:
    def test_motion_page_renders(self, client):
        response = client.get("/motion")
        assert response.status_code == 200
        body = response.text
        assert "Animation Bible &amp; Motion System" in body
        ...

class TestMotionPromptBuilder:
    def test_form_renders(self, client):
        body = client.get("/motion").text
        assert 'action="/motion/prompt"' in body
        assert 'name="character"' in body
        # No result until submitted.
        assert "prompt-result" not in body

    def test_build_prompt(self, client):
        response = client.post("/motion/prompt", data={
            "character": "Lily Bunny", "template": "dance", ...
        })
        assert response.status_code == 200
        body = response.text
        assert "Prompt for Lily Bunny &mdash; Dance" in body
        # Negative prompt accompanies every result.
        assert "violent motion" in body
        # Form values are preserved after submit.
        assert 'value="Lily Bunny"' in body
        assert '<option value="dance" selected' in body
```
Mirror as `TestMusicPage` / `TestMusicPromptBuilder`: page renders with all 24 categories; form posts preserve values; preview shows caption + negative without tripping any transport guard.

**Full-pipeline DI fixture when repo-backed wiring matters** (test_review_ui_generation.py lines 18–41):
```python
@pytest.fixture
def sqlite_app(tmp_path):
    """create_app wired to a temp SQLite repo (catalog pre-seeded)."""
    db = str(tmp_path / "ui.db")
    char_repo = SQLiteCharacterRepository(db_path=db)
    asset_repo = SQLiteAssetRepository(db_path=db)
    combined = SQLiteCombinedRepo(char_repo, asset_repo)
    asyncio.run(seed_all(char_repo))
    ...
    app = create_app(
        asset_repo=combined,
        character_repo=char_repo,
        seed_catalog=seed,
    )
    return app, char_repo, asset_repo

@pytest.fixture
def client(sqlite_app):
    app, _, _ = sqlite_app
    return TestClient(app)
```
Music tests inject `music_backend=<mock>` instead of relying on env; point output at `tmp_path`.

**Background-job assertion trick** (test_review_ui_generation.py lines 254–264 proves TestClient flushes background tasks synchronously after the POST response):
```python
    def test_logs_endpoint_returns_generate_entries(self, tmp_path):
        ...
        client.post("/generate", data={...})
        data = client.get("/logs").json()
        entries = data.get("entries", [])
        assert any("Generate queued" in e["message"] for e in entries)
        assert any("UI batch complete" in e["message"] for e in entries)
```
So `POST /music/generate` → immediately `GET /api/music/jobs` can assert terminal status (`completed`/`failed`) with zero sleeps — mock backend completes near-instantly.

**Failure-path assertion style**: suno selection must yield a `failed` job + error message, NOT HTTP 500 (compare `test_unknown_action_returns_400`, test_review_ui_api.py lines 152–155).

---

### 6. `colab/AnimationStudio_Colab_Phase5.ipynb` (notebook, subprocess orchestration)

**Analog:** `colab/AnimationStudio_Colab_Phase4.ipynb` — verified 9 cells: [markdown intro, settings, clone+install, scope preview, regenerate report, pytest, review report, sync, markdown next-steps]. Cell sources extracted verbatim:

**Cell 1 — Settings (`#@param` form controls):**
```python
#@title 1. Settings
REPO_URL = "https://github.com/YOUR_ORG/AnimationStudio.git"  #@param {type:"string"}
BRANCH = "master"  #@param ["master", "colab-gpu"]
SYNC_TO_GITHUB = True  #@param {type:"boolean"}
GIT_NAME = "Colab Studio"  #@param {type:"string"}
GIT_EMAIL = "colab@animationstudio.local"  #@param {type:"string"}
GITHUB_TOKEN = ""  #@param {type:"string"}
```
Phase 5 adds: `RUN_REAL_GENERATION` boolean + `ACESTEP_MODEL` choice (research D3 cell table).

**Cell 2 — Clone + install (`run()` helper, light deps, `--no-deps`):**
```python
#@title 2. Clone repo and install the studio
def run(cmd, **kw):
    print("+ " + " ".join(cmd))
    return subprocess.run(cmd, check=True, **kw)

os.chdir(WORK)
if not os.path.isdir(REPO):
    run(["git", "clone", "--branch", BRANCH, REPO_URL, "AnimationStudio"])
os.chdir(REPO)
run(["git", "checkout", BRANCH])
run(["git", "pull", "origin", BRANCH])
run([sys.executable, "-m", "pip", "install", "-q", "-e", ".", "--no-deps"])
run([sys.executable, "-m", "pip", "install", "-q",
     "fastapi", "uvicorn", "jinja2", "aiosqlite", "python-multipart",
     "pydantic", "scikit-learn"])
print("No GPU needed for Phase 4 — CPU runtime is fine.")
```
Copy verbatim; change the closing prints for Phase 5 (GPU runtime unlocks real songs via ACE-Step; CPU runtime gets mock mode).

**Cells 3–6 shapes:** scope preview (pure-python counts → swap to `AudioBible().list_song_categories()`), regenerate report via `[sys.executable, "scripts/generate_phaseN.py"]` (→ add `--generate --backend acestep|mock`), pytest suites (`pytest tests/test_audio_bible.py tests/test_music_generation.py -q`), display report via IPython Markdown.

**Cell 7 — Sync (PAT basic-auth push or download fallback):**
```python
#@title 7. Sync the refreshed report (GitHub push or manual download)
if SYNC_TO_GITHUB:
    sys.path.insert(0, f"{REPO}/colab")
    from git_sync import _basic_auth_header
    def _run(cmd, **kw):
        print("+ " + " ".join(cmd))
        return subprocess.run(cmd, check=False, cwd=REPO, **kw)

    _run(["git", "config", "user.name", GIT_NAME])
    _run(["git", "config", "user.email", GIT_EMAIL])
    _run(["git", "add", "PHASE4_REPORT.md"])
    dirty = _run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if dirty.stdout.strip():
        _run(["git", "commit", "-m", f"Phase 4 report {datetime.now():%Y-%m-%d %H:%M}"])
        if GITHUB_TOKEN:
            _run(["git", "-c",
                  f"http.extraheader=Authorization: {_basic_auth_header(GITHUB_TOKEN)}",
                  "push", "origin", BRANCH])
        else:
            _run(["git", "push", "origin", BRANCH])
else:
    from google.colab import files
    files.download(f"{REPO}/PHASE4_REPORT.md")
```
Phase 5 stages `Audio/Music/ PHASE5_REPORT.md` instead. Helper reference: `colab/git_sync.py:25–33` builds `"basic " + base64("x-access-token:<token>")`.

**No-analog sub-part:** the ACE-Step service install/start cell (clone `/content/ACE-Step-1.5`, isolated `uv sync` venv, `uv run acestep-api`, health-wait loop). Use the RESEARCH Code Example (lines ~302–330) which CITES vendor README commands; closest stylistic precedent is Cell 2's `run()`/subprocess idiom. Never mix ACE-Step deps into the studio install.

---

### 7. `PHASE5_STATUS.md` (docs update)

**Analog:** itself (84 lines, fully read). Update targets:

- **Deliverables table format** (lines 8–20): three columns `| Deliverable | Status | Evidence |` — append rows for script generation mode, Review UI music hooks, Colab notebook, and `Audio/Music/manifest.json` as artifact inventory source.
- **Reproduction block** (lines 49–60): fenced bash with commented one-liners — add `--generate --backend mock` offline example + live-smoke pointer.
- **Notes/Caveats revision** (lines 62–84): line 82–84 currently claims *"this phase delivers standards + working pipeline wiring, not rendered audio files; audio rendering is left to the AI platforms with prompts built by this package"* — now false for ace-step/mock paths; rewrite per research D4.
- Add a new `## Music Generation Wiring (Phase 8)` section following the heading style of `## Generated Artifact Inventory` (line 37) / `## Reproduction` (line 49).
- Bump the dated verification line at top (lines 3–4: `> Date: 2026-08-03`).

---

## Shared Patterns

### S1. Factory-closure DI + optional injection
**Source:** `src/review_ui/app.py:231–320` (`create_app` kwargs, docstring-documented args, `jq = job_queue or JobQueue()` at :308)
**Apply to:** all four music routes + `music_backend=None` kwarg. Tests inject fakes; production falls back to env-resolved defaults.

### S2. Lazy function-local imports of heavy/new modules
**Source:** `app.py:274–281` (SQLite stack inside factory), `:532` (BatchRunner), `:836` (animation_bible libraries), `:976` (build_animation_prompt), `:1041` (resolve_backend)
**Apply to:** every `src.music_generation` import (routes, `_run_music_job`, script already bootstraps sys.path). Mandatory until Phase 7 lands; house style afterward.

### S3. POST → side effect → `RedirectResponse(referer, 303)`
**Source:** `app.py:1100–1111` (`/generate`), `:1113–1127` (`/seed`), `:1133–1135` (`_get_referer`)
**Apply to:** `POST /music/generate`. Pure previews instead re-render the template with `result + form_values` (`/motion/prompt`, :996–999).

### S4. JobQueue lifecycle state machine
**Source:** `src/pipeline/job_queue.py:66–140` — `create_job(character_id, job_type, config)` → pending; `update_status` validates pending→running→completed/failed (raises `JobError` otherwise); `list_jobs(character_id=None, status=None)` newest-first.
**Apply to:** UI music jobs with `job_type="music"`, `character_id="music"` sentinel, config carrying `{category, backend}` (+ later `error`/`file`). Constructed WITHOUT repository (C2).

### S5. Typed error boundaries, never raw tracebacks
**Source:** CLI exit contract `scripts/generate_phase5.py:188` (`return 0 if passed else 1`); route handlers catch typed errors → log + graceful redirect (`app.py:1183–1212`); API errors → structured JSON 400 (`app.py:1252–1258`)
**Apply to:** catch `MusicBackendError` (covers NotConfigured/BackendUnavailable/GenerationFailed) at both entry points: CLI stderr + exit 1; UI failed-job marking. Suno always raises NotConfigured — must degrade gracefully.

### S6. Root-relative path resolution + atomic writes
**Source:** `scripts/generate_phase5.py:47–50, 176–178` (root join for relative paths). Atomic temp+replace has NO in-codebase precedent yet — RESEARCH prescribes `manifest.json.tmp` + `os.replace()` (Pitfall 6); implement once in the shared manifest writer used by both tiers.

### S7. Offline-first testing discipline
**Source:** fixtures above (S1/S5 analogs); suite runs green with zero network/catalog.db writes; fail-loud transport guards prove dial-free paths (07-02 precedent per RESEARCH D5)
**Apply to:** both new test files. MockBackend everywhere; tmp_path outputs; TestClient's synchronous background-task flush for job assertions.

### S8. Colab operator-artifact conventions
**Source:** Phase 4 notebook Cells 1/2/7 (verbatim above) + `colab/git_sync.py:25–33`
**Apply to:** every Phase 5 notebook cell: `#@title N.` numbering, `#@param` settings, `run()` printer helper, `pip install -e . --no-deps`, PAT http.extraheader push, `files.download` fallback.

## Deliberate Divergences (mandated by RESEARCH — do not "fix" back to analog)

1. **Single-song UI submits vs CLI batch** (Open Question 2 recommendation): `POST /music/generate` handles ONE category per click; 24-category batching stays in `--generate`/notebook. The `/generate` analog batches — do not copy its batch semantics into music routes.
2. **Manifest writer shared across tiers:** Plan 08-02's `_run_music_job` imports the manifest/file-layout helpers from `scripts/generate_phase5.py` (08-01 deliverable) rather than duplicating logic — first cross-tier scripts←UI import in the project; intentional dedup.
3. **catalog.db isolation (C2):** unlike every other route family, music routes dereference neither `repo` nor `char_repo`; JobQueue stays repo-less; grep-gate: phase files add no `sqlite3` import.
4. **acestep alias normalization:** ROADMAP says `acestep`, registry key is `ace-step` — CLI maps aliases before `get_backend` (Pitfall 1). No existing precedent; implement in script only.
5. **Duration policy:** default `duration_s=None` so LOCKED Phase 7 category params apply (Alphabet 75 … Bedtime 120); do NOT translate bible duration labels (`Short`/`Standard`, libraries.py) unless an explicit flag demands it (Pitfall 2).
6. **Report/generation mode orthogonality:** without `--generate`, byte-compatible report behavior (Colab Phase 5 + PHASE5_STATUS Reproduction depend on it).

## Caveats / Partial Analogs

| Sub-pattern | Status | Planner guidance |
|-------------|--------|------------------|
| Batch generate loop + `<category>-<topic-slug>-<seed>.<format>` naming | **Plan-locked, not live code** — `scripts/generate_phase7.py` does not exist (verified); naming comes from 07-02-PLAN Task 3 text | Use RESEARCH Code Example (lines ~211–253) as the composition sketch; verify against real Phase 7 code at execution time (A1) |
| Atomic manifest write (tmp + `os.replace`) | No in-repo precedent | Follow Pitfall 6 prescription; add crash-leftover test |
| ACE-Step notebook service cell | No in-repo analog (external service bring-up) | Vendor-CITED commands in RESEARCH lines ~302–330; isolated venv mandatory (Pitfall 7) |
| `src/music_generation/` surface | Does not exist yet (07 plans committed, unimplemented) | All imports function-local; execution strictly ordered after Phase 7 |

## No Analog Found

*(No wholly orphaned files — every file above has an exact in-repo structural analog. Only the sub-patterns listed under Caveats rely on plan-locked or vendor-cited material.)*

## Metadata

**Analog search scope:** `scripts/`, `tests/`, `src/review_ui/` (incl. `templates/`), `src/pipeline/job_queue.py`, `colab/`, repo-root status docs
**Files read in full:** `scripts/generate_phase5.py` (192), `src/review_ui/app.py` (1260), `tests/test_generate_phase3_assets.py` (206), `tests/test_review_ui_generation.py` (330), `tests/test_review_ui_api.py` (266), `templates/motion.html` (584), `templates/base.html` (38), `PHASE5_STATUS.md` (84), `job_queue.py` (targeted 50–144), Colab Phase 4 cells 1/2/7 + cell census
**Verified absences:** `src/music_generation/` (not on disk), `scripts/generate_phase7.py` (not on disk), `Audio/Music/manifest.json` (dir holds bible markdown only), git HEAD `d5393afc` shows no post-phase4 implementation commits
**Pattern extraction date:** 2026-08-22
