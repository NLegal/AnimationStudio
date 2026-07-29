# Mastering Guide

## AI Nursery Studio — Audio Bible

### Version 1.0

---

## Introduction

Mastering is the final quality gate before audio reaches the audience. For preschool content, mastering must preserve clarity, warmth, and dynamic life while meeting streaming platform loudness standards.

Every master should sound polished but never squashed. The goal is consistency across episodes — not maximum loudness.

---

## Mastering Chain

Apply the following processing chain in order:

### Step 1: EQ (Corrective)

| Frequency | Action | Purpose |
|-----------|--------|---------|
| Below 30 Hz | Steep high-pass filter (48 dB/octave) | Remove subsonic rumble |
| 40–60 Hz | Gentle boost (0.5–1.5 dB) if mix feels thin | Add warmth |
| 200–400 Hz | Listen for muddiness; cut 1–2 dB if needed | Clean up low-mids |
| 2–4 kHz | Gentle presence boost (0.5–1 dB) | Clarity for dialogue |
| 8–12 kHz | Air shelf (0.5–1 dB boost) | Sparkle without harshness |
| Above 16 kHz | Gentle low-pass if noisy | Control hiss |

**Important**: Preschool mixes should never have aggressive EQ curves. Never boost more than 2 dB at any frequency.

### Step 2: Compression (Glue)

| Parameter | Setting |
|-----------|---------|
| Style | Opto or VCA emulation |
| Ratio | 1.5:1 to 2:1 |
| Threshold | -22 dB to -18 dB |
| Attack | 10–30 ms |
| Release | 100–250 ms (or auto) |
| Makeup Gain | 1–2 dB |
| GR (gain reduction) | 0.5–2 dB maximum |

- The compressor is for gentle cohesion, not dynamics control
- If more than 2 dB of gain reduction is needed, fix the mix
- Use a bus compressor with character (e.g., SSL-style, API-style)

### Step 3: Limiting

| Parameter | Setting |
|-----------|---------|
| Ceiling | -1.0 dBTP (true peak) |
| Threshold | Adjust until integrated loudness target is met |
| Attack | 0.5–1.0 ms |
| Release | 10–50 ms (program-dependent) |
| GR | 2–4 dB maximum |
| Style | Clean, transparent limiter |

- Target final output: -14 LUFS integrated at -1 dBTP ceiling
- Never allow more than 5 dB of gain reduction
- Listen for distortion, pumping, or loss of dynamics
- Finalize with true peak metering active

### Step 4: Dither

| Parameter | Setting |
|-----------|---------|
| Type | Noise-shaped (e.g., MBIT+ or POW-r Type 3) |
| Bit Depth | Reduce to 16-bit for distribution, 24-bit for archives |
| Noise Level | -4 dB below noise floor |

- Apply dither only during the final bit-depth conversion
- No dither needed when exporting 24-bit masters
- Use flat dither for dialogue-only exports

---

## Target Loudness

| Metric | Target | Tolerance |
|--------|--------|-----------|
| Integrated LUFS | -14 LUFS | ±0.5 LU |
| Short-term LUFS | -14 LUFS | ±1 LU |
| Momentary LUFS | -10 LUFS (max) | Peaks only |
| True Peak | -1.0 dBTP | Maximum ceiling |
| LRA (Loudness Range) | 8–12 LU | Preschool-appropriate |
| Dynamic Range (DR) | 10–14 dB | Measured per EBU R128 |

### Genre-Specific Settings

Preschool content is a distinct genre with unique mastering requirements.

| Content Type | LUFS Target | True Peak | Notes |
|-------------|-------------|-----------|-------|
| Dialogue-heavy episode | -14 LUFS | -1.0 dBTP | Dialogue must remain clear |
| Song-focused episode | -13 LUFS | -1.0 dBTP | Slightly more present |
| Lullaby / quiet episode | -16 LUFS | -2.0 dBTP | Preserve dynamic softness |
| Dance / high-energy song | -12 LUFS | -1.0 dBTP | Brief peaks, still controlled |
| Compilation / mix | -14 LUFS | -1.0 dBTP | Consistent across segments |
| Background music only | -18 LUFS | -3.0 dBTP | Ambient, non-distracting |
| Sound effects library | -20 LUFS | -3.0 dBTP | Headroom for mixing |

### Platform Delivery Targets

| Platform | Spec | Notes |
|----------|------|-------|
| Spotify | -14 LUFS integrated | Will normalize; provide headroom |
| Apple Music | -16 LUFS (Sound Check) | -1 dBTP ceiling recommended |
| YouTube | -14 LUFS (loudness-based) | -2 dBTP strongly recommended |
| Amazon Music | -14 LUFS | Follow general spec |
| Netflix | -27 LUFS (+10dB dialnorm) | Broadcast standard; separate QC |
| Broadcast TV | -23 LUFS (EBU R128) | Future consideration |

---

## Batch Mastering Workflow

For consistent quality across 100+ episodes, use a batch mastering workflow.

### Recommended Tools

- **iZotope Ozone**: Batch processing, mastering assistant, Tonal Balance Control
- **LANDR**: AI mastering with style matching
- **DAW-based templates**: Reaper, Logic Pro, or Ableton with mastering chains saved
- **FFmpeg + loudnorm**: Automated loudness normalization for batch export

### Batch Process

1. **Prepare session template**
   - Create a mastering session with the preset chain (EQ → Compression → Limiter → Dither)
   - Set metering to ITU-R BS.1770-4 standards
   - Name output directory and file convention

2. **Import stems or mixed WAVs**
   - Full mix WAV (48kHz 24-bit) as input
   - Keep original unprocessed file as safety backup

3. **Load preset**
   - Apply the mastering chain preset
   - Typically -1 dBTP ceiling, adjust threshold to hit -14 LUFS

4. **Analysis pass**
   - Run loudness analysis on each file
   - Log LUFS, true peak, dynamic range
   - Flag files outside spec for manual attention

5. **Render batch**
   - Export mastered WAV (48kHz 24-bit)
   - Export mastered MP3 (320kbps)
   - If needed: export 16-bit WAV for distribution

6. **Quality check**
   - Spot-check every 10th file on full range monitors
   - Check every file on phone speaker
   - Verify loudness matches reference tracks

### Mastering Template (Example)

```text
DAW: Reaper 7
Chain:
  1. ReaEQ: HPF @ 30Hz, gentle presence shelf
  2. ReaComp: 1.8:1, -20dB threshold, 15ms attack, 150ms release
  3. ReaLimit: Ceiling -1.0dBTP, release auto
  4. Loudness Meter (Youlean or EBU)
Output: WAV 48kHz 24-bit + MP3 320kbps
```

---

## Quality Check Process

Every mastered file must pass a 3-listening QC.

### QC Station 1: Phone Speaker

| Check | Standard |
|-------|----------|
| Dialogue clarity | Every word intelligible |
| Loudness | Comfortable at 50% volume |
| Distortion | None audible |
| Bass translation | Low end audible but not boomy |

### QC Station 2: Headphones

| Check | Standard |
|-------|----------|
| Stereo imaging | Correct panning, no phase issues |
| Background noise | No hiss, clicks, or artifacts |
| Reverb | Natural, not washy |
| EQ balance | Warm, not muddy or harsh |
| Transients | Clean attacks, no clipping |

### QC Station 3: Studio Monitors

| Check | Standard |
|-------|----------|
| Full spectrum | Balanced from sub to air |
| Dynamic range | Appropriate for content type |
| Depth perception | Clear front-to-back layering |
| Reference match | Comparable to approved reference |

### Per-Episode QC Log

```text
Episode: AINursery_Ep012_FunWithLetters
Mastered by: [Engineer]
Date: [Date]

LUFS Integrated: -14.2 LUFS
True Peak: -1.3 dBTP
LRA: 9.2 LU
DR: 12.1 dB

Phone QC: PASS
Headphone QC: PASS
Monitor QC: PASS

Notes: Green-lit for distribution.
```

---

## Reference File System

Maintain a reference library for consistent mastering across the catalog.

### Reference Hierarchy

```text
Masters/References/
    Episodes/
        Ep001_GoldStandard.wav
        Ep005_Reference.wav
    Songs/
        ABCSong_Reference.wav
        CountToTen_Reference.wav
        GoodMorning_Reference.wav
    Category/
        Dialogue_Reference.wav
        Lullaby_Reference.wav
        DanceSong_Reference.wav
```

### Reference Selection Criteria

- Approved by creative lead
- Meets all loudness and quality specs
- Represents the target sound of the studio
- Updated only when mix quality improves significantly

### Using References

1. Import reference into mastering session
2. Normalize both reference and new file to -14 LUFS
3. Switch between them using utility gain match (±0.3 dB)
4. Adjust master until new file matches reference in:
   - Perceived loudness
   - Tonal balance
   - Dynamic feel
   - Spatial width
   - Clarity of core elements

---

## Common Issues & Fixes

| Issue | Symptom | Fix |
|-------|---------|-----|
| Too quiet | -16 LUFS or lower | Lower threshold on limiter 1–2 dB |
| Distorted peaks | True peak above -1 dBTP | Reduce makeup gain, check limiter ceiling |
| Muddy low end | Cloudy, lacks clarity | Cut 200–300 Hz by 1–2 dB |
| Harsh top end | Fatiguing on headphones | Reduce 4–8 kHz shelf by 1 dB |
| Too compressed | No dynamic life | Reduce compression ratio to 1.5:1, increase threshold |
| Pumping | Volume fluctuates noticeably | Slow release to 200ms, reduce GR to 1dB |
| Phase issues | Thin in mono | Check correlation meter, bypass any widen plugins |
| Sibilance | Harsh S and T sounds | De-ess at 5–8 kHz before compressor |
