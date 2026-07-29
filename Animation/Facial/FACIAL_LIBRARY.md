# Facial Animation Library

## Introduction

Facial acting is the emotional core of every Animation Studio production. For preschool audiences, the face is the primary channel through which children understand how a character feels. Clear, readable expressions build empathy and emotional literacy — a smiling Bunny tells the child "this is a happy moment" before a single word is spoken.

This library standardizes every expression across the studio, ensuring consistent emotional communication regardless of which animator or AI model produces the shot.

---

## Expression Intensity Scale

Every emotion is rated on a 1–5 scale where:

| Level | Name     | Visible Cues                                              |
|-------|----------|-----------------------------------------------------------|
| 1     | Trace    | Barely perceptible, micro-expression                       |
| 2     | Mild     | Noticeable but restrained                                  |
| 3     | Moderate | Clear, readable expression                                 |
| 4     | Strong   | Exaggerated, obvious to a child                            |
| 5     | Maximum  | Extreme expression (still child-safe, never frightening)   |

---

## Standardized Smile Levels

Smiles are the most frequently used expression and must be consistent.

| Level | Name       | Description                                                       |
|-------|------------|-------------------------------------------------------------------|
| 1     | Micro-smile | Tiny upward curl at corners of mouth, neutral eyes, subtle        |
| 2     | Warm smile  | Gentle curve, slight eye crinkle at outer corners (Duchenne), soft |
| 3     | Big smile   | Mouth open, teeth visible (upper row), eyes happy/ squinted       |
| 4     | Huge grin   | Mouth wide, teeth fully visible, eyes squeezed, cheeks pushed up  |
| 5     | Ecstatic    | Mouth open wide (may show tongue), eyes bright/arched, eyebrows up, cheeks fully raised |

---

## Standardized Eye Openness

Controls perceived alertness and energy.

| Level | Name         | Description                        | Usage                            |
|-------|--------------|------------------------------------|----------------------------------|
| 1     | Closed       | Eyelids fully shut                 | Sleep, blink, eyes squeezed shut |
| 2     | Half-lidded  | Eyelid covers top half of iris     | Tired, relaxed, sleepy           |
| 3     | Normal       | Iris fully visible, natural        | Default, conversation, idle      |
| 4     | Slightly wide | White visible above iris           | Curiosity, mild surprise, alert  |
| 5     | Fully open   | Large whites all around iris       | Surprise, shock, excitement      |

---

## Eyebrow Positions

Eyebrows drive expression recognition as much as the mouth.

| Position       | Description                                    | Emotion Cue                    |
|----------------|------------------------------------------------|--------------------------------|
| Neutral        | Natural resting position                       | Default, listening             |
| Raised         | Arched upward, center lifts                    | Surprise, excitement, fear     |
| Lowered        | Pulled down and slightly together              | Anger, frustration, confusion  |
| One raised     | One brow up, one neutral                       | Curiosity, skepticism          |
| Knit           | Pulled together and down toward center         | Worry, concentration, sadness  |
| Arched         | Gentle upward curve across both                | Happiness, warmth              |
| Sad tilt       | Inner corners angled up, outer down            | Sadness, disappointment        |

---

## Lip Shapes

| Shape        | Description                                   | Used For                 |
|--------------|-----------------------------------------------|--------------------------|
| Closed smile | Lips together, corners up                     | Contentment, greeting    |
| Open smile   | Lips apart, teeth showing                     | Happy, laughing          |
| 'O' shape    | Lips rounded into circle                      | Surprise, "oh" sound     |
| Pursed       | Lips pressed together tightly                 | Disgust, thinking        |
| Pout         | Lower lip pushed forward, corners down        | Sadness, pleading        |
| Wide         | Lips stretched horizontally                   | "E" sounds, fear         |
| Asymmetric   | One side higher than the other                | Sarcasm, wry amusement   |
| Puckered     | Lips gathered forward                         | Kiss, "oo" sound         |
| Flat line    | Straight horizontal line                      | Neutral, anger           |

---

## Emotion Definitions

### Happiness

| Intensity | Name        | Face                                                                 |
|-----------|-------------|----------------------------------------------------------------------|
| 1         | Content     | Gentle closed smile, neutral eyes, relaxed brows                     |
| 2         | Pleased     | Warm smile, slight eye crinkle, soft raised brows                    |
| 3         | Happy       | Open smile with teeth, eyes squinted, brows arched, cheeks up        |
| 4         | Delighted   | Wide grin, eyes squeezed, head may tilt back slightly                |
| 5         | Ecstatic    | Mouth open wide, bright eyes (level 4), brows high, whole face lit  |

### Sadness

| Intensity | Name          | Face                                                                 |
|-----------|---------------|----------------------------------------------------------------------|
| 1         | Down          | Slight frown, eyes slightly lower, brows neutral                     |
| 2         | Disappointed  | Clear frown, eyes downcast, sad tilt brows                           |
| 3         | Sad           | Full frown, lower eyelids rise, brows knit inner up, eyes glassy     |
| 4         | Very sad      | Quivering lip, eyes level 2, tears welling, head tilted down         |
| 5         | Crying        | Mouth open in wobbly oval, eyes closed/squeezed, tears falling, brows knit |

### Surprise

| Intensity | Name         | Face                                                                 |
|-----------|--------------|----------------------------------------------------------------------|
| 1         | Curiosity    | Eyes level 4, brows raised, slight "o" mouth                         |
| 2         | Mild surprise| Eyes level 4–5, brows raised, "o" mouth, head pulls back slightly    |
| 3         | Surprise     | Eyes level 5, brows high, mouth open oval, head back                 |
| 4         | Startled     | Eyes level 5, brows very high, mouth wide, whole body may react      |
| 5         | Shocked      | Eyes level 5 held wide, brows at maximum, mouth open for 12–24 frames before reaction |

### Anger — Mild frustration to upset, never rage

| Intensity | Name          | Face                                                                 |
|-----------|---------------|----------------------------------------------------------------------|
| 1         | Annoyed       | Slight brow lower, thin lips, brief                                   |
| 2         | Frustrated    | Lowered brows, pursed mouth or slight frown, head shake possible      |
| 3         | Upset         | Brows lowered and knit, eyes narrowed (level 2), frown, arms may cross |
| 4         | Angry         | Strong brow lower, eyes level 2 with glare, tight flat-line mouth    |
| 5         | Very upset    | Maximum brow lower, narrowed eyes (level 2), teeth clenched visible  |

### Fear — Mild worry to scared, never terror

| Intensity | Name       | Face                                                                 |
|-----------|------------|----------------------------------------------------------------------|
| 1         | Worried    | Slight brow knit, eyes level 4, lip slightly tensed                  |
| 2         | Nervous    | Brows raised and knit, eyes level 4, mouth slightly open, fidgety    |
| 3         | Uneasy     | Raised brows, wide eyes (level 4–5), mouth tense, head pulling back  |
| 4         | Scared     | Brows high and knit, eyes level 5, mouth open, body tense            |
| 5         | Frightened | Maximum brows, eyes wide (level 5), mouth stretched horizontally, recoil |

### Disgust

| Intensity | Name     | Face                                                                 |
|-----------|----------|----------------------------------------------------------------------|
| 1         | Distaste | Slight nose wrinkle, one-sided lip curl, brief                       |
| 2         | Disgust  | Nose wrinkled, upper lip raised, eyes narrowed, head back            |
| 3         | "Eww"    | Full nose wrinkle, mouth open in disgust, tongue may protrude, recoil |

### Curiosity

| Intensity | Name         | Face                                                                 |
|-----------|--------------|----------------------------------------------------------------------|
| 1         | Interested   | Slight head tilt, eyes level 4, neutral mouth                        |
| 2         | Curious      | Head tilt, one brow raised, eyes level 4, mouth slightly open        |
| 3         | Inquisitive  | Both brows raised, eyes level 4–5, head tilted, "o" mouth            |
| 4         | Intrigued    | Leaning in, wide eyes (level 4), raised brows, open mouth            |
| 5         | Fascinated   | Eyes fully engaged (level 4–5), bright, leaning forward, smile       |

### Confusion

| Intensity | Name           | Face                                                                 |
|-----------|----------------|----------------------------------------------------------------------|
| 1         | Unsure         | Slight brow knit, head tilt, mouth flat                              |
| 2         | Confused       | Knit brows, eyes level 4, pursed mouth, head tilt                    |
| 3         | Very confused  | Deep knit, one brow lower than other, squint (eye level 3), wry mouth |
| 4         | Bewildered     | Brows asymmetrical, wide eyes (level 4), mouth open, head shake      |

### Excitement

| Intensity | Name          | Face                                                                 |
|-----------|---------------|----------------------------------------------------------------------|
| 1         | Interested    | Slight smile, eyes bright (level 3.5), brows up                      |
| 2         | Eager         | Smile level 2, eyes level 4, eyebrows raised, slight bounce          |
| 3         | Excited       | Smile level 3, eyes bright (level 4), brows up, head up             |
| 4         | Thrilled      | Smile level 4, eyes level 4–5, bouncing, whole face engaged          |
| 5         | Overjoyed     | Smile level 5, eyes level 5, jumping/happy, maximum brightness       |

### Embarrassment

| Intensity | Name         | Face                                                                 |
|-----------|--------------|----------------------------------------------------------------------|
| 1         | Self-conscious | Slight smile, eyes drop down, brief look away                      |
| 2         | Embarrassed  | Nervous smile (closed), eyes down or shifting, cheeks slightly pink  |
| 3         | Very embarrassed | Wide eyes then looking down, hand to face possible, cheeks darker |
| 4         | Mortified    | Eyes squeezed shut (level 1), head down, hands covering face possible |

### Pride

| Intensity | Name      | Face                                                                 |
|-----------|-----------|----------------------------------------------------------------------|
| 1         | Satisfied | Closed smile, chin slightly up, eyes level 3                         |
| 2         | Proud     | Smile level 2–3, chin up, chest out, eyes bright                     |
| 3         | Triumphant| Smile level 4, head high, eyes bright, arms may raise                |

### Love / Affection

| Intensity | Name        | Face                                                                 |
|-----------|-------------|----------------------------------------------------------------------|
| 1         | Fondness    | Soft smile, gentle eyes (level 3), head tilt                         |
| 2         | Warmth      | Warm smile (level 2), eyes soft and bright, slight lean in           |
| 3         | Affection   | Deep warm smile (level 3), eyes half-lidded and soft (level 2.5)     |
| 4         | Adoring     | Big smile (level 3–4), very soft eyes, head tilt, full attention     |

### Sleepiness

| Intensity | Name       | Face                                                                 |
|-----------|------------|----------------------------------------------------------------------|
| 1         | Tired      | Eyes half-lidded (level 2), slight yawn, slow blink                  |
| 2         | Sleepy     | Eyes level 1.5–2, heavy lids, head nodding, slow movements           |
| 3         | Very sleepy| Eyes nearly closed (level 1.5), mouth relaxed/slightly open          |
| 4         | Falling asleep | Eyes closed (level 1), head drooping, body relaxing              |

---

## Per-Character Facial Notes

### Bunny
- Big round eyes — eye openness levels read very clearly; level 3 on Bunny is more expressive than on other characters
- Ears are emotional indicators: perked up for alert/happy, relaxed for content, drooping for sad
- Small nose twitches for curiosity or smelling something
- Soft fur around cheeks amplifies smile crinkles
- Avoid squinting too small — it covers too much of her expressive eyes

### Pig
- Snout limits upper lip movement — smiles are wider horizontally rather than showing upper teeth
- Wrinkles at the base of the snout indicate smiling or laughing
- Ears flop during strong expressions (shake on surprise, droop on sadness)
- Nostril flaring (subtle) for strong emotions
- Cheek puff for frustration (huffing sound can pair)

### Owl
- Large, wide-set eyes — exaggerated blinking is a signature trait
- Blink duration can be held slightly longer (4–5 frames) for comedic or emphasis effect
- Eyebrows very expressive above large eyes
- Head turning substitutes for some expressions — Owl often tilts head to show curiosity
- Beak limits mouth shapes; open/closed distinction is most important

### Bear
- Broad face means expressions need to be slightly bigger to read
- Heavy brows make lowering very visible for anger/frustration
- Warm, deep-set eyes — crinkles at corners are key for genuine smiles
- Muzzle area: snout wrinkle for happy, lip curl for distaste
- Head tilts add approachability

### Cat
- Slit pupils change with emotion: wide/dilated for surprise or excitement, narrow for content or annoyed
- Whisker position: forward for curiosity, laid back for fear or startle
- Ear rotation: forward for interest, sideways for relaxed, flat for upset
- Small mouth means smiles and frowns are subtle compared to other characters

### Duck
- Bill makes most mouth shapes impossible — rely on bill opening degree: closed=neutral, slightly open=happy, wide open=surprise/shout
- Head bobbing frequency changes with emotional state (faster = excited, slower = sad)
- Eye level above bill means expressions read primarily through eyes
- Wing "shrugs" substitute for many gestural expressions

---

## Transition Timing Between Expressions

Default transition times based on intensity difference:

| Intensity Change | Frames | Notes                          |
|------------------|--------|--------------------------------|
| Same level       | 4      | Minor micro-adjustment         |
| 1 level          | 4–6    | Subtle shift                   |
| 2 levels         | 6–8    | Moderate change                |
| 3 levels         | 8–10   | Notable emotional shift        |
| 4 levels         | 10–12  | Major emotional swing          |
| Extreme (1↔5)    | 12     | Full emotional reversal        |

- Hold extreme expressions (levels 4–5) for 12–24 frames so children can register them
- Return to neutral expression takes 6 frames minimum
- Blink can mask transitions: time a blink mid-transition to make changes less noticeable

---

## Emotional Arc Examples

Building emotion over multiple sentences of dialogue or action.

### Growing Joy (3 sentences)
1. "Look what I found!" — Smile level 2, eyes level 3.5, raised brows
2. "It's a shiny red apple!" — Building to smile level 3, eyes level 4, brows up
3. "My favorite!" — Peak at smile level 4, eyes squinted, cheeks up — hold for 12 frames

### Disappointment to Acceptance (4 beats)
1. "Oh..." — Smile drops to flat line in 6 frames
2. "I wanted to go too..." — Frown level 2, sad brows, eyes downcast
3. "But maybe next time." — Mouth softens, brows back to neutral over 8 frames
4. "Okay, I understand." — Small brave smile level 1, eyes soft

### Surprise → Curiosity → Excitement
1. Surprise level 3 (eyes level 5, mouth O, brows high) — hold 12 frames
2. Sink to curiosity level 2 over 6 frames (one brow lowers, mouth closes)
3. Build to excitement level 3 over 10 frames (smile grows, eyes brighten, brows up)

### Worry → Relief (2 sentences)
1. "Where did Mama go?" — Worry level 2 (knit brows, looking around)
2. "There she is!" — Flash to relief: brows up, smile level 3, eyes bright in 4 frames
