#!/usr/bin/env bash
set -euo pipefail

TARGET_PATH=${TARGET_PATH:-}
EVALS_ROOT=${EVALS_ROOT:-./aaa-evals}

if [ -z "$TARGET_PATH" ]; then
  echo "TARGET_PATH is required" >&2
  exit 10
fi

python "$EVALS_ROOT/runner/run_repo_checks.py" --check workflow --repo "$TARGET_PATH"
