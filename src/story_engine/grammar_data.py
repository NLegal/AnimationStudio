from __future__ import annotations
from typing import List
from src.story_engine.models import StoryGrammar


FIND_SOMETHING = StoryGrammar(
    id="find_something",
    name="Find Something",
    description="A character searches for a lost or missing item, learning along the way",
    structure=[
        "Opening where something is lost",
        "Character notices something missing",
        "Search begins",
        "Discovery of clues",
        "Learning moment",
        "Item found",
        "Celebration",
        "Goodbye",
    ],
    conflict_types=["lost_balloon", "missing_puzzle_piece", "cant_find_teddy", "forgot_backpack"],
    resolution_types=["friend_helps", "discovery", "celebration"],
)

LEARN_SOMETHING = StoryGrammar(
    id="learn_something",
    name="Learn Something",
    description="A character learns a new skill or concept with guidance from a friend or teacher",
    structure=[
        "Opening showing curiosity",
        "Character discovers something new",
        "Teacher or friend introduces the concept",
        "Practice together",
        "Struggle moment",
        "Breakthrough with help",
        "Success demonstration",
        "Celebration and goodbye",
    ],
    conflict_types=["wrong_color", "cant_count", "needs_help_cleaning"],
    resolution_types=["teacher_explains", "practice", "character_learns"],
)

HELP_SOMEONE = StoryGrammar(
    id="help_someone",
    name="Help Someone",
    description="A character notices a friend who needs assistance and steps in to help",
    structure=[
        "Opening with happy characters",
        "Friend encounters a problem",
        "Main character offers help",
        "Working together",
        "Teaching moment",
        "Problem solved together",
        "Celebration of friendship",
        "Goodbye with gratitude",
    ],
    conflict_types=["dropped_cookie", "needs_help_cleaning", "plant_needs_water", "forgot_backpack"],
    resolution_types=["friend_helps", "family_helps", "celebration"],
)

BUILD_SOMETHING = StoryGrammar(
    id="build_something",
    name="Build Something",
    description="Characters work together to construct or create something from scratch",
    structure=[
        "Opening with an idea",
        "Gathering materials",
        "Planning the build",
        "Construction begins",
        "Oops moment something goes wrong",
        "Problem solving and fixing",
        "Creation complete",
        "Celebration and goodbye",
    ],
    conflict_types=["missing_puzzle_piece", "wrong_color", "cant_count"],
    resolution_types=["practice", "discovery", "celebration"],
)

VISIT_SOMEWHERE = StoryGrammar(
    id="visit_somewhere",
    name="Visit Somewhere",
    description="Characters travel to a new or familiar location and explore together",
    structure=[
        "Opening at home",
        "Decision to visit somewhere",
        "Journey begins",
        "Arrival at destination",
        "Exploration and discovery",
        "Learning about the place",
        "A special moment",
        "Return home and goodbye",
    ],
    conflict_types=["lost_balloon", "forgot_backpack", "cant_find_teddy"],
    resolution_types=["discovery", "friend_helps", "family_helps"],
)

CELEBRATE_SOMETHING = StoryGrammar(
    id="celebrate_something",
    name="Celebrate Something",
    description="Characters prepare for and enjoy a special celebration or holiday",
    structure=[
        "Opening with exciting news",
        "Planning the celebration",
        "Gathering decorations and treats",
        "Preparations underway",
        "A small problem arises",
        "Friends help fix it",
        "Celebration begins",
        "Goodbye with joy",
    ],
    conflict_types=["dropped_cookie", "wrong_color", "needs_help_cleaning"],
    resolution_types=["celebration", "family_helps", "friend_helps"],
)

CLEAN_SOMETHING = StoryGrammar(
    id="clean_something",
    name="Clean Something",
    description="Characters tidy up a space and learn organization skills along the way",
    structure=[
        "Opening in a messy space",
        "Realization that cleaning is needed",
        "Sorting and organizing begins",
        "Making it fun with a game",
        "Discovering lost items while cleaning",
        "Learning moment about tidiness",
        "Space is clean and beautiful",
        "Celebration and goodbye",
    ],
    conflict_types=["needs_help_cleaning", "cant_find_teddy", "missing_puzzle_piece"],
    resolution_types=["friend_helps", "practice", "celebration"],
)

COUNT_SOMETHING = StoryGrammar(
    id="count_something",
    name="Count Something",
    description="Characters practice counting various objects in a fun engaging way",
    structure=[
        "Opening with curious discovery",
        "Finding things to count",
        "Learning number names",
        "Counting together",
        "Almost getting it wrong",
        "Trying again with help",
        "Counting success",
        "Celebration and goodbye",
    ],
    conflict_types=["cant_count", "wrong_color", "missing_puzzle_piece"],
    resolution_types=["teacher_explains", "practice", "character_learns"],
)

SORT_SOMETHING = StoryGrammar(
    id="sort_something",
    name="Sort Something",
    description="Characters organize items by color shape size or other attributes",
    structure=[
        "Opening with mixed up items",
        "Realization things need sorting",
        "Learning categories",
        "Sorting begins",
        "A tricky item causes confusion",
        "Figuring out where it belongs",
        "All sorted correctly",
        "Celebration and goodbye",
    ],
    conflict_types=["wrong_color", "cant_count", "needs_help_cleaning"],
    resolution_types=["teacher_explains", "practice", "friend_helps"],
)

GROW_SOMETHING = StoryGrammar(
    id="grow_something",
    name="Grow Something",
    description="Characters plant seeds and nurture a living thing watching it grow",
    structure=[
        "Opening in a garden or pot",
        "Planting seeds together",
        "Learning what plants need",
        "Waiting and caring",
        "A problem with growth",
        "Adjusting care routine",
        "Plant sprouts and grows",
        "Celebration and goodbye",
    ],
    conflict_types=["plant_needs_water", "wrong_color", "dropped_cookie"],
    resolution_types=["practice", "discovery", "celebration"],
)

SING_TOGETHER = StoryGrammar(
    id="sing_together",
    name="Sing Together",
    description="Characters come together to sing learn a song and share musical joy",
    structure=[
        "Opening with musical sounds",
        "Gathering friends to sing",
        "Learning the song words",
        "Practicing the melody",
        "Finding the right rhythm",
        "Singing together",
        "Adding dance moves",
        "Final performance and goodbye",
    ],
    conflict_types=["cant_count", "wrong_color", "forgot_backpack"],
    resolution_types=["practice", "celebration", "friend_helps"],
)

DANCE_TOGETHER = StoryGrammar(
    id="dance_together",
    name="Dance Together",
    description="Characters learn and perform dance moves building confidence and coordination",
    structure=[
        "Opening with music playing",
        "Friends arrive to dance",
        "Learning the first move",
        "Practicing the steps",
        "Tripping or mixing up",
        "Encouragement and retry",
        "Dancing in harmony",
        "Final bow and goodbye",
    ],
    conflict_types=["wrong_color", "dropped_cookie", "cant_count"],
    resolution_types=["practice", "friend_helps", "celebration"],
)

ADVENTURE_TOGETHER = StoryGrammar(
    id="adventure_together",
    name="Adventure Together",
    description="Characters embark on an adventurous journey exploring unknown places",
    structure=[
        "Opening with excitement",
        "Setting out on adventure",
        "Encountering a new place",
        "Facing a small challenge",
        "Working as a team",
        "Discovering something amazing",
        "Reflecting on the journey",
        "Return and goodbye",
    ],
    conflict_types=["lost_balloon", "cant_find_teddy", "forgot_backpack", "missing_puzzle_piece"],
    resolution_types=["discovery", "friend_helps", "celebration"],
)

ALL_GRAMMARS: List[StoryGrammar] = [
    FIND_SOMETHING,
    LEARN_SOMETHING,
    HELP_SOMEONE,
    BUILD_SOMETHING,
    VISIT_SOMEWHERE,
    CELEBRATE_SOMETHING,
    CLEAN_SOMETHING,
    COUNT_SOMETHING,
    SORT_SOMETHING,
    GROW_SOMETHING,
    SING_TOGETHER,
    DANCE_TOGETHER,
    ADVENTURE_TOGETHER,
]
