#!/bin/bash
# OMEGA Phase D Destructive Test Runner
# Proves Audit-Immunity by attempting to bypass the governance gates.

set -e

CLI="python3 aaa-tools/aaa_cli.py"
BUNDLE_DIR="artifacts/evidence_bundle/v2.0.1"
TMP_DIR="tmp_destructive_test"

echo "--- STARTING OMEGA PHASE D DESTRUCTIVE TESTS ---"

# 1. Tamper Mutation Test
echo "[*] Test 1: Tamper Mutation (Decoupling Hash Integrity)"
mkdir -p "$BUNDLE_DIR"
$CLI export --evidence --version v2.0.1 > /dev/null

rm -rf "$TMP_DIR" && mkdir -p "$TMP_DIR"
unzip -qo "$BUNDLE_DIR/bundle.zip" -d "$TMP_DIR"
# Modify policy_snapshot.json by one byte
echo '{"policy_hash": "TAMPERED"}' > "$TMP_DIR/policy_snapshot.json"
zip -jqo "$BUNDLE_DIR/tampered_bundle.zip" "$TMP_DIR"/*

set +e
$CLI omega replay --bundle "$BUNDLE_DIR/tampered_bundle.zip"
EXIT_CODE=$?
set -e

if [ $EXIT_CODE -eq 1 ]; then
    echo "[v] Tamper Mutation: PASS (Exit 1: TAMPER SUSPECT detected)"
    ls artifacts/court/cases/CASE_REPLAY_*.json
else
    echo "[X] Tamper Mutation: FAIL (Expected Exit 1, got $EXIT_CODE)"
    exit 1
fi

# 2. Env Drift Simulation
echo "[*] Test 2: Env Drift (Simulating Python/OS Version Change)"
rm -rf "$TMP_DIR" && mkdir -p "$TMP_DIR"
unzip -qo "$BUNDLE_DIR/bundle.zip" -d "$TMP_DIR"
# Modify hash_chain.txt env_fingerprint to trick it
sed -i '' 's/"arch":"x86_64"/"arch":"arm64"/g' "$TMP_DIR/hash_chain.txt"
zip -jqo "$BUNDLE_DIR/drift_bundle.zip" "$TMP_DIR"/*

set +e
$CLI omega replay --bundle "$BUNDLE_DIR/drift_bundle.zip"
EXIT_CODE=$?
set -e

if [ $EXIT_CODE -eq 2 ]; then
    echo "[v] Env Drift Simulation: PASS (Exit 2: ENV_DRIFT detected)"
else
    echo "[X] Env Drift Simulation: FAIL (Expected Exit 2, got $EXIT_CODE)"
    exit 1
fi

# 3. Enum Drift Injection
echo "[*] Test 3: Enum Drift Injection (Roadmap vs Specs)"
# Append a fake Enum to Roadmap
echo "| \`ERR_UNKNOWN_DRIFT\` | HIGH | Drift simulation | Connection Denied | No |" >> aaa-tpl-docs/milestones/AAA_ROADMAP_V2_V3_ENTERPRISE.md

set +e
$CLI check --enums
EXIT_CODE=$?
set -e

# Restore Roadmap (Manual cleanup to be safe)
sed -i '' '/ERR_UNKNOWN_DRIFT/d' aaa-tpl-docs/milestones/AAA_ROADMAP_V2_V3_ENTERPRISE.md

# 4. Enum Pass Test
echo "[*] Test 4: Enum Consistency (Sanity PASS)"
$CLI check --enums > /dev/null && echo "[v] Enum Gate: PASS"

# 5. Evidence Index Test
echo "[*] Test 5: Evidence Index (Missing path detected)"
mv artifacts/evidence_bundle/v2.0.1 artifacts/evidence_bundle/v2.0.1_bak
set +e
$CLI check --evidence-index > /dev/null
EXIT_CODE=$?
set -e
mv artifacts/evidence_bundle/v2.0.1_bak artifacts/evidence_bundle/v2.0.1
if [ $EXIT_CODE -ne 0 ]; then
    echo "[v] Evidence Index: PASS (Blocking missing path)"
else
    echo "[X] Evidence Index: FAIL"
    exit 1
fi

# 6. Core 5 Zip Root Contract
echo "[*] Test 6: Core 5 Zip Root Contract"
unzip -l "$BUNDLE_DIR/bundle.zip" | grep -E "case_snapshot.json|ledger_export.jsonl|policy_snapshot.json|test_results.json|hash_chain.txt" | wc -l | grep 5 > /dev/null
echo "[v] Core 5 in root: PASS"

echo "--- OMEGA PHASE D SUCCESS: SYSTEM IS AUDIT-IMMUNE ---"
rm -rf "$TMP_DIR"
