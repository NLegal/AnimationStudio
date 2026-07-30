from __future__ import annotations
import random
from typing import List, Dict, Optional

from src.story_engine.models import Theme, LearningObjective


THEME_ASSETS: Dict[str, List[str]] = {
    "birthday": ["cake", "candles", "balloons", "gift boxes", "party hats", "confetti", "streamers", "party plate"],
    "beach": ["sand toys", "pail", "shovel", "beach ball", "towel", "sunglasses", "sun hat", "bucket"],
    "school": ["pencils", "books", "backpack", "crayons", "paper", "ruler", "chalkboard", "desk"],
    "lost_toy": ["stuffed animal", "basket", "clues", "magnifying glass", "map", "lantern"],
    "rainy_day": ["umbrella", "rain boots", "raincoat", "puddle", "raindrop", "rainbow"],
    "camping": ["tent", "campfire", "sleeping bag", "flashlight", "marshmallow", "compass"],
    "zoo": ["animal cage", "binoculars", "zoo map", "animal food", "camera"],
    "treasure_hunt": ["treasure map", "compass", "chest", "gold coins", "gemstone", "spyglass"],
    "cooking": ["mixing bowl", "spoon", "apron", "oven mitts", "rolling pin", "cookie cutter"],
    "gardening": ["watering can", "seeds", "shovel", "flower pot", "soil bag", "sunflower"],
    "picnic": ["picnic basket", "blanket", "sandwich", "apple", "juice box", "napkin"],
    "building_blocks": ["blocks", "planks", "hammer", "screws", "blueprint", "hard hat"],
    "flying_kites": ["kite", "string", "wind sock", "ribbon", "breeze"],
    "snow_day": ["snowman kit", "sled", "mittens", "scarf", "snowball", "hot cocoa"],
    "space_adventure": ["spaceship", "helmet", "stars", "planet", "moon rock", "telescope"],
    "farm_visit": ["hay bale", "feed bucket", "milking stool", "egg basket", "scarecrow"],
    "halloween": ["pumpkin", "costume", "candy bucket", "ghost decoration", "glow stick"],
    "christmas": ["ornament", "stocking", "gingerbread", "candy cane", "star topper", "wreath"],
    "lost_balloon": ["balloon", "string", "net", "ladder", "cloud"],
    "wrong_color": ["paint", "paintbrush", "canvas", "color wheel", "smock"],
    "counting": ["counting beads", "number cards", "abacus", "counting blocks", "number chart"],
    "sorting": ["sorting tray", "shape blocks", "color bowls", "matching cards", "labels"],
    "cleaning": ["sponge", "broom", "dustpan", "soap", "bucket", "rag"],
    "music": ["drum", "tambourine", "maraca", "xylophone", "microphone", "kazoo"],
    "growing": ["plant pot", "watering can", "soil", "seed packet", "sunlight", "growth chart"],
    "visit": ["suitcase", "map", "camera", "ticket", "passport"],
}

OBJECTIVE_ASSETS: Dict[str, List[str]] = {
    "count_to_five": ["counting beads", "number cards", "apple counters", "finger puppets", "dice"],
    "count_to_ten": ["number chart", "counting blocks", "abacus", "ten frame", "number line"],
    "recognize_red": ["red apple", "red balloon", "red crayon", "red flower", "red block"],
    "recognize_blue": ["blue balloon", "blue paint", "blue block", "blue flower", "blue bird"],
    "recognize_yellow": ["yellow sun", "yellow banana", "yellow crayon", "yellow star", "yellow duck"],
    "recognize_green": ["green leaf", "green frog", "green crayon", "green block", "green apple"],
    "identify_circle": ["circle block", "wheel", "clock", "plate", "coin"],
    "identify_square": ["square block", "window", "picture frame", "tile", "book"],
    "identify_triangle": ["triangle block", "roof", "cone", "flag", "pie slice"],
    "learn_duck_sounds": ["duck puppet", "pond picture", "duck feather", "yellow feather"],
    "sort_shapes": ["sorting tray", "shape blocks", "matching cards", "shape sorter"],
    "tie_shoes": ["shoe", "shoelace", "practice board", "ribbon", "bow template"],
    "wash_hands": ["soap", "towel", "sink", "water", "hand puppet"],
    "name_farm_animals": ["animal figures", "flash cards", "barn picture", "feed bucket"],
    "brush_teeth": ["toothbrush", "toothpaste", "dental model", "timer", "cup"],
    "share_toys": ["toy car", "building blocks", "ball", "teddy bear", "puzzle"],
    "learn_alphabet": ["letter blocks", "alphabet chart", "letter cards", "magnetic letters"],
    "learn_weather": ["weather chart", "umbrella", "sun picture", "rain cloud", "snowflake"],
    "learn_emotions": ["emotion cards", "mirror", "puppet", "feeling chart"],
    "learn_colors": ["color wheel", "paint set", "colored blocks", "rainbow chart"],
    "learn_animals": ["animal cards", "stuffed animals", "nature book", "animal puzzle"],
    "practice_friendship": ["friendship bracelet", "sharing jar", "toy set", "pair cards"],
    "practice_motor_skills": ["clay", "scissors", "stringing beads", "puzzle pieces"],
    "learn_music": ["drum", "bell", "xylophone", "shaker egg", "song card"],
    "learn_dance": ["ribbon wand", "scarf", "dance mat", "music player"],
    "learn_seasons": ["season wheel", "weather clothes", "calendar", "nature tray"],
    "learn_transportation": ["toy car", "bus", "train", "airplane", "boat"],
    "learn_community_helpers": ["costume pieces", "tool set", "helper cards", "vehicle toys"],
}

DEFAULT_ASSETS: List[str] = ["play mat", "cushion", "story book", "puppet", "music player"]


class AssetEngine:
    def __init__(self):
        self.theme_assets: Dict[str, List[str]] = {k: list(v) for k, v in THEME_ASSETS.items()}
        self.objective_assets: Dict[str, List[str]] = {k: list(v) for k, v in OBJECTIVE_ASSETS.items()}

    def select_assets(self, theme: Theme, objective: LearningObjective) -> List[str]:
        assets: List[str] = []
        assets.extend(self.theme_assets.get(theme.id, []))
        assets.extend(self.objective_assets.get(objective.id, []))
        if not assets:
            assets.extend(DEFAULT_ASSETS)
        seen: set = set()
        deduped = []
        for a in assets:
            if a not in seen:
                seen.add(a)
                deduped.append(a)
        return deduped

    def get_assets_for_theme(self, theme_id: str) -> List[str]:
        return list(self.theme_assets.get(theme_id, []))

    def get_assets_for_objective(self, objective_id: str) -> List[str]:
        return list(self.objective_assets.get(objective_id, []))

    def register_theme_assets(self, theme_id: str, assets: List[str]):
        self.theme_assets[theme_id] = assets

    def register_objective_assets(self, objective_id: str, assets: List[str]):
        self.objective_assets[objective_id] = assets
