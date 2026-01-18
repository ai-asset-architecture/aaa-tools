#!/usr/bin/env bash
set -euo pipefail

PLAN_PATH=${PLAN_PATH:-}
SCHEMA_PATH=${SCHEMA_PATH:-specs/plan.schema.json}

if [ -z "$PLAN_PATH" ]; then
  echo "PLAN_PATH is required" >&2
  exit 10
fi

aaa init validate-plan --plan "$PLAN_PATH" --schema "$SCHEMA_PATH" --jsonl
