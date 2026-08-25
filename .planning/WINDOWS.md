---
schema_version: 1
open_count: 1
waived_count: 0
fixed_count: 0
total_count: 1
last_updated: 2026-08-25T02:06:08.908Z
---

# Broken Windows Ledger

> Cross-phase defect register. `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 07 | deviation | .planning/phases/07-music-generation-backend-integration/deferred-items.md |  | Full-suite exit != 0 solely from pre-existing unrelated failures (story_engine/review_ui_generation families pre-dating Phase 7; evidence in deferred-items.md) | open |  | 2026-08-25T02:06:08.908Z |  |

````json
[
  {
    "id": 1,
    "kind": "deviation",
    "phase": "07",
    "file": ".planning/phases/07-music-generation-backend-integration/deferred-items.md",
    "line": null,
    "description": "Full-suite exit != 0 solely from pre-existing unrelated failures (story_engine/review_ui_generation families pre-dating Phase 7; evidence in deferred-items.md)",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-08-25T02:06:08.908Z",
    "resolved_at": null
  }
]
````
