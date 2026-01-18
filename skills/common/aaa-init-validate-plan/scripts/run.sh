#!/usr/bin/env bash
set -euo pipefail

PLAN_PATH=${PLAN_PATH:-}
SCHEMA_PATH=${SCHEMA_PATH:-specs/plan.schema.json}
AAA_BIN=${AAA_BIN:-aaa}

if [ -z "$PLAN_PATH" ]; then
  echo "PLAN_PATH is required" >&2
  exit 10
fi

$AAA_BIN init validate-plan --plan "$PLAN_PATH" --schema "$SCHEMA_PATH" --jsonl
