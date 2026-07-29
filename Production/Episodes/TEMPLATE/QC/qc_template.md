# Quality Control Checklist Template

## Pre-Generation Checklist

Before generation begins, verify every item:

- [ ] Episode manifest is complete and approved
- [ ] Episode timeline is finalized and approved
- [ ] Story has been decomposed into scenes
- [ ] Every scene has a defined purpose and location
- [ ] All shots are defined with shot IDs
- [ ] Cameras are assigned to every shot
- [ ] Characters are assigned to every shot with correct states
- [ ] Assets are referenced by production IDs (no free-form names)
- [ ] Animation references are assigned
- [ ] Audio is synchronized to the master timeline
- [ ] Prompt templates are resolved
- [ ] Render queue is generated
- [ ] Quality gates are configured
- [ ] Continuity validation has passed

---

## Post-Generation Checklist

### Visual
- [ ] Image is properly framed
- [ ] Lighting matches the assigned configuration
- [ ] Color palette is consistent with the episode
- [ ] No visual artifacts or rendering errors
- [ ] Resolution meets spec (1920x1080 minimum)
- [ ] Composition follows the camera plan

### Character
- [ ] Correct characters appear in the shot
- [ ] Character clothing matches continuity specification
- [ ] Character accessories are correct
- [ ] Character proportions are consistent
- [ ] Character expressions match assigned emotion
- [ ] Character coloring is on-model

### Environment
- [ ] Environment matches the assigned ID
- [ ] Weather matches continuity specification
- [ ] Time of day is consistent
- [ ] Props are placed correctly
- [ ] Background is consistent with adjacent shots

### Animation
- [ ] Animation plays correctly
- [ ] No clipping or geometry issues
- [ ] Lip sync is accurate (if applicable)
- [ ] Movement speed is appropriate for target age
- [ ] Animation loop is seamless (if looping)

### Audio
- [ ] Dialogue is clear and intelligible
- [ ] Narration is properly synchronized
- [ ] Music levels are appropriate
- [ ] Sound effects are timed correctly
- [ ] Lip sync matches audio track
- [ ] No distortion or audio artifacts

### Continuity
- [ ] Character clothing matches previous shot
- [ ] Props are in consistent positions
- [ ] Weather conditions are consistent
- [ ] Lighting matches adjacent shots
- [ ] Character positions are spatially consistent

---

## QC Report Form

```
Episode ID: _______________
Shot ID:    _______________
Scene ID:   _______________
Reviewer:   _______________
Date:       _______________

### Gate Results

| Gate          | Pass/Fail | Score | Notes |
|---------------|-----------|-------|-------|
| Visual        |           |       |       |
| Character     |           |       |       |
| Environment   |           |       |       |
| Animation     |           |       |       |
| Audio         |           |       |       |
| Continuity    |           |       |       |
| Prompt        |           |       |       |
| Rendering     |           |       |       |

### Issues Found

| # | Gate | Description | Severity |
|---|------|-------------|----------|
|   |      |             |          |

### Overall Verdict

[ ] PASS — All gates passed. Shot is approved for final render.
[ ] FAIL — One or more gates failed. See issues above.

### Approval

Signed: _________________   Date: _______________
```

---

## Approval Workflow

```
Shot Generated
     ↓
Pre-Generation Checklist Verified
     ↓
Post-Generation QC Gates Run
     ↓
     ├── All Pass → Shot Approved → Render Queue
     └── Any Fail → Shot Rejected → Revision Notes
                      ↓
              Fix Issues → Re-run QC Gates
```
