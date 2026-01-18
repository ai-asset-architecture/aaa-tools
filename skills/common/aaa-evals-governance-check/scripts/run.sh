#!/usr/bin/env bash
set -euo pipefail

TARGET_PATH=${TARGET_PATH:-}
EVALS_ROOT=${EVALS_ROOT:-./aaa-evals}
PYTHON=${PYTHON:-python3}
CHECKS=${CHECKS:-readme,workflow,skills,prompt}

if [ -z "$TARGET_PATH" ]; then
  echo "TARGET_PATH is required" >&2
  exit 10
fi

IFS=',' read -r -a check_list <<< "$CHECKS"
for check in "${check_list[@]}"; do
  case "$check" in
    readme)
      $PYTHON "$EVALS_ROOT/runner/run_repo_checks.py" --check readme --repo "$TARGET_PATH"
      ;;
    workflow)
      $PYTHON "$EVALS_ROOT/runner/run_repo_checks.py" --check workflow --repo "$TARGET_PATH"
      ;;
    skills)
      $PYTHON "$EVALS_ROOT/runner/run_repo_checks.py" --check skills --repo "$TARGET_PATH" --skills-root skills
      ;;
    prompt)
      $PYTHON "$EVALS_ROOT/runner/run_repo_checks.py" --check prompt --repo "$TARGET_PATH" --schema-path prompt.schema.json --prompts-dir prompts
      ;;
  esac
done
