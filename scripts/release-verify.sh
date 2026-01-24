#!/usr/bin/env bash
set -euo pipefail

TAG="${1:-}"
if [[ -z "${TAG}" ]]; then
  echo "usage: release-verify.sh <tag>"
  exit 2
fi

REPO_URL="https://github.com/ai-asset-architecture/aaa-tools.git"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

python3 -m venv "${TMP_DIR}/venv"
source "${TMP_DIR}/venv/bin/activate"

python3 -m pip install --upgrade pip >/dev/null
python3 -m pip install --no-cache-dir "git+${REPO_URL}@${TAG}" >/dev/null

INSTALLED_VERSION="$(aaa --version | awk '{print $2}')"
if [[ "${INSTALLED_VERSION}" != "${TAG#v}" ]]; then
  echo "version mismatch: expected ${TAG#v}, got ${INSTALLED_VERSION}"
  exit 3
fi

python3 - <<'PY'
import importlib.metadata as md

dist = md.distribution("aaa-tools")
files = [str(f) for f in dist.files or []]
has_cmd = any(f.startswith("aaa/cmd") for f in files)
if not has_cmd:
    raise SystemExit("package missing aaa.cmd subpackage")
PY

echo "release-verify: OK (${TAG})"
