"""Canonical data for the Phase 4 Animation Bible.

Every value here is transcribed from the `Animation/` markdown bibles
so the docs and the runtime library agree on the quantitative standards.
"""

from .models import (
    ActionTiming, BlinkType, CameraShot, ClothElement, DanceLoop,
    EmotionalBeat, ExpressionLevel, FacialExpression, Gesture, IdleLayer,
    Interaction, InteractionPhase, JumpCycle, JumpPhase, LocomotionVariant,
    MouthAction, MotionCycle, PacingStandard, PhysicsRule, ReactionStandard,
    SceneTransition, ShotHold,
)

# ---------------------------------------------------------------------------
# Studio-wide constants
# ---------------------------------------------------------------------------

MASTER_FRAME_RATE = 24
EXPORT_FRAME_RATE = 30
VALID_FRAME_RATES = (24, 30, 60)
DANCE_BPM = 120
DANCE_FRAMES_PER_BEAT = 24  # at 24 fps

PHILOSOPHY = [
    "playful", "soft", "rounded", "energetic", "safe",
    "readable", "slightly exaggerated", "easy for young children to follow",
]

FORBIDDEN_MOTION = [
    "fast", "jerky", "chaotic", "violent", "aggressive",
    "rapid zoom", "camera shake", "unpredictable",
]

QUALITY_CHECKS = [
    "Smooth motion",
    "Consistent character proportions",
    "Correct facial expressions",
    "Natural blinking",
    "Soft body movement",
    "Child-friendly pacing",
    "Stable camera",
    "Proper interaction with objects",
    "Secondary motion present",
    "Matches studio style",
]

# ---------------------------------------------------------------------------
# Base cycle library (mirrors src/animation/motion.MOTION_PROPERTIES)
# ---------------------------------------------------------------------------

MOTION_CYCLES = [
    MotionCycle("idle", 24, True, "Standing relaxed with breathing, blinking, and subtle weight shifts", "simple"),
    MotionCycle("walk", 8, True, "Natural forward walking with arm swing and gentle bounce", "moderate"),
    MotionCycle("run", 6, True, "Bouncy running with increased arm swing and faster pace", "moderate"),
    MotionCycle("skip", 12, True, "Playful skipping with alternating hops and arm swings", "moderate"),
    MotionCycle("dance", 48, True, "Rhythmic full-body dance loop", "complex"),
    MotionCycle("jump", 16, False, "Upward jump with squat anticipation and landing recovery", "moderate"),
    MotionCycle("wave", 12, False, "Hand waving side to side with slight arm movement", "simple"),
    MotionCycle("point", 10, False, "Arm extends to point at an object with hand gesture", "simple"),
    MotionCycle("clap", 8, True, "Hands clap together with slight body bounce", "simple"),
    MotionCycle("hug", 20, False, "Arms open wide then close around another character or object", "moderate"),
    MotionCycle("sit", 14, False, "Character lowers into seated position with knee bend", "simple"),
    MotionCycle("stand", 14, False, "Character rises from seated to standing position", "simple"),
    MotionCycle("read", 60, False, "Head moves slightly while eyes track text across a page", "simple"),
    MotionCycle("write", 30, False, "Hand moves across surface with slight shoulder and head movement", "moderate"),
    MotionCycle("sleep", 40, True, "Gentle rhythmic breathing with slow rise and fall of chest", "simple"),
    MotionCycle("eat", 20, False, "Hand-to-mouth motion with chewing and swallowing", "moderate"),
    MotionCycle("drink", 18, False, "Cup raises to mouth with tilting and swallowing motion", "moderate"),
    MotionCycle("play", 30, True, "Playful movement with varied gestures and body language", "moderate"),
    MotionCycle("laugh", 14, False, "Body shakes with open mouth and eye crinkle expression", "simple"),
    MotionCycle("cry", 24, False, "Shoulders heave with occasional wiping of eyes", "simple"),
    MotionCycle("celebrate", 32, False, "Arms raised in excitement with possible jumping or spinning", "complex"),
]

# ---------------------------------------------------------------------------
# Idle animation layers (Animation/Motion/IDLE.md)
# ---------------------------------------------------------------------------

IDLE_LAYERS = [
    IdleLayer("breathing", "12 cycles per minute", 120, "chest rise 2-4% of torso height",
              "Smooth sine-wave breath; inhalation 48 frames, exhalation 72 frames"),
    IdleLayer("blinking", "every 4-6 seconds", 3, "3 frames total",
              "Snap shut, ease open; never hold closed over 3 frames"),
    IdleLayer("head_sway", "4 second cycle", 96, "±3 degrees Y-axis",
              "Slow sine wave; micro-tilt ±1 degree offset by 90 degrees"),
    IdleLayer("weight_shift", "6 second loop", 144, "60/40 -> 50/50 -> 40/60",
              "Hip sway ±2 degrees with spine counter-sway at half amplitude"),
    IdleLayer("accessory", "follows main action", 0, "ears/bow/tail secondary",
              "Ear, bow, or tail movement where applicable; 2-3 frame delay"),
]

# ---------------------------------------------------------------------------
# Walk variants (Animation/Motion/WALK_CYCLES.md)
# ---------------------------------------------------------------------------

WALK_VARIANTS = [
    LocomotionVariant(
        "slow_walk", 12, 24, 30,
        "Upright, slight lean forward (±2°)",
        "Soft elbows, gentle swing ±15° from rest",
        "Short stride, feet lift max 3% of character height",
        "±3% per step (very low bounce)",
        "Smooth step, no sharp transitions",
        "A relaxed, meandering pace — exploring, not rushing",
    ),
    LocomotionVariant(
        "normal_walk", 8, 16, 50,
        "Upright, natural posture, slight forward lean (±4°)",
        "Natural swing ±25° from rest",
        "Medium stride, feet lift max 6% of character height",
        "±5% per step (moderate bounce)",
        "Smooth step with slight ease at toe-off",
        "The default gait for everyday movement",
    ),
    LocomotionVariant(
        "happy_skip", 6, 12, 70,
        "Leaning back slightly (±3°) to counterbalance the bounce",
        "Arms up (elbows bent 90°), pumping ±35°",
        "One leg extends forward, other tucks under, airborne moment",
        "±12% — significant bounce with 2-frame airborne hang-time",
        "Bounce ease — fast up, slow down, hang at apex",
        "A joyful, bouncy gait — the character is having a good time",
        air_frames=2,
    ),
    LocomotionVariant(
        "fast_walk", 6, 12, 75,
        "Forward lean (±8°) — body chasing the feet",
        "Extended swing ±35°, elbows straighter",
        "Long stride, feet lift max 8% of character height",
        "±6% per step",
        "Ease in/out with linear mid-section",
        "Purposeful, energized walking — still walking, one foot always grounded",
    ),
    LocomotionVariant(
        "careful_walk", 16, 32, 20,
        "Upright, tense — leaning back slightly (±2°)",
        "Arms held out to sides (±20°) — balance position",
        "Very short stride, feet lift max 2%, toe points down",
        "±2% per step (nearly flat)",
        "Smooth step — slow, deliberate, no bounce",
        "Tiptoeing around something delicate or trying not to wake someone",
    ),
    LocomotionVariant(
        "tiptoe", 14, 28, 25,
        "Forward lean (±10°), torso extended upward",
        "Arms raised above shoulders (±45°) — reaching or balancing",
        "Knees bent, weight on balls of feet, heels up 5%",
        "±4% per step",
        "Smooth step with gentle rise and fall",
        "Heels off ground, reaching high; body appears 5-8% taller",
    ),
]

# ---------------------------------------------------------------------------
# Run variants (Animation/Motion/RUN_CYCLES.md)
# ---------------------------------------------------------------------------

RUN_VARIANTS = [
    LocomotionVariant(
        "normal_run", 5, 10, 80,
        "Forward lean ±12°",
        "Elbows bent 90°, arms pump forward-backward ±40°",
        "Knee drive forward, heel kick toward glutes",
        "±8% per stride",
        "Quick push-off ease-out, slight hang, landing ease-in",
        "Everyday running — playing in the park, chasing a ball",
        gait="run", air_frames=2,
    ),
    LocomotionVariant(
        "excited_run", 4, 8, 90,
        "Forward lean ±15°, chest slightly puffed",
        "Elbows bent 90°, arms pump ±50°, fists clenched",
        "High knee drive, longer stride, heels kick toward glutes",
        "±12% per stride — high bounce, extended airborne",
        "Explosive push-off ease-out, extended hang, soft landing",
        "The character is thrilled — joyful, never frantic",
        gait="run", air_frames=3,
    ),
    LocomotionVariant(
        "play_chase", 5, 10, 85,
        "Forward lean ±10°, upper body rotated ±20°",
        "One arm pumps forward, other reaches back playfully",
        "Standard running stride, wider stance for balance",
        "±6% per stride",
        "Normal run ease with gradual torso sine rotation",
        "Running while looking back at a friend — fun chase, never scary",
        gait="run", air_frames=2,
    ),
    LocomotionVariant(
        "small_sprint", 3, 6, 95,
        "Forward lean ±20°, head down slightly",
        "Elbows bent 90°, arms pump maximum ±55°, fists tight",
        "Maximum knee drive, feet barely touch the ground",
        "±10% per stride",
        "Near-linear with very short ground-contact ease",
        "Maximum speed, short bursts only — max 2 seconds, then decelerate",
        gait="run", air_frames=3,
    ),
]

# ---------------------------------------------------------------------------
# Jump library (Animation/Motion/JUMP_CYCLES.md)
# ---------------------------------------------------------------------------

JUMP_CYCLES = [
    JumpCycle(
        "standing_jump",
        (
            JumpPhase("anticipation", 3, "Crouch, torso lowers ±15%, knees bend to 60°"),
            JumpPhase("launch", 3, "Body extends rapidly, arms swing up overhead"),
            JumpPhase("apex", 3, "Full extension, slight hang-time"),
            JumpPhase("landing", 3, "Soft crouch to absorb, knees bend to 45°"),
        ),
        12, 30, "The basic vertical jump — from standing to standing",
    ),
    JumpCycle(
        "hop",
        (
            JumpPhase("anticipation", 2, "Slight crouch on one foot"),
            JumpPhase("launch", 3, "Upward push from one foot"),
            JumpPhase("apex", 1, "Brief hang-time"),
            JumpPhase("landing", 2, "Soft landing on same foot"),
        ),
        8, 15, "A single-foot hop — shifting position or bouncing in place",
    ),
    JumpCycle(
        "skip_step",
        (
            JumpPhase("hop_lift", 2, "Body lifts on standing leg"),
            JumpPhase("airborne", 2, "Suspended, weight transfers"),
            JumpPhase("step_landing", 2, "Land on opposite foot"),
            JumpPhase("transfer", 2, "Repeat on other side"),
        ),
        8, 12, "A hop combined with a step — forward locomotion with bounce",
    ),
    JumpCycle(
        "jump_for_joy",
        (
            JumpPhase("anticipation", 3, "Deep crouch, ±20% compression, arms swing far back"),
            JumpPhase("launch", 3, "Explosive upward, ±15% stretch, arms throw up and out"),
            JumpPhase("apex", 2, "Full stretch, legs spread, arms wide (jazz hands optional)"),
            JumpPhase("landing", 2, "Soft landing, slight crouch, arms come down open"),
        ),
        10, 45, "Exaggerated vertical jump expressing pure happiness — the highest jump",
    ),
    JumpCycle(
        "puddle_jump",
        (
            JumpPhase("anticipation", 3, "Crouch, looking down at puddle"),
            JumpPhase("launch", 2, "Forward + upward trajectory"),
            JumpPhase("apex_curl", 2, "Knees pulled up to chest to avoid splash"),
            JumpPhase("extend", 1, "Legs extend forward for landing"),
            JumpPhase("landing", 2, "Soft land, knees absorb"),
        ),
        10, 25, "Jumping over a puddle or small obstacle — legs curl to avoid the splash",
    ),
    JumpCycle(
        "dance_jump",
        (
            JumpPhase("anticipation", 2, "Slight crouch, coil for rotation"),
            JumpPhase("jump_turn", 3, "Body rotates 90° in air, or clap overhead at apex"),
            JumpPhase("landing", 3, "Land facing new direction, knees bend"),
        ),
        8, 20, "A jump with a turn or clap — used in dance sequences",
    ),
]

# ---------------------------------------------------------------------------
# Dance library (Animation/Motion/DANCE_LIBRARY.md)
# ---------------------------------------------------------------------------

DANCE_LOOPS = [
    DanceLoop("side_to_side", 8, 120, "Weight shifts side to side with a head bob",
              "100% of character width (close, casual)", "Easy"),
    DanceLoop("circle_dance", 48, 120, "Group dance — hands joined, rotating in a circle",
              "120% minimum between centers (arms-length)", "Moderate"),
    DanceLoop("clap_dance", 8, 120, "Clapping on the beat with body movement",
              "80% of character width", "Easy"),
    DanceLoop("spin", 8, 120, "Solo 360° turn in place with a head snap at the end",
              "150% of character width (solo clearance)", "Moderate"),
    DanceLoop("march", 12, 120, "High knees, arms pumping — playful marching",
              "150% of character width (knee lift room)", "Easy"),
    DanceLoop("freeze_dance", 12, 120, "Dance 8 frames then freeze 4 frames in a surprised pose",
              "100% of character width", "Easy"),
    DanceLoop("ribbon_dance", 16, 120, "Flowing arm circles with a ribbon, gentle body movement",
              "200% of character width (ribbon clearance)", "Moderate"),
]

# ---------------------------------------------------------------------------
# Facial expression library (Animation/Facial/FACIAL_LIBRARY.md)
# ---------------------------------------------------------------------------

FACIAL_EXPRESSIONS = [
    FacialExpression("happiness", (
        ExpressionLevel(1, "content", "Gentle closed smile, neutral eyes, relaxed brows"),
        ExpressionLevel(2, "pleased", "Warm smile, slight eye crinkle, soft raised brows"),
        ExpressionLevel(3, "happy", "Open smile with teeth, eyes squinted, brows arched"),
        ExpressionLevel(4, "delighted", "Wide grin, eyes squeezed, head may tilt back slightly"),
        ExpressionLevel(5, "ecstatic", "Mouth open wide, bright eyes, brows high, whole face lit"),
    ), "The most frequently used expression — standardized smile levels 1-5"),
    FacialExpression("sadness", (
        ExpressionLevel(1, "down", "Slight frown, eyes slightly lower, brows neutral"),
        ExpressionLevel(2, "disappointed", "Clear frown, eyes downcast, sad tilt brows"),
        ExpressionLevel(3, "sad", "Full frown, lower eyelids rise, brows knit, eyes glassy"),
        ExpressionLevel(4, "very_sad", "Quivering lip, tears welling, head tilted down"),
        ExpressionLevel(5, "crying", "Mouth wobbly oval, eyes closed, tears falling, brows knit"),
    )),
    FacialExpression("surprise", (
        ExpressionLevel(1, "curiosity", "Eyes level 4, brows raised, slight 'o' mouth"),
        ExpressionLevel(2, "mild_surprise", "Eyes level 4-5, brows raised, head pulls back"),
        ExpressionLevel(3, "surprise", "Eyes level 5, brows high, mouth open oval"),
        ExpressionLevel(4, "startled", "Eyes level 5, brows very high, mouth wide"),
        ExpressionLevel(5, "shocked", "Eyes held wide, brows maximum, mouth open 12-24 frames"),
    )),
    FacialExpression("anger", (
        ExpressionLevel(1, "annoyed", "Slight brow lower, thin lips, brief"),
        ExpressionLevel(2, "frustrated", "Lowered brows, pursed mouth or slight frown"),
        ExpressionLevel(3, "upset", "Brows lowered and knit, eyes narrowed, frown"),
        ExpressionLevel(4, "angry", "Strong brow lower, glare, tight flat-line mouth"),
        ExpressionLevel(5, "very_upset", "Maximum brow lower, narrowed eyes, clenched teeth visible"),
    ), "Mild frustration to upset — never rage"),
    FacialExpression("fear", (
        ExpressionLevel(1, "worried", "Slight brow knit, eyes level 4, lip tensed"),
        ExpressionLevel(2, "nervous", "Brows raised and knit, eyes level 4, mouth open"),
        ExpressionLevel(3, "uneasy", "Raised brows, wide eyes, mouth tense, head pulling back"),
        ExpressionLevel(4, "scared", "Brows high and knit, eyes level 5, body tense"),
        ExpressionLevel(5, "frightened", "Maximum brows, eyes wide, mouth stretched horizontally"),
    ), "Mild worry to scared — never terror"),
    FacialExpression("disgust", (
        ExpressionLevel(1, "distaste", "Slight nose wrinkle, one-sided lip curl"),
        ExpressionLevel(2, "disgust", "Nose wrinkled, upper lip raised, eyes narrowed"),
        ExpressionLevel(3, "eww", "Full nose wrinkle, mouth open in disgust, recoil"),
    )),
    FacialExpression("curiosity", (
        ExpressionLevel(1, "interested", "Slight head tilt, eyes level 4, neutral mouth"),
        ExpressionLevel(2, "curious", "Head tilt, one brow raised, eyes level 4"),
        ExpressionLevel(3, "inquisitive", "Both brows raised, head tilted, 'o' mouth"),
        ExpressionLevel(4, "intrigued", "Leaning in, wide eyes, raised brows, open mouth"),
        ExpressionLevel(5, "fascinated", "Eyes bright and engaged, leaning forward, smile"),
    )),
    FacialExpression("confusion", (
        ExpressionLevel(1, "unsure", "Slight brow knit, head tilt, mouth flat"),
        ExpressionLevel(2, "confused", "Knit brows, eyes level 4, pursed mouth"),
        ExpressionLevel(3, "very_confused", "Deep knit, one brow lower, squint, wry mouth"),
        ExpressionLevel(4, "bewildered", "Asymmetrical brows, wide eyes, mouth open, head shake"),
    )),
    FacialExpression("excitement", (
        ExpressionLevel(1, "interested", "Slight smile, eyes bright, brows up"),
        ExpressionLevel(2, "eager", "Smile level 2, eyes level 4, slight bounce"),
        ExpressionLevel(3, "excited", "Smile level 3, eyes bright, brows up, head up"),
        ExpressionLevel(4, "thrilled", "Smile level 4, eyes level 4-5, bouncing"),
        ExpressionLevel(5, "overjoyed", "Smile level 5, eyes level 5, jumping — maximum brightness"),
    )),
    FacialExpression("embarrassment", (
        ExpressionLevel(1, "self_conscious", "Slight smile, eyes drop down, brief look away"),
        ExpressionLevel(2, "embarrassed", "Nervous closed smile, eyes down or shifting"),
        ExpressionLevel(3, "very_embarrassed", "Wide eyes then looking down, cheeks darker"),
        ExpressionLevel(4, "mortified", "Eyes squeezed shut, head down, hands covering face"),
    )),
    FacialExpression("pride", (
        ExpressionLevel(1, "satisfied", "Closed smile, chin slightly up, eyes level 3"),
        ExpressionLevel(2, "proud", "Smile level 2-3, chin up, chest out, eyes bright"),
        ExpressionLevel(3, "triumphant", "Smile level 4, head high, arms may raise"),
    )),
    FacialExpression("love", (
        ExpressionLevel(1, "fondness", "Soft smile, gentle eyes, head tilt"),
        ExpressionLevel(2, "warmth", "Warm smile, eyes soft and bright, slight lean in"),
        ExpressionLevel(3, "affection", "Deep warm smile, eyes half-lidded and soft"),
        ExpressionLevel(4, "adoring", "Big smile, very soft eyes, head tilt, full attention"),
    ), "Love / affection"),
    FacialExpression("sleepiness", (
        ExpressionLevel(1, "tired", "Eyes half-lidded, slight yawn, slow blink"),
        ExpressionLevel(2, "sleepy", "Heavy lids, head nodding, slow movements"),
        ExpressionLevel(3, "very_sleepy", "Eyes nearly closed, mouth relaxed"),
        ExpressionLevel(4, "falling_asleep", "Eyes closed, head drooping, body relaxing"),
    )),
]

# ---------------------------------------------------------------------------
# Eye / blink standards (Animation/Facial/EYE_ANIMATION.md)
# ---------------------------------------------------------------------------

BLINK_TYPES = [
    BlinkType("normal", "2-3", "~100ms", "Default"),
    BlinkType("slow", "4-6", "~200ms", "Tired, relaxed, content"),
    BlinkType("double", "2+2 (+4 gap)", "~300ms", "Emphasis, surprise, processing"),
    BlinkType("fast", "1-2", "~60ms", "Startle, quick reaction"),
    BlinkType("exaggerated", "6-8", "~300ms", "Comedic, Owl signature"),
]

EYE_OPENNESS = {
    "closed": "Eyelids fully shut — sleep, blink, eyes squeezed shut",
    "half_lidded": "Eyelid covers top half of iris — tired, relaxed, sleepy",
    "normal": "Iris fully visible, natural — default, conversation, idle",
    "slightly_wide": "White visible above iris — curiosity, mild surprise, alert",
    "fully_open": "Large whites all around iris — surprise, shock, excitement",
}

BROW_POSITIONS = {
    "neutral": "Natural resting position — default, listening",
    "raised": "Arched upward, center lifts — surprise, excitement, fear",
    "lowered": "Pulled down and slightly together — anger, frustration, confusion",
    "one_raised": "One brow up, one neutral — curiosity, skepticism",
    "knit": "Pulled together and down toward center — worry, concentration, sadness",
    "arched": "Gentle upward curve across both — happiness, warmth",
    "sad_tilt": "Inner corners angled up, outer down — sadness, disappointment",
}

EXPRESSION_TRANSITION_FRAMES = {
    (0,): 4,        # same level
    (1,): (4, 6),   # 1 level
    (2,): (6, 8),   # 2 levels
    (3,): (8, 10),  # 3 levels
    (4,): (10, 12), # 4 levels
    (5,): 12,       # extreme 1<->5
}

# ---------------------------------------------------------------------------
# Mouth standards (Animation/Facial/MOUTH_ANIMATION.md)
# ---------------------------------------------------------------------------

MOUTH_SHAPES = {
    "closed": "M, B, P — lips gently together, relaxed",
    "open": "A, I — mouth open oval, jaw dropped",
    "wide": "E, S — lips stretched horizontally",
    "pursed": "O, U — lips rounded forward, small opening",
    "smile": "Happy sounds — corners up, slight opening",
    "frown": "Sad sounds — corners down, lower lip may protrude",
    "laugh": "Ha, He — wide open, teeth visible, jaw dropped",
    "yawn": "— huge oval, jaw fully dropped",
    "whisper": "— very small opening, lips barely apart",
    "singing": "All — exaggerated shapes, held longer",
    "kiss": "— puckered forward",
    "flat": "— straight horizontal line, firm",
}

MOUTH_ACTIONS = [
    MouthAction("talking", "Per phoneme 4-6 frames; per syllable 8-12; word pause 6-8; sentence pause 12-18",
                "Pre-speech breath 4 frames; post-speech 6 frames back to neutral"),
    MouthAction("singing", "Per shape 8-12 frames (2x longer than speech); phrase end 12-16",
                "Vowels emphasized; head sways with melody; eyes may close on emotional notes"),
    MouthAction("laughing", "Open 3 / closed 3 / cycle 6 frames",
                "Repeat 3-5 cycles; breathing gaps every 2-3 cycles; body bounces with rhythm"),
    MouthAction("yawning", "Build 8 / peak 12 / release 8 frames",
                "Preceded by eye rubbing (6 frames); followed by head shake or stretch (12)"),
    MouthAction("whispering", "Mouth shape 4-6 frames; head lean 4; hand cue 8",
                "Small subtle movements held slightly longer than normal speech"),
    MouthAction("breathing", "Idle 6-8; pre-speech 4; post-speech 6; exhausted 10-12; sigh 12",
                "Continuous idle breathing; combine with chest/shoulder rise"),
]

# ---------------------------------------------------------------------------
# Gesture library (Animation/Gestures/GESTURE_LIBRARY.md)
# ---------------------------------------------------------------------------

GESTURES = [
    Gesture("wave", "12 frames per cycle (can repeat)",
            "Arm raised to shoulder height, elbow bent ~90°",
            "Open palm facing forward, fingers together",
            "Slight lean toward recipient, smile",
            "Greeting, departing, getting attention",
            "Wrist rotates side-to-side, not whole arm"),
    Gesture("point", "Extend 8, hold variable, retract 6",
            "Arm extends toward target, nearly straight",
            "Index finger extended, other fingers curled in",
            "Lean slightly toward target, follow gaze",
            "Directing attention, answering 'where' questions",
            "Hold at extension min 8 frames; point at objects, not characters"),
    Gesture("thumbs_up", "8 frames",
            "Arm raised, elbow bent, fist near chest or extended",
            "Closed fist with thumb pointing up",
            "Smile, slight head nod, chest slightly out",
            "Approval, encouragement, 'good job'"),
    Gesture("high_five", "10 total (raise 4, slap 1, hold 1, lower 4)",
            "Arm raises to shoulder height, hand facing partner",
            "Open palm, fingers together, slightly cupped",
            "Lean toward partner, smile, slight head forward",
            "Celebration, greeting, accomplishment",
            "Add a subtle bounce on contact"),
    Gesture("hug", "16 total (arms open 4, close 4, hold 4, release 4)",
            "Arms open wide then wrap around",
            "Open, relaxed — gently grasping",
            "Lean forward into hug, eyes soft or closed, smile",
            "Greeting, comfort, affection, reunion",
            "Hold min 4 frames, extend 8-12 for emotional moments; release smoothly"),
    Gesture("clap", "6 frames per clap",
            "Hands at chest height, elbows bent",
            "Hands slightly cupped, fingers together",
            "Smile, slight bounce, head may tilt",
            "Applause, celebration, song rhythm, excitement",
            "Repeat every 6 frames for sustained clapping"),
    Gesture("hold_object", "Varies by object size",
            "Small: one hand at waist/chest; Large: both hands wrapped",
            "Small: fingers curled; Large: palms supporting",
            "Adjust based on object weight",
            "Carrying, presenting, examining items",
            "Objects feel light; hands visibly contact the surface"),
    Gesture("pick_up", "12 total (reach 4, grasp 2, lift 4, hold 2)",
            "Reach down/toward object, then lift to natural hold",
            "Reach open; grasp closing; lift secure grip",
            "Bend slightly at waist for floor pickup",
            "Retrieving any object from a surface",
            "Eyes look 4-6 frames before reach; smooth arc lift"),
    Gesture("put_down", "10 total (lower 4, release 2, withdraw 4)",
            "Lower from hold position to surface",
            "Maintaining grip then opening, relaxing",
            "Lean forward slightly",
            "Setting an object on a surface",
            "Place gently; hand lingers 2 frames after release"),
    Gesture("throw_gentle", "12 total (wind up 4, release 2, follow through 6)",
            "Wind up back; release extends; follow continues arc",
            "Holding then open, fingers extend then relaxed",
            "Weight back on wind up, forward on release",
            "Playing catch, tossing a ball, gentle underhand throw",
            "Underhand preferred; never throw at another character"),
    Gesture("catch", "8 total (arms out 2, close 2, hold 2, lower 2)",
            "Extend toward incoming object, then bring to chest",
            "Open palms then wrapping then secure",
            "Eyes track object, slight lean toward catch",
            "Receiving a thrown object",
            "Small bounce/absorb motion on catch"),
    Gesture("open_book", "10 total (hands out 2, grasp 2, open 4, hold 2)",
            "Both hands to book edges, then spread outward",
            "Open palms, fingertips holding edges, sliding apart",
            "Look down at book, head centered",
            "Reading a book, showing pictures"),
    Gesture("turn_page", "8 total (hand to corner 2, pinch 1, turn 3, release 2)",
            "Hand moves to upper corner of page",
            "Pinch then sliding then open",
            "Head may tilt slightly to watch page",
            "Reading a book sequentially",
            "Page lifts, crosses, settles — slow enough for children"),
    Gesture("shake_head_no", "10 total (center-left 3, center-right 3, center 4)",
            "Arms at sides or raised with palms out",
            "Relaxed or palms facing outward",
            "Head rotates on neck axis, shoulders stable",
            "Disagreement, refusal, 'no' response"),
    Gesture("nod_yes", "8 total (down 3, up 3, hold 2)",
            "Arms at rest or neutral",
            "Relaxed",
            "Chin drops toward chest, then rises",
            "Agreement, affirmation, understanding",
            "Single nod for simple agreement, 2-3 for enthusiastic yes"),
    Gesture("shrug", "12 total (shoulders up 4, hands open 2, hold 2, release 4)",
            "Shoulders rise toward ears, arms relax at sides",
            "Palms turn upward, open — 'I don't know' shape",
            "Head may tilt, eyebrows raise",
            "Uncertainty, 'I don't know', indifference"),
    Gesture("think", "10 to achieve, hold as needed",
            "One arm raises, hand approaches chin",
            "Fingers lightly touching chin or stroking",
            "Head tilted up/to side, eyes looking up or away",
            "Pondering a question, considering options",
            "Hold 12-48 frames; alternate with eye darts"),
    Gesture("count_fingers", "6 frames per number",
            "Hand raised to chest height, palm facing viewer",
            "Fingers extend one by one (index to thumb)",
            "Eyes look at fingers, slight head tilt",
            "Counting items, listing, showing quantity",
            "Each extension 4 frames + 2 frame pause"),
    Gesture("blow_kiss", "10 total (hand to lips 3, kiss 1, blow 3, wave 3)",
            "Hand moves to mouth, then extends outward",
            "Fingertips at lips then open palm releasing",
            "Slight lean forward, soft eyes",
            "Sending affection from a distance, goodbye"),
    Gesture("cover_mouth", "6 frames",
            "Hand(s) move quickly to cover mouth area",
            "Open palm or both hands flat over mouth",
            "Eyes wide, brows raised, head may pull back",
            "Surprise, shock, gasping, 'oh my'",
            "Hold covered 6-12 frames, then lower slowly"),
    Gesture("hands_on_hips", "8 frames",
            "Both arms bend, hands move to hip area",
            "Palms resting on hips, fingers forward or slightly curled",
            "Chest slightly out, chin up, feet shoulder-width",
            "Confidence, impatience, scolding, determination",
            "Can be held as a stance; often paired with foot tapping"),
    Gesture("arms_crossed", "10 frames",
            "Both arms fold across chest, hands on opposite upper arms",
            "Relaxed grip on own arms",
            "Shoulders may hunch, head may tilt",
            "Defensiveness, stubbornness, disagreement, waiting"),
    Gesture("fist_pump", "6 total (pull down 2, pump up 2, hold 2)",
            "Elbow bends, fist moves down then up",
            "Closed fist, thumb outside",
            "Smile, slight body bounce, head may nod",
            "Celebration, 'yes!', success, victory",
            "More restrained than an adult fist pump"),
]

# ---------------------------------------------------------------------------
# Interaction library (Animation/Interactions/INTERACTION_LIBRARY.md)
# ---------------------------------------------------------------------------

INTERACTIONS = [
    Interaction("open_door", (
        InteractionPhase("reach", 3, "Arm extends toward handle, eyes lead the movement"),
        InteractionPhase("grasp", 1, "Fingers wrap around handle, subtle squeeze"),
        InteractionPhase("turn", 4, "Wrist rotates, handle turns with smooth resistance"),
        InteractionPhase("pull", 6, "Arm pulls door open, body leans back, feet shift"),
        InteractionPhase("release", 2, "Fingers open, arm lowers to side"),
    ), 16, "Standing to hinge side, facing door panel; eyes track handle; shoulder leads reach"),
    Interaction("close_door", (
        InteractionPhase("reach", 2, "Arm extends toward door edge or handle"),
        InteractionPhase("grasp", 1, "Hand contacts door surface or handle"),
        InteractionPhase("push", 6, "Arm pushes door closed, body leans forward"),
        InteractionPhase("release", 3, "Hand lifts away from door"),
        InteractionPhase("step_back", 2, "Character steps backward to neutral"),
    ), 14, "Standing on the open side; subtle blink at contact frame"),
    Interaction("open_book", (
        InteractionPhase("hands_out", 2, "Arms extend forward from idle, palms down"),
        InteractionPhase("grasp", 2, "Hands contact book cover edges, thumbs on top"),
        InteractionPhase("open_wide", 4, "Arms move apart, book opens, wrists rotate outward"),
        InteractionPhase("hold", 2, "Book held open, slight bobble settles, eyes scan pages"),
    ), 10, "Sitting or standing, book at chest level; head tilts down to pages"),
    Interaction("eat_apple", (
        InteractionPhase("hold_up", 2, "Arm lifts apple from waist to mouth height, eyes on apple"),
        InteractionPhase("bite", 2, "Arm brings apple to mouth, jaw opens, head tilts slightly"),
        InteractionPhase("chew", 10, "Jaw chews in steady rhythm, cheeks bulge subtly"),
        InteractionPhase("swallow", 2, "Throat motion, apple lowers slightly"),
        InteractionPhase("lower", 4, "Arm lowers apple back to waist, swallow completes"),
    ), 20, "Standing or sitting relaxed; chewing steady and exaggerated for readability"),
    Interaction("drink_water", (
        InteractionPhase("reach_cup", 2, "Hand extends toward cup on table"),
        InteractionPhase("grasp", 1, "Fingers wrap around cup handle or body"),
        InteractionPhase("lift", 4, "Arm raises cup to mouth, forearm rotates to tilt"),
        InteractionPhase("sip", 4, "Cup tilts, liquid enters mouth, throat moves"),
        InteractionPhase("lower", 4, "Arm lowers cup back to table surface"),
        InteractionPhase("release", 1, "Fingers open, hand returns to neutral"),
    ), 16, "Sitting at table; eyes track cup; lips purse at cup rim"),
    Interaction("kick_ball", (
        InteractionPhase("wind_up", 4, "Kicking leg pulls backward, arms balance"),
        InteractionPhase("kick", 1, "Leg swings forward, foot contacts ball"),
        InteractionPhase("follow_through", 4, "Leg continues forward arc, body shifts forward"),
        InteractionPhase("land", 3, "Kicking foot returns to ground, balance restores"),
    ), 12, "Standing behind ball; opposite arm forward during kick; eyes track through impact"),
    Interaction("throw_ball", (
        InteractionPhase("reach_back", 3, "Arm swings backward, torso rotates away, weight to back foot"),
        InteractionPhase("forward", 3, "Arm swings forward, torso rotates toward target"),
        InteractionPhase("release", 1, "Fingers open, ball leaves hand at apex of arc"),
        InteractionPhase("follow_through", 5, "Arm continues downward arc, body settles"),
        InteractionPhase("settle", 2, "Arms lower, posture returns to neutral"),
    ), 14, "Standing sideways to target; underhand preferred; never throw at a character"),
    Interaction("catch_ball", (
        InteractionPhase("arms_out", 2, "Both arms extend forward, palms open facing ball"),
        InteractionPhase("track", 4, "Eyes follow ball, head and arms adjust"),
        InteractionPhase("close", 2, "Hands close around ball as it arrives"),
        InteractionPhase("hold", 2, "Arms absorb impact, pull ball toward chest"),
        InteractionPhase("lower", 2, "Arms lower ball to waist, eyes check ball"),
    ), 12, "Standing facing the thrower; knees bend to absorb; small bounce settle"),
    Interaction("build_blocks", (
        InteractionPhase("select", 4, "Eyes scan blocks, arm reaches toward chosen block"),
        InteractionPhase("grasp", 2, "Fingers wrap around block, confirm grip"),
        InteractionPhase("lift", 4, "Arm raises block to placement height, eyes on target"),
        InteractionPhase("position", 4, "Arm moves block above stack, adjusts alignment"),
        InteractionPhase("place", 4, "Arm lowers block onto stack, fingers release"),
        InteractionPhase("release", 2, "Fingers open, arm pulls back, check stability"),
    ), 20, "Per block; stack stays steady up to 8 blocks; gentle wiggle on placement"),
    Interaction("draw_picture", (
        InteractionPhase("hold_pencil", 0, "Continuous tripod grip on pencil or crayon"),
        InteractionPhase("stroke", 8, "Arm moves pencil across paper, eyes follow tip"),
        InteractionPhase("lift", 2, "Pencil lifts from paper, arm repositions"),
        InteractionPhase("reposition", 6, "Arm moves to new start, eyes check reference"),
    ), 16, "Sitting at table or easel; shoulder drives long strokes; loops seamlessly",
    loopable=True),
    Interaction("brush_teeth", (
        InteractionPhase("hold_brush", 2, "Hand lifts brush to mouth, toothpaste visible"),
        InteractionPhase("brush_motion", 18, "Arm moves brush in gentle circles across teeth"),
        InteractionPhase("rinse", 4, "Hand lowers brush, mouth fills, swish, spit"),
    ), 24, "Per cycle; small circles top then bottom; cheeks puff during rinse"),
    Interaction("wash_hands", (
        InteractionPhase("turn_water", 3, "Hand reaches faucet, twists, water flows"),
        InteractionPhase("wet", 3, "Both hands under water stream, palms up"),
        InteractionPhase("soap", 6, "Hand reaches soap pump, rubs soap between palms"),
        InteractionPhase("scrub", 12, "Hands rub in circular motion, fingers interlace"),
        InteractionPhase("rinse", 4, "Hands return under water, rub to remove soap"),
        InteractionPhase("dry", 2, "Hands reach for towel, rub together to dry"),
    ), 30, "Standing at sink; water splashes softly; wiggling fingers during rinse"),
    Interaction("plant_flower", (
        InteractionPhase("dig", 12, "Small shovel or hands dig hole in soil"),
        InteractionPhase("place_seed", 4, "Hand lowers seed into hole, releases carefully"),
        InteractionPhase("cover", 8, "Hands push soil over seed, pat down gently"),
        InteractionPhase("water", 12, "Watering can lifts, tilts, water pours"),
        InteractionPhase("stand", 4, "Character stands, brushes hands, smiles"),
    ), 40, "Kneeling or squatting near pot; deliberate careful arm movements"),
    Interaction("feed_animal", (
        InteractionPhase("hold_food", 2, "Hand lifts food from container"),
        InteractionPhase("offer", 6, "Arm extends toward animal, palm open, food visible"),
        InteractionPhase("animal_eats", 6, "Animal takes food gently, character watches"),
        InteractionPhase("lower", 2, "Arm lowers, character smiles, may pet animal"),
    ), 16, "Standing or crouching near enclosure; hand stays still while animal eats"),
    Interaction("pet_dog", (
        InteractionPhase("reach", 2, "Arm extends toward dog's head/back"),
        InteractionPhase("stroke_forward", 4, "Hand moves from head toward tail along back"),
        InteractionPhase("stroke_back", 4, "Hand returns from tail toward head"),
        InteractionPhase("lift", 2, "Hand lifts away, arm returns to neutral"),
    ), 12, "Sitting or crouching beside dog; gentle pressure, no heavy patting"),
    Interaction("pet_dog_loop", (
        InteractionPhase("stroke_forward", 4, "Hand moves from head toward tail"),
        InteractionPhase("stroke_back", 4, "Hand returns from tail toward head"),
    ), 8, "Continuous loop; settled posture beside the dog", loopable=True),
    Interaction("ride_bicycle", (
        InteractionPhase("pedal_cycle", 24, "Legs alternate pushing pedals, handlebars held steady"),
    ), 24, "Per pedal cycle; upper body stable; gentle side-to-side sway"),
    Interaction("pick_up_toy", (
        InteractionPhase("bend", 3, "Hips and knees bend, torso lowers toward toy"),
        InteractionPhase("reach", 2, "Arm extends toward toy, fingers preparing to grasp"),
        InteractionPhase("grasp", 1, "Fingers wrap around toy, confirm grip"),
        InteractionPhase("lift", 2, "Arm raises toy, body begins to straighten"),
        InteractionPhase("stand", 2, "Hips and knees extend, returns to full height"),
    ), 10, "Bend at hips and knees, not a back-bend; toy held at waist after lift"),
    Interaction("put_away_toy", (
        InteractionPhase("hold", 2, "Character stands holding toy at waist level"),
        InteractionPhase("bend", 2, "Hips and knees bend toward shelf/box"),
        InteractionPhase("reach", 2, "Arm extends toy toward target location"),
        InteractionPhase("place", 2, "Toy is set down, fingers release"),
        InteractionPhase("release", 2, "Fingers open, hand pulls back"),
        InteractionPhase("stand", 2, "Hips and knees extend, returns to full height"),
    ), 12, "Gentle release, no dropping; satisfied expression after release"),
    Interaction("tie_shoelaces", (
        InteractionPhase("bend", 4, "Hips and knees bend, hands reach toward shoes"),
        InteractionPhase("cross", 4, "Laces crossed over, one end pulled under"),
        InteractionPhase("loop", 8, "One lace folded into loop, held between thumb and finger"),
        InteractionPhase("pull", 4, "Second loop pulled through the crossed section"),
        InteractionPhase("second_loop", 12, "Second lace folded, crossed in front"),
        InteractionPhase("tie", 8, "Both loops pulled tight, knot forms"),
        InteractionPhase("straighten", 8, "Loops adjusted, laces straightened, knot centered"),
        InteractionPhase("stand", 12, "Hands lift off, back straightens, knees extend"),
    ), 60, "Sitting with one foot extended; concentration expression; satisfied exhale"),
    Interaction("blow_out_candle", (
        InteractionPhase("lean_in", 4, "Torso leans forward toward candle"),
        InteractionPhase("big_breath", 2, "Shoulders rise, chest expands, mouth opens wide"),
        InteractionPhase("blow", 4, "Lips purse, air expelled, flame flickers and extinguishes"),
        InteractionPhase("clap", 4, "Hands clap in celebration, smile"),
        InteractionPhase("lean_back", 2, "Torso returns to neutral, satisfied expression"),
    ), 16, "Standing or sitting at table with cake; flame flicker 1f, out 1f, smoke 2f"),
]

# ---------------------------------------------------------------------------
# Camera language (Animation/Camera/CAMERA_LANGUAGE.md)
# ---------------------------------------------------------------------------

CAMERA_SHOTS = [
    CameraShot("establishing", "Full location view establishing where the scene takes place",
               72, 120, "Wide view, characters <20% of frame, environment dominates",
               "Static or very slow gentle pan (1-2°/sec)",
               "Opening a new scene, location change, time of day transition",
               "Use 1 per scene at the start; environment fills 80%+ of frame"),
    CameraShot("wide", "Character visible within their environment during action",
               48, 96, "Full body, character 30-40% of frame height",
               "Static or smooth tracking with character",
               "Walking, playing, interacting with objects",
               "Standard action shot; room to move within frame"),
    CameraShot("medium", "Character from waist up — primary dialogue/expression shot",
               48, 144, "Character centered or rule-of-thirds, hands visible",
               "Static preferred; micro-adjustments (2-3 px) allowed",
               "Conversation, emotional beats, gestures",
               "Most frequently used shot type; hands visible for gestures"),
    CameraShot("close_up", "Face fills frame, emphasizes emotion",
               24, 96, "Face centered, minimal background",
               "Static only",
               "Emotional moments, reaction shots, important expressions",
               "Max 2 per scene; always establish wider first; min hold 24 frames"),
    CameraShot("over_shoulder", "Over the shoulder of one character onto another",
               48, 96, "Shoulder/back of foreground character in frame edge",
               "Static or very slow",
               "Conversation, exchange of glances",
               "Face of the character being watched reads clearly"),
    CameraShot("tracking", "Camera moves alongside the character during action",
               72, 192, "Character full body in motion, lead space ahead",
               "Smooth lateral tracking at character speed",
               "Walking, running, following action",
               "Never faster than the character; no shake"),
    CameraShot("slow_push_in", "Camera slowly moves toward the subject",
               72, 120, "Subject grows from medium to close range",
               "Slow steady push, ease in/out",
               "Emphasis, building emotion, reveal",
               "Avoid rapid zooms"),
    CameraShot("gentle_pan", "Camera rotates horizontally, scanning the scene",
               72, 144, "Scene revealed gradually left-right",
               "1-2° per second, steady",
               "Revealing a location, following a moving subject",
               "Gentle and slow; children never disoriented"),
    CameraShot("gentle_tilt", "Camera rotates vertically, up or down",
               72, 120, "Scene revealed vertically",
               "Slow steady tilt, ease in/out",
               "Revealing tall objects, height emphasis",
               "Smooth and predictable"),
    CameraShot("two_shot", "Two characters in the same frame",
               48, 144, "Both characters balanced in frame",
               "Static preferred",
               "Shared moments, interaction, dialogue",
               "Keep both faces readable"),
    CameraShot("group_shot", "Three or more characters together",
               72, 144, "Group balanced, all faces visible",
               "Static or very slow",
               "Group moments, ensemble scenes",
               "No character blocked for long"),
    CameraShot("insert_shot", "Close view of an object or detail",
               24, 72, "Object fills frame",
               "Static only",
               "Showing an important object, letters, numbers",
               "Cut to it then cut back to character"),
]

CAMERA_MOTION_TO_SHOT = {
    "static": "medium",
    "pan": "gentle_pan",
    "tilt": "gentle_tilt",
    "track": "tracking",
    "follow": "tracking",
    "push_in": "slow_push_in",
    "pull_out": "wide",
    "orbit": "group_shot",
    "crane": "group_shot",
    "dolly": "tracking",
}

# ---------------------------------------------------------------------------
# Transitions (Animation/Camera/TRANSITIONS.md)
# ---------------------------------------------------------------------------

SCENE_TRANSITIONS = [
    SceneTransition("cross_dissolve", 12, 16,
                    "First scene fades out while second fades in, overlapping",
                    "Linear cross-fade A 100%->0%, B 0%->100%",
                    "Standard scene change, time passing, location change",
                    "Default transition; not for changes within the same continuous scene"),
    SceneTransition("fade_to_black", 16, 16,
                    "Scene fades to solid black, holds, then next scene begins",
                    "Linear to black (100%->0% over 16 frames)",
                    "End of a story segment, end of episode, significant time passage",
                    "Hold on black 8-12 frames; max 2-3 times per episode"),
    SceneTransition("fade_from_black", 12, 12,
                    "Screen starts black, scene fades in to full visibility",
                    "Linear from black (0%->100% over 12 frames)",
                    "Beginning of a story segment after fade to black",
                    "Pairs with fade to black; faster than fade-out"),
    SceneTransition("fade_to_white", 12, 12,
                    "Scene fades to solid white, holds, then next scene begins",
                    "Linear to white (100%->0% over 12 frames)",
                    "Dream, imagination, magical segment",
                    "Hold white 6-8 frames"),
    SceneTransition("gentle_slide", 16, 16,
                    "Current scene slides aside revealing the next",
                    "Smooth horizontal slide with ease in/out",
                    "Adjacent rooms, spatial continuity",
                    "Direction should be consistent with geography"),
    SceneTransition("wipe", 12, 12,
                    "A moving edge replaces scene A with scene B",
                    "Straight horizontal or vertical edge",
                    "Location change, brisk pacing, playful energy",
                    "Keep the wipe gentle, not a hard slash"),
    SceneTransition("page_turn", 20, 20,
                    "Storybook page turn reveal",
                    "Page lifts, crosses, settles",
                    "Storybook-style segments, bookending",
                    "Optional; pairs with storybook framing"),
    SceneTransition("match_cut", 8, 8,
                    "Cut on visual similarity between two scenes",
                    "0 frame match + 8 frame dissolve",
                    "Thematic connection, comparison",
                    "Both frames must share clear visual similarity"),
    SceneTransition("iris_out", 12, 12,
                    "Scene shrinks to a circle, then black",
                    "Circular mask closing",
                    "Character emphasis at segment end",
                    "Hold black 6 frames before next segment"),
    SceneTransition("iris_in", 12, 12,
                    "Scene opens from a circle of black",
                    "Circular mask opening",
                    "Character emphasis at segment start"),
    SceneTransition("cut", 0, 0,
                    "Instant cut with no transition",
                    "None",
                    "Within the same continuous scene",
                    "No cuts faster than 1.5 seconds minimum hold"),
]

# ---------------------------------------------------------------------------
# Stylized physics (Animation/Physics/PHYSICS.md)
# ---------------------------------------------------------------------------

PHYSICS_RULES = [
    PhysicsRule("gravity_strength", "85% of real gravity", "Characters float slightly on jumps"),
    PhysicsRule("jump_arc", "Extended apex hold 4-6 frames", "Gives children time to see the moment"),
    PhysicsRule("fall_speed", "70% of real fall speed", "Never feels dangerous or fast"),
    PhysicsRule("landing", "Soft compression, 2-3 frame cushion", "Knees bend deeply, no hard impact"),
    PhysicsRule("anticipation_crouch", "4 frames before jumps", "Coil before launch is mandatory"),
    PhysicsRule("object_fall", "75% of realistic acceleration (light objects 60%, heavy 80%)",
                "Light paper/leaves, heavy blocks/books"),
    PhysicsRule("ball_bounce", "3 diminishing bounces, 50% height loss each, 18 frames (8+6+4)",
                "Bounce decay: 100% -> 50% -> 25% -> 0% settle"),
    PhysicsRule("character_landing_bounce", "2-3 diminishing vertical bobs, 12 frames (6+4+2)",
                "No infinite bouncing; ease-out up, ease-in down"),
    PhysicsRule("gentle_bump", "Small recoil + blink, 4 frames", "No violent reactions ever"),
    PhysicsRule("walk_into_object", "Stop, look, rub head, smile — 12 frames", "Impact followed by a pause to assess"),
    PhysicsRule("character_collision", "Both bounce apart, sit — 16 frames", "Never flying backward or spin-outs"),
    PhysicsRule("fall_to_ground", "Spread-eagle, 2-frame pause, get up — 24 frames total",
                "Falls are comedic and safe; getting up takes 8-12 frames"),
    PhysicsRule("trip", "Stumble forward, catch balance, recover — 16 frames", "Never fall more than own height"),
    PhysicsRule("slip", "Feet forward, sit, look around, stand — 24 frames", "Falls end sitting, not prone"),
    PhysicsRule("stack_wobble", "Gentle 4-frame oscillation after placement", "Stacks steady up to 8 blocks"),
    PhysicsRule("collapse", "Blocks 'whoosh' apart safely", "No pieces fly aggressively"),
]

CLOTH_ELEMENTS = [
    ClothElement("dresses", 4, "15% of hip swing", 10,
                 "Sway side-to-side with steps; hem arcs gently, settles in 3 bounces"),
    ClothElement("bows", 2, "12% of head movement", 6,
                 "6-frame oscillation loop; rotates opposite head tilt; 1 overshoot on stop"),
    ClothElement("tails", 3, "15% of hip motion (idle 5-8%)", 8,
                 "Gentle S-curve follow path; 2-3 diminishing sways on stop"),
    ClothElement("scarves", 3, "10-15% of primary motion", 10,
                 "Flutter with 2-6 frame delay; consistent wind direction across scene"),
    ClothElement("balloons", 1, "gentle float", 6,
                 "Tug gently on string; never yank; drift upward at idle"),
    ClothElement("hair", 2, "follows head movement", 8,
                 "Swings opposite to head turn; settles within 8-12 frames"),
]

# ---------------------------------------------------------------------------
# Timing & pacing (Animation/Timing/TIMING.md)
# ---------------------------------------------------------------------------

PACING_STANDARDS = [
    PacingStandard("2yr", 1.5, "Slowest — needs 50% more hold time"),
    PacingStandard("3yr", 1.3, ""),
    PacingStandard("4yr", 1.0, "Baseline"),
    PacingStandard("5yr", 0.8, ""),
    PacingStandard("6yr", 0.7, "Still slower than adult"),
    PacingStandard("adult", 0.4, "Reference point only"),
]

SHOT_HOLDS = [
    ShotHold("establishing", 72, "96 (4 sec)", 144),
    ShotHold("wide", 48, "72 (3 sec)", 120),
    ShotHold("medium", 48, "72-96 (3-4 sec)", 144),
    ShotHold("close_up", 36, "48-72 (2-3 sec)", 96),
    ShotHold("over_shoulder", 48, "72 (3 sec)", 120),
    ShotHold("tracking", 72, "96-120 (4-5 sec)", 192),
    ShotHold("two_shot", 48, "72-96 (3-4 sec)", 144),
    ShotHold("group_shot", 72, "96 (4 sec)", 144),
    ShotHold("insert_shot", 36, "48 (2 sec)", 72),
]

REACTION_STANDARDS = [
    ReactionStandard("surprise_event", "8-12 frames", "1-2 seconds"),
    ReactionStandard("funny_moment", "10-14 frames", "2-3 seconds"),
    ReactionStandard("sad_moment", "12-16 frames", "2-4 seconds"),
    ReactionStandard("question_asked", "8-12 frames pause before answer", "2-3 seconds"),
    ReactionStandard("object_appears", "6-10 frames to notice", "1-2 seconds"),
    ReactionStandard("character_enters", "8-12 frames to acknowledge", "1-2 seconds"),
]

ACTION_TIMINGS = [
    ActionTiming("simple_reach", 6, "10-12", "High"),
    ActionTiming("pick_up_object", 8, "12-16", "High"),
    ActionTiming("walk_across_room", 24, "24-48", "High"),
    ActionTiming("jump", 8, "12-16", "High"),
    ActionTiming("fall_down", 12, "16-20", "High"),
    ActionTiming("sit_down", 8, "12-16", "High"),
    ActionTiming("stand_up", 8, "12-16", "High"),
    ActionTiming("turn_head", 4, "6-8", "High"),
    ActionTiming("wave", 8, "12-16", "High"),
    ActionTiming("point", 6, "8-12", "High"),
    ActionTiming("hug", 12, "16-24", "High"),
    ActionTiming("complex_interaction", 16, "20-30", "Medium-High"),
]

EMOTIONAL_BEATS = [
    EmotionalBeat("happiness", "4-6 frames", "1-3 seconds", "8-12 frames"),
    EmotionalBeat("surprise", "2-4 frames", "1-2 seconds", "4-8 frames"),
    EmotionalBeat("sadness", "8-12 frames", "2-4 seconds", "12-16 frames"),
    EmotionalBeat("excitement", "4-6 frames", "2-3 seconds", "8-12 frames"),
    EmotionalBeat("curiosity", "6-8 frames", "2-3 seconds", "8-12 frames"),
    EmotionalBeat("frustration", "8-12 frames", "1-2 seconds", "12-16 frames"),
    EmotionalBeat("fear_mild", "4-8 frames", "1-2 seconds", "8-12 frames"),
    EmotionalBeat("contentment", "6-8 frames", "2-4 seconds", "8-12 frames"),
]

# ---------------------------------------------------------------------------
# Facial transition timing (FACIAL_LIBRARY.md)
# ---------------------------------------------------------------------------

FACIAL_TRANSITIONS = {
    "same_level": 4,
    "one_level": (4, 6),
    "two_levels": (6, 8),
    "three_levels": (8, 10),
    "four_levels": (10, 12),
    "extreme": 12,
}

EXPRESSION_HOLD_STRONG = (12, 24)  # hold levels 4-5 so children register them
RETURN_TO_NEUTRAL_FRAMES = 6  # minimum
