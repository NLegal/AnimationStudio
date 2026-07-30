# Song Engine Guide

## Purpose

The Song Engine determines whether an episode contains music, what type of song is needed, where it is placed, and what lyrical intent it should fulfill. The engine outputs song specifications — not audio — which are later produced by the Phase 5 audio pipeline.

---

## When to Include Songs

Not every episode needs a song. The Song Engine decides based on these criteria:

| Criterion | Include Song | Skip Song |
|---|---|---|
| Learning objective is musical | Alphabet, counting, color songs | Problem solving, emotions |
| Episode type | Song-and-dance, educational song | Story time, problem solving |
| Target age (2-3) | Include 1 short song | — |
| Target age (4-6) | Include 1-2 songs | — |
| Celebration scene | Always include | — |
| Holiday episode | Always include | — |
| Episode needs energy boost | Include | — |
| Episode follows a song episode | — | Skip to maintain variety |

---

## Song Placement Options

### Opening Song

**Purpose:** Greet the audience and set the tone.
**Duration:** 45-60 seconds
**Style:** Upbeat, welcoming
**Content:** Hello greeting, introduce characters, preview today's topic

### Middle Song

**Purpose:** Reinforce the learning objective mid-episode.
**Duration:** 60-90 seconds
**Style:** Depends on learning objective
**Content:** Teaching the core concept through lyrics and repetition

### Ending Song

**Purpose:** Celebrate success and wrap up.
**Duration:** 45-60 seconds
**Style:** Joyful, uplifting
**Content:** Recap what was learned, celebrate achievement

### Full Episode Musical

**Purpose:** Entirely song-based episode.
**Duration:** 2-3 minutes
**Style:** Varied — multiple song segments
**Content:** Story told entirely through song, no spoken narration

### Transition Song

**Purpose:** Bridge between scenes.
**Duration:** 15-30 seconds
**Style:** Brief, simple
**Content:** Short musical interlude — "And then they went to..."

### Dance Song

**Purpose:** Physical activity and motor skills.
**Duration:** 60-90 seconds
**Style:** Energetic, rhythmic
**Content:** Dance instructions, movement prompts

### Lullaby

**Purpose:** Calming, bedtime episodes.
**Duration:** 60-90 seconds
**Style:** Soft, gentle, slow
**Content:** Soothing lyrics, comfort themes

---

## Song Type by Learning Objective

| Learning Objective Category | Recommended Song Type | Example Theme |
|---|---|---|
| Alphabet | Alphabet Song, Opening Song | "A is for Apple" |
| Numbers | Counting Song, Dance Song | "Five Little Ducks" |
| Colors | Color Song, Full Episode Musical | "The Rainbow Song" |
| Shapes | Educational Song, Transition Song | "Shape Shuffle" |
| Animals | Animal Sound Song, Dance Song | "Old MacDonald" |
| Healthy Habits | Educational Song, Lullaby | "Brush Your Teeth Song" |
| Friendship | Celebration Song, Ending Song | "Friends Forever" |
| Emotions | Opening Lullaby, Ending Song | "If You're Happy and You Know It" |
| Seasons | Seasonal Song, Transition Song | "Winter Wonderland" |
| Weather | Educational Song, Dance Song | "Rain, Rain, Go Away" |
| Motor Skills | Dance Song, Full Episode Musical | "Head, Shoulders, Knees and Toes" |
| Music & Rhythm | Rhythm Song, Dance Song | "The Instrument Song" |
| Transportation | Educational Song, Transition Song | "The Wheels on the Bus" |
| Daily Routines | Educational Song, Lullaby | "This is the Way We..." |

---

## Duration Guidelines

| Song Type | Min Duration | Max Duration | Target Age |
|---|---|---|---|
| Opening Song | 45s | 60s | 2-6 |
| Middle Song | 60s | 90s | 3-6 |
| Ending Song | 45s | 60s | 2-6 |
| Full Musical Episode | 2min | 3min | 2-4 |
| Transition Song | 15s | 30s | 2-6 |
| Dance Song | 60s | 90s | 3-6 |
| Lullaby | 60s | 90s | 2-3 |

### Age-Adjusted Duration

| Age | Max Total Music per Episode | Max Song Length |
|---|---|---|
| 2 years | 60 seconds | 45 seconds |
| 3 years | 90 seconds | 60 seconds |
| 4 years | 120 seconds | 90 seconds |
| 5-6 years | 180 seconds | 120 seconds |

---

## Song Output Specification

When the Song Engine determines a song is needed, it produces a structured output:

```
Song Specification:
  Type: [Opening / Middle / Ending / Full / Transition / Dance / Lullaby]
  Position: [Scene placement]
  Duration: [Target duration]
  Learning Connection: [Which objective it reinforces]
  Lyrical Intent: [Core message / theme of the lyrics]
  Style: [Upbeat / Gentle / Energetic / Calm]
  Interactive Elements: [Actions / call-and-response / repetition]
  Key Vocabulary: [Words that must appear in lyrics]
```

---

## Song Placement Rules

| Rule | Explanation |
|---|---|
| No consecutive song episodes | At least one non-music episode between musical episodes |
| Opening song only once | Maximum one opening song per episode |
| Song supports objective | Lyrics must reinforce the learning objective |
| Age-appropriate lyrics | Words must match target age vocabulary |
| Actions encouraged | Include movement prompts for audience participation |
| Repetition is good | Repeat the key learning word in the chorus |
| Songs are not required | Not every episode needs music |
| Holiday songs are seasonal | Holiday songs only used near the corresponding holiday |

---

## Example Song Specifications

### Example 1: Counting Song (Middle)

```
Type: Middle Song (Counting Song)
Position: After teaching scene, before practice
Duration: 75 seconds
Learning Connection: Count to five
Lyrical Intent: Counting five objects with visual examples
Style: Upbeat, bouncy
Interactive Elements: Finger counting, "How many?" questions
Key Vocabulary: one, two, three, four, five, count
```

### Example 2: Rainbow Song (Opening)

```
Type: Opening Song (Color Song)
Position: Opening scene
Duration: 55 seconds
Learning Connection: Recognize colors
Lyrical Intent: Introduce colors through rainbow imagery
Style: Bright, cheerful
Interactive Elements: Point to colors, say color names
Key Vocabulary: red, orange, yellow, green, blue, purple
```

### Example 3: Goodnight Lullaby (Ending)

```
Type: Lullaby
Position: Goodbye scene
Duration: 70 seconds
Learning Connection: Bedtime routine
Lyrical Intent: Soothing wind-down, comfort
Style: Soft, gentle, slow tempo
Interactive Elements: Rock gently, close eyes
Key Vocabulary: night, sleep, dream, warm, safe
```
