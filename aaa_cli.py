#!/usr/bin/env python3
"""
AAA Governance Control Plane CLI (v2.1 Diamond Refined)
Mechanical baseline for Audit-Immune Governance.
"""

import sys
import argparse
import json
import os
import re
import hashlib
import platform
import zipfile

# --- Canonical Enums & Files ---
LEDGER_ENUM_FILE = "aaa-tpl-docs/specs/ledger_event_enum_v1.md"
COURT_ENUM_FILE = "aaa-tpl-docs/specs/court_case_type_enum_v1.md"
REASON_ENUM_FILE = "aaa-tpl-docs/specs/reason_code_enum_v1.md"
ROADMAP_FILE = "aaa-tpl-docs/milestones/AAA_ROADMAP_V2_V3_ENTERPRISE.md"

CORE_FILES = ["case_snapshot.json", "ledger_export.jsonl", "policy_snapshot.json", "test_results.json"]

def get_env_fingerprint():
    """Generates canonical environment fingerprint (Sorted JSON, no whitespace)."""
    data = {
        "os_v": platform.platform(),
        "arch": platform.machine(),
        "py_v": platform.python_version(),
        "aaa_v": "2.1.0-diamond-refined",
        "policy_hash": "H_POLICY_TBD",
        "capability_pack_hash": "H_CAP_TBD"
    }
    return json.dumps(data, sort_keys=True, separators=(',', ':'))

def load_enums(file_path):
    """Extracts enums from markdown tables."""
    if not os.path.exists(file_path):
        return set()
    with open(file_path, "r") as f:
        content = f.read()
    return set(re.findall(r"`([A-Z0-9_]+)`", content))

def check_enums(args):
    print(f"[*] Running Enum Consistency Gate...")
    ledger_enums = load_enums(LEDGER_ENUM_FILE)
    court_enums = load_enums(COURT_ENUM_FILE)
    reason_enums = load_enums(REASON_ENUM_FILE)
    
    if not ledger_enums or not court_enums or not reason_enums:
        print(f"[!] Error: Enum files missing or empty.")
        sys.exit(1)

    with open(ROADMAP_FILE, "r") as f:
        content = f.read()
    
    found_strings = set(re.findall(r"\| `([A-Z0-9_]+)`", content))
    drift = [s for s in found_strings if s not in ledger_enums and s not in court_enums and s not in reason_enums and s != "N/A"]
    
    if drift:
        print(f"[X] DRIFT DETECTED: {drift}")
        print(f"[!] Fail-Closed: Enum drift blocks release (ERR_AUDIT_SCHEMA_MISSING)")
        sys.exit(1)
    
    print("[v] Enum Gate: PASS")
    sys.exit(0)

def check_evidence_index(args):
    print(f"[*] Validating Release Gate Evidence Index...")
    with open(ROADMAP_FILE, "r") as f:
        lines = f.readlines()
    
    paths_found = []
    in_appendix_a = False
    for line in lines:
        if "## Appendix A: Evidence Index" in line:
            in_appendix_a = True
        if in_appendix_a and "|" in line:
            match = re.search(r"(aaa-[a-z-]+/[\w/-]+\.py)", line)
            if match:
                paths_found.append(match.group(1))
                
    missing = [p for p in paths_found if not os.path.exists(p)]
    if missing:
        print(f"[X] EVIDENCE MISSING: {missing}")
        sys.exit(1)
        
    print("[v] Evidence Index: PASS")
    sys.exit(0)

def export_evidence(args):
    version = args.version
    base_dir = f"artifacts/evidence_bundle/{version}"
    os.makedirs(base_dir, exist_ok=True)
    
    print(f"[*] Generating Evidence Bundle for {version}...")
    
    # Ensure core files exist
    for cf in CORE_FILES:
        path = os.path.join(base_dir, cf)
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write("{}")

    # Generate hash_chain.txt (Lexical order)
    hash_entries = []
    for f_name in sorted(CORE_FILES):
        f_path = os.path.join(base_dir, f_name)
        with open(f_path, "rb") as f:
            f_hash = hashlib.sha256(f.read()).hexdigest()
        hash_entries.append(f"sha256 {f_name} {f_hash}")
    
    hash_entries.append(f"env_fingerprint {get_env_fingerprint()}")
    
    hc_path = os.path.join(base_dir, "hash_chain.txt")
    with open(hc_path, "w") as f:
        f.write("\n".join(hash_entries) + "\n")
        
    # Zip package (Diamond-Refined: root-only)
    zip_path = os.path.join(base_dir, "bundle.zip")
    with zipfile.ZipFile(zip_path, "w") as bzip:
        for f_name in CORE_FILES + ["hash_chain.txt"]:
            bzip.write(os.path.join(base_dir, f_name), f_name)
            
    print(f"[v] Evidence Bundle Created: {zip_path}")
    sys.exit(0)

def omega_replay(args):
    bundle_path = args.bundle
    print(f"[*] Starting OMEGA Replay for: {bundle_path}")
    
    if not os.path.exists(bundle_path):
        print(f"[!] Error: Bundle not found.")
        sys.exit(3) # BUNDLE_INVALID
        
    tmp_dir = "tmp_replay_extract"
    os.makedirs(tmp_dir, exist_ok=True)
    
    try:
        with zipfile.ZipFile(bundle_path, 'r') as bzip:
            bzip.extractall(tmp_dir)
            
        # 1. Check core files
        for f in CORE_FILES + ["hash_chain.txt"]:
            if not os.path.exists(os.path.join(tmp_dir, f)):
                print(f"[X] Missing core file: {f}")
                sys.exit(3)

        # 2. Hash Chain & Env Check
        with open(os.path.join(tmp_dir, "hash_chain.txt"), "r") as hc_f:
            claimed_lines = [l.strip() for l in hc_f.readlines()]
            
        # Verify files
        for f_name in sorted(CORE_FILES):
            f_path = os.path.join(tmp_dir, f_name)
            with open(f_path, "rb") as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()
            # Find in claimed
            match = [l for l in claimed_lines if f_name in l]
            if not match or actual_hash not in match[0]:
                print(f"[X] Hash mismatch for {f_name}")
                sys.exit(1) # TAMPER SUSPECT

        # Verify Env
        current_env = get_env_fingerprint()
        env_match = [l for l in claimed_lines if "env_fingerprint" in l]
        if not env_match or current_env not in env_match[0]:
            print(f"[!] ENV_DRIFT: Bundle was generated in different environment.")
            print(f"    Claimed: {env_match[0] if env_match else 'None'}")
            print(f"    Current: {current_env}")
            sys.exit(2) # ENV_DRIFT

        print("[v] Replay: Integrity and Env verified.")
        sys.exit(0)
    except Exception as e:
        print(f"[!] Error during replay: {e}")
        sys.exit(3)

def main():
    parser = argparse.ArgumentParser(description="AAA Governance Control Center")
    subparsers = parser.add_subparsers(dest="command")

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--enums", action="store_true")
    check_parser.add_argument("--evidence-index", action="store_true")

    export_parser = subparsers.add_parser("export")
    export_parser.add_argument("--evidence", action="store_true")
    export_parser.add_argument("--version", required=True)

    replay_prog = subparsers.add_parser("omega")
    replay_sub = replay_prog.add_subparsers(dest="subcommand")
    replay_cmd = replay_sub.add_parser("replay")
    replay_cmd.add_argument("--bundle", required=True)

    args = parser.parse_args()

    if args.command == "check":
        if args.enums: check_enums(args)
        elif args.evidence_index: check_evidence_index(args)
    elif args.command == "export":
        export_evidence(args)
    elif args.command == "omega":
        if args.subcommand == "replay": omega_replay(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
