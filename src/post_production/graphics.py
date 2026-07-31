from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GraphicOverlay:
    overlay_id: str = ""
    type: str = ""  # title, learning_goal, label, lower_third, celebration, reward
    text: str = ""
    start_time: float = 0.0
    end_time: float = 0.0
    position: str = "center"  # center, top, bottom, lower_third
    style: str = "default"
    metadata: dict = field(default_factory=dict)


GRAPHIC_TEMPLATES: dict[str, dict] = {
    "episode_title": {
        "type": "title",
        "position": "center",
        "style": "large_playful",
        "duration": 4.0,
    },
    "learning_goal": {
        "type": "learning_goal",
        "position": "top",
        "style": "educational_banner",
        "duration": 3.0,
    },
    "letter_of_day": {
        "type": "label",
        "position": "top_left",
        "style": "letter_card",
        "duration": 5.0,
    },
    "number_of_day": {
        "type": "label",
        "position": "top_left",
        "style": "number_card",
        "duration": 5.0,
    },
    "color_label": {
        "type": "label",
        "position": "bottom",
        "style": "color_swatch",
        "duration": 3.0,
    },
    "shape_label": {
        "type": "label",
        "position": "bottom",
        "style": "shape_card",
        "duration": 3.0,
    },
    "lower_third": {
        "type": "lower_third",
        "position": "lower_third",
        "style": "name_tag",
        "duration": 3.0,
    },
    "celebration_stars": {
        "type": "celebration",
        "position": "center",
        "style": "stars_burst",
        "duration": 2.0,
    },
    "celebration_hearts": {
        "type": "celebration",
        "position": "center",
        "style": "hearts_float",
        "duration": 2.0,
    },
    "celebration_confetti": {
        "type": "celebration",
        "position": "full_screen",
        "style": "confetti_fall",
        "duration": 3.0,
    },
    "reward_badge": {
        "type": "reward",
        "position": "center",
        "style": "star_badge",
        "duration": 3.0,
    },
}


class GraphicsEngine:
    def create_overlay(
        self,
        template_key: str,
        text: str = "",
        start_time: float = 0.0,
        custom_duration: Optional[float] = None,
    ) -> Optional[GraphicOverlay]:
        template = GRAPHIC_TEMPLATES.get(template_key)
        if template is None:
            return None
        duration = custom_duration if custom_duration is not None else template["duration"]
        return GraphicOverlay(
            overlay_id=f"{template_key}_{start_time}",
            type=template["type"],
            text=text,
            start_time=start_time,
            end_time=start_time + duration,
            position=template["position"],
            style=template["style"],
        )

    def get_templates(self) -> dict[str, dict]:
        return dict(GRAPHIC_TEMPLATES)

    def list_template_keys(self) -> list[str]:
        return list(GRAPHIC_TEMPLATES.keys())
