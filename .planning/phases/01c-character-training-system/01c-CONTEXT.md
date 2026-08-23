# Phase 1c: Character Training System - Context

**Gathered:** 2026-08-22
**Status:** Ready for planning

<domain>
## Phase Boundary

LoRA training infrastructure and the first production training run for Lily Bunny: dataset builder pipeline extracting curated character assets, production LoRA v1.0, software-convention versioning (v0.1 → v1.0 → v2.0), and quality benchmark against the identity scorer baseline. The `src/training_engine/` package (Kohya adapter, DatasetBuilder, VersionRegistry, LoRABenchmark) already exists from Phase 1 — this phase verifies/completes it end-to-end offline, wires dataset curation to the asset repository, and prepares the actual GPU training run as a Colab notebook operator action (no GPU in the build environment).

</domain>

<decisions>
## Implementation Decisions

### Production Training Reality
- Build `colab/AnimationStudio_Colab_Training.ipynb` mirroring the existing Phase 4 notebook pattern; the real training run is an operator action on a T4/A100 Colab runtime
- Success criterion "production LoRA v1.0 trained" is satisfied by notebook + proven dry-run path locally, then recorded as `verification_deferred_human` at verify time (no blocking on GPU availability)

### Dataset Source & Curation
- Training images come from the asset repository filtered to lifecycle state `approved`/`production` for the target character
- Captions follow the existing `DatasetConfig` trigger-word convention (trigger word + descriptor sidecar `.txt` per image)
- Keep existing `DatasetConfig` min/max bounds (20–40 images per ROADMAP)

### Versions & Benchmark
- No placeholder registry versions — `VersionRegistry` entries are created only by completed real or dry-run trainings
- Benchmark pass threshold reuses identity-engine Brand Score default weights with ≥ 90% consistency requirement per ROADMAP

### the agent's Discretion
- Module layout, CLI surface shape, and test structure follow existing codebase conventions

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/training_engine/base.py` — `TrainingConfig`, `TrainingResult`, `TrainingBackend` ABC
- `src/training_engine/kohya_adapter.py` — Kohya SS adapter (`KohyaAdapter`)
- `src/training_engine/dataset_builder.py` — `DatasetBuilder`, `DatasetEntry`, `DatasetConfig`, `BuildResult`
- `src/training_engine/versioning.py` — `LoRAVersion`, `VersionRecord`, `VersionRegistry`
- `src/training_engine/benchmark.py` — `LoRABenchmark`, `ScorerProvider` protocol, `MockScorerProvider`
- `colab/AnimationStudio_Colab_Phase4.ipynb` — notebook skeleton to mirror

### Established Patterns
- Provider-agnostic adapter ABCs; mock-first testing (51 passing tests across training engine suites)
- Offline-first: no network/GPU in tests; notebooks carry real-compute steps

### Integration Points
- Asset repository lifecycle states feed dataset curation
- Identity scoring engine provides benchmark baseline via `ScorerProvider`

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>
