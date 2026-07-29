# Localization Guide

## AI Nursery Studio — Audio Bible

### Version 1.0

---

## Introduction

AI Nursery Studio content is designed for global audiences from day one. Every audio asset is created with localization in mind, ensuring that episodes can be adapted for different languages without compromising quality, educational value, or emotional impact.

Target languages are English (source), Spanish, French, German, Chinese (Mandarin), and Japanese, with additional languages added as the catalog grows.

---

## Localization Philosophy

| Principle | Description |
|-----------|-------------|
| **Design for replacement** | Every localized element should be replaceable without touching other layers |
| **Preserve education** | The learning objective must survive translation |
| **Maintain rhythm** | Songs must remain singable in the target language |
| **Cultural relevance** | Adapt references, don't just translate words |
| **Voice consistency** | Target-language characters should feel like the same person |
| **Quality parity** | Localized audio meets the same standards as the original |

---

## Target Languages

### Current Targets

| Code | Language | Priority | Complexity | Notes |
|------|----------|----------|------------|-------|
| en | English | Source | Baseline | Original production language |
| es | Spanish | High | Medium | Large preschool audience; clear phonetics |
| fr | French | High | Medium | Major market; important for EU distribution |
| de | German | Medium | Medium | Large market; longer word lengths |
| zh | Chinese (Mandarin) | High | High | Tonal language; vocal match critical |
| ja | Japanese | Medium | High | Different syllable structure; character-heavy |

### Future Targets (Planned)

Portuguese (pt-BR), Italian (it), Dutch (nl), Korean (ko), Arabic (ar), Hindi (hi), Turkish (tr), Vietnamese (vi), Thai (th), Russian (ru).

---

## Localization Pipeline

### Pipeline Overview

```text
Source Master (English)
        │
        ▼
Step 1: Export Dialogue Stems
        │
        ▼
Step 2: Translate
    ├── Dialogue Script Translation
    ├── Lyric Translation (rhyme & rhythm preserved)
    └── Subtitle Translation
        │
        ▼
Step 3: Cultural Adaptation Review
        │
        ▼
Step 4: Cast & Record Target Language
    ├── Cast local voice talent
    ├── Record dialogue (matching source timing)
    └── Record songs (matching source melody)
        │
        ▼
Step 5: Remix
    ├── Replace dialogue stem with new language
    ├── Replace vocal stem with new language
    └── Keep original music and SFX stems
        │
        ▼
Step 6: Localized Mastering
    ├── Apply same mastering chain
    ├── Match loudness to -14 LUFS
    └── Quality check
        │
        ▼
Step 7: Export Localized Master
```

---

### Step 1: Export Dialogue Stems

From the source project:

| Stem | Contains | Localization Use |
|------|----------|------------------|
| Dialogue stem | All spoken dialogue, no music/SFX | Replace entirely with new language |
| Vocal stem | All sung vocals | Replace with target-language vocals |
| Music stem | All instrumental music | Keep original (no change) |
| SFX stem | All sound effects | Keep original (adjust if culturally inappropriate) |
| Foley stem | All foley sounds | Keep original (typically universal) |
| Ambience stem | All ambient backgrounds | Keep original (typically universal) |

**Critical**: Dialogue and vocal stems must be rendered without any baked-in reverb or effects. Deliver these as dry stems so they can be processed consistently in each language.

### Step 2: Translation Workflow

```
Original English Script
        │
        ▼
Dialogue Translation
├── Translate meaning (not word-for-word)
├── Match character voice personality
├── Adapt idioms and cultural references
└── Keep to original timing (±10% duration)
        │
        ▼
Lyric Translation
├── Maintain syllable count per line
├── Preserve rhyme scheme (AABB, ABAB, etc.)
├── Keep key educational words
└── Ensure singability with original melody
        │
        ▼
Subtitle Translation
├── Follow subtitle standards (see SUBTITLE_STANDARDS.md)
├── Max 32 characters per line
└── Reading speed ≤ 15 chars/second
```

### Step 3: Cultural Adaptation

| Element | Adapt | Keep |
|---------|-------|------|
| Character names | May adapt for phonetic fit | Keep meaning/theme if possible |
| Food references | Use regionally familiar foods | Maintain nutritional context |
| Holiday references | Use regionally celebrated holidays | Maintain emotional tone |
| Animal references | Use regionally known animals | Maintain role in story |
| Color associations | Use culturally appropriate examples | Maintain educational objective |
| Songs about letters | Adapt for target alphabet | Maintain educational structure |
| Counting songs | Numbers are universal | Maintain pacing and repetition |
| Social scenarios | Adapt to local norms | Maintain kindness/respect message |

**Example Adaptations**:

| English | Spanish | French | German | Chinese | Japanese |
|---------|---------|--------|--------|---------|----------|
| Apple pie | Pastel de manzana | Tarte aux pommes | Apfelkuchen | 苹果派 (píngguǒ pài) | アップルパイ (appuru pai) |
| Barn | Granero | Grange | Scheune | 谷仓 (gǔcāng) | 納屋 (naya) |
| Fairy | Hada | Fée | Fee | 仙女 (xiānnǚ) | 妖精 (yōsei) |
| Snowman | Muñeco de nieve | Bonhomme de neige | Schneemann | 雪人 (xuěrén) | 雪だるま (yukidaruma) |

### Step 4: Recording Target Language

#### Voice Casting Guidelines

| Character | Voice Requirements by Language |
|-----------|-------------------------------|
| Lily Bunny | Female, medium-high pitch, playful, neutral accent in target language |
| Max Bear | Male, medium pitch, warm, gentle, patient |
| Zara Cat | Female, medium-high pitch, curious, clever |
| Oliver Dog | Male, medium pitch, energetic, enthusiastic |
| Narrator | Warm, calm, clear pronunciation, appropriate for target language |

#### Recording Standards

- Same microphone and recording environment as source
- Same distance from mic (6–12 inches)
- Same sample rate and bit depth (48kHz 24-bit)
- Match source timing as closely as possible
- Record multiple takes for each line
- Label files with episode, character, and language code

#### File Naming Convention

```
AINursery_Ep012_CharacterName_Dialogue_LANG.wav
```

Example:
```
AINursery_Ep012_LilyBunny_Dialogue_ES.wav
```

### Step 5: Remixing

1. Import original master session
2. Mute source dialogue and vocal stems
3. Import target-language dialogue and vocal stems
4. Align timing (stretch or compress if needed, ≤5% adjustment)
5. Apply language-appropriate reverb to dialogue
6. Re-check level balance:
   - Dialogue: -6 dB to -3 dB
   - Vocals: -9 dB to -6 dB
   - Music/SFX: unchanged
7. Listen for natural integration

### Step 6: Localized Mastering

- Apply the same mastering chain as the source (see MASTERING_GUIDE.md)
- Target: -14 LUFS integrated, -1 dB true peak
- Compare loudness against source master
- Check that localized vocals sit naturally in the mix

### Step 7: Export Localized Master

| Format | Spec | Naming |
|--------|------|--------|
| Master WAV | 48kHz 24-bit | AINursery_Ep012_Title_LANG.wav |
| Distribution MP3 | 320kbps | AINursery_Ep012_Title_LANG.mp3 |
| Dialogue Stem WAV | 48kHz 24-bit | AINursery_Ep012_Stem_Dialogue_LANG.wav |
| Vocal Stem WAV | 48kHz 24-bit | AINursery_Ep012_Stem_Vocals_LANG.wav |

---

## Lyric Translation Guidelines

### Priority 1: Singability

The translated lyric must fit the original melody. Syllable count per line is critical.

```
English:     "The sun is up, it's time to play"  (8 syllables)
Spanish:     "El sol salió, es hora de jugar"    (8 syllables) ✓
French:      "Le soleil est levé, c'est l'heure" (9 syllables) — adjust melody ✓
German:      "Die Sonne scheint, es ist Spielzeit" (9 syllables) — adjust melody ✓
```

### Priority 2: Rhyme

Preserve the rhyme scheme if possible.

| Scheme | Must Match |
|--------|------------|
| AABB | Lines 1-2 rhyme, lines 3-4 rhyme |
| ABAB | Lines 1-3 rhyme, lines 2-4 rhyme |
| ABCB | Lines 2 and 4 rhyme |

### Priority 3: Educational Content

- Key vocabulary words must be preserved in meaning
- Counting, letters, colors, shapes must transfer exactly
- Emotional vocabulary should match in developmental level

### Priority 4: Character Voice

- A shy character should sound shy in all languages
- An energetic character should sound energetic in all languages
- Personality adjectives from voice profiles should inform translation choices

---

## Cultural Adaptation Guide

### Character Names

| English | Spanish | French | German | Chinese | Japanese |
|---------|---------|--------|--------|---------|----------|
| Lily Bunny | Lily Conejo | Lily Lapin | Lily Hase | 莉莉兔 (Lìlì Tù) | リリ・バニー (Riri Banī) |
| Max Bear | Max Oso | Max Ours | Max Bär | 马克斯熊 (Mǎkèsī Xióng) | マックス・ベア (Makkusu Bea) |
| Zara Cat | Zara Gato | Zara Chat | Zara Katze | 扎拉猫 (Zālā Māo) | ザラ・キャット (Zara Kyatto) |
| Oliver Dog | Oliver Perro | Oliver Chien | Oliver Hund | 奥利弗狗 (Àolìfú Gǒu) | オリバー・ドッグ (Oribā Doggu) |

**Strategy**: Keep English names where they are phonetically comfortable. Adapt where pronunciation would be challenging for the target audience.

### References to Adapt

| English Reference | Localization Strategy |
|-------------------|----------------------|
| "Apple pie" → universal or local pastry | Adapt to regionally recognized baked good |
| "Baseball" → region-specific sport | Use soccer (global), cricket (UK/India), etc. |
| "Snow" in winter song | Use regional cold-weather or alternative season |
| "Farm animals" → region-specific common animals | Include animals children in that region encounter |
| "School routine" → culturally accurate routine | Adapt lunch, recess, uniform norms |
| "Holiday" → locally celebrated | Christmas→Christmas or Lunar New Year as appropriate |

### Sensitive Content Check

| Topic | Guideline |
|-------|-----------|
| Religion | Avoid unless universal (gratitude, kindness) |
| Politics | Never reference |
| Violence | Zero tolerance in all markets |
| Gender roles | Avoid stereotypes in all markets |
| Family structures | Inclusive of diverse families in all markets |
| Disabilities | Present respectfully in all markets |

---

## Character Name Localization

### Strategy Options

1. **Keep original name**: Good for brand consistency. Example: "Lily" → "Lily"
2. **Phonetic adaptation**: Adjust spelling for target phonetics. Example: "Lily" → "Lili" (German)
3. **Meaning translation**: Translate the name's meaning. Example: "Lily" → "Lirio" (Spanish)
4. **Cultural equivalent**: Replace with culturally familiar name. Example: "Max" → "Mateo" (Spanish)

### Recommended Strategy by Language

| Language | Strategy | Example |
|----------|----------|---------|
| Spanish | Keep original or phonetic adaptation | Lily → Lily |
| French | Keep original | Lily → Lily |
| German | Keep original, adjust spelling | Lily → Lilli |
| Chinese | Phonetic translation with meaningful characters | Lily → 莉莉 (Lìlì, meaning "beautiful") |
| Japanese | Katakana phonetic transcription | Lily → リリ (Riri) |

---

## Subtitle Timing Standards

### Core Standards

| Parameter | Standard | Notes |
|-----------|----------|-------|
| Max lines | 2 lines | Never more than 2 simultaneous lines |
| Max characters per line | 32 characters | Including spaces |
| Max width | 80% of screen | Safe zone |
| Reading speed | ≤15 characters/second | For early readers (ages 3–6) |
| Minimum display time | 1.5 seconds | Below this, too fast to read |
| Maximum display time | 7 seconds | Above this, viewers re-read |
| Timing margin | 1 frame before speech start, 1 frame after | Prevents clipping |
| Gap between subtitles | 2 frames minimum | Prevents merging |

### Timing by Content Type

| Content Type | Reading Speed | Max Display Time |
|-------------|---------------|------------------|
| Dialogue | 15 chars/sec | 4 seconds |
| Song lyrics | 12 chars/sec | 6 seconds (highlighted) |
| Educational text | 10 chars/sec | 7 seconds |
| Sound description | 15 chars/sec | 3 seconds |

### Song Subtitle Timing

For karaoke-style song subtitles:
- Highlight each word/syllable as it is sung
- Use color coding per character (if multi-character song)
- Keep highlighted word on screen for minimum 0.5 seconds
- Advance highlight in sync with audio waveform

---

## Region-Specific Pronunciation Notes

### Spanish (es)

| Sound | Guideline | Example |
|-------|-----------|---------|
| "c" before e/i | Soft "th" (Castilian) or "s" (Latin American) | "cinco" → "theen-co" or "seen-co" |
| "ll" | "y" sound | "llama" → "yah-mah" |
| "j" | Soft "h" | "jugo" → "hoo-go" |
| "r" | Rolled single or double | "perro" → rolled r |
| "v" | Soft "b" | "vaca" → "bah-kah" |

### French (fr)

| Sound | Guideline | Example |
|-------|-----------|---------|
| Nasal vowels | Distinct nasal quality | "bon" → nasal 'o' |
| "r" | Guttural, throat-based | "rouge" → throat r |
| "u" | Pure, lips rounded | "lune" → pure 'ü' |
| Liaison | Link final consonant to next vowel | "les amis" → "lez ami" |
| Silent consonants | Many final consonants silent | "petit" → "puh-tee" |

### German (de)

| Sound | Guideline | Example |
|-------|-----------|---------|
| "ch" | Soft "ich" or hard "ach" | "ich" → soft 'ish', "acht" → guttural 'akh' |
| "r" | Rolled or uvular | "rot" → rolled or uvular r |
| "w" | "v" sound | "Wasser" → "vah-ser" |
| "v" | "f" sound | "Vogel" → "foh-gel" |
| "z" | "ts" sound | "Zeit" → "tsait" |
| Umlauts | Distinct vowel modifications | "ä" → air, "ö" → ur, "ü" → ew |

### Chinese (zh - Mandarin)

| Feature | Guideline | Example |
|---------|-----------|---------|
| Tones | 4 tones + neutral; critical for meaning | mā (妈, mother) vs mǎ (马, horse) |
| Pinyin | Use pinyin for pronunciation guides | 你好 → nǐ hǎo |
| "x" | "sh" sound with tongue forward | 西 (xī) → "shee" |
| "q" | "ch" sound with tongue forward | 七 (qī) → "chee" |
| "zh" | Retroflex "j" | 中 (zhōng) → "jong" |
| "c" | "ts" sound | 词 (cí) → "tsuh" |

### Japanese (ja)

| Feature | Guideline | Example |
|---------|-----------|---------|
| Syllabic rhythm | Mora-timed (each syllable gets equal length) | "To-kyo" → 4 morae (To-u-kyo-u) |
| "r" | Between English 'r' and 'd' | ら (ra) → tap r |
| "f" | Bilabial (both lips) | ふ (fu) → "f" without teeth on lip |
| "tsu" | Distinct from "su" | つ → "tsu", not "su" |
| Long vowels | Hold for double duration | おばさん (obasan) vs おばあさん (obaasan) |
| Pitch accent | Not tonal, but pitch patterns matter | はし (hashi) → chopsticks (L-H) vs bridge (H-L) |

---

## Localization Quality Checklist

### Pre-Production

- [ ] Dialogue script translated with character voice preserved
- [ ] Lyrics translated with syllable count matched to melody
- [ ] Cultural references reviewed and adapted
- [ ] Voice casting matches character profiles
- [ ] Recording studio meets technical specs

### Production

- [ ] Timing matched to source (±10%)
- [ ] Dry stems recorded (no baked effects)
- [ ] Multiple takes captured per line
- [ ] Pronunciation consistent with region guide

### Post-Production

- [ ] Dialogue levels match source: -6 dB to -3 dB
- [ ] Vocal levels match source: -9 dB to -6 dB
- [ ] Localized mix integrated naturally with stems
- [ ] Loudness matches source: -14 LUFS ±0.5
- [ ] No artifacts, clicks, or pops from editing

### Final QC

- [ ] Native speaker review (dialogue accuracy)
- [ ] Native speaker review (cultural appropriateness)
- [ ] Child test audience (ages 3–5) comprehension check
- [ ] Subtitle timing and reading speed verified
- [ ] Subtitle sync with audio verified
- [ ] All file naming and metadata correct
