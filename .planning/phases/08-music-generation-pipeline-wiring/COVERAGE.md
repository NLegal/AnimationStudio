# API Coverage — Phase 8

No external API integration: Phase 8 is pure wiring — every entry point added here (CLI generation mode, Review UI routes, notebook cells) consumes the in-repo `src.music_generation` Python layer behind `backend.generate()` and makes zero new HTTP calls; the complete capability matrices for both external services were already decided at plan time in `.planning/phases/07-music-generation-backend-integration/COVERAGE.md` and remain binding.

Detector note: the deterministic scan fired on research prose describing Suno wrapper APIs ("Suno assumed reachable via wrapper APIs ... stub stays refusing") — that sentence records an opt-out decided in Phase 7, not an integration performed here. Per checkpoint rules no matrix rows are fabricated for a surface this phase does not touch.

Wiring-surface decisions made THIS phase (entry-point exposure choices over the already-integrated backend, recorded for traceability):

- CLI batch generation (`--generate`, all three backends): exposed per the ROADMAP goal — batch song requests from the 24 categories.
- UI single-song generation (`POST /music/generate`): exposed following the research Open Question 2 recommendation; batches stay on CLI/notebook to cap request-time DoS.
- UI pure prompt preview (`POST /music/prompt`): exposed on the motion-page precedent — zero side effects.
- UI job polling (`GET /api/music/jobs`): exposed for BackgroundTasks lifecycle visibility.
- Notebook orchestration (offline mock path / isolated ace-step GPU path): exposed mirroring the Phase 4 notebook family pattern.
