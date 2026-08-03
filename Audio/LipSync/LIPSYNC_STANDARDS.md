# Lip-Sync Standards

## AI Nursery Studio — Audio Bible

### Version 1.0

---

## Introduction

Lip-sync connects the audio pipeline to the animation pipeline. Every dialogue
line and song lyric must produce a phoneme track that the animator can drive
mouth shapes from. Because audio and animation share a single master timecode,
phoneme timing must be standardized so any episode, character, or language syncs
identically.

---

## Master Timing Reference

| Parameter | Value | Notes |
|-----------|-------|-------|
| Master frame rate | **24 fps** | Shared with the animation pipeline |
| Timecode source | Single master timecode | Audio and animation use one clock |
| Beat grid | 24 frames per 2 beats at 120 BPM | Music sections align to the frame grid |
| Bars to frames | Frames per beat = 2,400 / BPM | See `Music/SONG_STRUCTURE.md` |

Every phoneme, word boundary, and section boundary lands on this grid.

---

## Phoneme Timing

| Element | Standard | Notes |
|---------|----------|-------|
| Phoneme duration | **4–6 frames per phoneme** | Phase 4 mouth library (PHONEME_MOUTH_MAP) |
| Phoneme placement | Frame-aligned, no fractional frames | Offsets must be integers |
| Word pause | 6–8 frames | Clear word boundaries |
| Sentence pause | 12–18 frames | Natural processing time |
| Dialogue pacing | ~2.5 words per second | Phase 5 dialogue standard |

Consistent mouth shapes: a recurring sound always maps to the same mouth shape.
Do not invent new mouth shapes for the same phoneme between episodes.

---

## Per-Phoneme Guidance

| Phoneme | Mouth Shape | Timing Note |
|---------|-------------|-------------|
| Vowel (long, e.g. /iː/ /eɪ/) | Open | Hold 4–6 frames, shape steady |
| Vowel (short, e.g. /æ/ /ʌ/) | Mid-open | 4–5 frames, quick release |
| Consonant (plosive, /p/ /b/) | Closed then open | Closure 2–3 frames before burst |
| Consonant (fricative, /s/ /f/) | Slightly closed, lip near teeth | Hold 3–5 frames |
| Nasal (/m/ /n/) | Lips together / tongue up | 4–6 frames |
| Silent pause | Closed (relaxed) | Use word/sentence pause standards |

All shapes map to the mouth shapes defined in the Phase 4 animation bible.

---

## Timing Reference for Common Tempos

At **110 BPM** (common educational tempo), per `Music/SONG_STRUCTURE.md`:

| Section | Bars | Time | Frames (24fps) |
|---------|------|------|----------------|
| Intro | 4 | ~8.7s | 209 |
| Verse | 8 | ~17.5s | 418 |
| Chorus | 8 | ~17.5s | 418 |
| Bridge | 4 | ~8.7s | 209 |
| Outro | 4 | ~8.7s | 209 |

Section boundaries are natural cut points for the animator. Lyrics should never
cross a section boundary mid-word.

---

## Song Lip-Sync

- Keep lyrics on the beat grid (24 frames per 2 beats at 120 BPM)
- Hold final vowel of each line for the bar's duration when the melody sustains
- Call-and-response pauses (2–3 seconds) stay silent on the phoneme track
- Chorus repetitions reuse the same phoneme track (identical or near-identical)

---

## Localization Note

Phoneme tracks are language-specific. When a dialogue or vocal stem is replaced
for a locale, the phoneme track is regenerated from the target-language line
against the same 24 fps grid. Never stretch the source phoneme track across a
language change.

---

## Quality Checklist

Every lip-sync track must verify:

- [ ] Phoneme durations are 4–6 frames each
- [ ] All timestamps are frame-aligned (24 fps)
- [ ] Word pauses 6–8 frames, sentence pauses 12–18 frames
- [ ] Recurring phonemes reuse the same mouth shape
- [ ] Lyrics stay within section boundaries
- [ ] Pauses in call-and-response are silent
- [ ] Track regenerated per locale

---

*Part of the AI Nursery Rhyme Studio — Audio Bible*
*Version 1.0 — 2026-08-03*
