from typing import List, Optional
from src.story_engine.models import LearningObjective


class LearningObjectiveEngine:
    def __init__(self):
        self._objectives: List[LearningObjective] = [
            # Alphabet
            LearningObjective(
                id="letter-a", curriculum_area="alphabet", name="Letter A",
                description="Recognize and say the letter A",
                difficulty=1, age_range="2-3",
                keywords=["letter A", "apple", "alligator", "alphabet"],
            ),
            LearningObjective(
                id="letter-b", curriculum_area="alphabet", name="Letter B",
                description="Recognize and say the letter B",
                difficulty=1, age_range="2-3",
                keywords=["letter B", "ball", "bear", "alphabet"],
            ),
            LearningObjective(
                id="abc-song", curriculum_area="alphabet", name="ABC Song",
                description="Sing the alphabet song from A to Z",
                difficulty=2, age_range="2-4",
                keywords=["ABC", "alphabet", "song", "letters"],
                prerequisites=["letter-a", "letter-b"],
            ),
            LearningObjective(
                id="letter-sounds", curriculum_area="alphabet", name="Letter Sounds",
                description="Learn the phonetic sounds of letters",
                difficulty=3, age_range="3-5",
                keywords=["phonics", "sounds", "letters", "reading"],
                prerequisites=["abc-song"],
            ),

            # Numbers
            LearningObjective(
                id="count-to-5", curriculum_area="numbers", name="Count to 5",
                description="Count objects from 1 to 5 using one-to-one correspondence",
                difficulty=1, age_range="2-3",
                keywords=["count", "one", "two", "three", "four", "five"],
            ),
            LearningObjective(
                id="count-to-10", curriculum_area="numbers", name="Count to 10",
                description="Count objects from 1 to 10 with confidence",
                difficulty=2, age_range="3-4",
                keywords=["count", "numbers", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"],
                prerequisites=["count-to-5"],
            ),
            LearningObjective(
                id="recognize-number-1", curriculum_area="numbers", name="Recognize Number 1",
                description="Identify the numeral 1 in print",
                difficulty=1, age_range="2-3",
                keywords=["number 1", "one", "numeral"],
            ),
            LearningObjective(
                id="recognize-number-5", curriculum_area="numbers", name="Recognize Number 5",
                description="Identify the numeral 5 in print",
                difficulty=2, age_range="3-4",
                keywords=["number 5", "five", "numeral"],
                prerequisites=["count-to-5"],
            ),
            LearningObjective(
                id="simple-addition", curriculum_area="numbers", name="Simple Addition",
                description="Add small quantities up to 5",
                difficulty=3, age_range="4-5",
                keywords=["add", "plus", "altogether", "total"],
                prerequisites=["count-to-10"],
            ),

            # Colors
            LearningObjective(
                id="recognize-red", curriculum_area="colors", name="Recognize Red",
                description="Identify the color red in everyday objects",
                difficulty=1, age_range="2-3",
                keywords=["red", "apple", "color"],
            ),
            LearningObjective(
                id="recognize-blue", curriculum_area="colors", name="Recognize Blue",
                description="Identify the color blue in everyday objects",
                difficulty=1, age_range="2-3",
                keywords=["blue", "sky", "color"],
            ),
            LearningObjective(
                id="recognize-yellow", curriculum_area="colors", name="Recognize Yellow",
                description="Identify the color yellow in everyday objects",
                difficulty=1, age_range="2-3",
                keywords=["yellow", "sun", "color"],
            ),
            LearningObjective(
                id="recognize-green", curriculum_area="colors", name="Recognize Green",
                description="Identify the color green in everyday objects",
                difficulty=2, age_range="2-3",
                keywords=["green", "grass", "color"],
            ),
            LearningObjective(
                id="color-mixing", curriculum_area="colors", name="Color Mixing Basics",
                description="Learn that mixing two colors creates a new color",
                difficulty=3, age_range="3-5",
                keywords=["mix", "colors", "blue and yellow", "green"],
                prerequisites=["recognize-blue", "recognize-yellow"],
            ),

            # Shapes
            LearningObjective(
                id="identify-circle", curriculum_area="shapes", name="Identify Circle",
                description="Recognize and name a circle shape",
                difficulty=1, age_range="2-3",
                keywords=["circle", "round", "shape"],
            ),
            LearningObjective(
                id="identify-square", curriculum_area="shapes", name="Identify Square",
                description="Recognize and name a square shape",
                difficulty=1, age_range="2-3",
                keywords=["square", "four sides", "shape"],
            ),
            LearningObjective(
                id="identify-triangle", curriculum_area="shapes", name="Identify Triangle",
                description="Recognize and name a triangle shape",
                difficulty=2, age_range="3-4",
                keywords=["triangle", "three sides", "shape"],
            ),
            LearningObjective(
                id="identify-star", curriculum_area="shapes", name="Identify Star",
                description="Recognize and name a star shape",
                difficulty=2, age_range="2-4",
                keywords=["star", "points", "shape"],
            ),
            LearningObjective(
                id="sort-shapes", curriculum_area="shapes", name="Sort Shapes",
                description="Sort objects by shape into matching groups",
                difficulty=2, age_range="3-4",
                keywords=["sort", "shapes", "match", "group"],
                prerequisites=["identify-circle", "identify-square"],
            ),

            # Animals
            LearningObjective(
                id="name-farm-animals", curriculum_area="animals", name="Name Farm Animals",
                description="Name common farm animals like cow, pig, horse, sheep",
                difficulty=1, age_range="2-3",
                keywords=["farm", "cow", "pig", "horse", "sheep", "chicken"],
            ),
            LearningObjective(
                id="duck-sounds", curriculum_area="animals", name="Duck Sounds",
                description="Learn that ducks say quack quack",
                difficulty=1, age_range="2-3",
                keywords=["duck", "quack", "sound", "animal noise"],
            ),
            LearningObjective(
                id="cow-sounds", curriculum_area="animals", name="Cow Sounds",
                description="Learn that cows say moo moo",
                difficulty=1, age_range="2-3",
                keywords=["cow", "moo", "sound", "animal noise"],
            ),
            LearningObjective(
                id="animal-habitats", curriculum_area="animals", name="Animal Habitats",
                description="Learn where different animals live",
                difficulty=3, age_range="3-5",
                keywords=["habitat", "home", "farm", "forest", "ocean", "desert"],
                prerequisites=["name-farm-animals"],
            ),

            # Science
            LearningObjective(
                id="five-senses", curriculum_area="science", name="Five Senses",
                description="Learn about the five senses: sight, hearing, touch, taste, smell",
                difficulty=2, age_range="3-4",
                keywords=["senses", "see", "hear", "touch", "taste", "smell"],
            ),
            LearningObjective(
                id="plant-growth", curriculum_area="science", name="Plant Growth",
                description="Learn that plants need sun, water, and soil to grow",
                difficulty=3, age_range="3-5",
                keywords=["plant", "grow", "seed", "sun", "water", "soil"],
            ),
            LearningObjective(
                id="sink-float", curriculum_area="science", name="Sink or Float",
                description="Discover which objects sink and which float in water",
                difficulty=2, age_range="3-4",
                keywords=["sink", "float", "water", "experiment"],
            ),

            # Space
            LearningObjective(
                id="sun-moon-stars", curriculum_area="space", name="Sun Moon and Stars",
                description="Learn that the sun shines during the day and the moon and stars at night",
                difficulty=2, age_range="3-4",
                keywords=["sun", "moon", "stars", "day", "night", "sky"],
            ),

            # Ocean
            LearningObjective(
                id="ocean-animals", curriculum_area="ocean", name="Ocean Animals",
                description="Name common ocean animals like fish, whale, dolphin, octopus",
                difficulty=1, age_range="2-3",
                keywords=["ocean", "fish", "whale", "dolphin", "octopus", "sea"],
            ),

            # Farm
            LearningObjective(
                id="farm-life", curriculum_area="farm", name="Life on the Farm",
                description="Learn about daily life and activities on a farm",
                difficulty=2, age_range="2-4",
                keywords=["farm", "barn", "tractor", "crops", "animals"],
            ),

            # Healthy Habits
            LearningObjective(
                id="brush-teeth", curriculum_area="healthy-habits", name="Brush Teeth",
                description="Learn the importance of brushing teeth twice a day",
                difficulty=1, age_range="2-4",
                keywords=["brush", "teeth", "clean", "toothbrush", "toothpaste"],
            ),
            LearningObjective(
                id="wash-hands", curriculum_area="healthy-habits", name="Wash Hands",
                description="Learn proper hand washing technique",
                difficulty=1, age_range="2-3",
                keywords=["wash", "hands", "soap", "water", "clean"],
            ),
            LearningObjective(
                id="eat-vegetables", curriculum_area="healthy-habits", name="Eat Vegetables",
                description="Learn that vegetables help us grow strong",
                difficulty=2, age_range="2-4",
                keywords=["vegetables", "carrots", "broccoli", "healthy", "strong"],
            ),
            LearningObjective(
                id="exercise-routine", curriculum_area="healthy-habits", name="Exercise Routine",
                description="Learn that daily exercise keeps our bodies healthy",
                difficulty=2, age_range="3-5",
                keywords=["exercise", "running", "jumping", "healthy", "strong"],
            ),

            # Friendship
            LearningObjective(
                id="share-toys", curriculum_area="friendship", name="Share Toys",
                description="Learn to share toys with friends",
                difficulty=1, age_range="2-4",
                keywords=["share", "toy", "friend", "take turns"],
            ),
            LearningObjective(
                id="help-friend", curriculum_area="friendship", name="Help a Friend",
                description="Learn to help a friend in need",
                difficulty=2, age_range="2-4",
                keywords=["help", "friend", "kind", "assist"],
            ),
            LearningObjective(
                id="say-thank-you", curriculum_area="friendship", name="Say Thank You",
                description="Learn to express gratitude with thank you",
                difficulty=1, age_range="2-3",
                keywords=["thank you", "thanks", "manners", "polite"],
            ),
            LearningObjective(
                id="teamwork", curriculum_area="friendship", name="Teamwork",
                description="Work together with others to achieve a goal",
                difficulty=2, age_range="3-5",
                keywords=["team", "together", "cooperate", "work together"],
            ),

            # Emotions
            LearningObjective(
                id="name-emotions", curriculum_area="emotions", name="Name Emotions",
                description="Identify and name basic emotions like happy, sad, angry",
                difficulty=1, age_range="2-3",
                keywords=["happy", "sad", "angry", "feelings", "emotions"],
            ),
            LearningObjective(
                id="happy-vs-sad", curriculum_area="emotions", name="Happy vs Sad",
                description="Differentiate between happy and sad facial expressions",
                difficulty=1, age_range="2-3",
                keywords=["happy", "sad", "face", "expression"],
            ),
            LearningObjective(
                id="calm-down", curriculum_area="emotions", name="Calm Down Strategies",
                description="Learn simple techniques to calm down when upset",
                difficulty=3, age_range="3-5",
                keywords=["calm", "breathe", "relax", "feelings"],
                prerequisites=["name-emotions"],
            ),

            # Problem Solving
            LearningObjective(
                id="find-solution", curriculum_area="problem-solving", name="Find a Solution",
                description="Identify a simple solution to a problem",
                difficulty=2, age_range="3-4",
                keywords=["problem", "solution", "think", "solve"],
            ),
            LearningObjective(
                id="ask-for-help", curriculum_area="problem-solving", name="Ask for Help",
                description="Learn to ask for help when needed",
                difficulty=1, age_range="2-4",
                keywords=["help", "ask", "problem"],
            ),

            # Motor Skills
            LearningObjective(
                id="tie-shoes", curriculum_area="motor-skills", name="Tie Shoes",
                description="Learn to tie shoelaces independently",
                difficulty=3, age_range="4-5",
                keywords=["tie", "shoes", "laces", "knot", "bunny ears"],
            ),
            LearningObjective(
                id="hop-on-one-foot", curriculum_area="motor-skills", name="Hop on One Foot",
                description="Practice hopping on one foot",
                difficulty=2, age_range="3-4",
                keywords=["hop", "balance", "foot", "jump"],
            ),
            LearningObjective(
                id="clap-hands", curriculum_area="motor-skills", name="Clap Hands",
                description="Learn to clap hands together rhythmically",
                difficulty=1, age_range="2-3",
                keywords=["clap", "hands", "rhythm"],
            ),

            # Music
            LearningObjective(
                id="rhythm-clap", curriculum_area="music", name="Clap to Rhythm",
                description="Clap hands following a simple rhythm",
                difficulty=1, age_range="2-3",
                keywords=["rhythm", "clap", "beat", "music"],
            ),
            LearningObjective(
                id="instrument-names", curriculum_area="music", name="Name Instruments",
                description="Identify common musical instruments by name and sound",
                difficulty=2, age_range="3-4",
                keywords=["drum", "guitar", "piano", "instrument", "music"],
            ),

            # Dance
            LearningObjective(
                id="follow-dance", curriculum_area="dance", name="Follow Dance Moves",
                description="Imitate simple dance movements",
                difficulty=1, age_range="2-3",
                keywords=["dance", "move", "follow", "imitate"],
            ),

            # Language
            LearningObjective(
                id="rhyming-words", curriculum_area="language", name="Rhyming Words",
                description="Recognize and generate simple rhyming words",
                difficulty=2, age_range="3-4",
                keywords=["rhyme", "words", "cat", "hat", "sound alike"],
            ),
            LearningObjective(
                id="opposites", curriculum_area="language", name="Opposites",
                description="Understand basic opposite concepts like big/small and hot/cold",
                difficulty=2, age_range="3-4",
                keywords=["opposite", "big", "small", "hot", "cold", "fast", "slow"],
            ),
            LearningObjective(
                id="simple-sentences", curriculum_area="language", name="Simple Sentences",
                description="Form three-word simple sentences",
                difficulty=2, age_range="3-4",
                keywords=["sentence", "words", "speak", "grammar"],
            ),

            # Seasons
            LearningObjective(
                id="spring-flowers", curriculum_area="seasons", name="Spring Flowers",
                description="Learn about flowers that bloom in spring",
                difficulty=1, age_range="2-3",
                keywords=["spring", "flowers", "bloom", "garden"],
            ),
            LearningObjective(
                id="winter-clothes", curriculum_area="seasons", name="Winter Clothes",
                description="Learn what clothes to wear in winter",
                difficulty=1, age_range="2-3",
                keywords=["winter", "coat", "hat", "scarf", "mittens", "cold"],
            ),

            # Weather
            LearningObjective(
                id="sunny-weather", curriculum_area="weather", name="Sunny Weather",
                description="Identify sunny weather and sun safety",
                difficulty=1, age_range="2-3",
                keywords=["sun", "sunny", "weather", "sunglasses", "sun hat"],
            ),
            LearningObjective(
                id="rainy-day-activities", curriculum_area="weather", name="Rainy Day Activities",
                description="Learn fun indoor activities for rainy days",
                difficulty=1, age_range="2-4",
                keywords=["rain", "rainy", "indoor", "activities"],
            ),

            # Community Helpers
            LearningObjective(
                id="doctor-helps", curriculum_area="community-helpers", name="Doctor Helps",
                description="Learn that doctors help keep us healthy",
                difficulty=1, age_range="2-3",
                keywords=["doctor", "hospital", "healthy", "checkup"],
            ),
            LearningObjective(
                id="firefighter-role", curriculum_area="community-helpers", name="Firefighter Role",
                description="Learn that firefighters help put out fires and rescue people",
                difficulty=1, age_range="2-3",
                keywords=["firefighter", "fire truck", "rescue", "help"],
            ),

            # Transportation
            LearningObjective(
                id="vehicle-sounds", curriculum_area="transportation", name="Vehicle Sounds",
                description="Learn the sounds different vehicles make",
                difficulty=1, age_range="2-3",
                keywords=["car", "vroom", "train", "choo", "plane", "vehicle sounds"],
            ),
            LearningObjective(
                id="transportation-types", curriculum_area="transportation", name="Types of Transportation",
                description="Identify different modes of transportation",
                difficulty=2, age_range="3-4",
                keywords=["car", "train", "plane", "boat", "bicycle", "transportation"],
            ),

            # Geography
            LearningObjective(
                id="my-home", curriculum_area="geography", name="My Home",
                description="Describe different rooms and features of a home",
                difficulty=1, age_range="2-3",
                keywords=["home", "house", "kitchen", "bedroom", "living room"],
            ),
            LearningObjective(
                id="neighborhood-places", curriculum_area="geography", name="Neighborhood Places",
                description="Identify common places in a neighborhood",
                difficulty=2, age_range="3-4",
                keywords=["neighborhood", "park", "store", "school", "library"],
            ),
        ]

    def select_objective(self, area_id: str, difficulty: int = 1, exclude: List[str] = None) -> Optional[LearningObjective]:
        exclude = exclude or []
        candidates = [o for o in self._objectives if o.curriculum_area == area_id and o.id not in exclude]
        if not candidates:
            return None
        candidates.sort(key=lambda o: abs(o.difficulty - difficulty))
        return candidates[0]

    def get_objectives_for_area(self, area_id: str) -> List[LearningObjective]:
        return [o for o in self._objectives if o.curriculum_area == area_id]

    def get_objective(self, objective_id: str) -> Optional[LearningObjective]:
        for o in self._objectives:
            if o.id == objective_id:
                return o
        return None
