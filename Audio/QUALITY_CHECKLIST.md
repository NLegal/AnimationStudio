# Audio Quality Checklist

## AI Nursery Studio — Quality Control Manual

### Version 1.0

---

## Introduction

Every audio asset released by AI Nursery Studio must pass a standardized quality control process. This checklist ensures consistency, technical quality, and educational appropriateness across all episodes, songs, and audio elements.

QC is not optional. Every file must be checked before it enters the episode pipeline.

---

## Pre-Generation Checklist

Before generating any audio asset, verify:

### Concept Check

- [ ] Asset type is clearly defined (song, voice, SFX, Foley, ambience)
- [ ] Educational purpose is documented
- [ ] Target age range is confirmed (2–3, 3–4, or 4–6)
- [ ] Emotional tone matches scene requirements
- [ ] Duration is appropriate for the context

### Technical Prep

- [ ] Session template loaded (correct sample rate, bit depth)
- [ ] Reference tracks available for comparison
- [ ] Prompt template selected and customized
- [ ] Output path and naming convention confirmed
- [ ] Stem separation plan documented

### Creative Alignment

- [ ] Asset matches studio audio identity (warm, cheerful, educational)
- [ ] Character voice profile consulted (if character-specific)
- [ ] Episode audio bible consistency check passed
- [ ] No conflicts with existing audio assets in the episode

---

## Post-Generation Checklists

### Song QC Checklist

- [ ] Lyrics are clearly intelligible (every word)
- [ ] Educational content is accurate and correctly placed
- [ ] Tempo is within 80–130 BPM range
- [ ] Melody is simple, repetitive, easy to sing along
- [ ] Lead vocal and backing blend naturally
- [ ] Call-and-response sections have clear separation
- [ ] Song structure follows standard format (verse-chorus-bridge)
- [ ] Duration matches target (30s, 60s, 90s, 2min, 3min)
- [ ] No off-key notes or harmonic clashes
- [ ] Rhythm is steady and clearly defined
- [ ] Instrumentation is bright and preschool-appropriate
- [ ] No harsh frequencies or distorted elements
- [ ] Dynamics appropriate for the energy level
- [ ] Reverb is natural and not washy
- [ ] Stereo image is balanced (no extreme panning)
- [ ] File naming follows convention
- [ ] Metadata populated (title, episode, artist, language)
- [ ] Stems exported (dialogue, vocal, music, SFX)
- [ ] Master loudness: -14 LUFS integrated, -1 dB true peak

### Voice QC Checklist (Character Dialogue)

- [ ] Voice matches character profile (age, gender, pitch, energy)
- [ ] Consistent character voice across all lines
- [ ] Clear pronunciation, all words intelligible
- [ ] Pacing is age-appropriate (not too fast)
- [ ] Emotional tone matches scene direction
- [ ] No robotic or unnatural TTS artifacts
- [ ] No background noise or hiss
- [ ] Timing matches lip-sync reference
- [ ] No clipping or distortion
- [ ] Consistent volume across all lines
- [ ] No breath pops or mouth clicks (if avoidable)
- [ ] Pronunciation matches pronunciation dictionary
- [ ] Character catchphrases delivered consistently
- [ ] Laugh and cry sounds sound natural
- [ ] File naming follows convention

### Voice QC Checklist (Narrator)

- [ ] Narrator voice matches chosen variation (warm/educational/bedtime)
- [ ] Consistent pacing throughout
- [ ] Clear, even pronunciation
- [ ] Emotion appropriate to story segment
- [ ] No unnatural emphasis on words
- [ ] Transitions between narration and dialogue are smooth
- [ ] Narration does not compete with dialogue
- [ ] Volume consistent: -6 dB to -4 dB

### SFX QC Checklist

- [ ] Sound matches the on-screen action
- [ ] Quality is high (no compression artifacts, distortion)
- [ ] Duration matches action duration
- [ ] No background noise in SFX file
- [ ] Volume is appropriate: -12 dB to -9 dB (supporting)
- [ ] EQ matches scene frequency context
- [ ] Sound is child-friendly (not scary or harsh)
- [ ] File named according to SFX library convention
- [ ] Metadata includes category tags

### Foley QC Checklist

- [ ] Sound matches the on-screen interaction
- [ ] Timing is precise (±2 frames)
- [ ] Volume is natural and subtle: -15 dB to -12 dB
- [ ] No exaggerated sounds (preschool-appropriate)
- [ ] Sound is comforting and familiar
- [ ] File named according to Foley library convention

### Ambience QC Checklist

- [ ] Ambience matches scene location
- [ ] Loop point is seamless (if looping)
- [ ] No distracting elements in the loop
- [ ] Volume is background-level only: -18 dB to -15 dB
- [ ] EQ is thin (heavy high-pass, cut mids)
- [ ] Duration covers scene length (with padding)
- [ ] File named according to ambience library convention

### Mix QC Checklist

- [ ] Dialogue is clear and at -6 dB to -3 dB
- [ ] Vocals are at -9 dB to -6 dB (intelligible over music)
- [ ] Music bed is at -18 dB to -12 dB (under dialogue)
- [ ] SFX support without distracting
- [ ] Foley is natural and subtle
- [ ] Ambience fills the background without notice
- [ ] Levels are balanced across whole episode
- [ ] No sudden volume spikes or drops
- [ ] EQ balance is warm, not muddy or harsh
- [ ] Compression is gentle (no pumping)
- [ ] Reverb is natural and scene-appropriate
- [ ] Stereo image is balanced
- [ ] Mono compatibility confirmed (no phase cancellation)
- [ ] Master loudness: -14 LUFS integrated, -1 dB true peak
- [ ] Dynamic range: 8–12 LU (consistent)

### Master QC Checklist

- [ ] Integrated LUFS: -14 LUFS ±0.5
- [ ] True peak: -1 dBTP or lower
- [ ] LRA: 6–10 LU
- [ ] No clipping or intersample peaks
- [ ] No distortion, pumping, or artifacts
- [ ] EQ balance: warm, clear, non-fatiguing
- [ ] Translation check: phone speakers, headphones, monitors
- [ ] Reference comparison: matches approved reference
- [ ] Export format: WAV 48kHz 24-bit (master)
- [ ] Export format: MP3 320kbps (distribution)
- [ ] File naming follows convention
- [ ] Metadata populated
- [ ] Stems archived with master

---

## Rejection Criteria

Any asset meeting any of these criteria must be rejected immediately. Do not pass to the next stage.

### Critical Rejection Criteria (Stop)

| Issue | Severity | Action |
|-------|----------|--------|
| Distortion (any) | Critical | Regenerate or re-record |
| Clipping (true peak above 0 dBTP) | Critical | Remix and remaster |
| Background noise or hiss | Critical | Re-record or use noise reduction; if irreducible, reject |
| Unnatural TTS artifacts (robotic, glitchy) | Critical | Regenerate with different prompt or platform |
| Off-key or out-of-tune singing | Critical | Regenerate song |
| Wrong tempo (outside 80–130 BPM) | Critical | Regenerate with correct BPM |
| Inaudible dialogue | Critical | Regenerate or re-record |
| Wrong language or accent | Critical | Re-record with correct talent |
| Educational content error | Critical | Rewrite and regenerate |
| Culturally inappropriate content | Critical | Remove and replace |

### Moderate Rejection Criteria (Flag, Fix, or Reject)

| Issue | Severity | Action |
|-------|----------|--------|
| Volume mismatch with scene | Moderate | Adjust levels in mix |
| Over-compressed (no dynamics) | Moderate | Remix with lighter compression |
| Harsh EQ (sibilant or piercing) | Moderate | EQ adjustment |
| Muddy low end (unclear dialogue) | Moderate | EQ cut at 200–400 Hz |
| Washey reverb (excessive) | Moderate | Reduce reverb wet mix |
| Stereo imbalance | Moderate | Adjust panning |
| Slight timing drift in dialogue | Moderate | Time-align in DAW |
| Slight background buzz/hum | Moderate | Apply noise gate or spectral repair |
| Breath pops or mouth clicks | Moderate | Edit out or reduce |
| Inconsistent character voice | Moderate | Consider re-recording or select alternative take |

### Minor Issues (Note and Pass if non-accumulating)

| Issue | Severity | Action |
|-------|----------|--------|
| Slight volume variation across takes | Minor | Level match in editing |
| Minor EQ preference differences | Minor | Note for future but pass |
| Slightly different reverb feel | Minor | Check against scene needs; pass if appropriate |
| File naming inconsistency | Minor | Rename |
| Missing metadata | Minor | Add metadata |

### Accumulation Rule

If a single asset accumulates 3+ moderate issues, it is rejected. If an asset has 5+ minor issues, it is flagged for review.

---

## Mixing QC Form

Use this form for every episode mix.

### Episode Information

```
Episode Title: _________________________________
Episode Number: _______________
Mixer: _________________________________
Date: _________________________________
Duration: _______________
```

### Technical Measurements

| Metric | Result | Pass/Fail |
|--------|--------|-----------|
| Integrated LUFS | ______ | ___ |
| Short-term LUFS | ______ | ___ |
| True Peak (dBTP) | ______ | ___ |
| LRA | ______ | ___ |
| Dynamic Range | ______ | ___ |
| Phase Correlation | ______ | ___ |

### Level Check

| Element | Target | Actual | Pass/Fail |
|---------|--------|--------|-----------|
| Dialogue | -6 dB to -3 dB | ______ | ___ |
| Vocals (singing) | -9 dB to -6 dB | ______ | ___ |
| Music bed (under dialogue) | -18 dB to -12 dB | ______ | ___ |
| Music bed (solo) | -9 dB to -6 dB | ______ | ___ |
| SFX (supporting) | -12 dB to -9 dB | ______ | ___ |
| Foley | -15 dB to -12 dB | ______ | ___ |
| Ambience | -18 dB to -15 dB | ______ | ___ |

### EQ Check

| Check | Pass/Fail | Notes |
|-------|-----------|-------|
| Dialogue clarity (2–4 kHz presence) | ___ | |
| No low rumble (below 80Hz rolled off) | ___ | |
| Music warmth (200–400 Hz presence) | ___ | |
| No harsh frequencies (4–8 kHz) | ___ | |
| Overall tonal balance (warm, not muddy) | ___ | |

### Dynamics Check

| Check | Pass/Fail | Notes |
|-------|-----------|-------|
| Dialogue compression (gentle 2:1) | ___ | |
| Vocal compression (3:1) | ___ | |
| No pumping or breathing | ___ | |
| Consistent level across episode | ___ | |

### Stereo Check

| Check | Pass/Fail | Notes |
|-------|-----------|-------|
| Dialogue centered | ___ | |
| Ambience wide | ___ | |
| Music stereo balanced | ___ | |
| Mono compatibility | ___ | |
| Phase correlation > +0.5 | ___ | |

### Listening Check

| Platform | Pass/Fail | Notes |
|----------|-----------|-------|
| Phone speaker | ___ | |
| Headphones | ___ | |
| Studio monitors | ___ | |
| Laptop speakers | ___ | |

### Overall Verdict

```
PASS (all checks passed)      ❏
PASS WITH NOTES (minor issues) ❏
FLAGGED (moderate issues)     ❏
REJECT (critical issues)      ❏

Reviewer: _________________________________
Date: _________________________________
```

---

## Localization QC

### Translation Accuracy

- [ ] Native speaker review completed
- [ ] Dialogue meaning preserved (not literal)
- [ ] Character voice personality preserved
- [ ] Educational content accurately translated
- [ ] No added content that changes meaning
- [ ] Cultural references appropriate for target market
- [ ] Humor translated effectively (not lost or confusing)

### Vocal Sync

- [ ] Dialogue timing matches source (±10%)
- [ ] Vocal timing matches source melody
- [ ] No audible editing artifacts (cuts, crossfades)
- [ ] Breath sounds preserved (not cut off)
- [ ] Lip-sync timing acceptable for animation

### Cultural Appropriateness

- [ ] No culturally insensitive content
- [ ] Region-specific references accurate
- [ ] Character names appropriate for target language
- [ ] Visual elements match audio (if applicable)
- [ ] Age-appropriateness confirmed for target market

### Technical QC (Localized)

- [ ] Mix levels match source spec
- [ ] Mastering meets -14 LUFS standard
- [ ] No artifacts from time-stretching
- [ ] Stems properly replaced
- [ ] File naming follows localization convention
- [ ] Metadata includes language tag

---

## QC Sign-Off

All checklists must be completed and signed off before an audio asset enters production.

### Sign-Off Hierarchy

| Role | Signs Off On |
|------|-------------|
| Audio Producer | Technical quality, mix, master |
| Content Reviewer | Educational accuracy, lyrics |
| Character Lead | Voice consistency |
| Episode Director | Creative alignment, emotional tone |
| Localization Manager | Localization QC |
| Executive Producer | Final sign-off |

### Sign-Off Form

```
Asset: _________________________________
Type: _________________________________
Date: _________________________________

Produced by: ___________________ Date: _______
Content reviewed by: ____________ Date: _______
Character verified by: __________ Date: _______
Direction approved by: __________ Date: _______
Localization approved by: _______ Date: _______

FINAL APPROVAL: ___________________ Date: _______
```
