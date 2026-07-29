import pytest
from src.production.models import (
    Camera,
    CharacterAssignment,
    Shot,
    Scene,
    Episode,
    EpisodeManifest,
    ProductionTokens,
    RenderTask,
    QCReport,
)
from src.production.manifest import ManifestBuilder
from src.production.prompt_generator import PromptGenerator
from src.production.continuity import ContinuityEngine
from src.production.pipeline import ProductionPipeline, decompose_story
from src.production.api import ShotType, CameraMovement
from src.production.prompt_templates import (
    resolve_character_template,
    resolve_environment_template,
    resolve_animation_template,
    resolve_camera_template,
)
from src.production.episode_templates import TEMPLATES


class TestCamera:
    def test_default_camera(self):
        c = Camera()
        assert c.shot_type == "medium"
        assert c.movement == "static"
        assert c.position == "front"

    def test_camera_prompt_suffix_static(self):
        c = Camera(shot_type="wide", movement="static", position="front")
        suffix = c.to_prompt_suffix()
        assert "wide shot" in suffix
        assert "front view" in suffix
        assert "static" not in suffix  # static omitted

    def test_camera_prompt_suffix_with_movement(self):
        c = Camera(shot_type="medium", movement="track", position="side")
        suffix = c.to_prompt_suffix()
        assert "track camera" in suffix
        assert "medium shot" in suffix
        assert "side view" in suffix


class TestShot:
    def test_frame_count_calculation(self):
        shot = Shot(id="SH_001", duration_seconds=3.0)
        assert shot.frame_count == 72

    def test_frame_count_zero(self):
        shot = Shot(id="SH_002", duration_seconds=0)
        assert shot.frame_count == 0


class TestEpisode:
    def test_empty_episode(self):
        ep = Episode(id="S01E001", title="Test")
        assert ep.scene_count == 0
        assert ep.shot_count == 0
        assert ep.total_estimated_images() == 0

    def test_episode_with_scenes_and_shots(self):
        ep = Episode(id="S01E001", title="Test")
        scene = Scene(id="SC_001", episode_id="S01E001")
        shot1 = Shot(id="SH_001", scene_id="SC_001")
        shot2 = Shot(id="SH_002", scene_id="SC_001")
        scene.shots = [shot1, shot2]
        ep.scenes = [scene]
        assert ep.scene_count == 1
        assert ep.shot_count == 2
        assert ep.total_estimated_images() == 2


class TestManifestBuilder:
    def test_build_manifest(self):
        builder = ManifestBuilder()
        manifest = builder.build(
            episode_id="S01E001",
            title="Five Colorful Ducks",
            duration_seconds=192,
            learning_goal="Primary Colors",
            has_song=True,
            characters=["Lily Bunny", "Ben Bear"],
            locations=["Sunny Pond"],
            assets=["Balloon", "Flower"],
        )
        assert manifest.episode_id == "S01E001"
        assert manifest.has_song is True
        assert "Lily Bunny" in manifest.characters

    def test_from_episode(self):
        builder = ManifestBuilder()
        ep = Episode(id="S01E001", title="Test")
        scene = Scene(
            id="SC_001",
            episode_id="S01E001",
            characters=["Lily Bunny"],
            location="Playground",
            assets=["Ball"],
        )
        scene.shots = [Shot(id="SH_001", scene_id="SC_001")]
        ep.scenes = [scene]
        manifest = builder.from_episode(ep)
        assert manifest.episode_id == "S01E001"
        assert "Lily Bunny" in manifest.characters
        assert manifest.shot_count == 1

    def test_to_dict(self):
        builder = ManifestBuilder()
        manifest = EpisodeManifest(
            episode_id="S01E001",
            title="Test",
            duration_seconds=180,
            scene_count=6,
            shot_count=24,
        )
        d = builder.to_dict(manifest)
        assert d["Episode ID"] == "S01E001"
        assert d["Duration"] == "3:00"


class TestPromptGenerator:
    def test_generate_shot_prompt(self):
        gen = PromptGenerator()
        shot = Shot(
            id="SH_001",
            environment="Playground",
            lighting="sunny",
            weather="clear",
            characters=[
                CharacterAssignment(
                    character_id="CHAR_LILY_001",
                    emotion="happy",
                    animation="wave",
                )
            ],
        )
        prompt = gen.generate_shot_prompt(shot)
        assert "CHAR_LILY_001" in prompt
        assert "Playground" in prompt
        assert "clear" in prompt

    def test_register_template(self):
        gen = PromptGenerator()
        gen.register_template("custom", "Custom template: {character_description}")
        shot = Shot(
            id="SH_001",
            characters=[CharacterAssignment(character_id="Lily")],
        )
        prompt = gen.generate_shot_prompt(shot, template_key="custom")
        assert prompt.startswith("Custom template:")

    def test_generate_prompt_package(self):
        gen = PromptGenerator()
        shot = Shot(
            id="SH_001",
            environment="Forest",
            lighting="golden_hour",
            animation="walk",
            weather="clear",
            camera=Camera(shot_type="wide"),
            characters=[
                CharacterAssignment(
                    character_id="CHAR_BEN_001",
                    emotion="happy",
                )
            ],
        )
        pkg = gen.generate_prompt_package(shot)
        assert pkg["environment"] == "Forest"
        assert pkg["lighting"] == "golden_hour"

    def test_compose_full_prompt(self):
        gen = PromptGenerator()
        prompt = gen.compose_full_prompt(
            character_prompt="Lily Bunny happy waving",
            environment_prompt="in Sunny Meadow",
            animation_prompt="gentle animation",
            camera_prompt="medium shot front view",
            lighting_prompt="sunny natural light",
        )
        assert "Lily Bunny" in prompt
        assert "Sunny Meadow" in prompt
        assert "Pixar-quality" in prompt


class TestContinuityEngine:
    def test_valid_episode_no_issues(self):
        engine = ContinuityEngine()
        ep = Episode(id="S01E001", title="Test")
        scene = Scene(
            id="SC_001",
            episode_id="S01E001",
            characters=["Lily"],
            location="Playground",
        )
        scene.shots = [
            Shot(
                id="SH_001",
                scene_id="SC_001",
                environment="Playground",
                duration_seconds=3.0,
                characters=[
                    CharacterAssignment(character_id="Lily", clothing="red_dress")
                ],
            )
        ]
        ep.scenes = [scene]
        issues = engine.validate_episode(ep)
        assert len(issues) == 0

    def test_clothing_change_detected(self):
        engine = ContinuityEngine()
        ep = Episode(id="S01E001", title="Test")
        scene = Scene(
            id="SC_001",
            episode_id="S01E001",
            characters=["Lily"],
            location="Playground",
        )
        scene.shots = [
            Shot(
                id="SH_001",
                scene_id="SC_001",
                environment="Playground",
                duration_seconds=3.0,
                characters=[
                    CharacterAssignment(character_id="Lily", clothing="red_dress")
                ],
            ),
            Shot(
                id="SH_002",
                scene_id="SC_001",
                environment="Playground",
                duration_seconds=3.0,
                characters=[
                    CharacterAssignment(character_id="Lily", clothing="blue_dress")
                ],
            ),
        ]
        ep.scenes = [scene]
        issues = engine.validate_episode(ep)
        assert any("clothing changed" in i for i in issues)

    def test_no_shots_in_scene(self):
        engine = ContinuityEngine()
        scene = Scene(id="SC_001", episode_id="S01E001")
        ep = Episode(id="S01E001", scenes=[scene])
        issues = engine.validate_episode(ep)
        assert any("has no shots" in i for i in issues)

    def test_negative_duration(self):
        engine = ContinuityEngine()
        scene = Scene(id="SC_001", episode_id="S01E001")
        scene.shots = [Shot(id="SH_001", duration_seconds=-1)]
        ep = Episode(id="S01E001", scenes=[scene])
        issues = engine.validate_episode(ep)
        assert any("invalid duration" in i for i in issues)


class TestProductionPipeline:
    def test_create_episode(self):
        pipeline = ProductionPipeline()
        ep = pipeline.create_episode(
            episode_id="S01E001",
            title="Test Episode",
            learning_goal="Colors",
            has_song=True,
            characters=["Lily"],
            locations=["Playground"],
        )
        assert ep.id == "S01E001"
        assert ep.manifest is not None
        assert ep.manifest.learning_goal == "Colors"

    def test_add_scene(self):
        pipeline = ProductionPipeline()
        ep = pipeline.create_episode(episode_id="S01E001", title="Test")
        scene = pipeline.add_scene(
            episode=ep,
            scene_id="SC_001",
            title="Opening",
            purpose="Introduce characters",
            location="Playground",
            mood="happy",
            characters=["Lily"],
        )
        assert scene.id == "SC_001"
        assert scene in ep.scenes

    def test_add_shot(self):
        pipeline = ProductionPipeline()
        ep = pipeline.create_episode(episode_id="S01E001", title="Test")
        scene = pipeline.add_scene(
            episode=ep, scene_id="SC_001", title="Test", purpose="Test", location="Playground"
        )
        shot = pipeline.add_shot(
            scene=scene,
            shot_id="SH_001",
            duration_seconds=3.0,
            environment="Playground",
            emotion="happy",
        )
        assert shot.id == "SH_001"
        assert shot in scene.shots

    def test_build_manifest(self):
        pipeline = ProductionPipeline()
        ep = pipeline.create_episode(episode_id="S01E001", title="Test")
        scene = Scene(
            id="SC_001",
            episode_id="S01E001",
            characters=["Lily"],
            location="Park",
        )
        scene.shots = [Shot(id="SH_001", scene_id="SC_001")]
        ep.scenes = [scene]
        manifest = pipeline.build_manifest(ep)
        assert manifest.shot_count == 1

    def test_generate_prompts(self):
        pipeline = ProductionPipeline()
        ep = pipeline.create_episode(episode_id="S01E001", title="Test")
        scene = Scene(id="SC_001", episode_id="S01E001")
        scene.shots = [Shot(id="SH_001", scene_id="SC_001", environment="Park")]
        ep.scenes = [scene]
        prompts = pipeline.generate_prompts(ep)
        assert "SH_001" in prompts

    def test_validate_continuity(self):
        pipeline = ProductionPipeline()
        ep = pipeline.create_episode(episode_id="S01E001", title="Test")
        ep.scenes = [Scene(id="SC_001", episode_id="S01E001")]
        issues = pipeline.validate_continuity(ep)
        assert isinstance(issues, list)

    def test_build_render_queue(self):
        pipeline = ProductionPipeline()
        ep = pipeline.create_episode(episode_id="S01E001", title="Test")
        scene = Scene(id="SC_001", episode_id="S01E001")
        scene.shots = [
            Shot(id="SH_001", scene_id="SC_001"),
            Shot(id="SH_002", scene_id="SC_001"),
        ]
        ep.scenes = [scene]
        queue = pipeline.build_render_queue(ep)
        assert len(queue) == 2
        assert queue[0].shot_id == "SH_001"
        assert queue[0].status == "queued"

    def test_quality_gates_passing(self):
        pipeline = ProductionPipeline()
        shot = Shot(id="SH_001", duration_seconds=3.0, environment="Park")
        issues = pipeline.run_quality_gates(shot)
        assert len(issues) == 0

    def test_quality_gates_failing(self):
        pipeline = ProductionPipeline()
        pipeline.add_quality_gate(lambda s: ["FAIL" if not s.environment else ""])
        shot = Shot(id="SH_001", duration_seconds=3.0, environment="")
        issues = pipeline.run_quality_gates(shot)
        assert any("FAIL" in i for i in issues)
        assert pipeline.qc_reports["SH_001"].approved is False

    def test_approve_shot(self):
        pipeline = ProductionPipeline()
        shot = Shot(id="SH_001")
        pipeline.run_quality_gates(shot)
        result = pipeline.approve_shot("SH_001")
        assert result is True
        assert pipeline.qc_reports["SH_001"].approved is True

    def test_get_shot_status(self):
        pipeline = ProductionPipeline()
        ep = pipeline.create_episode(episode_id="S01E001", title="Test")
        scene = Scene(id="SC_001", episode_id="S01E001")
        scene.shots = [Shot(id="SH_001", scene_id="SC_001")]
        ep.scenes = [scene]
        pipeline.build_render_queue(ep)
        assert pipeline.get_shot_status("SH_001") == "queued"
        assert pipeline.get_shot_status("NONEXISTENT") is None

    def test_decompose_story(self):
        pipeline = ProductionPipeline()
        structure = [
            {
                "title": "Test Episode",
                "duration": 120,
                "goal": "Colors",
                "has_song": True,
                "acts": [
                    {
                        "title": "Opening",
                        "purpose": "Greet",
                        "location": "Playground",
                        "duration": 15,
                        "mood": "happy",
                        "characters": ["Lily"],
                        "shots": [
                            {
                                "shot_type": "wide",
                                "duration": 3.0,
                                "animation": "wave",
                                "emotion": "happy",
                                "environment": "Playground",
                                "characters": [{"id": "Lily", "emotion": "happy"}],
                            }
                        ],
                    }
                ],
            }
        ]
        ep = pipeline.decompose_story(structure)
        assert ep.id == "S01E001"
        assert ep.scene_count == 1
        assert ep.shot_count == 1


class test_production_tokens:
    def test_default_tokens(self):
        tokens = ProductionTokens()
        d = tokens.to_dict()
        assert d["Character"] is None

    def test_filled_tokens(self):
        tokens = ProductionTokens(
            character="CHAR_LILY_001",
            location="ENV_PLAYGROUND_001",
            weather="CLEAR",
            season="SPRING",
        )
        d = tokens.to_dict()
        assert d["Character"] == "CHAR_LILY_001"
        assert d["Weather"] == "CLEAR"


class TestPromptTemplates:
    def test_resolve_character_template(self):
        t = resolve_character_template("lily_bunny")
        assert "Lily Bunny" in t

    def test_resolve_character_template_default(self):
        t = resolve_character_template("unknown_character")
        assert "{character}" in t

    def test_resolve_environment_template(self):
        t = resolve_environment_template("playground")
        assert "Happy Hills Park" in t

    def test_resolve_environment_template_default(self):
        t = resolve_environment_template("unknown")
        assert "{environment}" in t

    def test_resolve_animation_template(self):
        t = resolve_animation_template("walk")
        assert "walk cycle" in t

    def test_resolve_camera_template(self):
        t = resolve_camera_template("close_up")
        assert "close-up shot" in t


class TestEpisodeTemplates:
    def test_educational_song_template(self):
        assert "educational_song" in TEMPLATES
        assert len(TEMPLATES["educational_song"]) == 6

    def test_story_time_template(self):
        assert "story_time" in TEMPLATES
        assert len(TEMPLATES["story_time"]) == 5

    def test_morning_routine_template(self):
        assert "morning_routine" in TEMPLATES
        assert len(TEMPLATES["morning_routine"]) == 4

    def test_templates_have_shots(self):
        for name, acts in TEMPLATES.items():
            for act in acts:
                assert "shots" in act, f"{name} act missing shots"
                assert len(act["shots"]) > 0, f"{name} act has empty shots"


class TestAPISpec:
    def test_shot_type_values(self):
        assert ShotType.WIDE.value == "wide"
        assert ShotType.CLOSE_UP.value == "close-up"

    def test_camera_movement_values(self):
        assert CameraMovement.PAN_LEFT.value == "pan_left"
        assert CameraMovement.TRACK.value == "track"

    def test_import_routes(self):
        from src.production.api import ROUTES
        assert len(ROUTES) > 0
        assert "POST /api/episodes" in ROUTES
