from .models import TransitionType


TRANSITION_PROPERTIES: dict[TransitionType, dict] = {
    TransitionType.FADE: {
        "duration": 0.5,
        "description": "Image fades to black (or from black) smoothly",
        "best_for": "scene starts, scene ends, time passing",
    },
    TransitionType.CROSSFADE: {
        "duration": 0.8,
        "description": "First image fades out while second fades in simultaneously",
        "best_for": "continuous scenes, gentle passage of time, montage",
    },
    TransitionType.PAGE_TURN: {
        "duration": 1.2,
        "description": "Image curls from corner like turning a page in a book",
        "best_for": "storybook feel, book-end episodes, nursery rhyme transitions",
    },
    TransitionType.SLIDE: {
        "duration": 0.6,
        "description": "New image slides in from left or right, pushing old image out",
        "best_for": "location changes, following character movement direction",
    },
    TransitionType.WIPE: {
        "duration": 0.6,
        "description": "Line moves across screen revealing new image behind old one",
        "best_for": "clean breaks between scenes, time progression",
    },
    TransitionType.SOFT_ZOOM: {
        "duration": 0.8,
        "description": "Image gently zooms in or out while transitioning to next shot",
        "best_for": "emotional moments, emphasis on character reaction",
    },
    TransitionType.DISSOLVE: {
        "duration": 1.0,
        "description": "Image breaks into soft particles that dissolve into next image",
        "best_for": "dream sequences, magical transitions, fantasy elements",
    },
}


class TransitionEngine:
    def describe(self, transition: TransitionType) -> dict:
        return TRANSITION_PROPERTIES.get(
            transition,
            TRANSITION_PROPERTIES[TransitionType.FADE],
        )

    def list_transitions(self) -> list[TransitionType]:
        return list(TransitionType)

    def suggest_for_mood(self, mood: str) -> TransitionType:
        suggestions = {
            "happy": TransitionType.CROSSFADE,
            "excited": TransitionType.SOFT_ZOOM,
            "calm": TransitionType.FADE,
            "magical": TransitionType.DISSOLVE,
            "educational": TransitionType.SLIDE,
            "sad": TransitionType.FADE,
            "storybook": TransitionType.PAGE_TURN,
            "playful": TransitionType.SOFT_ZOOM,
        }
        return suggestions.get(mood, TransitionType.FADE)

    def estimate_duration(self, transition: TransitionType) -> float:
        return TRANSITION_PROPERTIES.get(transition, TRANSITION_PROPERTIES[TransitionType.FADE])["duration"]
