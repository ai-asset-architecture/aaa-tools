# Local Codex CLI Procedure (v0.1)

This is the minimal local procedure to bootstrap a new project using Codex CLI.

## 1) Prerequisites
- `gh` CLI installed and authenticated (`gh auth status`)
- `git` installed
- `aaa` CLI available in PATH (`aaa --version`)
- Network access enabled for GitHub

## 2) One-line execution (Codex)
Replace placeholders and run:

```bash
codex exec --full-auto --json \
  --output-schema aaa-tools/runbooks/init/output.schema.json \
  "Use the AAA init runbook at aaa-tools/runbooks/init/INIT_PROJECT.md. \nInputs: PROJECT_NAME=<NAME>, PROJECT_PREFIX=<PREFIX>, TARGET_ORG=<ORG>, VISIBILITY=private. \nExecute the deterministic aaa init flow first, then handle exceptions and output the final JSON report only."
```

## 3) Expected output
- Codex outputs a single JSON object (stdout) matching `output.schema.json`.
- If errors occur, they are reported in the JSON under `failures` or `exceptions`.

## References
- `aaa-tools/runbooks/init/INIT_PROJECT.md`
- `aaa-tools/runbooks/init/plan.v0.1.json`
- `aaa-tools/specs/CLI_CONTRACT.md`
- `.github/BOOTSTRAP_PROTOCOL.md`
