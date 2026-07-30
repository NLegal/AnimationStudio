import re

from .models import LipSyncTrack, Phoneme


PHONEME_MOUTH_MAP: dict[str, str] = {
    "AA": "open_wide", "AE": "open_mid", "AH": "open_relaxed",
    "AO": "rounded_open", "AW": "rounded_wide", "AY": "smile_open",
    "B": "closed_tight", "CH": "puckered", "D": "tongue_up",
    "DH": "tongue_out", "EH": "open_mid", "ER": "rounded_tight",
    "EY": "smile_mid", "F": "lip_bite", "G": "mouth_open",
    "HH": "open_relaxed", "IH": "spread_mid", "IY": "spread_wide",
    "JH": "puckered", "K": "mouth_open", "L": "tongue_up",
    "M": "closed_tight", "N": "tongue_up", "NG": "mouth_open",
    "OW": "rounded", "OY": "rounded_to_smile",
    "P": "closed_tight", "R": "rounded_tight", "S": "teeth_together",
    "SH": "puckered", "T": "tongue_up", "TH": "tongue_out",
    "UH": "rounded_small", "UW": "rounded_small", "V": "lip_bite",
    "W": "rounded_small", "Y": "smile_mid", "Z": "teeth_together",
    "ZH": "puckered",
    "SIL": "closed",
}


SIMPLE_MOUTH_MAP: dict[str, str] = {
    "a": "open_wide", "e": "smile_mid", "i": "spread_wide",
    "o": "rounded_open", "u": "rounded_small",
    "b": "closed_tight", "d": "tongue_up", "f": "lip_bite",
    "k": "mouth_open", "l": "tongue_up", "m": "closed_tight",
    "n": "tongue_up", "p": "closed_tight", "r": "rounded_tight",
    "s": "teeth_together", "t": "tongue_up", "w": "rounded_small",
    " ": "closed", ".": "closed", ",": "closed",
    "!": "open_wide", "?": "rounded_open",
}


class LipSyncEngine:
    def generate(self, dialogue: str, duration: float) -> LipSyncTrack:
        words = re.findall(r"\S+", dialogue)
        if not words:
            return LipSyncTrack(dialogue=dialogue, duration=duration)

        time_per_word = duration / len(words)
        phonemes: list[Phoneme] = []

        for i, word in enumerate(words):
            word_start = i * time_per_word
            word_duration = time_per_word
            word_phonemes = self._word_to_phonemes(word, word_start, word_duration)
            phonemes.extend(word_phonemes)

        return LipSyncTrack(
            dialogue=dialogue,
            phonemes=phonemes,
            duration=duration,
        )

    def _word_to_phonemes(
        self, word: str, start: float, duration: float
    ) -> list[Phoneme]:
        letters = list(word.lower())
        if not letters:
            return []

        phonemes: list[Phoneme] = []
        per_letter = duration / len(letters)

        for i, letter in enumerate(letters):
            mouth = SIMPLE_MOUTH_MAP.get(letter, "open_relaxed")
            phone_start = start + i * per_letter
            phone_end = phone_start + per_letter
            phoneme_str = self._letter_to_phoneme_str(letter)

            phonemes.append(Phoneme(
                phoneme=phoneme_str,
                start_time=round(phone_start, 3),
                end_time=round(phone_end, 3),
                mouth_shape=mouth,
            ))

        return phonemes

    def _letter_to_phoneme_str(self, letter: str) -> str:
        lookup = {
            "a": "AA", "e": "EH", "i": "IH", "o": "AO", "u": "UH",
            "b": "B", "d": "D", "f": "F", "g": "G", "h": "HH",
            "j": "JH", "k": "K", "l": "L", "m": "M", "n": "N",
            "p": "P", "r": "R", "s": "S", "t": "T", "v": "V",
            "w": "W", "y": "Y", "z": "Z",
            "c": "K", "q": "K", "x": "KS",
        }
        return lookup.get(letter, "SIL")

    def estimate_duration(self, text: str, words_per_second: float = 2.5) -> float:
        word_count = len(re.findall(r"\S+", text))
        if word_count == 0:
            return 0.0
        return word_count / words_per_second
