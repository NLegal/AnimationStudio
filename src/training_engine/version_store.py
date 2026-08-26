"""JSON sidecar store for LoRA version records.

Provides ``JsonVersionStore``, a file-backed persistence layer for version
records that mirrors the ``lora_models`` SQL schema (field contract from
``migrations.py`` L49-58) without touching ``catalog.db``.

The store is fully isolated from the corrupted production database (A3,
C-CATALOGDB) — no imports from ``asset_repository`` are permitted here.

Serialization follows the repo JSON idiom (``indent=2``, ``ensure_ascii=False``,
UTF-8 encoding).  Writes are atomic (temp file + ``os.replace``) to prevent
corruption on mid-write crashes.  Reads are tolerant: missing files return
``[]`` and individual unparsable entries are skipped.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


class JsonVersionStore:
    """File-backed JSON store for version record dicts.

    Each record dict uses the ``lora_models`` field contract:
    ``id``, ``character_id``, ``version``, ``file_path``,
    ``training_config``, ``benchmark_scores``, ``trained_at``, ``promoted``.

    Args:
        store_path: Path to the JSON store file.
    """

    def __init__(self, store_path: Path) -> None:
        self._store_path = Path(store_path)

    def load(self) -> list[dict[str, Any]]:
        """Load all records from the store file.

        Returns an empty list when the file does not exist or is entirely
        unparseable.  Individual corrupt entries are silently skipped.

        Returns:
            List of record dicts.
        """
        if not self._store_path.exists():
            return []

        try:
            raw = self._store_path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return []

        if not isinstance(data, list):
            return []

        records: list[dict[str, Any]] = []
        for entry in data:
            if isinstance(entry, dict) and "character_id" in entry and "version" in entry:
                records.append(entry)
        return records

    def save(self, records: list[dict[str, Any]]) -> None:
        """Atomically persist *records* to the store file.

        Uses a temporary sibling file and ``os.replace`` so that a crash
        mid-write cannot leave a half-written file at *store_path*.

        Args:
            records: List of record dicts to persist.
        """
        self._store_path.parent.mkdir(parents=True, exist_ok=True)

        content = json.dumps(records, indent=2, ensure_ascii=False)
        # Write to sibling temp file in the same directory, then atomically replace
        fd, tmp_path = tempfile.mkstemp(
            dir=self._store_path.parent,
            prefix=f".{self._store_path.name}.",
            suffix=".tmp",
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self._store_path)
        except BaseException:
            # Clean up temp file on any failure
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise


def load_registry(store_path: Path) -> "VersionRegistry":
    """Factory: create a ``VersionRegistry`` hydrated from *store_path*.

    Args:
        store_path: Path to the JSON sidecar store file.

    Returns:
        A ``VersionRegistry`` instance with all persisted records loaded.
    """
    from .versioning import VersionRegistry

    store = JsonVersionStore(store_path)
    return VersionRegistry(store=store)
