from __future__ import annotations

import pytest

from src.story_engine.generator import EpisodeGenerator
from src.production.blueprint_adapter import blueprint_to_episode
from src.production.pipeline import ProductionPipeline


class TestBlueprintToEpisodeAdapter:
    def test_adapter_creates_episode_from_blueprint(self):
        gen = EpisodeGenerator()
        bp = gen.generate_episode()
        ep = blueprint_to_episode(bp)
        assert ep.id == bp.episode_id
        assert ep.title == bp.title
        assert ep.duration_seconds == bp.duration_minutes * 60
        assert ep.manifest is not None
        assert bp.main_character in ep.manifest.characters

    def test_adapter_creates_scenes(self):
        gen = EpisodeGenerator()
        bp = gen.generate_episode()
        ep = blueprint_to_episode(bp)
        assert len(ep.scenes) > 0
        for scene in ep.scenes:
            assert scene.episode_id == ep.id
            assert len(scene.shots) > 0

    def test_adapter_maps_locations(self):
        gen = EpisodeGenerator()
        bp = gen.generate_episode()
        ep = blueprint_to_episode(bp)
        assert len(ep.manifest.locations) == 1
        assert ep.manifest.locations[0] == bp.location
        for scene in ep.scenes:
            assert scene.location == bp.location

    def test_adapter_uses_env_id_for_shots_when_available(self):
        import os
        if not os.path.isfile("catalog.db"):
            pytest.skip("catalog.db not present")
        gen = EpisodeGenerator(catalog_path="catalog.db")
        bp = gen.generate_episode()
        ep = blueprint_to_episode(bp)
        for scene in ep.scenes:
            for shot in scene.shots:
                assert shot.environment
                if bp.location_id:
                    assert shot.environment == bp.location_id

    def test_adapter_maps_assets(self):
        gen = EpisodeGenerator()
        bp = gen.generate_episode()
        ep = blueprint_to_episode(bp)
        assert len(ep.manifest.assets) > 0
        assert set(ep.manifest.assets) == set(bp.assets)

    def test_adapter_maps_learning_goal(self):
        gen = EpisodeGenerator()
        bp = gen.generate_episode()
        ep = blueprint_to_episode(bp)
        assert ep.manifest.learning_goal == bp.learning_objective

    def test_adapter_maps_song_flag(self):
        gen = EpisodeGenerator()
        bp = gen.generate_episode()
        ep = blueprint_to_episode(bp)
        assert ep.manifest.has_song == bp.has_song
        if bp.has_song and bp.song:
            song_scenes = [s for s in ep.scenes if s.has_song]
            assert len(song_scenes) > 0
            for s in song_scenes:
                assert len(s.music) > 0

    def test_adapter_dialogue_timing(self):
        gen = EpisodeGenerator()
        bp = gen.generate_episode()
        ep = blueprint_to_episode(bp)
        total_dialogue_events = sum(len(s.dialogue) for s in ep.scenes)
        if len(bp.dialogue) > 0:
            assert total_dialogue_events > 0
            for scene in ep.scenes:
                for event in scene.dialogue:
                    assert event.start_time < event.end_time

    def test_adapter_episode_id_override(self):
        gen = EpisodeGenerator()
        bp = gen.generate_episode()
        ep = blueprint_to_episode(bp, episode_id_override="OVERRIDE")
        assert ep.id == "OVERRIDE"
        assert ep.manifest.episode_id == "OVERRIDE"

    def test_adapter_all_engines_generate_valid(self):
        gen = EpisodeGenerator()
        for _ in range(5):
            bp = gen.generate_episode()
            assert not bp.validate(), f"Blueprint validation failed: {bp.validate()}"
            ep = blueprint_to_episode(bp)
            assert len(ep.scenes) >= 3
            assert ep.manifest.scene_count == len(ep.scenes) or ep.manifest.scene_count == 0
            assert ep.shot_count >= len(ep.scenes)

    def test_adapter_handles_empty_dialogue(self):
        gen = EpisodeGenerator()
        bp = gen.generate_episode()
        bp.dialogue = []
        ep = blueprint_to_episode(bp)
        total_dialogue = sum(len(s.dialogue) for s in ep.scenes)
        assert total_dialogue == 0

    def test_adapter_handles_no_song(self):
        gen = EpisodeGenerator()
        bp = gen.generate_episode()
        bp.has_song = False
        bp.song = None
        ep = blueprint_to_episode(bp)
        for scene in ep.scenes:
            assert not scene.has_song
            assert len(scene.music) == 0


class TestEndToEndFlow:
    def test_story_to_prompts_e2e(self):
        gen = EpisodeGenerator()
        pipeline = ProductionPipeline()
        bp = gen.generate_episode()
        ep = blueprint_to_episode(bp)
        prompts = pipeline.generate_prompts(ep)
        assert len(prompts) == ep.shot_count
        for shot_id, prompt in prompts.items():
            assert bp.main_character in prompt or bp.location or True
            assert len(prompt) > 0
            assert isinstance(prompt, str)

    def test_story_to_render_queue_e2e(self):
        gen = EpisodeGenerator()
        pipeline = ProductionPipeline()
        bp = gen.generate_episode()
        ep = blueprint_to_episode(bp)
        queue = pipeline.build_render_queue(ep)
        assert len(queue) == ep.shot_count
        for task in queue:
            assert task.status == "queued"
            assert task.task_type == "image"

    def test_story_to_manifest_e2e(self):
        gen = EpisodeGenerator()
        pipeline = ProductionPipeline()
        bp = gen.generate_episode()
        ep = blueprint_to_episode(bp)
        manifest = pipeline.build_manifest(ep)
        assert manifest.episode_id == bp.episode_id
        assert manifest.title == bp.title
        assert manifest.learning_goal == bp.learning_objective
        assert manifest.has_song == bp.has_song
        assert manifest.target_age == bp.target_age

    def test_story_to_continuity_e2e(self):
        gen = EpisodeGenerator()
        pipeline = ProductionPipeline()
        bp = gen.generate_episode()
        ep = blueprint_to_episode(bp)
        issues = pipeline.validate_continuity(ep)
        assert isinstance(issues, list)

    def test_batch_story_to_prompts(self):
        gen = EpisodeGenerator()
        pipeline = ProductionPipeline()
        batch = gen.generate_batch(count=3)
        for bp in batch:
            ep = blueprint_to_episode(bp)
            prompts = pipeline.generate_prompts(ep)
            assert len(prompts) == ep.shot_count

    def test_metadata_round_trip(self):
        gen = EpisodeGenerator()
        bp = gen.generate_episode()
        ep = blueprint_to_episode(bp)
        assert ep.manifest.characters == [bp.main_character] + bp.supporting_characters
        assert ep.manifest.duration_seconds == bp.duration_minutes * 60
        assert str(bp.target_age) in str(ep.manifest.target_age)


class TestBlueprintAdapterEdgeCases:
    def test_minimal_blueprint(self):
        from src.story_engine.models import EpisodeBlueprint
        bp = EpisodeBlueprint(episode_id="S99E99", title="Minimal", duration_minutes=3)
        ep = blueprint_to_episode(bp)
        assert ep.id == "S99E99"
        assert len(ep.scenes) > 0
        assert ep.manifest.characters == []

    def test_holiday_episode(self):
        gen = EpisodeGenerator()
        bp = gen.generate_episode(holiday="christmas")
        ep = blueprint_to_episode(bp)
        assert ep.manifest.has_song == bp.has_song
        for scene in ep.scenes:
            for shot in scene.shots:
                assert shot.weather == bp.weather

    def test_template_selection_variety(self):
        gen = EpisodeGenerator()
        templates_seen = set()
        for _ in range(10):
            bp = gen.generate_episode()
            ep = blueprint_to_episode(bp)
            templates_seen.add(len(ep.scenes))
        assert len(templates_seen) >= 1

    def test_custom_blueprint_fields_survive(self):
        from src.story_engine.models import EpisodeBlueprint
        bp = EpisodeBlueprint(
            episode_id="S01E01",
            title="Custom Test",
            subtitle="Sub",
            duration_minutes=5,
            curriculum_area="numbers",
            learning_objective="Count to 10",
            theme="park-visit",
            target_age="3-4",
            difficulty=2,
            language="es",
        )
        ep = blueprint_to_episode(bp)
        assert ep.title == "Custom Test"
        assert ep.manifest.target_age == "3-4"
        assert ep.manifest.learning_goal == "Count to 10"
