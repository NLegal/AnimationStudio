# Scoping: N-06 Cloud-Backend Generation Notebook (fal/replicate/bfl)

Scoped and executed 2026-09-11. MAJOR, lands in `colab/`.

## Why this matters

Every image-generation notebook was ComfyUI-only — there was no notebook path
for `--backend cloud --provider fal|replicate|bfl`, even though:

- the phase CLI scripts already default to those providers,
- cloud backends need no 17 GB fp8 Flux download and no GPU runtime,
- the free-tier T4 cannot scale: ~2 min/image → the full 12,472-asset Phase
  1–3 library would take ~17 days on a free T4. Cloud is the only realistic
  path to generating the complete library.

## What was shipped

`colab/AnimationStudio_Colab_Cloud.ipynb` (10 cells):

1. **Settings** — `REPO_URL`, `BRANCH='colab-gpu'` (only supported branch),
   `CLOUD_PROVIDER` (`fal|replicate|bfl`), `PERSIST_IMAGES`,
   `SYNC_EVERY`, `SYNC_EVERY_IMAGE`, `LIMIT` (0 = full scope), `DRY_RUN`.
2. **Clone + install** — minimal deps (`requests`, `Pillow`, `pydantic`),
   imports `CloudAPIBackend` + `git_sync.auto_sync`; defines `_gen_cmd`/`_run_gen`.
3. **Secrets** — `FAL_API_KEY`/`REPLICATE_API_KEY`/`BFL_API_KEY` + GitHub PAT
   entered at runtime via `getpass` (never persisted), key validated through
   `CloudAPIBackend.load_model()`.
4-6. **Phase 1/2/3 generation** — each gate on `DRY_RUN`, then invoke
   `generate_phase1_library.py` / `generate_phase2_world.py` /
   `generate_phase3_assets.py` with `--backend cloud --provider {p}
   --persist-images --sync-every {N} --sync-every-image --sync-branch
   colab-gpu --sync-token {PAT} --sync-remote-url {REPO_URL}`.
   Per-image sync means a Colab termination loses at most one in-flight image.
7. **Validate** — `scripts/verify_catalog.py --db` integrity check.
8. **Final sync** — `git_sync.auto_sync` safety net for stragglers.
9. **Next steps** — Review UI approval → LoRA dataset → training notebook.

## Verification

- `TestCloudNotebookStructure` (10 tests) added to `tests/test_colab_notebooks.py`:
  settings knobs, colab-gpu-only branch, all three providers, getpass secrets,
  CloudAPIBackend import, correct phase script names + `--backend cloud`
  flags, `DRY_RUN` gate, no GPU requirement, verify + auto_sync cells,
  Next-steps markdown.
- `tests/test_colab_notebooks.py` → **166 passed**.
- All cells `ast.parse` clean (no IPython `!` magic); `_gen_cmd` output
  flag-checked against every phase script's `argparse` definitions.
- Settings cell executes offline (`DRY_RUN` path).

## Remaining

None for this ticket. Cloud runs themselves need API keys (pay-per-image,
≈$0.01–0.03/image on fal/Replicate Flux).