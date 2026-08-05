"""Read-only bridge between the Story Engine and the production asset catalog.

The Story Engine resolves characters, locations, and props against the
production ``catalog.db`` (SQLite) where those records exist, and degrades
gracefully to offline mode when the database is unavailable (missing file,
unreadable, or schema drift).

Performance notes
-----------------
- The assets table is large (tens of thousands of rows) and full-table scans
  are slow on the production filesystem.  Prop records and environment
  records are therefore cached once per process (the catalog is static during
  a run), and per-prop asset lookups go through the ``character_id`` index.
- All lookups are deterministic: queries are ordered and the first (or best)
  match is returned, so identical input always yields identical output.
"""

from __future__ import annotations

import os
import re
import sqlite3
from typing import Any, Dict, List, Optional

_UNIVERSE_CATEGORIES = ("main", "family", "friend", "community", "fantasy")

_ENVIRONMENT_ZONES = {
    "Residential": "Sunny Meadow",
    "Downtown": "Main Street",
    "School": "Sunny Meadow",
    "Playground": "Sunny Meadow",
    "Farm": "Green Valley",
    "Forest": "Whispering Woods",
    "Beach": "Sandy Cove",
    "Mountains": "Silver Peaks",
    "Fantasy": "Dreamland",
}


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def _best_token_match(target: str, candidates: List[Dict[str, str]], key: str):
    """Best token-subset match of ``target`` over ``candidates``, or None."""
    target_tokens = set(_norm(target).split())
    if not target_tokens:
        return None
    best = None
    best_score = 0.0
    for candidate in candidates:
        tokens = set(_norm(candidate[key]).split())
        if not tokens:
            continue
        score = len(target_tokens & tokens) / len(target_tokens)
        if score > best_score:
            best_score = score
            best = candidate
    return best if best_score >= 0.6 else None


class StoryCatalog:
    """Deterministic, read-only accessor over the production catalog.

    ``db_path`` defaults to ``catalog.db`` in the current working directory.
    Pass ``None`` (or a path that does not exist) to run fully offline.
    """

    _prop_rows: Optional[List[sqlite3.Row]] = None
    _universe_rows: Optional[List[sqlite3.Row]] = None
    _env_rows: Optional[List[sqlite3.Row]] = None

    def __init__(self, db_path: Optional[str] = "catalog.db"):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def _connect(self) -> Optional[sqlite3.Connection]:
        if self._conn is not None:
            return self._conn
        if not self.db_path or not os.path.isfile(self.db_path):
            return None
        try:
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            self._conn = conn
        except sqlite3.Error:
            self._conn = None
        return self._conn

    @property
    def available(self) -> bool:
        return self._connect() is not None

    def _query(self, sql: str, params: tuple = ()) -> Optional[List[sqlite3.Row]]:
        conn = self._connect()
        if conn is None:
            return None
        try:
            return conn.execute(sql, params).fetchall()
        except sqlite3.Error:
            return None

    def close(self) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
            except sqlite3.Error:
                pass
            self._conn = None

    # ------------------------------------------------------------------
    # Cached base tables
    # ------------------------------------------------------------------

    def _props(self) -> List[sqlite3.Row]:
        """All prop records (id, name), cached once per process."""
        if not self.available:
            return []
        if StoryCatalog._prop_rows is None:
            rows = self._query(
                "SELECT id, name FROM characters WHERE category = 'asset' ORDER BY name"
            )
            StoryCatalog._prop_rows = rows or []
        return StoryCatalog._prop_rows

    def _universe_characters(self) -> List[sqlite3.Row]:
        """All universe character records, cached once per process."""
        if not self.available:
            return []
        if StoryCatalog._universe_rows is None:
            placeholders = ",".join("?" * len(_UNIVERSE_CATEGORIES))
            rows = self._query(
                f"SELECT id, name, category, species FROM characters "
                f"WHERE category IN ({placeholders}) ORDER BY category, name",
                _UNIVERSE_CATEGORIES,
            )
            StoryCatalog._universe_rows = rows or []
        return StoryCatalog._universe_rows

    def _environments(self) -> List[sqlite3.Row]:
        """All environment records, cached once per process."""
        if not self.available:
            return []
        if StoryCatalog._env_rows is None:
            rows = self._query(
                "SELECT id, name, species FROM characters "
                "WHERE category = 'environment' ORDER BY name"
            )
            StoryCatalog._env_rows = rows or []
        return StoryCatalog._env_rows

    # ------------------------------------------------------------------
    # Characters
    # ------------------------------------------------------------------

    def resolve_character(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Return catalog record (id, name, category, species) for a character id."""
        rows = self._query(
            "SELECT id, name, category, species FROM characters WHERE id = ?",
            (character_id,),
        )
        if not rows:
            return None
        r = rows[0]
        return {
            "id": r["id"],
            "name": r["name"],
            "category": r["category"],
            "species": r["species"],
        }

    def resolve_character_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Return catalog record for a universe character by display name."""
        target = _norm(name)
        for r in self._universe_characters():
            if _norm(r["name"]) == target:
                return {
                    "id": r["id"],
                    "name": r["name"],
                    "category": r["category"],
                    "species": r["species"],
                }
        best = _best_token_match(name, self._universe_characters(), "name")
        if best is None:
            return None
        return {
            "id": best["id"],
            "name": best["name"],
            "category": best["category"],
            "species": best["species"],
        }

    def list_universe_characters(self) -> List[Dict[str, Any]]:
        """All universe character records (main/family/friend/community/fantasy)."""
        return [
            {
                "id": r["id"],
                "name": r["name"],
                "category": r["category"],
                "species": r["species"],
            }
            for r in self._universe_characters()
        ]

    # ------------------------------------------------------------------
    # Locations
    # ------------------------------------------------------------------

    def resolve_location(self, location: str) -> Optional[Dict[str, Any]]:
        """Return (record id, display name, zone) for a story location name.

        Exact normalized match first, then best token-subset match.  ``zone``
        is the database zone label (species column); the canonical ``ENV_*`` id
        comes from ``world.LOCATION_ID_MAP`` instead of the database.
        """
        target = _norm(location)
        for r in self._environments():
            if _norm(r["name"]) == target:
                return {"id": r["id"], "name": r["name"], "zone": r["species"]}
        best = _best_token_match(location, self._environments(), "name")
        if best is None:
            return None
        return {"id": best["id"], "name": best["name"], "zone": best["species"]}

    @staticmethod
    def zone_title(zone: str) -> str:
        """Map a database zone label to the World bible zone title."""
        for key, title in _ENVIRONMENT_ZONES.items():
            if key.lower() in (zone or "").lower():
                return title
        return zone or ""

    # ------------------------------------------------------------------
    # Props / assets
    # ------------------------------------------------------------------

    def resolve_assets(self, names: List[str]) -> Dict[str, Dict[str, str]]:
        """Resolve approved production files for a list of prop names.

        Returns ``{prop_name: {"asset_id": ..., "file_path": ...}}`` for each
        name that matched an approved asset record.  Unmatched names are
        omitted so callers can fall back to the offline asset names.
        """
        if not names:
            return {}
        props = self._props()
        if not props:
            return {}
        result: Dict[str, Dict[str, str]] = {}
        seen_props: set = set()
        for name in names:
            prop = self._match_prop(name, props)
            if prop is None:
                continue
            record = self._approved_asset_for(prop["id"])
            if record is None:
                continue
            if prop["id"] in seen_props and record["file_path"]:
                continue
            seen_props.add(prop["id"])
            result[name] = record
        return result

    @classmethod
    def _match_prop(
        cls, name: str, props: List[sqlite3.Row]
    ) -> Optional[sqlite3.Row]:
        target = _norm(name)
        for prop in props:
            if _norm(prop["name"]) == target:
                return prop
        return _best_token_match(name, props, "name")

    def _approved_asset_for(self, prop_id: str) -> Optional[Dict[str, str]]:
        """First approved, non-empty production file for a prop record."""
        conn = self._connect()
        if conn is None:
            return None
        try:
            with conn:
                info = conn.execute(
                    "SELECT json_extract(bio_data, '$.asset_id') AS asset_id "
                    "FROM characters WHERE id = ?",
                    (prop_id,),
                ).fetchone()
                asset = conn.execute(
                    "SELECT id, file_path FROM assets "
                    "WHERE character_id = ? AND state = 'approved' AND file_path != '' "
                    "ORDER BY created_at LIMIT 1",
                    (prop_id,),
                ).fetchone()
        except sqlite3.Error:
            return None
        if asset is None:
            return None
        asset_id = info["asset_id"] if info and info["asset_id"] else asset["id"]
        return {"asset_id": asset_id, "file_path": asset["file_path"]}
