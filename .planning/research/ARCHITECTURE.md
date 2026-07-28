# Architecture Patterns

**Domain:** AI-powered children's animation production pipeline
**Researched:** 2026-07-28
**Overall confidence:** HIGH

## Recommended Architecture

AnimationStudio uses a **staged DAG pipeline with an agentic orchestration layer** — every stage is independently replaceable, communicates through typed contracts, and is governed by a central orchestrator that manages the directed acyclic graph of production steps.

This is the architecture that production AI-video teams have converged on in 2025–2026. The monolithic "single model does everything" approach was abandoned because it cannot support: (1) swapping individual AI models as they improve, (2) parallelizing independent stages, (3) graceful degradation when a single model fails, or (4) quality-checking intermediate assets before spending compute on downstream stages.

```
                         ┌─────────────────────────────────────┐
                         │        Orchestrator & Gateway        │
                         │  (FastAPI + Java Spring Gateway)     │
                         │  Job queue, DAG scheduler, retry,    │
                         │  circuit breaker, observability      │
                         └──┬──────┬──────┬──────┬──────┬───────┘
                            │      │      │      │      │
              ┌─────────────┘      │      │      │      └─────────────┐
              │                     │      │      │                    │
     ┌────────▼────────┐  ┌────────▼──────▼──▼──────▼────────┐  ┌────▼──────────┐
     │   Asset Store    │  │      Modular Pipeline DAG        │  │  Publish       │
     │  (PostgreSQL +   │  │                                  │  │  Layer         │
     │   MinIO/S3)      │  │  L1: Story → L2: Lyrics →       │  │  (YouTube,     │
     │                  │  │  L3: Music → L4: Storyboard →   │  │  TikTok, etc.) │
     │  • Characters    │  │  L5: Images → L6: Video →       │  │                │
     │  • Backgrounds   │  │  L7: Lip-sync → L8: Edit →      │  └────────────────┘
     │  • Props         │  │  L9: Subtitles → L10: QC        │
     │  • Templates     │  │                                  │
     │  • Versions      │  └──────────────────────────────────┘
     └─────────────────┘
```

### Layer Architecture (GMI Cloud 4-Layer Model Adapted)

Building on the industry-standard four-layer architecture for generative media pipelines (GMI Cloud, 2026; IJIRMPS, 2026), AnimationStudio maps these layers as follows:

| Layer | AnimationStudio Component | Responsibility |
|-------|--------------------------|----------------|
| 1. **Model Access** | Unified API Gateway + Model Registry | Normalize all AI model calls behind a single endpoint; handle auth, billing, rate-limiting |
| 2. **Compute** | GPU-optimized stage runners | Match GPU tier to stage (H100 for images, H200 for video, L40 for audio) |
| 3. **Orchestration** | DAG Scheduler + Agentic Director | Sequence/parallelize stages, manage dependencies, version workflows |
| 4. **Scaling** | Serverless + Dedicated hybrid | Auto-scale to zero for bursty stages; dedicated for continuous batch processing |

---

## Component Boundaries

| Component | Responsibility | Communicates With | Can Be Replaced By |
|-----------|---------------|-------------------|-------------------|
| **Orchestrator** | Schedules DAG execution, manages job queue, handles retry/failure, emits observability events | Every stage via typed contracts | Different orchestration framework (Temporal, Prefect, Airflow) |
| **API Gateway** | Auth, rate limiting, model routing, circuit breaker, multi-model failover | Orchestrator, external AI APIs, clients | Different gateway (Kong, Envoy, custom) |
| **Story Generator** | Accepts nursery rhyme concept → produces structured story with scene breakdown | Orchestrator ↔ Asset Store (character refs) | Swap LLM (GPT-4o → Claude → Llama) |
| **Lyrics Generator** | Produces singable lyrics matching story beats and rhyme scheme | Orchestrator ↔ Story Generator output | Swap LLM or music-aware model |
| **Music Generator** | Generates instrumental + vocal track from lyrics | Orchestrator ↔ Lyrics output | Swap music model (Suno → ACE-Step → Meta) |
| **Storyboard Generator** | Produces shot list, camera angles, keyframe descriptions | Orchestrator ↔ Asset Store (character/background refs) | Replace with manual storyboard tool |
| **Image Generator** | Generates character-consistent frames per storyboard panel | Orchestrator ↔ Asset Store (LoRAs, reference sheets) | Swap image model (Flux → SDXL → DALL-E) |
| **Video Generator** | Image-to-video per clip (2–10s segments) | Orchestrator ↔ Image Generator output | Swap video model (Wan → Hunyuan → Kling → Veo) |
| **Lip-Sync Animator** | Aligns mouth shapes to sung audio per character | Orchestrator ↔ Video + Audio outputs | Swap lip-sync (Wav2Lip → SyncNet → custom) |
| **Video Editor** | Assembles clips, adds transitions, applies color grade | Orchestrator ↔ All upstream stage outputs | Replace with DaVinci Resolve API → FFmpeg |
| **Subtitle Generator** | Word-highlighted karaoke captions | Orchestrator ↔ Audio (timing) + Lyrics | Swap caption model (Whisper → custom aligner) |
| **Quality Controller** | Runs automated QC checks on outputs before publishing | Orchestrator ↔ All stage outputs | Add/remove checks independently |
| **Publisher** | Format optimization + platform upload | Orchestrator ↔ QC-passed final video | Add/remove target platforms |
| **Asset Store** | Versioned database of characters, backgrounds, props, reference sheets, LoRAs | Every stage that needs reference consistency | Replace storage backend (S3 → MinIO → GCS) |

---

## Data Flow

### Primary Production Flow (End-to-End)

```
Input: "Twinkle Twinkle Little Star" + style parameters
  │
  ▼
┌──────────────────────────────────────────────────────────────────┐
│ STAGE L1: STORY GENERATION                                       │
│ LLM: Accepts concept → produces structured story with scene      │
│       breakdown, character mapping, educational goals            │
│ Output: StoryDocument { scenes[], characters[], moral/theme }    │
│ QC: Schema validation, scene coherence check                     │
├──────────────────────────────────────────────────────────────────┤
│ STAGE L2: LYRICS GENERATION                                      │
│ LLM: Produces singable lyrics from story scenes, matching meter  │
│       and rhyme scheme for children's content                    │
│ Output: LyricsDocument { verses[], chorus[], bridge[] }          │
│ QC: Syllable count check, rhyme validation, age-appropriate check│
├──────────────────────────────────────────────────────────────────┤
│ STAGE L3: MUSIC GENERATION                                       │
│ Music Model: Generates instrumental + vocal from lyrics          │
│ Output: AudioTrack { vocals, instrumental, bpm, key }            │
│ QC: Audio quality check, loudness normalization (EBU R128)       │
├──────────────────────────────────────────────────────────────────┤
│ STAGE L4: STORYBOARD GENERATION                                  │
│ LLM + Template: Produces shot list with camera directions         │
│ Output: StoryboardDocument { shots[], camera[], continuity[] }   │
│ QC: Shot count vs story coverage check                           │
├──────────────────────────────────────────────────────────────────┤
│ STAGE L5: IMAGE GENERATION                                       │
│ Diffusion Model: Generates character-consistent frames using     │
│   LoRA + IP-Adapter + reference sheets from Asset Store          │
│ Output: ImageSet { keyframes[], backgrounds[], prop-shots[] }    │
│ QC: CLIP score (prompt adherence), LPIPS (temporal consistency), │
│     face-similarity check against character reference            │
├──────────────────────────────────────────────────────────────────┤
│ STAGE L6: VIDEO GENERATION                                       │
│ Video Model: Image-to-video per shot clip (2-10s segments)       │
│ Output: VideoClips { clip[], metadata, seed, duration }          │
│ QC: Temporal coherence, flicker detection, character persistence │
├──────────────────────────────────────────────────────────────────┤
│ STAGE L7: LIP-SYNC ANIMATION                                     │
│ Lip-sync Model: Aligns mouth shapes to sung audio per character  │
│ Output: LipSyncedClips { video[], audio[], alignment[] }         │
│ QC: AV sync drift check (< 1 frame threshold)                    │
├──────────────────────────────────────────────────────────────────┤
│ STAGE L8: VIDEO EDITING & ASSEMBLY                               │
│ Editor: Assembles clips, adds transitions, color grading,        │
│         thumbnail generation                                     │
│ Output: EditedVideo { timeline, transitions, thumbnails }        │
│ QC: Full playback check, transition smoothness                   │
├──────────────────────────────────────────────────────────────────┤
│ STAGE L9: SUBTITLE GENERATION                                    │
│ Aligner: Word-level karaoke captions synced to audio             │
│ Output: SubtitleTrack { segments[], highlights[] }               │
│ QC: Timing accuracy, word alignment verification                 │
├──────────────────────────────────────────────────────────────────┤
│ STAGE L10: FINAL QUALITY CONTROL                                 │
│ Multi-check pass: CLIP consistency, AV sync, audio loudness,     │
│   subtitle accuracy, thumbnail CTR prediction                    │
│ Output: QCReport { pass/fail per check, overall score }          │
├──────────────────────────────────────────────────────────────────┤
│ STAGE L11: PUBLISHING                                            │
│ Publisher: Transcode for target platforms, upload, metadata      │
│ Output: PublishedVideo { platform_urls[], analytics_tags[] }     │
└──────────────────────────────────────────────────────────────────┘
```

### Parallel Execution Opportunities

Based on the dependency graph, several stages can run in parallel:

```
Phase 1 (Sequential):  Story → Lyrics → Music
                            ↘
Phase 2 (Parallel):        ├── Storyboard ──┐
                           ├── Image Gen    │ (can start once story is ready,
                           │                │  doesn't need full lyrics)
                           └── Audio Prep   ──┘
                            ↗
Phase 3 (Sequential):  Video Gen (needs images)
                            ↘
Phase 4 (Parallel):        ├── Lip-sync (needs video + audio)
                           ├── Subtitle Gen (needs audio + lyrics)
                            ↘
Phase 5 (Sequential):  Video Editing (needs lip-sync + subtitles)
                            ↘
Phase 6 (Final):       QC → Publish
```

**Key insight:** Image generation and storyboard generation can be partially parallelized. Storyboard needs only the scene breakdown (not full lyrics), and image generation can begin for scene 1 while scene 2's storyboard is still being refined.

---

## Patterns to Follow

### Pattern 1: Staged DAG with Typed Contracts

**What:** Each pipeline stage defines its input/output schema using Pydantic models (Python) or equivalent typed interfaces. Stages communicate only through these contracts, never through shared state or side effects.

**When:** Always — this is the foundational pattern.

**Why:** Typed contracts make stages independently replaceable. If a better video model emerges, you swap it without touching any other stage. The contract between "image generator → video generator" stays the same even when the model changes.

**Example:**
```python
# Typed contract between Story → Lyrics
class StoryDocument(BaseModel):
    scenes: list[Scene]
    characters: list[CharacterRef]
    moral_theme: str
    target_age_range: tuple[int, int]

class LyricsDocument(BaseModel):
    verses: list[Verse]
    chorus: Chorus
    bridge: Bridge | None
    syllable_count_per_line: int
    rhyme_scheme: str

# The adapter that converts between stages
class StoryToLyricsAdapter:
    """Maps Story scenes into lyrics generation context.
    Can be swapped without changing StageL1 or StageL2."""
    def build_prompt(self, story: StoryDocument) -> str: ...
    def parse_response(self, raw: str) -> LyricsDocument: ...
```

### Pattern 2: Agentic Orchestration with a "Director" Agent

**What:** An orchestration agent (the "Director") manages the end-to-end pipeline — decomposing the brief into scenes, maintaining visual consistency across shots, detecting failures, retrying intelligently, and assembling the final cut. This is the pattern used by AutoMV (2025), ReelMind's Nolan, and the myAiVideos pipeline (2026).

**When:** The Director is responsible for the creative flow. It doesn't run models itself — it decides which models to call, in what order, and what to do if an output is poor.

**Example:**
```python
class DirectorAgent:
    """Manages the pipeline DAG for one production job."""
    
    async def produce(self, brief: ProductionBrief) -> FinalVideo:
        story = await self.stage_l1(brief)
        lyrics = await self.stage_l2(story)
        music = await self.stage_l3(lyrics)
        
        # Parallel: storyboard + images can be interleaved
        storyboard = await self.stage_l4(story)
        images = await self.stage_l5(story, self.asset_store)
        
        videos = []
        for shot in storyboard.shots:
            video = await self.stage_l6(images[shot.id], shot)
            videos.append(video)
        
        lip_sync = await self.stage_l7(videos, music)
        subtitles = await self.stage_l9(music, lyrics)
        edited = await self.stage_l8(lip_sync, subtitles)
        
        qc_report = await self.stage_l10(edited)
        if qc_report.overall_score < self.threshold:
            return await self.remediate(edited, qc_report)
        
        return await self.stage_l11(edited)
```

### Pattern 3: Prompt Anchoring for Character Consistency

**What:** Extract "visual anchors" from the first shot of a scene (character appearance, clothing, lighting, background) and inject them into every subsequent shot's prompt. This prevents character drift across shots without requiring per-shot manual prompt engineering.

**When:** Every stage that generates visual content (images, video frames).

**Why:** AI models treat each generation as a fresh invention unless anchored. Prompt anchoring is the lightweight alternative to fine-tuning per-character LoRAs for every scene.

**Example:**
```python
class PromptAnchor:
    """Extracts and propagates visual anchors across shots."""
    
    def extract_anchors(self, first_shot: ShotPrompt) -> Anchors:
        return Anchors(
            character_appearance=first_shot.character_desc,
            lighting=first_shot.lighting,
            color_palette=first_shot.color_scheme,
            outfit=first_shot.outfit,
        )
    
    def inject_anchors(self, shot_prompt: ShotPrompt, 
                       anchors: Anchors) -> ShotPrompt:
        """Append anchor constraints to every shot prompt."""
        shot_prompt.constraints.append(
            f"Character must match: {anchors.character_appearance}"
        )
        shot_prompt.constraints.append(
            f"Lighting: {anchors.lighting}. "
            f"Palette: {anchors.color_palette}"
        )
        return shot_prompt
```

### Pattern 4: Model Access Gateway with Failover

**What:** A unified API gateway that normalizes all AI model calls behind a single endpoint, with multi-model failover (primary → fallback → fallback), circuit breaker protection, and centralized billing.

**When:** Always — every model call goes through the gateway.

**Why:** Without this, swapping models requires refactoring every stage. The gateway makes model swap a config change, not a code change. (GMI Cloud MaaS model, 2026; myAiVideos Java Gateway pattern, 2026.)

**Example configuration:**
```yaml
# Model routing config — change model without code changes
models:
  image_generation:
    primary:
      provider: flux-pro
      endpoint: https://api.example.com/flux
      timeout: 30s
    fallback:
      provider: sdxl-turbo
      endpoint: https://api.example.com/sdxl
      timeout: 45s
    circuit_breaker:
      failure_threshold: 5
      recovery_timeout: 60s
  
  video_generation:
    primary:
      provider: wan-2.2
      endpoint: https://api.example.com/wan
    fallback:
      provider: hunyuan
    second_fallback:
      provider: kling-3.0
```

### Pattern 5: Layered Quality Control Gates

**What:** QC checks at three levels — (1) per-stage validation before passing output to next stage, (2) cross-stage consistency checks, (3) final full-pipeline QC before publishing.

**When:** Every stage output is validated before it becomes the next stage's input.

**Why:** A bad storyboard wastes image generation GPU time. A bad image wastes video generation GPU time and costs 10-100x more. Early validation saves compute.

**QC Gate Matrix:**

| Gate | Location | Metrics | Action on Failure |
|------|----------|---------|-------------------|
| **Schema** | Every stage output | Structural validation (Pydantic/JSON Schema) | Retry stage with error context |
| **CLIP Score** | Image output | Text-image alignment (> 0.30 threshold) | Regenerate with refined prompt |
| **Face Sim** | Image output | Face similarity to character ref (> 0.85) | Regenerate with stronger reference |
| **Temporal** | Video output | Frame-to-frame LPIPS (low = good) | Regenerate with shorter clip |
| **AV Sync** | Lip-sync output | Audio/visual offset (< 100ms) | Auto-rescue (atempo/pad) or retry |
| **Loudness** | Audio output | EBU R128 (-23 LUFS ± 1) | Normalize or re-render |
| **Drift** | Cross-shot | Character appearance deltas | Flag for manual review |
| **Comprehensive** | Pre-publish | All checks + overall score | Route to human review if borderline |

### Pattern 6: Asset Store with 4-Property Versioning

**What:** Every asset (character, background, prop) is stored exactly once with a canonical ID, and every meaningful take becomes a numbered version under that ID. Four properties must hold: (1) one identity per asset, (2) cheap non-destructive iteration, (3) unambiguous current version, (4) rollback as first-class operation.

**When:** Asset Store access for every stage that uses reference materials.

**Why:** Without versioning, asset drift accumulates silently across episodes. With versioning, you can branch, roll back, and always know which version is canonical. (Cinemagiq 2026 production model.)

**Example schema:**
```sql
-- Asset identity table
CREATE TABLE assets (
    id UUID PRIMARY KEY,
    asset_type VARCHAR(20) NOT NULL, -- 'character', 'background', 'prop', 'lora'
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    current_version_id UUID REFERENCES asset_versions(id)
);

-- Versioned instances
CREATE TABLE asset_versions (
    id UUID PRIMARY KEY,
    asset_id UUID NOT NULL REFERENCES assets(id),
    version_number INT NOT NULL,
    storage_path TEXT NOT NULL,        -- MinIO/S3 key
    thumbnail_path TEXT,
    metadata JSONB,                    -- LoRA weights path, prompt used, seed
    parent_version_id UUID REFERENCES asset_versions(id),
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL,
    checksum TEXT,                     -- Content hash for dedup
    UNIQUE(asset_id, version_number)
);

-- Which shots used which version of each asset
CREATE TABLE shot_asset_usage (
    shot_id UUID NOT NULL REFERENCES shots(id),
    asset_version_id UUID NOT NULL REFERENCES asset_versions(id),
    usage_role VARCHAR(20) NOT NULL, -- 'character_ref', 'background', 'prop'
    PRIMARY KEY (shot_id, asset_version_id)
);
```

### Pattern 7: Multi-Stage Recovery with Tiered Strategy

**What:** A four-tier error recovery strategy: (1) immediate retry for transient failures, (2) circuit breaker for repeated failures, (3) fallback model for provider outages, (4) human-in-the-loop escalation for unrecoverable failures.

**When:** Every stage that calls external AI models.

**Why:** Pipeline reliability is the #1 operational concern for production AI media systems. Without tiered recovery, a single model timeout can take down the entire multi-hour production run. (myAiVideos 2026; Preporato 2026; Portkey 2026.)

**Example:**
```python
class StageExecutor:
    """Executes a pipeline stage with multi-tier error recovery."""
    
    async def execute_with_recovery(self, stage: Stage, 
                                     input_data: dict) -> StageOutput:
        last_error = None
        for attempt in range(3):  # Tier 1: Retry
            try:
                return await stage.execute(input_data)
            except TransientError as e:
                last_error = e
                await asyncio.sleep(2 ** attempt + random.uniform(0, 1))
                continue
            except PermanentError as e:
                break  # Don't retry — escalate
        
        # Tier 2: Circuit breaker
        if self.circuit_breaker.is_open(stage.name):
            # Tier 3: Fallback model
            return await self.fallback_execute(stage, input_data)
        
        # Tier 4: Human-in-the-loop escalation
        if stage.requires_human_approval:
            return await self.escalate_to_human(stage, input_data, last_error)
        
        raise PipelineError(f"Stage {stage.name} failed after recovery attempts")
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Monolithic Pipeline

**What:** A single Python script that calls model A, then B, then C sequentially, with all logic in one file.

**Why bad:** Cannot parallelize independent stages. Cannot swap models without rewriting. One failure kills the entire run. No observability between stages.

**Instead:** Use a staged DAG with typed contracts. Each stage is independently deployable.

### Anti-Pattern 2: Prompt Sprawl

**What:** Every stage writes its own prompts from scratch with no shared template system or anchor propagation. Character descriptions are duplicated across 20 prompts and drift apart.

**Why bad:** Inconsistent character appearance across shots. Impossible to maintain style guides. Changes require editing every prompt individually.

**Instead:** Use a centralized Prompt Template Registry with anchor injection. Character descriptions are stored once in the Asset Store and injected into every prompt via the Director.

### Anti-Pattern 3: No QC Until the End

**What:** Generate everything, then check quality at the very end before publishing.

**Why bad:** A bad image costs 1x. A bad video costs 10-100x. Running QC only at the end means spending the most compute on bad inputs. The 2026 industry data shows 60-70% cost reduction from production pipelines that implement per-stage QC gates (IJIRMPS 2026).

**Instead:** QC every stage output before it feeds into the next stage.

### Anti-Pattern 4: Flat Asset Storage

**What:** Store all generated frames as `final_v3_new(2).png` in a single directory. No version tracking, no asset hierarchy, no cross-linking to shots.

**Why bad:** Asset drift accumulates silently. You can't tell which version of a character was used in which shot. Rollback is impossible. Context is lost when anyone else touches the project.

**Instead:** Use the 4-property versioning model (Pattern 6). Every asset has one identity, versioned instances, a canonical current version, and full rollback.

### Anti-Pattern 5: Infinite Regeneration

**What:** "Generate 50 variants and pick the best one" as the primary quality strategy.

**Why bad:** Creates decision fatigue. Wastes GPU budget. Inconsistent quality — the "best of 50" changes style between shots. Cost scales linearly with attempts but quality plateaus.

**Instead:** Use the Shot Factory Loop: anchor references, generate 2-6 targeted variants, evaluate with QC metrics, fix surgically, move on.

---

## Scalability Considerations

| Concern | At 1 video/day (MVP) | At 10 videos/day (Growth) | At 100+ videos/day (Scale) |
|---------|----------------------|--------------------------|---------------------------|
| **Orchestration** | Single FastAPI process | FastAPI + ARQ Redis queue | Temporal.io / Prefect for distributed DAG execution |
| **GPU Compute** | Local GPU / single cloud endpoint | Multi-GPU with stage-specific tiers | Bare metal clusters with auto-scaling per stage |
| **Asset Storage** | Local filesystem + SQLite | PostgreSQL + MinIO (S3) | PostgreSQL cluster + CDN-backed S3 + caching layer |
| **Queue Management** | In-process task queue | ARQ/Redis — async worker pool | Celery/PySpark — distributed workers per stage |
| **Observability** | Console logging | Structured logs + Langfuse tracing | Full OpenTelemetry + custom metrics dashboard |
| **Model Failover** | Manual swap | Gateway-level failover (2 models) | Multi-provider load balancing with canary testing |
| **QC Pipeline** | Per-stage validation scripts | Automated QC gates with thresholds | ML-powered QC that learns from human approvals |
| **Versioning** | Manual S3 bucket folders | Asset Store with version tracking | Full provenance graph with CI/CD for model weights |
| **Error Recovery** | Retry on failure | Circuit breaker + fallback chain | Predictive failure detection + auto-remediation |

---

## Prompt Generation and Template System

### Architecture

The prompt system has three layers:

```
┌─────────────────────────────────────────┐
│          Template Registry               │
│  config/style_templates/*.yaml          │
│  config/characters.yaml                  │
│  config/environments.yaml               │
│  config/skills/*.yaml                   │
├─────────────────────────────────────────┤
│          Prompt Director                 │
│  Reads templates + anchors from Asset    │
│  Store. Composes per-shot prompts with   │
│  consistent character references.        │
│  Injects visual anchors from first shot. │
├─────────────────────────────────────────┤
│          Stage Adapters                  │
│  Each stage (image, video, lip-sync)    │
│  has an adapter that converts the        │
│  composed prompt to the target model's   │
│  expected format (API-specific).         │
└─────────────────────────────────────────┘
```

### Template Structure

Each template captures the invariant parts of generation:

```yaml
# config/style_templates/cocomelon-style.yaml
style:
  art_style: "Cocomelon-inspired 3D animation"
  rendering: "Pixar-quality, soft global illumination"
  colors: "Bright, saturated primaries with pastel backgrounds"
  characters:
    eyes: "Oversized, expressive with catchlights"
    shapes: "Rounded, soft edges, no sharp angles"
    proportions: "Large head-to-body ratio (1:3)"
  backgrounds: "Simple, clean, toy-like environments"
  
prompt_skeleton:
  subject: "{character} in {outfit}"
  action: "{action_verb} {action_object}"
  camera: "{shot_type}, {camera_movement}"
  environment: "{location}, {lighting}, {color_scheme}"
  quality_tags: "cocomelon style, 3d render, soft lighting, pixar quality, 4k, trending on artstation"
  negative_prompt: "flat colors, 2d, anime, realistic, photorealistic, deformed, blurry, low quality"
```

### Anchor Propagation Flow

1. **Shot 1 prompt** → full description (character + outfit + lighting + background)
2. **Prompt Director** extracts Anchors from Shot 1 output
3. **Shots 2-N prompts** → only scene-specific variables change; anchors are injected
4. **Anchors include:** `character_appearance`, `lighting`, `color_palette`, `outfit`
5. **Scene change** → anchors reset to new scene's Shot 1

---

## Quality Control Checkpoints

### Pipeline Integration

QC gates sit between every pair of connected stages. They are independently deployable microservices called by the Orchestrator:

```
Stage Output → [QC Gate] → Pass → Next Stage Input
                            Fail → Retry / Fallback / Escalate
```

### Automated QC Metrics

| Metric | What It Measures | Tool/Model | Threshold | Cost |
|--------|------------------|------------|-----------|------|
| **CLIP Score** | Text-image alignment (prompt adherence) | CLIP ViT-L/14 | > 0.30 | Low (one forward pass) |
| **LPIPS** | Perceptual variation between frames | Learned Perceptual Image Patch Similarity | < 0.15 inter-frame | Low |
| **Face Similarity** | Character consistency vs reference | ArcFace / FaceNet | > 0.85 cosine sim | Medium |
| **AV Sync Offset** | Audio-visual alignment | SyncNet / custom | < 100ms drift | Medium |
| **Loudness** | Audio compliance | EBU R128 analyzer | -23 LUFS ± 1 LU | Low |
| **Motion Smoothness** | Temporal coherence | Flow-based metrics | Threshold per model | Medium |
| **VQA Score** | Compositional accuracy (multi-object prompts) | VQA models | > 0.40 | Higher (5-10x CLIP) |
| **Text Detection** | Unwanted burned-in text | OCR / GLM-4V | Zero false text | Medium |

### QC Escalation Hierarchy

```
PASS (all gates green)        → Continue pipeline
SOFT_FAIL (1-2 borderline)    → Auto-remediation (regenerate with adjusted params)
HARD_FAIL (any gate red)      → Circuit opens for this stage → escalate
CRITICAL (provenance check)   → Stop entire pipeline, human review required
```

---

## Versioning and Asset Provenance

### Provenance Chain

Every final video should be traceable back to every input that produced it:

```
Final Video (v7)
  ├── Story: "Twinkle Twinkle" (v3)
  │     └── LLM call: GPT-4o, prompt template v2, seed 12345
  ├── Lyrics: "Twinkle_lyrics_v2"
  │     └── LLM call: Claude 3.5, prompt template v1
  ├── Music: "twinkle_track_v4"
  │     └── Model: Suno v3, seed 67890
  ├── Images:
  │     ├── Character: "Maya" (v12, LoRA weights hash: abc123)
  │     ├── Background: "bedroom_night" (v3)
  │     └── Per-shot generations (seed recorded per frame)
  ├── Video clips: 15 clips, each with seed + model version
  ├── Lip-sync: Wav2Lip model v2.3
  └── Edit: DaVinci Resolve project file (v5)
```

### Provenance Database Schema

```sql
CREATE TABLE provenance_records (
    id UUID PRIMARY KEY,
    job_id UUID NOT NULL REFERENCES production_jobs(id),
    stage_name VARCHAR(50) NOT NULL,
    input_artifacts JSONB NOT NULL,   -- [{type, version_id, checksum}]
    output_artifact JSONB NOT NULL,   -- {version_id, storage_path, checksum}
    model_info JSONB NOT NULL,        -- {model_name, version, parameters}
    prompt_text TEXT,
    seed INT,
    latency_ms INT,
    cost_credits DECIMAL(10,4),
    created_at TIMESTAMPTZ NOT NULL
);

-- Fast lookup: "what version of character Maya was used in final video X?"
CREATE INDEX idx_provenance_artifacts 
    ON provenance_records USING GIN (input_artifacts);
```

---

## Batch Processing Architecture

### Job Structure

```yaml
BatchJob:
  type: "batch" | "single"
  episodes:
    - episode_id: "ep-001"
      concept: "Twinkle Twinkle Little Star"
      style: "cocomelon"
      target_duration: 180  # seconds
    - episode_id: "ep-002"
      concept: "The Wheels on the Bus"
      style: "cocomelon"
      target_duration: 180
  parallel: true           # Process episodes in parallel
  max_concurrent: 3        # GPU budget constraint
  output_format: "mp4"
  publish_targets: ["youtube", "tiktok"]
```

### Batch Processing Flow

```
Batch Request
  │
  ▼
Splitter — divides into individual episode jobs
  │
  ▼
Scheduler — assigns episodes to worker pool (max N concurrent)
  │
  ├── Worker 1: Ep-001 (full 11-stage pipeline)
  ├── Worker 2: Ep-002 (full 11-stage pipeline)
  └── Worker 3: Ep-003 (if concurrency allows)
  │
  ▼
Collector — gathers completed episodes
  │
  ▼
Publisher — batch uploads to all platforms
```

### Key Optimizations for Batch

1. **Model weights loaded once, shared across episodes** — LoRA weights for the same character aren't reloaded between episodes in the same batch
2. **GPU stage pooling** — Image generation H100s are shared across parallel episodes, video generation H200s are queued
3. **Asset deduplication** — If multiple episodes use the same background, it's generated once and referenced
4. **Progressive publishing** — Completed episodes are published immediately, not batched at the end

---

## Retry / Failure Handling

### Error Taxonomy

| Error Class | Examples | Retryable? | Strategy |
|-------------|----------|------------|----------|
| **Transient** | Network timeout, 429 rate limit, 503 temporary | Yes (3 attempts) | Exponential backoff + jitter |
| **Model** | NSFW filter triggered, hallucinated content, poor quality | Conditional | Regenerate with adjusted prompt |
| **Provider** | API key expired, quota exhausted, model deprecated | No (without config change) | Circuit breaker → fallback model |
| **Semantic** | Wrong character, incorrect scene, story doesn't make sense | Conditional | LLM-as-judge → regenerate with critique |
| **Permanent** | Invalid input schema, missing asset reference | No | Fail fast → human escalation |

### Recovery Strategy Matrix

```
                    ┌──────────────┐
                    │  Stage Fails │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        Is Transient?  Is Semantic?  Is Permanent?
              │            │            │
              ▼            │            ▼
      Retry (3x exp       │        Human Escalation
      backoff + jitter)   │        (alert + context)
              │            │
         Still fails?      │
              │            │
              ▼            │
        Circuit Breaker    │
        (5 failures →      │
         OPEN for 60s)     │
              │            │
              ▼            ▼
        Fallback Model ───►┐
        (primary → alt)    │
              │            │
              ▼            ▼
        Stage Succeeds  Human Escalation
        (circuit HALF_OPEN) (context from all attempts)
```

### Circuit Breaker States

```
CLOSED (normal operation)
  → Failure threshold exceeded (5 consecutive failures)
  → OPEN

OPEN (blocking requests)
  → Recovery timeout elapsed (60s)
  → HALF_OPEN

HALF_OPEN (testing recovery)
  → Test request succeeds
  → CLOSED (reset counter)

HALF_OPEN (testing recovery)
  → Test request fails
  → OPEN (reset timer)
```

### Human-in-the-Loop Escalation

When automated recovery is exhausted, the pipeline surfaces a structured escalation:

```json
{
  "escalation_id": "esc-abc123",
  "job_id": "job-456",
  "stage": "L5_image_generation",
  "failure_type": "SEMANTIC",
  "attempts": [
    {"attempt": 1, "error": "CLIP score 0.22 (below 0.30 threshold)", "seed": 1001},
    {"attempt": 2, "error": "CLIP score 0.18", "seed": 1002, "prompt_adjustment": "added negative prompt"},
    {"attempt": 3, "error": "Face similarity 0.62 (below 0.85)", "seed": 1003, "reference_strength_increased": true}
  ],
  "input_context": {"story_scene": "...", "character_ref": "Maya_v12"},
  "recommended_action": "Review character reference sheet or adjust prompt constraints"
}
```

---

## Suggested Build Order

Dependencies between components dictate phase ordering:

| Build Order | Component | Depends On | Why This Order |
|-------------|-----------|------------|----------------|
| **1** | **Pipeline Shell + Asset Store** | Nothing | Foundation — all stages need storage and orchestration |
| **2** | **API Gateway + Model Registry** | Pipeline Shell | Every stage needs model access through the gateway |
| **3** | **Orchestrator (DAG Scheduler)** | Pipeline Shell | The conductor — coordinates everything else |
| **4** | **Prompt Template System** | Asset Store | All generative stages need templates |
| **5** | **Story + Lyrics (L1-L2)** | Orchestrator, Templates | First content stages; produce text that other stages need |
| **6** | **Image Generation (L5)** | Asset Store, Templates, Orchestrator | Needs character/background assets from store |
| **7** | **Video Generation (L6)** | Image Generation | Needs images to animate; most expensive stage |
| **8** | **Storyboard (L4)** | Story, Asset Store | Can be built after story; helps guide image generation |
| **9** | **Music Generation (L3)** | Lyrics | Independent of visuals; can be parallelized |
| **10** | **Lip-Sync (L7)** | Video + Audio | Needs both video and audio outputs |
| **11** | **Video Editing (L8)** | Video, Lip-sync, Subtitles | Assembles all outputs |
| **12** | **Subtitle Generation (L9)** | Lyrics + Audio timing | Can be built earlier but needs timing data |
| **13** | **Quality Control Gates (L10)** | All stages | Each gate tests a specific stage output |
| **14** | **Publisher (L11)** | Final Video | Last phase — format optimization + upload |

### Dependency Graph

```
Asset Store ──────┬─────────────────────────────────────────┐
                  │                                         │
Pipeline Shell ───┼── Orchestrator ─── Prompt System ───────┤
                  │                                         │
Gateway ──────────┘                                         │
                                                            ▼
L1: Story ──────────► L2: Lyrics ───┬──► L3: Music ────────┤
                                     │                      │
                  ┌──────────────────┘                      │
                  ▼                                         ▼
L4: Storyboard ───► L5: Images ─────► L6: Video ───────────┤
                                                            │
                  L9: Subtitles ────┐                       │
                                    ├──► L7: Lip-sync ─────┤
                  L3: Music ────────┘                       ▼
                                                     L8: Edit ──► L10: QC ──► L11: Publish
```

---

## Sources

- **GMI Cloud (2026).** "How to build a scalable generative media AI pipeline on a cloud platform." — 4-layer architecture, GPU tier matching, orchestration patterns. [MEDIUM confidence — commercial source]
- **myccarl/ai-shortVideo-pipeline (2026).** GitHub — 7-layer pipeline architecture, Java Gateway with circuit breaker, CLIP consistency gating, AV sync rescue. [HIGH confidence — production code, 566 stars]
- **IJIRMPS (2026).** "Generative AI in Media Production: From Content Creation to Metadata Intelligence." — Layered GenAI production architecture, 76% adoption rate, 60-70% cost reduction. [HIGH confidence — peer-reviewed]
- **Prahlad Menon (2026).** "The AI Video Production Stack in 2026: Why the Model Is No Longer the Answer." — 3-layer stack (storyboard → model → orchestration), $0.50/sec cost analysis. [MEDIUM confidence — industry blog]
- **Cinemagiq (2026).** "Managing AI Assets at Scale: Versioning, Characters & Continuity." — 4-property asset versioning model. [MEDIUM confidence — vendor blog, but well-reasoned]
- **Neolemon (2025).** "AI Storyboard To Animation Pipeline: Complete Workflow." — Shot factory loop, 3 animation lanes, character consistency workflow. [MEDIUM confidence — vendor content]
- **Preporato (2026).** "Error Handling in AI Agents: Circuit Breakers, Retry & Recovery." — 7-layer resilience pattern, error taxonomy for AI pipelines. [HIGH confidence — NVIDIA certification curriculum]
- **Portkey (2026).** "Retries, fallbacks, and circuit breakers in LLM apps." — Retry strategies, circuit breaker states, multi-provider failover. [MEDIUM confidence — vendor]
- **AutoMV (2025).** "Multi-Agent Orchestration for Music-to-Video Generation." — Director Agent pattern, Character Bank management. [HIGH confidence — academic paper, arXiv]
- **TwelveLabs (2026).** "Build an AI Video QC Pipeline." — Brief-match verification, temporal coherence checks, 5-check QC pipeline. [MEDIUM confidence — vendor tutorial]
- **ImageBench (2026).** "Automated Metrics — Generative Image Benchmark." — CLIP Score, LPIPS, VQA Score, ImageReward metrics reference. [HIGH confidence — benchmark authority]
