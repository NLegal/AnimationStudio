# Audio Bible — Little Learning Town Studios

## Overview

Audio is the first thing children recognize. Before they understand words, they respond to melody, rhythm, and tone. A recognizable melody, voice, or sound effect becomes part of your brand. This Bible defines every aspect of the studio's audio identity so that every episode sounds like it belongs to the same world.

## Philosophy

Every audio asset in Little Learning Town must be:

| Attribute | Description |
|-----------|-------------|
| **Warm** | Soft tones, gentle attacks, no harsh frequencies |
| **Cheerful** | Bright major keys, bouncy rhythms, smiling delivery |
| **Educational** | Clear lyrics, intentional pacing, space for learning |
| **Memorable** | Repetition, simple melodies, earworm choruses |
| **Positive** | Upbeat lyrics, encouraging tone, constructive messages |
| **Calm** | Never overwhelming — high energy without chaos |
| **Clean** | Minimal noise floor, clear mix, crisp production |

## Audio Pipeline

```
Lyrics
      │
      ▼
Song Composition  ─── Suno (primary) / ACE-Step (offline backup)
      │
      ▼
Vocals  ───────────────── Kokoro / XTTS v2 / Piper
      │
      ▼
Character Voices ──────── XTTS v2 (recurring voices)
      │
      ▼
Dialogue  ─────────────── Kokoro (narration) / Piper (automation)
      │
      ▼
Sound Effects ─────────── Reusable SFX library
      │
      ▼
Ambient Audio ─────────── Bedroom, Kitchen, Playground, Forest, etc.
      │
      ▼
Mixing  ───────────────── Dialog → Vocals → SFX → Music → Ambience
      │
      ▼
Mastering ─────────────── Consistent loudness, no spikes, child-safe
      │
      ▼
Localization ──────────── Stems preserved for multi-language export
```

## Table of Contents

| Directory | Contents |
|-----------|----------|
| `Music/` | Style guide, song structures, categories, production templates |
| `Vocals/` | Vocal recordings, stems, session files |
| `CharacterVoices/` | Voice profiles for every recurring character |
| `Narration/` | Narrator standards and recordings |
| `Dialogue/` | Dialogue standards, scripts, recordings |
| `Foley/` | Foley sound effects library (book, chair, toys, etc.) |
| `SFX/` | Sound effects library (footsteps, animals, weather, etc.) |
| `Ambience/` | Ambient audio beds (bedroom, forest, rain, etc.) |
| `Mixes/` | Final mixed stereo tracks |
| `Masters/` | Mastered final deliverables |
| `Localization/` | Multi-language stems, alternate voice casts |
| `Lyrics/` | All song lyrics organized by category |
| `PronunciationDictionary/` | Approved pronunciations for names and places |
| `PromptTemplates/` | Reusable AI prompts for music and voice generation |
| `MusicTheory/` | Theory reference for prompt engineers |

## Quick Reference

| Parameter | Value |
|-----------|-------|
| **Tempo range** | 80–130 BPM (lullabies 60–80 BPM) |
| **Preferred keys** | C major, G major, F major |
| **Song durations** | 30s, 1min, 2min, 3min, 5min |
| **Time signature** | 4/4 (standard), 3/4 (lullabies) |
| **Primary generation** | Suno (cloud) |
| **Secondary generation** | ACE-Step Studio (offline) |
| **Narration** | Kokoro (fast, natural) |
| **Recurring voices** | XTTS v2 (multilingual) |
| **Automation** | Piper (lightweight, offline) |
| **Character voice pitch** | Medium-high for children, medium for adults |
| **Dialogue style** | Short sentences, simple vocab, positive tone |
| **Mixing priority** | Dialogue → Vocals → SFX → Music → Ambience |
| **Lip-sync reference** | 24 fps timing, standardized phoneme timing |
