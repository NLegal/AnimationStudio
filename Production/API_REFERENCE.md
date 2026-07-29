# Production API Reference — Little Learning Town Studios

## Overview

The Production API provides endpoints for every stage of the production pipeline. All endpoints follow RESTful conventions and accept and return JSON.

Base URL: `https://api.littlelearningtown.studio/v1`

## Authentication

Authentication is not yet implemented. A future version will require API keys passed via the `Authorization: Bearer <token>` header.

## Error Handling

All errors return a JSON response with this structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description"
  }
}
```

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | INVALID_REQUEST | Malformed request body |
| 404 | NOT_FOUND | Requested resource not found |
| 409 | CONFLICT | Resource already exists |
| 422 | VALIDATION_ERROR | Request failed validation |
| 500 | INTERNAL_ERROR | Unexpected server error |

---

## Endpoints

### POST /api/episodes

Create a new episode.

**Request Body:**

```json
{
  "episode_id": "S01E001",
  "title": "Five Colorful Ducks",
  "duration": "3:12",
  "target_age": "2-5",
  "learning_goal": "Primary Colors",
  "has_song": true,
  "has_narration": true,
  "characters": ["Lily Bunny", "Ben Bear", "Mama Duck"],
  "locations": ["Sunny Pond"],
  "assets": ["Balloons", "Flowers", "Boat"]
}
```

**Response:** `201 Created`

```json
{
  "episode_id": "S01E001",
  "status": "created",
  "manifest_url": "/api/episodes/S01E001/manifest"
}
```

---

### GET /api/episodes

List all episodes.

**Response:** `200 OK`

```json
{
  "episodes": [
    {
      "episode_id": "S01E001",
      "title": "Five Colorful Ducks",
      "status": "planning",
      "scene_count": 6,
      "shot_count": 24
    }
  ]
}
```

---

### GET /api/episodes/{id}

Get episode details by ID.

**Response:** `200 OK`

```json
{
  "episode_id": "S01E001",
  "title": "Five Colorful Ducks",
  "duration": "3:12",
  "target_age": "2-5",
  "learning_goal": "Primary Colors",
  "has_song": true,
  "has_narration": true,
  "characters": ["Lily Bunny", "Ben Bear", "Mama Duck"],
  "locations": ["Sunny Pond"],
  "assets": ["Balloons", "Flowers", "Boat"],
  "scenes": 6,
  "shots": 24,
  "status": "planning",
  "continuity_passed": false,
  "timeline": "/api/episodes/S01E001/timeline"
}
```

**Error:** `404 Not Found`

---

### POST /api/episodes/{id}/scenes

Add a scene to an episode.

**Request Body:**

```json
{
  "scene_id": "SC_001",
  "title": "Arrival at the Pond",
  "purpose": "Establish setting and characters",
  "duration": "0:30",
  "characters": ["CHAR_LILY_001", "CHAR_BEN_001"],
  "location": "ENV_POND_001",
  "learning_objective": "Introduce primary colors",
  "dialogue": null,
  "song": null,
  "mood": "happy",
  "transition": "fade_in"
}
```

**Response:** `201 Created`

```json
{
  "scene_id": "SC_001",
  "episode_id": "S01E001",
  "status": "added"
}
```

---

### POST /api/episodes/{id}/shots

Add a shot to an episode.

**Request Body:**

```json
{
  "shot_id": "SH_001",
  "scene_id": "SC_001",
  "length": 3.0,
  "camera": {
    "type": "wide",
    "movement": "static",
    "position": "front"
  },
  "characters": [
    {
      "id": "CHAR_LILY_001",
      "visible": true,
      "speaking": false,
      "singing": false,
      "animation": "wave",
      "emotion": "happy",
      "clothing": "pink_dress",
      "accessories": []
    }
  ],
  "assets": ["PROP_TREE_015", "PROP_BENCH_002"],
  "environment": "ENV_PLAYGROUND_001",
  "animation": "wave_loop_01",
  "lighting": "LIGHT_SUNRISE",
  "weather": "CLEAR",
  "dialogue": null,
  "emotion": "happy",
  "movement": "static",
  "transition": "cut"
}
```

**Response:** `201 Created`

```json
{
  "shot_id": "SH_001",
  "scene_id": "SC_001",
  "status": "added"
}
```

---

### POST /api/episodes/{id}/manifest

Build or rebuild the episode manifest.

**Request Body:** (empty or optional overrides)

```json
{
  "force_rebuild": false
}
```

**Response:** `200 OK`

```json
{
  "episode_id": "S01E001",
  "manifest_status": "complete",
  "scene_count": 6,
  "shot_count": 24,
  "asset_count": 12,
  "character_count": 3
}
```

---

### POST /api/episodes/{id}/prompts

Generate prompts for all shots in the episode.

**Request Body:**

```json
{
  "template_set": "default",
  "model_target": "stable-diffusion-v4",
  "regenerate": false
}
```

**Response:** `200 OK`

```json
{
  "episode_id": "S01E001",
  "total_prompts": 24,
  "prompts_generated": 24,
  "prompt_ids": ["PR_S01E001_001", "PR_S01E001_002", "..."]
}
```

---

### POST /api/episodes/{id}/continuity

Run continuity validation across all shots.

**Request Body:**

```json
{
  "checks": ["clothing", "weather", "lighting", "props", "location", "characters"]
}
```

**Response:** `200 OK`

```json
{
  "episode_id": "S01E001",
  "passed": true,
  "checks_performed": 6,
  "issues": [],
  "continuity_score": 1.0
}
```

On failure:

```json
{
  "episode_id": "S01E001",
  "passed": false,
  "checks_performed": 6,
  "issues": [
    {
      "type": "clothing_mismatch",
      "shot_id": "SH_012",
      "expected": "pink_dress",
      "found": "blue_shirt"
    }
  ],
  "continuity_score": 0.83
}
```

---

### POST /api/render-queue

Queue render tasks.

**Request Body:**

```json
{
  "episode_id": "S01E001",
  "shot_ids": ["SH_001", "SH_002"],
  "priority": "normal",
  "output_format": "mp4",
  "resolution": "1920x1080"
}
```

**Response:** `201 Created`

```json
{
  "queue_items": 2,
  "tasks": [
    {"task_id": "RND_001", "shot_id": "SH_001", "status": "queued"},
    {"task_id": "RND_002", "shot_id": "SH_002", "status": "queued"}
  ]
}
```

---

### GET /api/render-queue

List render queue.

**Query Parameters:**
- `status` (optional): `queued`, `rendering`, `complete`, `failed`
- `episode_id` (optional): filter by episode

**Response:** `200 OK`

```json
{
  "queue": [
    {
      "task_id": "RND_001",
      "shot_id": "SH_001",
      "episode_id": "S01E001",
      "status": "queued",
      "priority": "normal",
      "created_at": "2026-07-29T10:00:00Z"
    }
  ],
  "total": 1
}
```

---

### POST /api/quality-check

Run quality gates on specified shots.

**Request Body:**

```json
{
  "shot_ids": ["SH_001", "SH_002"],
  "gates": ["visual", "character", "environment", "animation", "audio", "continuity", "prompt", "rendering"]
}
```

**Response:** `201 Created`

```json
{
  "reports": [
    {
      "shot_id": "SH_001",
      "qc_id": "QC_001",
      "status": "pending"
    }
  ]
}
```

---

### GET /api/quality-check/{shot_id}

Get QC report for a specific shot.

**Response:** `200 OK`

```json
{
  "qc_id": "QC_001",
  "shot_id": "SH_001",
  "overall_status": "passed",
  "gates": [
    {"name": "visual", "status": "passed", "score": 0.95},
    {"name": "character", "status": "passed", "score": 1.0},
    {"name": "environment", "status": "passed", "score": 0.98},
    {"name": "animation", "status": "passed", "score": 0.92},
    {"name": "audio", "status": "passed", "score": 0.96},
    {"name": "continuity", "status": "passed", "score": 1.0},
    {"name": "prompt", "status": "passed", "score": 1.0},
    {"name": "rendering", "status": "passed", "score": 0.97}
  ],
  "issues": [],
  "checked_at": "2026-07-29T10:05:00Z"
}
```

---

## Data Models

### Series

| Field | Type | Description |
|-------|------|-------------|
| series_id | string | Unique identifier |
| title | string | Series title |
| seasons | array[Season] | Contained seasons |

### Season

| Field | Type | Description |
|-------|------|-------------|
| season_id | string | Unique identifier (e.g., S01) |
| title | string | Season title |
| episodes | array[Episode] | Contained episodes |

### Episode

| Field | Type | Description |
|-------|------|-------------|
| episode_id | string | Unique identifier (e.g., S01E001) |
| title | string | Episode title |
| duration | string | Runtime (e.g., "3:12") |
| target_age | string | Target age range |
| learning_goal | string | Educational objective |
| has_song | boolean | Contains song |
| has_narration | boolean | Contains narration |
| characters | array[string] | Character list |
| locations | array[string] | Location list |
| assets | array[string] | Asset list |
| status | string | Current production status |

### Scene

| Field | Type | Description |
|-------|------|-------------|
| scene_id | string | Unique identifier |
| title | string | Scene title |
| purpose | string | Scene purpose |
| duration | string | Scene runtime |
| characters | array[string] | Character IDs |
| location | string | Location ID |
| learning_objective | string | Learning objective |
| dialogue | string | Dialogue content |
| song | string | Song reference |
| mood | string | Scene mood |
| transition | string | Transition type |

### Shot

| Field | Type | Description |
|-------|------|-------------|
| shot_id | string | Unique identifier |
| scene_id | string | Parent scene |
| length | float | Duration in seconds |
| camera | Camera | Camera configuration |
| characters | array[CharacterAssignment] | Character states |
| assets | array[string] | Asset IDs |
| environment | string | Environment ID |
| animation | string | Animation reference |
| lighting | string | Lighting ID |
| weather | string | Weather condition |
| dialogue | string | Dialogue line |
| emotion | string | Shot emotion |
| movement | string | Camera movement |
| transition | string | Transition type |

### Camera

| Field | Type | Description |
|-------|------|-------------|
| type | string | Shot type (wide, medium, close-up, etc.) |
| movement | string | Movement type (static, pan, track, etc.) |
| position | string | Camera position (front, side, overhead, etc.) |

### Timeline Event

| Field | Type | Description |
|-------|------|-------------|
| time | string | Timestamp (e.g., "00:00") |
| event | string | Event description |

### Render Task

| Field | Type | Description |
|-------|------|-------------|
| task_id | string | Unique identifier |
| shot_id | string | Shot to render |
| status | string | Task status |
| priority | string | Priority level |
| output_format | string | Output format |
| resolution | string | Output resolution |
| created_at | datetime | Creation timestamp |

### QC Report

| Field | Type | Description |
|-------|------|-------------|
| qc_id | string | Unique identifier |
| shot_id | string | QC'd shot |
| overall_status | string | Pass/fail status |
| gates | array[GateResult] | Per-gate results |
| issues | array[Issue] | Detected issues |
| checked_at | datetime | Check timestamp |
