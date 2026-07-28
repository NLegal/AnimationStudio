# Technology Stack

**Project:** AI Nursery Rhyme Studio
**Researched:** 2026-07-28
**Overall confidence:** HIGH (cross-referenced from multiple 2026 sources)

## Recommended Stack

### Core Orchestration & Runtime

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| ComfyUI | Latest (2026 stable) | Universal AI pipeline runtime | Industry standard node-based workflow engine. Every major open-weights model (Flux, Wan, LTX, Hunyuan) ships ComfyUI partner nodes day-one. ~25% faster than A1111 on complex workflows. The only runtime that can chain image gen → video gen → upscale → lip-sync in a single graph. |
| Python 3.11+ | 3.11-3.12 | Backend pipeline scripting | DaVinci Resolve scripting API requires Python 3; ComfyUI custom nodes are Python. 3.11 for performance improvements over 3.10. |
| Node.js 20 LTS | 20.x | Web API / UI layer | If a web frontend is needed for job submission. Not core to the pipeline itself. |

### Image Generation

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **FLUX.1 [schnell]** | v1 (Apache 2.0) | Primary image gen for characters, backgrounds, props | Apache 2.0 license — clean for commercial use. Sub-second generation (BFL claims). 8GB min VRAM / 12GB recommended. Built for speed and consistency. |
| **FLUX.2 [dev]** | v2 (Nov 2025, 32B, open weights) | High-quality hero images, multi-reference compositing | 32B params — the highest-quality locally-runnable Flux. Multi-reference support for up to 10 images. Requires 24GB+ VRAM. Non-commercial license — use for R&D, swap out for [schnell] or [pro] API for production. |
| **SDXL** | 1.0 | LoRA training base, lower-VRAM fallback | Fully open-source, no revenue cap, most mature LoRA/ControlNet ecosystem. Runs from 8GB VRAM. ~3.2s on RTX 4090. Use as the training base for character LoRAs when Flux LoRA tooling is insufficient. |
| **FLUX.2 [klein]** | 9B (via BFL API or Platform tier) | Production fallback for commercial deployments | 9B model accessible via BFL's Platform license (up to 100K images/month). Middle ground between schnell speed and dev quality. |

**Default choice for this project:** FLUX.1 [schnell] for all pipeline image generation (Apache 2.0, commercial-safe, fast, character-consistent). FLUX.2 [dev] for hero keyframes and reference sheets (higher quality, research/R&D use). SDXL for LoRA training until Flux LoRA tooling matures fully.

**What NOT to use:**
- **SD 1.5** — Outdated. Only keep if you need specific legacy LoRAs.
- **SD 3.5** — Restrictive commercial license (revenue cap), slower adoption than Flux.
- **DALL-E 3 / Midjourney** — Cloud-only, no pipeline integration, per-image costs, no LoRA support.
- **Fooocus** — SDXL-only, no longer actively maintained in 2026.

### Video Generation

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **Wan 2.2** | 14B (Apache 2.0) | Primary video generation (image-to-video, text-to-video) | Best physics/motion quality of the three open models. Apache 2.0 license — cleanest commercial terms. Handles fluid dynamics, cloth simulation, object interactions best. 12GB min VRAM (block swap), 24GB comfortable. ~4.5 min per 5s clip on RTX 4090. |
| **LTX 2.3** | 22B (Apache 2.0) | Fast iteration, native audio, lower VRAM fallback | Fastest generation (~90s per 5s clip on 4090). Lowest VRAM requirement (8GB with GGUF, 16GB comfortable). ONLY model with native audio-video sync. Best for anime/stylized output — perfect for Cocomelon style. 25 fps native. |
| **HunyuanVideo 1.5** | 8.3B (Tencent Community License) | Cinematic shots | Best cinematic quality out of the box. **Avoid for commercial production** — license excludes EU, UK, South Korea, and requires separate license above 100M MAU. |

**Default choice for this project:** Wan 2.2 (14B) as the primary video model for its superior physics/motion and Apache 2.0 license. LTX 2.3 as the speed/lower-VRAM fallback and for stylized/Cocomelon output where its anime strength and native audio are advantages.

**Pipeline note:** Generate keyframes using the character-consistent image pipeline (Flux + PuLID + LoRA), then feed as I2V input into Wan 2.2 or LTX 2.3. This gives character consistency that video models alone cannot achieve.

**What NOT to use:**
- **Mochi 1** — Requires 24GB+ VRAM, slower than alternatives, less active development.
- **CogVideoX** — Smaller ecosystem, surpassed by Wan and LTX.
- **Runway Gen-3 / Pika / Kling** — Cloud API, per-second costs, no local pipeline integration.

### Character Consistency Stack

This is the most critical technology area for the project. No single method is sufficient — production-grade consistency requires stacked layers.

#### Recommended Stack (Flux-based)

| Layer | Technology | Purpose | Strength | Why |
|-------|------------|---------|----------|-----|
| **Layer 1: Identity anchor** | **PuLID** (v0.9+, ByteDance) | Face identity lock | Weight 0.8, start_at 0.0, end_at 0.8 | Purpose-built for Flux. Tightest identity lock available. Minimal style leakage — only locks face, not color palette. Stacks cleanly with ControlNet and style LoRAs. |
| **Layer 2: Character embedding** | **Face LoRA** (trained on 20-30 synthetic images) | Full character identity | Weight 0.6-0.8 | The nuclear option. Once trained, produces near-perfect consistency. Train on synthetic character sheet images generated from the same pipeline. |
| **Layer 3: Pose control** | **ControlNet OpenPose** | Body/pose consistency | ControlNet strength 0.5-0.7 | Locks body position across generations. Essential for consistent character placement across scenes. |
| **Layer 4: Style** | **Style LoRA** (optional) | Art style consistency | Weight 0.3-0.5 | Cocomelon-specific style LoRA (bright colors, rounded shapes, soft lighting). Optional but valuable for brand consistency. |
| **Layer 5: Face enhancement** | **FaceDetailer** (ComfyUI node) | Post-gen face refinement | Denoise 0.45 | Upscales and refines face region after generation. Catches remaining inconsistencies. |

**Production stack configuration:**
```
PuLID (0.8) + Face LoRA (0.6) + ControlNet OpenPose (0.5) = 95%+ character consistency
```

#### Training-free alternatives (for prototyping before committing to LoRA)

| Method | Best For | Quality | Setup Time |
|--------|----------|---------|------------|
| PuLID alone | Rapid prototyping, testing character concepts | 80% consistency | 5 min |
| IP-Adapter FaceID (Plus v2) | Fastest setup, no training | 70-85% consistency | 5 min |
| InstantID (SDXL) | SDXL-specific tight face lock | 85% consistency | 10 min |

**What NOT to use:**
- **Reactor / ROOP** — Post-hoc face swap, looks pasted-on, breaks at profile angles.
- **Textual inversion** — Too weak for production character work.
- **Seed control alone** — Gives mild consistency at best, unreliable across scenes.

### Music Generation

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **ACE-Step** | v1.5 (Apache 2.0) | Self-hosted music generation for pipeline integration | Open-source, Apache 2.0 license, runs locally on 8GB+ VRAM. Full control via LoRA, prompts, and sampling. Can integrate directly into the pipeline as a Python module. Vocal quality and instrument separation score higher than Suno in blind tests. ~45s per 30s track on RTX 3090. |
| **Suno** | v5 (API, $10-24/mo) | Quick music generation, lyrical nursery rhymes | Best overall quality for complete songs. $10/mo for 500 songs. Suno v5 leads on vocal realism and arrangement sophistication. **Must use API — no local integration.** |

**Default choice for this project:** ACE-Step v1.5 for all pipeline-integrated generation (self-hosted, zero per-track cost, full control, LoRA support for consistent nursery rhyme style). Suno v5 API as a fallback for one-off or experimental tracks where quality trumps pipeline integration.

**Pipeline note:** ACE-Step can be called from Python within the ComfyUI pipeline or as a standalone module. Generate music first, use the generated audio as the timing reference for video generation and lip-sync.

**What NOT to use:**
- **Udio** — Cloud-only, less pipeline-friendly than Suno, more expensive.
- **ElevenLabs Music** — Cloud-only, good quality but less control than ACE-Step.
- **AIVA** — Orchestral-focused, not suitable for nursery rhyme/pop music.
- **Stable Audio** — Instrumental only, no vocals.

### Voice Synthesis (TTS)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **Kokoro** | 82M (Apache 2.0) | Primary narrator/character voices | Tiny (82M params), fast, Apache 2.0 (commercial-safe). GPU-accelerated real-time audio. Multiple language support including English, French, Korean, Japanese, Mandarin. No voice cloning — use for fixed narrator voices. |
| **Chatterbox** | Latest (MIT) | Highest quality open-source TTS | MIT license (commercial-safe). Claims to beat ElevenLabs on quality benchmarks. Best for premium character voices where Kokoro's quality isn't sufficient. Requires more VRAM than Kokoro. |
| **Piper** | Latest (MIT) | Edge/CPU-only deployment | Runs on Raspberry Pi with zero GPU. Fast ONNX-based inference. MIT license. Use for ultra-low-latency or CPU-only scenarios, not primary production. |
| **XTTS v2** | 2.0 (Coqui Public Model License) | Voice cloning | Best voice cloning quality — clone from 6 seconds of audio. **Non-commercial license (CPML).** Use for R&D/prototyping only. For commercial voice cloning, use Kokoro (no cloning) or Chatterbox (MIT, limited cloning). |

**Default choice for this project:** Kokoro-82M for all primary character voices (Apache 2.0, commercial-safe, tiny footprint, fast). Chatterbox for premium voices when higher quality is needed (MIT, also commercial-safe). XTTS v2 for voice cloning experiments only (non-commercial license).

**Voice strategy for nursery rhymes:**
- Main narrator voice: Kokoro (fixed identity, consistent across episodes)
- Character voices: Kokoro with different voice parameters, or Chatterbox for more distinct character differentiation
- Singing voices: Bypass TTS — use ACE-Step/Suno music generation which produces sung vocals natively

**What NOT to use:**
- **ElevenLabs** — Cloud API, per-character cost, no local integration, expensive at scale.
- **F5-TTS** — CC-BY-NC-4.0 (non-commercial), cannot use in production.
- **Bark** — Slow (minutes per sentence), generative audio includes non-speech artifacts.
- **Coqui STT** — Discontinued in Jan 2024, use Whisper instead.

### Speech-to-Text / Subtitle Generation

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **faster-whisper** | large-v3 (MIT) | Primary transcription, subtitle generation | 4x faster than OpenAI Whisper, same accuracy. Int8 quantization drops VRAM to ~3GB for large-v3. Default recommendation for pipeline transcription. |
| **WhisperX** | Latest | Word-level timing for karaoke subtitles | Builds on faster-whisper with wav2vec2 forced alignment for ±50ms word-level timestamps (vs ±500ms vanilla Whisper). Essential for karaoke-style word highlighting in subtitles. |
| **Demucs** | v4 (MIT) | Vocal/instrumental separation for karaoke | Facebook AI's stem separation. Extract vocals from mixed audio for independent transcription of sung lyrics. Essential for nursery rhyme karaoke pipeline. |

**Subtitle pipeline:**
1. Demucs → separate vocals from instrumental
2. WhisperX → transcribe vocals with word-level timestamps
3. karaoke-subs (Python package) → convert to ASS/SRT with `\k` karaoke tags
4. FFmpeg → burn subtitles into video

**Output formats:** ASS (karaoke with word highlighting), SRT (standard), WebVTT (web)

### Lip-Sync

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **LatentSync** | 1.6 (Apache 2.0, ByteDance) | Primary lip-sync for final quality | Highest quality open-source lip-sync. Diffusion-based — produces sharper mouth regions, better teeth, smoother boundaries. 512x512 face resolution (vs 96x96 for Wav2Lip). Apache 2.0 license. LPIPS 0.089, SyncNet confidence 8.91. ~8GB VRAM. |
| **MuseTalk** | 1.5 (MIT, TMElyralab) | Real-time preview / fast iteration | Real-time at 30fps+ on V100. MIT license. Single-step latent inpainting — fast but capped at 256x256 face resolution. Good for quick previews and iteration before final LatentSync quality pass. |
| **SadTalker** | Latest (Apache 2.0) | Single-image talking head | Use only when animating from a single still image (e.g., thumbnail talking-head). 3DMM-based. Apache 2.0. Not needed for full video pipeline. |

**Default choice for this project:** LatentSync 1.6 for all final lip-sync output (Apache 2.0, best quality, 512x512 resolution). MuseTalk for previews and rapid iteration during development (MIT, real-time).

**What NOT to use:**
- **Wav2Lip** — Non-commercial license (trained on LRS2, cannot use commercially). 96x96 face resolution — visibly lower quality. Avoid entirely.
- **VideoReTalking / Diff2Lip** — Less mature, smaller communities, unverified commercial licenses.

### Video Editing / Compositing

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **DaVinci Resolve Studio** | 18.5+ (paid, $295 one-time) | Timeline assembly, compositing, color grading, audio mixing | Industry-standard NLE. Full Python/Lua scripting API for automation. Fusion tab for compositing. Fairlight audio tools. **Scripting API requires the paid Studio version** — the free version has no external scripting support. |
| **DaVinci Resolve MCP Server** | v2.60 (MIT) | AI-controlled editing via natural language | MCP server exposing full Resolve Scripting API as callable tools for LLM agents. Can create timelines, import media, set in/out points, render exports — all from natural language commands or programmatic calls. |
| **FFmpeg** | Latest (LGPL/GPL) | Format conversion, audio extraction, subtitle burning | Swiss army knife for media processing. Extract audio for Whisper transcription, burn ASS subtitles into video, concatenate clips, transcode formats. |

**Pipeline automation approach:**
1. Generate all assets programmatically (images, video clips, audio, subtitles)
2. Use DaVinci Resolve Python API to create project, import media, assemble timeline
3. Apply color grades, transitions, text overlays via scripting
4. Render final output via API

**OR** (lighter-weight alternative): Use FFmpeg for timeline assembly if compositing needs are simple (cut, overlay, subtitle burn). Only use DaVinci Resolve for complex multi-track editing.

### Upscaling / Frame Interpolation

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **Topaz Video AI** | Latest (subscription $299/yr) | Primary upscaling (AI-generated footage to 4K) | Professional standard. Aion model for 4K large-motion, Chronos for clean FPS conversion, Starlight Precise 2.5 for face detail enhancement on synthetic footage. Astra 2 Creative mode tuned for GenAI footage. |
| **RIFE / Practical-RIFE** | Latest (MIT/Apache) | Free frame interpolation | Open-source, ComfyUI-compatible. For smooth slow-motion and frame-rate conversion without Topaz cost. |
| **FlashVSR** | Latest (Apache 2.0) | Free video super-resolution | Open-source video upscaling distilled from Wan 2.1-T2V-1.3B. ComfyUI wrappers available. Good free alternative for upscaling synthetic footage. |

**Upscaling pipeline:**
1. Generate video at native resolution (720p-1080p depending on model)
2. Frame interpolation: RIFE (free) or Topaz Chronos (paid)
3. Upscaling: Topaz Starlight Precise 2.5 (paid, best for synthetic faces) or FlashVSR (free)
4. Output at 4K 60fps for YouTube delivery

**What NOT to use:**
- **ESRGAN (frame-by-frame)** — No temporal lock, produces flickering on video. Use only for single-image upscaling.
- **SUPIR** — Heavyweight, no temporal awareness, flickers on sequences.

### LLM / Text Generation

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| **Claude** (Anthropic API) | Claude 3.5+ / Claude 4 | Story generation, lyric writing, scene breakdown | Best creative writing quality. Handles nursery rhyme structure, educational content, scene descriptions. Use API for prompt chaining. |
| **Ollama + local models** | Latest | Offline fallback, cost reduction | Run open-source LLMs locally for simple tasks when API cost is a concern. Llama 3.1 8B or Qwen 2.5 7B for story/lyric generation. |

---

## Alternatives Considered

| Category | Recommended | Alternative 1 | Why Not Alt 1 | Alternative 2 | Why Not Alt 2 |
|----------|-------------|---------------|---------------|---------------|---------------|
| Image gen | FLUX.1 [schnell] | SDXL | Lower prompt adherence, text rendering quality | DALL-E 3 | Cloud-only, per-image cost, no LoRA, no pipeline integration |
| Video gen | Wan 2.2 + LTX 2.3 | HunyuanVideo 1.5 | License restricts EU/UK/South Korea use | Runway Gen-3 | $0.10-1.00/sec, cloud-only, no local pipeline |
| Character identity | PuLID + Face LoRA | IP-Adapter FaceID | Lower identity fidelity than PuLID+LoRA stack | InstantID | SDXL-only, doesn't work with Flux |
| Music gen | ACE-Step v1.5 (local) | Suno v5 (API) | Cloud API, no pipeline integration, per-track cost | Udio | More expensive, less quality than Suno |
| TTS | Kokoro + Chatterbox | ElevenLabs | Cloud API, per-character cost, expensive at scale | XTTS v2 | Non-commercial license (CPML) |
| Lip-sync | LatentSync 1.6 | Wav2Lip | Non-commercial license, 96x96 low quality | MuseTalk | 256x256 resolution cap, lower quality than LatentSync |
| Video editing | DaVinci Resolve Studio | Adobe Premiere | Subscription ($240/yr vs $295 one-time), less powerful scripting | FFmpeg alone | No multi-track timeline, no GUI for manual tweaks |
| Upscaling | Topaz Video AI | ESRGAN per-frame | No temporal lock, flickering on video | Gigapixel AI | Image-only, doesn't handle video |
| Frame interpolation | RIFE (free) / Topaz Chronos | DAIN | Slower, less accurate than RIFE | Flowframes | Windows-only, less actively maintained |

---

## Hardware Requirements

### Minimum (development / light production)

| Component | Specification |
|-----------|---------------|
| GPU | NVIDIA RTX 3060 12GB / RTX 4060 Ti 16GB |
| RAM | 32GB DDR5 |
| Storage | 2TB NVMe SSD (models are 30-80GB each) |
| OS | Ubuntu 22.04+ / Windows 11 |

### Recommended (production pipeline)

| Component | Specification |
|-----------|---------------|
| GPU | NVIDIA RTX 4090 24GB (or RTX 5090 32GB) |
| RAM | 64GB DDR5 |
| Storage | 4TB NVMe SSD (to hold all models + asset library) |
| OS | Ubuntu 22.04+ (for CUDA compatibility) |

### Production Farm (scaled)

| Component | Specification |
|-----------|---------------|
| GPU | 2-4× RTX 5090 32GB (parallel generation + video inference) |
| RAM | 128GB DDR5 |
| Storage | 8TB NVMe RAID (asset library + model storage + output) |

**VRAM requirements by pipeline stage:**

| Stage | VRAM Required | Model |
|-------|---------------|-------|
| Image gen (Flux schnell) | 8GB min, 12GB recommended | FLUX.1 [schnell] |
| Image gen (Flux dev) | 16GB min, 24GB recommended | FLUX.2 [dev] |
| Video gen (LTX 2.3) | 8GB (GGUF), 16GB comfortable | LTX 2.3 22B |
| Video gen (Wan 2.2) | 12GB (block swap), 24GB comfortable | Wan 2.2 14B |
| Music gen (ACE-Step) | 8GB+ | ACE-Step v1.5 |
| Lip-sync (LatentSync) | 8GB | LatentSync 1.6 |
| Upscaling (Topaz) | 12GB min, 16-24GB recommended | Starlight Precise 2.5 |
| LoRA training | 12GB (Flux), 6-8GB (SDXL) | ComfyUI-FluxTrainer |

---

## Pipeline Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI Nursery Rhyme Studio Pipeline                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────────┐   │
│  │ Claude   │───▶│ Scene    │───▶│ Story-   │───▶│ Lyrics +         │   │
│  │ (LLM)    │    │ Planner  │    │ board    │    │ Timing Sheet     │   │
│  └──────────┘    └──────────┘    └──────────┘    └────────┬─────────┘   │
│                                                            │             │
│         ┌──────────────────────────────────────────────────┼──────────┐  │
│         │                    PARALLEL LANES                │          │  │
│         ▼                          ▼                       ▼          │  │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────────┐  │
│  │ MUSIC LANE   │    │ VISUAL LANE      │    │ VOICE LANE           │  │
│  │              │    │                  │    │                      │  │
│  │ ACE-Step     │    │ Flux + PuLID     │    │ Kokoro / Chatterbox  │  │
│  │ → music.wav  │    │ + LoRA           │    │ → voice.wav          │  │
│  │              │    │ → keyframes      │    │                      │  │
│  │              │    │                  │    │                      │  │
│  │              │    │ Wan 2.2 / LTX    │    │                      │  │
│  │              │    │ → video clips    │    │                      │  │
│  └──────┬───────┘    └────────┬─────────┘    └──────────┬───────────┘  │
│         │                    │                          │              │
│         ▼                    ▼                          ▼              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    ASSEMBLY LANE                                 │  │
│  │                                                                  │  │
│  │  1. LatentSync lip-sync (sync character faces to vocals)         │  │
│  │  2. WhisperX transcription → karaoke-subs → .ASS subtitles       │  │
│  │  3. DaVinci Resolve API / FFmpeg timeline assembly               │  │
│  │  4. Topaz Video AI upscaling (720p/1080p → 4K)                  │  │
│  │  5. RIFE / Topaz Chronos frame interpolation (24fps → 60fps)     │  │
│  │  6. Final render with subtitle burn-in                           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  OUTPUT: 4K 60fps MP4 with karaoke subtitles, ready for YouTube/TikTok  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Installation

### Core Pipeline Dependencies

```bash
# ComfyUI (primary workflow engine)
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt

# Custom nodes for the pipeline
cd custom_nodes
git clone https://github.com/ltdrdata/ComfyUI-Manager.git  # Node management
git clone https://github.com/Gourieff/comfyui-reactor-node.git  # Face detailer
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git  # IP-Adapter nodes
git clone https://github.com/lightricks/ComfyUI-LTXVideo.git  # LTX video
git clone https://github.com/Kijai/ComfyUI-WanVideoWrapper.git  # Wan 2.2 wrapper
git clone https://github.com/balazik/ComfyUI-PuLID-Flux.git  # PuLID for Flux

# Python pipeline dependencies
pip install faster-whisper whisperx demucs karaoke-subs
pip install ace-step  # ACE-Step music generation
```

### Voice / TTS

```bash
# Kokoro TTS
pip install kokoro

# Chatterbox TTS
pip install chatterbox-tts

# Piper TTS (optional, for edge deployment)
pip install piper-tts
```

### Video Editing

```bash
# DaVinci Resolve Studio (purchase from Blackmagic Design)
# Add Python path to Resolve scripting:
echo 'export PYTHONPATH="/opt/resolve/Developer/Scripting/Modules:$PYTHONPATH"' >> ~/.bashrc

# DaVinci Resolve MCP Server (for AI-controlled editing)
git clone https://github.com/samuelgursky/davinci-resolve-mcp.git
cd davinci-resolve-mcp
pip install -r requirements.txt

# FFmpeg
sudo apt-get install ffmpeg
```

### Upscaling

```bash
# Topaz Video AI — purchase/download from topazlabs.com
# RIFE frame interpolation (open-source alternative)
pip install rife-ncnn-vulkan
```

---

## Sources

- ["Local AI Image Generation in 2026: Flux, SD & ComfyUI"](https://www.digitalapplied.com/blog/local-image-generation-flux-stable-diffusion-comfyui-2026) — Digital Applied, Jun 2026 (HIGH confidence — cross-referenced with other sources)
- ["Flux vs Stable Diffusion: Technical Comparison (2026)"](https://pxz.ai/blog/flux-vs-stable-diffusion:-technical-&-real-world-comparison-2026) — pxz.ai, Jan 2026 (HIGH confidence)
- ["Best Local AI Video Model 2026: LTX vs WAN vs Hunyuan"](https://www.earngenix.com/workflows/best-local-ai-video-model-2026) — Earngenix, Jul 2026 (HIGH confidence — comprehensive comparison)
- ["Consistent AI Characters in 2026: Every Method That Actually Works"](https://aiofm.info/en/guides/consistent-ai-character) — aiofm, Apr 2026 (HIGH confidence — detailed production-tested guide)
- ["ACE-Step vs Suno: Which AI Music Generator Wins?"](https://fm9.ai/ace-step/vs-suno) — FM9, Feb 2026 (MEDIUM confidence — vendor-neutral but single source)
- ["Kokoro vs Chatterbox vs XTTS: Best Local TTS in 2026"](https://aivideosensei.com/compare/kokoro-vs-chatterbox-vs-xtts) — AI Video Sensei, Jul 2026 (HIGH confidence — production-tested)
- ["AI Lip-Sync Model Selection Guide 2026"](https://tomodahinata.com/en/blog/ai-lip-sync-talking-head-model-selection-guide-2026) — tomodahinata, Jun 2026 (HIGH confidence — detailed commercial license analysis)
- ["DaVinci Resolve MCP Server"](https://github.com/samuelgursky/davinci-resolve-mcp) — GitHub (HIGH confidence — 1.8k stars, active, MIT license)
- ["AI Upscaler Benchmark: Video Upscalers"](https://github.com/ismael-joffroy-chandoutis/ai-upscaler-benchmark/blob/main/docs/video-upscalers.md) — GitHub, Jun 2026 (HIGH confidence — detailed benchmark with measured RTX 5090 data)
- ["ComfyUI 2026: The Definitive Workflow Guide"](https://www.creativeainews.com/articles/comfyui-2026-definitive-workflow-guide/) — Creative AI News, May 2026 (HIGH confidence — production workflow tested)
- ["Generate Subtitles Locally with Whisper"](https://localaimaster.com/blog/local-ai-subtitles-whisper) — Local AI Master, Jun 2026 (HIGH confidence — verified against other sources)
- ["Best Local TTS Models 2026: 8 Open-Source Voices Tested"](https://localaimaster.com/blog/best-local-tts-models) — Local AI Master, Jun 2026 (HIGH confidence)
- ["Open Source AI Video Generation: Wan 2.2 vs HunyuanVideo 1.5 vs LTXVideo"](https://www.aimagicx.com/blog/open-source-ai-video-models-comparison-2026) — AI Magicx, Mar 2026 (HIGH confidence)
