# AI Prompt Templates

## Purpose

These prompt templates are used to invoke AI models for specific Story Engine tasks. Each template is designed for a single responsibility, ensuring consistent, structured outputs that feed cleanly into the next engine layer.

---

## 1. Planning Prompt Template

**Purpose:** Generate a complete episode plan from curriculum to validation.

```
Create a preschool educational episode for [TARGET_AGE]-year-old children.

Curriculum Area: [AREA]
Learning Objective: [OBJECTIVE_ID — DESCRIPTION]
Theme: [THEME]
Target Age: [AGE]

Characters:
  Main: [CHARACTER]
  Supporting: [CHARACTERS]
  Teacher/Parent: [CHARACTER] (if applicable)

Location: [LOCATION]
Season: [SEASON]
Weather: [WEATHER]

Requirements:
  - Include one gentle, child-friendly problem
  - Include [NUMBER] interactive audience moments
  - Include one short song placement ([SONG_TYPE])
  - End with a positive resolution that reinforces the learning objective
  - Use age-appropriate vocabulary ([VOCAB_LEVEL])
  - Maximum [DURATION] minutes running time
  - Grammar pattern: [GRAMMAR_PATTERN]

Output the episode plan as a structured blueprint with:
  Episode Title, Description, Characters, Environment, Required Assets,
  Scene Outline, Conflict, Resolution, Learning Moments,
  Interactive Moments, Song Placement, Emotional Arc, Metadata
```

---

## 2. Curriculum Prompt Template

**Purpose:** Generate a sequence of lessons across multiple episodes.

```
Generate a sequence of [NUMBER] preschool lessons for the [CURRICULUM_AREA] curriculum area.

Target Age: [AGE_RANGE]
Difficulty Range: [LEVEL_START] to [LEVEL_END]

Requirements:
  - Gradually increase in difficulty
  - No repeating themes or locations excessively
  - Each lesson has one clear learning objective
  - Lessons should build on previous knowledge
  - Include variety in teaching approach (song, play, story, activity)

For each lesson provide:
  Lesson ID, Learning Objective, Suggested Theme, Difficulty Level,
  Key Vocabulary, Brief Description, Prerequisite Knowledge

Ensure balanced coverage across [NUMBER] episodes without repetition.
```

---

## 3. Character Selection Prompt Template

**Purpose:** Select appropriate characters for an episode.

```
Select characters for a preschool episode with the following parameters:

Learning Objective: [OBJECTIVE]
Theme: [THEME]
Location: [LOCATION]
Target Age: [AGE]

Available characters:
  [LIST ALL CHARACTERS WITH THEIR AGES, PERSONALITIES, AND RELATIONSHIPS]

Rules:
  - Main character should connect naturally to the learning objective
  - Maximum [MAX_CHARACTERS] characters total
  - Include at least one supporting character for social interaction
  - Include an adult character if the objective requires teaching
  - Respect established relationships (use continuity data)
  - Avoid overcrowding — young children follow fewer characters

Recent character usage (last 5 episodes):
  [RECENT_CASTING_DATA]

Select: Main Character, Supporting Characters (1-2), Adult (if needed),
        Background Characters (list only)
```

---

## 4. Dialogue Generation Prompt Template

**Purpose:** Write age-appropriate dialogue for each scene.

```
Write dialogue for a preschool educational episode.

Episode: [TITLE]
Learning Objective: [OBJECTIVE]
Characters:
  [CHARACTER 1] — Age [AGE], Personality: [TRAITS], Voice: [VOICE_DESCRIPTION]
  [CHARACTER 2] — Age [AGE], Personality: [TRAITS], Voice: [VOICE_DESCRIPTION]
  [CHARACTER 3] — Age [AGE], Personality: [TRAITS], Voice: [VOICE_DESCRIPTION]

Scene: [SCENE_NUMBER — SCENE_TYPE — SCENE_PURPOSE]
Setting: [LOCATION_DESCRIPTION]

Dialogue Rules:
  - Short sentences (max [MAX_WORDS] words)
  - Simple grammar, active voice, present tense
  - Positive tone throughout
  - No sarcasm, slang, or abstract concepts
  - Key vocabulary "[KEY_TERM]" must appear [MIN_APPEARANCES] times naturally
  - Include [NUMBER] interactive moments directed at the audience
  - Character dialogue must match established voice patterns

Scene emotional state: [EMOTION]
Previous scene ended with: [PREVIOUS_STATE]
Next scene begins with: [NEXT_STATE]

Output:
  Scene direction (2-3 sentences)
  Character: "Dialogue line."
  [INTERACTIVE] Audience prompt (with pause note)
  Narration: "Narration text."
```

---

## 5. Song Planning Prompt Template

**Purpose:** Determine song placement and type.

```
Determine song requirements for a preschool episode.

Episode: [TITLE]
Learning Objective: [OBJECTIVE_ID — DESCRIPTION]
Theme: [THEME]
Target Age: [AGE]
Episode Duration: [MINUTES] minutes
Episode Type: [STORY / EDUCATIONAL_SONG / DANCE / ROUTINE / ADVENTURE]

Previous episode had a song: [YES/NO] — [SONG_TYPE if yes]

Criteria for inclusion:
  - Does the learning objective benefit from musical reinforcement? [YES/NO]
  - Is the episode type suitable for a song? [YES/NO]
  - Is the target age receptive to music in this context? [YES/NO]
  - Would a song disrupt the narrative flow? [YES/NO]

If song is recommended:
  - Song type: [OPENING / MIDDLE / ENDING / TRANSITION / DANCE / LULLABY]
  - Position: [Which scene / beat]
  - Duration: [SECONDS] seconds
  - Style: [UPBEAT / GENTLE / ENERGETIC / CALM / RHYTHMIC]
  - Interactive elements: [ACTIONS / CALL-AND-RESPONSE / REPETITION]
  - Key vocabulary to include: [WORDS]
  - Learning connection: [How the song reinforces the objective]

If song is not recommended, explain why.
```

---

## 6. Validation Prompt Template

**Purpose:** Validate an episode against all quality checks.

```
Validate the following preschool episode against the Story Engine quality standards.

Episode Blueprint:
  Title: [TITLE]
  Learning Objective: [OBJECTIVE_ID — DESCRIPTION]
  Theme: [THEME]
  Characters: [CHARACTERS]
  Location: [LOCATION]
  Target Age: [AGE]
  Duration: [MINUTES]

Validation Checks:
  1. Educational Objective: Is the objective clearly present, taught, practiced, and recapped?
  2. Positive Ending: Does the episode end positively with no unresolved problems?
  3. Character Consistency: Do all characters match their established personalities and relationships?
  4. World Consistency: Does the location and environment match established canon?
  5. Asset Availability: Are all required props listed and available?
  6. Lesson Repetition: Does the key concept appear 4-6 times naturally?
  7. Safe Content: Is the episode free of all forbidden content? (violence, bullying, politics, religion, horror, death, crime, weapons, alcohol, drugs, dangerous behavior)
  8. Age-Appropriate Vocabulary: Do sentence length and word complexity match target age?
  9. Interaction Moments: Is there at least one audience interaction per scene?
  10. Song Placement: Is the song appropriate for the learning objective and narrative flow?
  11. Continuity: Does the episode avoid contradicting established canon?
  12. Diversity: Does this episode differ sufficiently from the last 3 episodes?

For each check: PASS or FAIL with explanation.
Overall: PASS (all checks pass) or FAIL (any check fails).
If FAIL, list specific items to fix.
```

---

## 7. Story Grammar Assignment Prompt Template

**Purpose:** Assign the optimal grammar pattern for an episode.

```
Select a story grammar pattern for a preschool episode.

Learning Objective: [OBJECTIVE]
Theme: [THEME]
Main Character: [CHARACTER]
Target Age: [AGE]

Available grammar patterns:
  1. Find Something     — Character searches for a missing item
  2. Learn Something    — Character learns a new concept
  3. Help Someone       — Character helps a friend in need
  4. Build Something    — Character builds or creates something
  5. Visit Somewhere    — Character explores a new place
  6. Celebrate Something — Characters celebrate together
  7. Clean Something    — Characters clean and organize
  8. Count Something    — Characters count objects
  9. Sort Something     — Characters sort items by attribute
  10. Grow Something    — Characters plant and nurture
  11. Sing Together     — Characters sing as a group
  12. Dance Together    — Characters dance and move
  13. Adventure Together — Characters go on an imaginary journey
  14. Solve a Puzzle    — Characters solve a mystery

Last 3 grammar patterns used: [PATTERNS]

Select the best grammar pattern. Explain why it fits the learning objective,
theme, and character. Do not repeat a pattern from the last 2 episodes.
```

---

## 8. Episode Title Generation Prompt Template

**Purpose:** Generate a title for the episode.

```
Generate an episode title for a preschool show.

Main Character: [CHARACTER]
Learning Objective: [OBJECTIVE_DESCRIPTION]
Theme: [THEME]
Grammar Pattern: [PATTERN]

Title patterns to consider:
  - [Character] [Action] [Concept] — "Lily Bunny Learns to Share"
  - [Character]'s [Adventure] — "Ben Bear's Blue Day"
  - The [Adjective] [Noun] — "The Colorful Kite"
  - Let's [Action] [Something] — "Let's Count Together"
  - [Character] and the [Item] — "Daisy Duck and the Missing Cookie"

Rules:
  - 3-6 words maximum
  - Include the main character name when possible
  - No negative words
  - Clear, simple, descriptive
  - Age-appropriate language

Generate 3 title options with brief rationale for each.
```

---

## Prompt Usage Guidelines

| Rule | Explanation |
|---|---|
| One prompt per task | Do not combine multiple tasks in one prompt |
| Provide context | Include relevant continuity data in the prompt |
| Specify output format | Tell the model exactly how to structure its response |
| Include constraints | Always mention age, vocabulary, and safety rules |
| Iterate if needed | Low-quality output → refine the prompt, retry |
| Validate output | Always run validation on generated content |
| No prompt chaining | Do not feed one prompt's output directly into another prompt without validation |
