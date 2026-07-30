from __future__ import annotations
import random
from typing import Dict, List, Optional

from src.story_engine.models import InteractiveMoment, LearningObjective


class InteractionEngine:
    def __init__(self):
        self._question_templates = {
            "counting": [
                "Can you count the {object}s?",
                "How many {object}s do you see?",
                "Let us count {object}s together.",
            ],
            "color_id": [
                "What color is this?",
                "Can you find something {color}?",
                "Is this {color} or not?",
            ],
            "shape_id": [
                "What shape is this?",
                "Can you find a {shape}?",
                "Is this a {shape}?",
            ],
            "animal_sound": [
                "What sound does a {animal} make?",
                "Can you roar like a {animal}?",
                "How does a {animal} go?",
            ],
            "action": [
                "Can you {action}?",
                "Let us {action} together.",
                "Can you show me how to {action}?",
            ],
            "finding": [
                "Can you find the {object}?",
                "Where is the {object}?",
                "Do you see the {object}?",
            ],
        }
        self._default_objects = [
            "ball", "star", "apple", "duck", "flower", "tree",
            "balloon", "book", "car", "fish", "bird", "sun",
        ]
        self._default_colors = [
            "red", "blue", "yellow", "green", "orange", "purple",
        ]
        self._default_shapes = [
            "circle", "square", "triangle", "star", "diamond",
        ]
        self._default_animals = [
            "lion", "duck", "cow", "cat", "dog", "frog", "bird",
        ]
        self._default_actions = [
            "clap your hands",
            "stomp your feet",
            "wave hello",
            "wiggle your fingers",
            "jump up and down",
            "spin around",
            "nod your head",
            "blow a kiss",
        ]

    def plan_interactions(
        self,
        structure: List[str],
        objective: LearningObjective,
        characters: List[str],
    ) -> List[InteractiveMoment]:
        interaction_count = min(len(structure) // 2, 4)
        interaction_count = max(interaction_count, 2)
        if len(structure) <= interaction_count:
            step = 1
        else:
            step = len(structure) // interaction_count
        indices = list(range(0, len(structure), step))[:interaction_count]
        moments: List[InteractiveMoment] = []
        for idx in indices:
            beat = structure[idx].lower() if idx < len(structure) else "learning"
            moment = self._moment_for_beat(beat, objective)
            moments.append(moment)
        return moments

    def generate_counting_moment(
        self, objective: LearningObjective
    ) -> InteractiveMoment:
        obj = random.choice(self._default_objects)
        prompt = f"Can you count the {obj}s?"
        return InteractiveMoment(
            prompt=prompt,
            expected_reaction="count out loud",
            pause_duration=3.0,
            moment_type="counting",
        )

    def generate_action_moment(self, action: str) -> InteractiveMoment:
        prompt = f"Can you {action}?"
        return InteractiveMoment(
            prompt=prompt,
            expected_reaction=f"{action}",
            pause_duration=2.5,
            moment_type="action",
        )

    def _moment_for_beat(
        self, beat: str, objective: LearningObjective
    ) -> InteractiveMoment:
        kw = objective.name.lower() if objective.name else ""
        curriculum = objective.curriculum_area.lower() if objective.curriculum_area else ""
        if "count" in kw or "number" in kw or "count" in curriculum:
            return self._counting_moment(objective)
        if "color" in kw or "color" in curriculum:
            return self._color_moment(objective)
        if "shape" in kw or "shape" in curriculum:
            return self._shape_moment(objective)
        if "animal" in kw or "animal" in curriculum:
            return self._animal_moment(objective)
        if beat in ("goal", "problem", "discovery"):
            return self._finding_moment()
        if beat in ("learning", "practice", "play"):
            return self._action_moment()
        if beat in ("celebration", "success"):
            return self._action_moment()
        return self._action_moment()

    def _counting_moment(self, objective: LearningObjective) -> InteractiveMoment:
        obj = random.choice(self._default_objects)
        prompt = f"Can you count the {obj}s?"
        return InteractiveMoment(
            prompt=prompt,
            expected_reaction="count out loud with the character",
            pause_duration=3.0,
            moment_type="counting",
        )

    def _color_moment(self, objective: LearningObjective) -> InteractiveMoment:
        color = random.choice(self._default_colors)
        prompt = f"Can you find something {color}?"
        return InteractiveMoment(
            prompt=prompt,
            expected_reaction=f"point to something {color}",
            pause_duration=2.5,
            moment_type="color_id",
        )

    def _shape_moment(self, objective: LearningObjective) -> InteractiveMoment:
        shape = random.choice(self._default_shapes)
        prompt = f"Can you find a {shape}?"
        return InteractiveMoment(
            prompt=prompt,
            expected_reaction=f"point to a {shape} shape",
            pause_duration=2.5,
            moment_type="shape_id",
        )

    def _animal_moment(self, objective: LearningObjective) -> InteractiveMoment:
        animal = random.choice(self._default_animals)
        sound_map = {
            "lion": "roar", "duck": "quack", "cow": "moo",
            "cat": "meow", "dog": "woof", "frog": "ribbit", "bird": "tweet",
        }
        sound = sound_map.get(animal, "sound")
        prompt = f"What sound does a {animal} make?"
        return InteractiveMoment(
            prompt=prompt,
            expected_reaction=f"make the {animal} {sound} sound",
            pause_duration=2.5,
            moment_type="animal_sound",
        )

    def _action_moment(self) -> InteractiveMoment:
        action = random.choice(self._default_actions)
        prompt = f"Can you {action}?"
        return InteractiveMoment(
            prompt=prompt,
            expected_reaction=action,
            pause_duration=2.5,
            moment_type="action",
        )

    def _finding_moment(self) -> InteractiveMoment:
        obj = random.choice(self._default_objects)
        prompt = f"Can you find the {obj}?"
        return InteractiveMoment(
            prompt=prompt,
            expected_reaction=f"look for and point to the {obj}",
            pause_duration=3.0,
            moment_type="finding",
        )


class EmotionEngine:
    def __init__(self):
        self._default_arc = [
            "curiosity",
            "excitement",
            "challenge",
            "thinking",
            "learning",
            "success",
            "celebration",
        ]
        self._beat_emotion_map: Dict[str, str] = {
            "opening": "curiosity",
            "goal": "excitement",
            "problem": "challenge",
            "conflict": "challenge",
            "discovery": "thinking",
            "learning": "learning",
            "practice": "thinking",
            "success": "success",
            "celebration": "celebration",
            "goodbye": "happy",
            "play": "excited",
            "exploration": "curiosity",
        }
        self._emotions = [
            "curiosity",
            "excitement",
            "challenge",
            "thinking",
            "learning",
            "success",
            "celebration",
            "happy",
            "surprised",
            "proud",
            "warm",
            "gentle",
        ]

    def generate_emotional_arc(self, structure: List[str]) -> List[str]:
        if not structure:
            return self._default_arc[:3]
        arc: List[str] = []
        for beat in structure:
            emotion = self.get_emotion_for_beat(beat)
            arc.append(emotion)
        arc = self._ensure_progression(arc, len(structure))
        return arc

    def get_emotion_for_beat(self, beat: str) -> str:
        key = beat.lower().strip()
        if key in self._beat_emotion_map:
            return self._beat_emotion_map[key]
        return "curiosity"

    def get_emotion_intensity(self, emotion: str, story_position: float) -> int:
        if story_position < 0.0 or story_position > 1.0:
            story_position = max(0.0, min(1.0, story_position))
        if emotion in ("challenge", "thinking"):
            if 0.4 <= story_position <= 0.8:
                return 4
            return 3
        if emotion in ("success", "celebration", "excited"):
            if 0.7 <= story_position <= 0.9:
                return 5
            if story_position >= 0.9 or story_position <= 0.3:
                return 3
            return 4
        if emotion in ("curiosity", "learning"):
            return max(1, min(4, int(1 + story_position * 3)))
        return max(1, min(4, int(1 + story_position * 2)))

    def _ensure_progression(self, arc: List[str], target_len: int) -> List[str]:
        if len(arc) == target_len:
            return arc
        while len(arc) < target_len:
            arc.append("happy")
        return arc[:target_len]

    def get_available_emotions(self) -> List[str]:
        return list(self._emotions)


class HumorEngine:
    def __init__(self):
        self._humor_library = [
            "funny sneeze",
            "silly dance",
            "goofy hat",
            "animal hiccup",
            "ticklish feathers",
            "bubble surprise",
            "gentle repetition",
            "wiggly tail",
            "silly sandwich",
            "giggle puddle",
            "backwards walking",
            "happy tumble",
        ]
        self._character_humor: Dict[str, List[str]] = {
            "bunny": ["funny sneeze", "wiggly tail", "happy tumble"],
            "bear": ["silly dance", "goofy hat", "silly sandwich"],
            "cat": ["ticklish feathers", "gentle repetition", "giggle puddle"],
            "dog": ["animal hiccup", "silly dance", "backwards walking"],
            "duck": ["bubble surprise", "funny sneeze", "wiggly tail"],
            "owl": ["gentle repetition", "goofy hat", "backwards walking"],
            "frog": ["giggle puddle", "happy tumble", "bubble surprise"],
            "elephant": ["funny sneeze", "silly dance", "bubble surprise"],
        }
        self._theme_humor: Dict[str, List[str]] = {
            "birthday": ["bubble surprise", "goofy hat", "silly dance"],
            "beach": ["funny sneeze", "wiggly tail", "giggle puddle"],
            "zoo": ["animal hiccup", "silly dance", "funny sneeze"],
            "farm": ["animal hiccup", "funny sneeze", "wiggly tail"],
            "bedtime": ["gentle repetition", "ticklish feathers", "happy tumble"],
            "school": ["silly sandwich", "goofy hat", "giggle puddle"],
            "park": ["bubble surprise", "silly dance", "backwards walking"],
            "kitchen": ["silly sandwich", "bubble surprise", "giggle puddle"],
            "space": ["backwards walking", "bubble surprise", "gentle repetition"],
            "ocean": ["bubble surprise", "giggle puddle", "funny sneeze"],
        }

    def select_humor_moment(
        self,
        exclude: Optional[List[str]] = None,
        characters: Optional[List[str]] = None,
    ) -> str:
        candidates: List[str] = []
        if characters:
            for char in characters:
                char_key = char.lower().split()[0]
                if char_key in self._character_humor:
                    candidates.extend(self._character_humor[char_key])
        if not candidates:
            candidates = list(self._humor_library)
        if exclude:
            candidates = [c for c in candidates if c not in exclude]
        if not candidates:
            candidates = list(self._humor_library)
        return random.choice(candidates)

    def get_humor_for_character(self, char_id: str) -> List[str]:
        key = char_id.lower().split("_")[-1].split("-")[-1]
        if key in self._character_humor:
            return list(self._character_humor[key])
        for k, v in self._character_humor.items():
            if k in char_id.lower():
                return list(v)
        return list(self._humor_library)

    def get_humor_for_theme(self, theme_id: str) -> List[str]:
        key = theme_id.lower().split("_")[-1].split("-")[-1]
        if key in self._theme_humor:
            return list(self._theme_humor[key])
        for k, v in self._theme_humor.items():
            if k in theme_id.lower():
                return list(v)
        return list(self._humor_library)


class HumorTimingEngine:
    def __init__(self, humor_engine: Optional[HumorEngine] = None):
        self._engine = humor_engine or HumorEngine()
        self._max_per_episode = 3

    def plan_humor_moments(
        self,
        structure: List[str],
        characters: Optional[List[str]] = None,
        used_moments: Optional[List[str]] = None,
    ) -> List[str]:
        if not structure:
            return []
        used = used_moments or []
        count = min(len(structure) // 3, self._max_per_episode)
        count = max(count, 1)
        selected: List[str] = []
        for _ in range(count):
            moment = self._engine.select_humor_moment(
                exclude=used + selected, characters=characters
            )
            selected.append(moment)
        return selected
