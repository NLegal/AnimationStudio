# Continuity & Diversity Engine Guide

## Purpose

The Continuity Engine ensures that every episode remains faithful to the established canon of characters, relationships, locations, and world rules. The Diversity Engine prevents repetitive episodes by tracking what has been used and ensuring variety across the series. Together, they maintain the integrity and freshness of the Little Learning Town universe.

---

## What the Engine Remembers

### Character Data

| Field | Example | Purpose |
|---|---|---|
| Name | Lily Bunny | Unique identifier |
| Age | 4 | Determines vocabulary level |
| Personality | Enthusiastic, curious | Guides dialogue patterns |
| Favorite color | Pink | Themed episode opportunities |
| Favorite food | Carrots | Can appear in cooking episodes |
| Favorite toy | Ribbon | Possible find/lost episodes |
| Home | 123 Carrot Lane, Sunny Meadows | Location consistency |
| Family | Mama Bunny, Papa Bunny | Relationship accuracy |
| Best friend | Ben Bear | Social dynamics |
| Catchphrase | "Let's try!" | Brand character voice |
| Pet | None currently | Future expansion |
| Recent activities | Garden visit in S01E002 | Prevents repetition |
| Current emotional state | Happy | Episode continuity |

### Relationship Data

| Relationship | Type | Established In | Status |
|---|---|---|---|
| Lily Bunny ↔ Ben Bear | Best friends | Season 1, Episode 1 | Active |
| Lily Bunny ↔ Daisy Duck | Good friends | Season 1, Episode 3 | Active |
| Ben Bear ↔ Daisy Duck | Friends | Season 1, Episode 4 | Active |
| Lily Bunny ↔ Miss Owl | Student / Teacher | Season 1, Episode 2 | Active |
| Ben Bear ↔ Mama Bear | Mother / Son | Season 1, Episode 1 | Active |
| Daisy Duck ↔ Grandma Duck | Granddaughter / Grandmother | Season 1, Episode 5 | Active |
| Lily Bunny ↔ Grandpa Bunny | Granddaughter / Grandfather | Season 1, Episode 2 | Active |
| Miss Owl ↔ All | Teacher | Season 1, Episode 1 | Active |

The engine ensures no relationship is contradicted. If Lily knows Ben, they must always act like friends.

### Location Usage Tracking

| Location | Last Used | Total Uses | Season |
|---|---|---|---|
| Sunny Meadows Playground | S01E001 | 3 | Season 1 |
| Lily's House (Kitchen) | S01E003 | 2 | Season 1 |
| Ben's House | S01E002 | 1 | Season 1 |
| Sunny Meadows School | S01E004 | 2 | Season 1 |
| Grandma Duck's House | Never | 0 | — |
| Sunny Meadows Garden | S01E005 | 1 | Season 1 |
| Sunny Meadows Market | Never | 0 | — |
| Sunny Meadows Park (Pond) | S01E003 | 1 | Season 1 |

**Rule:** No location may be used more than once every 3 episodes.

### Theme Usage Tracking

| Theme | Last Used | Total Uses |
|---|---|---|
| Lost Toy | S01E001 | 1 |
| Birthday | S01E003 | 1 |
| Rainy Day | Never | 0 |
| Camping | Never | 0 |
| Beach | Never | 0 |
| Zoo | Never | 0 |
| Cooking | S01E005 | 1 |

**Rule:** No theme may repeat within the same season.

### Learning Objective Usage Tracking

| Objective ID | Objective | Last Used | Total Uses | Season |
|---|---|---|---|---|
| FRD-01 | Share Toys | S01E001 | 1 | Season 1 |
| CLR-02 | Recognize Blue | S01E002 | 1 | Season 1 |
| NUM-02 | Count to Five | S01E003 | 1 | Season 1 |
| SHP-03 | Identify Triangle | S01E004 | 1 | Season 1 |
| HLT-01 | Brush Teeth | Never | 0 | — |

**Rule:** No learning objective may repeat within 5 episodes.

---

## Diversity Enforcement

### Episode Diversity Score

Each episode receives a diversity score based on its combination of:

```
Diversity Factors:
  Main character       — Who leads (rotate among Lily, Ben, Daisy)
  Location             — Where it happens (avoid repeats)
  Theme                — Story theme (unique per season)
  Grammar pattern      — Narrative structure (don't repeat back-to-back)
  Learning objective   — What is taught (5-episode cooldown)
  Song type            — Musical approach (vary across episodes)
  Season               — Match real season (spring, summer, fall, winter)
  Weather              — Rain, sun, snow, wind, cloudy (vary)
  Activity             — What characters do (paint, count, build, sing)
  Props                — Key items (balloons, blocks, crayons, seeds)
  Conflict type        — Problem style (lost, can't do, needs help)
  Resolution method    — How it ends (friend helps, learns, discovers)
```

**Minimum diversity requirement:** An episode must differ from the last 3 episodes in at least 6 of the 12 factors.

### Character Rotation

```
Character Rotation Rules:
  - Lily Bunny appears in no more than 60% of episodes (main character)
  - Ben Bear appears in no more than 50% of episodes (supporting lead)
  - Daisy Duck appears in no more than 40% of episodes
  - Miss Owl appears in no more than 30% of episodes (teacher role)
  - Every main character must appear at least once per 5 episodes
  - No character appears in more than 3 consecutive episodes
  - Background characters rotate freely
```

### Location Rotation

```
Location Rotation Rules:
  - No location twice in 3 episodes
  - Indoor and outdoor locations should alternate when possible
  - Each location gets at least 1 episode per season
  - New locations introduced gradually (1 per 5 episodes)
```

### Weather and Season Diversity

```
Weather Rotation:
  - No same weather condition 3 episodes in a row
  - Weather should match the current real season
  - Special weather (snow, storm) limited to seasonal episodes

Season Progression:
  - Episodes follow the real calendar year progression
  - Each season gets proportional representation (25% each)
  - Holiday episodes reserved for their calendar window
```

---

## Repetition Prevention

### Title Uniqueness

Every episode title is checked against the master title database. Duplicate titles are rejected. Similar titles (e.g., "Lily's Garden" and "Lily's Garden Adventure") are flagged for review.

### Plot Similarity Detection

The engine compares new episode plots against the last 10 episodes:

```
Similarity Check:
  Same grammar pattern?            → Flag (unless 3+ episodes apart)
  Same theme?                      → Reject (must differ)
  Same learning objective?         → Reject (5-episode cooldown)
  Same main character + location?  → Flag (rotate at least one)
  Same conflict type?              → Flag (vary the problem)
  Same resolution type?            → Flag (vary the solution)
```

Any episode flagged for 3+ similarity factors is sent back for replanning.

---

## Continuity Database

The Continuity Engine maintains a structured database that grows with each episode:

```
episode_id: S01E003
title: "Daisy Duck's Birthday"
learning_objective: NUM-02 (Count to Five)
theme: Birthday
main_character: Daisy Duck
supporting_characters: [Lily Bunny, Ben Bear, Miss Owl]
location: Sunny Meadows Playground
season: Spring
weather: Sunny
conflict: Not enough party hats
resolution: Friends help make more
song_type: Celebration Song
key_props: [cake, hats, balloons, candles, confetti]
character_states:
  Daisy Duck: happy, learned to count, wore party hat
  Lily Bunny: helpful, counted candles
  Ben Bear: brought balloons, counted with friends
  Miss Owl: supervised, taught counting
```

This database is consulted before every new episode to ensure continuity and diversity.

---

## Continuity Error Handling

| Error Type | Example | Action |
|---|---|---|
| Relationship contradiction | Lily and Ben shown as strangers | Reject episode, flag for rewrite |
| Location inconsistency | Sunny Meadows School has no playground | Fix description or choose new location |
| Character personality shift | Lily Bunny is mean | Reject, regenerate dialogue |
| Age inconsistency | Daisy Duck acts 5 when established at 3 | Fix dialogue, check vocabulary level |
| Canon conflict | Ben's favorite food changes | Revert to established favorite |
| Timeline error | Pumpkin patch in spring | Change season or location |

Only validated, continuity-checked episodes move forward to production.
