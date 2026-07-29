# Mouth Animation Standards

## Mouth Shapes (Phonemes)

For the studio's simplified, preschool-friendly style, we use a reduced phoneme set. Each shape maps to multiple real phonemes for ease of animation.

| Shape   | Phonemes    | Description                            | Usage                            |
|---------|-------------|----------------------------------------|----------------------------------|
| Closed  | M, B, P     | Lips gently together, relaxed          | Rest, thinking, M/B/P sounds     |
| Open    | A, I        | Mouth open oval, jaw dropped           | A and I vowels, surprise         |
| Wide    | E, S        | Lips stretched horizontally            | E and S sounds, grinning         |
| Pursed  | O, U        | Lips rounded forward, small opening    | O and U vowels, whistling        |
| Smile   | Happy sounds| Corners up, slight opening             | Positive dialogue                 |
| Frown   | Sad sounds  | Corners down, lower lip may protrude   | Negative dialogue                 |
| Laugh   | Ha, He      | Wide open, teeth visible, jaw dropped  | Laughing, delighted              |
| Yawn    | —           | Huge oval, jaw fully dropped           | Tired, yawning                   |
| Whisper | —           | Very small opening, lips barely apart  | Whispering, secrets              |
| Singing | All         | Exaggerated shapes, held longer        | Musical segments                  |
| Kiss    | —           | Puckered forward                       | Kissing, blowing a kiss          |
| Flat    | —           | Straight horizontal line, firm         | Anger, neutral, suppressed       |

---

## Talking Animation

### Per-Syllable Pattern
- Alternate between 2–3 shapes per syllable
- Pattern example for "Hello": Open → Closed → Wide → Pursed
- Each shape held 4–6 frames

### Timing
| Element          | Frames    | Notes                              |
|------------------|-----------|------------------------------------|
| Per phoneme      | 4–6       | At 24fps, ~170–250ms per shape     |
| Per syllable     | 8–12      | 2–3 shapes                         |
| Word pause       | 6–8       | Brief hold between words           |
| Sentence pause   | 12–18     | Longer break, may close mouth      |

### Dialogue Flow
1. **Pre-speech breath** (4 frames): mouth opens slightly, inhale
2. **Speech** (variable): phoneme shapes cycle
3. **Post-speech** (6 frames): mouth returns to neutral or smile

---

## Singing

Singing requires extended, exaggerated shapes.

| Element          | Frames    | Notes                              |
|------------------|-----------|------------------------------------|
| Per shape        | 8–12      | Held 2x longer than speech         |
| Shape range      | Maximum   | Open wider, purse tighter          |
| Phrase end       | 12–16     | Hold final shape for musical effect |
| Breath           | 6–8       | Larger breath between phrases      |

- Vowels are emphasized: Open (A) and Pursed (O) are bigger than in speech
- Head may tilt or sway in rhythm with the melody
- Eyes often closed or half-lidded during emotional sung notes

---

## Laughing

| Phase     | Frames | Description                        |
|-----------|--------|------------------------------------|
| Open      | 3      | Mouth opens, head tilts back       |
| Closed    | 3      | Mouth closes (or near-closed)      |
| Cycle     | 6      | One full laugh                     |

- Repeat cycles for sustained laughter (3–5 cycles typical)
- Breathing gaps every 2–3 cycles
- Body bounces with laugh rhythm (shoulders up/down)
- Tears may form at 3+ cycles of intense laughter

---

## Yawning

| Phase    | Frames | Description                            |
|----------|--------|----------------------------------------|
| Build    | 8      | Mouth slowly opens, eyes begin closing  |
| Peak     | 12     | Mouth fully open (huge oval), eyes closed or half-lidded |
| Release  | 8      | Mouth closes, eyes open, maybe shake head |

- Preceded by eye rubbing (optional, 6 frames)
- Followed by head shake or stretch (12 frames)

---

## Whispering

| Element      | Frames | Description                        |
|--------------|--------|------------------------------------|
| Mouth shape  | 4–6    | Small opening, lips barely apart   |
| Head lean    | 4      | Lean toward listener               |
| Hand cue     | 8      | Hand may cup near mouth            |

Whispering shapes are subtle — small movements, held slightly longer than normal speech.

---

## Breathing

Breath animation makes characters feel alive even when silent.

| Type         | Frames | Description                        |
|--------------|--------|------------------------------------|
| Idle breath  | 6–8    | Subtle open/close, barely visible  |
| Pre-speech   | 4      | Slightly larger inhale before talking |
| Post-speech  | 6      | Exhale, return to resting          |
| Exhausted    | 10–12  | Large inhale, longer hold, obvious |
| Sigh         | 12     | Inhale 4, hold 2, exhale 6        |

- Idle breathing is continuous (not tied to dialogue)
- Combine with chest/shoulder rise for visibility

---

## Sync Rules

| Principle                      | Details                                      |
|--------------------------------|----------------------------------------------|
| Mouth shape precedes audio     | Shape should reach target 1–2 frames before sound |
| Anticipation                   | Mouth opens slightly 2 frames before first phoneme |
| Hold on important words        | Lengthen shape hold by 2–4 frames on emphasized syllables |
| Reset between sentences        | Return to neutral or smile for 6–8 frames between sentences |

Preceding audio by 1–2 frames is critical — it matches how real mouths form shapes before sound leaves them. Animating mouth to exactly match audio creates a delayed, puppet-like feel.

---

## Per-Character Mouth Notes

### Bunny
- Small mouth relative to head — shapes are compact
- Open smile shows upper teeth only (cute, not wide)
- When surprised, mouth forms a small perfect "o" shape
- Whiskers twitch during speech (subtle secondary motion)

### Pig
- Snout limits vertical mouth opening
- Smiles stretch wide horizontally
- Upper lip barely moves — lower lip does most of the work
- Snout wrinkles intensify with shape exaggeration
- "O" shape is more forward-pursed due to snout anatomy

### Owl
- Beak is rigid — mouth opens at the tip only (lower beak drops)
- Open/closed is primary distinction; subtle shapes are lost
- Exaggerated open for singing or surprise
- Tongue visible when mouth is open (pink, small)

### Bear
- Broad mouth — shapes are wide and clear
- Full teeth visible in open smile (child-friendly, not threatening)
- Lower lip pushes out in pout or sad shapes
- Muzzle fur moves with mouth shapes (secondary motion)

### Cat
- Small mouth, pointed at corners
- Shapes are subtle due to mouth size
- Whiskers move forward with pursed shapes, back with wide shapes
- Tongue protrudes slightly during "L" sounds or licking

### Duck
- Bill is the entire mouth area — no lip separation
- Degree of bill opening is the only variable
- 0% = closed (neutral), 25% = talking, 50% = happy/laughing, 75% = singing, 100% = surprised/shouting
- No teeth visible — bill edges are smooth
- Head bobs often punctuate speech rhythm
