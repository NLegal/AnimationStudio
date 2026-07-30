from typing import Dict, List, Optional, Set
from src.production.models import Episode, Scene, Shot, CharacterAssignment


class ContinuityValidator:
    def __init__(self):
        self._rules: List[str] = []
        self._character_states: Dict[str, Dict] = {}

    def validate_episode(self, episode: Episode) -> List[str]:
        issues: List[str] = []
        self._character_states = {}

        for scene_idx, scene in enumerate(episode.scenes):
            scene_issues = self._validate_scene(scene, scene_idx, episode)
            issues.extend(scene_issues)

        issues.extend(self._validate_cross_scene(episode))
        return issues

    def _validate_scene(self, scene: Scene, scene_idx: int, episode: Episode) -> List[str]:
        issues: List[str] = []

        if not scene.shots:
            issues.append(f"Scene {scene.id} has no shots")

        if not scene.location:
            issues.append(f"Scene {scene.id} has no location")

        for shot_idx, shot in enumerate(scene.shots):
            shot_issues = self._validate_shot(shot, scene, shot_idx)
            issues.extend(shot_issues)

        return issues

    def _validate_shot(self, shot: Shot, scene: Scene, shot_idx: int) -> List[str]:
        issues: List[str] = []

        if not shot.environment:
            issues.append(f"Shot {shot.id} has no environment")

        if shot.duration_seconds <= 0:
            issues.append(f"Shot {shot.id} has invalid duration: {shot.duration_seconds}")

        for char in shot.characters:
            char_issues = self._validate_character(char, shot)
            issues.extend(char_issues)

        return issues

    def _validate_character(self, char: CharacterAssignment, shot: Shot) -> List[str]:
        issues: List[str] = []

        if char.character_id in self._character_states:
            prev = self._character_states[char.character_id]
            if char.clothing and prev.get("clothing") and char.clothing != prev["clothing"]:
                issues.append(
                    f"Continuity: {char.character_id} clothing changed "
                    f"from '{prev['clothing']}' to '{char.clothing}' in shot {shot.id}"
                )
        else:
            self._character_states[char.character_id] = {}

        self._character_states[char.character_id].update(
            {
                "clothing": char.clothing,
                "emotion": char.emotion,
                "accessories": tuple(char.accessories),
                "shot_id": shot.id,
            }
        )

        return issues

    def _validate_cross_scene(self, episode: Episode) -> List[str]:
        issues: List[str] = []
        envs: Set[str] = set()
        chars_used: Set[str] = set()

        for scene in episode.scenes:
            if scene.location:
                envs.add(scene.location)
            for char_id in scene.characters:
                chars_used.add(char_id)

        for scene in episode.scenes:
            if scene.characters:
                missing = [c for c in scene.characters if c not in chars_used]
                for c in missing:
                    issues.append(f"Character {c} used in scene {scene.id} but not in episode manifest")

        return issues

    def check_asset_consistency(self, shot: Shot, episode_assets: List[str]) -> List[str]:
        issues: List[str] = []
        for asset in shot.assets:
            if asset not in episode_assets:
                issues.append(
                    f"Asset {asset} used in shot {shot.id} but not in episode manifest"
                )
        return issues

    def add_rule(self, rule: str):
        self._rules.append(rule)
