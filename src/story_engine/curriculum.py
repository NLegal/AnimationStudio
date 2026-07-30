from typing import List, Optional
from src.story_engine.models import CurriculumArea


class CurriculumEngine:
    def __init__(self):
        self._usage_order: List[str] = []
        self._areas: List[CurriculumArea] = [
            CurriculumArea(
                id="alphabet", name="Alphabet",
                description="Learning letters and their sounds",
                age_range="2-5",
                topics=["Letter Recognition", "Phonics", "Uppercase & Lowercase", "ABC Order", "Letter Sounds"],
            ),
            CurriculumArea(
                id="numbers", name="Numbers",
                description="Counting and number concepts",
                age_range="2-5",
                topics=["Counting 1 to 5", "Counting 1 to 10", "Number Recognition", "Simple Addition", "Simple Subtraction"],
            ),
            CurriculumArea(
                id="shapes", name="Shapes",
                description="Identifying and naming shapes",
                age_range="2-5",
                topics=["Circle & Square", "Triangle & Rectangle", "Star & Diamond", "Oval & Heart", "Sorting Shapes"],
            ),
            CurriculumArea(
                id="colors", name="Colors",
                description="Recognizing and naming colors",
                age_range="2-5",
                topics=["Red & Blue", "Yellow & Green", "Orange & Purple", "Pink & Brown", "Mixing Colors"],
            ),
            CurriculumArea(
                id="animals", name="Animals",
                description="Learning about animals and their characteristics",
                age_range="2-5",
                topics=["Farm Animals", "Wild Animals", "Pet Animals", "Animal Sounds", "Animal Homes"],
            ),
            CurriculumArea(
                id="science", name="Science",
                description="Early science concepts and discovery",
                age_range="3-5",
                topics=["Five Senses", "Sink & Float", "Magnets", "Plant Growth", "Simple Weather"],
            ),
            CurriculumArea(
                id="space", name="Space",
                description="Exploring space and the solar system",
                age_range="3-5",
                topics=["The Sun", "The Moon", "Stars & Night Sky", "Planets", "Rockets & Space Travel"],
            ),
            CurriculumArea(
                id="ocean", name="Ocean",
                description="Discovering ocean life and environments",
                age_range="2-5",
                topics=["Fish & Whales", "Dolphins & Octopus", "Seashells & Sand", "Underwater Colors", "Ocean Life"],
            ),
            CurriculumArea(
                id="farm", name="Farm",
                description="Life on the farm and where food comes from",
                age_range="2-5",
                topics=["Barn Animals", "Crops & Garden", "Farm Tools", "The Tractor", "Food from the Farm"],
            ),
            CurriculumArea(
                id="healthy-habits", name="Healthy Habits",
                description="Building healthy daily routines",
                age_range="2-5",
                topics=["Brushing Teeth", "Washing Hands", "Eating Vegetables", "Exercise & Movement", "Bedtime Routine"],
            ),
            CurriculumArea(
                id="friendship", name="Friendship",
                description="Social skills and building friendships",
                age_range="2-5",
                topics=["Sharing", "Helping Friends", "Being Kind", "Teamwork", "Making New Friends"],
            ),
            CurriculumArea(
                id="emotions", name="Emotions",
                description="Understanding and expressing feelings",
                age_range="2-5",
                topics=["Happy & Sad", "Angry & Calm", "Scared & Brave", "Love & Care", "Naming Feelings"],
            ),
            CurriculumArea(
                id="problem-solving", name="Problem Solving",
                description="Developing problem-solving skills",
                age_range="3-5",
                topics=["Simple Puzzles", "Finding Solutions", "Asking for Help", "Trying Again", "Creative Thinking"],
            ),
            CurriculumArea(
                id="motor-skills", name="Motor Skills",
                description="Developing fine and gross motor skills",
                age_range="2-5",
                topics=["Hopping & Jumping", "Clapping & Stomping", "Drawing & Coloring", "Tying & Fastening", "Balancing"],
            ),
            CurriculumArea(
                id="music", name="Music",
                description="Exploring music and rhythm",
                age_range="2-5",
                topics=["Musical Instruments", "Rhythm & Beat", "Singing Together", "Loud & Soft", "Making Music"],
            ),
            CurriculumArea(
                id="dance", name="Dance",
                description="Movement and dance skills",
                age_range="2-5",
                topics=["Moving Together", "Follow the Leader", "Freeze Dance", "Animal Moves", "Dance Party"],
            ),
            CurriculumArea(
                id="language", name="Language",
                description="Building vocabulary and language skills",
                age_range="2-5",
                topics=["New Words", "Simple Sentences", "Opposites", "Rhyming Words", "Storytelling"],
            ),
            CurriculumArea(
                id="seasons", name="Seasons",
                description="Learning about the four seasons",
                age_range="2-5",
                topics=["Spring Flowers", "Summer Fun", "Fall Leaves", "Winter Snow", "Seasonal Changes"],
            ),
            CurriculumArea(
                id="weather", name="Weather",
                description="Understanding weather and atmospheric phenomena",
                age_range="2-5",
                topics=["Sunny Days", "Rainy Days", "Snowy Days", "Windy Days", "Stormy Weather"],
            ),
            CurriculumArea(
                id="community-helpers", name="Community Helpers",
                description="Learning about people who help in our community",
                age_range="2-5",
                topics=["Doctor", "Firefighter", "Police Officer", "Teacher", "Mail Carrier"],
            ),
            CurriculumArea(
                id="transportation", name="Transportation",
                description="Exploring different ways to travel",
                age_range="2-5",
                topics=["Cars & Trucks", "Trains", "Planes & Helicopters", "Boats & Ships", "Bicycles"],
            ),
            CurriculumArea(
                id="geography", name="Geography",
                description="Understanding places and spatial concepts",
                age_range="3-5",
                topics=["My Home", "My Neighborhood", "Maps & Directions", "Near & Far", "Places in Town"],
            ),
        ]

    def select_area(self, exclude: List[str] = None) -> Optional[CurriculumArea]:
        exclude = exclude or []
        candidates = [a for a in self._areas if a.id not in exclude]
        if not candidates:
            return None
        candidates.sort(key=lambda a: self._usage_order.index(a.id) if a.id in self._usage_order else -1)
        selected = candidates[0]
        if selected.id in self._usage_order:
            self._usage_order.remove(selected.id)
        self._usage_order.append(selected.id)
        return selected

    def list_areas(self) -> List[CurriculumArea]:
        return list(self._areas)

    def get_area(self, area_id: str) -> Optional[CurriculumArea]:
        for a in self._areas:
            if a.id == area_id:
                return a
        return None
