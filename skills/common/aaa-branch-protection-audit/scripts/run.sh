#!/usr/bin/env bash
set -euo pipefail

ORG=${ORG:-}
PLAN_PATH=${PLAN_PATH:-}
AAA_BIN=${AAA_BIN:-aaa}

if [ -z "$ORG" ]; then
  echo "ORG is required" >&2
  exit 10
fi

if [ -z "$PLAN_PATH" ]; then
  echo "PLAN_PATH is required" >&2
  exit 10
fi

$AAA_BIN init protect --org "$ORG" --from-plan "$PLAN_PATH" --dry-run --jsonl
