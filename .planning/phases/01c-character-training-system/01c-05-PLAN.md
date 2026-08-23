---
phase: 01c-character-training-system
plan: 05
type: execute
wave: 4
depends_on: ["01c-01", "01c-02", "01c-03", "01c-04"]
files_modified:
  - scripts/train_lora.py
  - tests/test_train_lora_script.py
autonomous: true
requirements:
  - CHAR-07
user_setup: []
must_haves:
  truths:
    - scripts/train_lora.py --dry-run completes the full pipeline end-to-end offline — curate from the repository, build a bounded dataset, prove the train command, register a version, run an advisory benchmark — with ZERO subprocess invocation (the locked deferred-human evidence path)
    - Curation dedupes to one best image per variant (highest brand score) and caps at max_images before handing clean entries to DatasetBuilder (G7 / A5)
    - Local real training is refused by policy — the train subcommand without dry-run exits with an error directing operators to the Colab notebook (locked Production Training Reality)
    - The versions subcommand is read-only over the persisted registry — no placeholder entries can be fabricated (locked decision)
    - Exit codes follow repo convention: 0 success, 1 failure (generate_phase5/export_assets precedent)
  artifacts:
    - scripts/train_lora.py (argparse CLI: build-dataset / train / benchmark / versions subcommands)
    - tests/test_train_lora_script.py (offline CLI integration suite)
  key_links:
    - find_curated output → per-variant dedupe → DatasetBuilder.build() — curation happens in the orchestration layer, never inside the builder (research anti-pattern)
    - train subcommand wires TrainingConfig(dry_run=True) + KohyaAdapter + persisted VersionRegistry(load_registry path) so dry-run evidence survives sessions
    - benchmark subcommand feeds LoRABenchmark with IdentityScorerProvider and explicit test images, honoring the G14 stub constraint (offline runs must supply images)
---

<objective>
Deliver the offline-provable orchestration path for CHAR-07 criterion 2's deferred-human chain: one CLI that curates approved/production assets into a bounded dataset, proves the Flux training command via first-class dry-run, benchmarks against the identity scorer, and manages persisted versions.

Purpose: This script is the local half of the production-training evidence chain — when it exits 0 on --dry-run with zero subprocess spawns, the only unproven step left is the GPU itself (Colab operator action, Plan 01c-06).
Output: scripts/train_lora.py + full offline integration test coverage.
</objective>

<execution_context>
@/root/.config/opencode/gsd-core/workflows/execute-plan.md
@/root/.config/opencode/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/phases/01c-character-training-system/01c-CONTEXT.md
@.planning/phases/01c-character-training-system/01c-RESEARCH.md
@.planning/phases/01c-character-training-system/01c-PATTERNS.md

@scripts/export_assets.py
@scripts/generate_phase5.py
@src/training_engine/dataset_builder.py
@src/training_engine/kohya_adapter.py
@src/training_engine/versioning.py
@src/training_engine/benchmark.py

Phase constraints (echoed in every action):
- C-OFFLINE: the script must complete --dry-run with no GPU and no network; tests never spawn subprocesses.
- C-CATALOGDB: the script READS catalog.db via index-covered queries only; never writes or migrates it.
- C-NODEP: stdlib argparse/subprocess/json/pathlib only plus existing package imports.
- Report byte-compatibility constraints do NOT apply to this phase (Phase 7/8 scope).
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: CLI skeleton + build-dataset + train (dry-run-enforced) end-to-end slice</name>
  <files>scripts/train_lora.py, tests/test_train_lora_script.py</files>
  <read_first>
    @scripts/export_assets.py (L30 sys.path bootstrap; L39-69 argparse conventions incl. --db/--states/--dry-run; comma-set parsing; fail-fast SystemExit; exit-code tail)
    @scripts/generate_phase5.py (docstring reproduction header L1-16; main() -> int + sys.exit(main()) convention)
    @.planning/phases/01c-character-training-system/01c-PATTERNS.md ("Script bootstrap & CLI hygiene" shared pattern; train_lora.py analog assignment)
    @src/training_engine/dataset_builder.py (DatasetConfig fields incl. new min/max; build() signature)
    @src/asset_repository/sqlite_repo.py (SQLiteAssetRepository constructor + find_curated from Plan 01c-01)
  </read_first>
  <behavior>
    - build-dataset against a seeded tmp sqlite db containing mixed-state assets for lily-bunny: dataset directory materializes with sidecar captions, TOML config, baselines dir; entries deduped to one per variant keeping the highest brand score; capped at max_images.
    - train --dry-run: writes .train_cmd.json artifact under the output root, registers exactly one version record in the registry file at the given path, exits 0; second invocation registers the NEXT version rather than duplicating.
    - train without --dry-run: exits non-zero with an error message naming the Colab notebook as the real-run path; zero subprocess spawns ever occur locally.
    - Unknown character or empty curated set: exits non-zero with the per-state count breakdown (Pitfall 1 surfacing).
  </behavior>
  <action>
    Create `scripts/train_lora.py` following the export_assets/generate_phase5 conventions exactly: reproduction docstring header, sys.path bootstrap inserting the repo root via parents[1], ArgumentParser with RawDescriptionHelpFormatter and description=__doc__, global flags --db (default catalog.db), --character-id (default lily-bunny), --output-root (default training/), --registry-path (default training/lora_registry.json), --states (default "approved,production", comma-set parsed), --min-images/--max-images overrides, --dry-run store_true. Subcommands: build-dataset, train, benchmark, versions. Invalid input raises SystemExit with a clear message; main() -> int returns 0/1; module tail uses sys.exit(main()).

    Shared curation helper used by build-dataset (and later cells): open SQLiteAssetRepository on --db, call find_curated(character_id) (states already enforced by the query; --states maps to the two supported values with validation rejecting anything else), then dedupe per (asset_type, variant) keeping the highest brand-score row with stable tie-break by asset id, then cap to max_images. Hand the resulting dicts straight to build_entries_from_assets — no state filtering inside DatasetBuilder.

    build-dataset: construct DatasetConfig with bounds from flags, call builder.build(), print a summary line (image counts, output dir, baselines count). Exit 1 with the raised ValueError message when below minimum.

    train: REFUSE real execution locally — if --dry-run is absent, print an explanation that real training is a Colab operator action (notebook name) and return 1. With --dry-run: compute the next version via recommend_next on the persisted registry (load_registry), build TrainingConfig with dry_run=True and the Flux model-path/memory fields left at defaults (operator fills them in the notebook), run KohyaAdapter.train, print the result summary and the command-artifact path, exit 0 on success / 1 on typed failure. Registration happens ONLY through the adapter's post-completion path — never pre-seed versions (locked no-placeholder rule).

    Identifier hygiene: reuse the same conservative character-id/version pattern validation as the engine before any filesystem interpolation (threat T-01c-05a).

    Create tests/test_train_lora_script.py mirroring test_training_engine.py conventions: module docstring scope list, class-per-subcommand grouping, tmp_path everywhere, seeded tmp sqlite database built through SQLiteAssetRepository fixtures (in-memory repo API or file-backed as the constructor requires), dummy image bytes files, subprocess.run monkeypatched with a sentinel at the module-under-test boundary asserting it is NEVER called across the whole suite (C-OFFLINE proof). Cover the four behaviors above.
  </action>
  <verify>
    <automated>python3 -m pytest tests/test_train_lora_script.py -q</automated>
    <automated>python3 scripts/train_lora.py --help</automated>
  </verify>
  <done>
    CLI exists with repo-conventional argparse surface; build-dataset produces a valid bounded dataset from curated assets with variant dedupe; train enforces the Colab-only policy while its dry-run path registers durable version evidence offline; all behaviors covered by sentinel-guarded offline tests.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: benchmark + versions subcommands and full CLI integration coverage</name>
  <files>scripts/train_lora.py, tests/test_train_lora_script.py</files>
  <read_first>
    @src/training_engine/benchmark.py (LoRABenchmark constructor injection L187; evaluate(lora_path, character_id, test_images) contract; report(); BenchmarkResult.passed semantics incl. weight_coverage from Plan 01c-02)
    @src/training_engine/scorer_adapter.py (IdentityScorerProvider light-mode construction from Plan 01c-02)
    @src/training_engine/versioning.py (get_versions/get_promoted/recommend_next read paths; persisted registry from Plan 01c-04)
    @tests/test_train_lora_script.py (Task 1 conventions to extend)
  </read_first>
  <behavior>
    - benchmark with a dummy lora file, tmp baseline dir populated, and explicit --images: prints the markdown report, exits 0 when passed=True, exits 1 when failed; coverage below full prints a warning line.
    - benchmark without required inputs: exits non-zero naming the missing input (G14 — offline runs must supply images explicitly).
    - versions: lists persisted records for the character (version, promoted flag, trained_at) read-only; empty registry prints a clear none-registered message and exits 0; no record is ever created by this subcommand.
  </behavior>
  <action>
    Extend scripts/train_lora.py with the two remaining subcommands.

    benchmark: requires --lora (path to a .safetensors file) and --images (comma list or repeated flag of image paths) — offline runs must supply test images explicitly because engine-side generation is a documented stub (G14). Optional --baseline-dir defaulting to the dataset output root's baselines parent so Plan 01c-01's copy target feeds _load_baseline_images naturally. Construct LoRABenchmark with IdentityScorerProvider() (light mode offline), evaluate, print report() to stdout, return 0 if result.passed else 1; when weight_coverage is below 1.0 print an advisory line that the gate ran on partial plugin coverage and full evaluation happens on Colab.

    versions: load the persisted registry via load_registry(--registry-path), print one line per record sorted newest-first (version string, promoted marker, trained-at ISO, file path), exit 0. Strictly read-only — this command never registers, promotes, or writes (no-placeholder locked rule).

    Round out tests/test_train_lora_script.py: benchmark pass/fail/missing-input cases using a dummy bytes lora file and tiny fixture images plus a stub provider injected where the script structure allows (or light-mode real scorer against dummy bytes if the adapter tolerates non-image data — prefer injecting a fake provider through a small seam parameter on the script's benchmark entry function to keep tests deterministic); versions listing case asserting exact output ordering and read-only behavior (registry file unchanged byte-for-byte after invocation); end-to-end chain test build-dataset → train --dry-run → versions proving the whole deferred-human evidence path in one process-free sequence.

    Keep every test subprocess-sentinel-guarded and network-free (C-OFFLINE).
  </action>
  <verify>
    <automated>python3 -m pytest tests/test_train_lora_script.py -q</automated>
    <automated>python3 -m pytest -q</automated>
  </verify>
  <done>
    All four subcommands work offline; benchmark honors explicit-images + coverage honesty with correct exit codes; versions is provably read-only; the full curate → dry-run-train → inspect chain passes as one integration sequence with zero subprocess spawns.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| CLI arguments → filesystem/sqlite | Operator-supplied ids/paths cross into queries and file operations |
| catalog.db → curation | Repo rows cross into dataset building |
| Registry JSON → versions output | On-disk records cross into operator-visible reporting |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-01c-05a | Tampering/Elevation | character-id/path args interpolated into fs ops and engine calls | high | mitigate | Conservative identifier pattern enforced before interpolation; output confined under --output-root via resolve containment; engine-side validation from Plan 01c-03 backs this up |
| T-01c-05b | DoS | Corrupt catalog.db failing mid-curation | medium | mitigate | Index-covered find_curated only; DatabaseError propagates loudly with non-zero exit — no silent partial datasets |
| T-01c-05c | Repudiation | Fabricated version history via CLI | low | mitigate | train registers only post-completion through the adapter; versions strictly read-only; no seed/import path exists |
| T-01c-SC | Tampering | Package installs | low | accept | stdlib-only CLI (C-NODEP); real training stack installs happen exclusively inside the operator's ephemeral Colab runtime |
</threat_model>

<verification>
1. `python3 -m pytest tests/test_train_lora_script.py -q` — all green
2. Full suite `python3 -m pytest -q` — no regressions vs baseline
3. `python3 scripts/train_lora.py train --character-id lily-bunny` (no --dry-run) exits 1 pointing at the notebook — policy proof
4. `python3 scripts/train_lora.py train --dry-run --db <tmp> --registry-path <tmp>` exits 0 with artifact + registry evidence, zero spawns
</verification>

<success_criteria>
1. One command proves the entire offline training-evidence chain end-to-end
2. Curation implements the per-variant best-image rule and bounds before the builder sees anything
3. Local real training impossible by policy; Colab named as the exclusive GPU path
4. Version history appendable only by completed runs, durable across sessions
5. All tests green offline; sentinel guard proves zero subprocess invocation
</success_criteria>

<output>
Create `.planning/phases/01c-character-training-system/01c-05-SUMMARY.md` when done.
</output>
