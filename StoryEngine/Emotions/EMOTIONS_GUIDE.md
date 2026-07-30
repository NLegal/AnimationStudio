# Emotion Engine Guide

> **Version:** 1.0
> **Purpose:** Control emotional flow across every episode

## Philosophy

Emotion in preschool content should be:
- **Clear** — children should easily read every character's feeling
- **Gentle** — avoid intense or frightening emotions
- **Educational** — name emotions explicitly ("I feel happy!")
- **Positive arc** — every episode ends happier than it began
- **Contagious** — characters model healthy emotional responses

## Emotional Arc

Every episode follows a structured emotional journey:

```
                     Celebration
                    ↗           ↘
     Curiosity — Excitement    Happy
          ↘           ↗           ↘
         Challenge — Thinking    Goodbye
              ↘         ↗
            Worry — Learning
```

**Arc rules:**
1. Start with curiosity (hook the viewer)
2. Brief challenge/worry moment (mild tension)
3. Learning moment (curiosity returns)
4. Celebration (peak positive emotion)
5. End warm and content (not hyperactive)

## Emotion Intensity Scale

Each emotion has 3 levels suitable for preschool content:

| Emotion | Level 1 (Mild) | Level 2 (Moderate) | Level 3 (Strong) |
|---------|----------------|---------------------|-------------------|
| Happy | Content, peaceful | Smiling, cheerful | Laughing, excited |
| Sad | Quiet, resting | Lower lip out | Gentle tears |
| Surprised | Interested | Eyes widen | Delighted gasp |
| Curious | Glancing | Leaning forward, asking | Exploring, investigating |
| Worried | Frowning | Fidgeting | Looking for help |
| Proud | Small smile | Standing taller | "I did it!" celebration |

## Emotional Safety

| Avoid | Reason | Replace With |
|-------|--------|--------------|
| Anger | Scares children | Mild frustration, "Hmm, that's tricky" |
| Fear | Causes distress | Concern, caution |
| Jealousy | Negative social model | "I'd like to try that too!" |
| Embarrassment | Damages confidence | "Oops! That was silly!" (laugh together) |
| Overwhelming joy | Can overstimulate | Measured excitement with breathing room |

## Character Emotional Signatures

| Character | Default Emotion | Emotional Peak | Processing Style |
|-----------|-----------------|----------------|------------------|
| Lily Bunny | Happy | Excitement | Expresses openly, seeks comfort |
| Ben Bear | Content | Pride | Processes quietly, needs prompting |
| Charlie Fox | Curious | Discovery | Analyzes, then reacts |
| Daisy Duck | Cheerful | Joy | Dramatic expression, dances it out |
| Mommy Bunny | Warm | Pride in children | Calm reassurance |
| Daddy Bunny | Playful | Delight | Silly reaction to defuse tension |

## Emotional Learning

Each episode should explicitly name at least one emotion:
- "I feel happy when I share!"
- "It's okay to feel sad. Let's try again tomorrow."
- "Wow, you look so proud of your drawing!"

## Implementation Notes

The EmotionEngine in `src/story_engine/interaction.py` provides:
- `generate_emotional_arc(narrative_beats)` — creates emotion-per-beat mapping
- Integration with DialogueEngine for emotionally-aware dialogue
- Per-character emotional defaults and peaks

## Quality Checklist

- [ ] Episode starts curious/positive
- [ ] Emotional peak is celebration, not fear
- [ ] Episode ends warmer than it began
- [ ] No intense negative emotions (anger, terror, grief)
- [ ] At least one emotion is named explicitly
- [ ] Characters model healthy emotional responses
- [ ] Pacing allows emotional processing time
