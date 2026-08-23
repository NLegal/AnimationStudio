# Phase 1c: Character Training System - Pattern Map

**Mapped:** 2026-08-23
**Files analyzed:** 9 (4 new source/notebook artifacts + 1 new test file + 4 modified modules)
**Analogs found:** 9 / 9 (all files have an in-repo analog; one is role-match only)

> **Correction for planner:** The orchestrator brief listed "base.py (DatasetConfig bounds)". `DatasetConfig` does **not** live in `base.py` — it lives in `src/training_engine/dataset_builder.py` L27–38. `base.py` owns `TrainingConfig`/`TrainingResult`/`TrainingBackend`; its Phase 1c change is the `dry_run: bool = False` field on `TrainingConfig` (RESEARCH Pattern 2). Both modifications are mapped below under their true owners.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `src/training_engine/scorer_adapter.py` | adapter (service) | request-response | `MockScorerProvider` in `src/training_engine/benchmark.py` + `IdentityScorer` in `src/identity_engine/scorer.py` | exact |
| `src/training_engine/version_store.py` *(name at planner discretion)* | store (persistence) | CRUD | `VersionRegistry.from_db_records` in `versioning.py` + JSON-write idiom in `dataset_builder.py` | role-match |
| `scripts/train_lora.py` | CLI orchestrator (utility) | batch/transform | `scripts/export_assets.py` (+ exit codes of `generate_phase5.py`) | exact |
| `colab/AnimationStudio_Colab_Training.ipynb` | notebook (config/workflow) | batch (operator-triggered) | `colab/AnimationStudio_Colab_Phase4.ipynb` | exact |
| `tests/test_train_lora_script.py` | test (CLI integration) | offline integration | `tests/test_training_engine.py` | exact |
| `src/training_engine/base.py` (modify) | model contracts | — | self (`TrainingConfig`, add `dry_run`) | self-analog |
| `src/training_engine/dataset_builder.py` (modify) | service (transform) | file-I/O | self (+ Kohya TOML schema in RESEARCH Code Examples) | self-analog |
| `src/training_engine/benchmark.py` (modify) | service (evaluation) | transform | self (+ weight tables in `brand_score.py` / plugins) | self-analog |
| `src/training_engine/kohya_adapter.py` (modify) | adapter (subprocess) | request-response | self (+ Flux command skeleton in RESEARCH Code Examples) | self-analog |

## Pattern Assignments

### `src/training_engine/scorer_adapter.py` (adapter, request-response) — NEW

**Analog:** `src/training_engine/benchmark.py` (protocol shape + mock reference impl) and `src/identity_engine/scorer.py` (the wrapped engine).

**Protocol to implement** (benchmark.py L88–111 — signature must match exactly):
```python
class ScorerProvider(Protocol):
    def score_identity(
        self,
        image_path: Path,
        reference_path: Optional[Path] = None,
        character_id: Optional[str] = None,
    ) -> dict[str, float]: ...
```

**Reference implementation of the protocol shape** (benchmark.py L118–141 — copy this structure; the real adapter swaps RNG delegation for `IdentityScorer.score_all`):
```python
class MockScorerProvider:
    def __init__(self, seed: int = 42) -> None:
        import random
        self._rng = random.Random(seed)

    def score_identity(self, image_path, reference_path=None, character_id=None) -> dict[str, float]:
        return {
            "dino_similarity": self._rng.uniform(0.7, 0.95),
            ...  # six fixed dimension keys
        }
```

**The engine being wrapped** (scorer.py L65–67, L82, L101–103 — constructor injection + `light` mode + plugin-name keys):
```python
def __init__(self, plugins=None, light: bool = False):
    self.plugins = plugins or self._default_plugins(light=light)
# light=True drops torch-backed DINOv2/CLIP plugins (offline-safe; A7 in RESEARCH.md)

def score_all(self, image: Image.Image, **kwargs) -> dict[str, float]:
    """Run all plugins and return a dict of {name: score}."""
    return {p.name: p.score(image, **kwargs) for p in self.plugins}
```
Key fact: returned keys are **plugin names** (`character_consistency`, `prompt_accuracy`, `color_harmony`, `facial_appeal`, `silhouette_recognizability`, `child_friendliness`, `style_consistency`) — NOT the benchmark's `_BENCHMARK_WEIGHTS` keys (benchmark.py L148–155). The adapter must remap one direction; RESEARCH recommends aligning `_BENCHMARK_WEIGHTS` onto plugin names instead (fewer moving parts). Resolve assumption A2 before coding.

**Protocol-with-name-and-weight precedent** (scorer.py L15–32 — structural template for typed seams in this repo):
```python
class ScoringPlugin(Protocol):
    name: str
    weight: float
    def score(self, image: Image.Image,
              reference: Optional[Image.Image] = None, **kwargs) -> float: ...
```

---

### `src/training_engine/version_store.py` (store, CRUD) — NEW (sidecar persistence; catalog.db untouched)

**Analog:** `src/training_engine/versioning.py` (domain semantics to persist) + `dataset_builder.py` JSON idiom. **No file-backed store exists anywhere in `src/` today** (grep confirmed: only `json.dumps` into SQLite columns in `sqlite_repo.py` and `metadata.json` writes) — this module composes two existing halves.

**Record schema to serialize/deserialize** (matches `lora_models` exactly — `src/asset_repository/migrations.py` L49–58; do NOT apply this migration to the corrupted catalog.db per locked constraint/A3):
```sql
CREATE TABLE IF NOT EXISTS lora_models (
    id TEXT PRIMARY KEY,
    character_id TEXT NOT NULL,
    version TEXT NOT NULL,
    file_path TEXT NOT NULL,
    training_config TEXT,      -- JSON string
    benchmark_scores TEXT,     -- JSON string
    trained_at TEXT NOT NULL,  -- ISO datetime
    promoted INTEGER DEFAULT 0
);
```

**Hydration pattern to copy** (versioning.py L228–261 — tolerant parse, ISO datetime, bool coercion):
```python
@staticmethod
def from_db_records(records: list[dict]) -> "VersionRegistry":
    registry = VersionRegistry()
    for rec in records:
        try:
            version = LoRAVersion.parse(rec.get("version", "v0.1"))
        except ValueError:
            continue
        trained_at = None
        if rec.get("trained_at"):
            trained_at = datetime.fromisoformat(rec["trained_at"])
        registry.register(
            character_id=rec["character_id"], version=version,
            file_path=rec.get("file_path", ""),
            training_config=rec.get("training_config"),
            benchmark_scores=rec.get("benchmark_scores"),
            trained_at=trained_at,
            promoted=bool(rec.get("promoted", False)),
        )
    return registry
```

**JSON file-write idiom to copy** (dataset_builder.py L110–114):
```python
meta_file = output_dir / "metadata.json"
meta_file.write_text(
    json.dumps(metadata, indent=2, ensure_ascii=False),
    encoding="utf-8",
)
```

**In-memory registry being persisted** (versioning.py L141–142 dict; register() L144–175): store sits behind the registry (load-on-construct, save-on-mutate seam), enforces uniqueness on `(character_id, version)` (RESEARCH Pitfall 5), and gains `promote(character_id, version)` (gap G10).

---

### `scripts/train_lora.py` (CLI orchestrator, batch/transform) — NEW

**Analog:** `scripts/export_assets.py` (closest: argparse incl. `--db`/`--states`/`--dry-run`, bootstrap, fail-fast validation) + `scripts/generate_phase5.py` (docstring header, pass/fail exit codes).

**Header + path bootstrap** (generate_phase5.py L1–16; export_assets variant at L30):
```python
#!/usr/bin/env python3
"""<purpose>.

Reproduction:
    python scripts/train_lora.py --dry-run
"""
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # phase5 L16
# export_assets L30: sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
```

**Argparse conventions** (export_assets.py L39–69):
```python
parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--db", default="catalog.db",
                    help="SQLite database path (default: catalog.db)")
parser.add_argument("--states", default="shortlisted,approved,production",
                    help="Comma list of asset states to export (...)")
parser.add_argument("--dry-run", action="store_true",
                    help="Print destinations without writing files")
args = parser.parse_args()

states = {s.strip().lower() for s in args.states.split(",") if s.strip()}
if scopes not in (...):
    raise SystemExit(f"Unknown scope '{scopes}'")   # fail-fast, non-zero exit
```

**Curated-state SQL filter precedent** (export_assets.py L89–93 — exact `state IN (...)` shape Wave 1 curation needs; prefer index-covered queries per RESEARCH Pitfall 2):
```python
rows = conn.execute(
    "SELECT id, character_id, asset_type, variant, state, file_path, prompt, seed "
    "FROM assets WHERE state IN (%s) ORDER BY character_id" % ", ".join("?" * len(states)),
    tuple(states),
).fetchall()
```
Repo-method alternative: `SQLiteAssetRepository.find_approved(character_id, asset_type)` (`src/asset_repository/sqlite_repo.py` ~L348–358, filters `state = 'approved'`) — extend/wrap for the two-state rule already used in `review_ui/app.py` L208–213: `a.get("state") in ("approved", "production")`.

**Exit-code convention** (generate_phase5.py L188, L191–192; export_assets.py L163, L166–167):
```python
return 0 if doc_report.passed and plan.passed else 1
...
if __name__ == "__main__":
    sys.exit(main())          # or sys.exit(asyncio.run(main()))
```
Subcommand surface (`build-dataset/train/benchmark/versions`) keeps single `main() -> int` + `SystemExit`-on-bad-input style; subprocess stays arg-list-only (see Shared Patterns).

---

### `colab/AnimationStudio_Colab_Training.ipynb` (notebook) — NEW

**Analog:** `colab/AnimationStudio_Colab_Phase4.ipynb` — nbformat 4, **9-cell skeleton** (verified):

| Cell | Type | Title | Content to mirror |
|------|------|-------|-------------------|
| 0 | markdown | `# AnimationStudio — Phase 4: … on Google Colab` | intro + usage notes |
| 1 | code | `#@title 1. Settings` | `#@param` fields (below) |
| 2 | code | `#@title 2. Clone repo and install the studio` | `run()` helper + full clone + `pip install -e . --no-deps` |
| 3–5 | code | preview / regenerate report / run tests | phase-specific work cells |
| 6 | code | review | display step |
| 7 | code | `#@title 7. Sync … (GitHub push or manual download)` | `git_sync._basic_auth_header` push (below) |
| 8 | markdown | `## Next steps` | operator follow-ups |

**Settings cell pattern** (Phase4 cell 1 — `#@param` forms; token stays EMPTY in committed ipynb):
```python
#@title 1. Settings
REPO_URL = "https://github.com/YOUR_ORG/AnimationStudio.git"  #@param {type:"string"}
BRANCH = "master"  #@param ["master", "colab-gpu"]
WORK = "/content"; REPO = f"{WORK}/AnimationStudio"
SYNC_TO_GITHUB = True  #@param {type:"boolean"}
GITHUB_TOKEN = ""  #@param {type:"string"}   # never commit real tokens
```
Training deltas: add `HF_TOKEN = "" #@param {type:"string"}` and VRAM-profile params.

**Clone/install cell pattern** (Phase4 cell 2):
```python
def run(cmd, **kw):
    print("+ " + " ".join(cmd))
    return subprocess.run(cmd, check=True, **kw)

os.chdir(WORK)
if not os.path.isdir(REPO):
    run(["git", "clone", "--branch", BRANCH, REPO_URL, "AnimationStudio"])
os.chdir(REPO)
run([sys.executable, "-m", "pip", "install", "-q", "-e", ".", "--no-deps"])
```
Training deltas: GPU-check cell (`nvidia-smi`, `torch.cuda.is_available()`, fail-fast), sd-scripts clone + requirements install, dataset-build cell (`python scripts/train_lora.py --build-dataset`), HF model-download cell (4 gated files), `accelerate launch flux_train_network.py` training cell (flag skeleton in RESEARCH Code Examples), sample-gen + benchmark cell.

**Sync cell pattern** (Phase4 cell 7 — reuse verbatim, extend the `git add` list):
```python
sys.path.insert(0, f"{REPO}/colab")
from git_sync import _basic_auth_header          # colab/git_sync.py L25–33
_run(["git", "-c",
      f"http.extraheader=Authorization: {_basic_auth_header(GITHUB_TOKEN)}",
      "push", "origin", BRANCH])
```
Sync additions per RESEARCH Pattern 3: `Universe/Characters/Lily Bunny/lora/*.safetensors` + benchmark report.

---

### `tests/test_train_lora_script.py` (test, offline CLI integration) — NEW

**Analog:** `tests/test_training_engine.py`.

**Conventions to copy** (line refs from that file):
- Module docstring listing coverage scope (L1–6)
- Class-per-concern grouping with banner comments: `TestTrainingConfig:` L22, `TestKohyaEnvironmentValidation:` L127, `TestKohyaCommandGeneration:` L173
- `tmp_path` fixture for all filesystem work (L136–141); fake images via `p.write_text("dummy-image-data")` (L154–156)
- Subprocess never runs for real — env-not-ready asserted via `result.success is False` + `"error" in result.metrics` (L246–256); dry-run tests monkeypatch `subprocess.run` with a sentinel (RESEARCH test map CHAR-07-b)
- Command assertions as joined-string substring checks (L232–240): `cmd_str = " ".join(cmd); assert "--learning_rate" in cmd_str`
- Imports from package root (L15): `from src.training_engine import ...` — new public classes go through `src/training_engine/__init__.py` imports + `__all__` (L14–35)
- Boundary: zero torch/network/GPU deps so the suite stays ~3.4 s / 51 green (RESEARCH Anti-Patterns)

---

### `src/training_engine/base.py` (modify) — self-analog

Add `dry_run: bool = False` to `TrainingConfig` (dataclass L20–44; follow the plain-default field style of `caption_dropout_rate: float = 0.05` at L43). Semantics per RESEARCH Pattern 2: `True` → never invoke subprocess; write config artifacts, then register the version exactly like the real path (locked decision allows dry-run registrations). Note: `DatasetConfig` min/max bounds do **not** go here — see next entry.

### `src/training_engine/dataset_builder.py` (modify) — self-analog

Touch points (verified):
- `DatasetConfig` L27–38 — ADD `min_images: int = 20` / `max_images: int = 40` (fields do not exist today; assumption A1)
- `_copy_and_caption` L126–168 — caption assembly precedent at L152–159 (prefix/caption/suffix join with `", "`) becomes the `.txt` sidecar body: trigger word first, descriptor from record prompt, survives `shuffle_caption=true` via `keep_tokens=1`. Dest naming convention `f"{i:04d}_{src.stem}{src.suffix}"` (L149) gains a sibling `{dest.stem}.txt`
- `_write_kohya_config` L170–210 — remove invalid key `caption_metadata_file` (L197) and bare `caption_prefix = ""` (L198); remove val-as-training-subset block (L204–206) in favor of native `validation_split`/`validation_seed` or val exclusion (gap G3). Target TOML shape: RESEARCH Code Examples ("Valid minimal Kohya TOML")
- Empty/below-min dataset → raise a clear error listing counts per state (RESEARCH Pitfall 1); the `warnings.warn`-and-skip idiom already exists at L146
- Curation input arrives pre-filtered from repo query — do NOT filter inside the builder (RESEARCH Anti-Patterns)

### `src/training_engine/benchmark.py` (modify) — self-analog

Touch points (verified):
- `_BENCHMARK_WEIGHTS` L148–155 — realign onto identity-engine plugin names. Candidates: D-06 plugin weights (0.40 character_consistency / 0.20 prompt_accuracy / 0.10 color_harmony / 0.10 facial_appeal / 0.05 silhouette_recognizability / 0.05 child_friendliness / 0.10 style_consistency — documented in `scorer.py` L70–73) vs `BrandScore.WEIGHTS` (`brand_score.py` L22–31, includes unscoreable `technical_quality`, capping achievable total at 0.85). Resolve A2 before coding
- `BenchmarkConfig.similarity_threshold` L40 — `0.85` → `0.90` (change default + update tests)
- `MockScorerProvider` dimension keys L134–141 — update to canonical names so determinism tests stay meaningful
- Composite math and pass gate L263–298 / L306–309 are correct as-is — reuse unchanged

### `src/training_engine/kohya_adapter.py` (modify) — self-analog

Touch points (verified):
- `train()` control flow L131–218 — insert `config.dry_run` branch after `cmd = self._build_command(config)` (L150): write `{character_id}_{version}.train_cmd.json` artifact, skip `subprocess.run` (L156–161), still run registry registration (reuse L169–188 verbatim)
- Preserve error-shape precedent: typed `TrainingResult(success=False, metrics={"error": …})` returns for `CalledProcessError` / `FileNotFoundError` (L200–218) — never raise across the ABC boundary
- `_build_command` L258–302 — keep arg-list invariant (module docstring L6–7: never `shell=True`; paths resolved); fix misleading comment L296; wrap with `accelerate launch`; add `networks.lora_flux`, `--clip_l/--t5xxl/--ae`, `--save_model_as safetensors`, fp8/cache flags, `--max_data_loader_n_workers 2`. Full flag skeleton in RESEARCH Code Examples
- `validate_environment()` L56–79 — GPU warning is advisory (comment L74–77 admits future strict flag); config-level `dry_run` supersedes it

## Shared Patterns

### Script bootstrap & CLI hygiene
**Source:** `scripts/export_assets.py` L30, L39–69; `scripts/generate_phase5.py` L16, L188–192
**Apply to:** `scripts/train_lora.py`
`sys.path.insert(0, parents[1])` → `argparse.ArgumentParser(description=__doc__, formatter_class=RawDescriptionHelpFormatter)` → comma-list parsing via set comprehension → `raise SystemExit(msg)` on invalid input → `main() -> int` + `sys.exit(main())`.

### Typed-result error handling (no exceptions across seams)
**Source:** `kohya_adapter.py` L200–218; advisory `warnings.warn` + skip in `dataset_builder.py` L146
**Apply to:** all training_engine changes and the CLI script. Advisory problems warn-and-continue; hard failures return typed results with `"error"` in metrics; only user-input errors raise (`SystemExit` / `ValueError`).

### JSON file persistence idiom
**Source:** `dataset_builder.py` L110–114 (write); `versioning.py` L228–261 (hydrate)
**Apply to:** version store, dry-run command artifact, benchmark report output. Always `json.dumps(..., indent=2, ensure_ascii=False)` + `encoding="utf-8"`; datetimes as ISO strings; tolerant skip-on-`ValueError` parse when reading back.

### Subprocess safety: arg-list only
**Source:** `kohya_adapter.py` L6–7, L156–161, L274–294; Phase4 notebook `run()` helper prints commands before executing
**Apply to:** kohya_adapter changes, `train_lora.py` if it shells out, notebook cells. Never `shell=True`; resolve paths before adding to argv.

### Protocol seam + mock-first default
**Source:** `benchmark.py` L88–141 (protocol + default `MockScorerProvider` fallback wired at L187)
**Apply to:** scorer_adapter and any new store seam. Program against protocols; tests inject mocks/fakes; heavy deps stay out of unit paths.

### Colab notebook conventions
**Source:** `colab/AnimationStudio_Colab_Phase4.ipynb` cells 1/2/7; `colab/git_sync.py` L25–33 (`_basic_auth_header`)
**Apply to:** training notebook. Numbered `#@title N.` titles, `#@param` settings with empty-token placeholders, `run()` command-printing helper, sync via `git_sync._basic_auth_header`, trailing `## Next steps` markdown.

### Package export discipline
**Source:** `src/training_engine/__init__.py` L14–35 (imports + `__all__`)
**Apply to:** after adding scorer_adapter / version store, re-export public classes here and update `__all__` — tests import from package root.

## No Analog Found

No file is fully analog-less. Two partial gaps the planner should know about:

| File | Role | Data Flow | Gap Detail |
|------|------|-----------|------------|
| `src/training_engine/version_store.py` | store | CRUD | No file-backed JSON/SQLite-sidecar store exists in-repo (grep: only SQLite-column `json.dumps` and `metadata.json` writes). Compose `from_db_records` hydration + metadata.json write idiom; schema contract comes from `migrations.py` L49–58 |
| Notebook GPU-check cell | config | — | All 5 existing notebooks target CPU runtime; no GPU-check precedent. Plain `nvidia-smi` + `torch.cuda.is_available()` fail-fast cell per RESEARCH Pattern 3 |

## Metadata

**Analog search scope:** `scripts/`, `src/training_engine/`, `src/identity_engine/`, `src/asset_repository/`, `src/review_ui/`, `colab/`, `tests/`
**Files read (full or targeted):** 14 — all 5 `training_engine` modules, `scorer.py`, `brand_score.py`, `migrations.py` (L40–64), `sqlite_repo.py` (L330–375), `review_ui/app.py` (L195–225), `generate_phase5.py`, `export_assets.py`, `test_training_engine.py`, Phase4 notebook cells 1/2/7, `git_sync.py` symbol scan, `training_engine/__init__.py`
**Searches run:** glob inventories (scripts/, tests/, templates); grep `json.dump` across src/; grep `lora_models|_schema_version|SchemaManager`; grep git_sync symbols
**Pattern extraction date:** 2026-08-23
