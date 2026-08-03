"""Canonical Phase 5 standards — transcribed verbatim from `Audio/` markdown bibles.

Every value in this module is the machine-readable form of a standard defined
in the Audio bible markdown docs. The `AudioBible.check_docs()` consistency
test keeps the two in sync.
"""

from __future__ import annotations

from .models import (
    AmbientSound, DialogueRule, FoleySound, LipSyncStandard, LocalizationStandard,
    MasteringRule, MixingRule, MusicStyle, PronunciationEntry, SongCategory,
    SongDuration, SongSection, SoundEffect, VoiceProfile,
)

# ---------------------------------------------------------------------------
# Master values
# ---------------------------------------------------------------------------

MASTER_FRAME_RATE = 24
SPEAKING_RATE_WPS = 2.5
TEMP_RANGE = (80, 130)
MASTER_LOUDNESS_LUFS = -14.0
TRUE_PEAK_DBTP = -1.0
MASTER_SAMPLE_RATE = 48000
MASTER_BIT_DEPTH = 24
DEFAULT_KEY = "C major"
DEFAULT_MOOD = "cheerful"

PRIMARY_MUSIC_PLATFORM = "Suno"
SECONDARY_MUSIC_PLATFORM = "ACE-Step Studio"
NARRATOR_ENGINE = "Kokoro"
CHARACTER_ENGINE = "XTTS v2"
OFFLINE_ENGINE = "Piper"

SUPPORTED_LANGUAGES = ("English", "Spanish", "French", "German", "Mandarin", "Japanese")

PHILOSOPHY = (
    "Warm", "Cheerful", "Educational", "Memorable",
    "Positive", "Calm", "Clean", "High energy without being overwhelming",
)

MOOD_WORDS = (
    "cheerful", "playful", "friendly", "cozy", "sunny",
    "bouncy", "gentle", "magical", "adventurous", "peaceful",
)

SIGNATURE_INSTRUMENTATION = (
    "hand claps", "xylophone", "acoustic guitar", "ukulele",
    "piano", "glockenspiel", "light percussion", "soft synth pads",
)

QUALITY_CHECKS = (
    "Matches studio identity",
    "Child-friendly",
    "Clear vocals",
    "Consistent character voice",
    "Pleasant pacing",
    "Balanced mix",
    "High-quality mastering",
    "Reusable stems archived",
    "Proper metadata",
    "Localization-ready",
)

# ---------------------------------------------------------------------------
# Songs
# ---------------------------------------------------------------------------

SONG_CATEGORIES = (
    SongCategory("Alphabet", "Letter names and sounds", "alphabet song about letters", "ABC songs, phonics"),
    SongCategory("Numbers", "Counting and number recognition", "counting song", "Counting songs"),
    SongCategory("Shapes", "Shape names and attributes", "shapes song", "Shape discovery"),
    SongCategory("Colors", "Color names and color mixing", "color song about colors", "Rainbow songs"),
    SongCategory("Animals", "Animal sounds, names, and traits", "animal song", "Animal parade"),
    SongCategory("Transportation", "Vehicles and travel", "transportation song", "Train and car songs"),
    SongCategory("Food", "Foods, cooking, and snacks", "food song", "Nutrition songs"),
    SongCategory("Family", "Family members and love", "family song", "Family songs"),
    SongCategory("Bedtime", "Winding down and sleep", "gentle lullaby", "Lullabies"),
    SongCategory("Morning Routine", "Waking up and getting ready", "morning routine song", "Morning songs"),
    SongCategory("Good Manners", "Please, thank you, sharing", "good manners song", "Etiquette songs"),
    SongCategory("Emotions", "Naming and handling feelings", "emotions song", "Feeling songs"),
    SongCategory("Exercise", "Movement and physical activity", "exercise song", "Wiggle songs"),
    SongCategory("Science", "Nature, discovery, and wonder", "science song", "Experiment songs"),
    SongCategory("Nature", "Plants, weather, outdoors", "nature song", "Garden songs"),
    SongCategory("Space", "Stars, planets, and astronauts", "space song", "Space adventure"),
    SongCategory("Ocean", "Sea creatures and the deep sea", "ocean song", "Under-the-sea songs"),
    SongCategory("Farm", "Farm animals and farm life", "farm song", "On-the-farm songs"),
    SongCategory("Weather", "Sun, rain, snow, seasons", "weather song", "Weather songs"),
    SongCategory("Seasons", "The four seasons", "seasons song", "Season change songs"),
    SongCategory("Holiday Specials", "Celebration and seasonal holidays", "holiday song", "Holiday songs"),
    SongCategory("Birthday Songs", "Birthdays and celebrations", "birthday song", "Birthday dance"),
    SongCategory("Interactive Learning", "Call-and-response and participation", "interactive learning song", "Learning games"),
    SongCategory("Dance Songs", "Movement and dance", "dance song", "Dance party"),
)

SONG_SECTIONS = (
    SongSection("Intro", 1, "Instrumental or short vocal hook; establishes tempo"),
    SongSection("Verse", 2, "Introduces story/idea A"),
    SongSection("Pre-Chorus", 3, "Builds anticipation, repeats lyric hook", optional=True),
    SongSection("Chorus", 4, "Main hook; full energy, most repeated"),
    SongSection("Verse", 5, "Introduces story/idea B"),
    SongSection("Chorus", 6, "Hook repeat (same as section 4)"),
    SongSection("Bridge", 7, "Contrast; new idea or key change", optional=True),
    SongSection("Final Chorus", 8, "Big final hook; often add choir"),
    SongSection("Outro", 9, "Resolution; fade or tag line"),
)

SONG_DURATIONS = (
    SongDuration("Micro", 30, "Intro/outro stingers, transitions, interactive moments"),
    SongDuration("Short", 60, "Single-concept songs, morning routines"),
    SongDuration("Standard", 120, "Default nursery rhymes and educational songs"),
    SongDuration("Feature", 180, "Episode feature songs, holiday specials"),
    SongDuration("Long", 300, "Compilations and specials (assembled from shorter songs)"),
)

CATEGORY_TEMPO = {
    "Alphabet": (100, 120), "Numbers": (100, 120), "Shapes": (90, 110),
    "Colors": (100, 120), "Animals": (90, 120), "Transportation": (110, 130),
    "Food": (90, 110), "Family": (80, 100), "Bedtime": (60, 80),
    "Morning Routine": (100, 120), "Good Manners": (90, 110),
    "Emotions": (80, 110), "Exercise": (110, 130), "Science": (90, 110),
    "Nature": (90, 110), "Space": (100, 120), "Ocean": (90, 110),
    "Farm": (100, 120), "Weather": (90, 110), "Seasons": (90, 110),
    "Holiday Specials": (100, 120), "Birthday Songs": (100, 120),
    "Interactive Learning": (90, 110), "Dance Songs": (110, 130),
}

MUSIC_STYLE = MusicStyle(
    tempo_min=TEMP_RANGE[0],
    tempo_max=TEMP_RANGE[1],
    moods=MOOD_WORDS,
    keys=("C major", "G major", "F major", "D major"),
    melody="Simple melodies, strong repetition, easy to sing",
    arrangement="Simple warm harmony, bright instrumentation, no harsh or complex arrangements",
    instrumentation=SIGNATURE_INSTRUMENTATION,
    vocals=("Female lead vocal", "Children's choir", "Male lead vocal for specific characters"),
)

# ---------------------------------------------------------------------------
# Voice profiles
# ---------------------------------------------------------------------------

VOICE_PROFILES = (
    VoiceProfile(
        character="Lily Bunny", age="5 years (preschool, 4-5)", pitch="Medium-high",
        energy="Playful", speech_speed="Medium", accent="Neutral", laugh_style="Soft",
        singing_style="Bright", favorite_expressions=("Giggles", 'cheerful "Wow!"'),
        tts_engine=CHARACTER_ENGINE,
    ),
    VoiceProfile(
        character="Ben Bear", age="5 years (preschool)", pitch="Medium-low, warm",
        energy="Calm", speech_speed="Slow", accent="Neutral", laugh_style="Deep, hearty",
        singing_style="Warm", favorite_expressions=('"Yummy!"', 'gentle "Hmm?"'),
        tts_engine=CHARACTER_ENGINE,
    ),
    VoiceProfile(
        character="Daisy Duck", age="5 years (preschool)", pitch="High, bright",
        energy="Cheerful", speech_speed="Fast", accent="Neutral", laugh_style="Quacky giggle",
        singing_style="Chirpy", favorite_expressions=('"Quack quack!"', '"So fancy!"'),
        tts_engine=CHARACTER_ENGINE,
    ),
    VoiceProfile(
        character="Charlie Fox", age="5 years (preschool)", pitch="Medium-high",
        energy="Energetic", speech_speed="Fast", accent="Neutral", laugh_style="Mischievous",
        singing_style="Sly, playful", favorite_expressions=('"Hehe, watch this!"',),
        tts_engine=CHARACTER_ENGINE,
    ),
    VoiceProfile(
        character="Mommy Bunny", age="Adult (30s)", pitch="Medium, warm",
        energy="Calm", speech_speed="Slow-medium", accent="Neutral", laugh_style="Gentle",
        singing_style="Sweet", favorite_expressions=('"Oh dear!"', '"Well done!"'),
        tts_engine=CHARACTER_ENGINE,
    ),
    VoiceProfile(
        character="Daddy Bunny", age="Adult (30s)", pitch="Medium-low",
        energy="Playful", speech_speed="Medium", accent="Neutral", laugh_style="Big, warm",
        singing_style="Cheerful", favorite_expressions=('"Story time!"', '"Hoppity-hop!"'),
        tts_engine=CHARACTER_ENGINE,
    ),
    VoiceProfile(
        character="Grandma Bunny", age="Elderly", pitch="Low, soft",
        energy="Gentle", speech_speed="Slow", accent="Neutral", laugh_style="Soft, warm",
        singing_style="Tender", favorite_expressions=('"Oh my!"', '"Sit by me"'),
        tts_engine=CHARACTER_ENGINE,
    ),
    VoiceProfile(
        character="Grandpa Bunny", age="Elderly", pitch="Low",
        energy="Calm", speech_speed="Slow", accent="Neutral", laugh_style="Rusty chuckle",
        singing_style="Humming", favorite_expressions=('"Good gravy!"', '"Aha!"'),
        tts_engine=CHARACTER_ENGINE,
    ),
    VoiceProfile(
        character="Baby Bunny", age="Toddler (2-3)", pitch="High",
        energy="Bouncy", speech_speed="Slow", accent="Neutral", laugh_style="Baby giggle",
        singing_style="Babble", favorite_expressions=('"Boo!"', '"Mine!"'),
        tts_engine=CHARACTER_ENGINE,
    ),
    VoiceProfile(
        character="Teacher Owl", age="Adult (40s)", pitch="Medium, clear",
        energy="Wise", speech_speed="Slow-medium", accent="Neutral", laugh_style="Soft hoot",
        singing_style="Melodic", favorite_expressions=('"Who, who?"', '"Excellent question!"'),
        tts_engine=CHARACTER_ENGINE,
    ),
    VoiceProfile(
        character="Narrator", age="Adult", pitch="Warm medium",
        energy="Gentle", speech_speed="Calm", accent="Neutral", laugh_style="Soft",
        singing_style="N/A", favorite_expressions=("Storybook cadence",),
        tts_engine=NARRATOR_ENGINE, role="narrator",
    ),
)

# ---------------------------------------------------------------------------
# Dialogue / pronunciation
# ---------------------------------------------------------------------------

DIALOGUE_RULES = (
    DialogueRule("Short sentences", "Sentences stay short", "One idea per sentence; 5-8 words typical"),
    DialogueRule("Simple vocabulary", "Preschool vocabulary", "Words a 2-6 year old already knows"),
    DialogueRule("Clear pronunciation", "Fully articulated words", "No slurring, no swallowed endings"),
    DialogueRule("Frequent repetition", "Key words/phrases repeated", "Repeat the learning word 3+ times"),
    DialogueRule("Positive tone", "Warm and encouraging", "Never scolding or mean"),
    DialogueRule("Age-appropriate pacing", "Slow-medium, calm", "~2.5 words per second speaking rate"),
    DialogueRule("No sarcasm", "Never sarcastic", "Children interpret literally"),
    DialogueRule("No complex idioms", "Avoid idioms entirely", '"It is raining cats and dogs" is forbidden'),
)

PRONUNCIATIONS = (
    PronunciationEntry("Lily Bunny", "LIL-ee BUN-ee", "Stress on first syllable of each word"),
    PronunciationEntry("Ben Bear", "BEN BARE", "Flat 'a' like 'bear'"),
    PronunciationEntry("Daisy Duck", "DAY-zee DUK", "Soft 'z'"),
    PronunciationEntry("Charlie Fox", "CHAR-lee FOKS", "'Ch' as in 'chair'"),
    PronunciationEntry("Mommy Bunny", "MOM-ee BUN-ee", "Warm, unstressed first syllable"),
    PronunciationEntry("Daddy Bunny", "DAD-ee BUN-ee", "Warm, unstressed first syllable"),
    PronunciationEntry("Grandma Bunny", "GRAN-ma BUN-ee", "'Ma' not 'maw'"),
    PronunciationEntry("Grandpa Bunny", "GRAN-pa BUN-ee", "'Pa' not 'paw'"),
    PronunciationEntry("Baby Bunny", "BAY-bee BUN-ee", "Bouncy 'bay'"),
    PronunciationEntry("Teacher Owl", "TEE-cher OWL", "'Owl' one syllable"),
    PronunciationEntry("Little Learning Town", "LIT-ul LURN-ing TOWN", "Gentle 't' in 'little'"),
    PronunciationEntry("Sunny Garden Playground", "SUN-ee GAR-den PLAY-ground", "Bright, crisp"),
    PronunciationEntry("Rainbow Hill", "RAIN-bo HILL", "'Rain' as in weather"),
    PronunciationEntry("Meadow Lane", "MED-o LANE", "Soft 'e'"),
    PronunciationEntry("Bubble Brook", "BUB-ul BRUK", "Double-bounce on 'bubble'"),
    PronunciationEntry("Fluffy the Bunny", "FLUF-ee the BUN-ee", "Lily's stuffed animal"),
    PronunciationEntry("Carrot Cupcake", "KARE-ut KUP-cake", "'T' softened"),
    PronunciationEntry("Hoppity Hop", "HOP-ih-tee HOP", "Bouncy rhythm"),
    PronunciationEntry("Magic Sparkle", "MA-jik SPAR-kul", "Gentle 'spar'"),
)

# ---------------------------------------------------------------------------
# Sound libraries
# ---------------------------------------------------------------------------

SOUND_EFFECTS = (
    SoundEffect("Footsteps", "Soft padded steps", "Gentle, no stomping"),
    SoundEffect("Running", "Quick soft footfalls", "Playful energy, never urgent"),
    SoundEffect("Jumping", "Single hop with soft landing", "Matches the 12-frame jump cycle"),
    SoundEffect("Clapping", "Bright hand claps", "Cheerful, light"),
    SoundEffect("Door", "Soft creak and click", "Friendly, no slam"),
    SoundEffect("Page Turn", "Paper swish", "Book-friendly"),
    SoundEffect("Water Splash", "Gentle splash", "Playful, no panic"),
    SoundEffect("Birds", "Cheerful chirps", "Morning ambience"),
    SoundEffect("Dog Bark", "Warm single bark", "Friendly, not scary"),
    SoundEffect("Cat Meow", "Soft meow", "Sweet"),
    SoundEffect("Duck Quack", "Bright quack", "Playful"),
    SoundEffect("Cow Moo", "Gentle low moo", "Calm"),
    SoundEffect("Train", 'Distant "choo-choo"', "Toy-like"),
    SoundEffect("Airplane", "Soft engine hum", "Soaring, gentle"),
    SoundEffect("Wind", "Gentle breeze", "Airy"),
    SoundEffect("Rain", "Light patter", "Cozy"),
    SoundEffect("Thunder (soft)", "Rumbled low roll", "Never startling"),
    SoundEffect("Bell", "Bright chime", "Clean tone"),
    SoundEffect("School Bell", "Cheerful two-tone bell", "Inviting"),
    SoundEffect("Toy Sounds", "Plastic squeaks and clicks", "Playful"),
    SoundEffect("Blocks", "Wooden clacks", "Stacking sounds"),
    SoundEffect("Piano", "Bright single notes", "Melodic"),
    SoundEffect("Xylophone", "Sparkling mallet notes", "Signature instrument"),
    SoundEffect("Bubbles", "Soft pops", "Magical"),
    SoundEffect("Magic Sparkle", "Twinkly chime", "Wonder moment"),
    SoundEffect("Applause", "Gentle clapping", "Encouraging"),
    SoundEffect("Laughter", "Warm child giggles", "Genuine, soft"),
)

FOLEY_SOUNDS = (
    FoleySound("Book opening", "Soft cover lift and page slide", "Gentle"),
    FoleySound("Book closing", "Quiet cover settle", "Soft thump"),
    FoleySound("Chair movement", "Light scuff and glide", "No screech"),
    FoleySound("Table tap", "Small wooden tap", "Friendly"),
    FoleySound("Toy pickup", "Soft grip and lift", "Plush"),
    FoleySound("Toy drop", "Light, muffled drop", "Never heavy"),
    FoleySound("Ball bounce", "Three diminishing bounces (8+6+4 frames)", "Matches physics"),
    FoleySound("Paper crumple", "Quiet crinkle", "Playful"),
    FoleySound("Backpack zipper", "Smooth zip and click", "Satisfying"),
    FoleySound("Pencil writing", "Soft scratchy strokes", "Calm"),
    FoleySound("Paint brush", "Gentle bristle sweeps", "Creative"),
    FoleySound("Building blocks", "Wooden clack and stack", "Bright"),
)

AMBIENT_SOUNDS = (
    AmbientSound("Bedroom", "Soft quiet, gentle hum, distant clock", "Very low"),
    AmbientSound("Kitchen", "Light clinks, soft simmer, faint fridge", "Low"),
    AmbientSound("Playground", "Distant children, gentle squeaks", "Low"),
    AmbientSound("Forest", "Leaves rustling, birdsong, breeze", "Low"),
    AmbientSound("Beach", "Soft waves, distant gulls", "Low"),
    AmbientSound("Farm", "Cows mooing far off, rooster, wind", "Low"),
    AmbientSound("School", "Soft chatter, bell echoes, pencils", "Low"),
    AmbientSound("Library", "Hushed silence, page turns", "Very low"),
    AmbientSound("Rain", "Steady light rain, window patter", "Low"),
    AmbientSound("Snow", "Muffled quiet, soft gusts", "Very low"),
    AmbientSound("Night", "Crickets, gentle wind, calm", "Very low"),
    AmbientSound("Morning Birds", "Cheerful dawn chorus, soft light", "Low"),
)

# ---------------------------------------------------------------------------
# Mix / master / lipsync / localization
# ---------------------------------------------------------------------------

MIXING_RULES = (
    MixingRule("Dialogue priority", "Dialogue always takes priority"),
    MixingRule("Vocal clarity", "Vocals remain intelligible over music"),
    MixingRule("SFX support", "Sound effects should support, not distract"),
    MixingRule("Consistent loudness", "Maintain consistent loudness across episodes"),
    MixingRule("No spikes", "Avoid sudden volume spikes"),
)

MIX_HIERARCHY = (
    ("Dialogue / Narration", "0 dB reference"),
    ("Lead Vocals", "-3 to -6 dB"),
    ("Music Bed", "-12 to -18 dB"),
    ("Choir / Backing", "-10 to -14 dB"),
    ("SFX", "-6 to -12 dB"),
    ("Foley", "-6 to -12 dB"),
    ("Ambience", "-18 to -24 dB"),
)

MASTERING_RULES = (
    MasteringRule("Consistent loudness", "-14 LUFS integrated"),
    MasteringRule("Clean peaks", "True peak never exceeds -1.0 dBTP"),
    MasteringRule("Warm tone", "Gentle high-frequency roll-off, no harshness"),
    MasteringRule("No clipping", "Never clip on purpose"),
    MasteringRule("Dialogue focus", "Mastering preserves dialogue clarity"),
    MasteringRule("No spikes", "No sudden loudness changes anywhere in the episode"),
)

LIPSYNC_STANDARDS = (
    LipSyncStandard("Same timing reference", "Audio and animation share one timecode (24 fps)"),
    LipSyncStandard("Standardize phoneme timing", "4-6 frames per phoneme (Phase 4 mouth library)"),
    LipSyncStandard("Consistent mouth shapes", "Recurring sounds always map to the same mouth shape"),
    LipSyncStandard("Dialogue pacing", "~2.5 words per second speaking rate"),
    LipSyncStandard("Word pause", "6-8 frames between words"),
    LipSyncStandard("Sentence pause", "12-18 frames between sentences"),
)

LOCALIZATION_STANDARDS = (
    LocalizationStandard("Multiple languages", "Every deliverable is language-tagged"),
    LocalizationStandard("Alternate voice casts", "Localized voices replace the primary cast without retraining"),
    LocalizationStandard("Localized songs", "Lyrics and vocals re-recorded per locale"),
    LocalizationStandard("Localized subtitles", "Timed text in every language"),
    LocalizationStandard("Region-specific pronunciations", "Pronunciations differ per region"),
    LocalizationStandard("Keep music stems", "Music stems kept so vocals can be replaced without recreating the song"),
)
