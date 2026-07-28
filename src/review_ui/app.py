"""FastAPI review application — character dashboard, detail, and side-by-side review.

All routes are server-rendered HTML via Jinja2 templates.  No JavaScript
framework; no build step.  Dependency injection through ``create_app()``
facilitates testing without a live database.
"""

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_HERE = Path(__file__).parent
_TEMPLATES = _HERE / "templates"
_STATIC = _HERE / "static"

templates = Jinja2Templates(directory=str(_TEMPLATES))


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
) -> FastAPI:
    """Application factory with optional dependency injection.

    Args:
        asset_repo: Object implementing ``list_characters()``,
            ``get_character(id)``, ``find_assets(...)``,
            ``find_approved(...)``.  Falls back to an in-memory stub.
        character_repo: Alias for *asset_repo* (same object in Phase 1).

    Returns:
        Configured FastAPI application.
    """
    repo = asset_repo or _StubAssetRepo()
    char_repo = character_repo or repo

    app = FastAPI(title="Character Review Studio")

    # Mount static files
    _STATIC.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(_STATIC)), name="static")

    # ------------------------------------------------------------------ #
    #  Routes
    # ------------------------------------------------------------------ #

    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request):
        """Dashboard listing all characters with generation status."""
        characters = repo.list_characters()
        return templates.TemplateResponse(
            "review.html",
            {
                "request": request,
                "page": "dashboard",
                "characters": characters,
                "candidates": [],
            },
        )

    @app.get("/character/{character_id}", response_class=HTMLResponse)
    async def character_detail(character_id: str, request: Request):
        """Character detail page with asset-type sections."""
        character = repo.get_character(character_id)
        if character is None:
            return HTMLResponse("Character not found", status_code=404)

        # Group assets by type
        assets = repo.find_assets(character_id)
        by_type: dict[str, list] = {}
        for a in assets:
            by_type.setdefault(a.get("asset_type", "unknown"), []).append(a)

        return templates.TemplateResponse(
            "review.html",
            {
                "request": request,
                "page": "character",
                "character": character,
                "assets_by_type": by_type,
            },
        )

    @app.get("/review/{character_id}", response_class=HTMLResponse)
    async def review_page(
        character_id: str,
        request: Request,
        asset_type: str = Query("expression"),
        batch: bool = Query(False),
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
            if a.get("state") in ("scored", "generated", "shortlisted")
        ]

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
                "seed": asset.get("seed", 42 + i),
                "model": asset.get("model_id", "FLUX.1-dev"),
                "prompt": asset.get("prompt", ""),
                "visual_drift": 0.45 + (i * 0.08),  # dummy varied values
            }
            candidate_cards.append(card)

        return templates.TemplateResponse(
            "review.html",
            {
                "request": request,
                "page": "review",
                "character": character,
                "asset_type": asset_type,
                "approved": approved,
                "candidates": candidate_cards,
                "batch_mode": batch,
            },
        )

    # ------------------------------------------------------------------ #
    #  Action handlers  (D-15 lifecycle transitions)
    # ------------------------------------------------------------------ #

    @app.post("/approve/{asset_id}")
    async def approve_asset(asset_id: str):
        """Approve: scored → shortlisted (or → approved)."""
        # In production: repo.update_state(asset_id, "shortlisted")
        return RedirectResponse(url="/", status_code=303)

    @app.post("/reject/{asset_id}")
    async def reject_asset(
        asset_id: str,
        reason: str = Form(""),
    ):
        """Reject with optional reason: scored → draft (regeneration)."""
        # In production: repo.update_state(asset_id, "draft")
        return RedirectResponse(url="/", status_code=303)

    @app.post("/regenerate/{asset_id}")
    async def regenerate_similar(asset_id: str):
        """Regenerate similar: queues a new generation job with nearby seeds."""
        # In production: create a new generation job with nearby seeds
        return RedirectResponse(url="/", status_code=303)

    @app.post("/promote/{asset_id}")
    async def promote_asset(asset_id: str):
        """Approve & Promote: shortlisted → approved → production (two-step)."""
        # In production: repo.update_state(asset_id, "approved")
        # then immediately: repo.update_state(asset_id, "production")
        return RedirectResponse(url="/", status_code=303)

    return app
