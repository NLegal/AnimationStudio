"""Studio UI application — realtime review + generation studio for PHASE 1-4.

The Studio covers every image-generation workflow across the production phases:

  * Phase 1  — Characters  (reference, expression, pose, outfit, lighting)
  * Phase 2  — World       (environment, exterior, interior, season,
               time_of_day, weather, camera, vehicle, background)
  * Phase 3  — Assets      (prop reference, view, material, color, lighting)
  * Phase 4  — Motion      (animation bible / motion system library browser)

Routes are server-rendered HTML via Jinja2 templates plus a lightweight JSON
API (``/api/...``) that the ``studio.js`` client uses for realtime interactions
— approving, rejecting, promoting, shortlisting or regenerating an asset
updates its state chip in place, with no full page reload.

The existing form-based POST routes (``/approve``, ``/reject``, ``/promote``,
``/regenerate``) are preserved verbatim so non-JS clients and the test suite
keep working; the JS simply calls the JSON endpoints instead.
"""

import json
import logging
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Optional

import jinja2
from fastapi import BackgroundTasks, FastAPI, Form, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.asset_repository.sqlite_repo import NotFoundError
from src.animation_bible.prompts import (
    ANIMATION_NEGATIVE_BASE,
    MOTION_PROMPT_TEMPLATES,
    _CAMERA_STYLE_DESCRIPTORS,
)
from src.pipeline.job_queue import JobQueue

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Phase metadata (PHASE1.md – PHASE4.md)
# ---------------------------------------------------------------------------

# Character categories (Phase 1) → their full asset-type library.  Turnarounds
# reuse the "reference" type with a variant angle (45/left/right/back/top/bottom).
CHARACTER_ASSET_TYPES = ["reference", "expression", "pose", "outfit", "lighting", "accessory"]

# World categories (Phase 2)
ENVIRONMENT_ASSET_TYPES = [
    "environment", "exterior", "interior", "season",
    "time_of_day", "weather", "camera",
]

# Reusable prop library (Phase 3)
PROP_ASSET_TYPES = ["reference", "view", "material", "color", "lighting"]

# Human labels for the asset-type → generate button wording.
ASSET_TYPE_LABELS = {
    "reference": "references",
    "expression": "expressions",
    "pose": "poses",
    "outfit": "outfits",
    "lighting": "lighting",
    "accessory": "accessories",
    "environment": "environment",
    "exterior": "exteriors",
    "interior": "interiors",
    "season": "seasons",
    "time_of_day": "time of day",
    "weather": "weather",
    "camera": "camera angles",
    "vehicle": "vehicles",
    "background": "backgrounds",
    "view": "views",
    "material": "materials",
    "color": "colors",
}

# All reviewable asset types across phases (for filters / review studio).
ALL_ASSET_TYPES = sorted({
    *CHARACTER_ASSET_TYPES, *ENVIRONMENT_ASSET_TYPES, *PROP_ASSET_TYPES,
    "vehicle", "background",
})

PENDING_STATES = ("scored", "generated", "shortlisted")


def _phase_for_category(category: str) -> int:
    """Map a character-record category to its production phase."""
    if category in ("environment", "vehicle", "background"):
        return 2
    if category == "asset":
        return 3
    return 1


def _asset_types_for(category: str) -> list[str]:
    """The reviewable asset types for an entity category."""
    if category in ("environment",):
        return ENVIRONMENT_ASSET_TYPES
    if category == "vehicle":
        return ["vehicle"]
    if category == "background":
        return ["background"]
    if category == "asset":
        return PROP_ASSET_TYPES
    return CHARACTER_ASSET_TYPES


# ---------------------------------------------------------------------------
# Activity log (in-app buffer surfaced on the dashboard via GET /logs)
# ---------------------------------------------------------------------------

_LOG_BUFFER: deque[dict] = deque(maxlen=250)


class _LogBufferHandler(logging.Handler):
    """Appends formatted log records from src.* loggers to ``_LOG_BUFFER``."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            _LOG_BUFFER.append({
                "time": datetime.fromtimestamp(record.created).strftime("%H:%M:%S"),
                "level": record.levelname,
                "logger": record.name,
                "message": self.format(record),
            })
        except Exception:
            pass


def _is_src_record(record: logging.LogRecord) -> bool:
    return record.name == "src" or record.name.startswith("src.")


_LOG_HANDLER = _LogBufferHandler()
_LOG_HANDLER.setLevel(logging.INFO)
_LOG_HANDLER.setFormatter(logging.Formatter("%(message)s"))
_LOG_HANDLER.addFilter(_is_src_record)


def _ensure_log_buffer_attached() -> None:
    """Attach the in-app log handler once per process and raise src log level."""
    root = logging.getLogger()
    if _LOG_HANDLER not in root.handlers:
        root.addHandler(_LOG_HANDLER)
    logging.getLogger("src").setLevel(logging.INFO)


def _template_field(obj, key: str, default=""):
    """Read a record field whether it is a dict or a pydantic model."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_HERE = Path(__file__).parent
_TEMPLATES = _HERE / "templates"
_STATIC = _HERE / "static"
_PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Disable Jinja2 template cache (cache_size=0) to avoid unhashable key
# errors with starlette's Jinja2Templates wrapper and newer jinja2 releases.
_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(_TEMPLATES)),
    autoescape=jinja2.select_autoescape(),
    cache_size=0,
)
_env.globals["field"] = _template_field
_env.globals["asset_type_label"] = lambda t: ASSET_TYPE_LABELS.get(t, t.replace("_", " ") + "s")
_env.globals["asset_types_for"] = _asset_types_for
templates = Jinja2Templates(env=_env)


# ---------------------------------------------------------------------------
# In-memory stubs (replaced by real repos when injected)
# ---------------------------------------------------------------------------

class _StubAssetRepo:
    """Minimal in-memory stub so the app works without dependencies."""

    def __init__(self):
        self._characters: dict[str, dict] = {}
        self._assets: list[dict] = []

    def list_characters(self):
        return list(self._characters.values())

    def get_character(self, character_id: str):
        return self._characters.get(character_id)

    def find_assets(self, character_id: str, asset_type: Optional[str] = None):
        return [
            a for a in self._assets
            if a["character_id"] == character_id
            and (asset_type is None or a["asset_type"] == asset_type)
        ]

    def find_approved(self, character_id: str, asset_type: str):
        return [
            a for a in self._assets
            if a["character_id"] == character_id
            and a["asset_type"] == asset_type
            and a.get("state") in ("approved", "production")
        ]

    async def get(self, asset_id: str):
        return next((a for a in self._assets if a["id"] == asset_id), None)

    async def update_state(self, asset_id: str, new_state: str) -> None:
        for a in self._assets:
            if a["id"] == asset_id:
                a["state"] = new_state
                return
        raise NotFoundError("Asset", asset_id)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

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
    music_backend=None,
    music_dir: Optional[str] = None,
) -> FastAPI:
    """Application factory with optional dependency injection.

    When no ``asset_repo`` is injected, the app is wired to a real SQLite
    repository (``db_path``, default ``catalog.db``) with the mock generation
    backend and universe auto-seeding, so ``uvicorn src.review_ui:create_app
    --factory`` lists the provisioned catalog and can generate immediately.

    Args:
        asset_repo: Object implementing ``list_characters()``,
            ``get_character(id)``, ``find_assets(...)``,
            ``find_approved(...)`` and the async ``save``/``get``/
            ``update_state`` handlers.  Falls back to a SQLite-backed repo.
        character_repo: Repository with ``save_character``/``find_character_by_name``
            used for seeding and generation (usually the SQLite character repo).
        job_queue: Optional ``JobQueue`` instance for regeneration jobs.
            Falls back to a fresh ``JobQueue()``.
        generation_backend: Optional ``GenerationBackend`` used by the
            ``POST /generate`` panel.  Falls back to the mock backend.
        seed_catalog: Optional async callable ``(char_repo) -> summary`` used
            to auto-seed the universe catalog when the repo is empty.
        db_path: SQLite database path used when ``asset_repo`` is not injected.
        universe_dir/world_dir/assets_dir: Catalog paths for the generate panel
            and image serving.
        persist_generated_images: Write images to disk when the generate panel
            runs (default: off).
        music_backend: Optional music generation backend (``MusicGenerationBackend``).
            Falls back to lazy ``get_backend(None)`` on first music route hit.
        music_dir: Directory for music output files (WAVs + manifest.json).
            Defaults to ``Audio/Music`` under the project root.

    Returns:
        Configured FastAPI application.
    """
    _ensure_log_buffer_attached()

    if asset_repo is None and db_path is not None:
        from src.asset_repository.sqlite_repo import (
            SQLiteAssetRepository,
            SQLiteCharacterRepository,
        )
        from src.universe.batch_generator import resolve_backend
        from src.universe.seed import seed_all
        from src.universe.sqlite_bridge import SQLiteCombinedRepo

        char_repo = SQLiteCharacterRepository(db_path=db_path)
        asset_repo = SQLiteCombinedRepo(char_repo, SQLiteAssetRepository(db_path=db_path))
        if character_repo is None:
            character_repo = char_repo
        if generation_backend is None:
            generation_backend = resolve_backend("mock")
        if seed_catalog is None:

            def _default_seed(
                char_repo_,
                universe_dir=universe_dir,
                world_dir=world_dir,
                assets_dir=assets_dir,
            ):
                return seed_all(
                    char_repo_,
                    universe_dir=universe_dir,
                    world_dir=world_dir,
                    assets_dir=assets_dir,
                )

            seed_catalog = _default_seed

    repo = asset_repo or _StubAssetRepo()
    char_repo = character_repo or repo
    jq = job_queue or JobQueue()

    # Music output directory (C2: never under repo root's catalog.db)
    _music_out = music_dir or str(_PROJECT_ROOT / "Audio" / "Music")

    # Lazy batch runner built on first generate request (avoids importing
    # heavy dependencies at import time).
    runner = None
    seeded = False

    app = FastAPI(title="Animation Studio")

    # Mount static files
    _STATIC.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(_STATIC)), name="static")

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    def _get_state(item) -> str:
        """Read a record's state whether it is a dict or a pydantic model."""
        if isinstance(item, dict):
            return item.get("state", "")
        return getattr(item, "state", "")

    # D-15 forward lifecycle order (used to advance approve/promote through
    # any intermediate states, e.g. scored → approved without a manual
    # shortlist click).
    _D15_CHAIN = [
        "draft", "generated", "scored", "shortlisted",
        "approved", "production", "archived",
    ]

    async def _advance_to(repo, asset_id: str, target: str) -> None:
        """Advance an asset forward along the D-15 chain to ``target``.

        Steps through each intermediate state so the Review UI can approve or
        promote a candidate that is still ``generated``/``scored`` without a
        separate shortlist action.  Raises the usual repo errors for missing
        assets or backward/no-op transitions.
        """
        asset = await repo.get(asset_id)
        if asset is None:
            raise NotFoundError("Asset", asset_id)
        current = _get_state(asset)
        if current not in _D15_CHAIN or target not in _D15_CHAIN:
            raise ValueError(
                f"Invalid state transition: '{current}' -> '{target}'"
            )
        start, end = _D15_CHAIN.index(current), _D15_CHAIN.index(target)
        if end <= start:
            raise ValueError(
                f"Invalid state transition: '{current}' -> '{target}'. "
                f"Already at or past '{target}'."
            )
        for state in _D15_CHAIN[start + 1 : end + 1]:
            await repo.update_state(asset_id, state)

    def _field(item, key: str, default=None):
        """Read a record field whether it is a dict or a pydantic model."""
        if isinstance(item, dict):
            return item.get(key, default)
        return getattr(item, key, default)

    def _record_dict(char) -> dict:
        """Normalise a character record (dict or model) for templates."""
        if isinstance(char, dict):
            return {
                "id": char.get("id", ""),
                "name": char.get("name", ""),
                "category": char.get("category", ""),
                "species": char.get("species", ""),
                "bio_data": char.get("bio_data", {}),
            }
        return {
            "id": getattr(char, "id", ""),
            "name": getattr(char, "name", ""),
            "category": getattr(char, "category", ""),
            "species": getattr(char, "species", ""),
            "bio_data": getattr(char, "bio_data", {}),
        }

    def _score_payload(asset) -> dict:
        """Extract persisted scores for an asset (real DB values, not stubs).

        Returns ``{"total", "components", "present"}``.  ``scores`` is the
        JSON dict written by the pipeline and ``brand_score`` the weighted
        composite; when only per-component scores exist the total is the mean.
        """
        raw = _field(asset, "scores", None)
        brand = _field(asset, "brand_score", None)
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except Exception:
                raw = None
        components: dict[str, float] = {}
        if isinstance(raw, dict):
            for key, val in raw.items():
                if isinstance(val, dict):
                    val = val.get("raw", val.get("score"))
                if isinstance(val, (int, float)):
                    components[key] = round(float(val), 3)
        total = brand if isinstance(brand, (int, float)) else None
        if total is None and components:
            total = round(sum(components.values()) / len(components), 3)
        return {"total": total, "components": components, "present": bool(components)}

    def _dashboard_rows(category: str) -> list[dict]:
        """Rows for one category section, enriched with asset counts."""
        rows = []
        for char in repo.list_characters():
            rec = _record_dict(char)
            if category == "all" or rec["category"] == category:
                assets = repo.find_assets(rec["id"])
                rec["asset_count"] = len(assets)
                rec["pending_count"] = sum(
                    1 for a in assets if _get_state(a) in PENDING_STATES
                )
                rec["phase"] = _phase_for_category(rec["category"])
                rows.append(rec)
        order = {"main": 0, "family": 1, "friend": 2, "community": 3, "fantasy": 4}
        rows.sort(key=lambda r: (order.get(r["category"], 5), r["name"]))
        return rows

    def _candidate_dict(rec: dict, asset) -> dict:
        """Normalise one pending/reviewable asset for templates + JSON API."""
        scores = _score_payload(asset)
        return {
            "asset_id": _field(asset, "id", ""),
            "entity_id": rec["id"],
            "entity": rec["name"],
            "category": rec["category"],
            "phase": _phase_for_category(rec["category"]),
            "asset_type": _field(asset, "asset_type", ""),
            "variant": _field(asset, "variant", ""),
            "state": _get_state(asset),
            "brand_score": scores["total"],
            "components": scores["components"],
            "score_present": scores["present"],
            "seed": _field(asset, "seed"),
            "image_url": f"/asset-image/{_field(asset, 'id', '')}",
            "prompt": _field(asset, "prompt", ""),
        }

    def _collect_candidates(
        asset_type: str = "",
        category: str = "",
        state: str = "",
        limit: int = 200,
    ) -> list[dict]:
        """Every pending candidate across the studio, newest-first.

        ``state`` filters to a single pending state; empty = all pending.
        """
        cands = []
        for char in repo.list_characters():
            rec = _record_dict(char)
            if category and _phase_for_category(rec["category"]) != _phase_for_category(category):
                continue
            for asset in repo.find_assets(rec["id"]):
                st = _get_state(asset)
                if st not in PENDING_STATES:
                    continue
                if state and st != state:
                    continue
                if asset_type and _field(asset, "asset_type", "") != asset_type:
                    continue
                cands.append(_candidate_dict(rec, asset))
        cands.sort(key=lambda c: c["asset_id"])
        return cands[:limit]

    def _overview_stats() -> dict:
        """Dashboard aggregate stats + the top review queue."""
        rows = _dashboard_rows("all")
        stats = {
            "total_entities": len(rows),
            "total_assets": 0,
            "pending": 0,
            "approved": 0,
            "production": 0,
            "by_phase": {1: {"count": 0, "pending": 0},
                         2: {"count": 0, "pending": 0},
                         3: {"count": 0, "pending": 0}},
            "by_state": {s: 0 for s in _D15_CHAIN},
        }
        for rec in rows:
            phase = rec["phase"]
            if phase in stats["by_phase"]:
                stats["by_phase"][phase]["count"] += 1
                stats["by_phase"][phase]["pending"] += rec["pending_count"]
            assets = repo.find_assets(rec["id"])
            stats["total_assets"] += len(assets)
            for a in assets:
                st = _get_state(a)
                if st in stats["by_state"]:
                    stats["by_state"][st] += 1
                if st in PENDING_STATES:
                    stats["pending"] += 1
                if st in ("approved", "production"):
                    stats["approved"] += 1
                if st == "production":
                    stats["production"] += 1
        stats["review_queue"] = _collect_candidates(limit=8)
        return stats

    async def _maybe_seed() -> None:
        """Seed the universe catalog once if the repo is empty and a seeder exists."""
        nonlocal seeded
        if seeded:
            return
        seeded = True
        if seed_catalog is None or not hasattr(char_repo, "save_character"):
            return
        try:
            if len(repo.list_characters()) == 0:
                summary = await seed_catalog(char_repo)
                logger.info("Auto-seeded universe catalog: %s", summary)
        except Exception as exc:
            logger.warning("Auto-seed failed: %s", exc)

    def _get_runner():
        """Lazily build the batch runner for the generate panel."""
        nonlocal runner
        if runner is not None:
            return runner
        from src.universe.batch_generator import BatchRunner
        runner = BatchRunner(
            asset_repo=repo,
            char_repo=char_repo,
            backend=generation_backend,
            persist_images=persist_generated_images,
            universe_dir=universe_dir,
            world_dir=world_dir,
            assets_dir=assets_dir,
        )
        return runner

    def _resolve_image_path(file_path: str) -> Optional[Path]:
        """Map a stored asset ``file_path`` to an existing file on disk.

        Paths are stored repository-root-relative (``Universe/Characters/...``)
        so the same DB works across checkouts.  Absolute paths are used as-is.
        """
        if not file_path:
            return None
        p = Path(file_path)
        if p.is_absolute():
            return p if p.exists() else None
        catalog_root = Path(universe_dir).parent
        candidate = catalog_root / p
        return candidate if candidate.exists() else None

    def _find_seeds(scope: str, item: str) -> list:
        """Resolve catalog seeds for a scope + optional item filter."""
        from src.universe.catalog import (
            discover_backgrounds,
            discover_characters,
            discover_environments,
            discover_props,
            discover_vehicles,
        )
        scope = (scope or "all").lower()
        item = (item or "").strip()

        groups = {}
        if scope in ("all", "characters"):
            groups["characters"] = discover_characters(universe_dir)
        if scope in ("all", "environments"):
            groups["environments"] = discover_environments(world_dir)
        if scope in ("all", "vehicles"):
            groups["vehicles"] = discover_vehicles(world_dir)
        if scope in ("all", "backgrounds"):
            groups["backgrounds"] = discover_backgrounds(world_dir)
        if scope in ("all", "props"):
            groups["props"] = discover_props(world_dir, assets_dir)

        if not item:
            return [seed for group in groups.values() for seed in group]

        item_l = item.lower()
        for group in groups.values():
            for seed in group:
                name = getattr(seed, "name", "") or ""
                asset_id = getattr(seed, "asset_id", "") or ""
                if item_l in name.lower() or item_l in asset_id.lower():
                    return [seed]

        # Category filter for props
        if "props" in groups:
            matches = [
                s for s in groups["props"]
                if (s.category or "").lower() == item.lower()
            ]
            if matches:
                return matches
        return []

    # ------------------------------------------------------------------ #
    #  Routes
    # ------------------------------------------------------------------ #

    @app.get("/", response_class=HTMLResponse)
    async def dashboard(
        request: Request,
        props_category: str = Query("", description="Filter the prop library table by category"),
        props_limit: int = Query(50, ge=1, le=500, description="Max prop rows to render"),
    ):
        """Dashboard: phase overview cards, review queue, live jobs + log."""
        await _maybe_seed()
        all_rows = _dashboard_rows("all")
        characters = [r for r in all_rows if r["category"] not in ("environment", "asset", "vehicle", "background")]
        envs = [r for r in all_rows if r["category"] in ("environment", "vehicle", "background")]
        props = [r for r in all_rows if r["category"] == "asset"]

        # Aggregate the asset library by its category field.
        prop_categories: dict[str, dict] = {}
        for p in props:
            cat = p.get("bio_data", {}).get("category", "") or "Uncategorized"
            entry = prop_categories.setdefault(
                cat, {"name": cat, "count": 0, "pending": 0}
            )
            entry["count"] += 1
            entry["pending"] += p["pending_count"]
        prop_categories = sorted(prop_categories.values(), key=lambda e: -e["count"])

        # Phase 3 entity browser — per-prop rows with View/Review/Generate,
        # filterable by category (the library holds 1,500+ props, so the
        # table is capped at ``props_limit`` rows).
        cat_filter = (props_category or "").strip()
        if cat_filter:
            props_rows = [
                p for p in props
                if (p.get("bio_data", {}).get("category", "") or "Uncategorized") == cat_filter
            ]
        else:
            props_rows = list(props)
        props_total = len(props_rows)
        props_rows = props_rows[:props_limit]

        jobs = [
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

        return templates.TemplateResponse(
            request,
            "dashboard.html",
            {
                "page": "dashboard",
                "characters": characters,
                "environments": envs,
                "prop_categories": prop_categories,
                "props_rows": props_rows,
                "props_total": props_total,
                "props_limit": props_limit,
                "props_category": cat_filter,
                "jobs": jobs,
                "logs": list(_LOG_BUFFER)[-50:],
                "overview": _overview_stats(),
                "asset_types": ALL_ASSET_TYPES,
            },
        )

    @app.get("/logs")
    async def activity_logs():
        """Recent activity log entries as JSON (polled by the dashboard)."""
        return {"entries": list(_LOG_BUFFER)}

    @app.get("/api/overview")
    async def api_overview():
        """Dashboard stats as JSON (polled for realtime counter updates)."""
        await _maybe_seed()
        return _overview_stats()

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

    @app.get("/api/candidates")
    async def api_candidates(
        asset_type: str = Query(""),
        category: str = Query(""),
        state: str = Query(""),
        limit: int = Query(50),
    ):
        """The pending review queue as JSON (filters optional)."""
        await _maybe_seed()
        return {
            "candidates": _collect_candidates(
                asset_type=asset_type, category=category,
                state=state, limit=limit,
            )
        }

    @app.get("/api/review/next")
    async def api_review_next(
        asset_type: str = Query(""),
        category: str = Query(""),
        state: str = Query(""),
    ):
        """The oldest pending candidate for the review studio."""
        await _maybe_seed()
        queue = _collect_candidates(
            asset_type=asset_type, category=category, state=state, limit=1
        )
        return {"candidate": queue[0] if queue else None, "remaining": len(queue)}

    @app.get("/character/{character_id}", response_class=HTMLResponse)
    async def character_detail(character_id: str, request: Request):
        """Entity detail page with phase-aware asset-type sections."""
        character = repo.get_character(character_id)
        if character is None:
            return HTMLResponse("Character not found", status_code=404)

        rec = _record_dict(character)
        asset_types = _asset_types_for(rec["category"])

        # Group assets by type (enriched with real scores + image URLs).
        assets = repo.find_assets(character_id)
        by_type: dict[str, list] = {}
        for a in assets:
            by_type.setdefault(_field(a, "asset_type", "unknown"), []).append(
                _candidate_dict(rec, a)
            )

        return templates.TemplateResponse(
            request,
            "entity_detail.html",
            {
                "page": "entity",
                "entity": character,
                "rec": rec,
                "asset_types": asset_types,
                "assets_by_type": by_type,
                "phase": _phase_for_category(rec["category"]),
            },
        )

    @app.get("/review/{character_id}", response_class=HTMLResponse)
    async def review_page(
        character_id: str,
        request: Request,
        asset_type: str = Query(""),
        batch: bool = Query(False),
        grid: str = Query("2x2"),
    ):
        """Side-by-side review page for a character's candidate assets."""
        character = repo.get_character(character_id)
        if character is None:
            return HTMLResponse("Character not found", status_code=404)

        rec = _record_dict(character)

        # Phase-scoped asset-type tabs (characters/world/props each get
        # their own library tabs on the review page).
        entity_asset_types = _asset_types_for(rec["category"])

        # Default to the entity's primary asset type (expression for
        # characters, environment for worlds, reference for props).
        if not asset_type or asset_type not in entity_asset_types:
            asset_type = entity_asset_types[0]

        # Approved reference (used as left-panel comparison)
        approved = repo.find_approved(character_id, asset_type)

        # Candidates awaiting review
        candidates = [
            a for a in repo.find_assets(character_id, asset_type)
            if _field(a, "state") in PENDING_STATES
        ]

        # Parse grid dimensions (D-16 configurable batch grids)
        grid_config = {"2x2": (2, 2, 4), "3x3": (3, 3, 9), "4x4": (4, 4, 16)}
        if grid not in grid_config:
            grid = "2x2"  # Normalise unrecognised grids to default
        grid_cols, grid_rows, grid_capacity = grid_config[grid]

        # Build candidate card list with real persisted scores.
        candidate_cards = []
        for asset in candidates:
            card = _candidate_dict(rec, asset)
            card["model"] = _field(asset, "model_id", "FLUX.1-dev")
            candidate_cards.append(card)

        # Limit to grid capacity in batch mode
        candidates_for_template = candidate_cards[:grid_capacity] if batch else candidate_cards

        return templates.TemplateResponse(
            request,
            "review.html",
            {
                "page": "review",
                "entity": character,
                "rec": rec,
                "asset_type": asset_type,
                "approved": approved,
                "candidates": candidates_for_template,
                "batch_mode": batch,
                "grid_cols": grid_cols,
                "grid_rows": grid_rows,
                "grid_capacity": grid_capacity,
                "current_grid": grid,
                "asset_types": entity_asset_types,
            },
        )

    def _motion_page_context(prompt_result: dict | None = None,
                             form_values: dict | None = None) -> dict:
        """Build the Phase 4 Animation Bible browser context."""
        from src.animation_bible import libraries as lib

        def _motion_dict(m):
            return {
                "name": m.motion, "frames": m.base_frames, "loopable": m.looping,
                "description": m.description,
                "difficulty": getattr(m, "complexity", ""),
            }

        def _shot_dict(s):
            return {
                "name": s.name, "description": s.description,
                "min_frames": getattr(s, "min_frames", ""),
                "max_frames": getattr(s, "max_frames", ""),
                "movement": getattr(s, "movement", ""),
                "use": getattr(s, "use", ""),
            }

        def _gesture_dict(g):
            return {
                "name": g.name, "frames": g.frames, "arm": g.arm,
                "hand": g.hand, "posture": g.posture, "use": g.use,
                "note": getattr(g, "note", ""),
            }

        def _transition_dict(t):
            return {
                "name": t.name, "description": t.description,
                "min_frames": getattr(t, "min_frames", ""),
                "max_frames": getattr(t, "max_frames", ""),
                "curve": getattr(t, "curve", ""), "use": getattr(t, "use", ""),
            }

        def _expression_dict(e):
            return {
                "emotion": e.emotion,
                "description": getattr(e, "description", ""),
                "levels": [
                    {"intensity": lvl.intensity, "name": lvl.name, "face": lvl.face}
                    for lvl in getattr(e, "levels", ())
                ],
            }

        def _loco_dict(v):
            return {
                "name": v.name,
                "frames_per_step": v.frames_per_step,
                "frames_per_stride": v.frames_per_stride,
                "speed_percent": v.speed_percent,
                "easing": getattr(v, "easing", ""),
                "description": v.description,
            }

        data = {
            "philosophy": lib.PHILOSOPHY,
            "forbidden": lib.FORBIDDEN_MOTION,
            "quality_checks": lib.QUALITY_CHECKS,
            "master_frame_rate": lib.MASTER_FRAME_RATE,
            "export_frame_rate": lib.EXPORT_FRAME_RATE,
            "motions": [_motion_dict(m) for m in lib.MOTION_CYCLES],
            "camera_shots": [_shot_dict(s) for s in lib.CAMERA_SHOTS],
            "gestures": [_gesture_dict(g) for g in lib.GESTURES],
            "transitions": [_transition_dict(t) for t in lib.SCENE_TRANSITIONS],
            "expressions": [_expression_dict(e) for e in lib.FACIAL_EXPRESSIONS],
            "idle_layers": [{
                "name": l.name, "rate": l.rate, "frames": l.frames,
                "amplitude": l.amplitude, "description": l.description,
            } for l in lib.IDLE_LAYERS],
            "interactions": [{
                "name": i.name, "description": i.description,
                "total_frames": i.total_frames, "loopable": i.loopable,
            } for i in lib.INTERACTIONS],
            # Locomotion standards (walk / run variants)
            "walk_variants": [_loco_dict(v) for v in lib.WALK_VARIANTS],
            "run_variants": [_loco_dict(v) for v in lib.RUN_VARIANTS],
            # Jump & dance libraries
            "jumps": [{
                "name": j.name, "total_frames": j.total_frames,
                "height_percent": j.height_percent, "loopable": j.loopable,
                "phases": list(getattr(j, "phases", ())), "description": j.description,
            } for j in lib.JUMP_CYCLES],
            "dances": [{
                "name": d.name, "frames": d.frames, "bpm": d.bpm,
                "difficulty": d.difficulty, "spacing": d.spacing,
                "loopable": d.loopable, "description": d.description,
            } for d in lib.DANCE_LOOPS],
            "dance_bpm": lib.DANCE_BPM,
            # Eye & mouth animation
            "blink_types": [{
                "name": b.name, "frames": b.frames,
                "duration": b.duration, "usage": b.usage,
            } for b in lib.BLINK_TYPES],
            "mouth_shapes": sorted(lib.MOUTH_SHAPES.items()),
            # Physics & secondary motion
            "physics_rules": [{
                "name": r.name, "value": r.value, "notes": r.notes,
            } for r in lib.PHYSICS_RULES],
            "cloth_elements": [{
                "name": c.name, "delay_frames": c.delay_frames,
                "amplitude": c.amplitude, "settle_frames": c.settle_frames,
                "description": c.description,
            } for c in lib.CLOTH_ELEMENTS],
            # Timing standards
            "pacing_standards": [{
                "age": p.age, "multiplier": p.multiplier, "notes": p.notes,
            } for p in lib.PACING_STANDARDS],
            # Prompt builder inputs
            "prompt_templates": sorted(MOTION_PROMPT_TEMPLATES.keys()),
            "camera_styles": sorted(_CAMERA_STYLE_DESCRIPTORS.keys()),
            "negative_prompt": ANIMATION_NEGATIVE_BASE,
            "prompt_result": prompt_result or {},
            "form_values": form_values or {},
        }
        return data

    @app.get("/motion", response_class=HTMLResponse)
    async def motion_page(request: Request):
        """Phase 4 — Animation Bible & Motion System library browser."""
        return templates.TemplateResponse(
            request, "motion.html", _motion_page_context()
        )

    @app.post("/motion/prompt", response_class=HTMLResponse)
    async def motion_prompt(request: Request):
        """Build an animation prompt from the bible templates (text only).

        Pure ``build_animation_prompt()`` evaluation — no database writes and
        no image generation.
        """
        form = await request.form()
        character = str(form.get("character", "")).strip() or "Lily Bunny"
        template = str(form.get("template", "")).strip() or "walk"
        emotion = str(form.get("emotion", "")).strip() or "happiness"
        environment = str(form.get("environment", "")).strip()
        camera_shot = str(form.get("camera_shot", "")).strip() or "medium"
        details = str(form.get("details", "")).strip()

        if template not in MOTION_PROMPT_TEMPLATES:
            template = "walk"

        from src.animation_bible.prompts import build_animation_prompt
        prompt = build_animation_prompt(
            character=character,
            action=template,
            emotion=emotion,
            environment=environment,
            camera_shot=camera_shot,
            details=(details,) if details else (),
            template=template,
        )
        result = {
            "prompt": prompt,
            "character": character,
            "template": template,
        }
        values = {
            "character": character, "template": template, "emotion": emotion,
            "environment": environment, "camera_shot": camera_shot,
            "details": details,
        }
        return templates.TemplateResponse(
            request, "motion.html",
            _motion_page_context(prompt_result=result, form_values=values),
        )

    # ------------------------------------------------------------------ #
    #  Music Generation (Phase 8 — browse / prompt preview / single-song) #
    # ------------------------------------------------------------------ #

    def _music_page_context(preview=None, form_values=None):
        """Build the Phase 5 Music Generation browse-page context."""
        from src.audio_bible import AudioBible
        from src.music_generation.backends import resolve_music_params

        bible = AudioBible()
        categories = bible.list_song_categories()
        category_params = []
        for cat in categories:
            params = resolve_music_params(cat)
            category_params.append({
                "name": cat,
                "bpm": params.bpm,
                "key_scale": params.key_scale,
                "time_signature": params.time_signature,
                "duration_s": params.duration_s,
            })

        recent_music_jobs = [
            {
                "id": j.id,
                "status": j.status,
                "category": j.config.get("category", ""),
                "topic": j.config.get("topic", ""),
                "error": j.config.get("error", ""),
                "file": j.config.get("file", ""),
            }
            for j in jq.list_jobs()
            if j.job_type == "music"
        ]

        return {
            "page": "music",
            "category_params": category_params,
            "categories": categories,
            "preview": preview or {},
            "form_values": form_values or {},
            "recent_music_jobs": recent_music_jobs,
        }

    @app.get("/music", response_class=HTMLResponse)
    async def music_page(request: Request):
        """Phase 5 — Music Generation browser and job launcher."""
        return templates.TemplateResponse(
            request, "music.html", _music_page_context()
        )

    @app.post("/music/generate")
    async def music_generate(
        request: Request,
        background_tasks: BackgroundTasks,
        category: str = Form("Alphabet"),
        topic: str = Form(""),
        backend: str = Form(""),
    ):
        """Queue a single song generation job and redirect back."""
        job = jq.create_job(
            character_id="music",
            job_type="music",
            config={"category": category, "topic": topic, "backend": backend},
        )
        jq.update_status(job.id, "running")
        background_tasks.add_task(
            _run_music_job, job.id, category, topic, backend,
        )
        logger.info(
            "Music job queued: category=%s topic=%s backend=%s",
            category, topic, backend,
        )
        return RedirectResponse(url=_get_referer(request), status_code=303)

    def _run_music_job(job_id, category, topic, backend_name):
        """Background worker: generate one song and write WAV + manifest entry."""
        import os as _os

        from src.music_generation import MusicBackendError, build_music_request, get_backend

        # Manifest helpers from scripts/generate_phase5 (shared schema, C2)
        from scripts.generate_phase5 import (
            atomic_write_manifest,
            load_manifest,
            song_filename,
            upsert_entry,
        )

        try:
            if backend_name:
                backend = get_backend(backend_name)
            elif music_backend is not None:
                backend = music_backend
            else:
                backend = get_backend(None)
            request = build_music_request(category, topic)
            result = backend.generate(request)

            fname = song_filename(category, topic, result.seed, result.format)
            fpath = _os.path.join(_music_out, fname)
            _os.makedirs(_music_out, exist_ok=True)
            with open(fpath, "wb") as fh:
                fh.write(result.audio)

            manifest_path = _os.path.join(_music_out, "manifest.json")
            manifest = load_manifest(manifest_path)
            upsert_entry(manifest, {
                "file": fname,
                "category": category,
                "topic": request.topic,
                "seed": result.seed,
                "backend": result.backend,
                "format": result.format,
                "bytes": len(result.audio),
                "duration_s": request.duration_s,
                "bpm": 0,
                "key_scale": "",
                "time_signature": "",
                "job_id": result.job_id,
                "generated_at": "",
            })
            atomic_write_manifest(manifest_path, manifest)

            # Fill in music params
            from src.music_generation.backends import resolve_music_params
            params = resolve_music_params(category)
            entry = manifest.get("songs", [{}])[-1]
            entry["bpm"] = params.bpm
            entry["key_scale"] = params.key_scale
            entry["time_signature"] = params.time_signature
            atomic_write_manifest(manifest_path, manifest)

            jq.update_status(job_id, "completed")
            # Store file reference in job config
            job = jq.get_job(job_id)
            if job is not None:
                job.config["file"] = fname

            logger.info("Music job %s completed: %s", job_id, fname)

        except MusicBackendError as exc:
            logger.error("Music job %s failed: %s", job_id, exc)
            job = jq.get_job(job_id)
            if job is not None:
                job.config["error"] = str(exc)
            jq.update_status(job_id, "failed")

    @app.get("/api/music/jobs")
    async def api_music_jobs():
        """JSON status list for music generation jobs."""
        jobs = []
        for j in jq.list_jobs():
            if j.job_type != "music":
                continue
            jobs.append({
                "id": j.id,
                "status": j.status,
                "category": j.config.get("category", ""),
                "error": j.config.get("error", ""),
                "file": j.config.get("file", ""),
            })
        return {"jobs": jobs}

    # ------------------------------------------------------------------ #
    #  Generation & seeding  (POST /generate, POST /seed)
    # ------------------------------------------------------------------ #

    @app.get("/asset-image/{asset_id}")
    async def asset_image(asset_id: str):
        """Serve a generated asset image from disk.

        Serves the persisted file for an asset (written at generation time or
        by the export script).  Returns 404 when no image exists yet so the UI
        can show a placeholder instead of failing the whole page.
        """
        getter = getattr(repo, "get", None)
        if getter is None:
            return HTMLResponse("Not found", status_code=404)
        try:
            asset = await getter(asset_id)
        except Exception:
            asset = None
        if asset is None:
            return HTMLResponse("Not found", status_code=404)
        path = _resolve_image_path(_field(asset, "file_path", "") or "")
        if path is None:
            return HTMLResponse("Not found", status_code=404)
        return FileResponse(str(path), media_type="image/png")

    def _repo_can_generate() -> bool:
        """A stub repo cannot persist generated assets; only real repos can."""
        return all(hasattr(repo, m) for m in ("save", "get", "update_state"))

    async def _background_batch(
        scope: str,
        item: str,
        asset_type: str,
        count: int,
        backend_name: str,
        variant: str,
        limit: int,
    ) -> None:
        """Run a batch generation in the background and log the summary."""
        from src.universe.batch_generator import resolve_backend
        backend = resolve_backend(backend_name) if backend_name else None

        kind_map = {
            "characters": "character",
            "environments": "environment",
            "vehicles": "vehicle",
            "backgrounds": "background",
            "props": "prop",
        }
        scope_names = list(kind_map) if (scope or "").lower() == "all" else [(scope or "characters").lower()]

        for scope_name in scope_names:
            if scope_name not in kind_map:
                continue
            kind = kind_map[scope_name]
            try:
                seeds = _find_seeds(scope_name, item)
            except Exception as exc:
                logger.exception("Generate: seed discovery failed: %s", exc)
                return
            if not seeds:
                continue
            shortlist = min(count, 5)
            try:
                result = await _get_runner().run_seeds(
                    seeds,
                    kind,
                    count=count,
                    shortlist=shortlist,
                    limit=limit or None,
                    asset_type=asset_type or None,
                    variant=variant or "front",
                    batch_id=f"ui_{int(time.time())}",
                    backend=backend,
                )
            except Exception as exc:
                logger.exception("Generate: batch run failed: %s", exc)
                return
            logger.info(
                "UI batch complete: kind=%s attempted=%s generated=%s shortlisted=%s",
                result["kind"], result["items_attempted"],
                result["total_generated"], result["total_shortlisted"],
            )

    @app.post("/generate")
    async def generate(
        request: Request,
        background_tasks: BackgroundTasks,
        scope: str = Form("characters"),
        item: str = Form(""),
        asset_type: str = Form(""),
        count: int = Form(4),
        backend: str = Form("mock"),
        variant: str = Form("front"),
        limit: int = Form(10),
    ):
        """Queue a background generation batch for catalog seeds."""
        if not _repo_can_generate():
            return RedirectResponse(
                url=_get_referer(request), status_code=303
            )
        seeds = _find_seeds(scope, item)
        if not seeds:
            return RedirectResponse(url=_get_referer(request), status_code=303)

        background_tasks.add_task(
            _background_batch, scope, item, asset_type, count, backend, variant, limit
        )
        logger.info("Generate queued: scope=%s item=%r count=%s backend=%s", scope, item, count, backend)
        return RedirectResponse(url=_get_referer(request), status_code=303)

    @app.post("/seed")
    async def seed(request: Request, background_tasks: BackgroundTasks):
        """Seed the universe catalog from the markdown docs (idempotent)."""
        if seed_catalog is None or not hasattr(char_repo, "save_character"):
            return RedirectResponse(url=_get_referer(request), status_code=303)

        async def _seed():
            try:
                summary = await seed_catalog(char_repo)
                logger.info("Seeded universe: %s", summary)
            except Exception as exc:
                logger.exception("Seed failed: %s", exc)

        background_tasks.add_task(_seed)
        return RedirectResponse(url=_get_referer(request), status_code=303)

    # ------------------------------------------------------------------ #
    #  Action handlers  (D-15 lifecycle transitions)
    # ------------------------------------------------------------------ #

    def _get_referer(request: Request) -> str:
        """Extract the referer URL from the request (with safe fallback)."""
        return request.headers.get("referer", "/")

    async def _apply_action(asset_id: str, action: str, reason: str = ""):
        """Run a lifecycle action and return ``(ok, message, new_state)``.

        Shared by the HTML form routes and the JSON API so both paths behave
        identically.  ``regenerate`` returns a job id instead of a state.
        """
        if action == "reject":
            await repo.update_state(asset_id, "draft")
            if reason:
                logger.info("Asset %s rejected. Reason: %s", asset_id, reason)
            else:
                logger.info("Asset %s rejected (no reason)", asset_id)
            return True, "Rejected", "draft"
        if action == "shortlist":
            await _advance_to(repo, asset_id, "shortlisted")
            logger.info("Asset %s shortlisted", asset_id)
            return True, "Shortlisted", "shortlisted"
        if action == "approve":
            await _advance_to(repo, asset_id, "approved")
            logger.info("Asset %s approved", asset_id)
            return True, "Approved", "approved"
        if action == "promote":
            await _advance_to(repo, asset_id, "production")
            logger.info("Asset %s promoted to production", asset_id)
            return True, "Promoted to production", "production"
        if action == "regenerate":
            asset = await repo.get(asset_id)
            seed = _field(asset, "seed", None) if asset is not None else None
            if seed is not None:
                nearby = [
                    seed - 5, seed - 3, seed - 1,
                    seed + 1, seed + 3, seed + 5,
                ]
                job = jq.create_job(
                    character_id=_field(asset, "character_id", ""),
                    job_type=_field(asset, "asset_type", ""),
                    config={"seeds": nearby, "prompt": _field(asset, "prompt", "")},
                )
                logger.info(
                    "Regeneration queued: asset=%s job=%s seeds=%s",
                    asset_id, job.id, nearby,
                )
                return True, "Regeneration queued", "", job.id
            return True, "No seed to regenerate from", ""
        raise ValueError(f"Unknown action: {action}")

    @app.post("/approve/{asset_id}")
    async def approve_asset(asset_id: str, request: Request):
        """Approve: any candidate state → approved (D-15, shortlist implied)."""
        try:
            await _apply_action(asset_id, "approve")
        except (NotFoundError, ValueError) as exc:
            logger.warning("Approve failed for %s: %s", asset_id, exc)
        return RedirectResponse(url=_get_referer(request), status_code=303)

    @app.post("/reject/{asset_id}")
    async def reject_asset(
        asset_id: str,
        request: Request,
        reason: str = Form(""),
    ):
        """Reject with optional reason: candidate → draft (regeneration)."""
        try:
            await _apply_action(asset_id, "reject", reason)
        except (NotFoundError, ValueError) as exc:
            logger.warning("Reject failed for %s: %s", asset_id, exc)
        return RedirectResponse(url=_get_referer(request), status_code=303)

    @app.post("/regenerate/{asset_id}")
    async def regenerate_similar(asset_id: str, request: Request):
        """Regenerate similar: queue a new generation job with nearby seeds."""
        try:
            await _apply_action(asset_id, "regenerate")
        except Exception as exc:
            logger.warning("Regenerate failed for %s: %s", asset_id, exc)
        return RedirectResponse(url=_get_referer(request), status_code=303)

    @app.post("/promote/{asset_id}")
    async def promote_asset(asset_id: str, request: Request):
        """Approve & Promote: any candidate state → production (two-step)."""
        try:
            await _apply_action(asset_id, "promote")
        except (NotFoundError, ValueError) as exc:
            logger.warning("Promote failed for %s: %s", asset_id, exc)
        return RedirectResponse(url=_get_referer(request), status_code=303)

    # ------------------------------------------------------------------ #
    #  Realtime JSON action API  (used by studio.js)
    # ------------------------------------------------------------------ #

    @app.post("/api/assets/{asset_id}/{action}")
    async def api_asset_action(
        asset_id: str,
        action: str,
        reason: str = Form(""),
    ):
        """Realtime lifecycle action → ``{ok, message, state, job_id}`` JSON.

        Allowed actions: approve | reject | promote | shortlist | regenerate.
        The frontend updates the asset's state chip in place from the response,
        so a click takes effect immediately without a page reload.
        """
        try:
            result = await _apply_action(asset_id, action, reason)
            ok, message, new_state = result[0], result[1], result[2]
            payload = {
                "ok": ok,
                "message": message,
                "asset_id": asset_id,
                "action": action,
                "state": new_state,
            }
            if len(result) > 3:
                payload["job_id"] = result[3]
            return JSONResponse(payload)
        except (NotFoundError, ValueError) as exc:
            logger.warning("API %s failed for %s: %s", action, asset_id, exc)
            return JSONResponse(
                {"ok": False, "error": str(exc), "asset_id": asset_id,
                 "action": action},
                status_code=400,
            )

    return app
