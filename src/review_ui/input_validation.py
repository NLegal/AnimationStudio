"""Pure input-validation helpers for the Studio UI (M-07).

Every user-supplied value that reaches a route handler is checked here before
it is passed to the database or a backend runner.  The helpers are pure
(side-effect free) so they are trivial to unit-test without a running app.

The design keeps one canonical whitelist per risky dimension:

* ``asset_id`` — the only user value interpolated into path lookups.  Must be
  a short ``[A-Za-z0-9._-]`` token; anything else is rejected before the repo
  layer sees it.
* ``action`` — an allowlist of the D-15 lifecycle transitions.
* ``backend`` — an allowlist matching ``resolve_backend`` names.
* ``scope`` — the batch generation scopes.
* free-text fields — length-capped so a hostile client cannot ask for an
  unbounded prompt/reason/topic string.

Violations raise ``ValueError`` so the existing route-level ``except
(NotFoundError, ValueError)`` handlers in ``app.py`` keep working unchanged.
"""

import re
from typing import Optional

MAX_ASSET_ID_LEN = 192
_ASSET_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,191}$")

ALLOWED_ACTIONS = frozenset({"approve", "reject", "shortlist", "promote", "regenerate"})

# Mirrors resolve_backend() accepted names (``batch_generator.py``).
ALLOWED_BACKENDS = frozenset({"", "mock", "comfy", "comfyui", "cloud", "cloudapi"})

# Mirrors the music generation registry (``music_generation/backends.py``).
ALLOWED_MUSIC_BACKENDS = frozenset({"", "ace-step", "suno", "mock"})

# Mirrors _find_seeds()/kind_map scopes (``app.py``).
ALLOWED_SCOPES = frozenset(
    {"all", "characters", "environments", "vehicles", "backgrounds", "props"}
)

# 2 kB is plenty for a rejection reason, a prompt tail, or a topic line.
MAX_TEXT_LEN = 2000

# Generation batch bounds (count per seed / overall limit / shortlist cap).
MIN_COUNT = 1
MAX_COUNT = 50
MAX_LIMIT = 1000


def validate_asset_id(asset_id: str) -> str:
    """Validate a path-parameter asset id; return it (or strip) unchanged.

    Raises:
        ValueError: when the id is empty, too long, or contains characters
            outside the safe token set.
    """
    if not isinstance(asset_id, str) or not asset_id:
        raise ValueError("asset_id must be a non-empty string")
    if len(asset_id) > MAX_ASSET_ID_LEN:
        raise ValueError(
            f"asset_id too long: {len(asset_id)} > {MAX_ASSET_ID_LEN} chars"
        )
    if not _ASSET_ID_RE.fullmatch(asset_id):
        raise ValueError(
            "asset_id may only contain [A-Za-z0-9._-] and must start alnum"
        )
    return asset_id


def validate_action(action: str) -> str:
    """Validate a lifecycle action name against the D-15 allowlist."""
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"Unknown action {action!r}")
    return action


def validate_backend(backend: str) -> str:
    """Validate a backend name against the resolve_backend() allowlist.

    Accepts the empty string (caller default) as well as every name
    ``resolve_backend`` understands.
    """
    if not isinstance(backend, str) or backend.lower() not in ALLOWED_BACKENDS:
        raise ValueError(f"Unknown backend {backend!r}")
    return backend


def validate_scope(scope: str) -> str:
    """Validate a batch-generation scope against the catalog scopes."""
    if not isinstance(scope, str) or scope.lower() not in ALLOWED_SCOPES:
        raise ValueError(f"Unknown scope {scope!r}")
    return scope.lower()


def validate_music_backend(backend: str) -> str:
    """Validate a music-generation backend against the get_backend() registry.

    Accepts the empty string (the caller falls back to the environment
    default).  Only ``ace-step``, ``suno``, and ``mock`` are valid.
    """
    if not isinstance(backend, str) or backend.lower() not in ALLOWED_MUSIC_BACKENDS:
        raise ValueError(f"Unknown music backend {backend!r}")
    return backend.lower()


def cap_text(value: str, max_len: int = MAX_TEXT_LEN) -> str:
    """Return *value* stripped and length-capped; never raises."""
    if not isinstance(value, str):
        return ""
    return value.strip()[:max_len]


def validate_count(count: int) -> int:
    """Clamp/validate a per-seed generation count (1..MAX_COUNT)."""
    if not isinstance(count, int) or isinstance(count, bool):
        raise ValueError("count must be an integer")
    if count < MIN_COUNT or count > MAX_COUNT:
        raise ValueError(f"count must be between {MIN_COUNT} and {MAX_COUNT}")
    return count


def validate_limit(limit: int) -> int:
    """Validate a generation overall limit (0..MAX_LIMIT); 0 means no limit."""
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise ValueError("limit must be an integer")
    if limit < 0 or limit > MAX_LIMIT:
        raise ValueError(f"limit must be between 0 and {MAX_LIMIT}")
    return limit


def optional_validated(validator, value) -> Optional[str]:
    """Run *validator* on *value* unless it is blank/None (empty passes)."""
    if value is None or not str(value).strip():
        return None
    return validator(str(value).strip())