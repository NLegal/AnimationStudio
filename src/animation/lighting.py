from .models import LightingCondition


LIGHTING_PROPERTIES: dict[LightingCondition, dict] = {
    LightingCondition.SUNRISE: {
        "color_temperature": "warm_orange_3000K",
        "brightness": 0.4,
        "shadow_softness": 0.7,
        "description": "Soft warm light from low horizon, long soft shadows, pink-orange hues",
        "direction": "low_angle_left",
    },
    LightingCondition.MORNING: {
        "color_temperature": "warm_4500K",
        "brightness": 0.6,
        "shadow_softness": 0.5,
        "description": "Clear warm daylight with gentle shadows and natural color",
        "direction": "medium_angle_right",
    },
    LightingCondition.NOON: {
        "color_temperature": "neutral_5500K",
        "brightness": 0.9,
        "shadow_softness": 0.3,
        "description": "Bright overhead light with short dark shadows, high contrast",
        "direction": "top_down",
    },
    LightingCondition.GOLDEN_HOUR: {
        "color_temperature": "warm_3500K",
        "brightness": 0.7,
        "shadow_softness": 0.6,
        "description": "Rich warm golden light, long soft shadows, warm glow on subjects",
        "direction": "low_angle_right",
    },
    LightingCondition.SUNSET: {
        "color_temperature": "warm_2800K",
        "brightness": 0.3,
        "shadow_softness": 0.8,
        "description": "Deep warm orange-red light, very long shadows, fading brightness",
        "direction": "low_angle_left",
    },
    LightingCondition.NIGHT: {
        "color_temperature": "cool_7000K",
        "brightness": 0.15,
        "shadow_softness": 0.9,
        "description": "Dark blue light with moonlight, deep shadows, scattered fill",
        "direction": "high_angle_moon",
    },
    LightingCondition.CLOUDS: {
        "color_temperature": "neutral_6000K",
        "brightness": 0.4,
        "shadow_softness": 0.9,
        "description": "Diffuse even light with very soft shadows, muted colors",
        "direction": "diffuse",
    },
    LightingCondition.RAIN: {
        "color_temperature": "cool_6200K",
        "brightness": 0.3,
        "shadow_softness": 0.8,
        "description": "Cool grey light with minimal shadows, wet reflective surfaces",
        "direction": "diffuse_overcast",
    },
    LightingCondition.SNOW: {
        "color_temperature": "cool_6500K",
        "brightness": 0.5,
        "shadow_softness": 0.6,
        "description": "Bright cool light reflected off snow, soft blue shadows",
        "direction": "diffuse_bright",
    },
    LightingCondition.INDOOR: {
        "color_temperature": "warm_3200K",
        "brightness": 0.5,
        "shadow_softness": 0.6,
        "description": "Warm artificial light with soft room-filling illumination",
        "direction": "ceiling_warm",
    },
    LightingCondition.HOLIDAY: {
        "color_temperature": "mixed_warm_cool",
        "brightness": 0.3,
        "shadow_softness": 0.7,
        "description": "Multi-colored festive lights with warm ambient fill, sparkle highlights",
        "direction": "multiple_colored",
    },
}


class LightingAnimationEngine:
    def describe(self, condition: LightingCondition) -> dict:
        return LIGHTING_PROPERTIES.get(
            condition,
            LIGHTING_PROPERTIES[LightingCondition.MORNING],
        )

    def list_conditions(self) -> list[LightingCondition]:
        return list(LightingCondition)

    def transition_time(self, from_cond: LightingCondition, to_cond: LightingCondition) -> float:
        if from_cond == to_cond:
            return 0.0
        rapid = {
            (LightingCondition.MORNING, LightingCondition.NOON),
            (LightingCondition.NOON, LightingCondition.SUNSET),
            (LightingCondition.SUNSET, LightingCondition.NIGHT),
            (LightingCondition.SUNRISE, LightingCondition.MORNING),
        }
        if (from_cond, to_cond) in rapid or (to_cond, from_cond) in rapid:
            return 1.0
        return 2.5
