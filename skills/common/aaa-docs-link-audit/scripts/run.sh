#!/usr/bin/env bash
set -euo pipefail

TARGET_PATH=${TARGET_PATH:-}
DOCS_PATTERN=${DOCS_PATTERN:-"<org>-docs"}

if [ -z "$TARGET_PATH" ]; then
  echo "TARGET_PATH is required" >&2
  exit 10
fi

rg -n "$DOCS_PATTERN" "$TARGET_PATH/docs/README.md"
