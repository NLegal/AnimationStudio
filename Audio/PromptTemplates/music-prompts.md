# Music Prompt Templates

## AI Nursery Studio — Prompt Engineering Guide

### Version 1.0

---

## Introduction

Effective music generation requires precise, structured prompts. This guide provides tested templates for Suno (primary platform) and adaptable patterns for ACE-Step Studio (offline backup).

Each template follows a consistent structure and can be customized by filling the bracketed `[variables]`.

---

## Prompt Structure

### Base Template

```
A cheerful preschool educational song about [topic], [lead vocal style], [backing vocals], [mood/key], [instruments], [rhythm], [tempo], [atmosphere], approximately [duration].
```

### Anatomy of a Music Prompt

| Component | Options | Example |
|-----------|---------|---------|
| Genre Descriptor | cheerful preschool educational song, gentle lullaby, upbeat action song | cheerful preschool educational song |
| Topic | about [topic] | about the color red |
| Lead Vocal | female lead vocal, male lead vocal, child lead vocal, narrator-style vocal | female lead vocal |
| Backing Vocals | children's backing choir, echo response group, hummed backing | children's backing choir |
| Mood/Key | upbeat major key, gentle major key, bright key of C major | upbeat major key |
| Instruments | bright instrumentation, hand claps, xylophone, acoustic guitar, piano, tambourine, marimba, ukulele, glockenspiel, shakers, wood blocks, bass drum, triangle, bells, strings, brass | xylophone, acoustic guitar, hand claps |
| Rhythm | simple repetitive melody, strong beat, bouncy rhythm, steady march tempo | simple repetitive melody, hand claps on beat |
| Tempo | [number] BPM | 120 BPM |
| Atmosphere | friendly atmosphere, warm atmosphere, magical atmosphere, playful atmosphere, calm atmosphere | friendly, warm atmosphere |
| Duration | approximately [30 seconds / 1 minute / 2 minutes] | approximately one minute |

---

## Platform-Specific Notes

### Suno v3.5

| Feature | Notes |
|---------|-------|
| Prompt length | 120–200 characters recommended |
| Style prompt | Use comma-separated keywords in Style field |
| Lyrics | Provide full lyrics in Lyrics field |
| Instrumental | Add "Instrumental" to style for no vocals |
| Best for | Full songs with clear structure |
| Limitations | May not follow complex instructions precisely |

### Suno v4

| Feature | Notes |
|---------|-------|
| Prompt length | 200–300 characters recommended |
| Persona | Can replicate consistent singer voice |
| Style prompt | More precise genre control |
| Lyrics | Supports structured lyrics with section markers |
| Best for | Full episodes, compilation songs |
| Improvements | Better vocal clarity, fewer artifacts |

### ACE-Step Studio

| Feature | Notes |
|---------|-------|
| Prompt length | 100–200 characters |
| Style prompt | Use descriptive adjectives |
| Best for | Instrumental backgrounds, short jingles |
| Limitations | Lower vocal quality than Suno |

---

## Prompt Templates (15+)

### 1. Alphabet Song Template

```
A cheerful preschool alphabet song about letters A to Z, female lead vocal, children's backing choir, bright major key, bouncy rhythm, xylophone and glockenspiel melody, acoustic guitar strums, hand claps, tambourine, 120 BPM, educational and playful atmosphere, simple repetitive chorus, approximately one minute.
```

### 2. Counting Song Template

```
A cheerful preschool counting song about numbers one to ten, female lead vocal with call-and-response children's choir, upbeat major key, steady simple beat, piano and marimba, wood block percussion, hand claps, 110 BPM, friendly educational atmosphere, strong repetitive counting hook, approximately one minute.
```

### 3. Color Song Template

```
A cheerful preschool song about colors, female lead vocal, children's backing harmony, bright major key, playful melody, ukulele and xylophone, gentle percussion, shakers, 115 BPM, warm educational atmosphere, verses name each color with examples, repeating color chorus in call-and-response style, approximately 90 seconds.
```

### 4. Animal Song Template

```
A cheerful preschool animal song with animal sounds, female lead vocal, children's backing choir responding with animal noises, upbeat major key, playful bouncy rhythm, acoustic guitar, slide whistle, hand claps, stomps, tambourine, 105 BPM, farmyard playful atmosphere, each verse introduces a new animal with its sound, approximately 90 seconds.
```

### 5. Morning Routine Template

```
A cheerful preschool song about morning routine, female lead vocal, children's backing vocals, bright major key, steady walking rhythm, acoustic guitar strum, piano melody, hand claps, triangle on key words, 100 BPM, warm encouraging atmosphere, step-by-step actions described in each verse, strong repetitive chorus about getting ready, approximately one minute.
```

### 6. Bedtime Lullaby Template

```
A gentle preschool lullaby about going to sleep, soft female vocal humming with occasional gentle words, children's choir humming softly in background, gentle major key, slow gentle tempo, soft piano, music box chimes, strings pad, no percussion, 75 BPM, calm dreamy atmosphere, soft repetitive melody, approximately two minutes.
```

### 7. Good Manners Template

```
A cheerful preschool song about good manners and kindness, female lead vocal, children's backing choir, warm major key, friendly melodic rhythm, acoustic guitar, gentle piano, soft hand claps, triangle, 95 BPM, warm educational atmosphere, teaches please, thank you, sorry, and excuse me through call-and-response, approximately 90 seconds.
```

### 8. Dance Song Template

```
A high-energy preschool dance song, female lead vocal leading action instructions, children's backing vocals shouting responses, upbeat major key, strong driving beat, bass drum, hand claps on every beat, tambourine, brass stabs on chorus, 130 BPM, energetic party atmosphere, instructions for movements (stomp, clap, jump, spin) in each section, approximately 90 seconds.
```

### 9. Holiday Song Template (Christmas)

```
A warm preschool Christmas song about holiday joy, female lead vocal, children's choir, gentle major key, classic holiday melody structure, sleigh bells, piano, acoustic guitar, soft strings, gentle hand percussion, 90 BPM, warm magical holiday atmosphere, simple verses about giving, family, and togetherness, approximately 90 seconds.
```

### 10. Holiday Song Template (Birthday)

```
A cheerful preschool birthday celebration song, female lead vocal leading, children's backing choir joining on chorus, bright major key, upbeat celebratory rhythm, hand claps, party horn sounds, xylophone, tambourine, bass drum on downbeats, 120 BPM, festive party atmosphere, verses describe birthday activities, chorus is sing-along celebration, approximately 60 seconds.
```

### 11. Friendship Song Template

```
A warm preschool song about friendship and playing together, female lead vocal, children's choir unison, gentle major key, friendly swaying rhythm, acoustic guitar, soft piano, gentle hand percussion, 95 BPM, warm inclusive atmosphere, verses describe sharing and helping friends, chorus emphasizes togetherness, approximately 90 seconds.
```

### 12. Nature/Outdoor Template

```
A cheerful preschool song about nature and the outdoors, female lead vocal, children's backing vocals humming nature sounds, bright major key, gentle flowing rhythm, acoustic guitar fingerpicking, bird whistle sounds, wind chimes, light percussion like rain sticks, 100 BPM, fresh outdoor atmosphere, describes trees, flowers, sky, and animals in nature, approximately one minute.
```

### 13. Emotion/Feelings Template

```
A gentle preschool song about feelings and emotions, warm female lead vocal, children's backing choir, gentle major key with brief minor touches for sad sections, calm steady rhythm, piano leads, soft strings, gentle percussion, 90 BPM, safe understanding atmosphere, names emotions (happy, sad, angry, scared) and validates each, approximately 90 seconds.
```

### 14. Instrumental Background Template

```
Gentle preschool instrumental background music, soft piano melody, light strings pad, gentle acoustic guitar, warm woodwinds, no percussion, 80 BPM, calm warm atmosphere, simple repeating melody suitable for narration or play scenes, approximately two minutes.
```

### 15. Story Narration Background Template

```
Soft preschool narration background, gentle piano chords, light ambient pad, subtle strings, no percussion, no strong melody, 70 BPM, spacious atmospheric sound, dynamic range suitable for voiceover, approximately three minutes.
```

### 16. Shapes Song Template

```
A cheerful preschool song about shapes, female lead vocal, children's backing choir repeating shape names, bright major key, steady educational rhythm, xylophone melody playing shape-associated motifs, triangle, wood block, hand claps, 108 BPM, playful learning atmosphere, each verse introduces a shape with a familiar object example, approximately 90 seconds.
```

### 17. Weather Song Template

```
A cheerful preschool song about weather, female lead vocal, children's backing vocals making weather sounds (pitter-patter, whoosh), bright major key, dynamic rhythm shifting with weather types, rain stick, wind sounds, gentle thunder drum, triangle for lightning, piano, 100 BPM, friendly educational atmosphere, each verse describes a different weather type, approximately 90 seconds.
```

### 18. Transportation Song Template

```
A cheerful preschool song about vehicles and transportation, female lead vocal, children's backing choir making vehicle sounds, upbeat major key, driving rhythmic feel, train whistle, honk sounds, engine rhythm percussion, guitar, piano, 120 BPM, energetic movement atmosphere, describes cars, trains, planes, boats with sounds and actions, approximately 60 seconds.
```

---

## Prompt Customization Rules

### Tempo by Mood

| Mood | BPM Range |
|------|-----------|
| Calm / Sleepy | 70–90 BPM |
| Gentle / Warm | 85–105 BPM |
| Playful / Cheerful | 100–120 BPM |
| Energetic / Dance | 115–130 BPM |
| Exciting / Action | 120–135 BPM |

### Instrument Selection by Category

| Category | Primary Instruments |
|----------|-------------------|
| Educational | Xylophone, glockenspiel, piano, acoustic guitar |
| Lullaby | Music box, piano, soft strings, harp |
| Action | Drums, percussion, brass, hand claps |
| Nature | Flute, acoustic guitar, wind chimes, rain stick |
| Celebration | Tambourine, hand claps, bells, piano |
| Story | Piano, strings pad, woodwinds |

### Vocal Style by Song Type

| Song Type | Lead Vocal | Backing |
|-----------|------------|---------|
| Alphabet | Female, clear enunciation | Children's choir |
| Counting | Female, rhythmic delivery | Call-and-response |
| Lullaby | Soft female or male | Humming choir |
| Action/Dance | Energetic female | Shouted responses |
| Story-song | Narrator-style | Minimal |

---

## Failed Generation Troubleshooting

| Issue | Likely Cause | Fix |
|-------|-------------|-----|
| Wrong genre | Prompt too vague | Add specific genre keywords |
| Instrument ignored | Too many instructions | Reduce to 3–4 key instruments |
| Poor vocal quality | No vocal direction | Specify vocal style explicitly |
| Wrong tempo | BPM too vague | Always include exact BPM |
| Too repetitive | Prompt too short | Add variation instructions |
| Distortion | Duration mismatch | Match duration to prompt description |
| No children's voices | Not specified | Always add children's choir if desired |
| Instrumental instead of song | Missing "vocals" | Explicitly state vocal style |
