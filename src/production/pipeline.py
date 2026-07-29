from typing import Dict, List, Optional, Callable
from src.production.models import (
    Episode,
    EpisodeManifest,
    Scene,
    Shot,
    RenderTask,
    QCReport,
    ProductionTokens,
    CharacterAssignment,
    Camera,
)
from src.production.manifest import ManifestBuilder
from src.production.prompt_generator import PromptGenerator
from src.production.continuity import ContinuityEngine


class ProductionPipeline:
    def __init__(self):
        self.manifest_builder = ManifestBuilder()
        self.prompt_generator = PromptGenerator()
        self.continuity = ContinuityEngine()
        self._quality_gates: List[Callable[[Shot], List[str]]] = []
        self.render_queue: List[RenderTask] = []
        self.qc_reports: Dict[str, QCReport] = {}

    def create_episode(
        self,
        episode_id: str,
        title: str,
        duration_seconds: float = 180.0,
        learning_goal: str = "",
        has_song: bool = False,
        characters: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
    ) -> Episode:
        manifest = self.manifest_builder.build(
            episode_id=episode_id,
            title=title,
            duration_seconds=duration_seconds,
            learning_goal=learning_goal,
            has_song=has_song,
            characters=characters or [],
            locations=locations or [],
        )
        return Episode(
            id=episode_id,
            title=title,
            duration_seconds=duration_seconds,
            manifest=manifest,
        )

    def add_scene(
        self,
        episode: Episode,
        scene_id: str,
        title: str,
        purpose: str,
        location: str,
        duration_seconds: float = 30.0,
        mood: str = "happy",
        characters: Optional[List[str]] = None,
    ) -> Scene:
        scene = Scene(
            id=scene_id,
            episode_id=episode.id,
            title=title,
            purpose=purpose,
            duration_seconds=duration_seconds,
            location=location,
            mood=mood,
            characters=characters or [],
        )
        episode.scenes.append(scene)
        return scene

    def add_shot(
        self,
        scene: Scene,
        shot_id: str,
        duration_seconds: float = 3.0,
        camera: Optional[Camera] = None,
        environment: str = "",
        animation: str = "idle",
        emotion: str = "neutral",
        characters: Optional[List[CharacterAssignment]] = None,
    ) -> Shot:
        shot = Shot(
            id=shot_id,
            scene_id=scene.id,
            duration_seconds=duration_seconds,
            camera=camera or Camera(),
            environment=environment or scene.location,
            animation=animation,
            emotion=emotion,
            characters=characters or [],
        )
        scene.shots.append(shot)
        return shot

    def build_manifest(self, episode: Episode) -> EpisodeManifest:
        return self.manifest_builder.from_episode(episode)

    def generate_prompts(self, episode: Episode) -> Dict[str, str]:
        prompts: Dict[str, str] = {}
        for scene in episode.scenes:
            for shot in scene.shots:
                prompts[shot.id] = self.prompt_generator.generate_shot_prompt(shot)
        return prompts

    def validate_continuity(self, episode: Episode) -> List[str]:
        return self.continuity.validate_episode(episode)

    def build_render_queue(self, episode: Episode) -> List[RenderTask]:
        self.render_queue = []
        for scene in episode.scenes:
            for shot in scene.shots:
                task = RenderTask(
                    shot_id=shot.id,
                    task_type="image",
                    status="queued",
                    priority=5,
                )
                self.render_queue.append(task)
        return self.render_queue

    def add_quality_gate(self, gate: Callable[[Shot], List[str]]):
        self._quality_gates.append(gate)

    def run_quality_gates(self, shot: Shot) -> List[str]:
        all_issues: List[str] = []
        for gate in self._quality_gates:
            issues = gate(shot)
            all_issues.extend(issues)

        report = QCReport(
            shot_id=shot.id,
            checks={},
            approved=len(all_issues) == 0,
            notes="; ".join(all_issues) if all_issues else None,
        )
        self.qc_reports[shot.id] = report
        return all_issues

    def approve_shot(self, shot_id: str) -> bool:
        if shot_id in self.qc_reports:
            self.qc_reports[shot_id].approved = True
            return True
        return False

    def get_shot_status(self, shot_id: str) -> Optional[str]:
        for task in self.render_queue:
            if task.shot_id == shot_id:
                return task.status
        return None

    def decompose_story(self, story_structure: List[Dict]) -> Episode:
        root = story_structure[0] if story_structure else {}
        ep = self.create_episode(
            episode_id="S01E001",
            title=root.get("title", "Untitled"),
            duration_seconds=root.get("duration", 180),
            learning_goal=root.get("goal", ""),
            has_song=root.get("has_song", False),
        )

        for i, act in enumerate(root.get("acts", [])):
            scene = self.add_scene(
                episode=ep,
                scene_id=f"SC_{i+1:03d}",
                title=act.get("title", f"Scene {i+1}"),
                purpose=act.get("purpose", ""),
                location=act.get("location", ""),
                duration_seconds=act.get("duration", 30),
                mood=act.get("mood", "happy"),
                characters=act.get("characters", []),
            )

            for j, shot_data in enumerate(act.get("shots", [])):
                camera = Camera(
                    shot_type=shot_data.get("shot_type", "medium"),
                    movement=shot_data.get("movement", "static"),
                    position=shot_data.get("position", "front"),
                )
                chars = [
                    CharacterAssignment(
                        character_id=c["id"],
                        emotion=c.get("emotion", "neutral"),
                        animation=c.get("animation", "idle"),
                        speaking=c.get("speaking", False),
                    )
                    for c in shot_data.get("characters", [])
                ]
                self.add_shot(
                    scene=scene,
                    shot_id=f"SH_{i+1:03d}_{j+1:03d}",
                    duration_seconds=shot_data.get("duration", 3.0),
                    camera=camera,
                    environment=shot_data.get("environment", scene.location),
                    animation=shot_data.get("animation", "idle"),
                    emotion=shot_data.get("emotion", "neutral"),
                    characters=chars,
                )

        return ep


def decompose_story(structure: Dict) -> Episode:
    pipeline = ProductionPipeline()
    return pipeline.decompose_story(structure)
