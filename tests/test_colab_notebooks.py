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

    def test_next_steps_markdown_present(self, training_notebook):
        """The notebook closes with operator follow-up guidance."""
        markdown_cells = [
            _cell_source_text(c)
            for c in _iter_cells(training_notebook)
            if c.get("cell_type") == "markdown"
        ]
        assert any("Next steps" in md for md in markdown_cells)


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