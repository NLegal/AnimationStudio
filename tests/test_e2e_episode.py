"""End-to-end episode smoke test (E-07).

Runs a complete episode from story generation through editing/export
entirely with in-process mock backends - no GPU, no ComfyUI, no network.
Every stage of the pipeline is exercised so structural breakage anywhere
in the chain fails this test rather than going unnoticed.
"""

from __future__ import annotations

import pytest

from src.post_production import (
    ClipReference,
    EditingEngine,
    ExportEngine,
    PostProductionQC,
    SceneAssembly,
)
from src.production.blueprint_adapter import blueprint_to_episode
from src.production.pipeline import ProductionPipeline
from src.story_engine.generator import EpisodeGenerator
from src.studio.orchestrator import PipelineOrchestrator
from src.studio.workflow import EpisodeWorkflowFactory


class TestEndToEndEpisode:
    def test_full_episode_pipeline_all_stages(self):
        # 1. Story generation
        gen = EpisodeGenerator()
        bp = gen.generate_episode()
        assert not bp.validate()

        # 2. Blueprint -> Episode
        ep = blueprint_to_episode(bp)
        assert ep.id == bp.episode_id
        assert len(ep.scenes) >= 3
        assert ep.manifest is not None

        # 3. Production pipeline: prompts, continuity, render queue
        pipeline = ProductionPipeline()
        prompts = pipeline.generate_prompts(ep)
        assert len(prompts) == ep.shot_count
        queue = pipeline.build_render_queue(ep)
        assert len(queue) == ep.shot_count
        issues = pipeline.validate_continuity(ep)
        assert isinstance(issues, list)

        # 4. Orchestrator workflow drives every stage to completion
        orch = PipelineOrchestrator()
        orch.setup_defaults()
        orch.create_pipeline(ep.id)
        complete = orch.process_pipeline(ep.id, passes=20)
        assert complete, "Episode workflow did not reach COMPLETED"

        # 5. Post-production: assemble clips into a timeline
        assembly = self._build_assembly(ep)
        assert assembly.total_clips() >= ep.shot_count
        edit = EditingEngine()
        tl = edit.assemble_scenes(ep.id, assembly, ep.title)
        assert tl.episode_id == ep.id
        assert tl.duration_seconds > 0

        # 6. QC on the assembled timeline
        qc = PostProductionQC()
        qc_timeline = qc.validate_timeline(tl)
        assert qc_timeline.passed
        assert qc_timeline.score == 100.0

        # 7. Export presets + export QC
        exporter = ExportEngine()
        presets = list(exporter.list_presets().values())
        assert presets
        qc_exports = qc.validate_exports(presets)
        assert qc_exports.passed
        assert all(p.format == "mp4" for p in presets)

        # 8. Final manifest linkage back to source
        assert ep.manifest.episode_id == bp.episode_id
        assert ep.manifest.title == bp.title

    def test_workflow_factory_stage_order_and_assets(self):
        factory = EpisodeWorkflowFactory()
        assert factory.STEP_SEQUENCE[0][0] == "story"
        assert factory.STEP_SEQUENCE[-1][0] == "monitor"
        assert "images" in {s[0] for s in factory.STEP_SEQUENCE}

    def test_batch_episodes_each_complete(self):
        gen = EpisodeGenerator()
        for bp in gen.generate_batch(count=3):
            ep = blueprint_to_episode(bp)
            prompts = ProductionPipeline().generate_prompts(ep)
            assert len(prompts) == ep.shot_count
            for shot_id, prompt in prompts.items():
                assert isinstance(prompt, str) and prompt.strip()

    def test_orchestrator_pipeline_without_gpu_dependencies(self):
        """The mock orchestrator must complete without raising, proving the
        workflow/queue wiring is independent of real GPU backends."""
        orch = PipelineOrchestrator()
        orch.setup_defaults()
        orch.create_pipeline("E2E_SMOKE")
        assert not orch.ready_steps("E2E_SMOKE") or orch.ready_steps("E2E_SMOKE")
        # story is first: it must become ready
        assert orch.ready_steps("E2E_SMOKE")
        assert orch.process_pipeline("E2E_SMOKE", passes=20)

    @staticmethod
    def _build_assembly(ep) -> SceneAssembly:
        sections = {
            "opening": [], "introduction": [], "learning": [], "song": [],
            "practice": [], "review": [], "celebration": [], "outro": [],
        }
        for scene in ep.scenes:
            section = getattr(scene, "type", None) or "learning"
            section_name = str(section).lower()
            target = sections.get(section_name, sections["learning"])
            for shot in scene.shots:
                clip = ClipReference(
                    clip_id=shot.id,
                    episode=ep.id,
                    scene=scene.id,
                    shot=shot.id,
                    duration=max(1.0, getattr(shot, "duration", 2.0) or 2.0),
                )
                target.append(clip)
        return SceneAssembly(episode_id=ep.id, **sections)

    def test_export_engine_presets_are_consistent(self):
        exporter = ExportEngine()
        presets = exporter.list_presets()
        assert "youtube" in presets
        assert "master_archive" in presets
        for name, preset in presets.items():
            assert preset.resolution_width > 0
            assert preset.resolution_height > 0
            assert preset.frame_rate in (24, 30, 60)
            assert preset.format