#!/usr/bin/env bash
set -euo pipefail

PROMPTS_ROOT=${PROMPTS_ROOT:-}
SCHEMA_PATH=${SCHEMA_PATH:-prompt.schema.json}
EVALS_ROOT=${EVALS_ROOT:-./aaa-evals}
PYTHON=${PYTHON:-python3}

if [ -z "$PROMPTS_ROOT" ]; then
  echo "PROMPTS_ROOT is required" >&2
  exit 10
fi

$PYTHON "$EVALS_ROOT/runner/run_repo_checks.py" --check prompt --repo "$PROMPTS_ROOT" --schema-path "$SCHEMA_PATH" --prompts-dir prompts
