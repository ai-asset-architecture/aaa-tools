# Security Policy

## Supported Scope

Security issues for `aaa-tools` include:

- Runbook execution safety
- File-system boundary enforcement
- Permission and authorization gates
- Release integrity and evidence-promotion boundaries

## Reporting

Please report security concerns privately to the maintainers before opening a public issue if the issue could enable misuse or compromise.

Include:

- Affected command or module
- Reproduction steps
- Expected boundary
- Actual behavior
- Impact assessment

## Security Posture

AAA favors fail-closed behavior where practical:

- Deterministic schemas constrain accepted inputs
- Runbook file operations reject path traversal
- Readiness and support-truth boundaries are explicit
- Human approval is retained for high-trust actions

## Non-Goals

`aaa-tools` is not a hosted security product. It provides governance and automation building blocks; operators remain responsible for repository permissions, secrets management, and release controls.
