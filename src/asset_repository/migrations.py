"""Schema migration manager for the SQLite asset catalog.

Provides versioned SQL migrations that create and evolve the database schema.
Uses parameterized queries exclusively for any dynamic values.
"""

import sqlite3
from datetime import datetime, timezone


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS characters (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    species TEXT,
    bio_data TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    locked_at TEXT
);

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
    created_at TEXT NOT NULL,
    approved_at TEXT,
    FOREIGN KEY (character_id) REFERENCES characters(id)
);

CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    character_id TEXT NOT NULL,
    job_type TEXT NOT NULL,
    config TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS lora_models (
    id TEXT PRIMARY KEY,
    character_id TEXT NOT NULL,
    version TEXT NOT NULL,
    file_path TEXT NOT NULL,
    training_config TEXT,
    benchmark_scores TEXT,
    trained_at TEXT NOT NULL,
    promoted INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS _schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);
"""


class SchemaManager:
    """Manages versioned SQLite schema migrations.

    Usage:
        mgr = SchemaManager('catalog.db')
        mgr.run_migrations()
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def get_schema_version(self) -> int:
        """Read the current schema version from the database."""
        try:
            with self._get_conn() as conn:
                row = conn.execute(
                    "SELECT MAX(version) FROM _schema_version"
                ).fetchone()
                return row[0] if row and row[0] else 0
        except sqlite3.OperationalError:
            return 0

    def run_migrations(self) -> None:
        """Apply all pending migrations in order."""
        current = self.get_schema_version()

        if current < 1:
            self._apply_version(1, self._create_schema)

    def _apply_version(self, version: int, fn) -> None:
        """Apply a specific migration version."""
        with self._get_conn() as conn:
            fn(conn)
            conn.execute(
                "INSERT INTO _schema_version (version, applied_at) VALUES (?, ?)",
                (version, datetime.now(timezone.utc).isoformat()),
            )

    def _create_schema(self, conn: sqlite3.Connection) -> None:
        """Create the initial database schema (version 1)."""
        conn.executescript(_SCHEMA_SQL)
