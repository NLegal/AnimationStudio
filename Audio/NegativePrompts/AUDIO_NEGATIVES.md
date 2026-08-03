# Audio Negative Prompts

## AI Nursery Studio — Prompt Engineering Guide

### Version 1.0

---

## Introduction

Negative prompts tell the AI what *not* to generate. For preschool audio, the
same safety rules apply across every asset: no harsh, scary, loud, or complex
sounds. Every generation should layer the base negative block with a
per-category block.

---

## Base Negative Block

Apply to every audio generation:

```
harsh, jarring, aggressive, distorted, shrill, scary, frightening, menacing,
sad, dark, loud, overwhelming, abrupt, chaotic, complex, adult content,
bad quality, robotic, monotone
```

---

## Per-Category Negative Blocks

### Music

```
harsh arrangement, dissonant, atonal, aggressive drums, distorted guitar,
minor-key menace, sad, scary, chaotic, loud noise, abrupt changes, off-key,
out of tune, adult style
```

### Voice (character / narrator)

```
robotic, monotone, flat, emotionless, adult voice, gruff, harsh, nasal,
whispery, garbled, mumbled, slurred, unclear pronunciation, creepy, unnatural,
glitchy
```

### Singing

```
off-key, breathy, strained, shouty, whispery, robotic, flat, no emotion,
mumbling, unclear lyrics, autotune artifacts, glitchy
```

### Sound Effects (SFX)

```
harsh, loud, distorted, distorted noise, clipping, shrill, scary, startling,
violent, metallic screech, unpleasant, jarring
```

### Foley

```
harsh, loud, distorted, creaky, screeching, scraping, jarring, startling,
mechanical noise, unpleasant
```

### Ambience

```
loud, dominant, hissing, harsh, droning, artificial, abrupt, startling,
distracting, noisy
```

### Mastering

```
clipping, distortion, harsh highs, muddy lows, loudness war, over-compressed,
digital artifacts, phase issues, shrill, boomy
```

---

## Usage Rules

1. Always start with the base negative block.
2. Append the per-category block for the asset being generated.
3. Keep the negative blocks stable across episodes so output style is consistent.
4. Record any prompt that needed extra negatives in the prompt test log.

---

*Part of the AI Nursery Rhyme Studio — Audio Bible*
*Version 1.0 — 2026-08-03*
