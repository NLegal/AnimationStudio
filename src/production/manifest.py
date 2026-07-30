from typing import List, Optional
from src.production.models import EpisodeManifest, Episode, Scene


class ManifestBuilder:
    def build(
        self,
        episode_id: str,
        title: str,
        duration_seconds: float = 180.0,
        target_age: str = "2-5",
        learning_goal: str = "",
        has_song: bool = False,
        has_narration: bool = True,
        characters: Optional[List[str]] = None,
        locations: Optional[List[str]] = None,
        assets: Optional[List[str]] = None,
    ) -> EpisodeManifest:
        return EpisodeManifest(
            episode_id=episode_id,
            title=title,
            duration_seconds=duration_seconds,
            target_age=target_age,
            learning_goal=learning_goal,
            has_song=has_song,
            has_narration=has_narration,
            characters=characters or [],
            locations=locations or [],
            assets=assets or [],
        )

    def from_episode(self, episode: Episode) -> EpisodeManifest:
        chars: set = set()
        locs: set = set()
        assets: set = set()
        for scene in episode.scenes:
            chars.update(scene.characters)
            if scene.location:
                locs.add(scene.location)
            assets.update(scene.assets)

        video_clips = 0
        images = 0
        for scene in episode.scenes:
            for shot in scene.shots:
                images += 1

        existing = episode.manifest
        return EpisodeManifest(
            episode_id=episode.id,
            title=episode.title,
            duration_seconds=episode.duration_seconds,
            target_age=existing.target_age if existing else "2-5",
            learning_goal=existing.learning_goal if existing else "",
            has_song=existing.has_song if existing else False,
            has_narration=existing.has_narration if existing else True,
            characters=sorted(chars),
            locations=sorted(locs),
            assets=sorted(assets),
            scene_count=episode.scene_count,
            shot_count=episode.shot_count,
            estimated_video_clips=video_clips,
            estimated_images=images,
        )

    def to_dict(self, manifest: EpisodeManifest) -> dict:
        return {
            "Episode ID": manifest.episode_id,
            "Title": manifest.title,
            "Duration": f"{int(manifest.duration_seconds // 60)}:{int(manifest.duration_seconds % 60):02d}",
            "Target Age": manifest.target_age,
            "Learning Goal": manifest.learning_goal,
            "Song": "Yes" if manifest.has_song else "No",
            "Narration": "Yes" if manifest.has_narration else "No",
            "Characters": manifest.characters,
            "Locations": manifest.locations,
            "Assets": manifest.assets,
            "Scenes": manifest.scene_count,
            "Shots": manifest.shot_count,
            "Estimated Video Clips": manifest.estimated_video_clips,
            "Estimated Images": manifest.estimated_images,
        }
