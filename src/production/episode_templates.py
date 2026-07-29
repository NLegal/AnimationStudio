"""Episode structure templates for common video formats."""

from typing import List, Dict

TEMPLATES: Dict[str, List[Dict]] = {
    "educational_song": [
        {
            "title": "Welcome",
            "purpose": "Greet the viewer and introduce topic",
            "duration": 15,
            "mood": "happy",
            "shots": [
                {"shot_type": "establishing", "duration": 4},
                {"shot_type": "wide", "duration": 6, "animation": "wave"},
                {"shot_type": "medium", "duration": 5},
            ],
        },
        {
            "title": "Learning Introduction",
            "purpose": "Introduce the educational concept",
            "duration": 20,
            "mood": "curious",
            "shots": [
                {"shot_type": "medium", "duration": 6},
                {"shot_type": "close-up", "duration": 7, "animation": "point"},
                {"shot_type": "wide", "duration": 7},
            ],
        },
        {
            "title": "Song",
            "purpose": "Educational song about the topic",
            "duration": 60,
            "mood": "excited",
            "has_song": True,
            "shots": [
                {"shot_type": "wide", "duration": 8, "animation": "dance"},
                {"shot_type": "medium", "duration": 8, "animation": "sing"},
                {"shot_type": "close-up", "duration": 6, "emotion": "happy"},
                {"shot_type": "wide", "duration": 8, "animation": "dance"},
                {"shot_type": "medium", "duration": 8, "animation": "sing"},
                {"shot_type": "close-up", "duration": 6, "emotion": "excited"},
                {"shot_type": "wide", "duration": 8, "animation": "dance"},
                {"shot_type": "group", "duration": 8},
            ],
        },
        {
            "title": "Practice",
            "purpose": "Practice the concept with viewer interaction",
            "duration": 30,
            "mood": "playful",
            "shots": [
                {"shot_type": "medium", "duration": 8, "animation": "point"},
                {"shot_type": "close-up", "duration": 7, "animation": "think"},
                {"shot_type": "wide", "duration": 8, "animation": "clap"},
                {"shot_type": "medium", "duration": 7},
            ],
        },
        {
            "title": "Celebration",
            "purpose": "Celebrate what was learned",
            "duration": 15,
            "mood": "excited",
            "shots": [
                {"shot_type": "wide", "duration": 5, "animation": "dance"},
                {"shot_type": "medium", "duration": 5, "animation": "clap"},
                {"shot_type": "close-up", "duration": 5, "emotion": "excited"},
            ],
        },
        {
            "title": "Goodbye",
            "purpose": "Say goodbye and preview next episode",
            "duration": 10,
            "mood": "happy",
            "shots": [
                {"shot_type": "medium", "duration": 5, "animation": "wave"},
                {"shot_type": "wide", "duration": 5},
            ],
        },
    ],
    "story_time": [
        {
            "title": "Opening",
            "purpose": "Establish setting and characters",
            "duration": 25,
            "mood": "peaceful",
            "shots": [
                {"shot_type": "establishing", "duration": 6},
                {"shot_type": "wide", "duration": 6},
                {"shot_type": "medium", "duration": 7},
                {"shot_type": "close-up", "duration": 6},
            ],
        },
        {
            "title": "Problem",
            "purpose": "Introduce the story problem",
            "duration": 30,
            "mood": "curious",
            "shots": [
                {"shot_type": "medium", "duration": 8},
                {"shot_type": "close-up", "duration": 7, "emotion": "worried"},
                {"shot_type": "wide", "duration": 8},
                {"shot_type": "over-the-shoulder", "duration": 7},
            ],
        },
        {
            "title": "Adventure",
            "purpose": "Characters solve the problem",
            "duration": 45,
            "mood": "adventurous",
            "shots": [
                {"shot_type": "tracking", "duration": 8, "animation": "walk"},
                {"shot_type": "wide", "duration": 7},
                {"shot_type": "medium", "duration": 8, "animation": "point"},
                {"shot_type": "close-up", "duration": 7, "emotion": "curious"},
                {"shot_type": "tracking", "duration": 8, "animation": "walk"},
                {"shot_type": "wide", "duration": 7},
            ],
        },
        {
            "title": "Resolution",
            "purpose": "Problem is solved, lesson learned",
            "duration": 25,
            "mood": "happy",
            "shots": [
                {"shot_type": "medium", "duration": 7, "emotion": "surprised"},
                {"shot_type": "wide", "duration": 8, "animation": "clap"},
                {"shot_type": "close-up", "duration": 5, "emotion": "happy"},
                {"shot_type": "medium", "duration": 5},
            ],
        },
        {
            "title": "Ending",
            "purpose": "Wrap up and moral lesson",
            "duration": 15,
            "mood": "warm",
            "shots": [
                {"shot_type": "wide", "duration": 6},
                {"shot_type": "close-up", "duration": 5, "emotion": "proud"},
                {"shot_type": "medium", "duration": 4, "animation": "wave"},
            ],
        },
    ],
    "morning_routine": [
        {
            "title": "Wake Up",
            "purpose": "Character wakes up and starts the day",
            "duration": 20,
            "mood": "gentle",
            "shots": [
                {"shot_type": "establishing", "duration": 5},
                {"shot_type": "close-up", "duration": 5, "emotion": "sleepy"},
                {"shot_type": "wide", "duration": 5, "animation": "stretch"},
                {"shot_type": "medium", "duration": 5, "emotion": "happy"},
            ],
        },
        {
            "title": "Getting Ready",
            "purpose": "Brush teeth, wash face, get dressed",
            "duration": 35,
            "mood": "energetic",
            "has_song": True,
            "shots": [
                {"shot_type": "medium", "duration": 8, "animation": "brush_teeth"},
                {"shot_type": "close-up", "duration": 7, "animation": "wash_face"},
                {"shot_type": "wide", "duration": 8, "animation": "get_dressed"},
                {"shot_type": "medium", "duration": 7, "animation": "comb_hair"},
                {"shot_type": "close-up", "duration": 5, "emotion": "proud"},
            ],
        },
        {
            "title": "Breakfast",
            "purpose": "Eat a healthy breakfast",
            "duration": 25,
            "mood": "happy",
            "shots": [
                {"shot_type": "wide", "duration": 7, "animation": "eat"},
                {"shot_type": "close-up", "duration": 6, "animation": "drink"},
                {"shot_type": "medium", "duration": 6, "animation": "talk"},
                {"shot_type": "wide", "duration": 6},
            ],
        },
        {
            "title": "Departure",
            "purpose": "Head out for the day's adventure",
            "duration": 15,
            "mood": "excited",
            "shots": [
                {"shot_type": "medium", "duration": 5, "animation": "wave"},
                {"shot_type": "tracking", "duration": 6, "animation": "skip"},
                {"shot_type": "wide", "duration": 4},
            ],
        },
    ],
}
