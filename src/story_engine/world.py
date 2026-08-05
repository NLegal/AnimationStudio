from __future__ import annotations
import random
from typing import List, Optional, Dict

from src.story_engine.models import Theme, LearningObjective
from src.story_engine.catalog import StoryCatalog


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

# Canonical World-bible identifiers (World/<Zone>/<ZONE>.md) for each story
# location, where the bible defines one.  Locations without a bible entry
# resolve to None so production can fall back to the catalog display name.
LOCATION_ID_MAP: Dict[str, Optional[str]] = {
    "Main Family Home": "ENV_Residential_001",
    "Grandparents' Cottage": "ENV_Residential_002",
    "Best Friend's House": "ENV_Residential_003",
    "Neighborhood Park": "ENV_Residential_016",
    "Community Garden": "ENV_Residential_017",
    "Tree-Lined Walking Path": "ENV_Residential_018",
    "Mailbox Row": "ENV_Residential_019",
    "Town Hall": "ENV_Downtown_001",
    "Library": "ENV_Downtown_002",
    "Bakery": "ENV_Downtown_003",
    "Ice Cream Shop": "ENV_Downtown_004",
    "Toy Store": "ENV_Downtown_005",
    "Music Store": "ENV_Downtown_006",
    "Flower Shop": "ENV_Downtown_007",
    "Pet Shop": "ENV_Downtown_008",
    "Post Office": "ENV_Downtown_009",
    "Police Station": "ENV_Downtown_010",
    "Fire Station": "ENV_Downtown_011",
    "Clinic": "ENV_Downtown_012",
    "Bus Stop": "ENV_Downtown_013",
    "Town Square & Gazebo": "ENV_Downtown_014",
    "Wishing Fountain": "ENV_Downtown_016",
    "Main School Building": "ENV_School_001",
    "Preschool Wing": "ENV_School_017",
    "Daycare Center": "ENV_School_017",
    "Science Center": "ENV_School_011",
    "Music School": "ENV_School_006",
    "Art Studio": "ENV_School_007",
    "School Library": "ENV_School_012",
    "Outdoor Classroom": "ENV_School_016",
    "School Garden": "ENV_School_015",
    "School Playground": "ENV_School_009",
    "Sports Field": "ENV_School_009",
    "Main Playground Structure": "ENV_Playground_001",
    "Splash Pad": "ENV_Playground_008",
    "Soccer Field": "ENV_Playground_009",
    "Basketball Court": "ENV_Playground_010",
    "Mini Golf Course": "ENV_Playground_011",
    "Picnic Area": "ENV_Forest_015",
    "Camping Area": "ENV_Forest_016",
    "Skate Park": "ENV_Playground_012",
    "Bike Trail": "ENV_Playground_013",
    "Restroom Pavilion": "ENV_Playground_015",
    "Main Barn": "ENV_Farm_001",
    "Chicken Coop": "ENV_Farm_003",
    "Cow Pasture": "ENV_Farm_004",
    "Horse Stable": "ENV_Farm_002",
    "Vegetable Garden": "ENV_Farm_006",
    "Corn Field": "ENV_Farm_007",
    "Windmill": "ENV_Farm_010",
    "Tractor Shed": "ENV_Farm_011",
    "Fruit Tree Orchard": "ENV_Farm_013",
    "Farm Pond": "ENV_Farm_014",
    "Pumpkin Patch": "ENV_Farm_009",
    "Hay Storage": "ENV_Farm_012",
    "Forest Entrance": "ENV_Forest_001",
    "Wandering Path": "ENV_Forest_002",
    "Crystal River": "ENV_Forest_004",
    "Waterfall Pool": "ENV_Forest_005",
    "Lake Serenity": "ENV_Forest_006",
    "Wooden Bridge": "ENV_Forest_012",
    "Flower Meadow": "ENV_Forest_007",
    "Apple Orchard": "ENV_Forest_013",
    "Friendly Cave": "ENV_Forest_011",
    "Hiking Trail": "ENV_Forest_002",
    "Butterfly Garden": "ENV_Forest_009",
    "Bee Garden": "ENV_Forest_010",
    "Treehouse Village": "ENV_Forest_008",
    "Main Beach": "ENV_Beach_001",
    "Oceanfront Shallow Water": "ENV_Beach_002",
    "Wooden Pier": "ENV_Beach_003",
    "Lighthouse": "ENV_Beach_004",
    "Boat Dock": "ENV_Beach_005",
    "Shell Collecting Area": "ENV_Beach_006",
    "Palm Tree Grove": "ENV_Beach_007",
    "Beach Playground": "ENV_Beach_008",
    "Ice Cream Stand": "ENV_Beach_009",
    "Beachside Pavilion": None,
    "Mountain Base Trailhead": "ENV_Mountains_001",
    "Pine Forest Slope": "ENV_Mountains_003",
    "Lookout Point": "ENV_Mountains_002",
    "Summit Meadow": "ENV_Mountains_007",
    "Cable Car Station": "ENV_Mountains_006",
    "Winter Sledding Hill": None,
    "Mountain Stream": "ENV_Mountains_004",
    "Rainbow Castle": "ENV_Fantasy_001",
    "Cloud Village": "ENV_Fantasy_002",
    "Friendly Dragon Cave": "ENV_Fantasy_003",
    "Magic Forest": "ENV_Fantasy_004",
    "Moon Garden": "ENV_Fantasy_005",
    "Toy Kingdom": "ENV_Fantasy_006",
    "Robot Workshop": "ENV_Fantasy_007",
    "Candy Village": "ENV_Fantasy_008",
    "Rainbow Bridge": None,
}

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
    def __init__(self, catalog: Optional[StoryCatalog] = None):
        self.current_season: str = "spring"
        self.catalog = catalog
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

    def location_id(self, location: str) -> Optional[str]:
        """Canonical World-bible identifier (ENV_*) for a story location."""
        return LOCATION_ID_MAP.get(location)

    def location_zone(self, location: str) -> Optional[str]:
        """Human-readable zone label for a location from the catalog, if present."""
        if self.catalog is None or not self.catalog.available:
            return None
        record = self.catalog.resolve_location(location)
        if not record:
            return None
        return self.catalog.zone_title(record["zone"])
