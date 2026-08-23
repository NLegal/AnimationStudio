---
phase: 01c-character-training-system
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/training_engine/dataset_builder.py
  - src/asset_repository/sqlite_repo.py
  - tests/test_lora_training.py
  - tests/test_asset_repository.py
autonomous: true
requirements:
  - CHAR-07
user_setup: []
must_haves:
  truths:
    - Curated query returns only assets in approved or production lifecycle state for a character (locked decision: datasets come from approved/production lifecycle states)
    - Every training image in the built dataset has an adjacent .txt caption sidecar beginning with the trigger word (locked caption convention)
    - Generated dataset_config.toml validates against the documented Kohya sd-scripts schema — only documented keys per section, and validation images are never mounted as a training subset (G1, G2, G3)
    - Dataset build enforces the 20-40 image bounds from ROADMAP — error below minimum with per-state counts, hard cap above maximum with warning (G6 / A1)
    - Reference-type curated assets land in baselines/{character_id}/ so LoRABenchmark._load_baseline_images has a population path (G15)
  artifacts:
    - src/asset_repository/sqlite_repo.py (async find_curated method)
    - src/training_engine/dataset_builder.py (sidecars, schema-valid TOML, bounds, baselines copy)
    - tests/test_lora_training.py (extended TestDatasetBuilder — sidecar/toml/bounds cases)
    - tests/test_asset_repository.py (curated-filter case)
  key_links:
    - find_curated output feeds build_entries_from_assets — returned dict shape must match the existing finder return contract
    - Sidecar body reuses the existing caption assembly (prefix + descriptor + suffix) so the trigger word survives shuffle_caption via keep_tokens=1
    - baselines/{character_id}/ directory naming matches LoRABenchmark._load_baseline_images lookup convention ({baseline_dir}/{character_id}/)
---

<objective>
Complete the dataset half of CHAR-07 criterion 1: close gaps G1, G2, G3, G4, G6, G15 in `DatasetBuilder` and add the two-state curated query the locked approved/production curation rule needs. After this plan, building a dataset from curated assets produces a schema-valid Kohya DreamBooth-style dataset with .txt caption sidecars, bounded to 20-40 images, and a populated baselines directory.

Purpose: The generated TOML currently uses a key that sd-scripts' schema validator rejects outright (a GPU-session killer discovered 10 minutes into a Colab run), captions never reach Kohya's expected sidecar files, and the locked curation filter has no query surface. These fixes make every downstream training run possible.
Output: Fixed dataset_builder.py, new find_curated repo method, extended offline test coverage.
</objective>

<execution_context>
@/root/.config/opencode/gsd-core/workflows/execute-plan.md
@/root/.config/opencode/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/phases/01c-character-training-system/01c-CONTEXT.md
@.planning/phases/01c-character-training-system/01c-RESEARCH.md
@.planning/phases/01c-character-training-system/01c-PATTERNS.md

@src/training_engine/dataset_builder.py
@src/asset_repository/sqlite_repo.py
@tests/test_lora_training.py
@tests/test_asset_repository.py

Phase constraints (echoed in every action):
- C-OFFLINE: all tests pass without GPU/network — fixtures and tmp_path only.
- C-CATALOGDB: catalog.db is never written or migrated by this phase's code or tests; live DB is corrupt for scans (index-covered queries only).
- C-NODEP: stdlib-only plus already-declared pyproject deps (Pillow allowed). No new packages.
- Report byte-compatibility constraints do NOT apply to this phase (that is Phase 7/8 scope).
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Add find_curated two-state repository query (G4)</name>
  <files>src/asset_repository/sqlite_repo.py, tests/test_asset_repository.py</files>
  <read_first>
    @src/asset_repository/sqlite_repo.py (find_approved method around L349-358 — the single-state precedent to mirror; assets table schema for exact column names incl. brand-score column)
    @scripts/export_assets.py (L89-93 — the state IN (...) parameterized SQL shape)
    @src/review_ui/app.py (L208-213 — the ("approved", "production") curated-set precedent)
    @.planning/phases/01c-character-training-system/01c-RESEARCH.md (G4 row; Pitfall 2 — corrupt catalog.db requires index-covered queries)
  </read_first>
  <behavior>
    - Seeded in-memory repo containing rows in scored, shortlisted, approved, and production states: find_curated(character_id) returns exactly the approved and production rows, nothing else.
    - find_curated(character_id, asset_types=("reference","expression")) filters by asset type when provided; returns all curated types when omitted.
    - Unknown character id returns an empty list (no exception), matching sibling finder behavior.
    - Returned dicts carry the same keys as find_approved results plus the brand-score column so callers can dedupe per variant later (Plan 01c-05).
  </behavior>
  <action>
    Add an async method `find_curated(self, character_id: str, asset_types: Optional[Sequence[str]] = None) -> list[dict]` to `SQLiteAssetRepository`, placed directly after `find_approved` and mirroring its structure, connection handling, and return-dict shape.

    SQL: SELECT the same columns find_approved returns PLUS the brand-score column (confirm the exact column name from the assets table schema at the top of sqlite_repo.py before writing) FROM assets WHERE character_id = ? AND state IN ('approved', 'production'), with an optional AND asset_type IN (...) clause built from parameter placeholders only — never string-interpolated values. ORDER BY a stable key (brand score descending, then id) so callers get deterministic ordering.

    Per RESEARCH Pitfall 2, keep the query index-covered: equality on character_id plus state/type membership follows the same access path as find_approved, which is verified to work against the live (scan-corrupt) database. Do NOT add GROUP BY or ORDER BY over unindexed global columns.

    Wrap execution like sibling methods: propagate sqlite3.DatabaseError as-is (fail loudly) — no silent partial reads.

    Do NOT modify any schema, migration, or existing method. Do NOT touch catalog.db. Tests seed an in-memory repository via the existing fixtures/conventions in tests/test_asset_repository.py.
  </action>
  <verify>
    <automated>python3 -m pytest tests/test_asset_repository.py -q</automated>
  </verify>
  <done>
    find_curated returns approved-union-production rows only, honors optional asset_types filter, returns [] for unknown characters, includes brand-score data, and passes the seeded in-memory tests without touching catalog.db.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: DatasetBuilder correctness — sidecars, schema-valid TOML, native validation split, min/max bounds, baselines copy (G1, G2, G3, G6, G15)</name>
  <files>src/training_engine/dataset_builder.py, tests/test_lora_training.py</files>
  <read_first>
    @src/training_engine/dataset_builder.py (DatasetConfig L27-38; _copy_and_caption L126-168 incl. caption assembly L152-159 and dest naming L149; _write_kohya_config L170-210; build() entry flow)
    @.planning/phases/01c-character-training-system/01c-RESEARCH.md (G1-G3 rows; Code Examples "Valid minimal Kohya TOML" and caption sidecar pair; Pitfall 1; Pitfall 3)
    @.planning/phases/01c-character-training-system/01c-PATTERNS.md (dataset_builder.py touch points section)
    @src/training_engine/benchmark.py (_load_baseline_images L347-370 — the {baseline_dir}/{character_id}/ convention the baselines copy must satisfy)
    @tests/test_lora_training.py (TestDatasetBuilder class conventions: tmp_path fixtures, dummy image files)
  </read_first>
  <behavior>
    - After build(), every image in train/ has a sibling .txt file whose content starts with the trigger-word prefix, then the record descriptor, joined with comma-space (suffix appended when configured); file stem matches the image stem.
    - Generated TOML parses with tomllib and contains ONLY documented keys: [general] shuffle_caption/caption_extension/keep_tokens/enable_bucket/min_bucket_reso/max_bucket_reso; [[datasets]] resolution/batch_size/validation_split/validation_seed; exactly one [[datasets.subsets]] with image_dir pointing at train/ and num_repeats. No subset references val/.
    - DatasetConfig(min_images=20, max_images=40) defaults exist; a build supplied fewer than min_images entries raises ValueError with per-lifecycle-state counts in the message; more than max_images truncates to max with a warnings.warn.
    - Reference-type curated entries are copied into {output_dir}/baselines/{character_id}/ (capped at 10) so the benchmark baseline loader finds them.
  </behavior>
  <action>
    Modify `DatasetConfig` (currently L27-38): add `min_images: int = 20` and `max_images: int = 40` fields following the existing plain-default field style. These fields do not exist today (assumption A1 confirmed by research); the 20-40 range comes from ROADMAP success criterion 2 per the locked decision to keep those bounds.

    Modify `_copy_and_caption`: keep the existing destination naming pattern for images, and after copying each image write a sibling sidecar named dest-stem + ".txt" in the same directory, UTF-8 encoded. Body = the already-assembled caption string from the existing assembly code (trigger-word prefix first, descriptor sourced from the record prompt, suffix appended), so shuffle_caption=true on Colab cannot displace the trigger word thanks to keep_tokens=1 emitted in general config.

    Rewrite `_write_kohya_config` to emit ONLY documented sd-scripts keys (schema per official config_README, cited in RESEARCH): a [general] table with shuffle_caption=true, caption_extension=".txt", keep_tokens=1, enable_bucket=true, min_bucket_reso=256, max_bucket_reso=2048; one [[datasets]] table carrying resolution (from config), batch_size=1, validation_split=config.validation_split, validation_seed=config.shuffle_seed; and a single [[datasets.subsets]] with image_dir set to the train directory path and num_repeats=config.repeat_count. Remove the custom caption-metadata key (G2 — rejected by the schema validator as an extra key), remove the bare empty caption_prefix emission, and remove the val/-as-training-subset block entirely (G3 — validation images must never be trained on). The builder still materializes the val/ directory for operator inspection; it is simply no longer mounted in any training subset — sd-scripts' native validation_split replaces it. Fix the misleading resolution comment while there.

    Add bounds enforcement in `build()` after entries are mapped but before copying: if the valid-entry count is below config.min_images, raise ValueError whose message lists counts per lifecycle state (scored/shortlisted/approved/production of the input records) — RESEARCH Pitfall 1's loud-failure requirement. If above config.max_images, emit warnings.warn naming the cap and truncate deterministically (entries arrive seed-shuffled; take the first max_images).

    Add a baselines step at the end of `build()`: copy up to 10 reference-type entries' source images into output_dir/"baselines"/character_id/ using whatever asset-type metadata `build_entries_from_assets` carries on DatasetEntry; if DatasetEntry does not carry asset type, extend it with an optional field populated by the existing mapping. This populates the exact directory convention LoRABenchmark._load_baseline_images reads ({baseline_dir}/{character_id}/).

    Preserve the existing warnings.warn-and-skip idiom for unreadable sources (L146 precedent). Before any filesystem copy, resolve each source path via Path.resolve() and skip-with-warning any resolved path that escapes its declared root — untrusted repo-supplied file_path values must not be able to place files outside the training output tree (threat T-01c-01a). Curation/state filtering stays OUT of this module (research anti-pattern): the builder trusts pre-filtered entries.

    Extend tests/test_lora_training.py TestDatasetBuilder: sidecar-per-image case asserting trigger word is the first token; TOML case parsing with tomllib and asserting the exact allowed-key sets per section plus single-subset/no-val-subset; bounds cases for under-min error message containing state counts and over-max truncation + warning; baselines case. Use tmp_path and dummy image bytes per existing class conventions. No network, no GPU, no new imports beyond stdlib tomllib/warnings and PIL if needed (C-OFFLINE, C-NODEP).
  </action>
  <verify>
    <automated>python3 -m pytest tests/test_lora_training.py::TestDatasetBuilder -q</automated>
    <automated>python3 -m pytest tests/test_lora_training.py tests/test_training_engine.py -q</automated>
  </verify>
  <done>
    Built datasets contain one .txt sidecar per train image starting with the trigger word; generated TOML is schema-valid (documented keys only, native validation_split, single train-only subset); builds below 20 images raise ValueError listing per-state counts; builds above 40 warn and cap; reference assets populate baselines/{character_id}/; full engine suites stay green offline.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| catalog.db → dataset pipeline | Repo-supplied rows (file_path, prompt, character_id) cross into filesystem operations |
| Universe Library PNGs → training dirs | Binary assets copied into dataset output trees |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-01c-01a | Tampering | find_curated → DatasetBuilder copy path | high | mitigate | Path.resolve() containment check before every copy; skip-and-warn paths escaping expected roots; character_id sanitized before directory-name interpolation |
| T-01c-01b | Tampering/DoS | Curated SQL query vs corrupted catalog.db | medium | mitigate | Index-covered query (equality on character_id + state/type membership); propagate sqlite3.DatabaseError loudly — no silent partial reads; no GROUP BY/global sorts |
| T-01c-01c | Denial of Service | Oversized/empty curated sets | low | accept | min/max bounds raise or cap deterministically; single-operator tooling |
| T-01c-SC | Tampering | Package installs | low | accept | No project-tree package installs — stdlib + existing pyproject deps only (C-NODEP) |
</threat_model>

<verification>
1. `python3 -m pytest tests/test_lora_training.py tests/test_asset_repository.py tests/test_training_engine.py -q` — all green offline
2. Full suite: `python3 -m pytest -q` — no regressions against the 51-test baseline (plus this plan's additions)
3. No code path in this plan writes to or migrates catalog.db (C-CATALOGDB)
</verification>

<success_criteria>
1. find_curated implements the locked approved/production curation rule with deterministic ordering
2. Datasets built by DatasetBuilder would pass Kohya sd-scripts' voluptuous schema validation offline (documented keys only)
3. Trigger-word-first .txt sidecars exist for every training image
4. 20-40 bounds enforced (error below min with state breakdown, capped above max)
5. Baselines directory convention populated from reference assets
6. All verification commands pass without GPU or network
</success_criteria>

<output>
Create `.planning/phases/01c-character-training-system/01c-01-SUMMARY.md` when done.
</output>
