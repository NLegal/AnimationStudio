# Song Structure Standards — Little Learning Town

## Standard Full Structure

```
  Section         Bars        Purpose
 ───────────────────────────────────────────────────
  INTRO           4–8         Establish key, tempo, mood
      │
  VERSE 1         8–16        Introduce concept, narrative verses
      │
  PRE-CHORUS      4–8         Build anticipation, tension-release
      │
  CHORUS          8–16        Core hook, main educational message
      │
  VERSE 2         8–16        Reinforce or expand concept
      │
  CHORUS          8–16        Repeat hook (identical or near-identical)
      │
  BRIDGE          4–8         New perspective, emotional peak, or twist
      │
  FINAL CHORUS    8–16        Biggest energy, may repeat twice
      │
  OUTRO           4–8         Wind down, resolve to tonic
```

**Total: 56–120 bars** (~1:45–3:30 at 110 BPM)

---

## Alternative Structures

### Short Songs (30 seconds – 1 minute)

For single-concept educational content (letter A, color red, number 1):

```
  VERSE    8 bars    Introduce concept
  CHORUS   8 bars    Repeat concept twice
  CHORUS   8 bars    Reinforce with slight variation
  OUTRO    4 bars    Quick resolution
```

**Total: 28 bars** (~30 seconds at 110 BPM)

---

### Medium Songs (1 minute)

```
  INTRO     2–4 bars
  VERSE 1   8 bars
  CHORUS    8 bars
  VERSE 2   8 bars
  CHORUS    8 bars
  OUTRO     4 bars
```

**Total: 38–40 bars** (~1:00–1:15 at 110 BPM)

---

### Full Songs (2 minutes)

```
  INTRO         4 bars
  VERSE 1       8 bars
  PRE-CHORUS    4 bars
  CHORUS        8 bars
  VERSE 2       8 bars
  PRE-CHORUS    4 bars
  CHORUS        8 bars
  BRIDGE        4 bars
  FINAL CHORUS  8 bars (repeat once for energy)
  OUTRO         4 bars
```

**Total: 60 bars** (~2:00 at 110 BPM)

---

### Extended Songs (3 minutes)

Same as full structure but with:
- Extended bridge (8 bars instead of 4)
- Instrumental break (4–8 bars after bridge)
- Final chorus repeats 2–3 times with additive instrumentation
- Longer outro (8 bars) with fade

---

### Compilation Songs (5 minutes)

Assembled from 2–3 shorter song blocks. Never generated as one continuous piece.

```
  Block 1:  Full song (2 min) ─── fade out ───
  Block 2:  Short song (1 min) ─── segue ───
  Block 3:  Medium song (1:30) ─── fade out
```

---

## Preschool-Specific Adjustments

| Element | Standard Practice | Preschool Adjustment |
|---------|-------------------|---------------------|
| **Intro length** | 4–8 bars | **1–4 bars** — children lose interest quickly |
| **Verse repetition** | New lyrics each verse | **Repeat verse 1 lyrics** the second time, or slight variation |
| **Chorus repetition** | 2× per appearance | **3–4×** — repetition builds learning |
| **Pre-chorus** | 4–8 bars | **0–4 bars** — often skipped for simplicity |
| **Bridge** | New material | **Simpler bridge** or restate the chorus in a new way |
| **Outro** | 4–8 bars | **2–4 bars** with a clear "ending" cue |
| **Downbeats** | Standard accent | **Exaggerated downbeats** — helps children feel the pulse |
| **Call-and-response** | Occasional | **Frequent** — pause for children to answer |
| **Silence/pause** | Rare | **Use intentionally** — gives processing time |

---

## Musical Transitions

### Intro → Verse
- 2-bar drum fill or simple riser (xylophone scale)
- Instrumental elements enter one at a time (drums first, then harmony, then melody)

### Verse → Pre-Chorus (if used)
- Add hi-hat or tambourine on 8th notes
- Slight crescendo in volume and energy
- Melody climbs to a higher register

### Pre-Chorus → Chorus
- Full stop on beat 1 (breakdown)
- All instruments crash in on chorus
- Vocal energy jumps

### Chorus → Verse
- Drop percussion or simplify arrangement
- End chorus on tonic, start verse on tonic or IV chord
- 1-bar instrumental link if needed

### Verse → Bridge
- Remove percussion
- Shift to subdominant (IV) or relative minor (vi)
- Softer vocal delivery

### Bridge → Final Chorus
- Drum fill (4 beats)
- Re-introduce all instruments
- Highest energy of the song

### Chorus → Outro
- Repeat last line of chorus a cappella or with minimal accompaniment
- Tag ending: repeat last 2 bars 2× with ritardando
- Resolve to sustained tonic chord

---

## Timing Reference for Animation Sync (24 fps)

### Bars to Frames

At **110 BPM** (common educational tempo):

| Duration | Beats | Bars (4/4) | Frames (24fps) |
|----------|-------|------------|----------------|
| 1 beat | 1 | 0.25 | ~13 frames |
| 2 beats | 2 | 0.5 | ~26 frames |
| 4 beats (1 bar) | 4 | 1 | ~52 frames |
| 8 bars | 32 | 8 | ~418 frames (~17.4s) |
| 16 bars | 64 | 16 | ~836 frames (~34.8s) |

### Tempo → Frame Conversion

```
Frames per beat = 2,400 / BPM
Frames per bar  = 9,600 / BPM
```

**Examples:**

| BPM | Frames per beat | Frames per bar |
|-----|----------------|----------------|
| 80 | 30.0 | 120.0 |
| 90 | 26.7 | 106.7 |
| 100 | 24.0 | 96.0 |
| 110 | 21.8 | 87.3 |
| 120 | 20.0 | 80.0 |
| 130 | 18.5 | 73.8 |

### Section Duration at 110 BPM (Reference)

| Section | Bars | Beats | Time | Frames (24fps) |
|---------|------|-------|------|----------------|
| Intro | 4 | 16 | ~8.7s | 209 |
| Verse | 8 | 32 | ~17.5s | 418 |
| Pre-Chorus | 4 | 16 | ~8.7s | 209 |
| Chorus | 8 | 32 | ~17.5s | 418 |
| Bridge | 4 | 16 | ~8.7s | 209 |
| Outro | 4 | 16 | ~8.7s | 209 |

Use these timings to plan animation cuts, character mouth movements, and scene transitions. Each section boundary is a natural cut point for the animator.
