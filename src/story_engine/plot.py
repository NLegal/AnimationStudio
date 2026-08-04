from __future__ import annotations
import random
from typing import List, Optional, Dict

from src.story_engine.models import Theme


CONFLICT_THEME_MAP: Dict[str, str] = {
    "lost_balloon": "A colorful balloon floats away and needs to be retrieved",
    "wrong_color": "A character uses the wrong color for their drawing or craft",
    "cant_count": "A character has trouble counting items correctly",
    "missing_puzzle_piece": "A puzzle piece is lost and the picture is incomplete",
    "dropped_cookie": "A cookie falls on the ground and a character feels sad",
    "needs_help_cleaning": "A space is too messy for one character to clean alone",
    "cant_find_teddy": "A favorite stuffed teddy bear has gone missing",
    "plant_needs_water": "A plant is droopy and needs watering to survive",
    "forgot_backpack": "A character realizes they left their backpack somewhere",
    "broken_toy": "A favorite toy breaks and needs to be fixed",
    "spilled_paint": "Paint spills on the floor during art time",
    "wrong_shoes": "A character puts on mismatched shoes",
    "scared_of_thunder": "A character is frightened by a loud thunder sound",
    "cant_reach_shelf": "A character cannot reach something on a high shelf",
    "lost_in_store": "A character gets separated from their grownup in a store",
    "tower_fell_down": "A block tower collapses before it is finished",
    "cold_soup": "The soup is too cold and needs warming up",
    "bedtime_resistance": "A character does not want to go to bed",
    "sharing_struggle": "A character finds it hard to share a toy with a friend",
    "stuck_zipper": "A jacket zipper gets stuck and won't move",
}

CONFLICTS_BY_THEME: Dict[str, List[str]] = {
    "birthday": ["lost_balloon", "dropped_cookie", "wrong_color", "cant_count"],
    "beach": ["cant_find_teddy", "forgot_backpack", "spilled_paint", "cant_reach_shelf"],
    "school": ["cant_count", "wrong_color", "forgot_backpack", "missing_puzzle_piece"],
    "lost_toy": ["cant_find_teddy", "missing_puzzle_piece", "lost_balloon"],
    "rainy_day": ["scared_of_thunder", "cant_find_teddy", "stuck_zipper", "spilled_paint"],
    "camping": ["lost_balloon", "cant_find_teddy", "cold_soup", "stuck_zipper"],
    "treasure_hunt": ["missing_puzzle_piece", "lost_balloon", "cant_reach_shelf"],
    "cooking": ["dropped_cookie", "cold_soup", "wrong_color", "cant_count"],
    "gardening": ["plant_needs_water", "cant_count", "wrong_color", "tower_fell_down"],
    "picnic": ["dropped_cookie", "forgot_backpack", "lost_balloon", "spilled_paint"],
    "building_blocks": ["tower_fell_down", "missing_puzzle_piece", "wrong_color"],
    "flying_kites": ["lost_balloon", "cant_reach_shelf", "stuck_zipper"],
    "snow_day": ["stuck_zipper", "cant_find_teddy", "cold_soup", "scared_of_thunder"],
    "space_adventure": ["cant_count", "missing_puzzle_piece", "lost_in_store"],
    "farm_visit": ["cant_find_teddy", "plant_needs_water", "forgot_backpack", "needs_help_cleaning"],
    "halloween": ["lost_balloon", "cant_find_teddy", "spilled_paint", "stuck_zipper"],
    "christmas": ["broken_toy", "wrong_color", "dropped_cookie", "cant_count"],
    "lost_balloon": ["lost_balloon", "cant_reach_shelf"],
    "wrong_color": ["wrong_color", "spilled_paint", "cant_count"],
    "counting": ["cant_count", "missing_puzzle_piece", "tower_fell_down"],
    "sorting": ["wrong_color", "cant_count", "needs_help_cleaning"],
    "cleaning": ["needs_help_cleaning", "cant_find_teddy", "missing_puzzle_piece"],
    "music": ["wrong_color", "cant_count", "forgot_backpack"],
    "growing": ["plant_needs_water", "cant_count", "cold_soup"],
    "visit": ["forgot_backpack", "cant_find_teddy", "lost_in_store"],
    "zoo": ["cant_find_teddy", "forgot_backpack", "lost_in_store", "spilled_paint"],
    "park_visit": ["lost_balloon", "cant_find_teddy", "forgot_backpack", "tower_fell_down"],
    "library_day": ["forgot_backpack", "missing_puzzle_piece", "cant_find_teddy"],
    "music_class": ["wrong_color", "cant_count", "stuck_zipper"],
    "art_day": ["spilled_paint", "wrong_color", "cant_count"],
    "splash_pad": ["cold_soup", "forgot_backpack", "cant_find_teddy"],
    "valentines_day": ["dropped_cookie", "cant_find_teddy", "wrong_color"],
    "easter": ["cant_find_teddy", "missing_puzzle_piece", "lost_balloon"],
    "st_patricks_day": ["missing_puzzle_piece", "cant_find_teddy", "forgot_backpack"],
    "thanksgiving": ["dropped_cookie", "cold_soup", "cant_count"],
    "new_year": ["lost_balloon", "cant_count", "forgot_backpack"],
}


RESOLUTION_METHODS: List[str] = [
    "friend_helps",
    "practice",
    "teacher_explains",
    "family_helps",
    "character_learns",
    "discovery",
    "celebration",
]

RESOLUTION_DESCRIPTIONS: Dict[str, str] = {
    "friend_helps": "A friend arrives and kindly helps solve the problem together",
    "practice": "The character tries again and improves with more practice",
    "teacher_explains": "A teacher gently explains how to solve the problem",
    "family_helps": "A family member steps in with love and guidance",
    "character_learns": "The character figures it out all by themselves",
    "discovery": "A lucky discovery reveals the solution unexpectedly",
    "celebration": "Everyone celebrates the happy outcome together",
}

RESOLUTIONS_BY_CONFLICT: Dict[str, List[str]] = {
    "lost_balloon": ["friend_helps", "discovery", "family_helps"],
    "wrong_color": ["teacher_explains", "friend_helps", "character_learns"],
    "cant_count": ["practice", "teacher_explains", "friend_helps"],
    "missing_puzzle_piece": ["discovery", "friend_helps", "family_helps"],
    "dropped_cookie": ["family_helps", "friend_helps", "celebration"],
    "needs_help_cleaning": ["friend_helps", "family_helps", "practice"],
    "cant_find_teddy": ["discovery", "family_helps", "friend_helps"],
    "plant_needs_water": ["practice", "discovery", "friend_helps"],
    "forgot_backpack": ["discovery", "friend_helps", "family_helps"],
    "broken_toy": ["friend_helps", "family_helps", "practice"],
    "spilled_paint": ["family_helps", "practice", "friend_helps"],
    "wrong_shoes": ["character_learns", "friend_helps", "teacher_explains"],
    "scared_of_thunder": ["family_helps", "friend_helps", "teacher_explains"],
    "cant_reach_shelf": ["friend_helps", "family_helps", "discovery"],
    "lost_in_store": ["family_helps", "friend_helps", "discovery"],
    "tower_fell_down": ["practice", "friend_helps", "character_learns"],
    "cold_soup": ["family_helps", "friend_helps", "practice"],
    "bedtime_resistance": ["family_helps", "celebration", "character_learns"],
    "sharing_struggle": ["teacher_explains", "friend_helps", "family_helps"],
    "stuck_zipper": ["practice", "friend_helps", "family_helps"],
}


class ConflictEngine:
    def __init__(self):
        self.conflicts: Dict[str, str] = dict(CONFLICT_THEME_MAP)
        self.conflicts_by_theme: Dict[str, List[str]] = {}
        for k, v in CONFLICTS_BY_THEME.items():
            self.conflicts_by_theme[k] = list(v)
            self.conflicts_by_theme[k.replace("_", "-")] = list(v)

    def select_conflict(self, exclude: Optional[List[str]] = None, theme: Optional[str] = None) -> str:
        pool = list(self.conflicts.keys())
        if theme and theme in self.conflicts_by_theme:
            theme_conflicts = self.conflicts_by_theme[theme]
            pool = [c for c in pool if c in theme_conflicts]
        if exclude:
            pool = [c for c in pool if c not in exclude]
        if not pool:
            pool = list(self.conflicts.keys())
            if exclude:
                pool = [c for c in pool if c not in exclude]
        return random.choice(pool) if pool else "lost_balloon"

    def get_conflict_description(self, conflict_id: str) -> str:
        return self.conflicts.get(conflict_id, "A small problem needs solving")

    def get_conflicts_for_theme(self, theme_id: str) -> List[str]:
        return list(self.conflicts_by_theme.get(theme_id, []))

    def register_theme_conflicts(self, theme_id: str, conflicts: List[str]):
        self.conflicts_by_theme[theme_id] = conflicts
        self.conflicts_by_theme[theme_id.replace("_", "-")] = conflicts


class ResolutionEngine:
    def __init__(self):
        self.resolutions_by_conflict: Dict[str, List[str]] = {
            k: list(v) for k, v in RESOLUTIONS_BY_CONFLICT.items()
        }
        self.resolution_descriptions: Dict[str, str] = dict(RESOLUTION_DESCRIPTIONS)

    def select_resolution(self, conflict: str, characters: List[str]) -> str:
        pool = self.resolutions_by_conflict.get(conflict, list(RESOLUTION_DESCRIPTIONS.keys()))
        if not pool:
            pool = list(RESOLUTION_DESCRIPTIONS.keys())
        return random.choice(pool)

    def get_resolutions_for_conflict(self, conflict: str) -> List[str]:
        return list(self.resolutions_by_conflict.get(conflict, []))

    def generate_resolution_description(
        self,
        resolution_type: str,
        conflict: str,
        main_char: str,
        helper: Optional[str] = None,
    ) -> str:
        conflict_desc = CONFLICT_THEME_MAP.get(conflict, "a small problem")

        templates = {
            "friend_helps": f"{main_char} and {helper or 'a friend'} work together and solve {conflict_desc}.",
            "practice": f"{main_char} keeps trying and gets better with practice, solving {conflict_desc}.",
            "teacher_explains": f"Teacher Owl gently explains how to fix {conflict_desc}, and {main_char} learns something new.",
            "family_helps": f"{main_char}'s family comes with love and help, making {conflict_desc} disappear.",
            "character_learns": f"{main_char} thinks carefully and figures out how to solve {conflict_desc} all alone.",
            "discovery": f"With a happy surprise, {main_char} discovers the answer to {conflict_desc}.",
            "celebration": f"Everyone celebrates together, turning {conflict_desc} into a joyful moment.",
        }
        return templates.get(resolution_type, f"{main_char} solves {conflict_desc} happily.")
