# Project Research Summary

**Project:** AI Nursery Rhyme Studio
**Domain:** AI-powered children's animation production pipeline
**Researched:** 2026-07-28
**Confidence:** HIGH (all four research areas cross-validated against multiple independent sources)

## Executive Summary

AnimationStudio is a permanent AI-powered nursery rhyme animation studio, not a tool for making individual videos. The industry consensus in 2026 is that production-grade AI animation pipelines use a **staged DAG architecture with agentic orchestration** — each stage (story, lyrics, music, images, video, lip-sync, subtitles, assembly) is independently replaceable, communicates through typed contracts, and is governed by a central Director agent. The dominant runtime is ComfyUI, which every major open-weights model supports day-one. The #1 unsolved-hard problem across every platform remains **character consistency across shots, scenes, and episodes** — and the #2 gap is **singing lip-sync at production quality**.

The recommended approach builds a **Persistent Character Database** as the foundational asset that compounds over time. The stack is FLUX.1 [schnell] for image generation (Apache 2.0, commercial-safe), Wan 2.2 for primary video generation (Apache 2.0), ACE-Step v1.5 for music (self-hosted, zero per-track cost), PuLID + Face LoRA + ControlNet OpenPose stacked for character identity lock (~95%+ consistency), LatentSync 1.6 for lip-sync, and DaVinci Resolve Studio for timeline assembly. The key risk is building pipeline stages tightly coupled to specific AI models — the phase 1 architecture **must** define stage interfaces (adapter/wrapper pattern) so that individual models can be swapped without pipeline rewrites. The second critical risk is LoRA training without pose/lighting diversity, which causes character drift that cannot be fixed in post-production. Both risks are preventable with upfront design discipline.

The research is unanimous across 30+ sources: build the character asset system first, then the single-video pipeline, then batch/scale operations. The Persistent Character Database is the single highest-leverage investment — no current mass-market platform has a true persistent character DB with versioned reference sheets, expression libraries, and per-episode usage tracking. Owning this is the project's core competitive moat.

## Key Findings

### Recommended Stack

The stack is mature and well-documented across the 2026 production landscape. The full analysis is in [STACK.md](./STACK.md).

**Core technologies:**

- **ComfyUI** (latest stable): Universal AI pipeline runtime — every major model ships ComfyUI nodes day-one, the only runtime that chains image gen → video gen → upscale → lip-sync in a single graph.
- **FLUX.1 [schnell]** (Apache 2.0): Primary image generation — commercial-safe license, sub-second generation, 8GB VRAM minimum.
- **FLUX.2 [dev]** (open weights, 32B): Hero keyframes and reference sheets — highest quality locally-runnable Flux, requires 24GB+ VRAM, non-commercial license use for R&D only.
- **Wan 2.2 14B** (Apache 2.0): Primary video generation — best physics/motion quality of open models, 12GB min VRAM.
- **LTX 2.3 22B** (Apache 2.0): Speed/lower-VRAM fallback — 90s per 5s clip, 8GB VRAM with GGUF, native audio-video sync, ideal for Cocomelon stylized output.
- **PuLID + Face LoRA + ControlNet OpenPose**: Four-layer character consistency stack — PuLID at weight 0.8 locks identity, Face LoRA at 0.6 provides full identity, ControlNet at 0.5 locks body pose. Combined: ~95%+ consistency.
- **ACE-Step v1.5** (Apache 2.0): Self-hosted music generation — zero per-track cost, full LoRA support, Python module integration. Suno v5 API as quality fallback.
- **Kokoro-82M** (Apache 2.0): Primary TTS — tiny footprint (82M params), GPU-accelerated, commercial-safe. Chatterbox (MIT) as premium alternative.
- **LatentSync 1.6** (Apache 2.0): Primary lip-sync — 512x512 face resolution, diffusion-based quality, LPIPS 0.089, ~8GB VRAM.
- **DaVinci Resolve Studio** ($295 one-time): Video editing/compositing — full Python scripting API for automation.
- **faster-whisper + WhisperX + Demucs**: Subtitle pipeline — 4x faster than OpenAI Whisper, word-level timing via wav2vec2 forced alignment, Demucs for vocal separation on sung lyrics.
- **Topaz Video AI** ($299/yr): Primary upscaling — Starlight Precise 2.5 model tuned for GenAI face detail. FlashVSR (Apache 2.0) as free alternative.
- **Claude API + Ollama/local fallback**: LLM for story generation, lyric writing, scene breakdown.

**Hardware baseline (production):** RTX 4090 24GB, 64GB RAM, 4TB NVMe SSD. Minimum viable: RTX 3060 12GB / RTX 4060 Ti 16GB.

### Expected Features

Full landscape in [FEATURES.md](./FEATURES.md). The AI animation pipeline market in 2026 has converged on end-to-end platforms. Key takeaways:

**Must have (table stakes) — 11 features users expect as baseline:**
- Script/story text input with automatic scene breakdown
- Basic character reference image upload (1-5 images)
- Multi-scene generation (not isolated clips)
- AI voiceover / TTS with multiple voice options
- Background music overlay
- Auto-generated subtitles (SRT from transcript)
- Multi-aspect-ratio export (16:9, 9:16, 1:1)
- MP4 download (H.264 baseline)
- Scene-by-scene preview before full render
- Project save/resume
- Quality check on output

**Should have (competitive differentiators) — Tier 1 (Core IP, hard to copy):**
1. **Persistent Character Database** — structured identity records with versioning, per-episode tracking. **No mass-market platform has this. This is the project's core moat.**
2. **Character Turnaround & Expression Sheets** — auto-generate multi-angle reference + phoneme-based singing mouth shapes
3. **Singing Lip-Sync Engine** — word-level sync optimized for sung vocals, not dialogue. **The hardest technical problem — no platform does this well at production quality**
4. **Karaoke Subtitle Engine** — ASS format with `\kf` karaoke fill tags, child-friendly typography, multi-language
5. **Reusable World/Asset Library** — children's-content-specific backgrounds and props with lighting variants
6. **Checkpointed Pipeline with Resume** — zero-waste retry from any stage

**Tier 2 (Operational Excellence):** Music generation with lyric integration, automated thumbnails, multi-language pipeline (swap audio+subs only, never regenerate video), batch production mode, model router (cost-aware), quality gates with human approval.

**Defer (v2+):** Episode versioning/changelog, cost tracking dashboards, platform-specific metadata generation, analytics integration.

**Anti-features (explicitly don't build):** Real-time streaming, end-user UGC platform, generic video generation, frame-by-frame manual editing UI, custom model training UI, watermarks, social features.

### Architecture Approach

Full design in [ARCHITECTURE.md](./ARCHITECTURE.md). The architecture is a **staged DAG pipeline with agentic orchestration** (the "Director" agent pattern).

**11 pipeline stages with typed contracts:**
1. **Story Generation (L1)** — LLM produces structured story with scene breakdown, character mapping, educational goals
2. **Lyrics Generation (L2)** — LLM produces singable lyrics with meter/rhyme scheme
3. **Music Generation (L3)** — ACE-Step generates instrumental + vocal from lyrics (timing reference for everything downstream)
4. **Storyboard Generation (L4)** — Shot list with camera directions, continuity tracking
5. **Image Generation (L5)** — Flux + PuLID + LoRA + ControlNet for character-consistent keyframes
6. **Video Generation (L6)** — Wan 2.2 / LTX 2.3 I2V animation from keyframes
7. **Lip-Sync Animation (L7)** — LatentSync aligns mouth shapes to sung audio
8. **Video Editing & Assembly (L8)** — DaVinci Resolve/FFmpeg timeline assembly with color grading
9. **Subtitle Generation (L9)** — WhisperX word-level karaoke captions
10. **Quality Control (L10)** — Multi-check pass (CLIP, face sim, AV sync, loudness)
11. **Publishing (L11)** — Transcode, upload, metadata per platform

**Key patterns:**
- **Staged DAG with Typed Contracts** (Pydantic models) — foundational pattern ensuring model-swapability
- **Agentic Orchestration with Director Agent** — manages end-to-end flow, detects failures, retries intelligently
- **Prompt Anchoring** — extract visual anchors from first shot, inject into subsequent shots to prevent drift
- **Model Access Gateway with Failover** — unified endpoint with circuit breaker, multi-model fallback
- **Layered QC Gates** — per-stage validation before passing to next stage (catches bad images before they waste expensive video compute)
- **4-Property Asset Versioning** — one identity per asset, numbered versions, canonical current, rollback as first-class operation
- **Multi-Stage Recovery** — retry → circuit breaker → fallback model → human escalation

**Parallel execution:** L1-L3 sequential (Story → Lyrics → Music), L4-L5 parallel (Storyboard + Image Gen start simultaneously), L6 sequential (Video needs images), L7-L9 parallel (Lip-sync + Subtitles), L10-L11 sequential (QC → Publish).

### Critical Pitfalls

Full catalog in [PITFALLS.md](./PITFALLS.md). Six critical pitfalls that can cause rewrites or major issues:

1. **CRITICAL-1: Training LoRAs Without Pose/Lighting Diversity** — The most common character consistency failure. If a LoRA is trained on 28+ front-facing portraits, it memorizes the pose, not the character. Side profiles and action shots produce different-looking characters. **Prevention:** Enforce pose diversity (30% close-up, 30% medium, 25% full-body, 15% "weird" angles), include lighting variation, test on "hard" prompts (side profile, extreme angle) immediately after training.

2. **CRITICAL-2: Captioning the Character Into the Background** — Every caption includes setting details (forest, soft lighting). The trigger token absorbs co-occurring concepts. Prompting the character in a new setting pulls in foliage/warm light. **Prevention:** Training captions must contain ONLY invariant character traits (red jacket, short black hair, freckles). Strip all setting tags. Use automated preprocessing.

3. **CRITICAL-3: No Shadow Deployment for Model Swaps** — Swapping Flux 1.x → 2.x causes 0.5% failure rate to spike to 15% because prompts were implicitly tuned to old model quirks. **Prevention:** Always run a 1-2 week shadow period where the new model processes live traffic but responses aren't served. Never allow auto-upgrade on production endpoints.

4. **CRITICAL-4: No Quality Gates Between Pipeline Stages** — Defects compound: bad image → bad video → unusable export. Reviewers develop fatigue. Unreviewed outputs pile up. **Prevention:** Every stage produces a quality score with automatic pass/fail threshold. Rejected outputs go to dead letter queue, not downstream. Track "regeneration cost tax" — if >20% of clips regenerate, quality gates are missing.

5. **CRITICAL-5: Pipeline Designed Around One AI Model** — The entire pipeline hardcoded to one model's API schema. Swapping models requires a 3-6 month rewrite. **Prevention:** Define stage interface contracts before implementing any stage. Use adapter/wrapper pattern. Changing a model endpoint must require touching at most 2 files.

6. **CRITICAL-6: Asset Graveyard — No Versioning or Lifecycle Management** — After 3 months: 14,000 files with names like `character_v2_final_NEW.png`. Nobody knows canonical version. Deprecated assets get reused. **Prevention:** Every asset has exactly one identity with numbered versions. Lifecycle: Draft → In Review → Approved → Deprecated. One "Approved" version at any time. Automated cleanup of drafts older than N months.

## Implications for Roadmap

The research across all four areas converges on a clear phase structure. Dependencies are explicit: character system before visual generation, story before music before images before video, single-video pipeline before batch operations.

### Phase 1: Architecture Foundation & Pipeline Shell

**Rationale:** Everything depends on the pipeline shell. This phase defines the contracts that prevent CRITICAL-5 (vendor lock-in) and CRITICAL-6 (asset graveyard). Must be built before any model integration.

**Delivers:** Stage interface contracts (Pydantic models), Asset Store schema (PostgreSQL + MinIO), API Gateway with model registry, basic Orchestrator, project scaffolding with ComfyUI.

**Addresses from FEATURES.md:** None directly — this is infrastructure that enables all features.

**Avoids:** CRITICAL-5 (adapter pattern at stage boundaries), CRITICAL-6 (versioning schema designed before assets exist).

**Stack elements:** ComfyUI setup, Python 3.11, PostgreSQL schema, MinIO/S3 configuration.

**Architecture components:** Pipeline Shell, Asset Store, API Gateway, Model Registry.

**Research flag:** STANDARD PATTERNS — infrastructure setup is well-documented; no need for `/gsd-plan-phase --research-phase`.

---

### Phase 2: Character System — The Core Differentiator

**Rationale:** The Persistent Character Database is the project's core moat. Every downstream stage (images, video, storyboard) needs character references. This phase must also establish the LoRA training pipeline with diversity enforcement, because training LoRAs later requires correct data from day one.

**Delivers:** Persistent Character Database (structured identity records, versioning, per-episode tracking), multi-angle reference sheet generation (front/3/4/profile/back), expression library (12 expressions including phoneme-based singing mouth shapes), LoRA training pipeline with dataset curation, caption preprocessing pipeline, world background library (5 environments × 3 lighting conditions), props library.

**Addresses from FEATURES.md:** Persistent Character Database, Character Turnaround & Expression Sheets, Reusable World/Asset Library.

**Avoids:** CRITICAL-1 (pose diversity enforcement in dataset spec), CRITICAL-2 (automated caption tag stripping), MODERATE-1 (bucketed training), MODERATE-2 (regularization images), MODERATE-3 (LR/dataset size matching).

**Stack elements:** FLUX.2 [dev] for reference sheets, SDXL for LoRA training base, ComfyUI-FluxTrainer, PuLID.

**Architecture components:** Asset Store (versioned character records), Prompt Template System (character descriptors).

**Research flag:** NEEDS DEEPER RESEARCH — LoRA training pipeline specifics (kohya-ss configuration, Flux vs SDXL training tooling maturity), PuLID + LoRA integration testing. Use `/gsd-plan-phase --research-phase` during planning.

---

### Phase 3: Story & Music Content Pipeline

**Rationale:** Story, lyrics, and music are the cheapest compute stages and produce the structural blueprint for everything downstream. Music duration determines scene count and timing. These stages must be stable before visual generation begins (you can't generate images for scenes you haven't written yet).

**Delivers:** LLM integration for story generation (Claude API), lyrics generation with rhyme/meter enforcement, music generation pipeline (ACE-Step), scene planning (beat-synced scene count from song duration), prompt template registry.

**Addresses from FEATURES.md:** Script/story text input, Music Generation with Lyric Integration.

**Avoids:** MODERATE-4 (sample rate spec defined before audio pipeline: 48kHz/24-bit/mono).

**Stack elements:** Claude API + Ollama fallback, ACE-Step v1.5, Python text processing.

**Architecture components:** Story Generator (L1), Lyrics Generator (L2), Music Generator (L3), Orchestrator.

**Research flag:** LOW — LLM prompt chaining and music model APIs are well-documented. Consider research-phase for nursery-rhyme-specific lyric structuring if quality is poor.

---

### Phase 4: Visual Pipeline — Image & Video Generation

**Rationale:** Image generation is the first GPU-intensive stage and depends on the character system (Phase 2) and story breakdown (Phase 3). Video generation is the most expensive stage (10-100x image cost) — QC gates must be in place before this runs to prevent wasting compute on bad inputs.

**Delivers:** Character-consistent image generation (Flux + PuLID + Face LoRA + ControlNet OpenPose), storyboard generation with prompt anchoring, image-to-video generation (Wan 2.2 primary, LTX 2.3 fallback), per-stage QC gates (CLIP score >0.30, face similarity >0.85, LPIPS <0.15).

**Addresses from FEATURES.md:** Basic character reference upload, Multi-scene video generation, Scene-by-scene preview (partially).

**Avoids:** CRITICAL-4 (QC gates at image→video boundary), MODERATE-1 (aspect ratio matching between training and inference).

**Stack elements:** FLUX.1 [schnell], PuLID, ControlNet OpenPose, Wan 2.2 14B, LTX 2.3 22B, FaceDetailer.

**Architecture components:** Storyboard Generator (L4), Image Generator (L5), Video Generator (L6), QC Gate layer.

**Research flag:** STANDARD PATTERNS — Flux + PuLID + Wan 2.2 are well-documented. QC metrics are standardized. Skip research-phase unless integrating a new model.

---

### Phase 5: Audio-Visual Assembly & Export

**Rationale:** Lip-sync, subtitles, and timeline assembly all need stable video and audio inputs from previous phases. Lip-sync is the hardest technical problem (singing, not speaking) and may require the most iteration. Subtitles depend on final audio timing. Assembly depends on everything.

**Delivers:** Singing lip-sync engine (LatentSync 1.6 for final quality, MuseTalk for preview), TTS integration (Kokoro + Chatterbox), karaoke subtitle pipeline (Demucs → WhisperX → karaoke-subs → ASS), video editing/assembly (DaVinci Resolve API + FFmpeg), color grading pass (MODERATE-3 prevention), upscaling pipeline (Topaz Starlight / FlashVSR to 4K), frame interpolation (RIFE / Topaz Chronos to 60fps), automated thumbnail generation, MPC export with QC pass.

**Addresses from FEATURES.md:** AI voiceover/TTS, Auto-generated subtitles, Karaoke Subtitle Engine, Singing Lip-Sync Engine, Automated Thumbnail Generation.

**Avoids:** MODERATE-4 (48kHz/24-bit/mono audio spec enforced), MINOR-3 (color grading as mandatory pipeline stage), MINOR-4 (reference sheets at 4K resolution).

**Stack elements:** LatentSync 1.6, MuseTalk, Kokoro, Chatterbox, faster-whisper, WhisperX, Demucs, DaVinci Resolve Studio, FFmpeg, Topaz Video AI, RIFE.

**Architecture components:** Lip-Sync Animator (L7), Video Editor (L8), Subtitle Generator (L9), Quality Controller (L10 partial).

**Research flag:** NEEDS DEEPER RESEARCH — singing lip-sync is the hardest technical problem (no platform does it well at production quality). The LatentSync docs don't explicitly address multi-second sung notes vs spoken dialogue. Use `/gsd-plan-phase --research-phase --deep`.

---

### Phase 6: Operations — Scale Multi-Language & Publish

**Rationale:** Batch production, multi-language, and publishing depend on a stable single-video pipeline. Attempting batch before the single-video pipeline is solid multiplies failures. Multi-language should ONLY swap audio + subtitles — never regenerate video — which requires the assembly pipeline to support track-swapping.

**Delivers:** Batch production mode (CSV-driven, N videos at once), multi-language pipeline (translate → localized TTS → localized karaoke subs — reuse video), multi-platform publishing (YouTube API, TikTok, Instagram), cost tracking and budget management, cold-view human review gates, model shadow deployment infrastructure.

**Addresses from FEATURES.md:** Multi-aspect-ratio export, Project save/resume, Batch Production Mode, Multi-Language Pipeline, Checkpointed Pipeline with Resume, Quality Gate with Human Approval.

**Avoids:** CRITICAL-3 (shadow deployment infrastructure), MODERATE-5 (cold-view review process), MODERATE-6 (retry strategy with error classification), MINOR-1 (style modifier limits), MINOR-5 (cost monitoring), MINOR-6 (regeneration tax).

**Stack elements:** YouTube API, DaVinci Resolve MCP Server, WhisperX for multi-language subtitles.

**Architecture components:** Quality Controller (L10 full), Publisher (L11), Batch Processing subsystem.

**Research flag:** NEEDS RESEARCH — YouTube API quota management, TikTok/Instagram publishing APIs, multi-language subtitle resyncing. Use `/gsd-plan-phase --research-phase` for batch processing and publishing.

---

### Phase Ordering Rationale

1. **Phase 1 (Foundation) before Phase 2 (Characters)** — The Asset Store schema must exist before characters can be stored. Stage contracts must exist before any model is integrated.
2. **Phase 2 (Characters) before Phase 4 (Visuals)** — Image generation needs trained LoRAs and reference sheets. Cannot generate consistent character images without the character system.
3. **Phase 3 (Story/Music) before Phase 4 (Visuals)** — Scene breakdown from lyrics determines what images to generate. Music duration determines scene count and timing.
4. **Phase 4 (Visuals) before Phase 5 (Assembly)** — Video clips must exist before lip-sync can align to them. Audio must exist before subtitles can be timed.
5. **Phase 5 (Assembly) before Phase 6 (Operations)** — Batch and multi-language require a proven single-video pipeline.
6. **QC gates built incrementally** — Phase 1 defines the QC framework (schema validation), Phase 4 adds visual QC, Phase 5 adds AV sync QC, Phase 6 completes the full QC matrix.

### Research Flags

**Needs deeper research during planning:**
- **Phase 2:** LoRA training pipeline specifics (kohya-ss configuration, Flux vs SDXL training tooling maturity, PuLID+LoRA stacking test results). Use `/gsd-plan-phase --research-phase`.
- **Phase 5:** Singing lip-sync is the hardest technical problem — LatentSync docs don't explicitly address multi-second sustained notes vs spoken dialogue. Requires hands-on testing. Use `/gsd-plan-phase --research-phase --deep`.
- **Phase 6:** YouTube API quota management, TikTok/Instagram publishing APIs, multi-language subtitle resyncing architecture. Use `/gsd-plan-phase --research-phase`.

**Standard patterns (skip research-phase):**
- **Phase 1:** Infrastructure setup, ComfyUI installation, PostgreSQL, MinIO. All well-documented.
- **Phase 4:** Flux + PuLIF + Wan 2.2 image/video generation. ComfyUI node workflows are well-documented.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | **HIGH** | Cross-referenced from 15+ sources including benchmarks, production comparisons, and license analyses. Stack choices have clear rationale with alternatives explicitly ruled out. |
| Features | **HIGH** | Cross-validated across 15+ competing platforms. Feature tiers are well-supported by competitive analysis. Persistent Character DB identified as clear differentiator gap. |
| Architecture | **HIGH** | Patterns verified against production code (myccarl/ai-shortVideo-pipeline), peer-reviewed research (IJIRMPS 2026), academic papers (AutoMV 2025), and vendor architectures (GMI Cloud). DAG + Director Agent pattern is industry consensus. |
| Pitfalls | **HIGH** | Each pitfall backed by multiple production practitioner sources. LoRA diversity and caption bleed issues are well-documented failure patterns with known prevention strategies. Phase-specific warnings cross-referenced with architecture phase suggestions. |

**Overall confidence: HIGH**

All four research areas have strong source quality with multiple independent corroborations. The stack choices have clear winners in each category. The architecture patterns are industry-standard. The pitfalls are well-documented from production experience across teams.

### Gaps to Address

1. **Singing lip-sync production quality gap** — No platform or documented workflow achieves production-quality singing lip-sync. LatentSync quality is high for spoken dialogue but unverified for multi-second sung notes. **Handle during execution:** Prototype LatentSync on 30s of nursery rhyme audio in Phase 5 execution; budget 2-3 iteration cycles for tuning parameters.

2. **Flux LoRA training maturity** — The stack recommends SDXL for LoRA training with Flux for inference. Flux-native LoRA tooling (ComfyUI-FluxTrainer) is less mature than SDXL's kohya-ss. **Handle during planning:** Research-phase for Phase 2 should test Flux-native LoRA quality vs SDXL-trained LoRA applied at inference. If Flux-native quality is sufficient, simplify the pipeline.

3. **DaVinci Resolve scripting API ceiling** — The free Resolve version has no external scripting API. The paid Studio version ($295) is required. If budget constraints prevent the Studio purchase, the pipeline must use FFmpeg-only assembly. **Handle during planning:** Budget $295 for DaVinci Resolve Studio; design FFmpeg-only assembly as a parallel track in case of procurement delays.

4. **Commercial license validation** — Several recommended models have nuanced commercial terms: FLUX.2 [dev] (non-commercial for R&D), HunyuanVideo 1.5 (excludes EU/UK/South Korea, requires license above 100M MAU), XTTS v2 (CPML non-commercial). **Handle during planning:** Legal review of all license terms before production deployment. Maintain a "go/nogo" matrix per model for commercial use.

## Sources

### Primary (HIGH confidence — verified across multiple sources)
- [STACK.md](./STACK.md) — 15 sources including Digital Applied (Jun 2026), pxz.ai (Jan 2026), Earngenix (Jul 2026), aiofm (Apr 2026), AI Video Sensei (Jul 2026), Creative AI News (May 2026)
- [FEATURES.md](./FEATURES.md) — 20 sources including OiiOii, Ciaro Pro, Atlabs, M Studio, Genor, U-Gen, Fliki, AnimeLoom, Pixel Dojo, kennedyraju55/ai-video-studio-public, identity-locked-film-pipeline
- [ARCHITECTURE.md](./ARCHITECTURE.md) — 11 sources including GMI Cloud (2026), myccarl/ai-shortVideo-pipeline (566 stars), IJIRMPS (2026, peer-reviewed), AutoMV (arXiv 2025), Cinemagiq (2026), ImageBench (2026)
- [PITFALLS.md](./PITFALLS.md) — 19 sources including Tudor Morari character consistency playbook, qcrao/Comicory LoRA pitfalls, Tian Pan model migration playbook, Wazza.ai QC system, Steve Light error handling, Cinemagiq asset versioning

### Secondary (MEDIUM confidence — single source or narrower scope)
- Multi-language pipeline architecture (Cutrix 2026, Perso AI 2026)
- Batch production patterns (Fliki, kennedyraju55 2026)
- Cold-view review practice (Vidu AI 2026)
- Draft-to-final tiering (Atlas Cloud 2026)

---

*Research completed: 2026-07-28*
*Ready for roadmap: yes*
