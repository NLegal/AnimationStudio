# Requirements: AI Nursery Rhyme Studio

**Defined:** 2026-07-28
**Core Value:** Character consistency and asset reusability across every episode. Build once, reuse forever.

## v1 Requirements

### Pipeline Infrastructure

- [ ] **INFR-01**: Staged DAG pipeline architecture with typed contracts between each stage
- [ ] **INFR-02**: Per-stage checkpoint and resume capability (retry from failed stage, not from start)
- [ ] **INFR-03**: Asset Store with 4-property versioning (identity, non-destructive iteration, current version, rollback)
- [ ] **INFR-04**: Model routing layer with circuit breaker and failover between compatible models
- [ ] **INFR-05**: Configurable stage interfaces to enable model swapping without pipeline rewrites

### Character System

- [x] **CHAR-01**: Persistent Character Database — structured identity records for every character
- [x] **CHAR-02**: Character reference sheet generation (front, 3/4, profile, back angles)
- [x] **CHAR-03**: Expression library for each character (happy, sad, surprised, singing, sleepy, etc.)
- [x] **CHAR-04**: Pose library for each character (standing, running, jumping, sitting, dancing, etc.)
- [ ] **CHAR-05**: Outfit/wardrobe variants per character (default, winter, rain, pajamas, holiday, etc.)
- [x] **CHAR-06**: Character personality profiles, relationships, catchphrases, and emotion matrix
- [ ] **CHAR-07**: LoRA training pipeline for character consistency (ComfyUI-FluxTrainer or SDXL-based)
- [x] **CHAR-08**: Reusable prompt templates and negative prompt standards per character
- [ ] **CHAR-09**: Age progression variants for characters (toddler, preschool, kindergarten)

### World & Asset Library

- [ ] **ASST-01**: Persistent library of reusable backgrounds/locations (bedroom, kitchen, playground, farm, beach, school, forest, etc.)
- [ ] **ASST-02**: Multiple lighting variants per location (morning, afternoon, golden hour, night, rainy, etc.)
- [ ] **ASST-03**: Reusable props library (toys, food, furniture, nature items, balloons, cake, etc.)
- [ ] **ASST-04**: Asset versioning, tagging, and search across the library

### Story & Lyrics

- [ ] **STORY-01**: LLM-powered story generation from theme/idea input
- [ ] **STORY-02**: Automatic lyric generation with verse/chorus structure
- [ ] **STORY-03**: Scene breakdown and timing from lyrics (scene count, duration per scene)
- [ ] **STORY-04**: Storyboard generation from scene descriptions

### Music Generation

- [ ] **MUSC-01**: AI music generation from lyrics (ACE-Step integration for pipeline-native generation)
- [ ] **MUSC-02**: Suno API integration for cloud-quality fallback
- [ ] **MUSC-03**: Beat-timed scene planning from generated song duration
- [ ] **MUSC-04**: Nursery rhyme genre optimization (catchy melodies, children's vocals)

### Voice & TTS

- [ ] **VOIC-01**: Recurring character voices via Kokoro TTS engine
- [ ] **VOIC-02**: Multi-voice support (narrator, main characters, supporting characters)
- [ ] **VOIC-03**: Warm/expressive children's content voice profiles

### Image Generation

- [ ] **IMG-01**: Character-consistent image generation pipeline (Flux + PuLID + Face LoRA + ControlNet)
- [ ] **IMG-02**: Prompt engineering system using character templates and scene context
- [ ] **IMG-03**: Keyframe generation for every storyboard scene
- [ ] **IMG-04**: Batch image generation with per-scene quality review

### Video Animation

- [ ] **ANIM-01**: Image-to-video generation pipeline (Wan 2.2 for quality, LTX 2.3 for speed)
- [ ] **ANIM-02**: 5-10 second clip generation per storyboard panel
- [ ] **ANIM-03**: Upscaling pipeline for final output quality (Topaz or Real-ESRGAN)
- [ ] **ANIM-04**: Frame interpolation for smooth motion (RIFE)

### Lip-Sync

- [ ] **LIPS-01**: Singing-optimized lip-sync engine (LatentSync for production quality)
- [ ] **LIPS-02**: Word-level mouth shape synchronization to sung vocals
- [ ] **LIPS-03**: Phoneme-based mouth position generation for animation-style faces
- [ ] **LIPS-04**: MuseTalk integration as fallback for dialogue sections

### Subtitles & Karaoke

- [ ] **SUBS-01**: Auto-generated subtitles from lyrics/transcript (WhisperX-based)
- [ ] **SUBS-02**: Karaoke-style word highlighting synchronized to music (ASS format with karaoke fill tags)
- [ ] **SUBS-03**: Child-friendly typography (large fonts, high contrast, Cocomelon-style)

### Video Assembly & Editing

- [ ] **EDIT-01**: Automated timeline assembly from generated clips (DaVinci Resolve via MCP server)
- [ ] **EDIT-02**: Music track alignment with video cuts
- [ ] **EDIT-03**: Transition and effect application
- [ ] **EDIT-04**: Multi-aspect-ratio export (16:9 for YouTube, 9:16 for Shorts/TikTok, 1:1 for Instagram)

### Thumbnails

- [ ] **THMB-01**: Automated thumbnail generation from video content
- [ ] **THMB-02**: Multiple thumbnail variants with CTR scoring
- [ ] **THMB-03**: Child-safe thumbnail style (bright colors, character-consistent)

### Multi-Language Pipeline

- [ ] **MLNG-01**: Per-language version generation reusing source video (swap audio + subtitle tracks only)
- [ ] **MLNG-02**: Localized TTS and karaoke subtitles per target language
- [ ] **MLNG-03**: Multi-language publishing with platform-native language support

### Batch Production & Operations

- [ ] **BAT-01**: CSV/spreadsheet-driven batch production mode
- [ ] **BAT-02**: Per-episode quality check gates with automated scoring
- [ ] **BAT-03**: Cost tracking and budget management per batch run
- [ ] **BAT-04**: Asset version audit (which character/asset versions used in each episode)
- [ ] **BAT-05**: Resume support for interrupted batch runs

### Publishing

- [ ] **PUB-01**: Automated metadata generation (title, description, tags, chapters)
- [ ] **PUB-02**: YouTube publishing integration (video + shorts)
- [ ] **PUB-03**: TikTok and Instagram publishing integration
- [ ] **PUB-04**: Platform-optimized formatting per channel

## v2 Requirements

### Advanced Production

- **ANIM-05**: Longer video context models for reduced clip segmentation
- **LIPS-05**: Real-time lip-sync preview during storyboard review
- **EDIT-05**: Multi-track audio editing (background music auto-ducking under vocals)
- **EDIT-06**: Dynamic scene transitions based on mood/pace analysis

### Distribution

- **PUB-05**: Facebook and Pinterest publishing
- **PUB-06**: Schedule-based publishing queue
- **PUB-07**: Analytics dashboard (per-language retention, thumbnail CTR, subtitle toggle rates)

### Quality

- **QC-01**: Automated quality scoring per pipeline stage (character consistency, composition, audio sync)
- **QC-02**: Cold-view human review workflow with Slack/notification integration
- **QC-03**: A/B thumbnail testing

### Community

- **SOCIAL-01**: Episode versioning and changelog tracking
- **SOCIAL-02**: Character evolution history (visual diffs across episodes)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real-time / live streaming | Pre-recorded batch pipeline only — live streaming adds unreleated complexity |
| User-generated content platform | Professional studio for operators, not a social platform |
| Generic video generation | Every video uses the same character universe — no one-off unrelated content |
| Frame-by-frame manual NLE editing | Timeline-less assembly with direction-in-plain-language; DaVinci for finishing only |
| Custom model training UI for operators | Pre-train and ship character LoRAs as part of character creation |
| Social features (comments, sharing) | Focus on production and publish — distribution happens on external platforms |
| Non-children's content | Studio is exclusively educational/children's nursery rhymes |
| Watermark/brand overlay | Clean output — monetize through subscription/credits |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFR-01 | Deferred | — |
| INFR-02 | Deferred | — |
| INFR-03 | Deferred | — |
| INFR-04 | Deferred | — |
| INFR-05 | Deferred | — |
| CHAR-01 | Phase 1 | Complete |
| CHAR-02 | Phase 1b | Complete |
| CHAR-03 | Phase 1b | Complete |
| CHAR-04 | Phase 1b | Complete |
| CHAR-05 | Phase 1b | Pending |
| CHAR-06 | Phase 1 | Complete |
| CHAR-07 | Phase 1c | Pending |
| CHAR-08 | Phase 1 | Complete |
| CHAR-09 | Phase 1 | Planning |
| ASST-01 | Phase 2 | Pending |
| ASST-02 | Phase 2 | Pending |
| ASST-03 | Phase 2 | Pending |
| ASST-04 | Phase 2 | Pending |
| STORY-01 | Phase 3 | Pending |
| STORY-02 | Phase 3 | Pending |
| STORY-03 | Phase 3 | Pending |
| STORY-04 | Phase 3 | Pending |
| MUSC-01 | Phase 3 | Pending |
| MUSC-02 | Phase 3 | Pending |
| MUSC-03 | Phase 3 | Pending |
| MUSC-04 | Phase 3 | Pending |
| VOIC-01 | Phase 5 | Pending |
| VOIC-02 | Phase 5 | Pending |
| VOIC-03 | Phase 5 | Pending |
| IMG-01 | Phase 4 | Pending |
| IMG-02 | Phase 4 | Pending |
| IMG-03 | Phase 4 | Pending |
| IMG-04 | Phase 4 | Pending |
| ANIM-01 | Phase 4 | Pending |
| ANIM-02 | Phase 4 | Pending |
| ANIM-03 | Phase 4 | Pending |
| ANIM-04 | Phase 4 | Pending |
| LIPS-01 | Phase 5 | Pending |
| LIPS-02 | Phase 5 | Pending |
| LIPS-03 | Phase 5 | Pending |
| LIPS-04 | Phase 5 | Pending |
| SUBS-01 | Phase 5 | Pending |
| SUBS-02 | Phase 5 | Pending |
| SUBS-03 | Phase 5 | Pending |
| EDIT-01 | Phase 5 | Pending |
| EDIT-02 | Phase 5 | Pending |
| EDIT-03 | Phase 5 | Pending |
| EDIT-04 | Phase 5 | Pending |
| THMB-01 | Phase 5 | Pending |
| THMB-02 | Phase 5 | Pending |
| THMB-03 | Phase 5 | Pending |
| MLNG-01 | Phase 6 | Pending |
| MLNG-02 | Phase 6 | Pending |
| MLNG-03 | Phase 6 | Pending |
| BAT-01 | Phase 6 | Pending |
| BAT-02 | Phase 6 | Pending |
| BAT-03 | Phase 6 | Pending |
| BAT-04 | Phase 6 | Pending |
| BAT-05 | Phase 6 | Pending |
| PUB-01 | Phase 6 | Pending |
| PUB-02 | Phase 6 | Pending |
| PUB-03 | Phase 6 | Pending |
| PUB-04 | Phase 6 | Pending |

**Coverage:**

- v1 requirements: 63 total
- Mapped to phases: 63
- Complete: 3 (CHAR-01, CHAR-06, CHAR-08)
- Unmapped: 0 ✓

---
*Requirements defined: 2026-07-28*
*Last updated: 2026-07-28 after initial definition*
