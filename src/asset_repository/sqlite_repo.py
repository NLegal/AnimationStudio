"""SQLite implementation of the CharacterRepository and AssetRepository interfaces.

Uses parameterized queries (? placeholders) exclusively per security domain T-01-01.
Supports :memory: for testing with PRAGMA WAL and foreign_keys enabled.
"""

import json
import sqlite3
from datetime import datetime
from typing import Optional

from src.models.schemas import CharacterModel, AssetModel
from src.asset_repository.interfaces import CharacterRepository, AssetRepository


class NotFoundError(Exception):
    """Raised when a requested entity does not exist."""

    def __init__(self, entity: str, entity_id: str):
        self.message = f"{entity} '{entity_id}' not found"
        self.status_code = 404
        super().__init__(self.message)


class ValidationError(Exception):
    """Raised when an operation would violate a domain rule."""

    def __init__(self, message: str):
        self.message = message
        self.status_code = 400
        super().__init__(self.message)


# D-15 lifecycle state machine
# Forward: draft → generated → scored → shortlisted → approved → production → archived
# Reversible: pre-production states reset to draft on reject/regeneration (D-15 reversible).
_VALID_TRANSITIONS: dict[str, list[str]] = {
    "draft": ["generated"],
    "generated": ["scored", "draft"],
    "scored": ["shortlisted", "approved", "draft"],
    "shortlisted": ["approved", "draft"],
    "approved": ["production", "archived"],
    "production": ["archived"],
    "archived": [],
}


def _validate_transition(current: str, new: str) -> None:
    """Validate asset state transition per D-15 lifecycle."""
    allowed = _VALID_TRANSITIONS.get(current, [])
    if new not in allowed:
        raise ValueError(
            f"Invalid state transition: '{current}' -> '{new}'. "
            f"Allowed transitions from '{current}': {allowed}"
        )


def _serialize_datetime(dt: Optional[datetime]) -> Optional[str]:
    return dt.isoformat() if dt else None


def _deserialize_datetime(val: Optional[str]) -> Optional[datetime]:
    return datetime.fromisoformat(val) if val else None


class SQLiteCharacterRepository(CharacterRepository):
    """SQLite-backed character repository."""

    def __init__(self, db_path: str = "catalog.db"):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._init_schema()

    def _get_conn(self) -> sqlite3.Connection:
        # Cache connection for :memory: databases so tables persist
        # across queries (each sqlite3.connect(":memory:") creates a new db).
        if self._conn is not None:
            return self._conn
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        self._conn = conn
        return conn

    def _init_schema(self) -> None:
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    species TEXT,
                    bio_data TEXT DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    locked_at TEXT
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_characters_name "
                "ON characters(name)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_characters_name_category "
                "ON characters(name, category)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_characters_asset_id "
                "ON characters(json_extract(bio_data, '$.asset_id'))"
            )

    async def save_character(self, char: CharacterModel) -> str:
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO characters (id, name, category, species, bio_data, created_at, locked_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    char.id,
                    char.name,
                    char.category,
                    char.species,
                    json.dumps(char.bio_data),
                    _serialize_datetime(char.created_at),
                    _serialize_datetime(char.locked_at),
                ),
            )
        return char.id

    async def update_character(self, character_id: str, char: CharacterModel) -> bool:
        """Refresh an existing record's fields from a fresh model.

        Returns True when the record was updated.  Used by idempotent seeding
        to self-heal stale metadata (e.g. ``category_dir`` added after the
        record was first seeded).
        """
        with self._get_conn() as conn:
            cur = conn.execute(
                "UPDATE characters SET name = ?, category = ?, species = ?, "
                "bio_data = ? WHERE id = ?",
                (
                    char.name,
                    char.category,
                    char.species,
                    json.dumps(char.bio_data),
                    character_id,
                ),
            )
            conn.commit()
        return cur.rowcount > 0

    async def get_character(self, character_id: str) -> Optional[CharacterModel]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM characters WHERE id = ?", (character_id,)
            ).fetchone()
        if row is None:
            return None
        return self._row_to_character(row)

    async def find_character_by_name(self, name: str) -> Optional[CharacterModel]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM characters WHERE name = ?", (name,)
            ).fetchone()
        if row is None:
            return None
        return self._row_to_character(row)

    async def find_character_by_name_and_category(
        self, name: str, category: str
    ) -> Optional[CharacterModel]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM characters WHERE name = ? AND category = ?",
                (name, category),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_character(row)

    async def find_character_by_asset_id(
        self, asset_id: str, category: str = "asset"
    ) -> Optional[CharacterModel]:
        """Look up a prop record by its permanent ``asset_id`` bio field.

        Props are keyed by asset_id rather than display name — duplicate names
        (e.g. two "Banana" seeds) must never merge.
        """
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM characters WHERE category = ? AND "
                "json_extract(bio_data, '$.asset_id') = ?",
                (category, asset_id),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_character(row)

    async def list_characters(self) -> list[CharacterModel]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM characters ORDER BY created_at").fetchall()
        return [self._row_to_character(row) for row in rows]

    def _row_to_character(self, row: sqlite3.Row) -> CharacterModel:
        return CharacterModel(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            species=row["species"],
            bio_data=json.loads(row["bio_data"] or "{}"),
            created_at=_deserialize_datetime(row["created_at"]),
            locked_at=_deserialize_datetime(row["locked_at"]),
        )


class SQLiteAssetRepository(AssetRepository):
    """SQLite-backed asset repository."""

    def __init__(self, db_path: str = "catalog.db"):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._init_schema()

    def _get_conn(self) -> sqlite3.Connection:
        # Cache connection for :memory: databases so tables persist
        # across queries (each sqlite3.connect(":memory:") creates a new db).
        if self._conn is not None:
            return self._conn
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        self._conn = conn
        return conn

    def _init_schema(self) -> None:
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assets (
                    id TEXT PRIMARY KEY,
                    character_id TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    variant TEXT,
                    state TEXT DEFAULT 'draft',
                    file_path TEXT NOT NULL,
                    prompt TEXT,
                    seed INTEGER,
                    model_id TEXT,
                    scores TEXT,
                    brand_score REAL,
                    lineage TEXT DEFAULT NULL,
                    created_at TEXT NOT NULL,
                    approved_at TEXT,
                    FOREIGN KEY (character_id) REFERENCES characters(id)
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_assets_character ON assets(character_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_assets_lookup "
                "ON assets(character_id, asset_type, variant)"
            )
        self._apply_migrations()

    def _apply_migrations(self) -> None:
        """Apply ALTER TABLE migrations for backward-compatible schema changes.

        Checks for missing columns and adds them via ALTER TABLE IF NOT EXISTS.
        This ensures existing Phase 1 databases are updated in-place without
        requiring a destructive reset.
        """
        with self._get_conn() as conn:
            # Get current columns
            cursor = conn.execute("PRAGMA table_info(assets)")
            columns = {row["name"] for row in cursor.fetchall()}

            # Migration: add lineage column (D-18)
            if "lineage" not in columns:
                conn.execute(
                    "ALTER TABLE assets ADD COLUMN lineage TEXT DEFAULT NULL"
                )

    async def save(self, record: AssetModel) -> str:
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO assets "
                "(id, character_id, asset_type, variant, state, file_path, prompt, seed, "
                " model_id, scores, brand_score, lineage, created_at, approved_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    record.id,
                    record.character_id,
                    record.asset_type,
                    record.variant,
                    record.state,
                    record.file_path,
                    record.prompt,
                    record.seed,
                    record.model_id,
                    json.dumps(record.scores) if record.scores else None,
                    record.brand_score,
                    json.dumps(record.lineage) if record.lineage else None,
                    _serialize_datetime(record.created_at),
                    _serialize_datetime(record.approved_at),
                ),
            )
        return record.id

    async def get(self, asset_id: str) -> Optional[AssetModel]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM assets WHERE id = ?", (asset_id,)
            ).fetchone()
        if row is None:
            return None
        return self._row_to_asset(row)

    async def update_state(self, asset_id: str, new_state: str) -> None:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT state FROM assets WHERE id = ?", (asset_id,)
            ).fetchone()
            if row is None:
                raise NotFoundError("Asset", asset_id)
            current = row["state"]
            _validate_transition(current, new_state)
            conn.execute(
                "UPDATE assets SET state = ? WHERE id = ?", (new_state, asset_id)
            )

    async def find_by_character(
        self, character_id: str, asset_type: Optional[str] = None
    ) -> list[AssetModel]:
        with self._get_conn() as conn:
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
        return [self._row_to_asset(row) for row in rows]

    async def find_approved(
        self, character_id: str, asset_type: str
    ) -> list[AssetModel]:
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM assets WHERE character_id = ? AND asset_type = ? "
                "AND state = 'approved' ORDER BY created_at",
                (character_id, asset_type),
            ).fetchall()
        return [self._row_to_asset(row) for row in rows]

    def _row_to_asset(self, row: sqlite3.Row) -> AssetModel:
        return AssetModel(
            id=row["id"],
            character_id=row["character_id"],
            asset_type=row["asset_type"],
            variant=row["variant"],
            state=row["state"],
            file_path=row["file_path"],
            prompt=row["prompt"],
            seed=row["seed"],
            model_id=row["model_id"],
            scores=json.loads(row["scores"]) if row["scores"] else None,
            brand_score=row["brand_score"],
            lineage=json.loads(row["lineage"]) if row["lineage"] else None,
            created_at=_deserialize_datetime(row["created_at"]),
            approved_at=_deserialize_datetime(row["approved_at"]),
        )
