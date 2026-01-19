# aaa-gh-org-audit

## Routing Logic

### Hard Rules (Governance)
- IF gh auth status fails THEN stop and request login

### Soft Rules (Scoring)
- Base score: 0

### Routing Decision
- Score < 3: single_path (run org audit)

## Execution Steps
1. Verify gh auth and org access.
2. Run org audit script.
3. Save report to `aaa-tpl-docs/reports/`.

## Fallback (Resilience)
- IF API rate limit THEN wait and retry once, else report partial.

## Inputs / Outputs
- Inputs: org name, output path
- Outputs: audit report file


## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- Requires org access; cannot fix settings.

Audit GitHub org repositories for AAA v0.1 governance compliance.

## Inputs
- `ORG` (required): GitHub org name (default: ai-asset-architecture)

## Usage
```bash
ORG=ai-asset-architecture bash scripts/run.sh
```

## Outputs
- Writes report to `aaa-tpl-docs/reports/github_audit_report_YYYYMMDD_HHMM.md`.
