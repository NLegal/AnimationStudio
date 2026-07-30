from __future__ import annotations
import random
from typing import List, Optional

from src.story_engine.models import StoryGrammar, Theme, LearningObjective
from src.story_engine.grammar_data import ALL_GRAMMARS


DEFAULT_STRUCTURE: List[str] = [
    "Opening",
    "Goal",
    "Problem",
    "Discovery",
    "Learning",
    "Practice",
    "Success",
    "Celebration",
    "Goodbye",
]


class StoryGrammarLibrary:
    def __init__(self):
        self.grammars: dict = {g.id: g for g in ALL_GRAMMARS}

    def get_grammar(self, grammar_id: str) -> Optional[StoryGrammar]:
        return self.grammars.get(grammar_id)

    def list_grammars(self) -> List[StoryGrammar]:
        return list(self.grammars.values())

    def select_grammar(self, exclude: Optional[List[str]] = None) -> StoryGrammar:
        pool = list(self.grammars.values())
        if exclude:
            pool = [g for g in pool if g.id not in exclude]
        if not pool:
            pool = list(self.grammars.values())
        return random.choice(pool) if pool else list(self.grammars.values())[0]

    def register_grammar(self, grammar: StoryGrammar):
        self.grammars[grammar.id] = grammar


class NarrativeEngine:
    def __init__(self, grammar_library: Optional[StoryGrammarLibrary] = None):
        self.grammar_library = grammar_library or StoryGrammarLibrary()

    def build_structure(
        self,
        grammar: StoryGrammar,
        objective: LearningObjective,
        theme: Theme,
    ) -> List[str]:
        if grammar.structure:
            return list(grammar.structure)
        return list(DEFAULT_STRUCTURE)

    def generate_title(
        self,
        objective: LearningObjective,
        theme: Theme,
        main_character: str,
    ) -> str:
        theme_words = theme.name.title() if theme.name else "Adventure"
        objective_words = objective.name.title() if objective.name else "Learn"
        return f"{main_character} {objective_words}"

    def generate_description(
        self,
        structure: List[str],
        objective: LearningObjective,
        characters: List[str],
    ) -> str:
        char_names = ", ".join(characters)
        if not objective.name:
            objective_name = "something new"
        else:
            objective_name = objective.name.lower()

        beats = structure[0] if structure else "an adventure"
        return (
            f"In this episode, {char_names} come together for {beats.lower()} "
            f"and learn to {objective_name}. "
            f"Through fun and discovery, everyone grows a little smarter and a little kinder."
        )
