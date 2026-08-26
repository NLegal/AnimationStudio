"""LoRA version management — semver-style versioning with lifecycle tracking.

Follows the convention::

    v{major}.{minor}

Where:
    - v0.x = development / experimental (pre-release)
    - v1.0 = first production release
    - v1.x = minor improvements, bug fixes
    - v2.0 = major redesign / retrain from scratch
"""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .version_store import JsonVersionStore


_LORA_VERSION_PATTERN = re.compile(r"^v(\d+)\.(\d+)$")


@dataclass(frozen=True)
class LoRAVersion:
    """A parsed LoRA model version.

    Comparison and ordering are supported::

        LoRAVersion("v0.1") < LoRAVersion("v1.0")  # True
    """

    major: int
    minor: int

    def __str__(self) -> str:
        return f"v{self.major}.{self.minor}"

    def __repr__(self) -> str:
        return f"LoRAVersion('v{self.major}.{self.minor}')"

    @classmethod
    def parse(cls, version_str: str) -> "LoRAVersion":
        """Parse a version string in the format ``v{major}.{minor}``.

        Args:
            version_str: Version string (e.g. ``"v0.1"``, ``"v2.0"``).

        Returns:
            A new LoRAVersion instance.

        Raises:
            ValueError: If the string does not match the expected format.
        """
        match = _LORA_VERSION_PATTERN.match(version_str.strip())
        if not match:
            raise ValueError(
                f"Invalid LoRA version format: '{version_str}'. "
                f"Expected 'v{{major}}.{{minor}}' (e.g. 'v0.1', 'v2.0')."
            )
        return cls(major=int(match.group(1)), minor=int(match.group(2)))

    @property
    def is_production(self) -> bool:
        """True if this is a production release (v1.0 or higher)."""
        return self.major >= 1

    @property
    def is_experimental(self) -> bool:
        """True if this is a pre-release version (v0.x)."""
        return self.major == 0

    def bump_major(self) -> "LoRAVersion":
        """Increment the major version and reset minor to 0.

        Example: ``v0.1`` → ``v1.0``, ``v1.3`` → ``v2.0``
        """
        return LoRAVersion(major=self.major + 1, minor=0)

    def bump_minor(self) -> "LoRAVersion":
        """Increment the minor version.

        Example: ``v0.1`` → ``v0.2``, ``v1.0`` → ``v1.1``
        """
        return LoRAVersion(major=self.major, minor=self.minor + 1)

    def bump(self, bump_type: str = "minor") -> "LoRAVersion":
        """Convenience method for version bumping.

        Args:
            bump_type: One of ``"major"``, ``"minor"``.

        Returns:
            A new version with the specified bump applied.

        Raises:
            ValueError: If *bump_type* is not recognised.
        """
        if bump_type == "major":
            return self.bump_major()
        elif bump_type == "minor":
            return self.bump_minor()
        raise ValueError(f"Unknown bump type: '{bump_type}'. Use 'major' or 'minor'.")


_VERSION_COMPARISON_ERROR = (
    "Cannot compare LoRAVersion with non-LoRAVersion type"
)


@dataclass
class VersionRecord:
    """A persisted version entry from the ``lora_models`` table."""

    character_id: str
    version: LoRAVersion
    file_path: str
    training_config: Optional[dict] = None
    benchmark_scores: Optional[dict] = None
    trained_at: Optional[datetime] = None
    promoted: bool = False


class VersionRegistry:
    """Manages LoRA version lifecycle for a single character.

    Tracks which versions have been trained, which are promoted to
    production, and computes the next recommended version number.

    When constructed with a ``store`` (:class:`JsonVersionStore`), the
    registry hydrates existing records on construction and persists on
    every mutation (register / promote).  Without a store the registry
    behaves identically to the original in-memory-only implementation
    — all 51 existing baseline tests keep their semantics.

    Registration is **idempotent** on ``(character_id, version)``:
    re-registering the same pair replaces the prior record in place
    instead of appending a duplicate (Pitfall 5).

    Usage::

        registry = VersionRegistry()
        registry.register(
            character_id="lily-bunny",
            version=LoRAVersion.parse("v0.1"),
            file_path="/output/lily-bunny_v0.1.safetensors",
        )
        next_v = registry.recommend_next("lily-bunny", "minor")
        # → LoRAVersion('v0.2')
    """

    def __init__(self, store: Optional["JsonVersionStore"] = None) -> None:
        self._records: dict[str, list[VersionRecord]] = {}
        self._store = store
        if store is not None:
            self._hydrate_from_store()

    # ------------------------------------------------------------------
    # Store integration
    # ------------------------------------------------------------------

    def _hydrate_from_store(self) -> None:
        """Load persisted records from the bound store (if any)."""
        if self._store is None:
            return
        for rec in self._store.load():
            try:
                version = LoRAVersion.parse(rec.get("version", "v0.1"))
            except ValueError:
                continue
            trained_at = None
            if rec.get("trained_at"):
                try:
                    trained_at = datetime.fromisoformat(rec["trained_at"])
                except (ValueError, TypeError):
                    pass
            self._records.setdefault(rec["character_id"], []).append(
                VersionRecord(
                    character_id=rec["character_id"],
                    version=version,
                    file_path=rec.get("file_path", ""),
                    training_config=rec.get("training_config"),
                    benchmark_scores=rec.get("benchmark_scores"),
                    trained_at=trained_at,
                    promoted=bool(rec.get("promoted", False)),
                )
            )

    def _persist(self) -> None:
        """Snapshot the full record set to the bound store (if any)."""
        if self._store is None:
            return
        self._store.save(self._serialize_all())

    def _serialize_all(self) -> list[dict]:
        """Serialize every record to a lora_models-compatible dict."""
        records: list[dict] = []
        for char_records in self._records.values():
            for r in char_records:
                records.append(self._serialize_record(r))
        return records

    @staticmethod
    def _serialize_record(r: VersionRecord) -> dict:
        """Serialize a single VersionRecord to a JSON-safe dict."""
        record_id = hashlib.sha256(
            f"{r.character_id}:{r.version}".encode()
        ).hexdigest()[:12]
        return {
            "id": record_id,
            "character_id": r.character_id,
            "version": str(r.version),
            "file_path": r.file_path,
            "training_config": r.training_config,
            "benchmark_scores": r.benchmark_scores,
            "trained_at": r.trained_at.isoformat() if r.trained_at else "",
            "promoted": r.promoted,
        }

    def _key(self, character_id: str, version: LoRAVersion) -> str:
        """Composite key for idempotent registration."""
        return f"{character_id}:{version}"

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        character_id: str,
        version: LoRAVersion,
        file_path: str,
        training_config: Optional[dict] = None,
        benchmark_scores: Optional[dict] = None,
        trained_at: Optional[datetime] = None,
        promoted: bool = False,
    ) -> None:
        """Register a version record (idempotent on ``(character_id, version)``).

        If the same ``(character_id, version)`` pair already exists the
        prior record is **replaced in place** — no duplicates are created.

        Args:
            character_id: Character identifier.
            version: The trained version.
            file_path: Path to the LoRA .safetensors file.
            training_config: Training configuration used.
            benchmark_scores: Benchmark evaluation scores.
            trained_at: When training completed.
            promoted: Whether this version is promoted to production.
        """
        new_record = VersionRecord(
            character_id=character_id,
            version=version,
            file_path=file_path,
            training_config=training_config,
            benchmark_scores=benchmark_scores,
            trained_at=trained_at or datetime.now(),
            promoted=promoted,
        )

        if character_id not in self._records:
            self._records[character_id] = []

        # Idempotent: replace if same version already exists
        existing = self._records[character_id]
        for i, rec in enumerate(existing):
            if rec.version == version:
                existing[i] = new_record
                self._persist()
                return

        existing.append(new_record)
        self._persist()

    def get_versions(self, character_id: str) -> list[VersionRecord]:
        """Return all registered versions for *character_id*, sorted descending."""
        records = self._records.get(character_id, [])
        records.sort(key=lambda r: (r.version.major, r.version.minor), reverse=True)
        return records

    def get_latest(self, character_id: str) -> Optional[VersionRecord]:
        """Return the highest (latest) version for *character_id*, or None."""
        versions = self.get_versions(character_id)
        return versions[0] if versions else None

    def get_promoted(self, character_id: str) -> Optional[VersionRecord]:
        """Return the promoted production version for *character_id*, or None."""
        for record in self.get_versions(character_id):
            if record.promoted:
                return record
        return None

    def get_production_candidates(self, character_id: str) -> list[VersionRecord]:
        """Return versions eligible for production promotion.

        A version is a candidate if its benchmark scores meet minimum
        thresholds (set by BenchmarkConfig standards).
        """
        candidates = []
        for record in self.get_versions(character_id):
            if record.benchmark_scores:
                candidates.append(record)
        return candidates

    # ------------------------------------------------------------------
    # Promotion
    # ------------------------------------------------------------------

    def promote(self, character_id: str, version: LoRAVersion) -> VersionRecord:
        """Flip an existing record to ``promoted=True`` post-hoc.

        Supports the *train-v0.x → benchmark-pass → promote-v1.0* flow:
        register the experimental version first, then promote it once
        benchmark evidence lands.

        **Multi-promotion semantics:** ``promote`` flips *only* the target
        record — it does **not** un-promote others.  The audit trail of
        every historically-promoted version is preserved.

        Args:
            character_id: Character identifier.
            version: Version to promote.

        Returns:
            The updated ``VersionRecord`` with ``promoted=True``.

        Raises:
            ValueError: If *character_id* or *version* is not registered.
        """
        records = self._records.get(character_id, [])
        for i, rec in enumerate(records):
            if rec.version == version:
                updated = replace(rec, promoted=True)
                records[i] = updated
                self._persist()
                return updated

        # Determine which key was missing for a helpful error message
        if not records:
            raise ValueError(
                f"Cannot promote: character_id '{character_id}' not found"
            )
        raise ValueError(
            f"Cannot promote: version {version} not found for "
            f"character_id '{character_id}'"
        )

    def recommend_next(
        self,
        character_id: str,
        bump_type: str = "minor",
    ) -> LoRAVersion:
        """Recommend the next version for *character_id*.

        If no versions exist, returns ``v0.1``.

        Args:
            character_id: Character identifier.
            bump_type: ``"major"`` or ``"minor"``.

        Returns:
            The recommended next LoRAVersion.
        """
        latest = self.get_latest(character_id)
        if latest is None:
            return LoRAVersion(major=0, minor=1)
        return latest.version.bump(bump_type)

    @staticmethod
    def from_db_records(records: list[dict]) -> "VersionRegistry":
        """Build a VersionRegistry from database records.

        Each *record* dict should contain:
            - ``character_id`` (str)
            - ``version`` (str)
            - ``file_path`` (str)
            - ``training_config`` (dict, optional)
            - ``benchmark_scores`` (dict, optional)
            - ``trained_at`` (str, optional)
            - ``promoted`` (int/bool, optional)
        """
        registry = VersionRegistry()
        for rec in records:
            try:
                version = LoRAVersion.parse(rec.get("version", "v0.1"))
            except ValueError:
                continue

            trained_at = None
            if rec.get("trained_at"):
                trained_at = datetime.fromisoformat(rec["trained_at"])

            registry.register(
                character_id=rec["character_id"],
                version=version,
                file_path=rec.get("file_path", ""),
                training_config=rec.get("training_config"),
                benchmark_scores=rec.get("benchmark_scores"),
                trained_at=trained_at,
                promoted=bool(rec.get("promoted", False)),
            )
        return registry
