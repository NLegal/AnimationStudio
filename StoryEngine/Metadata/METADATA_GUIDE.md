# Episode Metadata Guide

> **Version:** 1.0
> **Purpose:** Structured data that accompanies every generated episode

## Philosophy

Every episode carries metadata that enables:
- Search and discovery across hundreds of episodes
- Analytics on curriculum coverage and diversity
- Automated production pipeline decisions
- Localization and remixing
- Long-term continuity tracking

## Metadata Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| episode_id | string | Yes | Unique identifier | `S01E014` |
| season | integer | Yes | Season number | 1 |
| episode_number | integer | Yes | Episode within season | 14 |
| title | string | Yes | Episode title | "Five Colorful Ducks" |
| subtitle | string | No | Extended title | "Learning Primary Colors" |
| curriculum_area | string | Yes | Primary curriculum category | "colors" |
| learning_objective | string | Yes | Specific lesson | "Identify red, blue, yellow" |
| theme | string | Yes | Story theme | "park-visit" |
| target_age | string | Yes | Age range | "2-5" |
| difficulty | integer | Yes | Difficulty level 1-5 | 1 |
| duration_minutes | integer | Yes | Episode runtime | 3 |
| has_song | boolean | Yes | Contains musical segment | true |
| song_type | string | If has_song | Song category | "educational" |
| main_character | string | Yes | Episode protagonist | "lily-bunny" |
| supporting_characters | list | Yes | Additional characters | ["ben-bear", "daisy-duck"] |
| location | string | Yes | Primary setting | "playground" |
| weather | string | Yes | In-episode weather | "sunny" |
| season_name | string | Yes | In-episode season | "spring" |
| holiday | string | No | Holiday if applicable | "easter" |
| assets | list | Yes | Required props | ["balloons", "paint", "easel"] |
| story_grammar | string | Yes | Narrative template used | "find-something" |
| conflict | string | Yes | Story problem | "Can't find the right color" |
| resolution | string | Yes | How problem is solved | "Friends help mix colors" |
| language | string | Yes | Episode language | "en" |
| vocabulary_level | string | Yes | Language complexity | "simple" |
| keywords | list | Yes | Searchable tags | ["colors", "mixing", "paint"] |
| curriculum_tags | list | Yes | Educational taxonomy | ["colors", "primary"] |
| emotional_arc | list | Yes | Emotion sequence | ["curious", "frustrated", "proud"] |

## Metadata in the Code

The `EpisodeBlueprint` dataclass in `src/story_engine/models.py` implements all metadata fields with defaults and validation:

```python
@dataclass
class EpisodeBlueprint:
    episode_id: str = ""
    season: int = 1
    episode_number: int = 1
    title: str = ""
    # ... 20+ metadata fields
```

The `validate()` method returns a list of missing required fields:
- Missing learning objective
- Missing main character
- Missing location
- Missing conflict
- Missing resolution

## Production Manifest

When an EpisodeBlueprint flows through the production pipeline, its metadata is expanded into an `EpisodeManifest` (in `src/production/models.py`) that adds:
- scene_count, shot_count
- estimated_video_clips, estimated_images
- Production-specific fields (render status, QC status)

## Metadata Usage

| Department | Uses Metadata For |
|-----------|-------------------|
| Curriculum | Tracking learning objective coverage |
| Production | Scene/shot planning, asset allocation |
| Animation | Character assignments, emotion mapping |
| Audio | Song type, character voice selection |
| Marketing | Episode descriptions, keywords, SEO |
| Analytics | Diversity tracking, gap analysis |

## File Convention

Metadata should be stored per-episode as YAML:
```yaml
# Episodes/S01E014/episode.yaml
episode_id: S01E014
title: "Five Colorful Ducks"
learning_objective: "Identify primary colors"
main_character: "lily-bunny"
location: "pond"
has_song: true
```

## Quality Checklist

- [ ] All required fields present
- [ ] IDs follow naming convention (SxxExx)
- [ ] Keywords are drawn from controlled vocabulary
- [ ] Age range matches curriculum difficulty
- [ ] Duration is within expected range (1-5 minutes)
- [ ] Character names match character database
- [ ] Location names match world database
