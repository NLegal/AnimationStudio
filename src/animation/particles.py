from .models import ParticleEffect


PARTICLE_PROPERTIES: dict[ParticleEffect, dict] = {
    ParticleEffect.BUBBLES: {
        "count": 15,
        "speed": 0.3,
        "size": "small_to_medium",
        "color": "translucent_rainbow",
        "motion": "float_upward",
        "lifespan": 4.0,
        "description": "Gentle floating bubbles that drift upward and pop",
    },
    ParticleEffect.LEAVES: {
        "count": 8,
        "speed": 0.4,
        "size": "small",
        "color": "autumn_greens_yellows",
        "motion": "sway_fall",
        "lifespan": 5.0,
        "description": "Leaves drifting down with gentle side-to-side sway",
    },
    ParticleEffect.SNOW: {
        "count": 40,
        "speed": 0.2,
        "size": "tiny",
        "color": "white",
        "motion": "gentle_fall",
        "lifespan": 6.0,
        "description": "Soft snowflakes falling gently with slight horizontal drift",
    },
    ParticleEffect.RAIN: {
        "count": 60,
        "speed": 0.8,
        "size": "tiny",
        "color": "light_blue_translucent",
        "motion": "fast_fall",
        "lifespan": 2.0,
        "description": "Fine rain streaks falling straight with slight angle variation",
    },
    ParticleEffect.CONFETTI: {
        "count": 30,
        "speed": 0.5,
        "size": "small",
        "color": "multi_color",
        "motion": "burst_scatter",
        "lifespan": 3.0,
        "description": "Colorful paper pieces bursting outward and fluttering down",
    },
    ParticleEffect.SPARKLES: {
        "count": 12,
        "speed": 0.1,
        "size": "tiny",
        "color": "gold_white",
        "motion": "twinkle_fade",
        "lifespan": 2.0,
        "description": "Tiny sparkling points that appear and fade with gentle twinkle",
    },
    ParticleEffect.DUST: {
        "count": 10,
        "speed": 0.05,
        "size": "microscopic",
        "color": "warm_white_translucent",
        "motion": "suspended_drift",
        "lifespan": 8.0,
        "description": "Fine dust particles suspended in light, barely moving",
    },
    ParticleEffect.MAGIC: {
        "count": 20,
        "speed": 0.3,
        "size": "small",
        "color": "glowing_pastel",
        "motion": "swirl_upward",
        "lifespan": 3.5,
        "description": "Glowing magical particles swirling upward with sparkle trail",
    },
    ParticleEffect.BUTTERFLIES: {
        "count": 5,
        "speed": 0.3,
        "size": "small",
        "color": "bright_patterned",
        "motion": "flutter_random",
        "lifespan": 6.0,
        "description": "Small butterflies fluttering in random gentle paths",
    },
    ParticleEffect.FIREFLIES: {
        "count": 8,
        "speed": 0.15,
        "size": "tiny",
        "color": "glowing_yellow_green",
        "motion": "blink_drift",
        "lifespan": 5.0,
        "description": "Tiny glowing lights that pulse and drift slowly in darkness",
    },
}


class ParticleEngine:
    def describe(self, effect: ParticleEffect) -> dict:
        return PARTICLE_PROPERTIES.get(
            effect,
            PARTICLE_PROPERTIES[ParticleEffect.SPARKLES],
        )

    def list_effects(self) -> list[ParticleEffect]:
        return list(ParticleEffect)

    def suggest_for_mood(self, mood: str) -> list[ParticleEffect]:
        suggestions = {
            "magical": [ParticleEffect.SPARKLES, ParticleEffect.MAGIC, ParticleEffect.FIREFLIES],
            "celebratory": [ParticleEffect.CONFETTI, ParticleEffect.BUBBLES, ParticleEffect.SPARKLES],
            "calm": [ParticleEffect.SNOW, ParticleEffect.DUST, ParticleEffect.FIREFLIES],
            "playful": [ParticleEffect.BUBBLES, ParticleEffect.BUTTERFLIES, ParticleEffect.CONFETTI],
            "nature": [ParticleEffect.LEAVES, ParticleEffect.BUTTERFLIES, ParticleEffect.SNOW],
            "sad": [ParticleEffect.DUST, ParticleEffect.RAIN],
        }
        return suggestions.get(mood, [ParticleEffect.SPARKLES])
