#!/usr/bin/env bash
set -euo pipefail

ORG=${ORG:-}
PLAN_PATH=${PLAN_PATH:-}

if [ -z "$ORG" ]; then
  echo "ORG is required" >&2
  exit 10
fi

if [ -z "$PLAN_PATH" ]; then
  echo "PLAN_PATH is required" >&2
  exit 10
fi

aaa init protect --org "$ORG" --from-plan "$PLAN_PATH" --dry-run --jsonl
