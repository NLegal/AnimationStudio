---
phase: 08
slug: music-generation-pipeline-wiring
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-08-25
---

# Phase 08 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| CLI ↔ operator input | --category/--topic/--seed/--backend strings flow into filenames and backend selection | User-supplied text → slugified filenames, backend registry lookup |
| browser ↔ FastAPI routes | Untrusted form fields (category/topic/backend) cross into request building and filenames | Form data → manifest entries, background job configs |
| process ↔ local ACE-Step HTTP service | Reached only through Phase 7 adapter; UI adds no parsing | MusicRequest/MusicResult DTOs (no raw HTTP parsing) |
| environment ↔ process | MUSIC_BACKEND / ACESTEP_* enter as env strings | Backend name strings → registry lookup |
| notebook ↔ Colab VM | Service clone/install executes vendor commands on operator's VM | Shell commands in isolated venv, never studio env |
| tests ↔ world | Zero network, zero real audio, zero database side effects | MockBackend + fail-loud transport guards |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T8-01 | Tampering/Elevation of Privilege | _slug / song_filename path construction (CLI + UI) | high | mitigate | Both filename components slugified to [a-z0-9-] (slashes/dots eliminated); empty slug → literal "song" fallback; join confined under fixed output dir; UI worker funnels both components through the same helpers (single choke point); dedicated traversal unit test `test_slug_strips_traversal` | closed |
| T8-02-I | Info Disclosure | manifest.json entries + stdout/stderr reporting + job payloads | high | mitigate | Entry key-set pinned by golden test to the thirteen non-se1cret fields (seed/job_id/backend metadata only — never headers, URLs-with-keys, or credentials); failure messages carry typed exception text only; caplog-style logging emits only job_id + exception text (no env contents) | closed |
| T8-03-D | Denial of Service | Unbounded batch via UI request | high | mitigate | POST /music/generate handles EXACTLY one song per submit — no count/scope parameters exist on the route; per-song work capped by protocol timeout_s=300; batches belong to CLI/notebook (divergence #1); incremental manifest means interruption loses at most the in-flight song | closed |
| T8-04-C | Tampering (data integrity) | Repo-root asset-catalog database | high | mitigate | Constraint C2: music routes dereference neither repo nor char_repo; JobQueue stays repo-less (no repository argument); no sqlite3 import in phase files (grep-gate test `test_no_sqlite_imports`); md5 byte-identity fixture proves catalog.db unchanged across batch tests; explicit C2 comments in app.py | closed |
| T8-SC | Tampering (supply chain) | Dependency set + notebook service cell | high | mitigate | Zero new dependencies this phase (pyproject.toml diff-gate in acceptance criteria); notebook service cell clones OFFICIAL ACE-Step-1.5 repo into ISOLATED uv venv on operator VM — never mixes deps into studio env; legacy v1 pip package grep-gated | closed |
| T8-S | Spoofing | Local service identity / unauthenticated localhost routes | low | accept | Single-operator localhost tool at ASVS L1; adapter-side concern already dispositioned in Phase 7; matches every existing review-ui route disposition | closed |
| T8-R | Repudiation | Batch runs / UI-initiated generations | low | accept | Stdout summary + manifest generated_at timestamps + JobQueue records provide adequate operator traceability at L1 | closed |
| T8-E | Elevation of Privilege | Script execution path / worker file writes | low | accept | File writes confined to the operator-chosen output directory via shared helpers; no subprocess, no eval, no privileged operations; music routes write only under configured music_dir | closed |

*Status: open · closed · open — below high threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-08-S | T8-S | Single-operator localhost tool; authentication not meaningful at L1 for developer-facing local UI | gsd-security-auditor | 2026-08-25 |
| AR-08-R | T8-R | stdout summary + manifest timestamps + JobQueue provide adequate traceability for L1 single-operator tool | gsd-security-auditor | 2026-08-25 |
| AR-08-E | T8-E | Writes confined to configured music_dir via shared helpers; no subprocess/eval introduced | gsd-security-auditor | 2026-08-25 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-25 | 8 | 8 | 0 | gsd-security-auditor (ASVS L1, block_on: high) |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-25
