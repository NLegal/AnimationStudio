"""Lyrics Generator — VISION Phase 6 alignment.

Produces nursery-rhyme-style lyric text for a song placement, closing the
gap between ``SongEngine.plan_song`` (which picks topic/type/placement) and
the music backend (which needs actual verse/chorus lyric *text*).

The generator is fully offline, deterministic (seeded), and produces two
output forms:

- ``text``       — clean singing lines, one per line (feeds ``SubtitleEngine
                   .generate_from_lyrics``)
- ``formatted``  — section markers wrapping the lines (feeds ``MusicRequest
                   .lyrics_override`` which ACE-Step sends as-is)

VISION pipeline position: Story Generator → **Lyrics** → Music Generator →
Storyboard → Scene Planner → Prompt Generator → ...
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional


# --------------------------------------------------------------------------- #
# Data models                                                                  #
# --------------------------------------------------------------------------- #

@dataclass
class LyricsSection:
    """One section of a song: verse, chorus, bridge, or outro."""

    section_type: str
    lines: List[str]


@dataclass
class LyricsResult:
    """Complete lyrics output with both forms needed downstream."""

    sections: List[LyricsSection] = field(default_factory=list)
    text: str = ""        # singing lines only, newline-joined (subtitles)
    formatted: str = ""   # with [verse]/[chorus] markers (ACE-Step)


# --------------------------------------------------------------------------- #
# Vocabulary banks (curriculum-area aware, age 2-5 appropriate)               #
# --------------------------------------------------------------------------- #

_VERSE_BANKS: dict[str, list[list[str]]] = {
    "alphabet": [
        ["A is for apple, shiny and red",
         "B is for ball, bouncing ahead",
         "C is for cat, soft and sweet",
         "D is for dog, with happy feet"],
        ["E is for elephant, big and strong",
         "F is for fish, swimming along",
         "G is for garden, flowers so bright",
         "H is for horse, running with might"],
        ["I is for igloo, made of snow",
         "J is for jelly, watch it go",
         "K is for kite, up in the air",
         "L is for lion, with a great stare"],
    ],
    "colors": [
        ["Red is the color of apples so sweet",
         "Blue is the sky above our street",
         "Green is the grass where we like to play",
         "Yellow the sun on a bright sunny day"],
        ["Orange is carrots, crunchy and fresh",
         "Purple is grapes, the best breakfast",
         "Pink is the flowers, blooming with care",
         "Brown is the earth, everywhere"],
    ],
    "counting": [
        ["One little star shining up high",
         "Two little ducks swimming nearby",
         "Three little frogs jumping with glee",
         "Four little rabbits running so free"],
        ["Five little ducks went out one day",
         "Over the hills and far away",
         "Six little bees buzzing around the flowers",
         "Seven little hours full of hours"],
        ["Eight little fish in the deep blue sea",
         "Nine little crabs walking near me",
         "Ten little toes on my two little feet",
         "Ten little friends that I get to meet"],
    ],
    "animals": [
        ["The cat says meow, soft and low",
         "The dog says woof, watch him go",
         "The cow says moo, out on the farm",
         "The sheep says baa, keeping us warm"],
        ["The duck says quack, swimming in a row",
         "The pig says oink, in the mud below",
         "The hen says cluck, laying eggs each day",
         "The owl says hoo, hoo, coming out to play"],
        ["The lion roars, king of the land",
         "The monkey swings from tree to tree strand",
         "The elephant trumpets, so loud and proud",
         "The bunny hops along, standing out in a crowd"],
    ],
    "educational": [
        ["Learning is fun when we play along",
         "Singing together in a happy song",
         "Reading books and sharing too",
         "Discovering things that are brand new"],
        ["Counting and colors, shapes in a row",
         "Letters and numbers, watch them grow",
         "Asking questions, curious and keen",
         "The smartest kids that you have ever seen"],
    ],
    "dance": [
        ["Clap your hands and stomp your feet",
         "Dancing to the happy beat",
         "Spin around and jump up high",
         "Reach the stars up in the sky"],
        ["Wiggle to the left and right",
         "Dancing makes us feel so bright",
         "Hold a hand and dance along",
         "Everybody sing this song"],
    ],
    "lullaby": [
        ["Close your eyes, the moon is bright",
         "Stars are twinkling through the night",
         "Dream of clouds as soft as wool",
         "Everything is calm and full"],
        ["Hush now baby, time to sleep",
         "Gentle dreams are yours to keep",
         "Wind is whispering through the trees",
         "Floating on the night-time breeze"],
    ],
    "transition": [
        ["Off we go to somewhere new",
         "There are adventures waiting too",
         "Wave goodbye but don't be sad",
         "We will come back, isn't that rad"],
        ["Moving on to something fun",
         "Step by step, we're on the run",
         "Follow me, I know the way",
         "We'll be there by end of day"],
    ],
}

_CHORUS_BANKS: dict[str, list[list[str]]] = {
    "alphabet": [
        ["Letters, letters, one and all",
         "Learning them is such a ball",
         "Sing along from A to Z",
         "Now you know them, just like me"],
    ],
    "colors": [
        ["Colors, colors, everywhere",
         "Look around and you will see",
         "Rainbow bright for you and me",
         "Colors make the world so free"],
    ],
    "counting": [
        ["Count along from one to ten",
         "We can count them all again",
         "Numbers dancing, here they come",
         "One through ten, here is the sum"],
    ],
    "animals": [
        ["Animals are friends of mine",
         "Every creature, every kind",
         "From the tiniest little bug",
         "To the biggest creature shrug"],
    ],
    "educational": [
        ["Learning, learning every day",
         "This is how we learn and play",
         "Growing smarter, growing strong",
         "Sing along to our learning song"],
    ],
    "dance": [
        ["Everybody dance with me",
         "Happy as a dance can be",
         "Clap and spin and move your feet",
         "Dancing to the happy beat"],
    ],
    "lullaby": [
        ["Sleep, sleep, little one",
         "Night has come for everyone",
         "Dream of wonderful things tonight",
         "Everything will be alright"],
    ],
    "transition": [
        ["Here we go, on our way",
         "Adventure calls, it is a new day",
         "Follow, follow, come along",
         "This is where we all belong"],
    ],
}

_BRIDGE_BANKS: dict[str, list[list[str]]] = {
    "default": [
        ["Oh, can you see it, can you feel",
         "The magic happening here is real",
         "Together we can learn and grow",
         "The best of friends, through all we know"],
    ],
}

# `SongEngine.select_song_type` emits singular forms ("color", "animal")
# while the vocabulary banks above are plural-keyed ("colors", "animals").
# Without this alias the banks silently fall back to the generic
# "educational" lyrics (audit A-02).
_SONG_TYPE_ALIASES: dict[str, str] = {
    "color": "colors",
    "animal": "animals",
}


def _normalize_song_type(song_type: str) -> str:
    return _SONG_TYPE_ALIASES.get(song_type, song_type)

_OUTRO_BANKS: dict[str, list[list[str]]] = {
    "default": [
        ["And that is how the story goes",
         "From seeds of learning, a garden grows",
         "Thanks for singing, thanks for play",
         "See you all again someday"],
    ],
}


# --------------------------------------------------------------------------- #
# Section arrangement rules                                                    #
# --------------------------------------------------------------------------- #

def _build_section_plan(
    song_type: str,
    duration_seconds: int,
) -> list[str]:
    """Produce an ordered list of section types for the song.

    Duration drives the count: ~12s per verse, ~8s per chorus,
    ~6s per bridge, ~6s per outro.

    Returns a list like ``["verse", "chorus", "verse", "chorus"]``.
    """
    if duration_seconds <= 30:
        return ["verse", "chorus"]
    if duration_seconds <= 50:
        return ["verse", "chorus", "verse", "chorus"]
    if duration_seconds <= 75:
        return ["verse", "chorus", "bridge", "verse", "chorus"]
    # 76-120s+ (full episode song)
    return ["verse", "chorus", "verse", "chorus", "bridge", "chorus", "outro"]


def _pick_section_bank(
    section_type: str,
    song_type: str,
    rng: random.Random,
) -> list[str]:
    """Pick a random line set from the appropriate bank."""
    if section_type == "verse":
        bank = _VERSE_BANKS.get(_normalize_song_type(song_type), _VERSE_BANKS["educational"])
    elif section_type == "chorus":
        bank = _CHORUS_BANKS.get(_normalize_song_type(song_type), _CHORUS_BANKS["educational"])
    elif section_type == "bridge":
        bank = _BRIDGE_BANKS["default"]
    else:
        bank = _OUTRO_BANKS["default"]
    return rng.choice(bank)


# --------------------------------------------------------------------------- #
# Generator                                                                    #
# --------------------------------------------------------------------------- #

class LyricsGenerator:
    """Produce nursery-rhyme lyrics for a ``SongPlacement``.

    Usage::

        gen = LyricsGenerator(seed=42)
        result = gen.generate(
            song_type="alphabet",
            topic="Lily Bunny alphabet song",
            character="Lily Bunny",
            duration_seconds=55,
        )
        # result.text       -> subtitle lines
        # result.formatted  -> ACE-Step lyrics_override
    """

    def generate(
        self,
        song_type: str = "educational",
        topic: str = "",
        character: str = "",
        duration_seconds: int = 60,
        seed: Optional[int] = None,
    ) -> LyricsResult:
        """Generate lyrics for the given song parameters.

        Parameters
        ----------
        song_type:
            One of the ``SongEngine`` type values (educational, dance,
            lullaby, alphabet, counting, color, animal, transition).
            Singular/plural forms are both accepted.
        topic:
            Free-text topic string (e.g. ``"Lily Bunny consonant song"``).
            Not yet interpolated into lyric banks (audit A-02, S).
        character:
            Main character name to weave into the outro if present.
        duration_seconds:
            Target duration; drives section count.
        seed:
            Optional RNG seed for reproducibility.

        Returns
        -------
        LyricsResult with both ``text`` and ``formatted`` fields populated.
        """
        song_type = _normalize_song_type(song_type)
        rng = random.Random(seed)
        plan = _build_section_plan(song_type, duration_seconds)

        sections: list[LyricsSection] = []
        seen_types: set[str] = set()
        used_indices: dict[str, list[int]] = {}

        for stype in plan:
            bank_key = f"{stype}_{song_type}" if stype in ("verse", "chorus") else stype
            bank_options = {
                "verse": _VERSE_BANKS.get(song_type, _VERSE_BANKS["educational"]),
                "chorus": _CHORUS_BANKS.get(song_type, _CHORUS_BANKS["educational"]),
                "bridge": _BRIDGE_BANKS["default"],
                "outro": _OUTRO_BANKS["default"],
            }[stype]

            # Avoid repeating the same lines within the same song
            used = used_indices.get(bank_key, [])
            available = [i for i in range(len(bank_options)) if i not in used]
            if not available:
                available = list(range(len(bank_options)))
            idx = rng.choice(available)
            used_indices.setdefault(bank_key, []).append(idx)
            lines = bank_options[idx][:]

            # Personalize outro with character name
            if stype == "outro" and character:
                lines = [ln.replace("See you all", f"{character} says see you")
                         if "See you all" in ln else ln
                         for ln in lines]

            sections.append(LyricsSection(section_type=stype, lines=lines))
            seen_types.add(stype)

        # Build both output forms
        clean_lines: list[str] = []
        marker_lines: list[str] = []

        for section in sections:
            marker_lines.append(f"[{section.section_type}]")
            for line in section.lines:
                clean_lines.append(line)
                marker_lines.append(line)

        return LyricsResult(
            sections=sections,
            text="\n".join(clean_lines),
            formatted="\n".join(marker_lines),
        )
