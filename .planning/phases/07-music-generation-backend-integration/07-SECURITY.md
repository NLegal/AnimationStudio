---
phase: 07-music-generation-backend-integration
slug: music-generation-backend-integration
status: verified
# threats_open = count of OPEN threats at or above workflow.security_block_on severity (the blocking gate)
threats_open: 0
asvs_level: 1
created: 2026-08-25
---

# Phase 07 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| process ↔ local ACE-Step HTTP service | Untrusted/malformed JSON crosses here once adapters wire in (plan 07-02); seam + error map established in plan 01 | JSON payloads, audio bytes, HTTP headers |
| environment ↔ process | ACESTEP_API_KEY / ACESTEP_BASE_URL / MUSIC_BACKEND enter as operator-controlled strings | Secret (API key), configuration URLs, backend name |
| CLI ↔ operator | Arguments and printed reports must never leak credentials | CLI arguments, stdout/stderr output |
| tests ↔ world | CI must have ZERO network/audio-hardware/database side effects | No data crossing — fake transports + fail-loud guards |
| process ↔ repo-root asset-catalog DB | Database is NEVER opened, written, or imported by this phase | No data crossing — constraint C2 enforced |

---

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|-----------|----------|-----------|----------|-------------|------------|--------|
| T7-01-SC | Tampering (supply chain) | dependency set of src/music_generation | high | mitigate | Constraint C4 grep-gated: stdlib urllib.request transport only, zero new dependencies declared or imported | closed |
| T7-01-T | Tampering | _get_json/_post_json response decoding | medium | mitigate | Strict stdlib json.loads decoding in _decode_json_object; malformed/non-dict bodies → typed GenerationFailed; no dynamic evaluation | closed |
| T7-01-I | Info Disclosure | transport helpers / exception messages | high | mitigate | Helpers never log or embed header values (incl. Authorization) in messages; _http_error_to_typed maps status codes only; test_token_never_leaks sweeps full matrix | closed |
| T7-01-D | Denial of Service | generate() polling loop | medium | mitigate | Hard deadline timeout_s=300 via _monotonic(), bounded exponential backoff capped ×8 via _sleep(), per-call (5,30) connect/read timeouts via _TRANSPORT_TIMEOUT | closed |
| T7-01-C | Database integrity | entire package vs repo-root asset-catalog DB | high | mitigate | Constraint C2 grep-gated: no sqlite3/DB driver imports anywhere in src/music_generation/; results held in memory only | closed |
| T7-01-S | Spoofing | local service identity | low | accept | Single-operator localhost deployment at ASVS L1; Bearer verification is the server's concern | closed |
| T7-01-R | Repudiation | offline library layer | low | accept | No security-relevant actions taken in-process; Phase 8 job wiring owns audit needs | closed |
| T7-01-E | Elevation of Privilege | package surface | low | accept | Library performs no privileged operations, subprocesses, or filesystem writes outside process memory | closed |
| T7-02-I | Info Disclosure | AceStepBackend auth header handling; CLI reporting | high | mitigate | Key read from env/constructor only; header assembled at call time (_auth_headers); AceStepBackend never embeds api_key in exception messages or log records; CLI dry-run dumps request model with no credentials; test_token_never_leaks asserts secret absent from all exception reprs and captured log records | closed |
| T7-02-T | Tampering | response parsing in ace_step.py | medium | mitigate | Strict JSON decoding via _decode_json_object; missing/non-string job_id → GenerationFailed; non-dict poll bodies → GenerationFailed; unknown status strings → GenerationFailed; audio bytes accepted as opaque binary with content-type warning only | closed |
| T7-02-D | Denial of Service | adapter polling vs slow/hung local service | medium | mitigate | Inherits plan-01 caps: overall timeout_s=300 deadline, exponential backoff capped ×8, (5,30) per-call timeouts; _HEALTH_TIMEOUT=(5.0,5.0) for probes; deadline breach raises GenerationFailed with job id + elapsed | closed |
| T7-02-S | Spoofing | rogue service at configured base URL | low | accept | ASVS L1 single-operator localhost tool; base URL is operator-set env; Bearer secret never sent anywhere except the configured service | closed |
| T7-02-E | Elevation of Privilege | CLI execution path | low | accept | Script performs file writes only under operator-supplied --out; no subprocess, no privileged ops, no eval of server data | closed |
| T7-02-R | Repudiation | CLI runs | low | accept | Single-operator local tool; summary lines to stdout satisfy traceability at L1; audit trails are Phase 8 batch-ops scope | closed |
| T7-02-SC | Tampering (supply chain) | dependency set of new modules + CLI | high | mitigate | Constraint C4 grep-gated: stdlib urllib.request transport consumed from plan-01 seam; zero packages installed this phase; generate_phase7.py imports only stdlib + src.music_generation public names | closed |
| T7-02-C | Database integrity | whole phase vs repo-root asset-catalog DB | high | mitigate | Constraint C2 grep-gated across src/, scripts/, and tests: no DB driver imports anywhere in music_generation package or generate_phase7.py; CLI writes only under --out; persistence remains Phase 8 scope | closed |

*Status: open · closed · open — below block_on threshold (non-blocking)*
*Severity: critical > high > medium > low — only open threats at or above workflow.security_block_on count toward threats_open*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---------|------------|-----------|-------------|------|
| AR-07-01 | T7-01-S | Single-operator localhost deployment at ASVS L1; Bearer verification delegated to the local ACE-Step server — not this package's concern | security-auditor | 2026-08-25 |
| AR-07-02 | T7-01-R | Offline library layer takes no security-relevant actions; audit trail ownership belongs to Phase 8 job wiring | security-auditor | 2026-08-25 |
| AR-07-03 | T7-01-E | Library performs no privileged operations, subprocesses, or filesystem writes — no attack surface to mitigate | security-auditor | 2026-08-25 |
| AR-07-04 | T7-02-S | ASVS L1 single-operator localhost tool; base URL is operator-controlled env; no spoofing mitigations needed at this deployment model | security-auditor | 2026-08-25 |
| AR-07-05 | T7-02-E | CLI writes only under operator-supplied --out; no subprocess/exec/eval; minimal privilege surface | security-auditor | 2026-08-25 |
| AR-07-06 | T7-02-R | Single-operator local tool; stdout summary satisfies traceability at L1; batch-ops audit trails are Phase 8 scope | security-auditor | 2026-08-25 |

*Accepted risks do not resurface in future audit runs.*

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-08-25 | 16 | 16 | 0 | gsd-security-auditor |

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-08-25
