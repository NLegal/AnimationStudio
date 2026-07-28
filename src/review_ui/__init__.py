"""Human Review UI — FastAPI + Jinja2 web interface for asset approval (D-17).

Provides a simple server-rendered web UI for operators to review generated
character assets side-by-side with reference sheets, view Brand Scores and
sub-scores, and approve/reject/refine candidates through the D-15 asset
lifecycle.

Usage::

    from src.review_ui import create_app
    app = create_app(asset_repo=..., character_repo=...)
"""

from .app import create_app

__all__ = ["create_app"]
