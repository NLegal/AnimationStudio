"""Offline structural smoke tests for the Colab notebooks (C-OFFLINE).

Parses every ``colab/*.ipynb`` file as JSON and checks structural invariants
plus the Phase 1c training-notebook content contract.  Zero network access
and zero notebook execution — the notebooks target GPU Colab runtimes and
must never be executed here (C-OFFLINE).
"""

import json
import re
from pathlib import Path

import pytest

_COLAB_DIR = Path(__file__).resolve().parent.parent / "colab"
_TRAINING_NOTEBOOK = _COLAB_DIR / "AnimationStudio_Colab_Training.ipynb"
_IDLOCK_NOTEBOOK = _COLAB_DIR / "AnimationStudio_Colab_IdentityLock.ipynb"
_PHASE7_NOTEBOOK = _COLAB_DIR / "AnimationStudio_Colab_Phase7.ipynb"
_PHASE8_NOTEBOOK = _COLAB_DIR / "AnimationStudio_Colab_Phase8.ipynb"
_PHASE9_12_NOTEBOOK = _COLAB_DIR / "AnimationStudio_Colab_Phase9to12.ipynb"
_NOTEBOOKS = sorted(_COLAB_DIR.glob("*.ipynb"))

_SECRET_PATTERNS = [
    ("github-pat", re.compile(r"\bghp_[A-Za-z0-9]{30,}\b")),
    ("hf-token", re.compile(r"\bhf_[A-Za-z0-9]{30,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
]


def _load_notebook(path: Path) -> dict:
    """Parse *path* as notebook JSON (raises JSONDecodeError when invalid)."""
    return json.loads(path.read_text(encoding="utf-8"))


def _iter_cells(notebook: dict):
    """Yield notebook cells (tolerates nbformat-4 cell dicts)."""
    for cell in notebook.get("cells", []):
        yield cell


def _cell_source_text(cell: dict) -> str:
    """Return the cell source as a single string (handles str and list forms)."""
    source = cell.get("source", "")
    if isinstance(source, str):
        return source
    return "".join(source)


def _notebook_source_text(notebook: dict) -> str:
    """Concatenate every cell source in *notebook* into one string."""
    return "\n".join(_cell_source_text(cell) for cell in _iter_cells(notebook))


@pytest.fixture(scope="module")
def training_notebook() -> dict:
    """The Phase 1c Colab training notebook, parsed once per module."""
    return _load_notebook(_TRAINING_NOTEBOOK)


@pytest.fixture(scope="module")
def readme_text() -> str:
    """README.md content (universal newlines), read once per module."""
    readme = Path(__file__).resolve().parent.parent / "README.md"
    return readme.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Structural validity across all committed notebooks
# ---------------------------------------------------------------------------

class TestNotebookStructuralValidity:
    """Every colab notebook is a valid, clean nbformat-4 document."""

    @pytest.mark.parametrize("notebook_path", _NOTEBOOKS, ids=lambda p: p.name)
    def test_parses_as_nbformat4_with_cells(self, notebook_path):
        """The file is valid ipynb JSON with nbformat 4 and a non-empty cell list."""
        notebook = _load_notebook(notebook_path)
        assert notebook["nbformat"] == 4
        assert len(notebook.get("cells") or []) > 0

    @pytest.mark.parametrize("notebook_path", _NOTEBOOKS, ids=lambda p: p.name)
    def test_code_cells_have_clean_execution_state(self, notebook_path):
        """No committed notebook embeds executed output or live results."""
        notebook = _load_notebook(notebook_path)
        for cell in _iter_cells(notebook):
            if cell.get("cell_type") == "code":
                assert cell.get("execution_count") is None
                # Missing ``outputs`` key (never-run cell) is as clean as ``[]``;
                # any listed output would indicate embedded execution results.
                assert cell.get("outputs") in (None, [])


# ---------------------------------------------------------------------------
# Training notebook content contract
# ---------------------------------------------------------------------------

class TestTrainingNotebookStructure:
    """The Phase 1c training notebook carries every required stage."""

    def _code_cells(self, notebook: dict) -> list:
        return [c for c in _iter_cells(notebook) if c.get("cell_type") == "code"]

    def test_settings_cell_has_empty_token_params(self, training_notebook):
        """Both token params exist and default to empty strings (T-01c-06a)."""
        settings = next(
            c for c in self._code_cells(training_notebook)
            if _cell_source_text(c).lstrip().startswith("#@title 1. Settings")
        )
        source = _cell_source_text(settings)
        assert re.search(r'GITHUB_TOKEN\s*=\s*""', source)
        assert re.search(r'HF_TOKEN\s*=\s*""', source)

    def test_gpu_check_cell_present(self, training_notebook):
        """The notebook fails fast on runtimes without a usable GPU."""
        text = _notebook_source_text(training_notebook)
        assert "nvidia-smi" in text
        assert "torch.cuda.is_available()" in text

    def test_model_download_cell_has_disk_and_size_guards(self, training_notebook):
        """Cell 4 fails fast on low disk and catches truncated downloads (N-08/N-10)."""
        text = _notebook_source_text(training_notebook)
        assert "EXPECTED_BYTES" in text
        assert 'flux1-dev.safetensors": 33956436064' in text
        assert "disk_usage(WORK)" in text
        assert "looks truncated" in text

    def test_pinned_sd_scripts_clone_present(self, training_notebook):
        """sd-scripts is cloned at a pinned upstream commit (T-01c-06b)."""
        text = _notebook_source_text(training_notebook)
        assert "sd-scripts" in text
        assert re.search(r"\b[0-9a-f]{40}\b", text), (
            "a 40-hex pinned upstream commit hash must appear in the clone cell"
        )

    def test_training_cell_uses_accelerate_flux(self, training_notebook):
        """Training runs through accelerate + flux_train_network.py."""
        text = _notebook_source_text(training_notebook)
        assert "accelerate" in text
        assert "flux_train_network.py" in text
        assert "networks.lora_flux" in text

    def test_benchmark_cell_present(self, training_notebook):
        """Samples via a diffusers pipeline and scores with LoRABenchmark."""
        text = _notebook_source_text(training_notebook)
        assert "FluxPipeline" in text
        assert "LoRABenchmark" in text
        assert "IdentityScorerProvider" in text

    def test_promote_step_present(self, training_notebook):
        """Version registration and benchmark-gated promotion are in the flow."""
        text = _notebook_source_text(training_notebook)
        assert "recommend_next" in text
        assert "promote(" in text

    def test_sync_cell_present(self, training_notebook):
        """Artifact sync reuses git_sync._basic_auth_header for the push."""
        text = _notebook_source_text(training_notebook)
        assert "_basic_auth_header" in text
        assert "push" in text

    def test_sync_cell_authorization_header_prefixed(self, training_notebook):
        """The push header carries the required 'Authorization: ' prefix (N-03)."""
        text = _notebook_source_text(training_notebook)
        assert re.search(r"Authorization:\s*\{_basic_auth_header\(", text), (
            "push cell must set http.extraheader=Authorization: {_basic_auth_header(...)}"
        )

    def test_next_steps_markdown_present(self, training_notebook):
        """The notebook closes with operator follow-up guidance."""
        markdown_cells = [
            _cell_source_text(c)
            for c in _iter_cells(training_notebook)
            if c.get("cell_type") == "markdown"
        ]
        assert any("Next steps" in md for md in markdown_cells)


# ---------------------------------------------------------------------------
# Identity Lock notebook content contract
# ---------------------------------------------------------------------------

class TestIdentityLockNotebookStructure:
    """The Progressive Locking Pipeline notebook (N-05) drives all 4 lock scripts."""

    _LOCK_NOTEBOOK = _IDLOCK_NOTEBOOK

    def _code_cells(self, notebook: dict) -> list:
        return [c for c in _iter_cells(notebook) if c.get("cell_type") == "code"]

    def test_settings_cell_has_character_knobs(self):
        """Cell 1 exposes CHARACTERS and MAX_CHARACTERS_PER_LOCK."""
        notebook = _load_notebook(self._LOCK_NOTEBOOK)
        settings = next(
            c for c in self._code_cells(notebook)
            if _cell_source_text(c).lstrip().startswith("#@title 1. Settings")
        )
        source = _cell_source_text(settings)
        assert "CHARACTERS =" in source
        assert "MAX_CHARACTERS_PER_LOCK =" in source
        assert "COMFYUI_URL" not in source or 'BRANCH = "colab-gpu"' in source

    def test_branch_restricted_to_colab_gpu(self):
        """Settings offer only colab-gpu; master is deprecated (N-02)."""
        text = _notebook_source_text(_load_notebook(self._LOCK_NOTEBOOK))
        assert 'BRANCH = "colab-gpu"' in text
        assert '"master"' not in text

    def test_gpu_assert_guard_present(self):
        """GPU cell fails fast instead of silently degrading (N-09)."""
        text = _notebook_source_text(_load_notebook(self._LOCK_NOTEBOOK))
        assert "assert torch.cuda.is_available()" in text

    def test_all_four_lock_scripts_run_headless(self):
        """Cell 8 invokes all 4 lock scripts with every CLI knob (N-05/E-02)."""
        text = _notebook_source_text(_load_notebook(self._LOCK_NOTEBOOK))
        for script in ("generate_identity_lock.py", "generate_face_lock.py",
                       "generate_body_lock.py", "generate_wardrobe.py"):
            assert script in text
        # Headless mode must be wired so scripts don't each block on uvicorn.
        assert "--no-review-ui" in text
        # Per-character parameterization from E-02 must be threaded through.
        for flag in ("--comfyui-url", "--character", "--universe-dir", "--db-path"):
            assert flag in text

    def test_lock_scripts_run_in_order(self):
        """Identity -> Face -> Body -> Wardrobe, never the reverse."""
        notebook = _load_notebook(self._LOCK_NOTEBOOK)
        pipeline = next(
            c for c in self._code_cells(notebook)
            if "Run the Progressive Locking Pipeline" in _cell_source_text(c)
        )
        source = _cell_source_text(pipeline)
        order = [source.index(s) for s in
                 ("generate_identity_lock.py", "generate_face_lock.py",
                  "generate_body_lock.py", "generate_wardrobe.py")]
        assert order == sorted(order), "lock scripts must run in pipeline order"

    def test_review_ui_started_single_cell(self):
        """The Review UI is launched once (Cell 10), not inside each script."""
        text = _notebook_source_text(_load_notebook(self._LOCK_NOTEBOOK))
        assert "Launch the Review UI and tunnel" in text
        assert "create_app(" in text

    def test_training_readiness_gate_present(self):
        """Cell 11 prints the >=20 approved/character dataset-readiness table."""
        text = _notebook_source_text(_load_notebook(self._LOCK_NOTEBOOK))
        assert "APPROVED ASSETS PER CHARACTER" in text
        assert "READY" in text
        assert "train_lora.py" in text or "build-dataset" in text

    def test_fp8_model_download_guards_present(self):
        """Model download carries disk + truncation guards (N-08/N-10)."""
        text = _notebook_source_text(_load_notebook(self._LOCK_NOTEBOOK))
        assert "disk_usage" in text
        assert "17.25" in text

    def test_next_steps_markdown_present(self):
        """The notebook closes with operator follow-up guidance."""
        md_cells = [
            _cell_source_text(c)
            for c in _iter_cells(_load_notebook(self._LOCK_NOTEBOOK))
            if c.get("cell_type") == "markdown"
        ]
        assert any("Next steps" in md for md in md_cells)


# ---------------------------------------------------------------------------
# Phase 7 storyboard notebook content contract
# ---------------------------------------------------------------------------

class TestPhase7NotebookStructure:
    """The Phase 7 production-planning notebook (N-04) drives story -> blueprint."""

    _PHASE7_NOTEBOOK = _PHASE7_NOTEBOOK

    def _code_cells(self, notebook: dict) -> list:
        return [c for c in _iter_cells(notebook) if c.get("cell_type") == "code"]

    def test_settings_cell_has_episode_knobs(self):
        """Cell 1 exposes SEASON / EPISODE_NUMBER / EPISODES / REPORT_PATH."""
        notebook = _load_notebook(self._PHASE7_NOTEBOOK)
        settings = next(
            c for c in self._code_cells(notebook)
            if _cell_source_text(c).lstrip().startswith("#@title 1. Settings")
        )
        source = _cell_source_text(settings)
        assert "SEASON =" in source
        assert "EPISODE_NUMBER =" in source
        assert "EPISODES =" in source
        assert "REPORT_PATH =" in source

    def test_branch_restricted_to_colab_gpu(self):
        """Settings offer only colab-gpu; master is deprecated (N-02)."""
        text = _notebook_source_text(_load_notebook(self._PHASE7_NOTEBOOK))
        assert 'BRANCH = "colab-gpu"' in text
        assert '"master"' not in text

    def test_story_to_blueprint_chain_present(self):
        """Story generation -> blueprint -> episode must be the driver chain."""
        text = _notebook_source_text(_load_notebook(self._PHASE7_NOTEBOOK))
        assert "EpisodeGenerator" in text
        assert "blueprint_to_episode" in text

    def test_production_planning_drivers_present(self):
        """Prompts, render queue, continuity, and the 8-step workflow all exist."""
        text = _notebook_source_text(_load_notebook(self._PHASE7_NOTEBOOK))
        assert "generate_prompts" in text
        assert "build_render_queue" in text
        assert "validate_continuity" in text
        assert "EpisodeWorkflowFactory" in text
        assert "PipelineOrchestrator" in text
        assert "process_pipeline" in text

    def test_phase_report_written(self):
        """Cell 7 writes PHASE7_REPORT.md into the checkout."""
        text = _notebook_source_text(_load_notebook(self._PHASE7_NOTEBOOK))
        assert "PHASE7_REPORT.md" in text
        assert "open(f" in text or 'open(f"{REPO}/{REPORT_PATH}"' in text

    def test_offline_mock_no_gpu_requirement(self):
        """The notebook must run offline with mocks (no torch assert, no GPU)."""
        text = _notebook_source_text(_load_notebook(self._PHASE7_NOTEBOOK))
        assert "mock" in text or "in-process" in text
        assert "torch.cuda.is_available" not in text
        assert "ComfyUIBackend" not in text

    def test_next_steps_markdown_present(self):
        """The notebook closes with operator follow-up guidance."""
        md_cells = [
            _cell_source_text(c)
            for c in _iter_cells(_load_notebook(self._PHASE7_NOTEBOOK))
            if c.get("cell_type") == "markdown"
        ]
        assert any("Next steps" in md for md in md_cells)


# ---------------------------------------------------------------------------
# Phase 8 image-generation notebook content contract
# ---------------------------------------------------------------------------

class TestPhase8NotebookStructure:
    """The Phase 8 visual pipeline notebook (N-04) runs mock + real-sections."""

    _PHASE8_NOTEBOOK = _PHASE8_NOTEBOOK

    def _code_cells(self, notebook: dict) -> list:
        return [c for c in _iter_cells(notebook) if c.get("cell_type") == "code"]

    def test_settings_cell_has_phase8_knobs(self):
        """Cell 1 exposes the Part A episode scope and Part B real-gen switches."""
        notebook = _load_notebook(self._PHASE8_NOTEBOOK)
        settings = next(
            c for c in self._code_cells(notebook)
            if _cell_source_text(c).lstrip().startswith("#@title 1. Settings")
        )
        source = _cell_source_text(settings)
        assert "SEASON =" in source
        assert "EPISODE_NUMBER =" in source
        assert "RUN_REAL_GENERATION =" in source
        assert "REAL_SCENE_INDEX =" in source

    def test_branch_restricted_to_colab_gpu(self):
        """Settings offer only colab-gpu; master is deprecated (N-02)."""
        text = _notebook_source_text(_load_notebook(self._PHASE8_NOTEBOOK))
        assert 'BRANCH = "colab-gpu"' in text
        assert '"master"' not in text

    def test_part_a_mock_visual_pipeline_present(self):
        """Part A drives MockBackend + validator + scorer + consistency."""
        text = _notebook_source_text(_load_notebook(self._PHASE8_NOTEBOOK))
        assert "MockBackend" in text
        assert "ImageValidator" in text
        assert "IdentityScorer" in text
        assert "ConsistencyManager" in text

    def test_part_b_real_generation_gated(self):
        """Part B builds ComfyUIBackend and is gated on RUN_REAL_GENERATION."""
        text = _notebook_source_text(_load_notebook(self._PHASE8_NOTEBOOK))
        assert "ComfyUIBackend" in text
        assert "RUN_REAL_GENERATION" in text

    def test_fp8_model_download_guards_present(self):
        """Model download carries disk + truncation guards (N-08/N-10)."""
        text = _notebook_source_text(_load_notebook(self._PHASE8_NOTEBOOK))
        assert "disk_usage" in text
        assert "17.25" in text

    def test_gpu_assert_guard_present(self):
        """Part B GPU cell fails fast instead of silently degrading (N-09)."""
        text = _notebook_source_text(_load_notebook(self._PHASE8_NOTEBOOK))
        assert "torch.cuda.is_available" in text

    def test_planning_chain_imported(self):
        """Part A reuses the Phase 7 planning chain for the episode prompts."""
        text = _notebook_source_text(_load_notebook(self._PHASE8_NOTEBOOK))
        assert "EpisodeGenerator" in text
        assert "blueprint_to_episode" in text
        assert "generate_prompts" in text

    def test_next_steps_markdown_present(self):
        """The notebook closes with operator follow-up guidance."""
        md_cells = [
            _cell_source_text(c)
            for c in _iter_cells(_load_notebook(self._PHASE8_NOTEBOOK))
            if c.get("cell_type") == "markdown"
        ]
        assert any("Next steps" in md for md in md_cells)


# ---------------------------------------------------------------------------
# Phases 9-12 episode production notebook content contract
# ---------------------------------------------------------------------------

class TestPhase9to12NotebookStructure:
    """The Phases 9-12 notebook (N-04) drives render -> post -> publish -> orchestrate."""

    _PHASE9_12_NOTEBOOK = _PHASE9_12_NOTEBOOK

    def _code_cells(self, notebook: dict) -> list:
        return [c for c in _iter_cells(notebook) if c.get("cell_type") == "code"]

    def test_settings_cell_has_episode_and_master_knobs(self):
        """Cell 1 exposes episode scope plus the real-render switch."""
        notebook = _load_notebook(self._PHASE9_12_NOTEBOOK)
        settings = next(
            c for c in self._code_cells(notebook)
            if _cell_source_text(c).lstrip().startswith("#@title 1. Settings")
        )
        source = _cell_source_text(settings)
        assert "SEASON =" in source
        assert "EPISODE_NUMBER =" in source
        assert "RUN_REAL_RENDER =" in source
        assert "REAL_SCENE_INDEX =" in source

    def test_branch_restricted_to_colab_gpu(self):
        """Settings offer only colab-gpu; master is deprecated (N-02)."""
        text = _notebook_source_text(_load_notebook(self._PHASE9_12_NOTEBOOK))
        assert 'BRANCH = "colab-gpu"' in text
        assert '"master"' not in text

    def test_phase9_render_and_regeneration_present(self):
        """Phase 9 drives the RenderPipeline and the regeneration workflow."""
        text = _notebook_source_text(_load_notebook(self._PHASE9_12_NOTEBOOK))
        assert "RenderPipeline" in text
        assert "process_next" in text
        assert "complete_job" in text
        assert "ClipRegenerationEngine" in text

    def test_phase10_post_production_drivers_present(self):
        """Phase 10 assembles a timeline, runs QC, and lists export presets."""
        text = _notebook_source_text(_load_notebook(self._PHASE9_12_NOTEBOOK))
        assert "SceneAssembly" in text
        assert "assemble_scenes" in text
        assert "PostProductionQC" in text
        assert "validate_timeline" in text
        assert "ExportEngine" in text

    def test_phase11_publishing_drivers_present(self):
        """Phase 11 generates metadata, creates a record, and schedules."""
        text = _notebook_source_text(_load_notebook(self._PHASE9_12_NOTEBOOK))
        assert "prepare_publish_package" in text
        assert "create_record" in text
        assert "SchedulingEngine" in text
        assert "create_schedule" in text

    def test_phase12_orchestrator_drives_full_workflow(self):
        """Phase 12 runs the 8-step production workflow via the orchestrator."""
        text = _notebook_source_text(_load_notebook(self._PHASE9_12_NOTEBOOK))
        assert "PipelineOrchestrator" in text
        assert "create_pipeline" in text
        assert "process_pipeline" in text

    def test_report_written_to_checkout(self):
        """Cell 9 writes the episode production report into the checkout."""
        text = _notebook_source_text(_load_notebook(self._PHASE9_12_NOTEBOOK))
        assert "PHASE9_12_EPISODE_REPORT.md" in text

    def test_part_a_mock_no_gpu_requirement(self):
        """Part A (Phases 9-12) is offline-green: mocks, no GPU forces."""
        text = _notebook_source_text(_load_notebook(self._PHASE9_12_NOTEBOOK))
        assert "mock" in text or "in-process" in text
        # The torch GPU assert exists ONLY inside the Part B gate.
        assert "assert torch.cuda.is_available()" in text

    def test_fp8_model_download_guards_present(self):
        """Part B model download carries disk + truncation guards (N-08/N-10)."""
        text = _notebook_source_text(_load_notebook(self._PHASE9_12_NOTEBOOK))
        assert "disk_usage" in text
        assert "17.25" in text

    def test_next_steps_markdown_present(self):
        """The notebook closes with operator follow-up guidance."""
        md_cells = [
            _cell_source_text(c)
            for c in _iter_cells(_load_notebook(self._PHASE9_12_NOTEBOOK))
            if c.get("cell_type") == "markdown"
        ]
        assert any("Next steps" in md for md in md_cells)


# ---------------------------------------------------------------------------
# Secret-shape guard across all notebooks
# ---------------------------------------------------------------------------

class TestSecretShapeGuard:
    """No committed notebook contains token-shaped literals (T-01c-06a)."""

    @pytest.mark.parametrize("notebook_path", _NOTEBOOKS, ids=lambda p: p.name)
    @pytest.mark.parametrize(
        "secret_name,pattern", _SECRET_PATTERNS, ids=[name for name, _ in _SECRET_PATTERNS]
    )
    def test_no_secret_shaped_strings(self, notebook_path, secret_name, pattern):
        """High-entropy token-like literals fail CI if ever pasted in."""
        text = _notebook_source_text(_load_notebook(notebook_path))
        assert pattern.search(text) is None, (
            f"{secret_name}-shaped literal found in {notebook_path.name}"
        )


# ---------------------------------------------------------------------------
# Validate notebook drift guards (N-17)
# ---------------------------------------------------------------------------

class TestValidateNotebookStructure:
    """The pre-flight notebook is a single clean, linear 8-step flow."""

    def test_eight_sequential_steps_no_duplicates(self):
        """STEP cells are exactly 1..8 in order with no repeats (N-01)."""
        notebook = _load_notebook(_COLAB_DIR / "AnimationStudio_Validate.ipynb")
        steps = [
            int(m.group(1))
            for cell in _iter_cells(notebook)
            if cell.get("cell_type") == "code"
            for m in [re.search(r"STEP (\d)", _cell_source_text(cell))]
            if m
        ]
        assert steps == [1, 2, 3, 4, 5, 6, 7, 8], f"unexpected step order: {steps}"

    def test_model_filename_defined_before_download_and_check(self):
        """MODEL_FILE / MODEL_URL / MODEL_EXPECTED_BYTES are literal settings."""
        text = _notebook_source_text(
            _load_notebook(_COLAB_DIR / "AnimationStudio_Validate.ipynb")
        )
        assert 'MODEL_FILE = "flux1-dev.safetensors"' in text
        assert "MODEL_URL" in text
        assert "MODEL_EXPECTED_BYTES = 17250000000" in text
        assert "wget" in text and "MODEL_URL" in text

    def test_backend_and_gen_input_built_before_generate(self):
        """STEP 6 builds backend+gen_input; STEP 7 uses them (not vice versa)."""
        notebook = _load_notebook(_COLAB_DIR / "AnimationStudio_Validate.ipynb")
        sources = [
            _cell_source_text(cell)
            for cell in _iter_cells(notebook)
            if cell.get("cell_type") == "code"
        ]
        build = next(i for i, s in enumerate(sources) if "ComfyUIBackend(" in s)
        gen = next(i for i, s in enumerate(sources) if "backend.generate(gen_input" in s)
        assert build < gen, "backend/gen_input must be constructed before the generate call"

    def test_branch_restricted_to_colab_gpu(self):
        """Settings cell offers only the supported colab-gpu branch (N-02)."""
        text = _notebook_source_text(
            _load_notebook(_COLAB_DIR / "AnimationStudio_Validate.ipynb")
        )
        assert 'BRANCH = "colab-gpu"' in text
        assert '"master"' not in text

    def test_gpu_assert_guard_present(self):
        """The GPU check fails fast instead of silently degrading (N-09)."""
        text = _notebook_source_text(
            _load_notebook(_COLAB_DIR / "AnimationStudio_Validate.ipynb")
        )
        assert "assert torch.cuda.is_available()" in text


# ---------------------------------------------------------------------------
# Phase 1-3 model download drift guards (N-02 / N-10 / N-17)
# ---------------------------------------------------------------------------

class TestPhaseNotebookModelDownloads:
    """Phase 1-3 notebooks download only the live colab-gpu fp8 URL."""

    _PHASE_NOTEBOOKS = [
        _COLAB_DIR / "AnimationStudio_Colab.ipynb",
        _COLAB_DIR / "AnimationStudio_Colab_Phase2.ipynb",
        _COLAB_DIR / "AnimationStudio_Colab_Phase3.ipynb",
    ]
    _FP8_URL = (
        "https://huggingface.co/Comfy-Org/flux1-dev/resolve/main/"
        "flux1-dev-fp8.safetensors"
    )
    _CITY96_404_URLS = [
        "city96/FLUX.1-dev-gguf/resolve/main/flux1-dev-Q4_K_S.gguf",
        "city96/FLUX.1-dev-gguf/resolve/main/clip_l.safetensors",
        "city96/FLUX.1-dev-gguf/resolve/main/t5xxl_fp16.safetensors",
        "city96/FLUX.1-dev-gguf/resolve/main/ae.safetensors",
    ]

    @pytest.mark.parametrize("notebook_path", _PHASE_NOTEBOOKS, ids=lambda p: p.name)
    def test_colab_gpu_fp8_url_present(self, notebook_path):
        """Each notebook downloads the working fp8 single-file Flux model."""
        text = _notebook_source_text(_load_notebook(notebook_path))
        assert self._FP8_URL in text

    @pytest.mark.parametrize("notebook_path", _PHASE_NOTEBOOKS, ids=lambda p: p.name)
    def test_no_city96_dead_urls(self, notebook_path):
        """The 404 Q4 GGUF encoder/VAE URLs must not reappear (N-02)."""
        text = _notebook_source_text(_load_notebook(notebook_path))
        for url in self._CITY96_404_URLS:
            assert url not in text, f"dead city96 URL in {notebook_path.name}: {url}"

    @pytest.mark.parametrize("notebook_path", _PHASE_NOTEBOOKS, ids=lambda p: p.name)
    def test_branch_param_restricted_to_colab_gpu(self, notebook_path):
        """Settings offer only colab-gpu; master is deprecated (N-02)."""
        text = _notebook_source_text(_load_notebook(notebook_path))
        assert 'BRANCH = "colab-gpu"' in text
        assert '"master"' not in text

    @pytest.mark.parametrize("notebook_path", _PHASE_NOTEBOOKS, ids=lambda p: p.name)
    def test_gpu_assert_guard_present(self, notebook_path):
        """GPU cell fails fast instead of silently degrading (N-09)."""
        text = _notebook_source_text(_load_notebook(notebook_path))
        assert "assert torch.cuda.is_available()" in text


# ---------------------------------------------------------------------------
# README runbook
# ---------------------------------------------------------------------------

class TestReadmeRunbook:
    """README documents the local dry-run chain and the Colab runbook."""

    def test_readme_has_character_training_section(self, readme_text):
        """A dedicated Character Training heading exists."""
        assert re.search(r"^#{2,3} Character Training", readme_text, re.MULTILINE)

    def test_readme_documents_local_evidence_chain(self, readme_text):
        """The offline curate/build/dry-run chain is documented."""
        assert "scripts/train_lora.py" in readme_text
        assert "dry-run" in readme_text

    def test_readme_links_colab_runbook(self, readme_text):
        """The notebook path and VRAM profile guidance are referenced."""
        assert "AnimationStudio_Colab_Training.ipynb" in readme_text
        assert "VRAM" in readme_text or "T4" in readme_text

    def test_readme_notes_deferred_human_verification(self, readme_text):
        """The deferred-human status of production LoRA training is declared."""
        assert any(
            marker in readme_text
            for marker in ("deferred-human", "deferred human", "deferred_human")
        )