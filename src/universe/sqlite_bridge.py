"""SQLiteCombinedRepo — bridges SQLite repos to the Review UI's expectations.

The Review UI expects one object exposing both synchronous GET methods
(``list_characters``, ``get_character``, ``find_assets``,
``find_approved``) and async POST methods (``save``, ``get``,
``update_state``).  This adapter wraps the two SQLite repositories behind a
single object, reading rows directly for the sync methods.
"""

from typing import Optional

from src.asset_repository.sqlite_repo import (
    SQLiteAssetRepository,
    SQLiteCharacterRepository,
)
from src.models.schemas import AssetModel, CharacterModel


class SQLiteCombinedRepo:
    """One object exposing the sync + async surface the UI needs."""

    def __init__(self, char_repo: SQLiteCharacterRepository,
                 asset_repo: SQLiteAssetRepository):
        self._char = char_repo
        self._asset = asset_repo

    # -- Characters (sync) ------------------------------------------- #

    def list_characters(self) -> list[CharacterModel]:
        conn = self._char._get_conn()
        rows = conn.execute(
            "SELECT * FROM characters ORDER BY created_at"
        ).fetchall()
        return [self._char._row_to_character(r) for r in rows]

    def get_character(self, character_id: str) -> Optional[CharacterModel]:
        conn = self._char._get_conn()
        row = conn.execute(
            "SELECT * FROM characters WHERE id = ?", (character_id,)
        ).fetchone()
        return self._char._row_to_character(row) if row else None

    # -- Assets (sync) ----------------------------------------------- #

    def find_assets(self, character_id: str,
                    asset_type: Optional[str] = None) -> list[AssetModel]:
        conn = self._asset._get_conn()
        if asset_type:
            rows = conn.execute(
                "SELECT * FROM assets WHERE character_id = ? AND asset_type = ? "
                "ORDER BY created_at", (character_id, asset_type),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM assets WHERE character_id = ? ORDER BY created_at",
                (character_id,),
            ).fetchall()
        return [self._asset._row_to_asset(r) for r in rows]

    def find_approved(self, character_id: str,
                      asset_type: str) -> list[AssetModel]:
        conn = self._asset._get_conn()
        rows = conn.execute(
            "SELECT * FROM assets WHERE character_id = ? AND asset_type = ? "
            "AND state IN ('approved', 'production') ORDER BY created_at",
            (character_id, asset_type),
        ).fetchall()
        return [self._asset._row_to_asset(r) for r in rows]

    # -- Assets (async — POST handlers) ------------------------------ #

    async def save(self, record: AssetModel) -> str:
        return await self._asset.save(record)

    async def get(self, asset_id: str) -> Optional[AssetModel]:
        return await self._asset.get(asset_id)

    async def update_state(self, asset_id: str, new_state: str) -> None:
        return await self._asset.update_state(asset_id, new_state)
