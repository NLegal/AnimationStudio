from __future__ import annotations
from dataclasses import dataclass, field
import re


SUBTITLE_MAX_LINES = 2
SUBTITLE_CHARS_PER_LINE = 42


@dataclass
class SubtitleEntry:
    text: str = ""
    start_time: float = 0.0
    end_time: float = 0.0
    is_highlight: bool = False
    word_timings: list[tuple[str, float, float]] = field(default_factory=list)


class SubtitleEngine:
    def generate_from_text(
        self, text: str, start_time: float, duration: float, is_highlight: bool = False
    ) -> list[SubtitleEntry]:
        words = text.split()
        if not words:
            return []

        time_per_word = duration / max(len(words), 1)
        entries: list[SubtitleEntry] = []
        current_entry_words: list[str] = []
        current_line_len = 0
        entry_start = start_time

        for i, word in enumerate(words):
            if current_line_len + len(word) + 1 > SUBTITLE_CHARS_PER_LINE and current_entry_words:
                entry_text = " ".join(current_entry_words)
                word_count = len(current_entry_words)
                word_timings = self._generate_word_timings(
                    current_entry_words, entry_start, word_count * time_per_word
                )
                entry_end = entry_start + word_count * time_per_word
                entries.append(SubtitleEntry(
                    text=self._split_long_line(entry_text),
                    start_time=entry_start,
                    end_time=entry_end,
                    is_highlight=is_highlight,
                    word_timings=word_timings,
                ))
                current_entry_words = [word]
                current_line_len = len(word)
                entry_start = entry_end
            else:
                current_entry_words.append(word)
                current_line_len += len(word) + 1

        if current_entry_words:
            entry_text = " ".join(current_entry_words)
            word_count = len(current_entry_words)
            word_timings = self._generate_word_timings(
                current_entry_words, entry_start, word_count * time_per_word
            )
            entry_end = entry_start + word_count * time_per_word
            entries.append(SubtitleEntry(
                text=self._split_long_line(entry_text),
                start_time=entry_start,
                end_time=entry_end,
                is_highlight=is_highlight,
                word_timings=word_timings,
            ))

        return entries

    def generate_from_dialogue(
        self, dialogue: str, character: str, start_time: float, duration: float
    ) -> list[SubtitleEntry]:
        text = f"{character}: {dialogue}" if character else dialogue
        return self.generate_from_text(text, start_time, duration, is_highlight=False)

    def generate_from_lyrics(
        self, lyrics: str, start_time: float, duration: float
    ) -> list[SubtitleEntry]:
        lines = [l.strip() for l in lyrics.split("\n") if l.strip()]
        if not lines:
            return []
        time_per_line = duration / len(lines)
        entries: list[SubtitleEntry] = []
        for i, line in enumerate(lines):
            line_start = start_time + i * time_per_line
            line_end = line_start + time_per_line
            entries.append(SubtitleEntry(
                text=line,
                start_time=line_start,
                end_time=line_end,
                is_highlight=True,
            ))
        return entries

    def to_srt(self, entries: list[SubtitleEntry]) -> str:
        lines: list[str] = []
        for i, entry in enumerate(entries, 1):
            lines.append(str(i))
            lines.append(f"{self._format_time(entry.start_time)} --> {self._format_time(entry.end_time)}")
            lines.append(entry.text)
            lines.append("")
        return "\n".join(lines)

    def to_vtt(self, entries: list[SubtitleEntry]) -> str:
        lines: list[str] = ["WEBVTT", ""]
        for entry in entries:
            lines.append(f"{self._format_time(entry.start_time)} --> {self._format_time(entry.end_time)}")
            lines.append(entry.text)
            lines.append("")
        return "\n".join(lines)

    def total_duration(self, entries: list[SubtitleEntry]) -> float:
        if not entries:
            return 0.0
        return max(e.end_time for e in entries)

    def _generate_word_timings(
        self, words: list[str], start: float, total_duration: float
    ) -> list[tuple[str, float, float]]:
        if not words:
            return []
        per_word = total_duration / len(words)
        timings: list[tuple[str, float, float]] = []
        for i, word in enumerate(words):
            w_start = start + i * per_word
            w_end = w_start + per_word
            timings.append((word, round(w_start, 3), round(w_end, 3)))
        return timings

    def _split_long_line(self, text: str) -> str:
        if len(text) <= SUBTITLE_CHARS_PER_LINE:
            return text
        mid = len(text) // 2
        space_before = text.rfind(" ", 0, mid)
        space_after = text.find(" ", mid)
        split_at = space_before if space_before > 0 else (space_after if space_after > 0 else mid)
        return text[:split_at].strip() + "\n" + text[split_at:].strip()

    def _format_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
