from __future__ import annotations
import random
from typing import Dict, List, Optional

from src.story_engine.models import (
    EpisodeBlueprint, InteractiveMoment, SongPlacement, DialogueLine,
    Theme, LearningObjective,
)
from src.story_engine.curriculum import CurriculumEngine
from src.story_engine.theme import ThemeEngine
from src.story_engine.learning_objective import LearningObjectiveEngine
from src.story_engine.casting import CharacterEngine, RelationshipEngine
from src.story_engine.world import WorldEngine
from src.story_engine.asset import AssetEngine
from src.story_engine.plot import ConflictEngine, ResolutionEngine
from src.story_engine.narrative import NarrativeEngine
from src.story_engine.dialogue import DialogueEngine
from src.story_engine.song import SongEngine
from src.story_engine.interaction import InteractionEngine, EmotionEngine, HumorEngine
from src.story_engine.reinforcement import ReinforcementEngine, VocabularyEngine
from src.story_engine.validation import StoryValidationEngine
from src.story_engine.diversity import DiversityEngine
from src.story_engine.continuity import ContinuityTracker
from src.story_engine.catalog import StoryCatalog


class EpisodeGenerator:
    def __init__(self, catalog_path: Optional[str] = "catalog.db"):
        catalog = StoryCatalog(catalog_path)
        self.catalog = catalog
        self.curriculum = CurriculumEngine()
        self.theme_engine = ThemeEngine()
        self.learning_objective = LearningObjectiveEngine()
        self.character = CharacterEngine(catalog=catalog)
        self.relationship = RelationshipEngine(self.character)
        self.world = WorldEngine(catalog=catalog)
        self.asset = AssetEngine(catalog=catalog)
        self.conflict = ConflictEngine()
        self.resolution = ResolutionEngine()
        self.narrative = NarrativeEngine()
        self.dialogue = DialogueEngine()
        self.song = SongEngine()
        self.interaction = InteractionEngine()
        self.emotion = EmotionEngine()
        self.humor = HumorEngine()
        self.reinforcement = ReinforcementEngine()
        self.vocabulary = VocabularyEngine()
        self.validation = StoryValidationEngine()
        self.diversity = DiversityEngine()
        self.continuity = ContinuityTracker()

    def generate_episode(
        self,
        season: int = 1,
        episode_number: int = 1,
        exclude: Optional[Dict] = None,
        holiday: Optional[str] = None,
        target_age: str = "2-5",
        difficulty: int = 1,
    ) -> EpisodeBlueprint:
        exclude = exclude or {}
        exclude_areas = exclude.get("curriculum_areas", [])
        exclude_chars = exclude.get("characters", [])
        exclude_locs = exclude.get("locations", [])
        exclude_themes = exclude.get("themes", [])
        exclude_objectives = exclude.get("objectives", [])

        curriculum_area = self.curriculum.select_area(exclude=exclude_areas)
        if curriculum_area is None:
            curriculum_area = self.curriculum.get_area("numbers")

        objective: Optional[LearningObjective] = None
        if curriculum_area:
            objective = self.learning_objective.select_objective(
                area_id=curriculum_area.id, difficulty=difficulty, exclude=exclude_objectives
            )
            if objective is None:
                objs = self.learning_objective.get_objectives_for_area(curriculum_area.id)
                objective = objs[0] if objs else None

        theme = self.theme_engine.select_theme(
            exclude=exclude_themes, holiday=holiday, season=None
        )
        if theme is None:
            theme = Theme(id="park-visit", name="Park Visit", description="")

        main_char_info = self.character.select_main_character(exclude=exclude_chars)
        main_char = main_char_info.character_id if main_char_info else "lily-bunny"

        supporting_infos = self.character.select_supporting(main_char, count=random.randint(2, 3))
        supporting_chars = [c.character_id for c in supporting_infos if c is not None][:3]
        if not supporting_chars:
            supporting_chars = ["ben-bear", "daisy-duck"]
        all_chars = [main_char] + supporting_chars

        season_name = self.world.select_season()
        location = self.world.select_location(exclude=exclude_locs)
        weather = self.world.select_weather(season=season_name)

        grammar = self.narrative.grammar_library.select_grammar()
        structure = self.narrative.build_structure(grammar, objective, theme)
        normalized_beats = [self._normalize_beat(b) for b in structure]

        conflict_id = self.conflict.select_conflict(exclude=None, theme=theme.id)
        conflict_desc = conflict_id
        if hasattr(self.conflict, 'get_conflict_description'):
            conflict_desc = self.conflict.get_conflict_description(conflict_id)

        resolution_type = self.resolution.select_resolution(conflict=conflict_id, characters=all_chars)
        try:
            resolution_desc = self.resolution.generate_resolution_description(
                resolution_type=resolution_type,
                conflict=conflict_id,
                main_char=self._char_name(main_char_info),
                helper=self._char_name(supporting_infos[0]) if supporting_infos else None,
            )
        except Exception:
            resolution_desc = f"The friends work together and solve the problem through {resolution_type}."

        theme_assets = self.asset.get_assets_for_theme(theme.id)
        obj_id = objective.id if objective else ""
        obj_assets = self.asset.get_assets_for_objective(obj_id)
        assets = list(dict.fromkeys(theme_assets + obj_assets))
        if not assets:
            assets = ["play mat", "cushion", "story book"]

        has_song = self.song.should_include_song(
            themes_require_song=(theme.requires_song if theme else False)
        )
        song_placement: Optional[SongPlacement] = None
        if has_song and objective:
            placement = self.song.select_placement(len(structure))
            song_type = self.song.select_song_type(objective)
            song_placement = self.song.plan_song(
                placement=placement, song_type=song_type,
                objective=objective, main_character=self._char_name(main_char_info),
            )

        emotional_arc = self.emotion.generate_emotional_arc(normalized_beats)

        interactive_moments: List[InteractiveMoment] = []
        if objective:
            interactive_moments = self.interaction.plan_interactions(
                structure=normalized_beats, objective=objective, characters=all_chars,
            )

        dialogue: List[DialogueLine] = []
        if objective:
            dialogue.extend(self.dialogue.generate_intro(
                self._char_name(main_char_info), location, objective))
            dialogue.extend(self.dialogue.generate_teaching_moment(objective, all_chars))
            dialogue.extend(self.dialogue.generate_celebration(all_chars))
            dialogue.extend(self.dialogue.generate_goodbye(all_chars))

        humor_moment = self.humor.select_humor_moment(exclude=None, characters=all_chars)
        humor_moments = [humor_moment]

        repetition_count = self.reinforcement.calculate_repetition_count(
            difficulty=difficulty, age_range=target_age
        )
        vocab_level = self.vocabulary.get_vocabulary_level(target_age)

        title = self.narrative.generate_title(
            objective=objective, theme=theme,
            main_character=self._char_name(main_char_info),
        )
        description = self.narrative.generate_description(
            structure=structure, objective=objective, characters=all_chars,
        )

        episode_id = f"S{season:02d}E{episode_number:02d}"

        blueprint = EpisodeBlueprint(
            episode_id=episode_id,
            season=season,
            episode_number=episode_number,
            title=title,
            subtitle="",
            curriculum_area=curriculum_area.id if curriculum_area else "",
            learning_objective=objective.name if objective else "",
            theme=theme.id if theme else "",
            target_age=target_age,
            difficulty=difficulty,
            duration_minutes=3,
            has_song=has_song,
            song=song_placement,
            main_character=main_char,
            supporting_characters=supporting_chars,
            location=location,
            weather=weather,
            season_name=season_name,
            holiday=holiday or (theme.holiday if theme else None),
            assets=assets,
            story_grammar=grammar.id if grammar else "",
            narrative_structure=structure,
            conflict=conflict_desc,
            resolution=resolution_desc,
            dialogue=dialogue,
            interactive_moments=interactive_moments,
            emotional_arc=emotional_arc,
            humor_moments=humor_moments,
            reinforcement_count=repetition_count,
            vocabulary_level=vocab_level,
            keywords=objective.keywords if objective else [],
            curriculum_tags=[curriculum_area.id if curriculum_area else "", objective.id if objective else ""],
            language="en",
        )

        self._enrich_blueprint(blueprint, all_chars)

        return blueprint

    def _enrich_blueprint(
        self, blueprint: EpisodeBlueprint, all_chars: List[str]
    ) -> None:
        """Attach production catalog records to the blueprint, when available."""
        if self.catalog is None or not self.catalog.available:
            return
        blueprint.location_id = self.world.location_id(blueprint.location)
        zone = self.world.location_zone(blueprint.location)
        if zone:
            blueprint.location_zone = zone
        blueprint.asset_file_paths = self.asset.resolve_file_paths(blueprint.assets)
        blueprint.asset_ids = self.asset.resolve_asset_ids(blueprint.assets)
        blueprint.character_catalog = {
            char_id: record
            for char_id in all_chars
            for record in [self.character.catalog_info(char_id)]
            if record is not None
        }

    @staticmethod
    def _normalize_beat(beat: str) -> str:
        beat_lower = beat.lower().strip()
        mapping = [
            ("opening", "opening"),
            ("goal", "goal"),
            ("problem", "problem"),
            ("discovery", "discovery"),
            ("learning", "learning"),
            ("practice", "practice"),
            ("success", "success"),
            ("celebration", "celebration"),
            ("goodbye", "goodbye"),
            ("play", "play"),
            ("exploration", "exploration"),
            ("planning", "plan"),
            ("set out", "goal"),
            ("journey", "goal"),
            ("encounter", "exploration"),
            ("face", "problem"),
            ("challenge", "problem"),
            ("work as", "practice"),
            ("reflect", "learning"),
            ("return", "goodbye"),
            ("arrival", "exploration"),
            ("gathering", "plan"),
            ("construction", "practice"),
            ("preparation", "plan"),
            ("planting", "practice"),
            ("nurtur", "practice"),
            ("finding", "discovery"),
            ("realization", "discovery"),
            ("curiosity", "opening"),
            ("curious", "opening"),
            ("news", "opening"),
            ("idea", "opening"),
            ("music", "opening"),
            ("mess", "opening"),
            ("mixed up", "problem"),
            ("tricky", "problem"),
            ("wrong", "problem"),
            ("oops", "problem"),
            ("struggle", "problem"),
            ("breakthrough", "success"),
            ("demonstrat", "success"),
            ("perform", "celebration"),
            ("bow", "goodbye"),
        ]
        for pattern, replacement in mapping:
            if beat_lower.startswith(pattern) or pattern in beat_lower:
                return replacement
        return beat_lower

    @staticmethod
    def _char_name(char_info) -> str:
        if hasattr(char_info, 'name'):
            return char_info.name
        if hasattr(char_info, 'character_id'):
            return char_info.character_id
        return str(char_info)

    def generate_episode_from_scratch(self, **overrides) -> EpisodeBlueprint:
        blueprint = self.generate_episode()
        for key, value in overrides.items():
            if hasattr(blueprint, key):
                setattr(blueprint, key, value)
        return blueprint

    def generate_batch(
        self, count: int, **base_params
    ) -> List[EpisodeBlueprint]:
        episodes: List[EpisodeBlueprint] = []
        for i in range(count):
            episode_num = base_params.get("episode_number", 1) + i
            ep = self.generate_episode(
                season=base_params.get("season", 1),
                episode_number=episode_num,
                exclude=base_params.get("exclude"),
                holiday=base_params.get("holiday"),
                target_age=base_params.get("target_age", "2-5"),
                difficulty=base_params.get("difficulty", 1),
            )
            self.diversity.tracker.record(ep)
            self.continuity.record_episode(ep)
            episodes.append(ep)
        return episodes
