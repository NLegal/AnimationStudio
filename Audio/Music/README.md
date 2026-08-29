# Music Generation — Backend Layer (Phase 7)

`src/music_generation/` is the provider-agnostic music generation layer for
Little Learning Town. It speaks to one real backend today, refuses a second
one loudly, and always offers a deterministic offline fallback:

| Backend | Name (`--backend` / `MUSIC_BACKEND`) | Status |
|---|---|---|
| ACE-Step Studio 1.5 (local REST service) | `ace-step` | Real adapter — async jobs: submit → poll → download |
| Suno | `suno` | Refusing stub — no official public API (as of Aug 2026) |
| Deterministic mock | `mock` | Always available offline; same seed ⇒ byte-identical WAV |

The experimental `SunoWrapperBackend` exists in code as a flagged integration
point for a future third-party relay. It is **disabled by default** and can
never be selected through the registry.

## Quickstart

```bash
# 1) Offline: print the resolved request as JSON (zero network I/O)
python scripts/generate_phase7.py --dry-run --category Bedtime --topic "sleepy moon"

# 2) Offline: generate a deterministic placeholder song via the mock
python scripts/generate_phase7.py --backend mock --category Bedtime --topic "sleepy moon" --seed 7

# 3) Live: one real song through your local ACE-Step service (manual smoke)
python scripts/generate_phase7.py --backend ace-step --category Bedtime --topic "sleepy moon"
```

Generated WAV files are written under `Audio/Music/` by default (`--out`
overrides). Nothing is ever written to the asset-catalog database.

## Environment

| Variable | Purpose | Source | Default |
|---|---|---|---|
| `ACESTEP_API_KEY` | Bearer credential sent as `Authorization: Bearer <key>` to the local ACE-Step service. **Optional** — when unset the header is omitted and the service is expected to be running with auth disabled | Your local ACE-Step Studio deployment configuration | *(unset — sends no auth header)* |
| `ACESTEP_BASE_URL` | Base URL of the local ACE-Step REST service | Set only if the service does not run at the default address | `http://localhost:8001` |
| `MUSIC_BACKEND` | Default backend selection when no `--backend` flag is given | Operator preference; Phase 8 pipeline wiring inherits this | `mock` |

Backend-selection precedence: **`--backend` flag > `MUSIC_BACKEND` env > `mock`**.
A constructor-level override (`api_key`, `base_url`) beats the environment when
embedding the library directly.

## ACE-Step 1.5 API contract

This adapter speaks the REAL ACE-Step 1.5 REST contract
(vendor `docs/en/API.md`) — not an assumed one:

- `GET  /health`              — readiness probe (`is_configured()`)
- `POST /release_task`        — create a task → `task_id`
- `POST /query_result`        — batch status query (`task_id_list`; int status:
  0 running, 1 succeeded, 2 failed)
- `GET  /v1/audio?path=...`   — download audio bytes

Every response is wrapped as `{data, code, error, ...}`. To honor the requested
seed, the payload sets `use_random_seed=false` alongside `seed`.

## Error taxonomy

Every failure surfaces as exactly one typed exception (all subclasses of
`MusicBackendError`):

| Exception | Meaning | First fixes |
|---|---|---|
| `NotConfigured` | The backend cannot be used at all: HTTP 401/403 from the service, or a refusing stub (Suno) | Verify the key against your local service; pick another backend |
| `BackendUnavailable` | The remote backend could not be reached: connection refused, DNS failure, or timeout on submit/poll/download | Confirm the ACE-Step service is running and reachable at `ACESTEP_BASE_URL`; retry later or fall back to `mock` |
| `GenerationFailed` | The generation job itself failed: terminal `failed` status (server error text included), malformed response bodies, or the overall deadline (300 s) expiring | Read the server error text; check service logs/GPU memory; re-run with a different seed |

Exception messages never contain credentials (the Bearer token is assembled at
call time and never logged).

## Determinism

The `seed` field controls reproducibility. The mock backend derives every
sample from `random.Random(seed)`: **the same effective seed produces
byte-identical output**, so tests and regression checks are stable offline.
Real ACE-Step generation honors the seed as its determinism hook per the
service contract.

## Live Smoke Checklist (MANUAL ONLY)

> CI and the pytest suite **never** require the ACE-Step service, a GPU, or
> network access. This checklist is the single manual verification step for an
> operator machine.

1. Start the local ACE-Step 1.5 service on `localhost:8001`
   (GPU ≥ 4 GB VRAM minimum; Turbo XL ~20 GB weights; optional CPU-offload env
   knob `ACESTEP_OFFLOAD_TO_CPU` documented by ACE-Step — our code never sets it).
   ACE-Step 1.5 pins `requires-python = >=3.11,<3.13`. If your interpreter is
   newer (e.g. Colab ships 3.13+), bring it up via `uv` which provisions a
   compatible isolated venv:
   `uv sync && uv run acestep-api` (do **not** `pip install -r requirements.txt`
   into a 3.13 env — it crashes at startup). When you spawn the server from a
   Jupyter/Colab kernel, force the headless backend by setting `MPLBACKEND=Agg`
   in the subprocess env — the kernel's `matplotlib_inline` backend is invalid
   in the isolated venv and crashes the import. Default `ACESTEP_NO_INIT=true`
   makes `/health` answer immediately and lazy-loads models on first request.
2. Export the API key: `export ACESTEP_API_KEY=<your-key>`
3. Run:
   ```bash
   python scripts/generate_phase7.py --backend ace-step --category Bedtime --topic "sleepy moon"
   ```
4. Confirm the job logs show a completed status and an audible WAV appears
   under `Audio/Music/`.
5. Delete or keep the generated artifact per operator preference.
6. (Optional) Batch generation through the pipeline wiring (Plan 08-01):
   ```bash
   python scripts/generate_phase5.py --generate --backend ace-step --category Bedtime --topic "sleepy moon"
   ```
   Confirm the WAV appears under `Audio/Music/` and `manifest.json` gains one entry.
   **Never executed in CI — requires the local ACE-Step service.**
