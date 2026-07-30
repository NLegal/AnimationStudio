from __future__ import annotations
import random
from typing import List

from src.story_engine.models import DialogueLine, LearningObjective


class DialogueEngine:
    def __init__(self):
        self._greetings = [
            "Hello friends",
            "Welcome everyone",
            "Hi there",
            "Good day",
        ]
        self._location_phrases = [
            "Today we are at",
            "We are visiting",
            "Let us go to",
        ]
        self._celebration_lines = [
            "We did it",
            "Great job everyone",
            "You are so smart",
            "Hooray for us",
        ]
        self._goodbyes = [
            "See you next time",
            "Goodbye friends",
            "Come back soon",
            "We will play again",
        ]
        self._praise_words = [
            "Wonderful",
            "Amazing",
            "Fantastic",
            "Great",
            "Super",
        ]
        self._emotions_child = ["happy", "curious", "excited", "surprised", "proud"]
        self._emotions_adult = ["warm", "kind", "encouraging", "cheerful", "gentle"]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_line(
        self,
        speaker: str,
        text: str,
        emotion: str = "neutral",
        interaction: bool = False,
    ) -> DialogueLine:
        pause = self._pick_pause(text, emotion, interaction)
        return DialogueLine(
            speaker=speaker,
            text=text,
            emotion=emotion,
            interaction=interaction,
            pause_after=pause,
        )

    def generate_intro(
        self,
        main_character: str,
        location: str,
        objective: LearningObjective,
    ) -> List[DialogueLine]:
        greeting = random.choice(self._greetings)
        loc_phrase = random.choice(self._location_phrases)
        lines = [
            self.generate_line(
                "Narrator", f"{greeting}!", "warm", interaction=False
            ),
            self.generate_line(
                "Narrator",
                f"{loc_phrase} {location}.",
                "cheerful",
                interaction=False,
            ),
            self.generate_line(
                "Narrator",
                f"{main_character} is here too.",
                "happy",
                interaction=False,
            ),
        ]
        objective_text = self._intro_objective_text(objective, main_character)
        if objective_text:
            lines.append(
                self.generate_line(
                    main_character,
                    objective_text,
                    "curious",
                    interaction=False,
                )
            )
        return lines

    def generate_teaching_moment(
        self,
        objective: LearningObjective,
        characters: List[str],
    ) -> List[DialogueLine]:
        lines: List[DialogueLine] = []
        teacher = self._pick_teacher(characters)
        student = self._pick_student(characters, teacher)

        lines.append(
            self.generate_line(teacher, self._teaching_question(objective), "kind")
        )
        lines.append(
            self.generate_line(
                student, self._student_answer(objective), "curious"
            )
        )
        lines.append(
            self.generate_line(
                teacher,
                f"{random.choice(self._praise_words)}!",
                "happy",
            )
        )

        extra = self._extra_teaching_lines(objective, characters)
        for speaker, text in extra:
            emotion = "happy" if speaker != teacher else "encouraging"
            lines.append(self.generate_line(speaker, text, emotion))

        return lines

    def generate_celebration(self, characters: List[str]) -> List[DialogueLine]:
        lines: List[DialogueLine] = []
        line = random.choice(self._celebration_lines)
        speaker = characters[0] if characters else "Narrator"
        lines.append(
            self.generate_line(speaker, f"{line}!", "excited", interaction=True)
        )
        if len(characters) > 1:
            lines.append(
                self.generate_line(
                    characters[1],
                    f"Yes! {random.choice(self._praise_words)}!",
                    "happy",
                    interaction=True,
                )
            )
        lines.append(
            self.generate_line(
                "Narrator",
                "Everybody celebrates.",
                "warm",
                interaction=False,
            )
        )
        return lines

    def generate_goodbye(self, characters: List[str]) -> List[DialogueLine]:
        lines: List[DialogueLine] = []
        goodbye = random.choice(self._goodbyes)
        if characters:
            lines.append(
                self.generate_line(
                    characters[0], f"{goodbye}!", "warm", interaction=True
                )
            )
        else:
            lines.append(
                self.generate_line("Narrator", f"{goodbye}!", "warm")
            )
        if len(characters) > 1:
            second = random.choice(self._goodbyes)
            lines.append(
                self.generate_line(
                    characters[1], f"{second}!", "cheerful", interaction=True
                )
            )
        lines.append(
            self.generate_line(
                "Narrator", "See you soon.", "warm", interaction=False
            )
        )
        return lines

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _pick_pause(self, text: str, emotion: str, interaction: bool) -> float:
        word_count = len(text.split())
        if interaction:
            return 2.5
        if emotion in ("surprised", "excited", "happy"):
            return 0.8
        if word_count > 10:
            return 1.2
        return 0.5

    def _pick_teacher(self, characters: List[str]) -> str:
        if not characters:
            return "Narrator"
        return characters[-1] if len(characters) > 1 else characters[0]

    def _pick_student(self, characters: List[str], teacher: str) -> str:
        suitable = [c for c in characters if c != teacher]
        return suitable[0] if suitable else teacher

    def _intro_objective_text(
        self, objective: LearningObjective, character: str
    ) -> str:
        kw = objective.name.lower() if objective.name else ""
        if "count" in kw or "number" in kw:
            return f"I want to count today."
        if "color" in kw or "blue" in kw or "red" in kw:
            return f"I love learning colors."
        if "shape" in kw or "triangle" in kw:
            return f"Shapes are so much fun."
        if "animal" in kw:
            return f"I like animals."
        if "letter" in kw or "alphabet" in kw or "abc" in kw:
            return f"Let us learn letters."
        return f"I am ready to learn."

    def _teaching_question(self, objective: LearningObjective) -> str:
        kw = objective.name.lower() if objective.name else ""
        if "count" in kw:
            return "Can you count with me?"
        if "color" in kw or "blue" in kw:
            return "Do you know this color?"
        if "shape" in kw:
            return "What shape is this?"
        if "animal" in kw:
            return "What sound does it make?"
        if "letter" in kw:
            return "What letter is this?"
        return "Do you know the answer?"

    def _student_answer(self, objective: LearningObjective) -> str:
        kw = objective.name.lower() if objective.name else ""
        if "count" in kw:
            return "One, two, three!"
        if "color" in kw:
            return "It is blue!"
        if "shape" in kw:
            return "It is a circle!"
        if "animal" in kw:
            return "Moo moo!"
        if "letter" in kw:
            return "It is A!"
        return "I know this!"

    def _extra_teaching_lines(
        self, objective: LearningObjective, characters: List[str]
    ) -> List[tuple[str, str]]:
        extra: List[tuple[str, str]] = []
        kw = objective.name.lower() if objective.name else ""
        if "count" in kw:
            extra.append((characters[0], "Let us try again."))
            extra.append(("Narrator", "Counting is fun."))
        elif "color" in kw:
            extra.append(("Narrator", "Colors are everywhere."))
        elif "shape" in kw:
            extra.append(("Narrator", "Shapes are all around us."))
        else:
            extra.append(("Narrator", "Learning is fun."))
        return extra


class NarrationMixin:
    def narrate(self, text: str, emotion: str = "neutral") -> DialogueLine:
        return DialogueLine(
            speaker="Narrator",
            text=text,
            emotion=emotion,
            interaction=False,
            pause_after=0.5,
        )
