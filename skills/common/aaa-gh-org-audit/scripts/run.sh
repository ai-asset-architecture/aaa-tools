#!/usr/bin/env bash
set -euo pipefail

ORG=${ORG:-ai-asset-architecture}
PYTHON_BIN=${PYTHON_BIN:-python3}
ROOT=${AAA_ROOT:-/Users/imac/Documents/Code/AI-Lotto/AAA_WORKSPACE}

$PYTHON_BIN "$ROOT/aaa-evals/runner/run_github_audit.py"
