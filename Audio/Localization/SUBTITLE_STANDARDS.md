# Subtitle Standards

## AI Nursery Studio — Localization Guide

### Version 1.0

---

## Introduction

Subtitles for preschool content require special considerations. Young children (ages 2–6) are developing their reading skills, and subtitles must support comprehension without creating cognitive overload.

These standards apply to all subtitles across episodes, songs, and promotional content.

---

## Formatting Standards

### Basic Specs

| Parameter | Standard | Notes |
|-----------|----------|-------|
| Max lines | 2 lines | Never exceed 2 simultaneous lines |
| Max characters per line | 32 characters | Including spaces and punctuation |
| Max total characters | 64 characters | Across both lines |
| Reading speed | ≤15 characters/second | For early readers |
| Min display time | 1.5 seconds | Below this is too fast |
| Max display time | 7 seconds | Above this, viewers re-read |
| Line break | Logical phrase break | Never split words or articles from nouns |
| Font | Rounded sans-serif | See font section below |
| Font size | Minimum 24pt | Larger recommended for preschool |
| Position | Bottom center | See placement section |
| Background | Semi-transparent box | Ensures readability on any background |

### Line Breaks

Good:
```
The sun is shining
in the sky today.
```

Bad (article split):
```
The sun is shining in
the sky today.
```

Bad (too many characters):
```
The sun is shining in the sky today and it's very bright.
```

### Punctuation

- Use periods at the end of subtitle blocks (unless continuous speech)
- Use commas for natural pauses
- Use question marks and exclamation marks normally
- Avoid semicolons and colons (too complex for early readers)
- Avoid ellipses (...) unless indicating trailing speech
- Avoid parentheses and quotation marks (use context instead)

---

## Timing Standards

### Core Timing

| Event | Timing Rule |
|-------|-------------|
| Subtitle appears | 1 frame before speech begins |
| Subtitle disappears | 1 frame after speech ends |
| Min gap between subtitles | 2 frames (approximately 83ms at 24fps) |
| Simultaneous speakers | Max 2 lines (one per speaker with dash prefix) |

### Timing by Content

| Content Type | Max Reading Speed | Min Display | Max Display |
|-------------|-------------------|-------------|-------------|
| Dialogue | 15 chars/sec | 1.5 seconds | 4 seconds |
| Song lyrics (static) | 12 chars/sec | 2 seconds | 6 seconds |
| Song lyrics (karaoke) | N/A (word-highlighted) | 0.5 sec per word | Per phrase |
| Educational labels | 10 chars/sec | 2 seconds | 7 seconds |
| Sound descriptions | 15 chars/sec | 1.5 seconds | 3 seconds |

### Timing Examples

```
Line: "Hello, friends!"
Length: 14 characters
Minimum display time: 14/15 = 0.93s → Round up to 1.5s minimum
Display: 1 frame before "Hello", 1 frame after "friends!"

Line: "Let's all count to ten together!"
Length: 29 characters
Minimum display time: 29/15 = 1.93s → Round up to 2.0s
Display: 1 frame before line starts, 1 frame after line ends
```

---

## Color Coding

### Optional: Per-Character Colors

Color coding helps children identify who is speaking without reading attribution.

| Character | Color | Hex Code |
|-----------|-------|----------|
| Lily Bunny | Pink | #FF69B4 |
| Max Bear | Blue | #4A90D9 |
| Zara Cat | Purple | #9B59B6 |
| Oliver Dog | Orange | #E67E22 |
| Narrator | White | #FFFFFF |
| Group/Chorus | Green | #2ECC71 |
| Other characters | Yellow | #F1C40F |

### Color Rules

- Use color coding only when 2+ characters speak in the same scene
- Maintain consistent character colors across all episodes
- Use white for single-speaker scenes
- Ensure sufficient contrast with subtitle background
- Test colors on both bright and dark backgrounds
- For karaoke songs, use character color for currently highlighted word

---

## Font Specifications

### Primary Font: Rounded Sans-Serif

| Property | Specification |
|----------|---------------|
| Font family | Nunito, Fredoka One, or Comic Neue |
| Fallback | Arial Rounded MT Bold, Verdana |
| Weight | Semi-Bold (600) or Bold (700) |
| Size | Minimum 24pt, recommended 28-32pt |
| Style | Regular (not italic, not condensed) |
| Letter spacing | 0.5–1.0px (increased for readability) |
| Line height | 1.4x font size |
| Color | White (#FFFFFF) |
| Background | Semi-transparent black box (#000000 at 75% opacity) |
| Shadow | Optional: 1px black shadow for additional contrast |

### Why Rounded Sans-Serif

- More recognizable letter shapes for early readers
- Rounded corners feel friendlier and less formal
- Better differentiation between similar letters (b/d, p/q)
- Clean, simple shapes reduce visual noise

---

## Placement

### Standard Position

```
┌─────────────────────────────────┐
│                                 │
│                                 │
│         Video Content           │
│                                 │
│                                 │
│  ┌─────────────────────────┐    │
│  │ Subtitle text here       │    │
│  └─────────────────────────┘    │
│                                 │
└─────────────────────────────────┘
```

### Placement Rules

- **Vertical**: Bottom 10–15% of the screen, safe zone
- **Horizontal**: Center-aligned
- **Clearance**: Minimum 5% of screen height from bottom edge
- **Avoid covering**: Faces, mouths (for lip reading), important visual elements, text/number graphics
- **Dynamic placement**: If bottom is occupied (e.g., by character), move to top of screen (rare)

### Safe Zone

Assuming 1920×1080 resolution (scaled proportionally for other resolutions):

| Zone | Position | Usage |
|------|----------|-------|
| Active video | 0–80% height | Never place subtitles here |
| Subtitle zone | 80–90% height | Standard subtitle placement |
| Bottom margin | 90–100% height | Keep clear of subtitles |

---

## Karaoke-Style Song Subtitles

### Format

For musical segments, use karaoke-style highlighting:

```
Standard view:
  Twinkle, twinkle, little star
  How I wonder what you are

Highlighted view (word by word):
  [Twinkle] twinkle, little star
  How I wonder what you are
  
  Twinkle [twinkle] little star
  How I wonder what you are
```

### Implementation

| Feature | Specification |
|---------|---------------|
| Highlight color | Per-character color (see above) or white default |
| Background text | Semi-transparent gray (#808080 at 50% opacity) |
| Word transition | Instant (no fade) |
| Timing accuracy | ±1 frame of sung word |
| Min highlight duration | 0.5 seconds per word |
| Line advance | Full line advances when last word highlighted |

### Multi-Character Songs

```
Lily (pink):  [Let's] sing together, you and me
Max (blue):   Let's [sing] together, happily
Both (green): Let's sing [together], happily
Both (green): Let's sing together, [happily]
```

---

## Subtitle File Formats

### Primary: SRT

```
1
00:00:01,500 --> 00:00:04,000
Hello, friends!
Let's play together.

2
00:00:04,500 --> 00:00:07,000
Today we're going to learn
about colors!
```

### Secondary: ASS (Advanced)

For karaoke highlighting and color coding:

```
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.50,0:00:04.00,Default,Lily,,0,0,0,,
{\c&HFF69B4&}Hello{\c}, friends!

Dialogue: 0,0:00:04.50,0:00:07.00,Default,Max,,0,0,0,,
{\c&H4A90D9&}Today{\c}, we will learn together!
```

### Delivery Spec

| Format | Use | Notes |
|--------|-----|-------|
| SRT | Universal distribution | Most widely supported |
| ASS | Advanced formatting | Karaoke, colors, positioning |
| VTT | Web distribution | For HTML5 video players |
| SSA | Legacy support | When ASS not available |

---

## Subtitle Content Guidelines

### Dialogue Subtitles

- Use simple vocabulary matching the audio
- Keep sentence structure parallel to audio
- Do not paraphrase or simplify beyond what is spoken
- Add sound descriptions in brackets: [bell rings], [music plays]
- Identify off-screen speakers: [Lily] Where are you?
- Use dashes for simultaneous speakers: -I think so. -Me too!

### Song Lyric Subtitles

- Match lyrics exactly as sung (including repeated words)
- Use karaoke highlighting when possible
- Keep line breaks at musical phrase boundaries
- Indicate group singing: [All] We love to sing!

### Educational Content

- Highlight numbers, letters, and key vocabulary when possible
- Keep on screen long enough for a child to recognize the word
- Consider using larger font or bold for key educational words
- Match visual text if it appears on screen (color names, number labels)

### Sound Descriptions

- Use brackets: [thunder rumbles], [door creaks]
- Place before the sound occurs (100–200ms lead time)
- Keep to 3–4 words maximum
- Only use for important plot-relevant sounds
- Avoid describing obvious visual actions

---

## Accessibility Considerations

### Visual Accessibility

- High contrast between text and background
- Semi-transparent background box on all subtitles
- No thin or light-colored fonts
- Avoid placing subtitles over bright/white backgrounds
- Consider dyslexia-friendly font (e.g., OpenDyslexic) for accessibility track

### Hearing Accessibility

- Include speaker identification for off-screen characters
- Describe music mood in brackets: [happy music], [gentle lullaby]
- Describe emotional tone when not obvious from visuals
- Include sound effect descriptions for plot-relevant sounds

### Cognitive Accessibility

- Consistent timing and formatting across all episodes
- Predictable line-break patterns
- Avoid flashing or rapidly changing subtitles
- No simultaneous text and graphic that competes for attention

---

## Per-Platform Requirements

| Platform | Format | Max Lines | Notes |
|----------|--------|-----------|-------|
| YouTube | SRT or VTT | 2 lines | Auto-sync; 32 char limit recommended |
| Netflix | SRT (TTML for higher quality) | 2 lines | 42 char limit (slightly more permissive) |
| Disney+ | SRT | 2 lines | 38 char limit; timed to audio precisely |
| Amazon Prime | SRT or VTT | 2 lines | 32 char limit recommended |
| Apple TV+ | SRT or iTunes-style | 2 lines | 32 char limit; 24pt minimum font |
| Broadcast TV | Teletext or DVB subs | 2 lines | 32 char limit; font determined by broadcaster |

---

## File Naming Convention

```
StudioName_EpisodeNumber_Title_LANG.srt
```

Examples:
```
AINursery_Ep012_FunWithLetters_EN.srt
AINursery_Ep012_FunWithLetters_ES.srt
AINursery_Ep012_FunWithLetters_FR.srt
```

### Language Codes

| Code | Language |
|------|----------|
| EN | English |
| ES | Spanish |
| FR | French |
| DE | German |
| ZH | Chinese (Simplified) |
| JA | Japanese |
| PT | Portuguese |
| IT | Italian |
| NL | Dutch |
| KO | Korean |
| AR | Arabic |
| HI | Hindi |

---

## QC Checklist for Subtitles

### Accuracy

- [ ] Subtitle text matches audio dialogue exactly
- [ ] Song lyrics match sung lyrics exactly
- [ ] No spelling or grammar errors
- [ ] Punctuation is correct and consistent
- [ ] Speaker identification is correct (if applicable)

### Timing

- [ ] In time: 1 frame before speech
- [ ] Out time: 1 frame after speech
- [ ] No overlaps between consecutive subtitles
- [ ] Reading speed ≤ 15 chars/second
- [ ] Minimum display time: 1.5 seconds
- [ ] Maximum display time: 7 seconds
- [ ] Karaoke timing: ±1 frame accuracy

### Formatting

- [ ] Max 2 lines per subtitle
- [ ] Max 32 characters per line
- [ ] Line breaks at logical phrase boundaries
- [ ] Font: rounded sans-serif, minimum 24pt
- [ ] Position: bottom center, safe zone
- [ ] Semi-transparent background applied
- [ ] Color coding consistent (if used)

### Accessibility

- [ ] Sound descriptions in brackets for important sounds
- [ ] Speaker identification for off-screen characters
- [ ] High contrast between text and background
- [ ] No flashing or rapidly changing subtitles

### Technical

- [ ] File format correct (SRT/ASS/VTT)
- [ ] File naming follows convention
- [ ] Timestamps use correct format (HH:MM:SS,mmm)
- [ ] No HTML or unsupported tags in SRT files
- [ ] Character encoding: UTF-8 (all languages)
- [ ] Line endings: Unix (LF) or Windows (CRLF) consistent
