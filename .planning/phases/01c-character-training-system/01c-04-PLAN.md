---
phase: 01c-character-training-system
plan: 04
type: execute
wave: 3
depends_on: ["01c-01", "01c-02"]
files_modified:
  - src/training_engine/versioning.py
  - src/training_engine/version_store.py
  - src/training_engine/__init__.py
  - tests/test_lora_training.py
autonomous: true
requirements:
  - CHAR-07
user_setup: []
must_haves:
  truths:
    - Version records survive process restarts via a sidecar JSON store — a registry constructed with a store path hydrates all previously saved records (G8, G9 fixed)
    - promote(character_id, version) flips an existing record to production post-hoc and persists the change (G10)
    - Registering the same (character_id, version) pair twice updates in place instead of duplicating (Pitfall 5)
    - catalog.db is never read, written, or migrated — persistence is fully isolated from the corrupted production database (A3; C-CATALOGDB)
    - No placeholder versions exist anywhere — records enter the store only through register() after a completed real or dry-run training (locked decision)
  artifacts:
    - src/training_engine/version_store.py (new JSON sidecar store matching the lora_models schema contract from migrations.py L49-58)
    - src/training_engine/versioning.py (store-backed registry seam + promote())
    - src/training_engine/__init__.py (store re-exports)
    - tests/test_lora_training.py (round-trip, promotion, uniqueness, tolerant-parse cases)
  key_links:
    - Store record fields mirror lora_models columns exactly (id, character_id, version, file_path, training_config JSON, benchmark_scores JSON, trained_at ISO, promoted) so a future consolidation can migrate mechanically
    - Registry hydrate path reuses from_db_records tolerant-parse semantics; save-on-mutate keeps every mutation durable
    - Default VersionRegistry() stays purely in-memory so all 51 existing baseline tests keep their semantics
---

<objective>
Give VersionRegistry durable storage and post-hoc promotion (CHAR-07 criterion 3): a corruption-isolated sidecar JSON store behind the existing in-memory domain logic, a promote() operation for the train-v0.x-then-promote-v1.0 flow, and idempotent registration.

Purpose: The registry forgets everything on process exit today, so dry-run evidence and future production records vanish between sessions and re-runs duplicate rows. The live catalog.db is corrupt for writes/scans, so persistence must be isolated (locked A3 direction).
Output: version_store.py, store-backed VersionRegistry with promote(), round-trip test coverage.
</objective>

<execution_context>
@/root/.config/opencode/gsd-core/workflows/execute-plan.md
@/root/.config/opencode/gsd-core/templates/summary.md
</execution_context>

<context>
@.planning/phases/01c-character-training-system/01c-CONTEXT.md
@.planning/phases/01c-character-training-system/01c-RESEARCH.md
@.planning/phases/01c-character-training-system/01c-PATTERNS.md

@src/training_engine/versioning.py
@src/asset_repository/migrations.py
@tests/test_lora_training.py

Phase constraints (echoed in every action):
- C-OFFLINE: all tests pass without GPU/network — tmp_path stores only.
- C-CATALOGDB: this plan NEVER touches catalog.db — no SchemaManager calls, no migrations applied; the lora_models SQL in migrations.py serves as the FIELD CONTRACT only.
- C-NODEP: stdlib-only (json/pathlib/datetime). No new packages.
- Report byte-compatibility constraints do NOT apply to this phase (Phase 7/8 scope).
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: JSON sidecar version store + registry persistence seam (G8, G9, A3)</name>
  <files>src/training_engine/version_store.py, src/training_engine/versioning.py, src/training_engine/__init__.py</files>
  <read_first>
    @src/asset_repository/migrations.py (lora_models table definition L49-58 — field contract only; do NOT apply any migration)
    @src/training_engine/versioning.py (_records dict L141-143; register() L144-175; from_db_records hydration L228-261 — tolerant parse, ISO datetime, bool coercion)
    @src/training_engine/dataset_builder.py (JSON write idiom L110-114 — indent=2, ensure_ascii=False, utf-8)
    @.planning/phases/01c-character-training-system/01c-PATTERNS.md (version_store.py pattern assignment — role-match note: no file-backed store exists in-repo yet)
    @.planning/phases/01c-character-training-system/01c-RESEARCH.md (G8, G9 rows; Open Question 2 resolution; Pitfall 5)
  </read_first>
  <behavior>
    - JsonVersionStore.save(path-less instance API) writes a readable JSON document; load() returns record dicts whose keys match the lora_models field contract.
    - Round-trip: register two versions → construct new registry over same store file → get_versions returns both with correct ordering, promoted flags, benchmark_scores and training_config payloads intact.
    - Corrupt/partial store content: unparsable records are skipped during hydration (tolerant parse), valid records survive.
    - VersionRegistry() with no store remains in-memory only — zero filesystem writes (existing baseline tests unchanged).
  </behavior>
  <action>
    Create `src/training_engine/version_store.py` defining `JsonVersionStore`: constructor takes a `store_path: Path`; methods `load() -> list[dict]` and `save(records: list[dict]) -> None`. Serialization follows the repo JSON idiom (indent=2, ensure_ascii=False, utf-8). Record dicts use exactly the lora_models field names as the schema contract: id, character_id, version (string form), file_path, training_config (JSON-encodable mapping or null), benchmark_scores (same), trained_at (ISO string), promoted (bool). save() must be atomic — write to a sibling temp file then os.replace over the destination — so a crash mid-write cannot corrupt the store. load() tolerates missing files (returns empty list) and skips individual unparsable entries rather than failing wholesale.

    Extend `VersionRegistry.__init__` with an optional `store: Optional[JsonVersionStore] = None` parameter. When a store is provided, hydrate on construction by feeding store.load() through the existing from_db_records-compatible parse path, and persist on every mutation (register/promote) by serializing the full current record set. Record ids: derive a stable id per (character_id, version) pair at registration time when absent.

    Make registration idempotent (Pitfall 5): registering a (character_id, version) that already exists REPLACES the prior record in place instead of appending a duplicate. Keep sort-order and immutability semantics of existing records intact; update the affected existing tests if they asserted blind-append behavior.

    Add a module-level convenience factory `load_registry(store_path: Path) -> VersionRegistry` returning a hydrated registry bound to the store.

    Re-export JsonVersionStore and load_registry from src/training_engine/__init__.py imports and __all__ per package conventions.

    Do NOT import anything from asset_repository (no SchemaManager, no migrations execution) — the coupling is documentation-level only (C-CATALOGDB).
  </action>
  <verify>
    <automated>python3 -m pytest tests/test_lora_training.py::TestVersionRegistry -q</automated>
    <automated>python3 -m pytest tests/test_lora_training.py -q</automated>
  </verify>
  <done>
    Sidecar store persists and hydrates version records losslessly with atomic writes; registries bound to a store survive round-trips; default in-memory behavior is untouched; no catalog.db involvement anywhere.
  </done>
  <reversibility rating="reversible">JSON sidecar chosen over migrating the corrupted catalog.db per locked A3; swapping to SQLite later is a mechanical format change isolated behind the JsonVersionStore seam.</reversibility>
</task>

<task type="auto" tdd="true">
  <name>Task 2: promote() post-hoc production promotion (G10)</name>
  <files>src/training_engine/versioning.py, tests/test_lora_training.py</files>
  <read_first>
    @src/training_engine/versioning.py (VersionRecord dataclass definition — immutability semantics; get_promoted L188-193; register signature L144-153)
    @.planning/phases/01c-character-training-system/01c-RESEARCH.md (G10 row; criterion 3 software-release convention v0.1 -> v1.0 -> v2.0)
    @tests/test_lora_training.py (TestVersionRegistry conventions)
  </read_first>
  <behavior>
    - promote(character_id, version) on an existing record: returns the updated record with promoted=True; get_promoted(character_id) then returns it; the change is persisted when a store is bound.
    - Promoting a second version after the first: both records may carry promoted=True historically OR the newest promotion wins — pick replace-semantics (promote flips only the target record; it does not un-promote others) and assert whichever contract is implemented consistently.
    - promote on unknown character or version raises ValueError naming the missing key.
  </behavior>
  <action>
    Add `promote(self, character_id: str, version: LoRAVersion) -> VersionRecord` to VersionRegistry. Records are immutable dataclasses, so implement promotion as replacement: locate the record for the (character_id, version) pair among existing records, rebuild it with promoted=True (dataclasses.replace or equivalent construction), swap it into the sorted list, persist through the store seam when bound, and return the updated record. Raise ValueError for unknown character ids or versions — message names which key was missing (typed-error convention: user-input errors raise, engine failures do not).

    Document the chosen multi-promotion semantics in the docstring (flip-target-only keeps the audit trail of every promoted version; get_promoted returns the highest-sorted promoted record).

    Extend TestVersionRegistry: promotion round-trip against a tmp_path-backed JsonVersionStore (promote → new registry instance over same file → promoted state visible); error cases for unknown character/version; interaction case proving dry-run registrations from Plan 01c-03's shape can be promoted after benchmark evidence lands. All offline.
  </action>
  <verify>
    <automated>python3 -m pytest tests/test_lora_training.py::TestVersionRegistry -q</automated>
    <automated>python3 -m pytest tests/test_lora_training.py tests/test_training_engine.py -q</automated>
  </verify>
  <done>
    promote() flips persisted records to production state post-registration, errors are typed ValueErrors, and the full register → persist → reload → promote → reload chain is proven offline.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Store JSON file → registry hydration | On-disk records cross into domain objects |
| Callers → promote/register API | Character/version keys cross into persistence |

## STRIDE Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation Plan |
|-----------|----------|-----------|----------|-------------|-----------------|
| T-01c-04a | Tampering | Corrupt/partial store content poisoning hydrated state | medium | mitigate | Atomic writes (temp + os.replace) prevent torn files; tolerant per-record parse skips unparsable entries instead of failing wholesale |
| T-01c-04b | Tampering | catalog.db cross-contamination via schema reuse | high | mitigate (by isolation) | Zero imports from asset_repository; lora_models SQL used as field contract documentation only; no migration ever executed |
| T-01c-04c | Repudiation | Duplicate registrations faking training history | low | mitigate | Idempotent (character_id, version) registration replaces in place — history cannot be padded with duplicate rows |
| T-01c-SC | Tampering | Package installs | low | accept | stdlib-only module (C-NODEP) |
</threat_model>

<verification>
1. `python3 -m pytest tests/test_lora_training.py::TestVersionRegistry -q` — all green
2. Full suite `python3 -m pytest -q` — no regressions vs baseline
3. grep-level sanity: no SchemaManager/migration invocation added anywhere under src/ (C-CATALOGDB holds)
</verification>

<success_criteria>
1. Version records durable across processes with atomic, corruption-tolerant storage isolated from catalog.db
2. promote() enables the train-v0.x → benchmark-pass → promote-v1.0 production flow
3. Registration idempotent on (character_id, version)
4. All tests pass offline; default registry behavior backward compatible
</success_criteria>

<output>
Create `.planning/phases/01c-character-training-system/01c-04-SUMMARY.md` when done.
</output>
