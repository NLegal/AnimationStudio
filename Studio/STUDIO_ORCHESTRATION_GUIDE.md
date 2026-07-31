# Studio Orchestration Guide — AI Nursery Studio

## Overview
The Studio is the autonomous production platform. It coordinates every stage of episode production — from story to publishing — with humans setting creative vision, characters, brand, and educational goals while the platform manages planning, generation, rendering, editing, publishing, monitoring, and optimization.

## Production Pipeline
1. **Workflow Planning** — Episode workflow with sequential stages: story → storyboard → images → animation → edit → QC → publish
2. **Task Scheduling** — Dependencies, priorities, and worker-type assignment for every stage
3. **Job Queue** — FIFO + priority queue with retry and failure handling
4. **Worker Pool** — CPU, GPU, audio, video, and publishing workers claim tasks
5. **Resource Management** — GPU units, CPU cores, and RAM allocation with utilization tracking
6. **GPU Render Farm** — Batch rendering queue across nodes
7. **Quality Gates** — Resolution, duration, and custom checks gate every stage before promotion
8. **Event Bus** — Story approved, rendering finished, publishing ready events notify the distribution department
9. **Monitoring** — Alerts, metrics collection, and production tracking
10. **Learning Loop** — Successes and failures feed the optimization engine
11. **Analytics** — AI performance, costs, and throughput reporting

## Agent Roster
Creative Director, Curriculum Planner, Story Writer, Storyboard, Prompt Engineer, Image Generation, Animation, Audio, Editor, QA, SEO, Publishing, Analytics, Trend Research, Localization, Infrastructure.

## Key Directories
- `Pipelines/` — Active episode pipelines
- `Tasks/` — Queued and completed tasks
- `Workflows/` — Workflow definitions
- `Agents/` — Agent configuration
- `Events/` — Event history
- `Models/` — Registered AI models
- `Prompts/` — Prompt templates and revisions
- `Assets/` — Registered production assets
- `Reports/` — Quality reports
- `Alerts/` — Monitoring alerts
- `Resources/` — Resource allocations
- `RenderFarm/` — Render job batches
- `Schedules/` — Scheduled production events
- `Learning/` — Learning-loop records
- `Analytics/` — Performance reports

## Usage
```python
from src.studio import PipelineOrchestrator

studio = PipelineOrchestrator()
studio.setup_defaults()
studio.create_pipeline("episode-001")
studio.process_pipeline("episode-001")
```

## Status
- All 14 modules implemented
- Ready for ComfyUI / GPU backend integration
