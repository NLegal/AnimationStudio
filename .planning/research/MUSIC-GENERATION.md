# Research: Music Generation Backends (Suno + ACE-Step) — Phase 5

> Researched 2026-08-21 for Phase 5 "Audio Bible & Music Production System"
> (`PHASE5.md`). Feeds the music-generation implementation phases.
> Constraint: this environment never generates images/audio; all integration
> must be runnable offline by the user and testable with mocks here.

## TL;DR

| | Suno (primary) | ACE-Step 1.5 / ACE-Step Studio (secondary, offline) |
|---|---|---|
| Official API | **None yet** — early-access announced 2026-07-01 (small partner cohort, no timeline/pricing) | **Yes** — local async REST API on `localhost:8001` |
| Access today | Web app only; consumer plans include no API. Third-party wrapper APIs exist (~$0.04–$0.11/song) with ToS/commercial-rights caveats | Open-source, self-hosted; unlimited free local generation |
| License/rights | Settled/licensed with Warner; commercial use tied to plan terms | Apache-2.0 lineage; v1.5 marketed as commercial-ready |
| Hardware | Cloud (none) | ~4 GB VRAM min, 8–12 GB+ recommended (CPU offload supported); Turbo XL weights ≈ 20 GB |
| Role in studio | Brand-quality flagship songs when access lands | Default offline workhorse + experimentation |

**Architecture consequence:** build a provider-agnostic
`MusicGenerationBackend` abstraction now, ship a fully working **ACE-Step
local-API adapter**, and keep **Suno behind the same interface** (official API
when it ships; optional third-party wrapper adapter clearly flagged).

## ACE-Step 1.5 (offline backend)

### What it is
Open-source 4B-parameter DiT music foundation model (`ace-step/ACE-Step-1.5`,
HuggingFace `ACE-Step/Ace-Step1.5`). Generates full vocal songs up to ~4 min,
50+ languages, structured lyrics, BPM/key/time-signature control, seeds.
"ACE-Step Studio" (timoncool/ACE-Step-Studio, MIT) is the portable one-click
offline packaging of it that PHASE5.md names — same engine underneath.

### Local REST API (the automation surface)
Default base URL `http://localhost:8001` (server: `python -m acestep.api_server`).

Workflow (async job pattern):
1. `POST /v1/music/generate` → `{job_id}`
2. Poll `GET /v1/jobs/{job_id}` (or batch `POST /query_result`) every 1–2 s
3. Download audio via `/v1/audio?path=...`

Key request parameters:
- `prompt` / `caption` — style description (≤512 chars)
- `lyrics` — ≤4096 chars; `[verse]`, `[chorus]`, `[bridge]` section markers;
  `[instrumental]` for no vocals
- `audio_duration` (s), `bpm`, `key_scale` (e.g. "C Major"), `time_signature`
- `seed`; batch jobs return multiple audios per task
- `thinking=true` → 5Hz LM enhances quality (slower, more VRAM)
- `model`: e.g. `acestep-v15-turbo` (fast) vs `acestep-v15-sft` (quality)

Ops knobs: `ACESTEP_API_KEY` (Bearer auth), `ACESTEP_OFFLOAD_TO_CPU=true`
(low VRAM), cache dir env vars, `/v1/models`, `/v1/stats`, health check.

Also available: Gradio UI, CLI, LoRA/LoKr training endpoints (out of scope),
hosted variants (HF Space, fal.ai, WaveSpeed) — not needed for offline.

## Suno (primary platform — future-facing)

- 2026-07-13 reporting: CPO Jack Brody opened an **early-access application**
  form; wording was "exploring", partner-cohort first. No public endpoint,
  keys, SDK, or docs exist today.
- Consumer Free/Pro/Premier plans do **not** include programmatic access.
- Third-party resellers (Lyrica, AI Music API, sunor.cc, …) expose REST APIs
  at roughly $0.04–$0.11/song; rights depend on reseller terms — treat as
  optional convenience adapters, never the pipeline's backbone.

## Mapping studio standards → ACE-Step parameters

The audio bible already encodes everything needed to drive the model:

| Studio standard (`src/audio_bible/`) | Maps to |
|---|---|
| Song categories (24) + topic | `caption` via existing `build_music_prompt()` |
| Tempo 80–130 BPM per category | `bpm` parameter |
| Major-key/simple-melody style guide | `key_scale` ("C Major", …) |
| Durations (30s/60s/120s/180s/300s labels) | `audio_duration` |
| Structure Intro→Verse→…→Outro | `[intro]/[verse]/[chorus]…` lyric markers |
| Negative prompts (`AUDIO_NEGATIVE_BASE`) | caption phrasing + post-filter metadata check |
| Voice profiles / TTS engines | later phase (Kokoro/XTTS v2/Piper are separate TTS stacks, not ACE-Step) |

## Risks / open questions

1. **VRAM contention**: user's GPU also runs ComfyUI (Flux). ACE-Step server
   should be started/stopped around music batches, or run with CPU offload.
2. **Model download size** (~20 GB) belongs on the generation machine
   (Colab/local PC), never in the repo or Drive budget.
3. **catalog.db stays untouched**: generated song artifacts need their own
   manifest (e.g. `Audio/Music/**` + JSON sidecar) rather than asset rows —
   consistent with the user's real-generation workflow.
4. Suno adapter must degrade gracefully (explicit `NotConfiguredError`) so the
   pipeline always has the offline path.
