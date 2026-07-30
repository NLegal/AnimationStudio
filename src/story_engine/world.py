from __future__ import annotations
import random
from typing import List, Optional, Dict

from src.story_engine.models import Theme, LearningObjective


LOCATIONS_BY_ZONE: Dict[str, List[str]] = {
    "Residential": [
        "Main Family Home",
        "Grandparents' Cottage",
        "Best Friend's House",
        "Neighborhood Park",
        "Community Garden",
        "Tree-Lined Walking Path",
        "Mailbox Row",
    ],
    "Downtown": [
        "Town Hall",
        "Library",
        "Bakery",
        "Ice Cream Shop",
        "Toy Store",
        "Music Store",
        "Flower Shop",
        "Pet Shop",
        "Post Office",
        "Police Station",
        "Fire Station",
        "Clinic",
        "Bus Stop",
        "Town Square & Gazebo",
        "Wishing Fountain",
    ],
    "School": [
        "Main School Building",
        "Preschool Wing",
        "Daycare Center",
        "Science Center",
        "Music School",
        "Art Studio",
        "School Library",
        "Outdoor Classroom",
        "School Garden",
        "School Playground",
        "Sports Field",
    ],
    "Playground": [
        "Main Playground Structure",
        "Splash Pad",
        "Soccer Field",
        "Basketball Court",
        "Mini Golf Course",
        "Picnic Area",
        "Camping Area",
        "Skate Park",
        "Bike Trail",
        "Restroom Pavilion",
    ],
    "Farm": [
        "Main Barn",
        "Chicken Coop",
        "Cow Pasture",
        "Horse Stable",
        "Vegetable Garden",
        "Corn Field",
        "Windmill",
        "Tractor Shed",
        "Fruit Tree Orchard",
        "Farm Pond",
        "Pumpkin Patch",
        "Hay Storage",
    ],
    "Forest": [
        "Forest Entrance",
        "Wandering Path",
        "Crystal River",
        "Waterfall Pool",
        "Lake Serenity",
        "Wooden Bridge",
        "Flower Meadow",
        "Apple Orchard",
        "Friendly Cave",
        "Hiking Trail",
        "Butterfly Garden",
        "Bee Garden",
        "Treehouse Village",
    ],
    "Beach": [
        "Main Beach",
        "Oceanfront Shallow Water",
        "Wooden Pier",
        "Lighthouse",
        "Boat Dock",
        "Shell Collecting Area",
        "Palm Tree Grove",
        "Beach Playground",
        "Ice Cream Stand",
        "Beachside Pavilion",
    ],
    "Mountains": [
        "Mountain Base Trailhead",
        "Pine Forest Slope",
        "Lookout Point",
        "Summit Meadow",
        "Cable Car Station",
        "Winter Sledding Hill",
        "Mountain Stream",
    ],
    "Fantasy": [
        "Rainbow Castle",
        "Cloud Village",
        "Friendly Dragon Cave",
        "Magic Forest",
        "Moon Garden",
        "Toy Kingdom",
        "Robot Workshop",
        "Candy Village",
        "Rainbow Bridge",
    ],
}

ALL_LOCATIONS: List[str] = [loc for zone_locs in LOCATIONS_BY_ZONE.values() for loc in zone_locs]

WEATHER_OPTIONS: List[str] = [
    "clear", "cloudy", "rain", "snow", "wind", "rainbow", "fog"
]

SEASONS: List[str] = ["spring", "summer", "autumn", "winter"]

SEASON_WEATHER_MAP: Dict[str, List[str]] = {
    "spring": ["clear", "cloudy", "rain", "wind", "rainbow", "fog"],
    "summer": ["clear", "cloudy", "rain", "wind", "rainbow"],
    "autumn": ["clear", "cloudy", "rain", "wind", "fog"],
    "winter": ["clear", "cloudy", "snow", "wind", "fog"],
}

ZONE_KEYWORDS: Dict[str, List[str]] = {
    "Residential": ["home", "house", "family", "neighbor", "garden", "mailbox", "path"],
    "Downtown": ["town", "shop", "store", "market", "library", "hall", "station"],
    "School": ["school", "classroom", "preschool", "academy", "teacher", "student", "learn"],
    "Playground": ["playground", "park", "slide", "swing", "splash", "picnic", "play"],
    "Farm": ["barn", "farm", "field", "animal", "tractor", "orchard", "pond", "crop"],
    "Forest": ["forest", "wood", "river", "trail", "tree", "meadow", "garden", "nature"],
    "Beach": ["beach", "ocean", "sand", "lighthouse", "pier", "shell", "shore"],
    "Mountains": ["mountain", "hill", "peak", "trail", "sled", "cable", "summit"],
    "Fantasy": ["castle", "kingdom", "dragon", "magic", "rainbow", "candy", "cloud", "moon"],
}


class WorldEngine:
    def __init__(self):
        self.current_season: str = "spring"
        self.locations_by_zone: Dict[str, List[str]] = {
            z: list(locs) for z, locs in LOCATIONS_BY_ZONE.items()
        }
        self._all_locations = list(ALL_LOCATIONS)

    def select_location(self, exclude: Optional[List[str]] = None, zone: Optional[str] = None) -> str:
        pool = self._all_locations
        if zone and zone in self.locations_by_zone:
            pool = self.locations_by_zone[zone]
        if exclude:
            pool = [l for l in pool if l not in exclude]
        if not pool:
            pool = list(self._all_locations)
            if exclude:
                pool = [l for l in pool if l not in exclude]
        return random.choice(pool) if pool else "Main Family Home"

    def select_weather(self, season: Optional[str] = None) -> str:
        s = season or self.current_season
        pool = SEASON_WEATHER_MAP.get(s, ["clear"])
        return random.choice(pool)

    def select_season(self) -> str:
        idx = SEASONS.index(self.current_season) if self.current_season in SEASONS else 0
        next_idx = (idx + 1) % len(SEASONS)
        self.current_season = SEASONS[next_idx]
        return self.current_season

    def get_locations_for_zone(self, zone: str) -> List[str]:
        return list(self.locations_by_zone.get(zone, []))

    def get_weather_for_season(self, season: str) -> List[str]:
        return list(SEASON_WEATHER_MAP.get(season, ["clear"]))

    def get_all_locations(self) -> List[str]:
        return list(self._all_locations)

    def get_all_zones(self) -> List[str]:
        return list(self.locations_by_zone.keys())

    def find_zone_for_location(self, location: str) -> Optional[str]:
        for zone, locs in self.locations_by_zone.items():
            if location in locs:
                return zone
        return None
