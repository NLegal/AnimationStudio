"""FastAPI review application — character dashboard, detail, and side-by-side review.

All routes are server-rendered HTML via Jinja2 templates.  No JavaScript
framework; no build step.  Dependency injection through ``create_app()``
facilitates testing without a live database.

The app also exposes a lightweight generation panel (``POST /generate``) that
queues catalog seeds through the standard pipeline in the background, plus
auto-seeding of the universe catalog when a real repository is injected.
"""

import logging
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Optional

import jinja2
from fastapi import BackgroundTasks, FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.asset_repository.sqlite_repo import NotFoundError
from src.pipeline.job_queue import JobQueue

logger = logging.getLogger(__name__)

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
        universe_dir/world_dir/assets_dir: Catalog paths for the generate panel.

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

    # Lazy batch runner built on first generate request (avoids importing
    # heavy dependencies at import time).
    runner = None
    seeded = False

    app = FastAPI(title="Character Review Studio")

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

    def _dashboard_rows(category: str) -> list[dict]:
        """Rows for one category section, enriched with asset counts."""
        rows = []
        for char in repo.list_characters():
            rec = _record_dict(char)
            if category == "all" or rec["category"] == category:
                assets = repo.find_assets(rec["id"])
                rec["asset_count"] = len(assets)
                rec["pending_count"] = sum(
                    1 for a in assets if _get_state(a) in ("scored", "generated", "shortlisted")
                )
                rows.append(rec)
        order = {"main": 0, "family": 1, "friend": 2, "community": 3, "fantasy": 4}
        rows.sort(key=lambda r: order.get(r["category"], 5))
        return rows

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
        )
        return runner

    def _find_seeds(scope: str, item: str) -> list:
        """Resolve catalog seeds for a scope + optional item filter."""
        from src.universe.catalog import (
            discover_characters,
            discover_environments,
            discover_props,
        )
        scope = (scope or "all").lower()
        item = (item or "").strip()

        groups = {}
        if scope in ("all", "characters"):
            groups["characters"] = discover_characters(universe_dir)
        if scope in ("all", "environments"):
            groups["environments"] = discover_environments(world_dir)
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
    async def dashboard(request: Request):
        """Dashboard listing characters, environments, props, and jobs."""
        await _maybe_seed()
        all_rows = _dashboard_rows("all")
        characters = [r for r in all_rows if r["category"] not in ("environment", "asset")]
        envs = [r for r in all_rows if r["category"] == "environment"]
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
            "review.html",
            {
                "page": "dashboard",
                "characters": characters,
                "environments": envs,
                "prop_categories": prop_categories,
                "jobs": jobs,
                "logs": list(_LOG_BUFFER)[-50:],
                "candidates": [],
            },
        )

    @app.get("/logs")
    async def activity_logs():
        """Recent activity log entries as JSON (polled by the dashboard)."""
        return {"entries": list(_LOG_BUFFER)}

    @app.get("/character/{character_id}", response_class=HTMLResponse)
    async def character_detail(character_id: str, request: Request):
        """Character detail page with asset-type sections."""
        character = repo.get_character(character_id)
        if character is None:
            return HTMLResponse("Character not found", status_code=404)

        rec = _record_dict(character)
        category = rec["category"]
        if category in ("environment",):
            asset_types = ["environment"]
        elif category == "asset":
            asset_types = ["prop"]
        else:
            asset_types = ["reference", "expression", "pose", "outfit"]

        # Group assets by type
        assets = repo.find_assets(character_id)
        by_type: dict[str, list] = {}
        for a in assets:
            by_type.setdefault(_field(a, "asset_type", "unknown"), []).append(a)

        return templates.TemplateResponse(
            request,
            "review.html",
            {
                "page": "character",
                "character": character,
                "rec": rec,
                "asset_types": asset_types,
                "assets_by_type": by_type,
            },
        )

    @app.get("/review/{character_id}", response_class=HTMLResponse)
    async def review_page(
        character_id: str,
        request: Request,
        asset_type: str = Query("expression"),
        batch: bool = Query(False),
        grid: str = Query("2x2"),
    ):
        """Side-by-side review page for a character's candidate assets."""
        character = repo.get_character(character_id)
        if character is None:
            return HTMLResponse("Character not found", status_code=404)

        # Approved reference (used as left-panel comparison)
        approved = repo.find_approved(character_id, asset_type)

        # Candidates awaiting review
        candidates = [
            a for a in repo.find_assets(character_id, asset_type)
            if _field(a, "state") in ("scored", "generated", "shortlisted")
        ]

        # Parse grid dimensions (D-16 configurable batch grids)
        grid_config = {"2x2": (2, 2, 4), "3x3": (3, 3, 9), "4x4": (4, 4, 16)}
        if grid not in grid_config:
            grid = "2x2"  # Normalise unrecognised grids to default
        grid_cols, grid_rows, grid_capacity = grid_config[grid]

        # Dummy score example for template rendering
        sample_scores = {
            "total": 0.82,
            "max": 1.0,
            "components": {
                "prompt_accuracy": {"raw": 0.85, "weighted": 0.17, "weight": 0.20},
                "character_consistency": {"raw": 0.90, "weighted": 0.18, "weight": 0.20},
                "technical_quality": {"raw": 0.75, "weighted": 0.1125, "weight": 0.15},
                "facial_appeal": {"raw": 0.80, "weighted": 0.12, "weight": 0.15},
                "child_friendliness": {"raw": 0.95, "weighted": 0.095, "weight": 0.10},
                "color_harmony": {"raw": 0.70, "weighted": 0.07, "weight": 0.10},
                "silhouette_recognizability": {"raw": 0.60, "weighted": 0.03, "weight": 0.05},
                "style_consistency": {"raw": 0.88, "weighted": 0.044, "weight": 0.05},
            },
        }

        # Build candidate card list with scores
        candidate_cards = []
        for i, asset in enumerate(candidates):
            card = {
                "asset": asset,
                "scores": sample_scores,
                "seed": _field(asset, "seed", 42 + i),
                "model": _field(asset, "model_id", "FLUX.1-dev"),
                "prompt": _field(asset, "prompt", ""),
                "visual_drift": 0.45 + (i * 0.08),  # dummy varied values
            }
            candidate_cards.append(card)

        # Limit to grid capacity in batch mode
        candidates_for_template = candidate_cards[:grid_capacity] if batch else candidate_cards

        return templates.TemplateResponse(
            request,
            "review.html",
            {
                "page": "review",
                "character": character,
                "asset_type": asset_type,
                "approved": approved,
                "candidates": candidates_for_template,
                "batch_mode": batch,
                "grid_cols": grid_cols,
                "grid_rows": grid_rows,
                "grid_capacity": grid_capacity,
                "current_grid": grid,
            },
        )

    # ------------------------------------------------------------------ #
    #  Generation & seeding  (POST /generate, POST /seed)
    # ------------------------------------------------------------------ #

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

    @app.post("/approve/{asset_id}")
    async def approve_asset(asset_id: str, request: Request):
        """Approve: shortlisted → approved (D-15)."""
        try:
            await repo.update_state(asset_id, "approved")
            logger.info("Asset %s approved", asset_id)
        except (NotFoundError, ValueError) as exc:
            logger.warning("Approve failed for %s: %s", asset_id, exc)
        return RedirectResponse(url=_get_referer(request), status_code=303)

    @app.post("/reject/{asset_id}")
    async def reject_asset(
        asset_id: str,
        request: Request,
        reason: str = Form(""),
    ):
        """Reject with optional reason: scored/shortlisted → draft (regeneration)."""
        try:
            await repo.update_state(asset_id, "draft")
            if reason:
                logger.info("Asset %s rejected. Reason: %s", asset_id, reason)
            else:
                logger.info("Asset %s rejected (no reason)", asset_id)
        except (NotFoundError, ValueError) as exc:
            logger.warning("Reject failed for %s: %s", asset_id, exc)
        return RedirectResponse(url=_get_referer(request), status_code=303)

    @app.post("/regenerate/{asset_id}")
    async def regenerate_similar(asset_id: str, request: Request):
        """Regenerate similar: queue a new generation job with nearby seeds."""
        try:
            asset = await repo.get(asset_id)
            if asset is not None and asset.seed is not None:
                nearby = [
                    asset.seed - 5, asset.seed - 3, asset.seed - 1,
                    asset.seed + 1, asset.seed + 3, asset.seed + 5,
                ]
                job = jq.create_job(
                    character_id=asset.character_id,
                    job_type=asset.asset_type,
                    config={"seeds": nearby, "prompt": asset.prompt},
                )
                logger.info(
                    "Regeneration queued: asset=%s job=%s seeds=%s",
                    asset_id, job.id, nearby,
                )
        except Exception as exc:
            logger.warning("Regenerate failed for %s: %s", asset_id, exc)
        return RedirectResponse(url=_get_referer(request), status_code=303)

    @app.post("/promote/{asset_id}")
    async def promote_asset(asset_id: str, request: Request):
        """Approve & Promote: shortlisted → approved → production (two-step)."""
        try:
            await repo.update_state(asset_id, "approved")
            await repo.update_state(asset_id, "production")
            logger.info("Asset %s promoted to production", asset_id)
        except (NotFoundError, ValueError) as exc:
            logger.warning("Promote failed for %s: %s", asset_id, exc)
        return RedirectResponse(url=_get_referer(request), status_code=303)

    return app
