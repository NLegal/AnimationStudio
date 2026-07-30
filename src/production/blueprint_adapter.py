from __future__ import annotations
from typing import Dict, List, Optional

from src.story_engine.models import EpisodeBlueprint, DialogueLine, SongPlacement
from src.production.models import (
    Episode,
    EpisodeManifest,
    Scene,
    Shot,
    Camera,
    CharacterAssignment,
    DialogueEvent,
    MusicEvent,
)
from src.production.episode_templates import TEMPLATES

BEAT_TO_PURPOSE: Dict[str, str] = {
    "opening": "Greet the viewer and introduce the topic",
    "goal": "Set the episode goal",
    "problem": "Introduce the story problem",
    "discovery": "Discover something new",
    "learning": "Teach the educational concept",
    "practice": "Practice with the viewer",
    "success": "Achieve success",
    "celebration": "Celebrate learning",
    "goodbye": "Say goodbye and wrap up",
    "play": "Playful exploration",
    "exploration": "Explore the environment",
    "plan": "Make a plan",
}

BEAT_TO_MOOD: Dict[str, str] = {
    "opening": "happy",
    "goal": "curious",
    "problem": "curious",
    "discovery": "surprised",
    "learning": "curious",
    "practice": "playful",
    "success": "excited",
    "celebration": "excited",
    "goodbye": "happy",
    "play": "playful",
    "exploration": "curious",
    "plan": "focused",
}


def _select_template(blueprint: EpisodeBlueprint) -> str:
    if blueprint.has_song:
        return "educational_song"
    beats_lower = [b.lower() for b in blueprint.narrative_structure]
    morning_keywords = ["wake", "morning", "breakfast", "bedtime", "routine"]
    if any(any(k in b for k in morning_keywords) for b in beats_lower):
        return "morning_routine"
    return "story_time"


def _estimate_dialogue_timing(
    dialogue: List[DialogueLine],
    total_duration_seconds: float,
) -> List[DialogueEvent]:
    events: List[DialogueEvent] = []
    current_time = 0.0
    word_rate = 2.5
    for line in dialogue:
        word_count = max(len(line.text.split()), 1)
        duration = max(word_count / word_rate, 1.5)
        events.append(
            DialogueEvent(
                character=line.speaker,
                line=line.text,
                start_time=current_time,
                end_time=current_time + duration,
                emotion=line.emotion,
            )
        )
        current_time += duration + line.pause_after
    if events and current_time > total_duration_seconds:
        scale = total_duration_seconds / current_time
        for ev in events:
            mid = (ev.start_time + ev.end_time) / 2
            ev.start_time = round(ev.start_time * scale, 2)
            ev.end_time = round(ev.end_time * scale, 2)
    return events


def _distribute_across(n_items: int, n_groups: int) -> List[int]:
    if n_groups == 0:
        return []
    base = n_items // n_groups
    remainder = n_items % n_groups
    return [base + (1 if i < remainder else 0) for i in range(n_groups)]


def _make_shot_characters(
    all_chars: List[str],
    beat: str,
    sdata: Dict,
    main_character: str,
) -> List[CharacterAssignment]:
    result: List[CharacterAssignment] = []
    for cid in all_chars[:2]:
        result.append(
            CharacterAssignment(
                character_id=cid,
                visible=True,
                speaking=cid == main_character,
                animation=sdata.get("animation", "idle"),
                emotion=sdata.get("emotion", BEAT_TO_MOOD.get(beat, "happy")),
            )
        )
    return result


def blueprint_to_episode(
    blueprint: EpisodeBlueprint,
    episode_id_override: Optional[str] = None,
) -> Episode:
    ep_id = episode_id_override or blueprint.episode_id
    duration_seconds = float(blueprint.duration_minutes * 60)
    all_chars = [c for c in [blueprint.main_character] + blueprint.supporting_characters if c]

    ep = Episode(
        id=ep_id,
        title=blueprint.title,
        duration_seconds=duration_seconds,
        manifest=EpisodeManifest(
            episode_id=ep_id,
            title=blueprint.title,
            duration_seconds=duration_seconds,
            target_age=blueprint.target_age,
            learning_goal=blueprint.learning_objective,
            has_song=blueprint.has_song,
            characters=all_chars,
            locations=[blueprint.location],
            assets=blueprint.assets,
        ),
    )

    template_name = _select_template(blueprint)
    template_scenes = list(TEMPLATES.get(template_name, TEMPLATES["story_time"]))

    beats = blueprint.narrative_structure or [
        "opening", "problem", "learning", "celebration", "goodbye"
    ]
    if len(template_scenes) < len(beats):
        template_scenes += [template_scenes[-1]] * (len(beats) - len(template_scenes))
    template_scenes = template_scenes[: len(beats)]

    dialogue_events = _estimate_dialogue_timing(blueprint.dialogue, duration_seconds)
    dialogue_per_scene = _distribute_across(len(dialogue_events), len(template_scenes))

    scene_dialogue_idx = 0
    for i, (beat, tscene) in enumerate(zip(beats, template_scenes)):
        scene_id = f"SC_{i+1:03d}"
        scene_mood = BEAT_TO_MOOD.get(beat, tscene.get("mood", "happy"))
        scene_has_song = (
            blueprint.has_song
            and (tscene.get("has_song", False) or beat in ("celebration", "learning", "song"))
        )

        scene = Scene(
            id=scene_id,
            episode_id=ep_id,
            title=tscene.get("title", beat.capitalize()),
            purpose=BEAT_TO_PURPOSE.get(beat, tscene.get("purpose", "")),
            duration_seconds=float(tscene.get("duration", 30)),
            characters=list(all_chars),
            location=blueprint.location,
            learning_objective=blueprint.learning_objective,
            has_dialogue=len(blueprint.dialogue) > 0,
            has_song=scene_has_song,
            mood=scene_mood,
            assets=list(blueprint.assets),
        )

        n_dialogue = dialogue_per_scene[i]
        for _ in range(n_dialogue):
            if scene_dialogue_idx < len(dialogue_events):
                scene.dialogue.append(dialogue_events[scene_dialogue_idx])
                scene_dialogue_idx += 1

        template_shots = tscene.get(
            "shots", [{"shot_type": "medium", "duration": 3}]
        )
        for j, sdata in enumerate(template_shots):
            shot_id = f"SH_{i+1:03d}_{j+1:03d}"
            camera = Camera(
                shot_type=sdata.get("shot_type", "medium"),
                movement=sdata.get("movement", "static"),
                position=sdata.get("position", "front"),
            )
            shot = Shot(
                id=shot_id,
                scene_id=scene_id,
                duration_seconds=float(sdata.get("duration", 3)),
                camera=camera,
                characters=_make_shot_characters(all_chars, beat, sdata, blueprint.main_character),
                assets=list(blueprint.assets),
                environment=blueprint.location,
                animation=sdata.get("animation", "idle"),
                lighting="natural",
                weather=blueprint.weather,
                emotion=sdata.get("emotion", scene_mood),
                movement=camera.movement,
            )
            scene.shots.append(shot)

        if scene_has_song and blueprint.song:
            scene.music.append(
                MusicEvent(
                    track_id=f"song_{scene_id}",
                    start_time=0,
                    end_time=float(blueprint.song.duration_seconds),
                    music_type=blueprint.song.song_type,
                )
            )

        ep.scenes.append(scene)

    return ep
