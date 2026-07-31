from .models import TransitionStyle


TRANSITION_PROPERTIES: dict[TransitionStyle, dict] = {
    TransitionStyle.FADE: {
        "duration": 0.5,
        "description": "Gradual fade to or from black",
        "best_for": "scene starts, scene ends, time passing",
    },
    TransitionStyle.CROSSFADE: {
        "duration": 0.8,
        "description": "First clip fades out while second fades in simultaneously",
        "best_for": "continuous scenes, gentle passage of time",
    },
    TransitionStyle.SLIDE: {
        "duration": 0.6,
        "description": "New clip slides in pushing old clip out",
        "best_for": "location changes, following character movement",
    },
    TransitionStyle.ZOOM: {
        "duration": 0.8,
        "description": "Clip gently zooms in or out during transition",
        "best_for": "emotional emphasis, character reactions",
    },
    TransitionStyle.PAGE_TURN: {
        "duration": 1.2,
        "description": "Clip curls from corner like turning a page",
        "best_for": "storybook feel, nursery rhyme transitions",
    },
    TransitionStyle.SOFT_WIPE: {
        "duration": 0.6,
        "description": "Soft edge moves across screen revealing new clip",
        "best_for": "clean breaks between scenes",
    },
    TransitionStyle.DISSOLVE: {
        "duration": 1.0,
        "description": "Clip breaks into soft particles revealing next clip",
        "best_for": "dream sequences, magical transitions",
    },
    TransitionStyle.QUICK_CUT: {
        "duration": 0.1,
        "description": "Instant cut between clips with no transition effect",
        "best_for": "fast-paced sequences, dialogue back-and-forth",
    },
    TransitionStyle.NONE: {
        "duration": 0.0,
        "description": "No transition — direct cut",
        "best_for": "default, when no effect is desired",
    },
}


class TransitionLibrary:
    def describe(self, style: TransitionStyle) -> dict:
        return TRANSITION_PROPERTIES.get(
            style,
            TRANSITION_PROPERTIES[TransitionStyle.FADE],
        )

    def list_styles(self) -> list[TransitionStyle]:
        return list(TransitionStyle)

    def suggest_for_mood(self, mood: str) -> TransitionStyle:
        suggestions = {
            "happy": TransitionStyle.CROSSFADE,
            "excited": TransitionStyle.ZOOM,
            "calm": TransitionStyle.FADE,
            "magical": TransitionStyle.DISSOLVE,
            "educational": TransitionStyle.SLIDE,
            "storybook": TransitionStyle.PAGE_TURN,
            "playful": TransitionStyle.ZOOM,
            "fast": TransitionStyle.QUICK_CUT,
        }
        return suggestions.get(mood, TransitionStyle.FADE)

    def estimate_duration(self, style: TransitionStyle) -> float:
        return TRANSITION_PROPERTIES.get(style, TRANSITION_PROPERTIES[TransitionStyle.FADE])["duration"]
