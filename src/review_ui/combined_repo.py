"""Shared Review UI helpers used by the generation scripts.

Extracted from generate_identity_lock / generate_face_lock /
generate_body_lock / generate_wardrobe to remove copy-paste duplication.

- :class:`CombinedRepo`: adapts CharacterRepository + AssetRepository into the
  single object shape expected by :func:`review_ui.app.create_app`.
- :func:`check_comfyui`: verifies ComfyUI is reachable.
"""

from typing import Optional

from src.asset_repository.sqlite_repo import (
    SQLiteAssetRepository,
    SQLiteCharacterRepository,
)
from src.models.schemas import AssetModel


class CombinedRepo:
    """Adapter that wraps CharacterRepository + AssetRepository for create_app().

    The Review UI expects a single object with methods from both repos.
    GET routes call methods synchronously (no await), POST routes use async.
    We bridge by storing raw connections for sync reads and delegating
    writes to the async repo methods.
    """

    def __init__(self, char_repo: SQLiteCharacterRepository, asset_repo: SQLiteAssetRepository):
        self._char = char_repo
        self._asset = asset_repo

    # -- Character methods (sync — called from GET routes) --
    def list_characters(self) -> list:
        """Sync version: read characters directly from SQLite."""
        conn = self._char._get_conn()
        rows = conn.execute(
            "SELECT * FROM characters ORDER BY created_at"
        ).fetchall()
        return [self._char._row_to_character(r) for r in rows]

    def get_character(self, character_id: str):
        """Sync version: read character directly from SQLite."""
        conn = self._char._get_conn()
        row = conn.execute(
            "SELECT * FROM characters WHERE id = ?", (character_id,)
        ).fetchone()
        if row is None:
            return None
        return self._char._row_to_character(row)

    # -- Asset methods (sync — called from GET routes) --
    def find_assets(self, character_id: str, asset_type: Optional[str] = None):
        """Sync version: read assets directly from SQLite."""
        conn = self._asset._get_conn()
        if asset_type:
            rows = conn.execute(
                "SELECT * FROM assets WHERE character_id = ? AND asset_type = ? "
                "ORDER BY created_at",
                (character_id, asset_type),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM assets WHERE character_id = ? ORDER BY created_at",
                (character_id,),
            ).fetchall()
        return [self._asset._row_to_asset(r) for r in rows]

    def find_approved(self, character_id: str, asset_type: str):
        """Sync version: find approved assets from SQLite."""
        conn = self._asset._get_conn()
        rows = conn.execute(
            "SELECT * FROM assets WHERE character_id = ? AND asset_type = ? "
            "AND state IN ('approved', 'production') ORDER BY created_at",
            (character_id, asset_type),
        ).fetchall()
        return [self._asset._row_to_asset(r) for r in rows]

    # -- Asset methods (async — called from POST handlers) --
    async def save(self, record: AssetModel) -> str:
        return await self._asset.save(record)

    async def get(self, asset_id: str) -> Optional[AssetModel]:
        return await self._asset.get(asset_id)

    async def update_state(self, asset_id: str, new_state: str) -> None:
        return await self._asset.update_state(asset_id, new_state)

    async def find_by_character(self, character_id: str, asset_type: Optional[str] = None):
        return await self._asset.find_by_character(character_id, asset_type)


def check_comfyui(comfyui_url: str) -> bool:
    """Verify ComfyUI is reachable at the configured URL."""
    import requests

    try:
        r = requests.get(f"{comfyui_url}/", timeout=5)
        r.raise_for_status()
        print(f"  ✓ ComfyUI reachable at {comfyui_url}")
        return True
    except Exception as exc:
        print(f"  ✗ ComfyUI not reachable at {comfyui_url}: {exc}")
        print("    Start ComfyUI first, then re-run this script.")
        return False