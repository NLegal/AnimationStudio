from __future__ import annotations
import random
from typing import Dict, List, Set

from src.story_engine.models import LearningObjective


class ReinforcementEngine:
    def __init__(self):
        self._example_generators: Dict[str, object] = {
            "counting": self._counting_examples,
            "numbers": self._counting_examples,
            "color": self._color_examples,
            "colors": self._color_examples,
            "shape": self._shape_examples,
            "shapes": self._shape_examples,
            "animal": self._animal_examples,
            "animals": self._animal_examples,
            "alphabet": self._alphabet_examples,
            "letters": self._alphabet_examples,
        }
        self._number_objects = [
            "apple", "balloon", "duck", "star", "flower", "block",
            "cookie", "crayon", "fish", "bird", "tree", "car",
        ]
        self._color_items = [
            ("red", ["apple", "balloon", "flower", "car"]),
            ("blue", ["sky", "water", "balloon", "bird"]),
            ("yellow", ["sun", "duck", "banana", "flower"]),
            ("green", ["frog", "tree", "leaf", "caterpillar"]),
            ("orange", ["orange", "fish", "carrot", "pumpkin"]),
            ("purple", ["grape", "flower", "balloon", "crayon"]),
        ]
        self._shape_items = [
            ("circle", ["sun", "ball", "wheel", "cookie"]),
            ("square", ["block", "window", "box", "tile"]),
            ("triangle", ["roof", "slice", "sign", "flag"]),
            ("star", ["starfish", "star fruit", "star toy", "night star"]),
            ("diamond", ["kite", "diamond ring", "diamond shape", "gem"]),
        ]
        self._animals = [
            "duck", "cow", "cat", "dog", "frog", "bird",
            "lion", "elephant", "fish", "bunny", "bear", "pig",
        ]

    def calculate_repetition_count(
        self, difficulty: int, age_range: str
    ) -> int:
        age_lower = self._parse_age_lower(age_range)
        base = 6 - age_lower
        base = max(3, min(7, base))
        bonus = min(difficulty, 3)
        return min(7, base + bonus)

    def identify_reinforcement_moments(
        self, structure: List[str]
    ) -> List[int]:
        if not structure:
            return []
        target_beats = {"learning", "practice", "discovery", "play", "goal"}
        indices: List[int] = []
        for i, beat in enumerate(structure):
            if beat.lower() in target_beats:
                indices.append(i)
        if not indices:
            step = max(1, len(structure) // 3)
            indices = list(range(0, len(structure), step))
        return indices

    def suggest_examples(
        self, objective: LearningObjective, count: int
    ) -> List[str]:
        kw = objective.name.lower() if objective.name else ""
        curriculum = objective.curriculum_area.lower() if objective.curriculum_area else ""
        for key, generator_fn in self._example_generators.items():
            if key in kw or key in curriculum:
                return generator_fn(count)
        return self._generic_examples(count)

    def _parse_age_lower(self, age_range: str) -> int:
        try:
            parts = age_range.replace(" ", "").split("-")
            return int(parts[0])
        except (ValueError, IndexError):
            return 2

    def _counting_examples(self, count: int) -> List[str]:
        number = min(count, 10)
        examples: List[str] = []
        for i in range(count):
            obj = random.choice(self._number_objects)
            examples.append(f"{number} {obj}{'s' if number != 1 else ''}")
        return examples

    def _color_examples(self, count: int) -> List[str]:
        examples: List[str] = []
        for _ in range(count):
            color_name, items = random.choice(self._color_items)
            item = random.choice(items)
            examples.append(f"{color_name} {item}")
        return examples

    def _shape_examples(self, count: int) -> List[str]:
        examples: List[str] = []
        for _ in range(count):
            shape_name, items = random.choice(self._shape_items)
            item = random.choice(items)
            examples.append(f"{shape_name} {item}")
        return examples

    def _animal_examples(self, count: int) -> List[str]:
        examples: List[str] = []
        sounds = {
            "duck": "quack", "cow": "moo", "cat": "meow",
            "dog": "woof", "frog": "ribbit", "bird": "tweet",
            "lion": "roar", "elephant": "trumpet", "pig": "oink",
        }
        for _ in range(count):
            animal = random.choice(self._animals)
            sound = sounds.get(animal, "sound")
            examples.append(f"{animal} goes {sound}")
        return examples

    def _alphabet_examples(self, count: int) -> List[str]:
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        letter_words = {
            "A": "apple", "B": "ball", "C": "cat", "D": "duck",
            "E": "egg", "F": "fish", "G": "goat", "H": "hat",
            "I": "igloo", "J": "jump", "K": "kite", "L": "lion",
            "M": "moon", "N": "nest", "O": "ocean", "P": "pig",
            "Q": "queen", "R": "rain", "S": "sun", "T": "tree",
            "U": "umbrella", "V": "van", "W": "water", "X": "fox",
            "Y": "yellow", "Z": "zebra",
        }
        examples: List[str] = []
        for i in range(min(count, 26)):
            letter = letters[i % 26]
            word = letter_words.get(letter, "something")
            examples.append(f"{letter} is for {word}")
        return examples

    def _generic_examples(self, count: int) -> List[str]:
        return [f"example {i + 1}" for i in range(count)]


class VocabularyEngine:
    def __init__(self):
        self._age_levels: Dict[str, str] = {
            "2": "one_word",
            "2-3": "two_word",
            "3": "two_word",
            "3-4": "simple_sentence",
            "4": "simple_sentence",
            "4-5": "simple_sentence",
            "5": "longer_conversation",
            "5-6": "longer_conversation",
            "6": "longer_conversation",
        }
        self._max_sentence_lengths: Dict[str, int] = {
            "one_word": 1,
            "two_word": 3,
            "simple_sentence": 7,
            "longer_conversation": 12,
        }
        self._age_2_words: Set[str] = {
            "apple", "ball", "cat", "dog", "duck", "eat", "fish",
            "go", "hat", "in", "jump", "kiss", "look", "milk",
            "no", "on", "play", "run", "sleep", "tree", "up",
            "water", "yes", "baby", "book", "car", "doll", "eye",
            "foot", "hand", "head", "nose", "toe", "sun", "moon",
            "star", "bed", "cup", "door", "bird", "bug", "ant",
            "big", "hot", "cold", "wet", "dry", "good", "bye",
            "hi", "love", "mom", "dad", "balloon", "cake", "candy",
            "hair", "shoe", "sock", "bath", "soap", "towel",
        }
        self._age_3_words: Set[str] = {
            "apple", "ball", "bear", "bunny", "cat", "dog", "duck",
            "eat", "fish", "go", "hat", "house", "jump", "look",
            "milk", "play", "run", "sleep", "tree", "water",
            "baby", "book", "car", "doll", "sun", "moon", "star",
            "bed", "cup", "door", "bird", "big", "small", "red",
            "blue", "yellow", "green", "one", "two", "three",
            "hello", "goodbye", "happy", "sad", "love", "mom",
            "dad", "friend", "balloon", "cake", "candy", "shoe",
            "sock", "bath", "soap", "towel", "chair", "table",
            "flower", "rain", "snow", "wind", "kite",
        }
        self._age_4_words: Set[str] = {
            "apple", "ball", "bear", "bunny", "cat", "dog", "duck",
            "eat", "fish", "go", "hat", "house", "jump", "look",
            "milk", "play", "run", "sleep", "tree", "water",
            "baby", "book", "car", "doll", "sun", "moon", "star",
            "bed", "cup", "door", "bird", "big", "small", "red",
            "blue", "yellow", "green", "one", "two", "three",
            "four", "five", "hello", "goodbye", "happy", "sad",
            "love", "mom", "dad", "friend", "balloon", "cake",
            "candy", "shoe", "sock", "bath", "soap", "towel",
            "chair", "table", "flower", "rain", "snow", "wind",
            "kite", "orange", "purple", "circle", "square",
            "triangle", "star", "heart", "duckling", "chick",
            "puppy", "kitten", "garden", "kitchen", "bedroom",
            "school", "park", "zoo", "farm", "beach", "ocean",
            "please", "thank", "sorry", "share", "help", "clean",
            "wash", "brush", "comb",
        }

    def get_vocabulary_level(self, age_range: str) -> str:
        key = age_range.strip()
        if key in self._age_levels:
            return self._age_levels[key]
        for k, v in self._age_levels.items():
            if k in key or key in k:
                return v
        return "simple_sentence"

    def get_max_sentence_length(self, age_range: str) -> int:
        level = self.get_vocabulary_level(age_range)
        return self._max_sentence_lengths.get(level, 7)

    def simplify_text(self, text: str, age_range: str) -> str:
        max_words = self.get_max_sentence_length(age_range)
        sentences = text.replace("!", ".").replace("?", ".").split(".")
        simplified: List[str] = []
        for sentence in sentences:
            words = sentence.strip().split()
            if not words:
                continue
            truncated = words[:max_words]
            simplified.append(" ".join(truncated))
        return ". ".join(simplified).strip() + "."

    def get_age_appropriate_words(self, age_range: str) -> List[str]:
        age_lower = self._parse_age_lower(age_range)
        if age_lower <= 2:
            return sorted(self._age_2_words)
        if age_lower <= 3:
            return sorted(self._age_3_words)
        if age_lower <= 4:
            return sorted(self._age_4_words)
        return sorted(self._age_4_words)

    def is_age_appropriate(self, word: str, age_range: str) -> bool:
        approved = self.get_age_appropriate_words(age_range)
        return word.lower().strip() in approved

    def _parse_age_lower(self, age_range: str) -> int:
        try:
            parts = age_range.replace(" ", "").split("-")
            return int(parts[0])
        except (ValueError, IndexError):
            return 2
