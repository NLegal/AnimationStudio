from typing import List, Optional
from src.story_engine.models import Theme


class ThemeEngine:
    def __init__(self):
        self._usage_order: List[str] = []
        self._themes: List[Theme] = [
            Theme(
                id="lost-toy", name="Lost Toy",
                description="A beloved toy goes missing and friends help find it",
                suggested_assets=["Stuffed Animal", "Toy Box", "Blanket", "Search Light", "Magnifying Glass"],
                suggested_locations=["Bedroom", "Playroom", "Living Room", "Backyard"],
            ),
            Theme(
                id="birthday", name="Birthday",
                description="Celebrating a special birthday with friends",
                requires_song=True,
                suggested_assets=["Cake", "Candles", "Balloons", "Gift Boxes", "Party Hats", "Confetti", "Streamers"],
                suggested_locations=["Home", "Playground", "Party Hall", "Kitchen"],
            ),
            Theme(
                id="rainy-day", name="Rainy Day",
                description="Fun indoor activities on a rainy day",
                season="spring",
                suggested_assets=["Umbrella", "Raincoat", "Rain Boots", "Puddle", "Books", "Puzzle", "Rain Drops"],
                suggested_locations=["Home", "Living Room", "Playroom", "Window"],
            ),
            Theme(
                id="camping", name="Camping",
                description="Outdoor camping adventure under the stars",
                season="summer",
                requires_song=True,
                suggested_assets=["Tent", "Campfire", "Flashlight", "Sleeping Bag", "Marshmallows", "Stars", "Map"],
                suggested_locations=["Forest", "Campsite", "Mountain", "Lake"],
            ),
            Theme(
                id="beach", name="Beach",
                description="A fun day at the beach building sandcastles",
                season="summer",
                suggested_assets=["Sandcastle", "Beach Ball", "Bucket", "Shovel", "Seashells", "Sunscreen", "Towel"],
                suggested_locations=["Beach", "Ocean", "Boardwalk", "Shore"],
            ),
            Theme(
                id="zoo", name="Zoo",
                description="Visiting the zoo and learning about animals",
                suggested_assets=["Animal Figures", "Zoo Map", "Camera", "Binoculars", "Animal Food", "Tickets"],
                suggested_locations=["Zoo", "Animal Enclosures", "Petting Zoo", "Picnic Area"],
            ),
            Theme(
                id="treasure-hunt", name="Treasure Hunt",
                description="Following clues on a treasure hunt adventure",
                suggested_assets=["Treasure Map", "Compass", "Treasure Chest", "Gold Coins", "Gems", "Clue Cards"],
                suggested_locations=["Backyard", "Park", "Forest", "Playground"],
            ),
            Theme(
                id="school", name="School",
                description="A day of learning and fun at school",
                season="fall",
                suggested_assets=["Books", "Pencils", "Crayons", "Blackboard", "Desk", "Apple", "Backpack"],
                suggested_locations=["Classroom", "School", "Playground", "Library"],
            ),
            Theme(
                id="cooking", name="Cooking",
                description="Preparing a delicious meal or treat together",
                suggested_assets=["Bowls", "Spoons", "Apron", "Chef Hat", "Ingredients", "Recipe Book", "Mixer"],
                suggested_locations=["Kitchen", "Dining Room", "Cafe", "Backyard"],
            ),
            Theme(
                id="gardening", name="Gardening",
                description="Planting seeds and watching things grow",
                season="spring",
                suggested_assets=["Seeds", "Watering Can", "Shovel", "Flower Pot", "Soil", "Sunflower", "Garden Gloves"],
                suggested_locations=["Garden", "Backyard", "Park", "Greenhouse"],
            ),
            Theme(
                id="picnic", name="Picnic",
                description="Enjoying a picnic outdoors with friends",
                season="spring",
                suggested_assets=["Picnic Basket", "Blanket", "Sandwiches", "Fruit", "Juice Box", "Napkins", "Bubbles"],
                suggested_locations=["Park", "Meadow", "Beach", "Backyard"],
            ),
            Theme(
                id="building-blocks", name="Building Blocks",
                description="Building creative structures with blocks",
                suggested_assets=["Building Blocks", "Wooden Blocks", "Stacking Toys", "Toy Hammer", "Shape Sorter"],
                suggested_locations=["Playroom", "Living Room", "Classroom", "Bedroom"],
            ),
            Theme(
                id="flying-kites", name="Flying Kites",
                description="Flying colorful kites on a windy day",
                season="spring",
                suggested_assets=["Kite", "String", "Wind Sock", "Tail Ribbons", "Sky", "Clouds"],
                suggested_locations=["Park", "Hill", "Beach", "Meadow"],
            ),
            Theme(
                id="snow-day", name="Snow Day",
                description="Playing and exploring in the snow",
                season="winter",
                suggested_assets=["Snowman", "Snowflakes", "Scarf", "Mittens", "Hat", "Sled", "Ice Skates"],
                suggested_locations=["Backyard", "Park", "Hill", "Home"],
            ),
            Theme(
                id="space-adventure", name="Space Adventure",
                description="Blasting off on a space exploration journey",
                requires_song=True,
                suggested_assets=["Rocket Ship", "Astronaut Helmet", "Stars", "Planets", "Moon", "Space Suit", "Alien Friend"],
                suggested_locations=["Space", "Moon", "Planet", "Starship"],
            ),
            Theme(
                id="farm-visit", name="Farm Visit",
                description="Visiting a farm and meeting the animals",
                season="spring",
                suggested_assets=["Tractor", "Hay Bales", "Barn", "Farm Animals", "Eggs", "Milk Pail", "Fence"],
                suggested_locations=["Farm", "Barn", "Pasture", "Garden"],
            ),
            Theme(
                id="halloween", name="Halloween",
                description="Fun Halloween costumes and trick-or-treating",
                season="fall", holiday="halloween",
                requires_song=True,
                suggested_assets=["Costumes", "Pumpkin", "Candy", "Jack-o-Lantern", "Spider Web", "Ghost Decoration", "Treat Bag"],
                suggested_locations=["Home", "Neighborhood", "School", "Pumpkin Patch"],
            ),
            Theme(
                id="christmas", name="Christmas",
                description="Celebrating Christmas with family and friends",
                season="winter", holiday="christmas",
                requires_song=True,
                suggested_assets=["Christmas Tree", "Ornaments", "Lights", "Gifts", "Stockings", "Snowman", "Candy Cane"],
                suggested_locations=["Home", "Living Room", "Town Square", "Fireplace"],
            ),
            Theme(
                id="valentines-day", name="Valentine's Day",
                description="Showing love and appreciation to friends",
                season="winter", holiday="valentines",
                suggested_assets=["Hearts", "Valentine Cards", "Candy Hearts", "Flowers", "Teddy Bear", "Pink Decorations"],
                suggested_locations=["Classroom", "Home", "Craft Room", "Kitchen"],
            ),
            Theme(
                id="easter", name="Easter",
                description="Easter egg hunt and spring celebration",
                season="spring", holiday="easter",
                suggested_assets=["Easter Eggs", "Basket", "Bunny Ears", "Jellybeans", "Chocolate Bunny", "Grass", "Painted Eggs"],
                suggested_locations=["Backyard", "Park", "Garden", "Home"],
            ),
            Theme(
                id="st-patricks-day", name="St. Patrick's Day",
                description="Celebrating with green colors and luck",
                season="spring", holiday="st-patrick",
                suggested_assets=["Green Hat", "Shamrock", "Pot of Gold", "Rainbow", "Green Clothes", "Gold Coins"],
                suggested_locations=["Home", "School", "Town", "Park"],
            ),
            Theme(
                id="thanksgiving", name="Thanksgiving",
                description="Giving thanks for family and friends",
                season="fall", holiday="thanksgiving",
                suggested_assets=["Turkey", "Pumpkin Pie", "Cornucopia", "Fall Leaves", "Harvest Basket", "Dinner Table"],
                suggested_locations=["Home", "Dining Room", "Kitchen", "Grandma's House"],
            ),
            Theme(
                id="new-year", name="New Year",
                description="Celebrating the start of a new year",
                season="winter", holiday="new-year",
                suggested_assets=["Party Hats", "Noisemakers", "Confetti", "Clock", "Fireworks", "Sparkles"],
                suggested_locations=["Home", "Town Square", "Party Room", "Rooftop"],
            ),
            Theme(
                id="park-visit", name="Park Visit",
                description="Playing and exploring at the park",
                suggested_assets=["Swing", "Slide", "Sandbox", "Ball", "Bubbles", "Bench", "See-Saw"],
                suggested_locations=["Park", "Playground", "Meadow", "Pond"],
            ),
            Theme(
                id="library-day", name="Library Day",
                description="Discovering books and stories at the library",
                suggested_assets=["Books", "Story Time Rug", "Library Card", "Book Shelf", "Puppet", "Reading Chair"],
                suggested_locations=["Library", "Reading Room", "Story Corner", "Home"],
            ),
            Theme(
                id="music-class", name="Music Class",
                description="Learning about music and instruments",
                requires_song=True,
                suggested_assets=["Drum", "Tambourine", "Xylophone", "Maracas", "Guitar", "Sheet Music", "Microphone"],
                suggested_locations=["Music Room", "Classroom", "Stage", "Home"],
            ),
            Theme(
                id="art-day", name="Art Day",
                description="Creating beautiful art projects",
                suggested_assets=["Paint", "Crayons", "Paper", "Glue", "Scissors", "Clay", "Easel", "Paintbrush"],
                suggested_locations=["Art Room", "Classroom", "Backyard", "Kitchen Table"],
            ),
            Theme(
                id="splash-pad", name="Splash Pad",
                description="Cooling off and playing in the water",
                season="summer",
                suggested_assets=["Water Sprinklers", "Water Balloons", "Pool Toys", "Swimsuit", "Towel", "Sun Hat", "Goggles"],
                suggested_locations=["Splash Pad", "Backyard", "Pool", "Beach"],
            ),
        ]

    def select_theme(self, exclude: List[str] = None, holiday: str = None, season: str = None) -> Optional[Theme]:
        exclude = exclude or []
        candidates = [t for t in self._themes if t.id not in exclude]
        if not candidates:
            return None

        def score(t: Theme) -> float:
            s = 0.0
            if holiday and t.holiday == holiday:
                s += 2.0
            if season and t.season == season:
                s += 1.0
            if t.id not in self._usage_order:
                s += 0.5
            else:
                pos = self._usage_order.index(t.id)
                s -= pos * 0.1
            return s

        selected = max(candidates, key=score)
        if selected.id in self._usage_order:
            self._usage_order.remove(selected.id)
        self._usage_order.append(selected.id)
        return selected

    def get_themes_for_season(self, season: str) -> List[Theme]:
        return [t for t in self._themes if t.season == season]

    def get_themes_for_holiday(self, holiday: str) -> List[Theme]:
        return [t for t in self._themes if t.holiday == holiday]
