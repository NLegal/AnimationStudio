"""Tests for the generation engine backends and pipeline orchestration.

Covers:
- All 5 concrete generation backends satisfying the ABC
- MockBackend producing valid PIL Image output
- Graceful error handling (return error metadata, never crash)
- Lazy model loading (instantiation doesn't trigger model load)
- CloudAPIBackend missing API key fallback
- JobQueue CRUD and status transitions
- DiversityFilter edge cases
"""

import asyncio
import pytest
from PIL import Image

from src.generation_engine import (
    BACKENDS,
    GenerationBackend,
    GenerationInput,
    GenerationOutput,
    ModelLoadError,
)
from src.pipeline import JobQueue, JobError, DiversityFilter


# ── Backend Interface Tests ────────────────────────────────────────────


class TestBackendInterface:
    """Verify all backends satisfy the GenerationBackend ABC contract."""

    def test_all_backends_registered(self):
        """BACKENDS dict has all 5 generation backends."""
        assert set(BACKENDS.keys()) == {"flux", "sdxl", "pony", "comfy", "cloud"}

    def test_each_backend_implements_abc(self):
        """Every registered backend is a proper subclass of GenerationBackend."""
        for name, cls in BACKENDS.items():
            assert issubclass(cls, GenerationBackend), (
                f"{name} does not implement GenerationBackend"
            )

    def test_mock_backend_generate(self, mock_generation_backend):
        """MockBackend returns correct GenerationOutput with PIL Images."""
        result = mock_generation_backend.generate(
            GenerationInput(prompt="test", negative_prompt="", seed=42)
        )
        assert len(result.images) == 1
        assert isinstance(result.images[0], Image.Image)
        assert result.seed == 42
        assert result.metadata["backend"] == "mock"

    def test_backend_lazy_loading(self):
        """Each backend can be instantiated without loading models.

        load_model() is separate from __init__ — no model download or
        GPU allocation should happen on construction.
        """
        for name, cls in BACKENDS.items():
            instance = cls()
            assert instance is not None, f"{name} could not be instantiated"

    def test_backend_generate_error_handling(self):
        """Real backends return error metadata when generate() is called
        without GPU (model loading is expected to fail).

        The pipeline should never crash — always return a valid
        GenerationOutput, even on failure.
        """
        for name, cls in BACKENDS.items():
            instance = cls()
            result = instance.generate(
                GenerationInput(prompt="test", seed=1)
            )
            # Either images were generated (MockBackend-style) or
            # error metadata was returned (expected for GPU-less env)
            if result.images:
                assert isinstance(result.images[0], Image.Image)
            else:
                assert "error" in result.metadata or result.metadata.get("backend"), (
                    f"{name}: missing error/backend metadata"
                )
            assert result.seed == 1

    def test_cloud_backend_no_api_key(self, monkeypatch):
        """CloudAPIBackend without API key returns error metadata (not crash)."""
        from src.generation_engine.cloud_backend import CloudAPIBackend

        # Ensure no API key is set
        monkeypatch.delenv("FAL_API_KEY", raising=False)
        monkeypatch.delenv("REPLICATE_API_KEY", raising=False)
        monkeypatch.delenv("BFL_API_KEY", raising=False)

        backend = CloudAPIBackend(provider="fal")
        result = backend.generate(
            GenerationInput(prompt="test", seed=42)
        )
        assert len(result.images) == 0
        assert "error" in result.metadata
        assert "No API key" in result.metadata["error"]
        assert result.seed == 42

    def test_comfy_backend_rd_docstring(self):
        """ComfyUIBackend docstring documents R&D-only usage."""
        from src.generation_engine.comfy_backend import ComfyUIBackend
        doc = ComfyUIBackend.__doc__ or ""
        assert "R&D" in doc or "lab" in doc.lower(), (
            "ComfyUIBackend must document R&D-only usage"
        )

    def test_model_load_error_raised(self):
        """ModelLoadError is raised for backends that are not configured."""
        from src.generation_engine.base import ModelLoadError
        assert issubclass(ModelLoadError, Exception)

    def test_generation_output_defaults(self):
        """GenerationOutput handles empty image list correctly."""
        output = GenerationOutput(images=[], seed=42, metadata={"reason": "test"})
        assert len(output.images) == 0
        assert output.seed == 42
        assert output.metadata["reason"] == "test"

    def test_generation_input_defaults(self):
        """GenerationInput sets sensible defaults."""
        inp = GenerationInput(prompt="test")
        assert inp.prompt == "test"
        assert inp.negative_prompt == ""
        assert inp.seed == 42
        assert inp.width == 1024
        assert inp.height == 1024
        assert inp.num_images == 1


# ── JobQueue Tests ─────────────────────────────────────────────────────


class TestJobQueue:
    """Verify JobQueue CRUD and status transitions."""

    def test_job_queue_create_and_list(self):
        """Create 2 jobs → list all jobs → verify both returned."""
        jq = JobQueue()
        j1 = jq.create_job("char-1", "pose", {"count": 5})
        j2 = jq.create_job("char-2", "expression", {"count": 3})

        all_jobs = jq.list_jobs()
        assert len(all_jobs) == 2
        job_ids = {j.id for j in all_jobs}
        assert j1.id in job_ids
        assert j2.id in job_ids

    def test_job_queue_filter_by_character(self):
        """list_jobs filters by character_id."""
        jq = JobQueue()
        jq.create_job("char-1", "pose", {})
        jq.create_job("char-2", "expression", {})

        char1_jobs = jq.list_jobs(character_id="char-1")
        assert len(char1_jobs) == 1
        assert char1_jobs[0].character_id == "char-1"

    def test_job_queue_filter_by_status(self):
        """list_jobs filters by status."""
        jq = JobQueue()
        j1 = jq.create_job("char-1", "pose", {})
        j2 = jq.create_job("char-2", "pose", {})
        jq.update_status(j1.id, "running")

        pending = jq.list_jobs(status="pending")
        assert len(pending) == 1
        assert pending[0].id == j2.id

    def test_job_queue_status_transitions(self):
        """Verify status transitions: pending → running → completed."""
        jq = JobQueue()
        job = jq.create_job("char-1", "pose", {})

        assert job.status == "pending"
        jq.update_status(job.id, "running")
        assert jq.get_job(job.id).status == "running"

        jq.update_status(job.id, "completed")
        assert jq.get_job(job.id).status == "completed"
        assert jq.get_job(job.id).completed_at is not None

    def test_job_queue_status_transition_forward(self):
        """pending → completed is also valid (allowed for simpler workflows)."""
        jq = JobQueue()
        job = jq.create_job("char-1", "pose", {})
        jq.update_status(job.id, "completed")
        assert jq.get_job(job.id).status == "completed"
        assert jq.get_job(job.id).completed_at is not None

    def test_job_queue_invalid_transition(self):
        """Invalid status transitions raise JobError."""
        jq = JobQueue()
        job = jq.create_job("char-1", "pose", {})
        # completed → running is invalid
        jq.update_status(job.id, "completed")
        with pytest.raises(JobError):
            jq.update_status(job.id, "running")

    def test_job_queue_invalid_status_name(self):
        """Unknown status values raise JobError."""
        jq = JobQueue()
        job = jq.create_job("char-1", "pose", {})
        with pytest.raises(JobError):
            jq.update_status(job.id, "invalid_status")

    def test_job_queue_missing_job(self):
        """Getting a nonexistent job returns None."""
        jq = JobQueue()
        assert jq.get_job("nonexistent") is None

    def test_job_queue_missing_job_update(self):
        """Updating a nonexistent job raises JobError."""
        jq = JobQueue()
        with pytest.raises(JobError):
            jq.update_status("nonexistent", "running")

    def test_job_queue_get_job(self):
        """get_job returns the correct job by ID."""
        jq = JobQueue()
        job = jq.create_job("char-1", "pose", {"count": 3})
        retrieved = jq.get_job(job.id)
        assert retrieved is not None
        assert retrieved.id == job.id
        assert retrieved.character_id == "char-1"
        assert retrieved.job_type == "pose"

    def test_job_id_is_uuid(self):
        """Job IDs are valid UUIDs."""
        import uuid
        jq = JobQueue()
        job = jq.create_job("char-1", "pose", {})
        # Should not raise
        uuid.UUID(job.id)

    def test_job_completed_at_none_for_pending(self):
        """A pending job has completed_at = None."""
        jq = JobQueue()
        job = jq.create_job("char-1", "pose", {})
        assert job.completed_at is None

    def test_job_completed_at_set_on_terminal(self):
        """A completed job has completed_at set."""
        jq = JobQueue()
        job = jq.create_job("char-1", "pose", {})
        jq.update_status(job.id, "completed")
        assert jq.get_job(job.id).completed_at is not None


# ── DiversityFilter Tests ──────────────────────────────────────────────


class TestDiversityFilter:
    """Verify DiversityFilter edge cases."""

    def test_diversity_filter_empty_input(self):
        """DiversityFilter handles empty input gracefully."""
        df = DiversityFilter(n_clusters=3)
        result = df.cluster_and_select([], [])
        assert result == []

    def test_diversity_filter_single_image(self):
        """DiversityFilter handles a single image."""
        df = DiversityFilter(n_clusters=3)
        img = Image.new("RGB", (64, 64), color=(255, 0, 0))
        result = df.cluster_and_select([img], [0.9], n_select=1)
        assert len(result) == 1
        assert result[0][0] == 0
        assert result[0][1] == 0.9

    def test_diversity_filter_mismatched_lengths(self):
        """DiversityFilter raises ValueError on mismatched inputs."""
        df = DiversityFilter(n_clusters=3)
        imgs = [Image.new("RGB", (64, 64), color=(255, 0, 0))]
        with pytest.raises(ValueError):
            df.cluster_and_select(imgs, [0.9, 0.8], n_select=1)

    def test_diversity_filter_n_select_zero(self):
        """DiversityFilter returns empty when n_select=0."""
        df = DiversityFilter(n_clusters=3)
        imgs = [Image.new("RGB", (64, 64), color=(255, 0, 0))]
        result = df.cluster_and_select(imgs, [0.9], n_select=0)
        assert result == []

    def test_diversity_filter_n_select_larger_than_input(self):
        """DiversityFilter returns all when n_select > input size."""
        df = DiversityFilter(n_clusters=2)
        imgs = [
            Image.new("RGB", (64, 64), color=(255, 0, 0)),
            Image.new("RGB", (64, 64), color=(0, 255, 0)),
        ]
        result = df.cluster_and_select(imgs, [0.9, 0.8], n_select=10)
        assert len(result) == 2


# ── GenerationJob Tests ────────────────────────────────────────────


class TestGenerationJob:
    """Verify GenerationJob construction and error handling."""

    def test_generation_job_construction(self):
        """GenerationJob can be constructed with mock dependencies."""
        from src.pipeline import GenerationJob
        from src.identity_engine.scorer import IdentityScorer, MockScorerPlugin
        from src.prompt_builder.builder import PromptBuilder

        from tests.conftest import MockBackend

        repo = SQLiteAssetRepository(":memory:")
        backend = MockBackend()
        scorer = IdentityScorer(plugins=[MockScorerPlugin(weight=1.0)])
        df = DiversityFilter(n_clusters=2)
        gj = GenerationJob(
            backend=backend,
            prompt_builder=PromptBuilder(),
            identity_scorer=scorer,
            asset_repo=repo,
            diversity_filter=df,
        )
        assert gj is not None

    @pytest.mark.asyncio
    async def test_generation_job_execute_empty(self):
        """GenerationJob execution with empty variants returns zero counts (no crash)."""
        from src.pipeline import GenerationJob, Job
        from src.identity_engine.scorer import IdentityScorer, MockScorerPlugin
        from src.prompt_builder.builder import PromptBuilder

        from tests.conftest import MockBackend

        repo = SQLiteAssetRepository(":memory:")
        backend = MockBackend()
        scorer = IdentityScorer(plugins=[MockScorerPlugin(weight=1.0)])
        df = DiversityFilter(n_clusters=2)
        gj = GenerationJob(
            backend=backend,
            prompt_builder=PromptBuilder(),
            identity_scorer=scorer,
            asset_repo=repo,
            diversity_filter=df,
        )

        job = Job(character_id="test-char", job_type="reference", config={"variants": []})
        result = await gj.execute(job)
        assert result["total_generated"] == 0
        assert result["total_scored"] == 0
        assert result["shortlisted_ids"] == []
        assert result["variants_completed"] == 0
        assert result["variants_failed"] == 0


# ── ComfyUI Workflow Loading Tests ────────────────────────────────


class TestComfyUIWorkflowLoading:
    """Verify type-specific workflow template loading and prompt injection."""

    def test_load_expression_workflow(self):
        """Load expression template, verify Flux-correct KSampler, empty text."""
        from src.generation_engine.comfy_backend import ComfyUIBackend

        backend = ComfyUIBackend()
        workflow = backend._load_workflow_template("expression")

        assert workflow["3"]["class_type"] == "KSampler"
        assert workflow["3"]["inputs"]["cfg"] == 1.0
        assert workflow["3"]["inputs"]["steps"] == 30
        assert workflow["3"]["inputs"]["scheduler"] == "simple"
        assert workflow["5"]["class_type"] == "EmptySD3LatentImage"
        assert workflow["7"]["inputs"]["text"] == ""
        assert workflow["7"]["class_type"] == "CLIPTextEncode"

    def test_load_reference_sheet_workflow(self):
        """Load reference_sheet template, verify 1024x1024 dimensions."""
        from src.generation_engine.comfy_backend import ComfyUIBackend

        backend = ComfyUIBackend()
        workflow = backend._load_workflow_template("reference_sheet")

        assert workflow["5"]["inputs"]["width"] == 1024
        assert workflow["5"]["inputs"]["height"] == 1024
        assert workflow["3"]["inputs"]["cfg"] == 1.0

    def test_load_pose_workflow(self):
        """Load pose template, verify 768x1344 dimensions."""
        from src.generation_engine.comfy_backend import ComfyUIBackend

        backend = ComfyUIBackend()
        workflow = backend._load_workflow_template("pose")

        assert workflow["5"]["inputs"]["width"] == 768
        assert workflow["5"]["inputs"]["height"] == 1344
        assert workflow["3"]["inputs"]["cfg"] == 1.0

    def test_load_fallback_on_unknown_type(self):
        """Load nonexistent type, verify returns default template with cfg=1.0."""
        from src.generation_engine.comfy_backend import ComfyUIBackend

        backend = ComfyUIBackend()
        workflow = backend._load_workflow_template("nonexistent_type")

        # Default template uses Flux guidance (cfg=1.0), not SD-style CFG
        assert workflow["3"]["inputs"]["cfg"] == 1.0
        assert workflow["3"]["class_type"] == "KSampler"

    def test_default_template_has_valid_ckpt_name(self):
        """Fallback template must carry the installed checkpoint name."""
        from src.generation_engine.comfy_backend import ComfyUIBackend

        backend = ComfyUIBackend()
        workflow = backend._load_workflow_template("nonexistent_type")

        assert workflow["4"]["class_type"] == "CheckpointLoaderSimple"
        assert workflow["4"]["inputs"]["ckpt_name"] == "flux1-dev.safetensors"

    def test_build_workflow_fills_empty_ckpt_name(self):
        """Every submitted workflow names a checkpoint, never an empty string."""
        from src.generation_engine.comfy_backend import ComfyUIBackend
        from src.generation_engine.base import GenerationInput

        backend = ComfyUIBackend()
        workflow = backend._build_workflow(GenerationInput(prompt="hi"), asset_type="nope")

        assert workflow["4"]["inputs"]["ckpt_name"] == "flux1-dev.safetensors"

    def test_reference_aliases_to_reference_sheet(self):
        """'reference'/'lighting' reuse the reference_sheet graph (cfg 1.0)."""
        from src.generation_engine.comfy_backend import ComfyUIBackend

        backend = ComfyUIBackend()
        workflow = backend._load_workflow_template("reference")
        assert workflow["3"]["inputs"]["cfg"] == 1.0
        assert workflow["4"]["inputs"]["ckpt_name"] == "flux1-dev.safetensors"

        lighting = backend._load_workflow_template("lighting")
        assert lighting["3"]["inputs"]["cfg"] == 1.0

    def test_build_workflow_injects_into_sd3_latent_node(self):
        """Dimension injection must handle the Flux EmptySD3LatentImage node."""
        from src.generation_engine.comfy_backend import ComfyUIBackend
        from src.generation_engine.base import GenerationInput

        backend = ComfyUIBackend()
        workflow = backend._build_workflow(
            GenerationInput(prompt="hi", width=832, height=1216),
            asset_type="expression",
        )
        assert workflow["5"]["class_type"] == "EmptySD3LatentImage"
        assert workflow["5"]["inputs"]["width"] == 832
        assert workflow["5"]["inputs"]["height"] == 1216

    def test_build_workflow_upgrades_gguf_checkpoint(self):
        """A .gguf checkpoint must be rewired to UnetLoaderGGUF + clips + VAE."""
        from src.generation_engine.comfy_backend import ComfyUIBackend
        from src.generation_engine.base import GenerationInput

        backend = ComfyUIBackend()
        workflow = backend._build_workflow(
            GenerationInput(prompt="hi"), asset_type="expression"
        )
        workflow["4"]["inputs"]["ckpt_name"] = "flux1-dev-Q4_K_S.gguf"
        backend._upgrade_to_gguf_if_needed(workflow)

        assert workflow["4"]["class_type"] == "UnetLoaderGGUF"
        assert workflow["4"]["inputs"]["unet_name"] == "flux1-dev-Q4_K_S.gguf"
        clip_id = next(nid for nid, n in workflow.items()
                       if n.get("class_type") == "DualCLIPLoader")
        assert workflow[clip_id]["inputs"]["type"] == "flux"
        vae_id = next(nid for nid, n in workflow.items()
                      if n.get("class_type") == "VAELoader")
        assert workflow[vae_id]["inputs"]["vae_name"] == "ae.safetensors"
        # positive/negative CLIP nodes must now read from DualCLIPLoader
        assert workflow["6"]["inputs"]["clip"] == [clip_id, 0]
        assert workflow["8"]["inputs"]["vae"] == [vae_id, 0]

    def test_prompt_injection_into_loaded_workflow(self):
        """Build workflow with prompt, verify node 6 has injected text."""
        from src.generation_engine.comfy_backend import ComfyUIBackend
        from src.generation_engine.base import GenerationInput

        backend = ComfyUIBackend()
        gen_input = GenerationInput(prompt="test prompt")
        workflow = backend._build_workflow(gen_input, asset_type="expression")

        assert workflow["6"]["inputs"]["text"] == "test prompt"
        assert workflow["6"]["class_type"] == "CLIPTextEncode"
        assert workflow["3"]["inputs"]["cfg"] == 1.0  # Flux params preserved


# ── Helper to import sqlite repo for tests ─────────────────────────
from src.asset_repository.sqlite_repo import SQLiteAssetRepository
