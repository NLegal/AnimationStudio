# Humor Engine Guide

> **Version:** 1.0
> **Purpose:** Age-appropriate humor that delights without embarrassing

## Philosophy

Humor in preschool content should:
- Surprise gently — unexpected but not startling
- Include the audience — laughter is contagious
- Never mock — humor should never embarrass a character
- Be physical — funny sounds, silly movements, exaggerated expressions
- Be repeatable — catchphrases and running gags build familiarity

## Humor Types

| Type | Description | Example |
|------|-------------|---------|
| Funny Sound | Unexpected noise from character or object | Squeaky toy sneeze, hiccup at wrong moment |
| Silky Movement | Exaggerated or clumsy motion | Ben Bear tripping over his own feet (gently) |
| Goofy Appearance | Character wearing something silly | Lily Bunny with a bucket on her head |
| Animal Antics | Animals doing unexpected things | Cat chasing her own tail, Dog spinning in circles |
| Repetition Build | Same joke escalating | Balloon squeak getting higher each time |
| Surprise Reveal | Hidden object or character revealed | "Peek-a-boo!" from behind a bush |
| Word Play | Simple puns appropriate for age | "I'm stuck on you!" (hugging + sticky candy) |
| Role Reversal | Child acting like adult | Lily Bunny "teaching" Mommy Bunny |

## Humor by Character

| Character | Humor Style | Signature Bit |
|-----------|-------------|---------------|
| Lily Bunny | Giggly, infectious | Covers mouth when laughing, sometimes falls over |
| Ben Bear | Deadpan accident-prone | Says "Oops" calmly after doing something silly |
| Charlie Fox | Clever, trickster | Sets up gentle pranks, laughs at result |
| Daisy Duck | Dramatic, overreacts | Gasps dramatically at small surprises |
| Monkey | Physical comedy | Makes funny faces, tumbles, clowns around |
| Cat | Cat-typical mischief | Knocks things off tables, chases laser dots |

## Safety Rules

- No physical harm — falls are cushioned, nothing breaks
- No embarrassment — humor at character's expense is never the punchline
- No mean-spirited jokes — no teasing, no exclusion
- No complex irony — preschoolers don't understand sarcasm
- No scariness — surprise should be fun, not frightening
- Gentle recovery — characters laugh at themselves, not feel bad

## Implementation Notes

The HumorEngine in `src/story_engine/interaction.py` provides:
- `select_humor_moment(exclude, characters)` — picks a humor type appropriate for the episode
- Integration with DialogueEngine for comedic timing
- Character-specific humor preferences

## Quality Checklist

- [ ] Humor is age-appropriate (2-6 years)
- [ ] No character is embarrassed or hurt
- [ ] Humor supports the story, not distracts
- [ ] Laugh tracks are never used
- [ ] Humorous moments have clear setup and payoff
- [ ] Physical comedy is gentle (no painful-looking falls)
