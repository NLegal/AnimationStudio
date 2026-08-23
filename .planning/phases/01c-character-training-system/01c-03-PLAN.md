---
phase: 01c-character-training-system
plan: 03
type: execute
wave: 1
depends_on: []
files_modified:
  - src/training_engine/base.py
  - src/training_engine/kohya_adapter.py
  - tests/test_training_engine.py
autonomous: true
requirements:
  - CHAR-07
user_setup: []
must_haves:
  truths:
    - TrainingConfig.dry_run=True completes a training invocation WITHOUT any subprocess spawn, writing a inspectable command artifact and registering the version exactly like the real path (G17; locked decision allows dry-run registrations)
    - _build_command emits a Flux-complete accelerate launch command — networks.lora_flux network module, clip_l/t5xxl/ae model paths, safetensors output, fp8/cache flags, Colab-safe dataloader workers (G16)
    - Subprocess invocation remains arg-list-only (never shell=True) with resolved paths — existing security invariant preserved
    - Real (non-dry-run) training is impossible to trigger accidentally from local code paths — dry-run is the default-safe mode for offline proof
  artifacts:
    - src/training_engine/base.py (TrainingConfig gains dry_run + Flux model-path/memory fields)
    - src/training_engine/kohya_adapter.py (dry-run branch in train(); Flux-complete _build_command)
    - tests/test_training_engine.py (dry-run sentinel tests; extended TestKohyaCommandGeneration)
  key_links:
    - dry-run branch sits between cmd = self._build_command(config) and subprocess.run, reusing the existing registration block verbatim so registry entries from dry-runs are indistinguishable in shape from real ones
    - Command artifact filename {character_id}_{version}.train_cmd.json lands inside config.output_path for operator inspection before any GPU run
    - Typed TrainingResult(success=False, metrics={"error": ...}) error shape preserved across the ABC boundary — never raises
---

<objective>
Complete KohyaAdapter for the real Flux training run (CHAR-07 criterion 2, deferred-human path): make dry-run a first-class engine mode that proves the entire orchestration path offline, and finish _build_command with every Flux-specific requirement the Colab run depends on.

Purpose: The current command would fail on Colab (bare python instead of accelerate launch, wrong network module, missing ae/clip_l/t5xxl files), and there is no way to prove the train path locally without spawning a subprocess. This plan makes the locked "notebook + proven dry-run path" evidence chain possible.
Output: dry_run mode on TrainingConfig/KohyaAdapter; Flux-complete command builder; extended offline tests.
</objective>

<execution_context>
@/root/.config/opencode/gsd-core/workflows/execute-plan.md
@/root/.config/opencode/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/phases/01c-character-training-system/01c-CONTEXT.md
@.planning/phases/01c-character-training-system/01c-RESEARCH.md
@.planning/phases/01c-character-training-system/01c-PATTERNS.md

@src/training_engine/base.py
@src/training_engine/kohya_adapter.py
@tests/test_training_engine.py

Phase constraints (echoed in every action):
- C-OFFLINE: all tests pass without GPU/network — subprocess is only ever mocked/sentineled in tests.
- C-CATALOGDB: this plan never touches catalog.db.
- C-NODEP: stdlib-only. No new packages.
- Report byte-compatibility constraints do NOT apply to this phase (Phase 7/8 scope).
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: First-class dry_run mode on TrainingConfig and KohyaAdapter.train() (G17)</name>
  <files>src/training_engine/base.py, src/training_engine/kohya_adapter.py, tests/test_training_engine.py</files>
  <read_first>
    @src/training_engine/base.py (TrainingConfig dataclass L20-44 — plain-default field style to follow)
    @src/training_engine/kohya_adapter.py (train() control flow L131-218 — insertion point after cmd = self._build_command(config) at ~L150; registration block L169-188 reused verbatim; typed-error precedent L200-218; validate_environment L56-79 advisory-warning comment admitting dry-run is future work)
    @.planning/phases/01c-character-training-system/01c-RESEARCH.md (G17 row; Pattern 2 "Dry-run as a first-class mode")
    @tests/test_training_engine.py (sentinel/monkeypatch conventions; env-not-ready assertions L246-256)
  </read_first>
  <behavior>
    - TrainingConfig(dry_run=True) train(): subprocess.run is never invoked (sentinel monkeypatch fails the test if called); output_path is created; {character_id}_{version}.train_cmd.json exists containing the exact argv list as JSON; returned TrainingResult has success=True with metrics marking the dry-run; version registered exactly once.
    - TrainingConfig(dry_run=False) with environment not ready: unchanged behavior — typed failure result, no exception.
    - Dry-run with unwritable output_path: typed failure result (error in metrics), never a raised exception across the ABC boundary.
  </behavior>
  <action>
    Add `dry_run: bool = False` to `TrainingConfig` following the existing field style.

    In `KohyaAdapter.train()`, immediately after the command is built, branch on config.dry_run: create config.output_path (parents ok), write a JSON artifact named f"{config.character_id}_{config.version}.train_cmd.json" containing the argv list (json.dumps indent=2, ensure_ascii=False, encoding utf-8 per repo idiom), SKIP the subprocess call entirely, then fall through to the existing success-path validation and version-registration block UNCHANGED so dry-run registrations are structurally identical to real ones (locked decision: registry entries come only from completed real or dry-run trainings). Mark the returned TrainingResult metrics with a dry_run indicator so callers can distinguish evidence types. Any filesystem failure inside the dry-run branch returns the typed failure result rather than raising.

    Validate identifiers before they are interpolated into artifact filenames or command arguments: character_id and version must match a conservative pattern (lowercase alphanumerics, hyphen, underscore, dot for versions) — reject with the typed failure result otherwise. This keeps argv injection impossible even though exec stays arg-list-only.

    Do NOT change validate_environment semantics beyond leaving it advisory — config-level dry_run supersedes it (research G17 note). Keep the existing CalledProcessError/FileNotFoundError typed-error handling for the real path untouched.

    Tests extend tests/test_training_engine.py: monkeypatch subprocess.run with a sentinel that records invocation (and would fail the test if called) under dry_run; assert artifact existence/content, registry entry creation, success result shape; plus identifier-validation rejection cases. All offline (C-OFFLINE).
  </action>
  <verify>
    <automated>python3 -m pytest tests/test_training_engine.py -k dry -q</automated>
    <automated>python3 -m pytest tests/test_training_engine.py -q</automated>
  </verify>
  <done>
    Dry-run trainings complete offline with zero subprocess spawns, produce an inspectable .train_cmd.json artifact, register their version through the normal path, and return distinguishable success results — all proven by sentinel-based tests.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Flux-complete _build_command (G16)</name>
  <files>src/training_engine/base.py, src/training_engine/kohya_adapter.py, tests/test_training_engine.py</files>
  <read_first>
    @src/training_engine/kohya_adapter.py (_build_command L258-302 — current arg-list construction; misleading resolution comment ~L296; module docstring L6-7 shell=True prohibition; caption_dropout_rate dead config field)
    @src/training_engine/base.py (TrainingConfig fields — where Flux model-path and memory-profile fields will be added)
    @.planning/phases/01c-character-training-system/01c-RESEARCH.md (G16 row; Code Examples "Flux-complete training command skeleton"; Pattern 3 T4-vs-A100 VRAM profile notes)
    @tests/test_training_engine.py (TestKohyaCommandGeneration joined-string substring conventions L232-240)
  </read_first>
  <behavior>
    - Generated command begins with accelerate launch wrapper including a bounded cpu-thread count, then the trainer script path from KOHYA_SS_PATH.
    - Command contains the Flux network module argument, the three companion model file arguments when their config fields are set, safetensors save format, bf16 precision flags, gradient checkpointing, sdpa attention, fp8_base, cache flags for latents and text-encoder outputs, Flux sampling flags (guidance scale 1.0, flux-shift timestep sampling, raw prediction type), and dataloader workers bounded to 2.
    - blocks_to_swap value flows from a new config field defaulting to 8.
    - The previously dead caption-dropout config field now appears in the command.
    - Omitted optional model paths produce commands without those flags rather than empty-string arguments.
    - All existing command-generation substring assertions updated to the new argv layout keep passing.
  </behavior>
  <action>
    Extend `TrainingConfig` with optional Flux model-path fields for the single-file transformer checkpoint, the clip_l text encoder, the t5xxl text encoder, and the vae — all Optional[str] = None — plus an integer block-swap field defaulting to 8 and keeping any existing memory-related defaults consistent.

    Rewrite `_build_command` to emit the documented Flux skeleton (RESEARCH Code Examples): prefix the argv with an accelerate launch wrapper (bounded per-process CPU threads suitable for Colab's 2-vCPU runtimes), then the flux training script path resolved under the configured Kohya checkout root. Include: pretrained model path, the three companion model flags only when their config values are set (never emit empty-string args), dataset config TOML path, output dir/name built from character_id and version using the validated identifiers from Task 1, save-format flag for safetensors, the lora_flux network module with dim/alpha/learning-rate/optimizer/scheduler/epoch settings from existing config fields, bf16 mixed and save precision, seed, gradient checkpointing, sdpa, fp8_base, block swap with the configured count, latent caching flags (disk variants included), text-encoder output caching flags, guidance-scale 1.0, flux-shift timestep sampling, raw model prediction type, and dataloader workers reduced to 2 (the current value of 8 is too heavy for Colab). Forward the previously dead caption-dropout field as its corresponding flag.

    Preserve invariants: pure arg-list construction (never shell=True), every filesystem path resolved before entering argv, no quoting/mangling of arguments. Fix the misleading resolution comment — image resolution comes from the dataset TOML, not a width-x-height argument. Keep validate_environment() as-is.

    Update TestKohyaCommandGeneration assertions to the new layout using the established joined-string substring style: wrapper present, network module present, each companion-model flag appears exactly when configured, workers flag shows the reduced value, dropout flag present. Add a case asserting omitted optional paths yield no stray flags. Everything stays mocked/offline.
  </action>
  <verify>
    <automated>python3 -m pytest tests/test_training_engine.py::TestKohyaCommandGeneration -q</automated>
    <automated>python3 -m pytest tests/test_training_engine.py tests/test_lora_training.py -q</automated>
  </verify>
  <done>
    _build_command emits the full Flux contract (accelerate wrapper, lora_flux network, three companion models, fp8/cache/memory flags, Colab-safe worker count) as a safe arg-list, config fields carry the new knobs with sane defaults, and both engine suites stay green offline.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| TrainingConfig inputs → subprocess argv | character_id/version/paths cross into process spawning |
| KOHYA_SS_PATH checkout → executed scripts | External repo code invoked at train time |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-01c-03a | Tampering/Elevation | character_id/version interpolated into argv and artifact filenames | high | mitigate | Conservative identifier pattern validated before interpolation; arg-list-only exec preserved (never shell=True); paths resolved before entering argv |
| T-01c-03b | Tampering | Accidental real subprocess spawn during offline proof | high | mitigate | dry_run branch skips subprocess entirely; sentinel-based tests fail if subprocess.run is ever invoked on the dry-run path |
| T-01c-03c | Information Disclosure | .train_cmd.json artifact contents | low | accept | Artifact contains paths/flags only — tokens never enter TrainingConfig |
| T-01c-SC | Tampering | Package installs | low | accept | No project-tree installs (C-NODEP); kohya/sd-scripts execution happens only in the operator's Colab runtime (Plan 01c-06 pins it) |
</threat_model>

<verification>
1. `python3 -m pytest tests/test_training_engine.py -q` — all green offline
2. Full suite `python3 -m pytest -q` — no regressions
3. Dry-run sentinel test proves zero subprocess invocation on the deferred-human evidence path
</verification>

<success_criteria>
1. Dry-run is a first-class engine mode producing registry-valid completions with inspectable artifacts
2. Command builder emits the complete Flux training contract cited from official sd-scripts docs
3. Identifier validation + arg-list invariant make command construction injection-safe
4. All tests pass without GPU or network
</success_criteria>

<output>
Create `.planning/phases/01c-character-training-system/01c-03-SUMMARY.md` when done.
</output>
