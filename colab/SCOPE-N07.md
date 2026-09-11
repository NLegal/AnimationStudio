# Scoping: N-07 Multi-Character Batch Training Notebook (39-Character Driver)

Scoped and executed 2026-09-11. MAJOR, lands in `colab/`.

## Why this matters

The Phase 1c training notebook drove a single `CHARACTER_ID`/`CHARACTER_TITLE`.
Training all 39 characters required editing Cell 1 and re-running the whole
multi-hour pipeline 39×, with no loop, no per-character dataset gate status,
and no registry of "pending characters".

## What was shipped

`colab/AnimationStudio_Colab_Training.ipynb` (12 cells, rebuilt from the
N-07 generator):

1. **Settings** — keeps `CHARACTER_ID`/`CHARACTER_TITLE` (back-compat) and adds
   the N-07 batch knobs: `CHARACTERS` 39-name dropdown + `"all"`, plus
   `MAX_CHARACTERS_PER_RUN` (0 = no cap), `SKIP_ALREADY_TRAINED`, and
   `SEND_AHEAD_IDS` (comma-separated slugs for partial runs).
2. **GPU check** — unchanged.
3. **Clone/install + `run()` helper** — unchanged.
4. **Model download** — unchanged (disk + size guards).
5-9. **Per-character functions** — `build_dataset`, `train_lora`,
   `benchmark_lora` (returns `(result, report_path)`), `register_promote`,
   `sync_artifacts`. Each takes the character id/title/root explicitly.
10. **Batch driver** — resolves `CHARACTERS` via `discover_characters`
    (`by_slug`/`by_name`, `"all"`), honors `SEND_AHEAD_IDS` override,
    `MAX_CHARACTERS_PER_RUN` slice, then per character: `_already_trained`
    skips when `registry.get_promoted(slug)` exists AND
    `benchmark_scores.get("passed")`, else runs
    `build_dataset → train_lora → benchmark_lora → register_promote →
    sync_artifacts`, with per-character `char_root` created.
11. **Next steps** — updated for the batch flow.

## Verification

- `TestTrainingNotebookBatchDriver` (10 tests) added to
  `tests/test_colab_notebooks.py`: CHARACTERS dropdown with `"all"` + names,
  batch knobs present, back-compat `CHARACTER_ID`/`CHARACTER_TITLE`, the five
  per-character functions defined, driver cell resolves via
  `discover_characters`, gate uses `benchmark_scores.get("passed")`, all five
  stages called, send-ahead/cap wiring, `char_root` mkdir, Next-steps mentions
  batch/CHARACTERS.
- `verify_training_n07.py`: 12 cells, **0 syntax problems**, all contract
  checks OK (including the pre-existing `TestTrainingNotebookStructure`
  strings).
- `tests/test_colab_notebooks.py` → **176 passed**.

## Remaining

None for this ticket. Real training runs need a GPU runtime, C-01-approved
curated assets (≥20/character gate), and per-character registry
`training/lora_registry.json` promotion — all operator-side on Colab.