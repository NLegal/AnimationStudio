# Phase 7: Music Generation Backend Integration - Pattern Map

**Mapped:** 2026-08-21
**Files analyzed:** 8 (7 new files + 0 modified source files)
**Analogs found:** 8 / 8 (5 exact or near-exact, 3 role-match)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/music_generation/__init__.py` | config (package init) | n/a | `src/generation_engine/__init__.py` | exact |
| `src/music_generation/models.py` | model | transform | `src/models/schemas.py` | exact |
| `src/music_generation/backends.py` | service (protocol + registry + exceptions) | event-driven | `src/generation_engine/base.py` + `src/pipeline/job_queue.py` | role-match |
| `src/music_generation/ace_step.py` | service (REST adapter) | event-driven (async job: submit→poll→download) | `src/generation_engine/cloud_backend.py` (+ `comfy_backend.py` health probe) | exact |
| `src/music_generation/suno.py` | service (stub) | request-response (always fails) | `src/generation_engine/cloud_backend.py` (not-ready path) | role-match |
| `src/music_generation/mock.py` | service (mock) | transform | `src/generation_engine/mock_backend.py` | role-match |
| `scripts/generate_phase7.py` | utility (CLI script) | batch (report writing) | `scripts/generate_phase5.py` | exact |
| `tests/test_music_generation.py` | test | n/a | `tests/test_audio_bible.py` | exact |

**Dependency constraints verified** (`pyproject.toml`): `pydantic>=2.0.0` present;
**no** httpx/requests declared as direct deps (`requests` only appears transitively
and existing backends import it lazily inside methods). Research mandate stands:
new package uses **stdlib `urllib.request` only**, behind an injectable transport seam.

## Pattern Assignments

### `src/music_generation/__init__.py` (config, package init)

**Analog:** `src/generation_engine/__init__.py` (whole file, 27 lines)

This is the best analog because it combines **exports + a name→class registry dict**
— exactly what Phase 7 needs for `get_backend("ace-step"|"suno"|"mock")`.

**Exports + registry pattern** (lines 1–27):
```python
from .base import GenerationBackend, GenerationInput, GenerationOutput, ModelLoadError
from .flux_backend import FluxBackend
...
BACKENDS: dict[str, type[GenerationBackend]] = {
    "flux": FluxBackend,
    "sdxl": SDXLBackend,
    "pony": PonyBackend,
    "comfy": ComfyUIBackend,
    "cloud": CloudAPIBackend,
}

__all__ = [
    "GenerationBackend",
    ...
    "BACKENDS",
]
```

Secondary analog for docstring style: `src/audio_bible/__init__.py` (lines 1–8) opens
with a phase-scoped module docstring ("Phase 5 Audio Bible & Music Production System…")
before imports — copy this for "Phase 7 Music Generation Backend Integration".

**Adaptation:** new package exposes a factory function `get_backend(name)` rather than
a bare dict export (research §4); keep the dict private (`_BACKENDS`) inside
`backends.py` and re-export through `__init__.py`.

---

### `src/music_generation/models.py` (model, transform)

**Analog:** `src/models/schemas.py` (whole file, 85 lines)

Research §4 explicitly says "Pydantic v2, mirroring `src/models/schemas.py`".
⚠️ Do NOT copy `src/audio_bible/models.py` even though it is same-domain — it uses
frozen dataclasses; `schemas.py` is authoritative per research.

**Imports pattern** (lines 1–6):
```python
"""Shared Pydantic v2 models for all pipeline contracts."""

import uuid
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field
```

**Literal enum + Optional + default_factory conventions** (lines 9–26):
```python
class CharacterModel(BaseModel):
    """A character identity record in the studio universe."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: Literal[
        "main", "family", "friend", "community", "fantasy",
        "environment", "asset", "vehicle", "background",
    ]
    species: str
    bio_data: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    locked_at: Optional[datetime] = None
```

**Constrained field convention** (lines 74–76):
```python
    seed: Optional[int] = None
    count: int = Field(default=4, ge=1, le=100)
```

**Apply to:** `MusicRequest` (category/topic/duration_s/vocals/lyrics_override/seed/
tags), `MusicStatus` (state `Literal["pending","running","completed","failed"]`,
progress float, error `Optional[str]`), `MusicResult` (request, audio bytes, format
Literal["wav","mp3"], job_id, backend, seed). Every class gets a docstring like
schemas.py does.

---

### `src/music_generation/backends.py` (service: protocol + registry + exceptions)

**Analog A — interface:** `src/generation_engine/base.py` (whole file, 52 lines)

⚠️ **Deliberate divergence:** `base.py` uses `abc.ABC` + `@abstractmethod`; research §4
mandates `typing.Protocol` with `@runtime_checkable` so isinstance checks work without
inheritance. Copy the *shape* (input contract, output contract, exception class,
interface class), swap ABC for Protocol.

**Input/output contract + exception + interface shape** (lines 12–51):
```python
@dataclass
class GenerationInput:
    """Input contract for image generation."""
    prompt: str
    negative_prompt: str = ""
    seed: int = 42
    ...

class ModelLoadError(Exception):
    """Raised when a model fails to load (import, download, or OOM)."""

class GenerationBackend(ABC):
    @abstractmethod
    def generate(self, input: GenerationInput) -> GenerationOutput:
        """Run inference and return generated images."""
        ...
```

**Analog B — status state machine:** `src/pipeline/job_queue.py` (lines 14–20, 92–115)

The `MusicStatus.state` Literal and terminal-state semantics mirror this:

```python
# Valid status transitions for Job state machine
_VALID_JOB_TRANSITIONS: dict[str, list[str]] = {
    "pending": ["running", "completed", "failed"],
    "running": ["completed", "failed"],
    "completed": [],
    "failed": [],
}

class JobError(Exception):
    """Raised on invalid job operations (bad transitions, missing jobs)."""
```
and `update_status()` (lines 92–113) shows raising a domain-specific error with a
message that includes current + allowed states — copy this message style for
`GenerationFailed` payloads.

**Analog C — exception docstring convention:** exceptions carry a docstring explaining
when they're raised and what callers should do (see `ModelLoadError` above:
"All backends catch this in generate() and return error metadata"). ⚠️ For Phase 7,
callers should NOT swallow into metadata — research §2 defines strict raise-based
error mapping (`NotConfigured`, `BackendUnavailable`, `GenerationFailed` under base
`MusicBackendError`).

---

### `src/music_generation/ace_step.py` (service, async-job HTTP adapter)

**Primary analog:** `src/generation_engine/cloud_backend.py` (364 lines)

The `_generate_replicate` and `_generate_bfl` methods are the exact submit→poll→
download lifecycle ACE-Step needs (POST returns id → GET status until terminal →
GET bytes).

**Env-var key resolution (constructor arg > env var > None)** (lines 61–70, 84–98):
```python
def __init__(
    self,
    provider: str = "fal",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
):
    self.provider = Provider(provider)
    self.api_key = api_key
    ...

env_key = _PROVIDER_ENV_KEY[self.provider]
resolved_key = self.api_key or os.environ.get(env_key)
```
Adapt: constructor arg `api_key`/`base_url` > env `ACESTEP_API_KEY`/`ACESTEP_BASE_URL`
(default `http://localhost:8001`). ⚠️ Divergence: on missing key, cloud_backend logs a
warning and continues; ACE-Step must expose `is_configured() -> False` and raise
`NotConfigured` on use (research §2).

**Bearer auth + JSON POST headers** (lines 206–227, Replicate):
```python
headers = {
    "Authorization": f"Bearer {self.api_key}",
    "Content-Type": "application/json",
    "Prefer": "wait",
}
payload = {"input": {...}}
resp = requests.post(..., json=payload, headers=headers, timeout=120)
```
Adapt headers to `"Authorization": f"Bearer {os.environ['ACESTEP_API_KEY']}"`.

**Poll loop with terminal states and typed failure raise** (lines 232–248):
```python
if prediction.get("status") == "processing":
    prediction_id = prediction["id"]
    for _attempt in range(60):
        time.sleep(5)
        poll_resp = requests.get(
            f"https://api.replicate.com/v1/predictions/{prediction_id}",
            headers=headers, timeout=30,
        )
        poll_resp.raise_for_status()
        prediction = poll_resp.json()
        if prediction.get("status") == "succeeded":
            break
        elif prediction.get("status") == "failed":
            raise RuntimeError(
                f"Replicate prediction failed: {prediction.get('error', 'unknown')}"
            )
```
And BFL's timeout guard (lines 290–318): bounded loop then
`raise TimeoutError(f"...did not complete within timeout ({request_id})")`.
Adapt: `poll_interval_s=2.0`, exponential backoff cap ×8, overall `timeout_s=300`,
map failed-status JSON → `GenerationFailed`.

**Binary download with validation** (lines 320–354):
```python
resp = requests.get(url, timeout=30)
resp.raise_for_status()
content_type = resp.headers.get("content-type", "")
if not content_type.startswith("image/"):
    logger.warning(...)
```
Adapt: accept `audio/*` content-type for `/v1/audio?path=<path>` download.

⚠️ **Transport divergence:** cloud_backend lazily does `import requests` inside each
method (lines 168, 204, etc.). That lazy-import-as-seam idea carries over, but the
implementation MUST be stdlib `urllib.request` wrapped in module-level functions
(`_post_json`, `_get_json`, `_get_bytes`, each taking an explicit timeout), plus a
constructor `transport=` callable parameter so tests inject fakes (research §4).
Do not add `requests` calls.

**Health probe analog:** `src/generation_engine/comfy_backend.py` (lines 88–102):
```python
try:
    import requests
    resp = requests.get(f"{self.server_url}/", timeout=5)
    resp.raise_for_status()
    logger.info("ComfyUI server reachable at %s", self.server_url)
except Exception as exc:
    logger.warning("ComfyUI server at %s unreachable (%s)...", ...)
```
Adapt: short-timeout probe of `GET /v1/jobs/health` or root before first use;
on failure surface `is_configured() -> False` (not just a log line).

---

### `src/music_generation/suno.py` (service stub)

**Analog:** `src/generation_engine/cloud_backend.py` not-ready path (lines 119–130) —
the established way this codebase represents "backend exists but unusable":
```python
if not self._ready or not self.api_key:
    return GenerationOutput(
        images=[],
        seed=input.seed,
        metadata={
            "error": f"CloudAPIBackend[{self.provider.value}]: "
            f"No API key configured. ...",
            ...
        },
    )
```
⚠️ Divergence: Suno stub must **raise** `NotConfigured("Suno has no official public
API (as of Aug 2026); see .planning/research/MUSIC-GENERATION.md")` from every method
and return `is_configured() -> False` (research §4). Only the *intent* (explicit,
non-silent degradation) transfers; the mechanism becomes exceptions. No other stub
analog exists in the codebase — follow RESEARCH.md §4 verbatim for the rest.

---

### `src/music_generation/mock.py` (service, deterministic mock)

**Analog:** `src/generation_engine/mock_backend.py` (whole file, 71 lines)

Best-in-repo example of a deterministic, seed-derived placeholder backend used by
tests and offline pipelines.

**Class docstring + determinism contract** (lines 16–25):
```python
class MockBackend(GenerationBackend):
    """Generation backend that returns deterministic placeholder images.

    The colour is derived from the seed and prompt so re-running a job with
    the same seeds reproduces the same output (useful for regression tests).
    """
```

**Seed→output derivation via hash** (lines 60–63):
```python
def _seed_to_color(self, seed: int, prompt: str) -> tuple[int, int, int]:
    digest = hashlib.sha256(f"{seed}:{prompt}".encode()).hexdigest()
    return tuple(int(digest[i:i + 2], 16) for i in (0, 2, 4))
```
Adapt: research §4 wants seeded `random.Random(seed)` driving sine/silence sample
generation; keep the "same seed ⇒ identical bytes" property and document it in the
class docstring exactly like MockBackend does. Constructor knobs
(`base_size`, `draw_pattern` at lines 28–30) set the precedent for mock's
configurable latency/failure injection params.

---

### `scripts/generate_phase7.py` (utility, CLI batch/report)

**Analog:** `scripts/generate_phase5.py` (whole file, 192 lines)

Exact structural match: shebang, phase-docstring with Reproduction block,
sys.path bootstrap, argparse with defaults, report-line assembly, exit-code contract.

**Bootstrap + imports** (lines 1–18):
```python
#!/usr/bin/env python3
"""Phase 5 — Audio Bible & Music Production System verification + report.

Verifies ...
Reproduction:
    python scripts/generate_phase5.py
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.audio_bible import AudioBible, AudioProductionSystem, quality_checklist
```

**Argparse with help text and repo-root-relative path resolution** (lines 40–50):
```python
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--docs-dir", default="Audio",
                    help="Directory containing the Audio/ markdown bibles")
parser.add_argument("--out", default="PHASE5_REPORT.md",
                    help="Output report path")
args = parser.parse_args()

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

**Markdown report assembly + write + console summary + boolean exit code**
(lines 176–188):
```python
with open(out_path, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")

print(f"Doc consistency: {...}")
print(f"Report written:  {out_path}")
return 0 if doc_report.passed and plan.passed else 1
...
if __name__ == "__main__":
    sys.exit(main())
```

**Adaptations for Phase 7:** flags `--backend` (default from `MUSIC_BACKEND` env),
`--category`, `--topic`, `--dry-run` (prints resolved `MusicRequest` JSON, zero
network). Caption source: call `build_music_prompt(category, topic, duration_label,
vocals, mood)` from `src/audio_bible/prompts.py:185-215` (template fallback chain
shown there is already bible-conformant — reuse, don't re-implement). Negative
prompts: `category_negative(...)` + `AUDIO_NEGATIVE_BASE` from
`src/audio_bible/prompts.py:29-61,182`. Never touch `catalog.db`.

---

### `tests/test_music_generation.py` (test)

**Analog:** `tests/test_audio_bible.py` (343 lines)

**Header, package-level imports, ROOT constant, fixtures** (lines 1–29):
```python
"""Phase 5 tests — Audio Bible & Music Production System.

Covers library contents, brief resolution, ...
"""

import os

import pytest

from src.audio_bible import (
    AUDIO_NEGATIVE_BASE, AudioBible, ...
)
from src.audio_bible import libraries as lib


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def bible():
    return AudioBible()
```

**Test-class-per-component grouping + golden-value assertions** (lines 109–121):
```python
class TestMusicBrief:
    def test_build_standard(self, bible):
        brief = bible.build_music_brief(category="Alphabet", topic="letters",
                                        duration_label="Standard")
        assert isinstance(brief, MusicBrief)
        assert brief.duration_seconds == 120
        assert brief.tempo == 110
        assert brief.key == "C major"
```
Golden-value style maps directly to research's Validation Architecture table
(Bedtime → bpm 66, 3/4, `[instrumental` in scaffold; caption ≤512 chars).

**Env-var isolation convention:** `tests/test_generation_engine.py` lines 86–92:
```python
def test_cloud_backend_no_api_key(self, monkeypatch):
    monkeypatch.delenv("FAL_API_KEY", raising=False)
    monkeypatch.delenv("REPLICATE_API_KEY", raising=False)
    monkeypatch.delenv("BFL_API_KEY", raising=False)
```
Copy for `ACESTEP_API_KEY` / `MUSIC_BACKEND` cleanup; use `monkeypatch.setattr` for
transport injection (precedent: `tests/test_scoring_plugins.py:194`).

**Config already in place** (`pyproject.toml` lines 41–44): `asyncio_mode = "auto"`,
`testpaths = ["tests"]`, `timeout = 30` — no pytest config changes needed; all tests
must stay offline (no network, no catalog.db writes).

## Shared Patterns

### Package layout & public exports
**Source:** `src/generation_engine/__init__.py` + `src/audio_bible/__init__.py`
**Apply to:** `src/music_generation/__init__.py`
```python
BACKENDS: dict[str, type[GenerationBackend]] = { ... }   # private _BACKENDS + get_backend() factory
__all__ = ["MusicRequest", "MusicStatus", "MusicResult", "MusicGenerationBackend",
           "MusicBackendError", "NotConfigured", "BackendUnavailable", "GenerationFailed",
           "AceStepBackend", "SunoBackend", "MockBackend", "get_backend"]
```
Module docstring first line names the phase ("Phase N — …"), matching both packages.

### Pydantic v2 model conventions
**Source:** `src/models/schemas.py`
**Apply to:** `src/music_generation/models.py`
`BaseModel` + `Field(default_factory=...)` + `Optional[T] = None` + `Literal[...]`
for enums + `Field(default=..., ge=..., le=...)` for bounds + docstring per class.

### Typed exception hierarchy with explanatory docstrings
**Source:** `src/generation_engine/base.py:33-38` (`ModelLoadError`),
`src/pipeline/job_queue.py:23-24` (`JobError`)
**Apply to:** `src/music_generation/backends.py` — `MusicBackendError(Exception)`
base + `NotConfigured` / `BackendUnavailable` / `GenerationFailed` subclasses, each
with a docstring stating when it's raised. Raise (never log-and-return-empty) per
research §2 error mapping.

### Async-job lifecycle: submit → poll → download
**Source:** `src/generation_engine/cloud_backend.py:232-248` (Replicate),
`:290-318` (BFL incl. TimeoutError guard)
**Apply to:** `src/music_generation/ace_step.py` and the default
`generate()` orchestration loop in `backends.py` (interval 2 s, backoff ×2 capped ×8,
overall `timeout_s=300`). Terminal-state strings align with
`job_queue.py:15-20` transitions (`pending|running|completed|failed`).

### Credential/env configuration resolution
**Source:** `src/generation_engine/cloud_backend.py:84-98`
**Apply to:** `src/music_generation/ace_step.py` — constructor arg > env var
(`ACESTEP_API_KEY`, `ACESTEP_BASE_URL` default `http://localhost:8001`);
`is_configured()` reflects resolution result.

### Deterministic seed-derived placeholders
**Source:** `src/generation_engine/mock_backend.py:60-63`
**Apply to:** `src/music_generation/mock.py` — document the same-seed⇒same-bytes
contract in the class docstring; derive samples from `random.Random(seed)`.

### Script skeleton (bootstrap, argparse, report, exit code)
**Source:** `scripts/generate_phase5.py:1-18, 40-50, 176-192`
**Apply to:** `scripts/generate_phase7.py` — identical bootstrap and report-writing
conventions; add `--dry-run` semantics (print resolved request JSON, no network).

### Offline-first testing conventions
**Source:** `tests/test_audio_bible.py:1-29` (structure),
`tests/test_generation_engine.py:86-92` (monkeypatch env isolation)
**Apply to:** `tests/test_music_generation.py` — pytest classes per component,
golden-value asserts, fake transports injected via constructor/monkeypatch; zero
network in CI.

## Deliberate Divergences (do NOT copy these existing behaviors)

1. **ABC → Protocol.** `generation_engine/base.py` uses ABC; research mandates
   `typing.Protocol` + `@runtime_checkable` (isinstance-checkable without inheritance).
2. **`requests` → stdlib `urllib.request` + injectable transport.** All existing HTTP
   backends lazily import `requests` inside methods; Phase 7 wraps `urllib.request`
   in `_post_json/_get_json/_get_bytes` module functions with explicit timeouts and a
   `transport=` callable param (httpx/requests are NOT declared deps).
3. **Log-and-return-empty → raise typed exceptions.** Cloud/Comfy backends degrade by
   returning empty outputs with `metadata={"error": ...}`; Phase 7 adapters raise
   `NotConfigured` / `BackendUnavailable` / `GenerationFailed` per the research error
   map (connection errors → BackendUnavailable; 401/403 → NotConfigured;
   failed status / malformed response → GenerationFailed).
4. **Dataclasses → Pydantic.** Same-domain `audio_bible/models.py` uses frozen
   dataclasses; Phase 7 models are Pydantic v2 mirroring `schemas.py` (research-explicit).

## No Analog Found

| File / Portion | Role | Data Flow | Reason | Fallback |
|------|------|-----------|--------|----------|
| `src/music_generation/backends.py::generate()` orchestration w/ exponential backoff | service | event-driven | No existing default-method polling loop with backoff-cap exists (cloud loops are hardcoded sleep counts) | Follow RESEARCH.md §4 spec: interval 2 s, backoff 1→2→4→8 s cap, `timeout_s=300` |
| `src/music_generation/mock.py` WAV synthesis (RIFF header + samples) | service | transform | Grep confirms zero `wave`/`struct.pack`/`RIFF` usage anywhere in `src/` | RESEARCH.md §4: 44-byte RIFF header + seed-derived sine/silence; assert valid header in tests |
| `src/music_generation/ace_step.py` transport seam (`_post_json`/`_get_json`/`_get_bytes` + `transport=` callable) | utility | request-response | Existing backends call requests directly with no injection point | RESEARCH.md §4 contract; tests assert URL/path/method/headers/body on recorded fake-transport calls |

## Metadata

**Analog search scope:** `src/generation_engine/`, `src/image_generation/`,
`src/audio_bible/`, `src/pipeline/`, `src/models/`, `scripts/`, `tests/`
**Files read in full/part:** 13 (generation_engine: `__init__/base/cloud/comfy/mock`;
audio_bible: `__init__/models/prompts`; pipeline: `job_queue`; models: `schemas`;
scripts: `generate_phase5`; tests: `test_audio_bible`; `pyproject.toml`)
**Pattern extraction date:** 2026-08-21
