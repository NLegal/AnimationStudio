# API Coverage — ACE-Step Studio local REST service (+ Suno baseline re-decision)

> Full coverage by default. Opt-outs are explicit, reasoned decisions.
> Produced at plan time per the API Coverage Decision Checkpoint.
> Sources: `07-RESEARCH.md` §2 (REST contract), §4 (protocol design).

## Surface 1: ACE-Step Studio (primary backend)

External LOCAL service at `ACESTEP_BASE_URL` (default `http://localhost:8001`). Our code never starts or installs it; tests never require it.

| capability | decision | reason |
|---|---|---|
| generate.submit (`POST /v1/music/generate`) | INTEGRATE | Core async-job entry point of the locked REST contract (RESEARCH §2) |
| jobs.poll (`GET /v1/jobs/{job_id}`) | INTEGRATE | Required to observe pending/running/completed/failed lifecycle |
| audio.download (`GET /v1/audio?path=<path>`) | INTEGRATE | Retrieves completed audio bytes in-memory |
| health.probe (`GET /v1/jobs/health` or root) | INTEGRATE | Short-timeout reachability check backing `is_configured()` |
| orchestrate.generate (client submit→poll→download loop w/ backoff) | INTEGRATE | Default protocol method; convenience for Phase 8 wiring |
| seed.control (request `seed` field passthrough) | INTEGRATE | Determinism hook required by validation strategy |
| model.selection (`acestep-v15-turbo` \| `acestep-v15-sft`) | INTEGRATE | Explicit request field in locked contract |
| negative.prompt | OPT-OUT | not a field in the locked REST contract §2 body-field list; `music_negative_prompt()` helper (AUDIO_NEGATIVE_BASE + category negatives from bible standards) retained as documented future-use for Phase 8 / if the API ever adds such a field |
| error.surface (connection/401/failed/malformed mapping) | INTEGRATE | Typed exception map: BackendUnavailable / NotConfigured / GenerationFailed |

## Surface 2: Suno (secondary platform — same need, full baseline re-decided)

Per checkpoint rules the second integration against the same need re-decides every
capability from the full-coverage baseline rather than carrying over opt-outs.

| capability | decision | reason |
|---|---|---|
| suno.generate.submit | OPT-OUT | no official public API exists (as of Aug 2026); stub raises NotConfigured (RESEARCH §4) |
| suno.jobs.poll | OPT-OUT | no official public API exists (as of Aug 2026); stub raises NotConfigured |
| suno.audio.download | OPT-OUT | no official public API exists (as of Aug 2026); stub raises NotConfigured |
| suno.health.probe | OPT-OUT | nothing to probe — `is_configured()` is constant False |
| suno.third-party-wrapper | OPT-OUT (default-disabled) | optional `SunoWrapperBackend` allowed but MUST be flagged experimental and default-disabled; not part of default registry resolution |

## Mock backend

Not an external API — deterministic in-process backend for tests. Excluded from the matrix (no external surface).
