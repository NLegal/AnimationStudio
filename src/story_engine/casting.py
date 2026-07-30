from typing import List, Optional
from src.story_engine.models import CharacterInfo


class CharacterEngine:
    def __init__(self):
        self._characters: List[CharacterInfo] = [
            CharacterInfo(
                character_id="lily-bunny", name="Lily Bunny", role="student", age_group="child",
                personality=["curious", "kind", "gentle", "imaginative", "cheerful"],
                catchphrases=["Oh my whiskers!", "Let's explore!", "Hop to it!"],
                favorite_things=["carrots", "butterflies", "painting", "her yellow bow", "story time"],
                relationships={
                    "ben-bear": "best friend", "daisy-duck": "friend", "charlie-fox": "friend",
                    "teacher-owl": "teacher", "mommy-bunny": "mother", "daddy-bunny": "father",
                    "grandma-bunny": "grandmother", "grandpa-bunny": "grandfather", "baby-bunny": "sibling",
                    "doctor-panda": "family doctor", "librarian-hedgehog": "story time friend",
                    "dog": "neighbor's pet", "cat": "neighbor's pet",
                },
                home="The Bunny Burrow",
                preferred_locations=["Sunny Meadows", "Butterfly Garden", "Playground", "Kitchen", "Classroom"],
            ),
            CharacterInfo(
                character_id="ben-bear", name="Ben Bear", role="student", age_group="child",
                personality=["strong", "helpful", "brave", "loyal", "energetic"],
                catchphrases=["Beary cool!", "I've got this!", "Rawr-some!"],
                favorite_things=["honey", "climbing trees", "building forts", "his blue scarf", "naps"],
                relationships={
                    "lily-bunny": "best friend", "daisy-duck": "friend", "charlie-fox": "friend",
                    "teacher-owl": "teacher", "doctor-panda": "family doctor",
                    "firefighter-dalmatian": "role model", "chef-pig": "makes honey treats",
                    "dog": "friend",
                },
                home="The Bear Cave",
                preferred_locations=["Forest", "Playground", "River", "Home", "Gym"],
            ),
            CharacterInfo(
                character_id="daisy-duck", name="Daisy Duck", role="student", age_group="child",
                personality=["cheerful", "chatty", "friendly", "bubbly", "helpful"],
                catchphrases=["Quack-tastic!", "Waddly-doo!", "Happy quacks!"],
                favorite_things=["swimming", "splashing puddles", "feathers", "quacking games", "rainy days"],
                relationships={
                    "lily-bunny": "friend", "ben-bear": "friend", "charlie-fox": "friend",
                    "teacher-owl": "teacher", "musician-parrot": "music teacher",
                    "mail-carrier-turtle": "pen pal",
                },
                home="The Duck Pond",
                preferred_locations=["Pond", "Playground", "Garden", "Lake", "Music Room"],
            ),
            CharacterInfo(
                character_id="charlie-fox", name="Charlie Fox", role="student", age_group="child",
                personality=["clever", "quick", "playful", "curious", "witty"],
                catchphrases=["Sly move!", "Foxy idea!", "I found a clue!"],
                favorite_things=["puzzles", "exploring", "berries", "hiding games", "treasure maps"],
                relationships={
                    "lily-bunny": "friend", "ben-bear": "friend", "daisy-duck": "friend",
                    "teacher-owl": "teacher", "police-officer-beaver": "uncle",
                    "librarian-hedgehog": "favorite librarian",
                },
                home="The Fox Den",
                preferred_locations=["Forest", "Meadow", "Playground", "Hill", "Library"],
            ),
            CharacterInfo(
                character_id="teacher-owl", name="Teacher Owl", role="adult", age_group="adult",
                personality=["wise", "patient", "knowledgeable", "kind", "encouraging"],
                catchphrases=["Wise choice!", "Whoo wants to learn?", "Excellent thinking!"],
                favorite_things=["books", "teaching", "tea", "star gazing", "glasses"],
                relationships={
                    "lily-bunny": "student", "ben-bear": "student", "daisy-duck": "student",
                    "charlie-fox": "student", "doctor-panda": "friend",
                    "librarian-hedgehog": "close friend", "musician-parrot": "colleague",
                    "grandma-bunny": "old friend",
                },
                home="The Schoolhouse",
                preferred_locations=["Classroom", "Library", "Garden", "Observatory"],
            ),
            CharacterInfo(
                character_id="doctor-panda", name="Doctor Panda", role="adult", age_group="adult",
                personality=["caring", "gentle", "kind", "reassuring", "calm"],
                catchphrases=["Let's check your health!", "Bamboo-tiful!", "A spoonful of love!"],
                favorite_things=["bamboo", "health charts", "helping", "warm blankets", "stethoscope"],
                relationships={
                    "lily-bunny": "patient", "ben-bear": "patient", "daisy-duck": "patient",
                    "charlie-fox": "patient", "teacher-owl": "friend", "chef-pig": "cooking buddy",
                    "mommy-bunny": "friend",
                },
                home="The Clinic",
                preferred_locations=["Clinic", "Home", "Park", "Community Center"],
            ),
            CharacterInfo(
                character_id="chef-pig", name="Chef Pig", role="adult", age_group="adult",
                personality=["creative", "enthusiastic", "messy", "fun", "generous"],
                catchphrases=["Oink-tastic dish!", "Time to cook!", "Delicious!"],
                favorite_things=["cooking", "tasting", "recipes", "aprons", "fresh ingredients"],
                relationships={
                    "farmer-goat": "best friend", "doctor-panda": "cooking buddy",
                    "lily-bunny": "taste tester", "ben-bear": "makes honey treats",
                    "teacher-owl": "catering for school events",
                    "grandma-bunny": "recipe exchange",
                },
                home="The Kitchen",
                preferred_locations=["Restaurant", "Kitchen", "Farmer's Market", "Garden"],
            ),
            CharacterInfo(
                character_id="farmer-goat", name="Farmer Goat", role="adult", age_group="adult",
                personality=["hardworking", "friendly", "down-to-earth", "cheerful", "strong"],
                catchphrases=["Baa-rilliant!", "Happy harvest!", "Growing good things!"],
                favorite_things=["fresh hay", "sunny fields", "growing vegetables", "tractor", "overalls"],
                relationships={
                    "chef-pig": "best friend", "horse": "works together",
                    "cow": "cares for", "chicken": "cares for",
                    "sheep": "cares for", "pig": "cares for",
                    "lily-bunny": "farm visitor", "ben-bear": "farm helper",
                },
                home="The Farm",
                preferred_locations=["Barn", "Pasture", "Garden", "Tractor Shed"],
            ),
            CharacterInfo(
                character_id="firefighter-dalmatian", name="Firefighter Dalmatian", role="adult", age_group="adult",
                personality=["brave", "helpful", "energetic", "cheerful", "heroic"],
                catchphrases=["Spot on!", "Let's roll!", "Saving the day!"],
                favorite_things=["fire trucks", "spots", "rescue drills", "water hoses", "dog treats"],
                relationships={
                    "police-officer-beaver": "coworker", "teacher-owl": "safety drill partner",
                    "ben-bear": "role model", "lily-bunny": "teaches fire safety",
                    "dog": "cousin",
                },
                home="The Fire Station",
                preferred_locations=["Fire Station", "Town", "School", "Community Center"],
            ),
            CharacterInfo(
                character_id="police-officer-beaver", name="Police Officer Beaver", role="adult", age_group="adult",
                personality=["friendly", "helpful", "responsible", "fair", "community-minded"],
                catchphrases=["Be-aver ready!", "Safety first!", "Here to help!"],
                favorite_things=["traffic safety", "crosswalks", "community events", "building dams", "badge"],
                relationships={
                    "firefighter-dalmatian": "coworker", "charlie-fox": "nephew",
                    "teacher-owl": "school safety partner", "mail-carrier-turtle": "friend",
                    "mommy-bunny": "neighbor",
                },
                home="The Police Station",
                preferred_locations=["Police Station", "Town Square", "Crosswalk", "School Zone"],
            ),
            CharacterInfo(
                character_id="mail-carrier-turtle", name="Mail Carrier Turtle", role="adult", age_group="adult",
                personality=["slow", "steady", "reliable", "friendly", "patient"],
                catchphrases=["Slow and steady!", "Special delivery!", "Mail's here!"],
                favorite_things=["packages", "letters", "stamps", "walking trails", "delivering smiles"],
                relationships={
                    "daisy-duck": "pen pal", "police-officer-beaver": "friend",
                    "librarian-hedgehog": "delivers books", "teacher-owl": "school mail",
                    "grandpa-bunny": "mail buddy", "grandma-bunny": "delivers knitting patterns",
                },
                home="The Post Office",
                preferred_locations=["Post Office", "Neighborhood", "Town", "Walking Trails"],
            ),
            CharacterInfo(
                character_id="librarian-hedgehog", name="Librarian Hedgehog", role="adult", age_group="adult",
                personality=["quiet", "organized", "friendly", "helpful", "wise"],
                catchphrases=["Quill-tastic book!", "Shh... let's read!", "Book adventure!"],
                favorite_things=["books", "quiet corners", "story time", "bookmarks", "tidy shelves"],
                relationships={
                    "teacher-owl": "close friend", "charlie-fox": "frequent visitor",
                    "lily-bunny": "story time friend", "musician-parrot": "book club member",
                    "mail-carrier-turtle": "receives book deliveries",
                },
                home="The Library",
                preferred_locations=["Library", "Reading Room", "Book Nook", "Story Corner"],
            ),
            CharacterInfo(
                character_id="musician-parrot", name="Musician Parrot", role="adult", age_group="adult",
                personality=["colorful", "musical", "energetic", "joyful", "expressive"],
                catchphrases=["Polly wants a song!", "Let's make music!", "Sing with me!"],
                favorite_things=["singing", "colorful feathers", "instruments", "applause", "dancing"],
                relationships={
                    "daisy-duck": "music teacher", "teacher-owl": "colleague",
                    "librarian-hedgehog": "book club member",
                    "lily-bunny": "sings together",
                },
                home="The Music Room",
                preferred_locations=["Music Room", "Stage", "Town Square", "Classroom"],
            ),
            CharacterInfo(
                character_id="mommy-bunny", name="Mommy Bunny", role="parent", age_group="adult",
                personality=["caring", "nurturing", "warm", "patient", "loving"],
                catchphrases=["Hop to it!", "My little bunny!", "Time for a hug!"],
                favorite_things=["gardening", "baking", "hugs", "family dinners", "flower arranging"],
                relationships={
                    "lily-bunny": "daughter", "baby-bunny": "daughter",
                    "daddy-bunny": "husband", "grandma-bunny": "mother-in-law",
                    "grandpa-bunny": "father-in-law", "doctor-panda": "friend",
                    "police-officer-beaver": "neighbor",
                },
                home="The Bunny Burrow",
                preferred_locations=["Home", "Garden", "Kitchen", "Market"],
            ),
            CharacterInfo(
                character_id="daddy-bunny", name="Daddy Bunny", role="parent", age_group="adult",
                personality=["playful", "protective", "loving", "strong", "funny"],
                catchphrases=["Daddy's home!", "Who wants a piggyback?", "Let's play!"],
                favorite_things=["woodworking", "storytelling", "tickling", "family walks", "fixing things"],
                relationships={
                    "lily-bunny": "daughter", "baby-bunny": "daughter",
                    "mommy-bunny": "wife", "grandma-bunny": "mother",
                    "grandpa-bunny": "father",
                },
                home="The Bunny Burrow",
                preferred_locations=["Home", "Workshop", "Garden", "Park"],
            ),
            CharacterInfo(
                character_id="grandma-bunny", name="Grandma Bunny", role="elderly", age_group="elderly",
                personality=["warm", "loving", "wise", "gentle", "patient"],
                catchphrases=["For my sweet bunny!", "Come give Grandma a hug!", "Grandma loves you!"],
                favorite_things=["knitting", "baking cookies", "rocking chair", "family photos", "tea"],
                relationships={
                    "lily-bunny": "granddaughter", "baby-bunny": "granddaughter",
                    "daddy-bunny": "son", "grandpa-bunny": "husband",
                    "mommy-bunny": "daughter-in-law", "teacher-owl": "old friend",
                    "chef-pig": "recipe exchange", "mail-carrier-turtle": "gets knitting patterns delivered",
                },
                home="The Bunny Burrow",
                preferred_locations=["Home", "Garden", "Kitchen", "Porch"],
            ),
            CharacterInfo(
                character_id="grandpa-bunny", name="Grandpa Bunny", role="elderly", age_group="elderly",
                personality=["gentle", "patient", "wise", "playful", "storyteller"],
                catchphrases=["Back in my day!", "Grandpa loves you!", "Let me tell you a story!"],
                favorite_things=["gardening", "fishing", "telling stories", "napping", "whittling"],
                relationships={
                    "lily-bunny": "granddaughter", "baby-bunny": "granddaughter",
                    "daddy-bunny": "son", "grandma-bunny": "wife",
                    "mommy-bunny": "daughter-in-law", "mail-carrier-turtle": "mail buddy",
                },
                home="The Bunny Burrow",
                preferred_locations=["Home", "Garden", "Porch", "Fishing Pond"],
            ),
            CharacterInfo(
                character_id="baby-bunny", name="Baby Bunny", role="student", age_group="baby",
                personality=["curious", "adorable", "learning", "happy", "cuddly"],
                catchphrases=["Goo goo!", "Ma ma!", "Da da!"],
                favorite_things=["rattles", "peek-a-boo", "soft blankets", "bath time", "teddy bear"],
                relationships={
                    "lily-bunny": "big sister", "mommy-bunny": "mother",
                    "daddy-bunny": "father", "grandma-bunny": "grandmother",
                    "grandpa-bunny": "grandfather",
                },
                home="The Bunny Burrow",
                preferred_locations=["Playroom", "Garden", "Living Room", "Kitchen"],
            ),
            CharacterInfo(
                character_id="dog", name="Dog", role="fantasy", age_group="animal",
                personality=["playful", "loyal", "energetic", "friendly", "excitable"],
                catchphrases=["Woof woof!", "Let's play!", "Bark bark!"],
                favorite_things=["bones", "fetching", "belly rubs", "running", "chasing balls"],
                relationships={
                    "lily-bunny": "neighbor's pet", "ben-bear": "friend",
                    "firefighter-dalmatian": "cousin", "cat": "neighbor",
                },
                home="The Dog House",
                preferred_locations=["Backyard", "Park", "Neighborhood", "Fire Station"],
            ),
            CharacterInfo(
                character_id="cat", name="Cat", role="fantasy", age_group="animal",
                personality=["curious", "independent", "graceful", "aloof", "affectionate"],
                catchphrases=["Meow!", "Purr...", "Mrrow!"],
                favorite_things=["milk", "sunny spots", "yarn balls", "napping", "bird watching"],
                relationships={
                    "lily-bunny": "neighbor's pet", "dog": "neighbor",
                    "mouse": "frenemy",
                },
                home="The Cat's Home",
                preferred_locations=["Rooftop", "Windowsill", "Garden", "Living Room"],
            ),
            CharacterInfo(
                character_id="pig", name="Pig", role="fantasy", age_group="animal",
                personality=["cheerful", "playful", "messy", "friendly", "hungry"],
                catchphrases=["Oink oink!", "Snort!", "Oink!"],
                favorite_things=["mud", "apples", "rolling", "eating", "truffles"],
                relationships={
                    "farmer-goat": "cared for", "cow": "farm friend",
                    "chicken": "farm friend", "horse": "farm friend",
                    "sheep": "farm friend",
                },
                home="The Farm",
                preferred_locations=["Barn", "Mud Puddle", "Pasture", "Trough"],
            ),
            CharacterInfo(
                character_id="cow", name="Cow", role="fantasy", age_group="animal",
                personality=["gentle", "calm", "patient", "kind", "motherly"],
                catchphrases=["Moo moo!", "Moo!"],
                favorite_things=["fresh grass", "chewing", "cud", "daisy fields", "mooing"],
                relationships={
                    "farmer-goat": "cared for", "pig": "farm friend",
                    "chicken": "farm friend", "horse": "farm friend",
                    "sheep": "farm friend",
                },
                home="The Farm",
                preferred_locations=["Barn", "Pasture", "Meadow", "Milking Parlor"],
            ),
            CharacterInfo(
                character_id="chicken", name="Chicken", role="fantasy", age_group="animal",
                personality=["busy", "clucky", "protective", "energetic", "social"],
                catchphrases=["Cluck cluck!", "Bawk bawk!", "Bock bock!"],
                favorite_things=["seeds", "scratching", "nesting", "dust baths", "worms"],
                relationships={
                    "farmer-goat": "cared for", "pig": "farm friend",
                    "cow": "farm friend", "horse": "farm friend",
                    "sheep": "farm friend",
                },
                home="The Farm",
                preferred_locations=["Coop", "Barnyard", "Garden", "Fence"],
            ),
            CharacterInfo(
                character_id="horse", name="Horse", role="fantasy", age_group="animal",
                personality=["strong", "fast", "gentle", "proud", "hardworking"],
                catchphrases=["Neigh!", "Let's ride!", "Clip clop!"],
                favorite_things=["apples", "running", "grooming", "jumping", "carrots"],
                relationships={
                    "farmer-goat": "works together", "pig": "farm friend",
                    "cow": "farm friend", "chicken": "farm friend",
                    "sheep": "farm friend",
                },
                home="The Farm",
                preferred_locations=["Stable", "Pasture", "Trail", "Horse Jump"],
            ),
            CharacterInfo(
                character_id="sheep", name="Sheep", role="fantasy", age_group="animal",
                personality=["fluffy", "calm", "gentle", "shy", "soft"],
                catchphrases=["Baa baa!", "Baa!"],
                favorite_things=["soft wool", "clover", "grazing", "napping", "fields"],
                relationships={
                    "farmer-goat": "cared for", "pig": "farm friend",
                    "cow": "farm friend", "chicken": "farm friend",
                    "horse": "farm friend",
                },
                home="The Farm",
                preferred_locations=["Pasture", "Barn", "Hill", "Meadow"],
            ),
            CharacterInfo(
                character_id="mouse", name="Mouse", role="fantasy", age_group="animal",
                personality=["tiny", "brave", "curious", "quick", "squeaky"],
                catchphrases=["Squeak!", "Eek!", "Squeak squeak!"],
                favorite_things=["cheese", "tiny houses", "exploring", "crumbs", "warm spots"],
                relationships={
                    "cat": "frenemy", "lily-bunny": "kitchen visitor",
                    "elephant": "unlikely friend",
                },
                home="Tiny Tree Stump",
                preferred_locations=["Garden", "Kitchen", "Playroom", "Pantry"],
            ),
            CharacterInfo(
                character_id="elephant", name="Elephant", role="fantasy", age_group="animal",
                personality=["big", "kind", "gentle", "helpful", "wise"],
                catchphrases=["Trumpet!", "Big hug!", "Elephant power!"],
                favorite_things=["peanuts", "bathing", "splashing", "big hugs", "remembering"],
                relationships={
                    "mouse": "unlikely friend", "monkey": "jungle buddy",
                    "lily-bunny": "friend",
                },
                home="The Jungle",
                preferred_locations=["Jungle", "Watering Hole", "Playground", "Bath Time"],
            ),
            CharacterInfo(
                character_id="monkey", name="Monkey", role="fantasy", age_group="animal",
                personality=["silly", "energetic", "curious", "funny", "playful"],
                catchphrases=["Ooh ooh ah ah!", "Banana time!", "Silly monkey!"],
                favorite_things=["bananas", "swinging", "silly faces", "climbing", "peek-a-boo"],
                relationships={
                    "elephant": "jungle buddy", "lily-bunny": "friend",
                    "ben-bear": "climbing buddy",
                },
                home="The Treehouse",
                preferred_locations=["Treehouse", "Jungle Gym", "Playground", "Banana Tree"],
            ),
            CharacterInfo(
                character_id="robot", name="Robot", role="fantasy", age_group="fantasy",
                personality=["logical", "helpful", "friendly", "curious", "precise"],
                catchphrases=["Beep boop!", "System ready!", "Calculating..."],
                favorite_things=["oiling", "programming", "counting", "fixing things", "wheels"],
                relationships={
                    "lily-bunny": "friend", "ben-bear": "building buddy",
                },
                home="The Workshop",
                preferred_locations=["Workshop", "Playroom", "Town", "Science Lab"],
            ),
            CharacterInfo(
                character_id="unicorn", name="Unicorn", role="fantasy", age_group="fantasy",
                personality=["magical", "sparkly", "kind", "graceful", "gentle"],
                catchphrases=["Sparkle on!", "Rainbow power!", "Magical!"],
                favorite_things=["sparkles", "rainbows", "flying", "friendship", "stardust"],
                relationships={
                    "lily-bunny": "friend", "friendly-dragon": "magical friend",
                },
                home="Rainbow Meadow",
                preferred_locations=["Rainbow Meadow", "Forest", "Castle", "Sky"],
            ),
            CharacterInfo(
                character_id="friendly-dragon", name="Friendly Dragon", role="fantasy", age_group="fantasy",
                personality=["friendly", "warm", "gentle", "playful", "misunderstood"],
                catchphrases=["Friendly fire!", "Warm hugs!", "Roar... softly!"],
                favorite_things=["warm fires", "flying", "marshmallows", "stories", "hot cocoa"],
                relationships={
                    "unicorn": "magical friend", "lily-bunny": "friend",
                    "ben-bear": "adventure buddy",
                },
                home="The Cozy Cave",
                preferred_locations=["Cave", "Mountain", "Sky", "Campfire"],
            ),
        ]

    def select_main_character(self, exclude=None):
        exclude = exclude or []
        candidates = [c for c in self._characters if c.role == "student" and c.character_id not in exclude]
        if not candidates:
            candidates = [c for c in self._characters if c.character_id not in exclude]
        if not candidates:
            return None
        return candidates[hash(tuple(exclude)) % len(candidates)] if exclude else candidates[0]

    def select_supporting(self, main_id, count=2, exclude=None):
        exclude = exclude or [main_id]
        main_char = self.get_character(main_id)
        related_ids = list(main_char.relationships.keys()) if main_char else []
        related_ids = [rid for rid in related_ids if rid not in exclude]
        related_chars = [self.get_character(rid) for rid in related_ids]
        related_chars = [c for c in related_chars if c is not None]
        return related_chars[:count]

    def get_character(self, char_id):
        for c in self._characters:
            if c.character_id == char_id:
                return c
        return None

    def list_by_role(self, role):
        return [c for c in self._characters if c.role == role]


class RelationshipEngine:
    def __init__(self, character_engine):
        self._char_engine = character_engine

    def get_relationship(self, char_a, char_b):
        char = self._char_engine.get_character(char_a)
        if char and char_b in char.relationships:
            return char.relationships[char_b]
        char = self._char_engine.get_character(char_b)
        if char and char_a in char.relationships:
            return char.relationships[char_a]
        return None

    def are_connected(self, char_a, char_b):
        return self.get_relationship(char_a, char_b) is not None

    def get_related(self, char_id, relationship_type=None):
        char = self._char_engine.get_character(char_id)
        if not char:
            return []
        if relationship_type:
            return [cid for cid, rtype in char.relationships.items() if rtype == relationship_type]
        return list(char.relationships.keys())
