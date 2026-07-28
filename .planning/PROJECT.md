# AI Nursery Rhyme Studio

## What This Is

An AI-powered animation production pipeline that generates unlimited, high-quality Cocomelon-style nursery rhyme videos with consistent characters, reusable assets, and minimal manual work. The product is a scalable platform — a permanent animation studio with persistent character database, world assets, and automated production workflows — not a tool for making individual videos.

## Core Value

Character consistency and asset reusability across every episode. Build once, reuse forever.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Persistent character design system with reference sheets, expression libraries, pose libraries, and rotation sheets
- [ ] Reusable world/background locations with multiple lighting conditions
- [ ] Reusable props and asset library (toys, food, nature, etc.)
- [ ] AI music generation pipeline (Suno/ACE-Step)
- [ ] Recurring character voice system (Kokoro/XTTS/Piper)
- [ ] Automated story and lyric generation with scene breakdown
- [ ] Storyboard generation from lyrics/scene descriptions
- [ ] Image generation pipeline (Flux/SDXL) with character-consistent prompting
- [ ] Image-to-video animation pipeline (Wan 2.2/Hunyuan/LTX)
- [ ] Lip-sync animation for singing characters
- [ ] Automated video editing and timeline assembly (DaVinci Resolve)
- [ ] Karaoke subtitle generation with word highlighting
- [ ] Automated thumbnail generation with CTR optimization
- [ ] Multi-platform publishing (YouTube, TikTok, Instagram, Facebook)
- [ ] Multi-language localization support
- [ ] Batch production and asset versioning
- [ ] Quality-control checkpoints throughout the pipeline

### Out of Scope

- Real-time/live streaming — pre-recorded content only
- Non-children's content — studio is exclusively educational/children's nursery rhymes
- User-generated content platform — this is a production studio, not a social platform
- Generic video generation — every video uses the same character universe

## Context

This is a greenfield project building toward a long-term vision of an AI-powered animation studio comparable to Pixar or Cocomelon's production infrastructure. The key insight is that value compounds over time — every new character, background, prop, and workflow becomes reusable across future content.

Core philosophy: think of it as a studio with permanent characters, not as creating individual videos. The project builds modular stages so individual AI models can be replaced without rebuilding the entire pipeline.

## Constraints

- **Consistency**: Characters must look identical across all episodes using LoRA, reference sheets, IPAdapter, and related techniques
- **Modularity**: Each pipeline stage must be independently replaceable as AI models improve
- **AI-first**: Entirely AI-powered; minimal manual intervention
- **Animation style**: Cocomelon-inspired (colorful, rounded shapes, oversized eyes, soft lighting, Pixar-quality rendering)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Build a studio, not individual videos | Reusable assets compound over time | — Pending |
| LoRA for character consistency | Most reliable method for persistent characters | — Pending |
| Modular pipeline stages | Allows replacing individual AI models without rebuilding | — Pending |
| Cocomelon-inspired visual style | Proven formula for children's content engagement | — Pending |

---
*Last updated: 2026-07-28 after initialization*
