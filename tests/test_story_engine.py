from __future__ import annotations
import os
from typing import List

import pytest

from src.story_engine.curriculum import CurriculumEngine
from src.story_engine.theme import ThemeEngine
from src.story_engine.learning_objective import LearningObjectiveEngine
from src.story_engine.casting import CharacterEngine, RelationshipEngine
from src.story_engine.world import WorldEngine
from src.story_engine.asset import AssetEngine
from src.story_engine.plot import ConflictEngine, ResolutionEngine
from src.story_engine.narrative import NarrativeEngine, StoryGrammarLibrary
from src.story_engine.dialogue import DialogueEngine
from src.story_engine.song import SongEngine
from src.story_engine.interaction import InteractionEngine, EmotionEngine, HumorEngine
from src.story_engine.reinforcement import ReinforcementEngine, VocabularyEngine
from src.story_engine.generator import EpisodeGenerator
from src.story_engine.validation import StoryValidationEngine
from src.story_engine.continuity import ContinuityTracker
from src.story_engine.diversity import DiversityEngine
from src.story_engine.planner import SeriesPlanner
from src.story_engine.consistency import check_docs, quality_checklist
from src.story_engine.models import (
    CurriculumArea, LearningObjective, Theme, StoryGrammar,
    CharacterInfo, DialogueLine, InteractiveMoment, SongPlacement,
    EpisodeBlueprint, SeasonPlan, SeriesPlan, DiversityTracker,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ======================================================================
# TestCurriculumEngine
# ======================================================================

class TestCurriculumEngine:
    def setup_method(self):
        self.engine = CurriculumEngine()

    def test_select_area_returns_area(self):
        area = self.engine.select_area()
        assert area is not None
        assert isinstance(area, CurriculumArea)
        assert area.id
        assert area.name

    def test_list_areas(self):
        areas = self.engine.list_areas()
        assert len(areas) > 5
        assert all(isinstance(a, CurriculumArea) for a in areas)

    def test_get_area(self):
        area = self.engine.get_area("numbers")
        assert area is not None
        assert area.id == "numbers"
        assert area.name == "Numbers"

    def test_area_topics(self):
        area = self.engine.get_area("colors")
        assert area is not None
        assert len(area.topics) > 0
        assert "Red & Blue" in area.topics


# ======================================================================
# TestThemeEngine
# ======================================================================

class TestThemeEngine:
    def setup_method(self):
        self.engine = ThemeEngine()

    def test_select_theme(self):
        theme = self.engine.select_theme()
        assert theme is not None
        assert isinstance(theme, Theme)
        assert theme.id

    def test_holiday_theme_filtering(self):
        theme = self.engine.select_theme(holiday="halloween")
        assert theme is not None
        assert theme.holiday == "halloween"

    def test_season_theme_filtering(self):
        theme = self.engine.select_theme(season="summer")
        assert theme is not None
        assert theme.season == "summer"


# ======================================================================
# TestLearningObjectiveEngine
# ======================================================================

class TestLearningObjectiveEngine:
    def setup_method(self):
        self.engine = LearningObjectiveEngine()

    def test_select_objective(self):
        obj = self.engine.select_objective(area_id="numbers")
        assert obj is not None
        assert isinstance(obj, LearningObjective)
        assert obj.curriculum_area == "numbers"

    def test_objectives_for_area(self):
        objs = self.engine.get_objectives_for_area("colors")
        assert len(objs) >= 2
        assert all(o.curriculum_area == "colors" for o in objs)

    def test_difficulty_filtering(self):
        obj = self.engine.select_objective(area_id="numbers", difficulty=3)
        assert obj is not None
        assert obj.difficulty >= 1


# ======================================================================
# TestCharacterEngine
# ======================================================================

class TestCharacterEngine:
    def setup_method(self):
        self.engine = CharacterEngine()

    def test_select_main_character(self):
        char = self.engine.select_main_character()
        assert char is not None
        assert isinstance(char, CharacterInfo)
        assert char.character_id

    def test_select_supporting(self):
        main_info = self.engine.select_main_character()
        supporters = self.engine.select_supporting(main_info.character_id, count=2)
        assert isinstance(supporters, list)
        assert len(supporters) == 2

    def test_get_character(self):
        char = self.engine.get_character("lily-bunny")
        assert char is not None
        assert isinstance(char, CharacterInfo)
        assert char.name == "Lily Bunny"


# ======================================================================
# TestRelationshipEngine
# ======================================================================

class TestRelationshipEngine:
    def setup_method(self):
        self.char_engine = CharacterEngine()
        self.engine = RelationshipEngine(self.char_engine)

    def test_get_relationship(self):
        rel = self.engine.get_relationship("lily-bunny", "ben-bear")
        assert rel is not None
        assert "friend" in rel.lower()

    def test_are_connected(self):
        assert self.engine.are_connected("lily-bunny", "ben-bear") is True


# ======================================================================
# TestWorldEngine
# ======================================================================

class TestWorldEngine:
    def setup_method(self):
        self.engine = WorldEngine()

    def test_select_location(self):
        loc = self.engine.select_location()
        assert isinstance(loc, str)
        assert loc

    def test_select_weather(self):
        weather = self.engine.select_weather(season="spring")
        assert isinstance(weather, str)
        assert weather

    def test_get_locations_for_zone(self):
        locs = self.engine.get_locations_for_zone("Residential")
        assert isinstance(locs, list)
        assert len(locs) > 0


# ======================================================================
# TestAssetEngine
# ======================================================================

class TestAssetEngine:
    def setup_method(self):
        self.engine = AssetEngine()

    def test_select_assets_for_theme(self):
        assets = self.engine.get_assets_for_theme("birthday")
        assert isinstance(assets, list)
        assert len(assets) > 0

    def test_assets_for_objective(self):
        assets = self.engine.get_assets_for_objective("count_to_five")
        assert isinstance(assets, list)
        assert len(assets) > 0


# ======================================================================
# TestConflictEngine
# ======================================================================

class TestConflictEngine:
    def setup_method(self):
        self.engine = ConflictEngine()

    def test_select_conflict(self):
        conflict = self.engine.select_conflict()
        assert isinstance(conflict, str)
        assert conflict


# ======================================================================
# TestResolutionEngine
# ======================================================================

class TestResolutionEngine:
    def setup_method(self):
        self.engine = ResolutionEngine()

    def test_select_resolution(self):
        resolution = self.engine.select_resolution(
            conflict="lost_balloon", characters=["lily-bunny", "ben-bear"]
        )
        assert isinstance(resolution, str)
        assert resolution

    def test_generate_resolution_description(self):
        desc = self.engine.generate_resolution_description(
            resolution_type="friend_helps",
            conflict="lost_balloon",
            main_char="lily-bunny",
            helper="ben-bear",
        )
        assert isinstance(desc, str)
        assert len(desc) > 10


# ======================================================================
# TestNarrativeEngine
# ======================================================================

class TestNarrativeEngine:
    def setup_method(self):
        self.engine = NarrativeEngine()

    def _make_objects(self):
        grammar = StoryGrammar(
            id="find_something", name="Find Something",
            structure=["Opening", "Problem", "Learning", "Success", "Celebration", "Goodbye"],
        )
        objective = LearningObjective(
            id="count-to-5", curriculum_area="numbers", name="Count to 5",
        )
        theme = Theme(id="birthday", name="Birthday", description="")
        return grammar, objective, theme

    def test_build_structure(self):
        grammar, obj, theme = self._make_objects()
        structure = self.engine.build_structure(grammar, obj, theme)
        assert isinstance(structure, list)
        assert len(structure) >= 4
        assert "Opening" in structure[0] or "opening" in structure[0].lower()

    def test_generate_title(self):
        _, obj, theme = self._make_objects()
        title = self.engine.generate_title(
            objective=obj, theme=theme, main_character="Lily Bunny"
        )
        assert isinstance(title, str)
        assert len(title) > 0

    def test_generate_description(self):
        grammar, obj, theme = self._make_objects()
        structure = self.engine.build_structure(grammar, obj, theme)
        desc = self.engine.generate_description(
            structure=structure, objective=obj, characters=["Lily Bunny", "Ben Bear"]
        )
        assert isinstance(desc, str)
        assert len(desc) > 10


# ======================================================================
# TestStoryGrammarLibrary
# ======================================================================

class TestStoryGrammarLibrary:
    def setup_method(self):
        self.library = StoryGrammarLibrary()

    def test_list_grammars(self):
        grammars = self.library.list_grammars()
        assert isinstance(grammars, list)
        assert len(grammars) > 5
        assert all(isinstance(g, StoryGrammar) for g in grammars)

    def test_get_grammar(self):
        grammar = self.library.get_grammar("learn_something")
        assert grammar is not None
        assert isinstance(grammar, StoryGrammar)
        assert grammar.name == "Learn Something"


# ======================================================================
# TestDialogueEngine
# ======================================================================

class TestDialogueEngine:
    def setup_method(self):
        self.engine = DialogueEngine()

    def _make_objective(self, name="Count to 5", area="numbers"):
        return LearningObjective(
            id="count-to-5", curriculum_area=area, name=name,
            description="", difficulty=1, age_range="2-5",
        )

    def test_generate_intro(self):
        obj = self._make_objective()
        lines = self.engine.generate_intro("Lily Bunny", "Playground", obj)
        assert isinstance(lines, list)
        assert len(lines) >= 1
        assert all(isinstance(l, DialogueLine) for l in lines)

    def test_generate_teaching_moment(self):
        obj = self._make_objective()
        lines = self.engine.generate_teaching_moment(obj, ["Lily", "Ben"])
        assert isinstance(lines, list)
        assert len(lines) >= 1
        assert all(isinstance(l, DialogueLine) for l in lines)

    def test_generate_goodbye(self):
        lines = self.engine.generate_goodbye(["Lily", "Ben"])
        assert isinstance(lines, list)
        assert len(lines) >= 1
        assert all(isinstance(l, DialogueLine) for l in lines)


# ======================================================================
# TestSongEngine
# ======================================================================

class TestSongEngine:
    def setup_method(self):
        self.engine = SongEngine()

    def test_should_include_song(self):
        assert self.engine.should_include_song(themes_require_song=True) is True
        result = self.engine.should_include_song(themes_require_song=False)
        assert isinstance(result, bool)

    def test_select_placement(self):
        placement = self.engine.select_placement(structure_length=8)
        assert isinstance(placement, str)
        assert placement in ["opening", "middle", "ending", "transition", "full_episode"]

    def test_plan_song(self):
        obj = LearningObjective(
            id="count-to-5", curriculum_area="numbers", name="Count to 5",
        )
        song = self.engine.plan_song(
            placement="middle", song_type="counting",
            objective=obj, main_character="Lily Bunny",
        )
        assert isinstance(song, SongPlacement)
        assert song.position == "middle"
        assert song.song_type == "counting"


# ======================================================================
# TestInteractionEngine
# ======================================================================

class TestInteractionEngine:
    def setup_method(self):
        self.engine = InteractionEngine()

    def _make_objective(self, name="Count to 5", area="numbers"):
        return LearningObjective(
            id="count-to-5", curriculum_area=area, name=name,
            description="", difficulty=1, age_range="2-5",
        )

    def test_plan_interactions(self):
        obj = self._make_objective()
        structure = ["Opening", "Goal", "Problem", "Learning", "Practice", "Success", "Celebration"]
        moments = self.engine.plan_interactions(structure, obj, ["Lily", "Ben"])
        assert isinstance(moments, list)
        assert len(moments) >= 1
        assert all(isinstance(m, InteractiveMoment) for m in moments)

    def test_generate_counting_moment(self):
        obj = self._make_objective()
        moment = self.engine.generate_counting_moment(obj)
        assert isinstance(moment, InteractiveMoment)
        assert "count" in moment.prompt.lower()


# ======================================================================
# TestEmotionEngine
# ======================================================================

class TestEmotionEngine:
    def setup_method(self):
        self.engine = EmotionEngine()

    def test_generate_emotional_arc(self):
        structure = ["Opening", "Goal", "Problem", "Learning", "Success", "Celebration", "Goodbye"]
        arc = self.engine.generate_emotional_arc(structure)
        assert isinstance(arc, list)
        assert len(arc) == len(structure)
        assert all(isinstance(e, str) for e in arc)

    def test_get_emotion_intensity(self):
        intensity = self.engine.get_emotion_intensity("celebration", story_position=0.8)
        assert isinstance(intensity, int)
        assert 1 <= intensity <= 5


# ======================================================================
# TestHumorEngine
# ======================================================================

class TestHumorEngine:
    def setup_method(self):
        self.engine = HumorEngine()

    def test_select_humor_moment(self):
        moment = self.engine.select_humor_moment(exclude=None, characters=["lily-bunny"])
        assert isinstance(moment, str)
        assert moment


# ======================================================================
# TestReinforcementEngine
# ======================================================================

class TestReinforcementEngine:
    def setup_method(self):
        self.engine = ReinforcementEngine()

    def test_calculate_repetition_count(self):
        count = self.engine.calculate_repetition_count(difficulty=1, age_range="2-5")
        assert isinstance(count, int)
        assert 3 <= count <= 7


# ======================================================================
# TestVocabularyEngine
# ======================================================================

class TestVocabularyEngine:
    def setup_method(self):
        self.engine = VocabularyEngine()

    def test_get_vocabulary_level(self):
        level = self.engine.get_vocabulary_level("2-3")
        assert isinstance(level, str)
        assert level == "two_word"

    def test_simplify_text(self):
        text = "Hello everyone this is a very long sentence for young children to understand."
        simplified = self.engine.simplify_text(text, "2-3")
        assert isinstance(simplified, str)
        assert len(simplified.split()) <= 10


# ======================================================================
# TestEpisodeGenerator
# ======================================================================

class TestEpisodeGenerator:
    def setup_method(self):
        self.generator = EpisodeGenerator()

    def test_generate_episode_returns_valid_blueprint(self):
        blueprint = self.generator.generate_episode(
            season=1, episode_number=1, target_age="2-5", difficulty=1
        )
        assert isinstance(blueprint, EpisodeBlueprint)
        assert blueprint.episode_id == "S01E01"
        assert blueprint.season == 1
        assert blueprint.episode_number == 1
        assert blueprint.learning_objective
        assert blueprint.main_character
        assert blueprint.location
        assert blueprint.conflict
        assert blueprint.resolution
        assert len(blueprint.assets) > 0
        assert len(blueprint.narrative_structure) > 0

    def test_validate_method(self):
        blueprint = self.generator.generate_episode()
        validator = StoryValidationEngine()
        issues = validator.validate(blueprint)
        assert isinstance(issues, list)

    def test_batch_generation(self):
        blueprints = self.generator.generate_batch(count=3, season=1)
        assert isinstance(blueprints, list)
        assert len(blueprints) == 3
        assert all(isinstance(b, EpisodeBlueprint) for b in blueprints)


# ======================================================================
# TestStoryValidationEngine
# ======================================================================

class TestStoryValidationEngine:
    def setup_method(self):
        self.validator = StoryValidationEngine()

    def test_valid_episode_passes(self):
        gen = EpisodeGenerator()
        blueprint = gen.generate_episode()
        issues = self.validator.validate(blueprint)
        assert isinstance(issues, list)

    def test_missing_objective_fails(self):
        blueprint = EpisodeBlueprint(
            episode_id="S01E99",
            learning_objective="",
            main_character="lily-bunny",
            location="Park",
            conflict="Lost Balloon",
            resolution="Friend Helps",
            narrative_structure=["Opening", "Goal", "Success", "Celebration", "Goodbye"],
            assets=["Balloon"],
            interactive_moments=[InteractiveMoment(prompt="Count?", expected_reaction="count", pause_duration=2.0)],
            emotional_arc=["curiosity", "excitement", "success", "celebration", "happy"],
            vocabulary_level="simple_sentence",
        )
        issues = self.validator.validate(blueprint)
        assert any("educational objective" in i.lower() for i in issues)

    def test_safety_check(self):
        blueprint = EpisodeBlueprint(
            episode_id="S01E99",
            learning_objective="Count to 5",
            conflict="Scary monster in the dark",
            main_character="lily-bunny",
            location="Park",
            resolution="Friend Helps",
            narrative_structure=["Opening", "Goal", "Success", "Celebration", "Goodbye"],
            assets=["Balloon"],
            interactive_moments=[InteractiveMoment(prompt="Count?", expected_reaction="count", pause_duration=2.0)],
            emotional_arc=["curiosity", "excitement", "success", "celebration", "happy"],
            vocabulary_level="simple_sentence",
        )
        issues = self.validator.validate(blueprint)
        assert any("safe content" in i.lower() for i in issues)


# ======================================================================
# TestContinuityTracker
# ======================================================================

class TestContinuityTracker:
    def test_record_and_check_consistency(self):
        engine = ContinuityTracker()

        bp1 = EpisodeBlueprint(
            episode_id="S01E01", season=1, episode_number=1,
            main_character="lily-bunny",
            supporting_characters=["ben-bear"],
            location="Park",
            learning_objective="Count to 5",
        )
        engine.record_episode(bp1)
        assert engine.get_episode_count("lily-bunny") == 1
        assert engine.get_last_location("lily-bunny") == "Park"

        bp2 = EpisodeBlueprint(
            episode_id="S01E02", season=1, episode_number=2,
            main_character="lily-bunny",
            supporting_characters=["daisy-duck"],
            location="Beach",
            learning_objective="Recognize Blue",
        )
        issues = engine.check_consistency(bp2)
        assert len(issues) >= 1


# ======================================================================
# TestDiversityEngine
# ======================================================================

class TestDiversityEngine:
    def test_check_diversity_with_repeated_content(self):
        engine = DiversityEngine()

        bp1 = EpisodeBlueprint(
            episode_id="S01E01",
            main_character="lily-bunny",
            supporting_characters=["ben-bear"],
            location="Park",
            theme="birthday",
            learning_objective="Count to 5",
        )
        engine.tracker.record(bp1)

        bp2 = EpisodeBlueprint(
            episode_id="S01E02",
            main_character="lily-bunny",
            supporting_characters=["ben-bear"],
            location="Park",
            theme="birthday",
            learning_objective="Count to 5",
        )
        warnings = engine.check_diversity(bp2)
        assert len(warnings) >= 1


# ======================================================================
# TestSeriesPlanner
# ======================================================================

class TestSeriesPlanner:
    def test_plan_season_generates_correct_episode_count(self):
        planner = SeriesPlanner()
        season_plan = planner.plan_season(season_number=1, episode_count=5)
        assert isinstance(season_plan, SeasonPlan)
        assert len(season_plan.episodes) == 5
        assert season_plan.season_number == 1
        assert season_plan.title == "Meet the Characters"


# ======================================================================
# TestEpisodeBlueprint
# ======================================================================

class TestEpisodeBlueprint:
    def test_validate_method(self):
        bp = EpisodeBlueprint()
        issues = bp.validate()
        assert len(issues) > 0

        bp = EpisodeBlueprint(
            learning_objective="Count to 5",
            main_character="lily-bunny",
            location="Park",
            conflict="Lost Balloon",
            resolution="Friend Helps",
        )
        issues = bp.validate()
        assert len(issues) == 0


# ======================================================================
# TestDocConsistency
# ======================================================================

class TestDocConsistency:
    def test_check_docs_passes(self):
        report = check_docs(os.path.join(ROOT, "StoryEngine"))
        d = report.to_dict()
        assert d["passed"], d["facts_failed"]
        assert d["facts_checked"] == 21
        assert d["facts_passed"] == 21
        assert d["missing_files"] == []

    def test_check_docs_prefix_stripping(self):
        report = check_docs(os.path.join(ROOT, "StoryEngine"))
        assert report.to_dict()["facts_passed"] == 21

    def test_check_docs_missing_dir(self):
        report = check_docs("/tmp/does_not_exist_story_engine")
        assert not report.to_dict()["passed"]
        assert report.to_dict()["missing_files"]

    def test_quality_checklist(self):
        checks = quality_checklist()
        assert len(checks) == 14
        assert "One clear educational objective" in checks
        assert "Validation passed" in checks


# ======================================================================
# TestExtendedCurriculum
# ======================================================================

class TestExtendedCurriculum:
    def test_all_curriculum_areas_present(self):
        engine = CurriculumEngine()
        ids = {a.id for a in engine.list_areas()}
        assert len(ids) == 25
        assert {"alphabet", "geography", "nature", "music-rhythm", "daily-routines"} <= ids

    def test_new_area_objectives(self):
        loe = LearningObjectiveEngine()
        assert len(loe.get_objectives_for_area("nature")) >= 2
        assert len(loe.get_objectives_for_area("music-rhythm")) >= 2
        assert len(loe.get_objectives_for_area("daily-routines")) >= 2


# ======================================================================
# TestExtendedGrammarLibrary
# ======================================================================

class TestExtendedGrammarLibrary:
    def test_fourteen_grammars(self):
        library = StoryGrammarLibrary()
        grammars = library.list_grammars()
        assert len(grammars) == 14

    def test_solve_a_puzzle_grammar(self):
        library = StoryGrammarLibrary()
        grammar = library.get_grammar("solve_a_puzzle")
        assert grammar is not None
        assert grammar.name == "Solve a Puzzle"
        assert "clues" in " ".join(grammar.structure).lower()


# ======================================================================
# TestThemeAssetResolution
# ======================================================================

class TestThemeAssetResolution:
    def test_all_themes_resolve_assets(self):
        engine = AssetEngine()
        themes = ThemeEngine()
        for theme in themes._themes:
            assert engine.get_assets_for_theme(theme.id), f"no assets for {theme.id}"

    def test_hyphen_and_underscore_forms(self):
        engine = AssetEngine()
        assert engine.get_assets_for_theme("lost-toy")
        assert engine.get_assets_for_theme("lost_toy")

    def test_park_visit_assets(self):
        engine = AssetEngine()
        assets = engine.get_assets_for_theme("park-visit")
        assert assets
        assert any("swing" in a or "slide" in a for a in assets)

    def test_all_themes_have_conflicts(self):
        engine = ConflictEngine()
        themes = ThemeEngine()
        for theme in themes._themes:
            assert theme.id in engine.conflicts_by_theme, f"no conflicts for {theme.id}"


# ======================================================================
# TestExtendedEpisodeGenerator
# ======================================================================

class TestExtendedEpisodeGenerator:
    def test_generate_episode_validates(self):
        generator = EpisodeGenerator()
        blueprint = generator.generate_episode()
        assert blueprint.learning_objective
        assert blueprint.assets
        assert blueprint.interactive_moments
        assert blueprint.story_grammar
