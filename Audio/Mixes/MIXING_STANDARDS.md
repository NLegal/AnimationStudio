# Mixing Standards

## AI Nursery Studio — Audio Bible

### Version 1.0

---

## Introduction

This document defines the mixing standards for all AI Nursery Studio audio content. Every episode, song, and audio asset must conform to these specifications to ensure consistent, professional-quality audio across the entire catalog.

All mixes target preschool audiences (ages 2–6) and must prioritize clarity, warmth, and emotional safety. Harsh frequencies, excessive dynamics, and cluttered arrangements are unacceptable.

---

## Mixing Philosophy

| Principle | Description |
|-----------|-------------|
| **Clarity** | Dialogue and vocals must remain intelligible at all times. Every word should be understood on first listen. |
| **Warmth** | The overall tonal balance should feel inviting and gentle. Avoid bright, harsh, or aggressive EQ curves. |
| **Balance** | All elements coexist without fighting for space. Nothing distracts from the core educational content. |
| **Consistency** | Every episode sounds like it belongs to the same studio. Loudness, tone, and spatial placement remain uniform. |
| **Safety** | No sudden loud sounds, no extreme frequencies, no jarring transitions. The mix must never startle a child. |

---

## Loudness Standards

| Metric | Target | Notes |
|--------|--------|-------|
| **Integrated LUFS** | -14 LUFS | Streaming standard (Spotify, Apple Music, YouTube) |
| **Short-term LUFS** | -14 LUFS ±1 | Measured over 3-second windows |
| **True Peak Max** | -2 dBTP | Headroom for lossy codec conversion |
| **Dynamic Range** | 8–12 LU | Consistent without being fatiguing |
| **LRA (Loudness Range)** | 6–10 LU | Avoid extreme verse-to-chorus jumps |

### Compliance Notes

- Measure using ITU-R BS.1770-4 compliant meters (e.g., Youlean Loudness Meter, iZotope Insight)
- Verify on all target platforms: Spotify normalization targets -14 LUFS, YouTube targets -14 LUFS, Apple Music targets -16 LUFS (tolerate the -2dB headroom)
- If exporting for broadcast (future), adjust to -23 LUFS (EBU R128) with separate profile

---

## Channel Levels Reference

These are starting points. Adjust per scene context but always return to these baselines.

### Dialogue (Highest Priority)

| Context | Level | Notes |
|---------|-------|-------|
| Speaking (normal) | -6 dB to -3 dB | Always the clearest element in the mix |
| Speaking (whisper) | -12 dB to -9 dB | Still intelligible, never buried |
| Speaking (excited) | -3 dB to 0 dB | Brief peaks only |
| Character narration | -6 dB to -4 dB | Consistent across all narrator variants |

### Vocals (Singing)

| Context | Level | Notes |
|---------|-------|-------|
| Solo vocal | -9 dB to -6 dB | Lead singing sits below speaking dialogue |
| Chorus/group | -12 dB to -9 dB per voice | Blend together, no single voice dominates |
| Call-and-response lead | -9 dB to -6 dB | Lead voice clear above group |
| Call-and-response group | -12 dB to -9 dB | Response voices support the lead |

### Music Bed

| Context | Level | Notes |
|---------|-------|-------|
| Under dialogue | -18 dB to -12 dB | Music supports, never competes |
| Under singing | -15 dB to -10 dB | Slightly louder but vocals still lead |
| Solo (intro/outro) | -9 dB to -6 dB | Full presence, no vocal to compete with |
| Transition/sting | -6 dB to -3 dB | Brief moments only |

### Sound Effects

| Context | Level | Notes |
|---------|-------|-------|
| Supporting SFX | -12 dB to -9 dB | Reinforces the action |
| Emphasis SFX | -9 dB to -6 dB | Rare, for important moments |
| Background SFX | -18 dB to -15 dB | Sets the scene subtly |
| UI/magical sounds | -15 dB to -10 dB | Sparkles, bells, transitions |

### Foley

| Context | Level | Notes |
|---------|-------|-------|
| Natural actions | -15 dB to -12 dB | Footsteps, grabbing objects |
| Close-up actions | -12 dB to -9 dB | Eating, writing, drawing |
| Background movement | -18 dB to -15 dB | Chair scoots, page turns |

### Ambience

| Context | Level | Notes |
|---------|-------|-------|
| Room tone | -24 dB to -20 dB | Barely perceptible |
| Outdoor ambience | -18 dB to -15 dB | Birds, wind, distant play |
| Indoor ambience | -20 dB to -18 dB | Classroom hum, kitchen sounds |
| Nature ambience | -18 dB to -15 dB | Forest, beach, rain sounds |

---

## EQ Guidelines

### Dialogue EQ

| Frequency | Action | Purpose |
|-----------|--------|---------|
| Below 80 Hz | High-pass roll-off (24 dB/octave) | Remove rumble, muddiness |
| 200–400 Hz | Gentle cut (1–2 dB) if muddy | Reduce boxiness |
| 2–4 kHz | Gentle boost (1–3 dB) | Add clarity and presence |
| 5–8 kHz | Gentle boost (0–1 dB) if needed | Add air without sibilance |
| Above 10 kHz | High-shelf cut if sibilant | Control excessive sibilance |

### Music EQ

| Frequency | Action | Purpose |
|-----------|--------|---------|
| Below 40 Hz | High-pass roll-off | Remove sub-bass rumble |
| 200–400 Hz | Gentle boost (1–2 dB) | Add warmth and body |
| 800 Hz–2 kHz | Cut 1–2 dB if cluttered | Clear space for vocals |
| 5–10 kHz | Gentle shelf (0–1 dB) | Add brightness |

### Sound Effects EQ

- Match the EQ to the scene's frequency context
- Roll off low end below 100 Hz for non-bass SFX
- Cut 2–4 kHz region if SFX competes with dialogue
- Use high-pass filter aggressively on background SFX

### Ambience EQ

- Heavy high-pass filter (100–200 Hz)
- Gentle low-pass filter (8–10 kHz) for realism
- Cut mid-range (500 Hz–2 kHz) to avoid masking dialogue
- Keep ambience spectrally thin

---

## Compression

### Dialogue Compression

| Parameter | Setting |
|-----------|---------|
| Ratio | 2:1 |
| Threshold | -18 dB to -14 dB |
| Attack | 5–10 ms |
| Release | 50–100 ms |
| Gain | 2–4 dB makeup |
| Knee | Soft |

### Vocal (Singing) Compression

| Parameter | Setting |
|-----------|---------|
| Ratio | 3:1 |
| Threshold | -16 dB to -12 dB |
| Attack | 5–10 ms |
| Release | 40–60 ms |
| Gain | 3–5 dB makeup |
| Knee | Soft |

### Music Bus Compression

| Parameter | Setting |
|-----------|---------|
| Ratio | 2:1 (gentle glue) |
| Threshold | -20 dB to -18 dB |
| Attack | 10–30 ms |
| Release | Auto or 100 ms |
| Gain | 1–3 dB makeup |

### Master Bus Compression

| Parameter | Setting |
|-----------|---------|
| Ratio | 1.5:1 to 2:1 |
| Threshold | -22 dB to -18 dB |
| Attack | 10–30 ms |
| Release | 100–250 ms |
| Gain | 1–2 dB makeup |
| Notes | Very gentle. Preserve dynamics. |

---

## Reverb

| Type | Decay Time | Application |
|------|------------|-------------|
| Short Room | 0.4–0.6 s | Dialogue, everyday scenes |
| Medium Room | 0.6–0.8 s | Classroom, kitchen, indoor play |
| Long Room | 0.8–1.2 s | Large indoor spaces (gym, hall) |
| Hall | 1.2–1.8 s | Fantasy sequences, magical moments |
| Chamber | 0.8–1.5 s | Vocals in songs |
| Plate | 1.5–2.5 s | Solo instrument, emphasis moments |
| Ambience | 0.3–0.5 s | Subtle spatial placement |

### Reverb Mix Levels

| Element | Wet/Dry Mix |
|---------|-------------|
| Dialogue | 10–20% wet |
| Vocals (songs) | 15–30% wet |
| Music | 10–20% wet |
| SFX | 5–15% wet |
| Foley | 0–10% wet (mostly dry) |

### Pre-Delay Guidelines

- Dialogue: 10–20 ms pre-delay
- Vocals: 20–40 ms pre-delay
- Music: 30–50 ms pre-delay

---

## Stereo Imaging

| Element | Pan Position | Width |
|---------|-------------|-------|
| Dialogue | Center (mono) | 100% center |
| Lead vocal | Center (mono) | 100% center |
| Backing vocals | 30–50 L/R | Spread evenly |
| Music bed | Full stereo | 100% width |
| SFX (action) | Match screen position | Variable |
| SFX (background) | 40–60 L/R | Medium-wide |
| Foley | Center to 20 L/R | Narrow |
| Ambience | Full stereo | 100% width |

### Mono Compatibility

- All mixes must sum to mono without phase cancellation
- Check phase correlation meter: target +0.5 to +1.0
- Never use stereo widening plugins that compromise mono

---

## Reference Tracks

Maintain a library of approved reference tracks:

1. Select 1–2 reference episodes as gold standards
2. Keep at least 3 reference mixes per song category
3. Compare every new mix against the nearest reference
4. Update references only when quality improves

### Reference Check Procedure

1. Import reference track on separate channel in DAW
2. Match gain to -14 LUFS integrated
3. Alternate between reference and new mix (blind A/B)
4. Note differences in: tonal balance, loudness, clarity, spatial feel
5. Adjust mix until it matches reference quality

---

## Export Formats

| Format | Spec | Use |
|--------|------|-----|
| WAV | 48 kHz, 24-bit, interleaved stereo | Master archive, stems |
| Broadcast WAV | 48 kHz, 24-bit, with BWF metadata | Broadcast delivery |
| MP3 | 320 kbps, joint stereo, dither applied | Distribution, preview |
| FLAC | 48 kHz, 24-bit, lossless compression | Archival |
| AAC | 256 kbps, LC-AAC | Podcast, mobile delivery |

### File Naming Convention

```
StudioName_EpisodeNumber_Title_Version.wav
```

Example:
```
AINursery_Ep012_FunWithLetters_v2.wav
```

---

## Stem Separation

Every episode and song project must export stems:

| Stem | Contents | Format |
|------|----------|--------|
| Dialogue stem | All spoken lines, no music/SFX | WAV 48kHz 24-bit mono |
| Vocal stem | All sung vocals | WAV 48kHz 24-bit stereo |
| Music stem | All instrumental music | WAV 48kHz 24-bit stereo |
| SFX stem | All sound effects | WAV 48kHz 24-bit stereo |
| Foley stem | All foley sounds | WAV 48kHz 24-bit stereo |
| Ambience stem | All ambient backgrounds | WAV 48kHz 24-bit stereo |
| Full mix | Complete stereo master | WAV 48kHz 24-bit stereo |

### Stem Naming

```
AINursery_Ep012_FunWithLetters_Stem_Dialogue.wav
AINursery_Ep012_FunWithLetters_Stem_Music.wav
AINursery_Ep012_FunWithLetters_Stem_SFX.wav
```

### Why Stems Matter

- **Localization**: Replace dialogue stem with new language without remixing
- **Music replacement**: Swap music stem for regional versions
- **Editing**: Adjust levels globally without redoing the mix
- **Future-proofing**: Revisit episodes years later with full access
