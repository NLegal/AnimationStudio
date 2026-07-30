# Story Validation Engine Guide

## Purpose

The Story Validation Engine is the **quality gate** of the Story Engine. Every episode must pass validation before it moves forward to production. The engine automatically verifies that the episode meets all educational, safety, consistency, and quality standards.

---

## Validation Checks

Every episode is checked against these validation rules:

### 1. Educational Objective Present

| Check | Description |
|---|---|
| Objective assigned | Episode has a learning objective ID from the Learning Objectives library |
| Objective is valid | ID exists in the library and is not deprecated |
| Objective is taught | The concept appears explicitly in the teaching scene |
| Objective is practiced | The concept is reinforced in the practice scene |
| Objective is recapped | The concept is mentioned in the goodbye or celebration |
| Appropriate difficulty | Difficulty level matches target age |

**Fail if:** No objective assigned, objective not taught, or objective contradicted.

### 2. Positive Ending

| Check | Description |
|---|---|
| Resolution is positive | Episode ends with success, joy, or warm feeling |
| No negative conclusions | Problem is fully resolved |
| Characters are happy | All main characters end in a positive state |
| Lesson is reinforced | Final moments connect to learning |
| Audience is addressed | Goodbye includes audience |

**Fail if:** Episode ends negatively, problem unresolved, characters sad.

### 3. Character Consistency

| Check | Description |
|---|---|
| Characters exist | All characters are from the established cast |
| Personalities match | Dialogue matches character voice patterns |
| Relationships are correct | No contradictions with established relationships |
| Catchphrases respected | Characters use their established catchphrases if any |
| Physical traits accurate | Character descriptions match canon |
| No overcrowding | Maximum 4 main characters per episode (ages 2-3) or 6 (ages 4-6) |

**Fail if:** Non-existent character used, personality contradicts canon, relationship error.

### 4. World Consistency

| Check | Description |
|---|---|
| Location exists | Location is from the established world library |
| Location is correct | Physical description matches canon |
| Season matches location | No snow at the beach (unless special theme) |
| Weather is realistic | Weather matches season and location |
| Time of day appropriate | Bedtime routines happen at night, etc. |

**Fail if:** Invalid location, contradictory environment details.

### 5. Asset Availability

| Check | Description |
|---|---|
| Required assets listed | All props needed for the episode are in the asset list |
| Assets exist | Each asset is in the production library |
| Assets match theme | Asset list is appropriate for the selected theme |
| No missing props | Any prop mentioned in dialogue is in the asset list |

**Fail if:** Required asset missing from list, asset doesn't exist in library.

### 6. Lesson Repetition

| Check | Description |
|---|---|
| Key term appears | Learning objective term appears 4-6 times |
| Natural repetition | Repetition feels organic, not forced |
| Multiple contexts | Concept shown in at least 3 different examples |
| Audience practice | Audience is prompted to use the concept |
| Reinforcement spacing | Repetition is spread across the episode, not clustered |

**Fail if:** Key term appears fewer than 3 times, only one example shown.

### 7. Safe Content

| Check | Description |
|---|---|
| No violence | No physical aggression, hitting, pushing |
| No bullying | No teasing, exclusion, name-calling |
| No politics | No political references of any kind |
| No religion | No religious content or references |
| No horror | No scary elements, dark themes, monsters |
| No death | No death, dying, or loss themes |
| No crime | No stealing, lying, or illegal activity |
| No weapons | No weapons of any kind |
| No alcohol/drugs | No substance references |
| No dangerous behavior | No jumping from heights, touching hot surfaces, etc. |
| No medical misinformation | No incorrect health advice |
| Safe imitation | Children should not be encouraged to imitate dangerous acts |

**Fail if:** Any unsafe content detected. Zero tolerance.

### 8. Age-Appropriate Vocabulary

| Check | Description |
|---|---|
| Word complexity matches age | Vocabulary level aligns with target age |
| Sentence length appropriate | Sentences are within length limits |
| Concepts are concrete | No abstract concepts beyond age understanding |
| Instructions are clear | Interactive prompts are age-appropriate |

**Fail if:** Vocabulary too complex for target age, sentences too long.

### 9. Interaction Moments

| Check | Description |
|---|---|
| Minimum interactions met | At least 1 interaction per scene |
| Pause timing indicated | Script notes where pauses occur |
| Variety of interaction types | Not the same type every time |
| Age-appropriate interactions | Physical interactions match motor development |

**Fail if:** No interactions, or only one type used.

### 10. Song Placement

| Check | Description |
|---|---|
| Song is appropriate | Song type matches learning objective |
| Song placement is logical | Position in episode makes narrative sense |
| No consecutive songs | Previous episode did not have a song (unless intended) |
| Song has purpose | Song supports the learning objective |
| Duration within limits | Song length is age-appropriate |

**Fail if:** Song interrupts narrative flow, no clear purpose, or duration wrong.

### 11. Continuity

| Check | Description |
|---|---|
| No repeated episode title | Title not used before |
| No repeated plot | Story not identical to previous episodes |
| Character state correct | Character hasn't used same item / been to same place recently |
| Location diversity | Location not used in the last 3 episodes |
| Learning objective diversity | Same objective not used in the last 5 episodes |

**Fail if:** Duplicate or near-duplicate of recent episode.

---

## Safety Rules

The following content is **permanently forbidden** in all episodes:

```
✗ Violence               —  No hitting, pushing, fighting
✗ Bullying               —  No teasing, exclusion, mean words
✗ Politics               —  No political figures, parties, or issues
✗ Religion               —  No religious content, figures, or practices
✗ Scary horror           —  No monsters, ghosts, dark threats
✗ Death                  —  No death, dying, or permanent loss
✗ Crime                  —  No stealing, lying, cheating
✗ Weapons                —  No guns, knives, or any weapons
✗ Alcohol / Drugs        —  No substance references
✗ Gambling               —  No games of chance for stakes
✗ Dangerous behavior     —  No imitation-risk activities
✗ Medical misinformation —  No incorrect health or safety advice
✗ Unsafe imitation       —  Nothing children could harm themselves copying
```

Always prioritize child safety.

---

## Continuity Rules

The Story Engine must remember and never contradict:

- Character personalities
- Favorite foods
- Favorite toys
- Homes and addresses
- Relationships between characters
- Pets and their names
- Recurring jokes
- Catchphrases
- World geography
- Recurring locations

---

## Diversity Rules

To prevent repetitive episodes, the engine tracks:

| Category | Tracked Elements | Rule |
|---|---|---|
| Locations | Specific places visited | No reuse within 3 episodes |
| Characters | Main character assignment | Rotate main character duty |
| Songs | Song types used | No same song type twice in a row |
| Lessons | Learning objectives taught | No repeat within 5 episodes |
| Props | Key items used | Rotate through prop library |
| Activities | What characters do | Vary across episodes |
| Weather | Weather conditions | No same weather 3 episodes straight |
| Seasons | Seasonal settings | Match real-world season progression |
| Themes | Theme selection | No same theme twice in a season |
| Grammar patterns | Story structures | No same grammar back-to-back |

---

## QC Checklist

Every generated episode must satisfy all of the following:

```
□ One clear educational objective
□ One primary theme
□ Appropriate character count (2-4 for ages 2-3, 2-6 for ages 4-6)
□ Correct locations (matches world canon)
□ Correct assets (all required props listed)
□ Positive emotional arc (curiosity → joy)
□ Audience participation included (interaction in every scene)
□ Vocabulary matches target age (sentence length, word complexity)
□ Safe conflict (mild, child-friendly problem)
□ Positive resolution (problem fully resolved, happy ending)
□ Song opportunity identified (if appropriate)
□ Continuity maintained (no canon contradictions)
□ Variety maintained across recent episodes (diversity check passed)
□ Validation passed (all checks green)
```

Only validated stories move forward to production.
