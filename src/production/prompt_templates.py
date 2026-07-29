"""Pre-built prompt templates that combine character, environment, and animation prompts."""

from typing import Dict

CHARACTER_TEMPLATES: Dict[str, str] = {
    "lily_bunny": "Lily Bunny, {emotion}, {animation}, wearing {clothing}",
    "ben_bear": "Ben Bear, {emotion}, {animation}, wearing {clothing}",
    "teacher_owl": "Teacher Owl, {emotion}, {animation}, wearing {clothing}",
    "default": "{character}, {emotion}, {animation}",
}

ENVIRONMENT_TEMPLATES: Dict[str, str] = {
    "residential": "Sunny Meadow neighborhood, bright colorful preschool town, rounded architecture, soft pastel colors, lush green grass, clean sidewalks, friendly atmosphere, large trees, flower gardens",
    "school_exterior": "Little Learning Academy exterior, bright colorful school building, rounded architecture, soft pastel colors, playground visible, large windows, flower beds, friendly atmosphere",
    "classroom": "Bright colorful classroom, rounded kid-sized furniture, educational posters on walls, large windows with natural light, organized shelves with toys and books, colorful rug, friendly learning atmosphere",
    "playground": "Happy Hills Park playground, bright colorful play structures, soft safety surfaces, green grass, shade trees, colorful slides and swings, friendly outdoor atmosphere",
    "farm": "Green Valley Farm, red barn, green pastures, blue sky, white fence, friendly farm animals, vegetable garden, colorful flowers, warm rural atmosphere",
    "forest": "Whispering Woods, tall green trees, winding dirt path, colorful wildflowers, gentle stream, soft sunlight filtering through leaves, peaceful nature atmosphere",
    "beach": "Sandy Cove Beach, golden sand, gentle blue ocean waves, palm trees, bright blue sky with fluffy clouds, seashells scattered, calm seaside atmosphere",
    "downtown": "Main Street downtown, colorful storefronts, clean sidewalks, flower boxes, street lamps, friendly small-town atmosphere, bright and welcoming",
    "fantasy": "Dreamland, colorful magical landscape, glowing elements, friendly fantasy atmosphere, whimsical details, bright and enchanting",
    "default": "{environment}, bright colorful scene, friendly atmosphere",
}

ANIMATION_TEMPLATES: Dict[str, str] = {
    "idle": "gentle idle animation, subtle breathing, natural blinking, small body sway",
    "walk": "smooth walk cycle, gentle arm swing, natural steps, {speed} pace",
    "run": "playful run cycle, light steps, happy expression, child-friendly speed",
    "dance": "joyful dance loop, {dance_style} movement, bouncy rhythm, smiling",
    "wave": "friendly wave gesture, open hand, side-to-side motion, warm expression",
    "clap": "happy clapping motion, hands together, joyful expression",
    "sing": "singing animation, mouth shapes matching lyrics, expressive face, gentle body sway",
    "jump": "playful jump, light bounce, arms up, happy landing",
    "point": "pointing gesture, arm extended, curious expression, looking at target",
    "sit": "sitting pose, relaxed posture, gentle movement, comfortable position",
    "default": "{animation_type} animation, smooth motion, child-friendly",
}

CAMERA_TEMPLATES: Dict[str, str] = {
    "establishing": "wide establishing shot, shows full location, gentle camera",
    "wide": "wide shot, character visible in environment, steady composition",
    "medium": "medium shot, character waist-up, standard conversation distance",
    "close_up": "close-up shot, character face filling frame, emotional emphasis",
    "extreme_close_up": "extreme close-up, specific detail, dramatic emphasis",
    "tracking": "smooth tracking shot, following character movement, steady camera",
    "follow": "following shot from behind character, POV-lite perspective",
    "overhead": "overhead view, top-down perspective, shows layout and positions",
    "over_the_shoulder": "over-the-shoulder shot, conversation perspective",
    "default": "{shot_type} camera shot, stable framing, clear composition",
}

LIGHTING_TEMPLATES: Dict[str, str] = {
    "sunrise": "warm sunrise lighting, golden-pink tones, soft long shadows, gentle glow",
    "morning": "bright morning lighting, fresh clean light, moderate shadows, cheerful",
    "noon": "bright noon lighting, clean white light, minimal shadows, clear visibility",
    "golden_hour": "rich golden hour lighting, warm amber tones, long soft shadows, magical glow",
    "sunset": "warm sunset lighting, orange-purple sky, soft romantic atmosphere",
    "night": "night lighting, dark blue sky, warm window lights, starry sky, gentle moonlight",
    "indoor_warm": "warm indoor lighting, soft lamp glow, cozy atmosphere, gentle shadows",
    "indoor_bright": "bright indoor lighting, clean natural light from windows, cheerful",
    "studio": "soft studio lighting, even illumination, no harsh shadows, clean product lighting",
    "default": "{lighting} lighting, soft and flattering, child-friendly brightness",
}

WEATHER_TEMPLATES: Dict[str, str] = {
    "clear": "clear skies, bright sunshine, perfect weather, blue sky",
    "cloudy": "soft cloudy weather, diffused light, gentle overcast, comfortable",
    "rain": "gentle rain, raindrops, puddles, cozy atmosphere, umbrella",
    "snow": "light snow falling, white landscape, fluffy snow, magical winter atmosphere",
    "wind": "gentle breeze, leaves rustling, soft wind movement, fresh air",
    "rainbow": "rainbow in sky after rain, hopeful atmosphere, colorful arc, beautiful",
    "fog": "light morning mist, soft atmospheric fog, gentle mystery, calm",
    "default": "{weather} weather, pleasant atmosphere, child-friendly conditions",
}


def resolve_character_template(character_id: str) -> str:
    key = character_id.lower().replace(" ", "_")
    for template_key, template in CHARACTER_TEMPLATES.items():
        if key.startswith(template_key) or template_key in key:
            return template
    return CHARACTER_TEMPLATES["default"]


def resolve_environment_template(environment: str) -> str:
    key = environment.lower()
    for template_key, template in ENVIRONMENT_TEMPLATES.items():
        if template_key in key:
            return template
    return ENVIRONMENT_TEMPLATES["default"]


def resolve_animation_template(animation_type: str) -> str:
    key = animation_type.lower()
    for template_key, template in ANIMATION_TEMPLATES.items():
        if template_key in key:
            return template
    return ANIMATION_TEMPLATES["default"]


def resolve_camera_template(shot_type: str) -> str:
    key = shot_type.lower().replace("_", "_")
    for template_key, template in CAMERA_TEMPLATES.items():
        if template_key in key:
            return template
    return CAMERA_TEMPLATES["default"]


def resolve_lighting_template(lighting: str) -> str:
    key = lighting.lower()
    for template_key, template in LIGHTING_TEMPLATES.items():
        if template_key in key:
            return template
    return LIGHTING_TEMPLATES["default"]


def resolve_weather_template(weather: str) -> str:
    key = weather.lower()
    for template_key, template in WEATHER_TEMPLATES.items():
        if template_key in key:
            return template
    return WEATHER_TEMPLATES["default"]
