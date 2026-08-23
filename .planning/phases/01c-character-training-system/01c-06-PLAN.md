---
phase: 01c-character-training-system
plan: 06
type: execute
wave: 5
depends_on: ["01c-05"]
files_modified:
  - colab/AnimationStudio_Colab_Training.ipynb
  - tests/test_colab_notebooks.py
  - README.md
autonomous: true
requirements:
  - CHAR-07
user_setup:
  - service: huggingface
    why: "FLUX.1-dev is a gated model — operator accepts the license and supplies an HF token in the notebook at run time (never committed)"
    env_vars:
      - name: HF_TOKEN
        source: "huggingface.co -> Settings -> Access Tokens (requires gated FLUX.1-dev access accepted)"
    dashboard_config:
      - task: "Accept FLUX.1-dev model license for the operator account"
        location: "huggingface.co/black-forest-labs/FLUX.1-dev"
  - service: github
    why: "Sync cell pushes trained safetensors + benchmark report back to the repo branch"
    env_vars:
      - name: GITHUB_TOKEN
        source: "GitHub -> Settings -> Developer settings -> fine-grained PAT with write on AnimationStudio"
  - service: google-colab
    why: "Real training is an operator action on a Colab T4/A100 runtime — locked deferred-human path; free-tier T4 works with the fp8 profile at hours scale"
must_haves:
  truths:
    - An operator can open the committed notebook on a Colab GPU runtime and follow it top-to-bottom to produce lily-bunny_v1.0.safetensors plus a benchmark report without editing any cell except Settings (criterion 2 deferred-human path)
    - The notebook fails fast with clear guidance when no GPU is present or compute capability is below the Flux-viable threshold
    - Committed notebook contains NO tokens — HF/GitHub params are empty placeholders filled only at run time
    - sd-scripts checkout is pinned to a specific upstream commit so training behavior is reproducible across sessions
    - Notebook structural validity is enforced by smoke tests — valid ipynb JSON, required cells present, no secret-shaped strings, across all colab notebooks
  artifacts:
    - colab/AnimationStudio_Colab_Training.ipynb (mirrors Phase 4 nbformat-4 pattern with training-specific cells)
    - tests/test_colab_notebooks.py (structural smoke suite over colab/*.ipynb)
    - README.md (Character Training section — local dry-run + Colab runbook pointer)
  key_links:
    - Dataset-build cell invokes scripts/train_lora.py --build-dataset from the clone — Universe Library ships via git (4761 tracked PNGs verified) so no Drive upload step exists (A6 verified)
    - Training cell composes the same Flux flag set Plan 01c-03's _build_command emits locally — dry-run artifact and notebook command stay comparable line-for-line
    - Benchmark cell uses IdentityScorerProvider with full plugins and requires composite >= 0.90 at coverage 1.0 before the promote step runs
    - Sync cell reuses colab/git_sync.py _basic_auth_header exactly like the Phase 4 notebook
---

<objective>
Deliver the GPU half of CHAR-07 criterion 2 as an operator action: a Colab training notebook mirroring the proven Phase 4 pattern (settings → environment → work → sync → next steps) with VRAM profiles for T4/A100, gated model downloads, dataset build from the repo clone, accelerate-based Flux training, sample generation, identity benchmark gate, version registration/promotion, and artifact sync — plus structural smoke tests and README runbook documentation.

Purpose: No GPU exists in the build environment; the locked decision absorbs this via deferred-human verification. Success criterion "production LoRA v1.0 trained" is satisfied by this notebook plus the proven local dry-run path, recorded verification_deferred_human until an operator executes it.
Output: AnimationStudio_Colab_Training.ipynb, notebook smoke tests, README training section.
</objective>

<execution_context>
@/root/.config/opencode/gsd-core/workflows/execute-plan.md
@/root/.config/opencode/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/phases/01c-character-training-system/01c-CONTEXT.md
@.planning/phases/01c-character-training-system/01c-RESEARCH.md
@.planning/phases/01c-character-training-system/01c-PATTERNS.md

@colab/AnimationStudio_Colab_Phase4.ipynb
@colab/git_sync.py
@scripts/train_lora.py

Phase constraints:
- C-OFFLINE applies to TESTS only here: the notebook targets GPU Colab; the pytest smoke suite parses JSON offline and never executes notebook code.
- C-CATALOGDB: notebook reads catalog.db exclusively through train_lora.py's index-covered queries.
- C-NODEP: project-tree deps unchanged — every install happens inside the ephemeral Colab runtime.
</context>

<tasks>

<task type="auto">
  <name>Task 1: Build the Colab training notebook on the Phase 4 skeleton</name>
  <files>colab/AnimationStudio_Colab_Training.ipynb</files>
  <read_first>
    @colab/AnimationStudio_Colab_Phase4.ipynb (nbformat-4 JSON structure; cell layout per PATTERNS table — #@title numbered titles, #@param settings forms with EMPTY token fields, run() helper printing commands before executing, sync cell importing git_sync._basic_auth_header, trailing Next-steps markdown)
    @colab/git_sync.py (_basic_auth_header L25-33)
    @.planning/phases/01c-character-training-system/01c-PATTERNS.md ("Colab notebook conventions" shared pattern; notebook analog assignment)
    @.planning/phases/01c-character-training-system/01c-RESEARCH.md (Pattern 3 notebook deltas; Code Examples Flux command skeleton; Pitfall 6 T4 bf16 trap; State of the Art VRAM profiles)
  </read_first>
  <action>
    Author a valid nbformat-4 ipynb (kernelspec python3) mirroring the Phase 4 skeleton, extended for training. Numbered #@title cells:

    Markdown intro: purpose, prerequisites (GPU runtime type, HF gated-model acceptance, PAT), pointer to README runbook, explicit statement that the committed file contains no secrets.

    Cell 1 Settings: #@param fields — REPO_URL, BRANCH, WORK/REPO paths, CHARACTER_ID (default lily-bunny), VRAM_PROFILE selector (t4-16g default, a100-24g, t4-12gb-swap16), SYNC_TO_GITHUB boolean, GITHUB_TOKEN empty string param, HF_TOKEN empty string param, MODEL_DIR path.

    Cell 2 GPU check (fail-fast): assert nvidia-smi succeeds and torch.cuda.is_available(); print device name and compute capability; when capability < 8 warn that Turing needs the fp8 profile and expect hours-scale step times (Pitfall 6 NaN trap note: never fp16 on T4); abort execution with clear guidance when no GPU is visible.

    Cell 3 Clone and install: reuse the Phase 4 run() helper verbatim in style — clone --branch, pip install -e . --no-deps, then git clone kohya sd-scripts pinned to an explicit upstream commit hash into the workspace and pip install its requirements (document that the pin trades freshness for reproducibility and how to bump it).

    Cell 4 Model downloads: fetch the four required files (flux1-dev single-file safetensors, clip_l, t5xxl fp16, ae safetensors) from their Hugging Face repos using the HF_TOKEN header via huggingface_hub or authenticated curl arg-lists; verify non-zero sizes; never echo the token.

    Cell 5 Dataset build: run scripts/train_lora.py --build-dataset against the cloned repo's catalog.db for CHARACTER_ID — note in comments that Universe Library PNGs ship inside the git clone so no Drive upload is needed, and that if the curated set is under the 20-image minimum the script exits non-zero listing per-state counts and the operator must promote assets via the Review UI first (interactive promotion is the default per A4).

    Cell 6 Training: compose the accelerate launch flux_train_network.py command from the RESEARCH skeleton, selecting flags by VRAM_PROFILE (24 GB: batch 2 basic; 16 GB: batch 1 + fp8_base + blocks_to_swap 8; 12 GB: swap 16 + AdamW8bit), mixed/save precision bf16, guidance 1.0, flux-shift sampling, raw prediction, cache latents + text-encoder outputs to disk, dataloader workers 2, output name {character_id}_v{next}. Execute via run() after printing the full command; keep argv-list discipline (no shell=True).

    Cell 7 Samples + benchmark: generate N=8 samples with the trained LoRA through a diffusers Flux pipeline, save under the dataset output tree; construct LoRABenchmark with IdentityScorerProvider(full plugins, light off) and evaluate against the generated images with the baselines directory populated by Plan 01c-01; print report(); state plainly that composite >= 0.90 at coverage 1.0 is the promote gate.

    Cell 8 Register/promote: load VersionRegistry via the repo API, register the completed version (dry-run-style registration semantics do NOT apply here — this is the real completion), and call promote only when the benchmark passed; print final version state.

    Cell 9 Sync: Phase 4 pattern verbatim plus extended git add covering the lora safetensors directory and benchmark report; push with _basic_auth_header when SYNC_TO_GITHUB else print manual-download instructions.

    Markdown Next steps: operator follow-ups — Review UI promotion of remaining assets, bulk-promotion alternative note, session-limit expectations, how to record verification_deferred_human resolution evidence.

    All code cells carry real error handling on their single path; tokens only ever flow from runtime params into headers/env — never literals. Validate the finished file parses as JSON with nbformat minor 5-ish structure consistent with sibling notebooks.
  </action>
  <verify>
    <automated>python3 -c "import json,pathlib; nb=json.loads(pathlib.Path('colab/AnimationStudio_Colab_Training.ipynb').read_text()); assert nb['nbformat']==4 and len(nb['cells'])>=10"</automated>
  </verify>
  <done>
    Notebook exists as valid nbformat-4 JSON with all eleven sections, empty-token settings, GPU fail-fast, pinned sd-scripts clone, VRAM profiles, dataset build via the CLI, training/samples/benchmark/register/promote/sync cells, and next-steps guidance.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Notebook smoke tests + README training runbook</name>
  <files>tests/test_colab_notebooks.py, README.md</files>
  <read_first>
    @tests/test_training_engine.py (module conventions — docstring, class grouping)
    @colab/ (inventory of existing notebooks to include in the structural sweep)
    @README.md (existing section structure and heading style to extend)
  </read_first>
  <behavior>
    - Every colab/*.ipynb parses as JSON with nbformat 4 and a non-empty cells list.
    - The training notebook contains: a settings cell with empty GITHUB_TOKEN/HF_TOKEN fields, a GPU-check cell, an sd-scripts clone cell carrying a pinned commit reference, the accelerate training cell, benchmark cell, promote step, sync cell, next-steps markdown.
    - No cell source in any committed notebook matches secret-shaped strings (long token-like literals) — guards against future token commits.
    - README documents the local dry-run chain and links the notebook runbook.
  </behavior>
  <action>
    Create tests/test_colab_notebooks.py: offline pytest module that discovers colab/*.ipynb via pathlib glob, json.loads each file, and asserts nbformat major 4 plus non-empty cells. For the training notebook specifically, assert required structural markers by scanning concatenated cell sources: settings param names for both tokens present AND their default values are empty strings; a GPU availability check exists; a pinned sd-scripts checkout reference exists (a commit-hash-shaped string); the accelerate/training, sample/benchmark, register/promote, and git-sync stages each appear; a next-steps markdown cell exists. Add a negative scan across ALL committed notebooks for high-entropy token-shaped literals (e.g., strings of 30+ mixed alphanumerics prefixed like known providers) so a future accidental paste fails CI. Zero network, zero notebook execution (C-OFFLINE).

    Extend README.md with a Character Training section following its existing heading style: what the phase delivers; the local evidence chain (curate/build/dry-run commands from scripts/train_lora.py and what artifacts prove each step); operator prerequisites (HF gated access, PAT, Colab runtime selection); a pointer to the notebook path and the VRAM profile table summary; the promotion prerequisite (Review UI approve/promote before build-dataset when curated count is under the minimum) and the deferred-human verification note for criterion 2. Keep it documentation-only — no code changes.
  </action>
  <verify>
    <automated>python3 -m pytest tests/test_colab_notebooks.py -q</automated>
    <automated>python3 -m pytest -q</automated>
  </verify>
  <done>
    Structural smoke suite passes over every colab notebook including the new training notebook; secret-shape guard active; README carries the operator runbook and local dry-run instructions.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Operator tokens → Colab runtime | HF/GitHub credentials enter only as runtime #@param values |
| Hugging Face / GitHub downloads → runtime filesystem | Model files and cloned repos cross into executed code |
| Trained artifacts → repo push | safetensors + reports cross back into the project tree |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-01c-06a | Information Disclosure | Tokens leaked through committed notebook cells or printed output | high | mitigate | Empty-string params committed; tokens flow only into headers/env at run time; echo suppressed; CI smoke test fails on token-shaped literals |
| T-01c-06b | Tampering | Supply chain — pip installs and sd-scripts clone inside Colab runtime | medium | mitigate | Pin sd-scripts to an explicit upstream commit; official repos only; pin noted in comments with bump procedure; installs confined to the ephemeral runtime (project dependency tree untouched) |
| T-01c-06c | Tampering | Downloaded model files corrupted/truncated | low | mitigate | Non-zero size verification after download; registry stores artifact paths so provenance is inspectable |
| T-01c-06d | Denial of Service | Colab session limits mid-training | low | accept | Documented expectation (hours-scale, session limits); checkpoint/output dirs enable resume-and-resync; operator-facing note in Next steps |
| T-01c-SC | Tampering | Project-tree package installs | low | accept | None — all installs live in the throwaway Colab runtime; pyproject unchanged (C-NODEP) |
</threat_model>

<verification>
1. `python3 -m pytest tests/test_colab_notebooks.py -q` — structural suite green offline
2. Full suite `python3 -m pytest -q` — no regressions
3. Notebook JSON valid; token params empty; pinned clone reference present
4. Criterion 2 evidence chain complete: local dry-run proof (Plan 01c-05) + this notebook = verification_deferred_human package ready
</verification>

<success_criteria>
1. Operator-ready notebook mirrors the proven Phase 4 pattern end-to-end for a T4/A100 Flux LoRA run
2. No secrets committed; supply-chain pins documented
3. Benchmark gate >= 0.90 at full coverage enforced before promotion in the notebook flow
4. Docs make the local-proof → Colab-execution handoff unambiguous
5. All tests green offline
</success_criteria>

<output>
Create `.planning/phases/01c-character-training-system/01c-06-SUMMARY.md` when done.
</output>
