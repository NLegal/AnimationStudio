# Animation Quality Control Checklist

## Little Learning Town Studios

### Version 1.0

---

## Introduction

Every animation produced by Little Learning Town Studios must pass the Quality Control (QC) process before release. This document defines the QC criteria, rejection rules, and sign-off procedure.

**QC Philosophy:** We do not aim for photorealism. We aim for charming, child-friendly, emotionally clear animation that feels warm, safe, and consistent with our Cocomelon-inspired preschool style. Movement should be readable at a glance by a 2-5 year old child.

**When to QC:**
- Before exporting any animation clip
- After any AI generation pass
- After any manual animation edit
- Before final episode assembly

---

## Pre-Generation Checklist

Before generating an animation, verify these are in place:

| # | Item | Status |
|---|---|---|
| □ | Storyboard approved for this shot | |
| □ | Characters selected match scene | |
| □ | Environment selected | |
| □ | Props/objects selected | |
| □ | Animation type matches intent (walk, run, dance, interaction, etc.) | |
| □ | Prompt template selected from animation-prompts.md | |
| □ | Negative prompts prepared from animation-negatives.md | |
| □ | Camera shot selected from Camera library | |
| □ | Timing parameters set (duration, loop, fps) | |
| □ | Lighting style selected | |
| □ | Character emotion/expression chosen | |
| □ | Secondary motion expectations noted | |

**Pre-generation failure:** If any item above is unchecked, do NOT generate the animation. Resolve the gap first.

---

## Post-Generation Checklist

Check every animation against ALL of the following:

### Motion & Performance

| # | Criterion | Pass/Fail | Notes |
|---|---|---|---|
| □ | Motion is smooth (no jitter, freeze, or stutter) | | |
| □ | Character proportions consistent throughout animation | | |
| □ | Facial expressions match emotional intent | | |
| □ | Natural blinking present (every 4-6 seconds) | | |
| □ | Mouth shapes match speech/singing if applicable | | |
| □ | Body movement is soft and rounded (no sharp mechanical motion) | | |
| □ | Pacing is child-friendly (not too fast, not too slow) | | |
| □ | Camera is stable (no shake or wobble) | | |
| □ | Proper interaction with objects (no clipping, correct hand placement) | | |
| □ | Secondary motion present (clothing, accessories, ears, tail) | | |
| □ | Transitions are gentle (no jarring cuts) | | |

### Style & Brand

| # | Criterion | Pass/Fail | Notes |
|---|---|---|---|
| □ | Animation matches studio style (playful, soft, rounded, energetic) | | |
| □ | No violent or frightening content | | |
| □ | Character stays on model (consistent design) | | |
| □ | Colors match approved palette | | |
| □ | No text, watermarks, logos, or signatures | | |
| □ | No adult/anime/realistic style elements | | |
| □ | Child-appropriate energy level | | |

### Technical

| # | Criterion | Pass/Fail | Notes |
|---|---|---|---|
| □ | Frame rate is consistent (24fps target) | | |
| □ | No compression artifacts, noise, or grain | | |
| □ | No flickering or flashing frames | | |
| □ | Loop points are seamless if looping | | |
| □ | Resolution is correct for target platform | | |
| □ | No missing body parts or geometry errors | | |
| □ | Lighting is consistent throughout | | |

---

## Rejection Criteria (Automatic Fail)

If ANY of the following are present, the animation is **automatically rejected** — no partial pass:

| # | Rejection Reason | Severity |
|---|---|---|
| □ | Any violent, jerky, or aggressive motion | Critical |
| □ | Character deformation, distortion, or broken proportions | Critical |
| □ | Uncanny valley expressions (doll-like, mask-like, dead-eyed) | Critical |
| □ | Floating feet or sliding feet (not planted on ground) | Critical |
| □ | Object clipping through hands or body | Critical |
| □ | Missing limbs or body parts | Critical |
| □ | Text, watermarks, or logos in frame | Critical |
| □ | Horror, scary, or frightening imagery | Critical |
| □ | Flashing/strobing content (seizure risk) | Critical |
| □ | Character off-model (wrong colors, wrong proportions) | Major |
| □ | Camera shake or jitter | Major |
| □ | No blinking for >8 seconds | Major |
| □ | Expression does not match intended emotion | Major |
| □ | Frozen character (no idle animation, no breathing) | Major |
| □ | Lip sync does not match audio | Major |

**Any Critical rejection = immediate discard. Do not attempt to fix. Regenerate.**

**Any Major rejection = fix if minor/correctable, or regenerate.**

---

## Per-Animation-Type Checklists

### Walk Cycle QC

| # | Check | Pass/Fail |
|---|---|---|
| □ | Feet make contact with ground each step | |
| □ | No sliding or skating | |
| □ | Arms swing opposite to legs | |
| □ | Head bob is gentle and natural | |
| □ | Character moves forward at consistent speed | |
| □ | Loop is seamless (no visible start/end) | |
| □ | Secondary motion (ears, dress, tail) follows naturally | |

### Run Cycle QC

| # | Check | Pass/Fail |
|---|---|---|
| □ | Both feet leave ground during stride | |
| □ | Speed is moderate (preschool-appropriate, not frantic) | |
| □ | Arms pump, not flail | |
| □ | Facial expression shows joy/excitement, not fear | |
| □ | No aggressive or violent appearance | |
| □ | Ground contact is solid | |

### Dance Loop QC

| # | Check | Pass/Fail |
|---|---|---|
| □ | Motion is on-beat (if music is present) | |
| □ | No jerky or uncoordinated movement | |
| □ | Character looks happy and engaged | |
| □ | Full body participation (not just arms) | |
| □ | Loop point is seamless | |
| □ | Accessories move with the rhythm | |

### Facial Expression QC

| # | Check | Pass/Fail |
|---|---|---|
| □ | Emotion is clearly readable | |
| □ | No uncanny valley | |
| □ | Symmetrical face (unless intentionally asymmetrical) | |
| □ | Eyes have life and sparkle | |
| □ | Natural blinking included | |
| □ | Expression matches emotional intent from storyboard | |
| □ | Transition from previous expression is smooth | |

### Interaction QC

| # | Check | Pass/Fail |
|---|---|---|
| □ | Object is correctly held/grasped (no clipping) | |
| □ | Hand position matches object shape | |
| □ | Object follows character motion naturally | |
| □ | No floating or teleporting objects | |
| □ | Timing of contact feels natural | |
| □ | Character looks at object during interaction | |
| □ | Release/grip release is clean | |

### Scene/Sequence QC

| # | Check | Pass/Fail |
|---|---|---|
| □ | All characters remain on model | |
| □ | Camera framing is consistent with storyboard | |
| □ | Transitions between shots are smooth | |
| □ | Lighting is consistent across cuts | |
| □ | Audio sync (if applicable) is accurate | |
| □ | Pacing allows time to process (2-5 year old audience) | |
| □ | No continuity errors between shots | |

---

## QC Sign-Off Procedure

### Step 1: Self-Review (Animator)

The animator who produced the shot completes the Post-Generation Checklist above.

- All items must pass or have a documented note.
- If any **Rejection Criteria** are met, do not proceed — discard and regenerate.

### Step 2: Peer Review (Second Set of Eyes)

A second team member reviews the animation using the same checklist.

- Independent assessment — do not share your results with the reviewer beforehand.
- Compare checklists. Discrepancies must be discussed and resolved.

### Step 3: Technical Check

Verify:
- Output format is correct (`.mp4`, `.gif`, or platform-specified format)
- Resolution matches delivery specs
- File naming follows convention: `[Episode]_[Scene]_[Shot]_v[version].mp4`
- No technical artifacts in final export

### Step 4: Sign-Off

| Role | Name | Date | Status |
|---|---|---|---|
| Animator | | | □ Pass □ Fail |
| Peer Reviewer | | | □ Pass □ Fail |
| Technical Reviewer | | | □ Pass □ Fail |
| Final Approval | | | □ Approved □ Rejected |

### Step 5: Versioning

- Approved shots move to the episode assembly folder.
- Rejected shots go to `_REJECTED` subfolder with rejection reason in filename.
- Each iteration increments version number: `_v1`, `_v2`, `_v3`.

### Step 6: Episode Assembly QC

When all shots are assembled into an episode, run a final pass:

| # | Check |
|---|---|
| □ | All shots have passed individual QC |
| □ | Transitions between shots are smooth |
| □ | Audio mix is balanced (dialogue, music, sfx) |
| □ | Total runtime matches intended length |
| □ | Episode flows at child-friendly pace |
| □ | No jarring style changes between shots |

---

## Quick Pass / Fail Reference

| Result | Meaning | Action |
|---|---|---|
| **Pass** | All criteria met, no critical issues | Ship to episode assembly |
| **Conditional Pass** | Minor issues noted, acceptable for now | Note issues, ship, revisit in post |
| **Fail — Rework** | Major issues, fixable | Return to animator with notes |
| **Fail — Discard** | Critical issues, unfixable | Delete. Regenerate from scratch |

---

*Document maintained by Little Learning Town Studios — Animation Department*
