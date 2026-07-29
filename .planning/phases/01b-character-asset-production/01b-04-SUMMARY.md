---
phase: 01b
plan: 04
completed_at: "2026-07-29T07:50:00Z"
state: partial
tasks_completed: 2
tasks_total: 4
---

## Plan 01b-04: Identity Lock + Face Lock — Summary

**Objective:** Create orchestration scripts for reference sheet and expression generation.

### Completed

1. **scripts/generate_identity_lock.py** — Identity Lock pipeline: 4 angles × 80 candidates each, scoring, diversity filtering, shortlisting, Review UI launch.
2. **scripts/generate_face_lock.py** — Face Lock pipeline: 32 expressions × 60 candidates each, scoring with front reference, diversity filtering, shortlisting, Review UI launch.

### Pending (requires ComfyUI + human review)

- Run `scripts/generate_identity_lock.py` against ComfyUI
- Human review of reference sheet winners
- Run `scripts/generate_face_lock.py` against ComfyUI
- Human review of expression winners
- Approved images in `Universe/Characters/Lily Bunny/references/` and `expressions/`

### Self-Check: PASSED

- Both scripts import cleanly
- Follow same patterns as each other and the plan spec
- D-05 progressive pipeline, D-09/D-10 expression list, D-13 scoring weights, D-14 thresholds documented
