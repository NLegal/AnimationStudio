from typing import List
from src.story_engine.models import EpisodeBlueprint

class StoryValidationEngine:
    def validate(self, blueprint: EpisodeBlueprint) -> List[str]:
        issues: List[str] = []
        self._check_educational_objective(blueprint, issues)
        self._check_positive_ending(blueprint, issues)
        self._check_character_consistency(blueprint, issues)
        self._check_world_consistency(blueprint, issues)
        self._check_asset_availability(blueprint, issues)
        self._check_safe_content(blueprint, issues)
        self._check_age_appropriate_vocabulary(blueprint, issues)
        self._check_interactive_moments(blueprint, issues)
        self._check_song_placement(blueprint, issues)
        self._check_positive_emotional_arc(blueprint, issues)
        return issues

    def _check_educational_objective(self, blueprint, issues):
        if not blueprint.learning_objective:
            issues.append("Educational objective present: FAILED - no learning objective set")

    def _check_positive_ending(self, blueprint, issues):
        positive_endings = ["celebration", "success", "happy", "goodbye"]
        if blueprint.narrative_structure:
            last_beat = blueprint.narrative_structure[-1].lower()
            if not any(p in last_beat for p in positive_endings):
                issues.append(f"Positive ending: FAILED - last narrative beat '{last_beat}' is not positive")
        else:
            issues.append("Positive ending: FAILED - no narrative structure")

    def _check_character_consistency(self, blueprint, issues):
        if not blueprint.main_character:
            issues.append("Character consistency: FAILED - no main character set")
        if not blueprint.supporting_characters:
            issues.append("Character consistency: WARNING - no supporting characters")

    def _check_world_consistency(self, blueprint, issues):
        if not blueprint.location:
            issues.append("World consistency: FAILED - no location set")

    def _check_asset_availability(self, blueprint, issues):
        if not blueprint.assets:
            issues.append("Asset availability: FAILED - no assets selected")

    def _check_safe_content(self, blueprint, issues):
        unsafe_keywords = [
            "scary", "danger", "hurt", "fire", "crash",
            "monster", "stranger danger", "poison", "sharp",
            "bleeding", "sick", "injury", "violent", "weapon",
            "alcohol", "drug", "gambling", "death", "crime",
            "bullying", "politics", "religion",
        ]
        conflict_lower = (blueprint.conflict or "").lower()
        for kw in unsafe_keywords:
            if kw in conflict_lower:
                issues.append(f"Safe content: FAILED - conflict contains unsafe keyword '{kw}'")
                break

    def _check_age_appropriate_vocabulary(self, blueprint, issues):
        valid_levels = ["one_word", "two_word", "simple_sentence", "longer_conversation"]
        if blueprint.vocabulary_level not in valid_levels:
            issues.append(f"Age-appropriate vocabulary: WARNING - unknown level '{blueprint.vocabulary_level}'")

    def _check_interactive_moments(self, blueprint, issues):
        if len(blueprint.interactive_moments) < 1:
            issues.append("Interactive moments: FAILED - at least 1 interactive moment required")

    def _check_song_placement(self, blueprint, issues):
        if blueprint.has_song and blueprint.song is None:
            issues.append("Song placement: FAILED - episode has_song=True but no song defined")
        if blueprint.song and not blueprint.song.position:
            issues.append("Song placement: FAILED - song has no position set")

    def _check_positive_emotional_arc(self, blueprint, issues):
        if not blueprint.emotional_arc:
            issues.append("Positive emotional arc: FAILED - no emotional arc defined")
            return
        positive_end_emotions = {"celebration", "happy", "success", "proud", "warm", "excited"}
        last_emotion = blueprint.emotional_arc[-1].lower()
        if last_emotion not in positive_end_emotions:
            issues.append(f"Positive emotional arc: FAILED - ends with '{last_emotion}' instead of a positive emotion")
