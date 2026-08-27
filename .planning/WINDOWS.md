---
schema_version: 1
open_count: 2
waived_count: 1
fixed_count: 0
total_count: 3
last_updated: 2026-08-27T13:33:00.578Z
---

# Broken Windows Ledger

> Cross-phase defect register. `/gsd-ship` blocks while `open_count > 0`.
> Waive with `gsd-tools windows waive <id> "<reason>"` (reason required).
> Mark fixed with `gsd-tools windows fixed <id>`.

| id | phase | kind | file | line | description | status | reason | recorded_at | resolved_at |
|----|-------|------|------|------|-------------|--------|--------|-------------|-------------|
| 1 | 07 | deviation | .planning/phases/07-music-generation-backend-integration/deferred-items.md |  | Full-suite exit != 0 solely from pre-existing unrelated failures (story_engine/review_ui_generation families pre-dating Phase 7; evidence in deferred-items.md) | open |  | 2026-08-25T02:06:08.908Z |  |
| 2 | 01c | unrun-verify | colab/AnimationStudio_Colab_Training.ipynb |  | Operator GPU run of training notebook pending — lily-bunny_v1.0.safetensors + benchmark report (CHAR-07 criterion 2, deferred-human; tracked as coverage D3) | open |  | 2026-08-27T13:28:30.616Z |  |
| 3 | 01c | unrun-verify | colab/AnimationStudio_Colab_Training.ipynb |  | Operator GPU run of training notebook pending — lily-bunny_v1.0.safetensors + benchmark report (CHAR-07 criterion 2, deferred-human; tracked as coverage D3) | waived | Duplicate of entry 2 (same unrun-verify, appended during ledger inspection) | 2026-08-27T13:29:40.474Z | 2026-08-27T13:33:00.578Z |

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
  },
  {
    "id": 2,
    "kind": "unrun-verify",
    "phase": "01c",
    "file": "colab/AnimationStudio_Colab_Training.ipynb",
    "line": null,
    "description": "Operator GPU run of training notebook pending — lily-bunny_v1.0.safetensors + benchmark report (CHAR-07 criterion 2, deferred-human; tracked as coverage D3)",
    "status": "open",
    "reason": "",
    "recorded_at": "2026-08-27T13:28:30.616Z",
    "resolved_at": null
  },
  {
    "id": 3,
    "kind": "unrun-verify",
    "phase": "01c",
    "file": "colab/AnimationStudio_Colab_Training.ipynb",
    "line": null,
    "description": "Operator GPU run of training notebook pending — lily-bunny_v1.0.safetensors + benchmark report (CHAR-07 criterion 2, deferred-human; tracked as coverage D3)",
    "status": "waived",
    "reason": "Duplicate of entry 2 (same unrun-verify, appended during ledger inspection)",
    "recorded_at": "2026-08-27T13:29:40.474Z",
    "resolved_at": "2026-08-27T13:33:00.578Z"
  }
]
````
