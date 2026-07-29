"""LoRA version management — semver-style versioning with lifecycle tracking.

Follows the convention::

    v{major}.{minor}

Where:
    - v0.x = development / experimental (pre-release)
    - v1.0 = first production release
    - v1.x = minor improvements, bug fixes
    - v2.0 = major redesign / retrain from scratch
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


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

    def __init__(self) -> None:
        self._records: dict[str, list[VersionRecord]] = {}

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
        """Register a new version record.

        Args:
            character_id: Character identifier.
            version: The trained version.
            file_path: Path to the LoRA .safetensors file.
            training_config: Training configuration used.
            benchmark_scores: Benchmark evaluation scores.
            trained_at: When training completed.
            promoted: Whether this version is promoted to production.
        """
        if character_id not in self._records:
            self._records[character_id] = []
        self._records[character_id].append(VersionRecord(
            character_id=character_id,
            version=version,
            file_path=file_path,
            training_config=training_config,
            benchmark_scores=benchmark_scores,
            trained_at=trained_at or datetime.now(),
            promoted=promoted,
        ))

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
