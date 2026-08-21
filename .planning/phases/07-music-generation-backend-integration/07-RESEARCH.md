# Phase 7 Research — Music Generation Backend Integration

> Authoring note: written by the orchestrator as a filesystem fallback after the
> gsd-phase-researcher subagent returned empty twice. Grounded in
> `.planning/research/MUSIC-GENERATION.md` (completed web research, this session)
> and direct codebase inspection of `src/audio_bible/`, `src/review_ui/app.py`,
> `src/pipeline/job_queue.py`, `src/models/schemas.py`, `pyproject.toml`.

## 1. Source-of-truth inputs

| Input | Location | Relevance |
|---|---|---|
| Web research (ACE-Step 1.5 + Suno) | `.planning/research/MUSIC-GENERATION.md` | API contract, capability matrix baseline |
| Phase 5 audio standards | `src/audio_bible/` (`bible.py`, `libraries.py`, `models.py`, `production.py`, `prompts.py`) | Category/vocal/mood standards this backend must serve |
| Music prompt builder | `src/audio_bible/prompts.py:185` `build_music_prompt(category, topic, duration_label, vocals, mood)` | Caption source for ACE-Step requests |
| Platform constants | `src/audio_bible/libraries.py:30-34` | `PRIMARY_MUSIC_PLATFORM="Suno"`, `SECONDARY_MUSIC_PLATFORM="ACE-Step Studio"` |
| Job lifecycle analog | `src/pipeline/job_queue.py` (`Job`, `create_job/update_status/get_job/list_jobs`) | In-memory job-state pattern to mirror |
| Model conventions | `src/models/schemas.py` | Pydantic v2 BaseModel style for request/result models |
| Review UI | `src/review_ui/app.py` (FastAPI + Jinja2) | Where Phase 8 will wire routes; Phase 7 stays library-only |

## 2. ACE-Step 1.5 local REST contract

Service is an EXTERNAL local server (ACE-Step Studio / ACE-Step 1.5), default
`http://localhost:8001`. Our code never starts or installs it; tests never require it.

- **Auth**: header `Authorization: Bearer <ACESTEP_API_KEY>` (env var). If unset → adapter raises `NotConfigured`.
- **Submit** — `POST /v1/music/generate`
  - JSON body fields: `prompt`/`caption` (≤512 chars), `lyrics` (≤4096 chars; `[verse]`/`[chorus]` markers, or `[instrumental]`), `audio_duration` (seconds), `bpm`, `key_scale` (e.g. `"C major"`), `time_signature` (e.g. `"4/4"`), `seed` (int — determinism hook), `thinking` (bool), `model` (`acestep-v15-turbo` | `acestep-v15-sft`)
  - Response: `{"job_id": "<id>", ...}`
- **Poll** — `GET /v1/jobs/{job_id}` → status `pending|running|completed|failed` (+ progress info); completed carries the audio path/URL.
- **Download** — `GET /v1/audio?path=<path-from-job>` → raw audio bytes.
- **Server env**: `ACESTEP_OFFLOAD_TO_CPU`; ≥4 GB VRAM min (Turbo XL ~20 GB weights) — irrelevant to our code, documented context only.
- **Error mapping**
  - connection refused / DNS failure / timeout on submit or poll → `BackendUnavailable`
  - HTTP 401/403 → `NotConfigured`
  - job status `failed` → `GenerationFailed`
  - malformed response (non-JSON, missing `job_id`) → `GenerationFailed`

## 3. Category → music-parameter mapping (proposal)

Phase 5 music categories: `Alphabet`, `Numbers`, `Colors`, `Animals`, `Bedtime`
(+ generic fallback via `_BASE_MUSIC_TEMPLATE`). Proposed defaults:

| category | caption seed | bpm | key_scale | time_signature | lyrics structure |
|---|---|---|---|---|---|
| Alphabet | "playful preschool alphabet song …" | 110 | C major | 4/4 | [verse][chorus][verse][chorus] |
| Numbers | "cheerful preschool counting song …" | 116 | D major | 4/4 | [verse][chorus][verse][chorus] |
| Colors | "bright preschool colors song …" | 108 | G major | 4/4 | [verse][chorus][bridge][chorus] |
| Animals | "fun preschool animal song …" | 120 | C major | 4/4 | [verse][chorus][verse][chorus] |
| Bedtime | "gentle preschool lullaby …" | 66 | F major | 3/4 | [instrumental intro][verse][chorus][verse][outro] |

Durations: 45–90 s typical; Bedtime 120 s. All captions composed via
`build_music_prompt()` so bible rules (category→topic→vocals→mood→key→melody→
instrumentation→atmosphere→duration) stay authoritative; the table above only
supplies the *numeric* params + lyric scaffold. Negative prompt:
`AUDIO_NEGATIVE_BASE` + `music` category negatives from
`src/audio_bible/prompts.py:29-61` where the API accepts one.

## 4. Protocol & package design questions — answered

- **Package**: new `src/music_generation/` with `__init__.py` exporting public names; modules: `backends.py` (protocol + registry), `ace_step.py`, `suno.py`, `mock.py`, `models.py` (Pydantic result types).
- **Protocol surface** (`MusicGenerationBackend`, `typing.Protocol`, runtime_checkable):
  - `is_configured() -> bool`
  - `submit(request: MusicRequest) -> str` (job id)
  - `poll(job_id: str) -> MusicStatus`
  - `download(job_id: str) -> bytes`
  - `generate(request: MusicRequest, *, timeout_s: float = 300, poll_interval_s: float = 2.0) -> MusicResult` — default-method convenience loop submit→poll→download with exponential backoff (cap ×8).
- **Exceptions**: base `MusicBackendError`; subclasses `NotConfigured`, `BackendUnavailable`, `GenerationFailed`. Live in `src/music_generation/backends.py`.
- **Models** (Pydantic v2, mirroring `src/models/schemas.py`): `MusicRequest` (category, topic, duration_s, vocals, lyrics_override, seed, tags), `MusicStatus` (state Literal["pending","running","completed","failed"], progress float, error Optional[str]), `MusicResult` (request, audio bytes, format "wav"/"mp3", job_id, backend name, seed used).
- **Catalog isolation**: results are returned in-memory only. NO writes to `catalog.db` (repo-root SQLite accessed by `src/asset_repository/sqlite_repo.py`). Persistence/integration into review pipeline is Phase 8's concern.
- **HTTP transport seam**: stdlib `urllib.request` wrapped in module-level functions (`_post_json`, `_get_json`, `_get_bytes`) taking an explicit timeout; adapters accept an optional `transport=` callable so tests inject fakes without network. No new dependencies (httpx/requests NOT in pyproject).
- **Mock backend**: seeded (`random.Random(seed)`), deterministic; synthesizes a tiny valid WAV (44-byte RIFF header + sine/silence samples derived from seed) so download-path parsing is exercisable offline; configurable latency/failure injection for tests.
- **Suno stub**: `SunoBackend.is_configured()` always False; every method raises `NotConfigured("Suno has no official public API (as of Aug 2026); see .planning/research/MUSIC-GENERATION.md")`. A separate `SunoWrapperBackend` (third-party relay) is allowed but MUST be flagged experimental and default-disabled.
- **Registry/discovery**: `get_backend(name)` factory ("ace-step", "suno", "mock"); ACE-Step health check = GET `/v1/jobs/health` or root probe with short timeout before first use.

## 5. Config / timeouts / polling

- Env: `ACESTEP_API_KEY` (auth), `ACESTEP_BASE_URL` (default `http://localhost:8001`), `MUSIC_BACKEND` (default selection for Phase 8 wiring).
- Timeouts: connect 5 s, read 30 s per HTTP call; generate() overall `timeout_s=300`; backoff 1→2→4→8 s capped.
- Poll interval 2.0 s default; mock returns immediately.

## Validation Architecture

Deterministic/offline-first. Nothing in CI touches network, audio hardware, or `catalog.db`.

| Deliverable | Verified by | Environment |
|---|---|---|
| Protocol + exception taxonomy | unit tests: isinstance checks against `runtime_checkable` Protocol; subclass assertions | offline CI |
| Request builder (category→params) | golden-value assertions: Bedtime → bpm 66, 3/4, `[instrumental` in lyrics scaffold; caption ≤512 chars; built from `build_music_prompt` output containing category keyword | offline CI |
| ACE-Step adapter submit | fake transport records URL/path/method/headers/body; assert `POST {base}/v1/music/generate`, Bearer header from env, body field constraints (lyrics ≤4096 etc.) | offline CI (monkeypatched transport) |
| ACE-Step poll/download | scripted fake transport sequence pending→running→completed→bytes; assert state transitions + payload pass-through | offline CI |
| Error mapping | fake transport raising URLError→BackendUnavailable; 401→NotConfigured; failed-status JSON→GenerationFailed | offline CI |
| Mock backend determinism | same seed twice → identical bytes; different seeds differ; valid RIFF/WAV header asserted | offline CI |
| Suno stub | every method raises NotConfigured with message citing missing official API | offline CI |
| generate() orchestration | mock backend with injected latency; assert timeout enforcement and backoff call counts via fake clock/transport | offline CI |
| Live service smoke | manual checklist: start ACE-Step locally, run scripts/generate_phase7.py --backend ace-step --dry-run then real single-song run | integration machine ONLY (manual) |

Test file: `tests/test_music_generation.py`, pytest classes per component, matching
existing conventions (`tests/test_audio_bible.py` style; asyncio_mode=auto already configured).

## Recommended Plan Structure

Two plans, sequential (single wave would also work but split keeps reviews focused):

- **Plan 01 (Wave 1)** — Core layer: `src/music_generation/` models, protocol,
  exceptions, category→params mapping, mock backend, transport seam +
  `tests/test_music_generation.py` covering all of the above.
- **Plan 02 (Wave 2)** — Real adapters + glue: `ace_step.py` full adapter against
  fake-transport contract suite, `suno.py` stub (+flagged wrapper), `get_backend`
  registry/env config, `scripts/generate_phase7.py` CLI (--backend, --category,
  --topic, --dry-run printing the resolved request JSON without any network call),
  README/Audio docs touch-up, live-service manual smoke checklist doc.

Depends-on chain: Plan 02 depends on Plan 01 (imports protocol/models/mock).

Constraint reminders for plans: no image generation anywhere; `catalog.db`
never modified; no network in tests; stdlib urllib only (no new deps).
