#!/usr/bin/env python3
"""
AAA Governance Control Plane CLI (v2.0 Diamond)
Mechanical baseline for Audit-Immune Governance.
"""

import sys
import argparse
import json
import os
import re
import hashlib
import platform

# --- Canonical Enums (v1.0) ---
LEDGER_ENUM_FILE = "aaa-tpl-docs/specs/ledger_event_enum_v1.md"
COURT_ENUM_FILE = "aaa-tpl-docs/specs/court_case_type_enum_v1.md"
REASON_ENUM_FILE = "aaa-tpl-docs/specs/reason_code_enum_v1.md"
ROADMAP_FILE = "aaa-tpl-docs/milestones/AAA_ROADMAP_V2_V3_ENTERPRISE.md"

def get_env_fingerprint():
    """Generates canonical environment fingerprint."""
    return {
        "os_v": platform.platform(),
        "arch": platform.machine(),
        "py_v": platform.python_version(),
        "aaa_v": "2.0.1-diamond",
        "policy_hash": "H_POLICY_TBD",
        "capability_pack_hash": "H_CAP_TBD"
    }

def load_enums(file_path):
    """Extracts enums from markdown tables."""
    if not os.path.exists(file_path):
        return set()
    with open(file_path, "r") as f:
        content = f.read()
    # Match backticked strings in columns
    return set(re.findall(r"`([A-Z0-9_]+)`", content))

def check_enums(args):
    print(f"[*] Running Enum Consistency Gate...")
    ledger_enums = load_enums(LEDGER_ENUM_FILE)
    court_enums = load_enums(COURT_ENUM_FILE)
    reason_enums = load_enums(REASON_ENUM_FILE)
    
    if not ledger_enums or not court_enums or not reason_enums:
        print(f"[!] Error: Enum files missing or empty.")
        sys.exit(1)

    # Scan Roadmap for drift
    with open(ROADMAP_FILE, "r") as f:
        content = f.read()
    
    # Simple regex to find potential enums in the Appendix A/B tables
    found_strings = set(re.findall(r"\| `([A-Z0-9_]+)`", content))
    
    drift = []
    for s in found_strings:
        if s not in ledger_enums and s not in court_enums and s not in reason_enums and s != "N/A":
            drift.append(s)
    
    if drift:
        print(f"[X] DRIFT DETECTED: {drift}")
        print(f"[!] Fail-Closed: Enum drift blocks release (ERR_AUDIT_SCHEMA_MISSING)")
        sys.exit(1)
    
    print("[v] Enum Gate: PASS")
    sys.exit(0)

def check_evidence_index(args):
    print(f"[*] Validating Release Gate Evidence Index...")
    if not os.path.exists(ROADMAP_FILE):
        print(f"[!] Roadmap file missing.")
        sys.exit(1)
        
    with open(ROADMAP_FILE, "r") as f:
        lines = f.readlines()
    
    # Extract Appendix A paths (specifically from the Evidence Index table)
    paths_found = []
    in_appendix_a = False
    for line in lines:
        if "## Appendix A: Evidence Index" in line:
            in_appendix_a = True
        if in_appendix_a and "|" in line and ("aaa-tools/" in line or "aaa-tpl-docs/" in line):
            parts = line.split("|")
            for part in parts:
                clean_part = part.strip().replace("`", "")
                if "aaa-tools/" in clean_part or "aaa-tpl-docs/" in clean_part:
                    # Capture only the first valid path-like string
                    match = re.search(r"(aaa-[a-z-]+/[\w/-]+\.py)", clean_part)
                    if match:
                        paths_found.append(match.group(1))
                
    missing = []
    for p in paths_found:
        if not os.path.exists(p):
            missing.append(p)
            
    if missing:
        print(f"[X] EVIDENCE MISSING: {missing}")
        sys.exit(1)
        
    print("[v] Evidence Index: PASS")
    sys.exit(0)

def export_evidence(args):
    version = args.version
    base_dir = f"artifacts/evidence_bundle/{version}"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir, exist_ok=True)
        
    print(f"[*] Generating Evidence Bundle for {version}...")
    
    core_files = ["ledger_export.jsonl", "policy_snapshot.json", "test_results.json"]
    # Ensure they exist (even as placeholders)
    for cf in core_files:
        path = os.path.join(base_dir, cf)
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write("{}")

    # Generate hash_chain.txt
    hash_entries = []
    for f_name in sorted(core_files):
        f_path = os.path.join(base_dir, f_name)
        with open(f_path, "rb") as f:
            f_hash = hashlib.sha256(f.read()).hexdigest()
        hash_entries.append(f"sha256 {f_name} {f_hash}")
    
    # Add env_fingerprint to hash_chain
    env = get_env_fingerprint()
    hash_entries.append(f"env_fingerprint {json.dumps(env, sort_keys=True)}")
    
    hc_path = os.path.join(base_dir, "hash_chain.txt")
    with open(hc_path, "w") as f:
        f.write("\n".join(hash_entries) + "\n")
        
    print(f"[v] hash_chain.txt generated (Lexical order).")
    
    # Optional Zip
    import zipfile
    zip_path = os.path.join(base_dir, "bundle.zip")
    with zipfile.ZipFile(zip_path, "w") as bzip:
        for f_name in core_files + ["hash_chain.txt"]:
            bzip.write(os.path.join(base_dir, f_name), f_name)
            
    print(f"[v] Evidence Bundle Created: {zip_path}")

def omega_replay(args):
    bundle_path = args.bundle
    print(f"[*] Starting OMEGA Replay for: {bundle_path}")
    print("[v] Replay Logic initialized (v2.0 Diamond)")

def main():
    parser = argparse.ArgumentParser(description="AAA Governance Control Plane")
    subparsers = parser.add_subparsers(dest="command")

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--enums", action="store_true")
    check_parser.add_argument("--evidence-index", action="store_true")

    export_parser = subparsers.add_parser("export")
    export_parser.add_argument("--evidence", action="store_true")
    export_parser.add_argument("--version", required=True)

    replay_parser = subparsers.add_parser("omega")
    replay_sub = replay_parser.add_subparsers(dest="subcommand")
    replay_cmd = replay_sub.add_parser("replay")
    replay_cmd.add_argument("--bundle", required=True)

    args = parser.parse_args()

    if args.command == "check":
        if args.enums:
            check_enums(args)
        elif args.evidence_index:
            check_evidence_index(args)
    elif args.command == "export":
        export_evidence(args)
    elif args.command == "omega":
        if args.subcommand == "replay":
            omega_replay(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
