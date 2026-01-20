#!/usr/bin/env bash
set -euo pipefail
skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ ! -f "$skill_dir/SKILL.md" ]; then
  echo "FAIL: SKILL.md missing"
  exit 1
fi
if ! grep -q "## Execution Test" "$skill_dir/SKILL.md"; then
  echo "FAIL: Execution Test section missing"
  exit 1
fi
echo "PASS"
