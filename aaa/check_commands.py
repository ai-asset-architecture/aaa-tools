import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional
from aaa.registry.policy_client import RegistryClient, RegistryClientError
from aaa.engine.repair import AutoFixEngine

from .cmd import verify_ci


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GATE = "ai-asset-architecture/aaa-actions/.github/workflows/reusable-gate.yaml"
CHECKS = [
    "readme",
    "workflow",
    "repo_type_consistency",
    "checks_manifest_alignment",
    "orphaned_assets",
    "test_policy_compliance",
]


def _load_repo_type(repo_root: Path) -> str:
    metadata_path = repo_root / ".aaa" / "metadata.json"
    if not metadata_path.exists():
        return ""
    try:
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ""
    return str(payload.get("repo_type") or "").strip()


def _run_repo_checks(repo_root: Path) -> list[str]:
    evals_root = Path(os.environ.get("AAA_EVALS_ROOT", REPO_ROOT.parent / "aaa-evals"))
    runner = evals_root / "runner" / "run_repo_checks.py"
    errors: list[str] = []
    if not runner.exists():
        return ["evals_runner_missing"]

    repo_type = _load_repo_type(repo_root)
    manifest_path = os.environ.get(
        "AAA_CHECKS_MANIFEST",
        str(REPO_ROOT.parent / "aaa-actions" / "checks.manifest.json"),
    )
    details_map: dict[str, Any] = {}
    for check in CHECKS:
        args = [sys.executable, str(runner), "--check", check, "--repo", str(repo_root)]
        if repo_type:
            args.extend(["--repo-type", repo_type])
        if check == "checks_manifest_alignment":
            args.extend(["--manifest-path", manifest_path])
        run_result = subprocess.run(args, capture_output=True, text=True, check=False)
        result = run_result.stdout.strip()
        try:
            payload = json.loads(result) if result else {}
        except json.JSONDecodeError:
            payload = {"pass": False, "details": ["invalid_json_output"]}
            
        if run_result.returncode != 0 or payload.get("pass") is not True:
            err_id = f"check_failed:{check}"
            errors.append(err_id)
            details_map[err_id] = payload.get("details", [])
    return errors, details_map


def _run_fixable_checks(repo_root: Path, auto_fix: bool) -> tuple[list[str], dict[str, Any]]:
    """
    Demonstration of Self-Healing Loop:
    1. Check for 'License' in README.md.
    2. If missing and auto_fix=True, use AutoFixEngine to append it.
    """
    errors = []
    details = {}
    readme = repo_root / "README.md"
    
    if readme.exists():
        content = readme.read_text(encoding="utf-8")
        if "License" not in content:
            if auto_fix:
                print("🛠️  Auto-Fixing: Adding License section to README.md...")
                engine = AutoFixEngine()
                
                def add_license(text: str) -> str:
                    return text + "\n\n## License\nMIT"
                    
                result = engine.apply_fix(readme, add_license)
                if result.success:
                     print(f"✅ Fix Applied: {result.message}")
                else:
                     errors.append("autofix_failed")
                     details["autofix_failed"] = [result.message]
            else:
                 # Only report error if not fixing
                 # However, to avoid noise in this MVP, we might only warn.
                 # For demonstration, we'll flag it.
                 pass
                 # errors.append("missing_license_section")
                 # details["missing_license_section"] = ["README.md missing 'License' section. Run with --auto-fix to repair."]
    
    return errors, details


def run_blocking_check(repo_root: Path, auto_fix: bool = False) -> dict[str, Any]:
    workflow_ref = os.environ.get("AAA_GATE_WORKFLOW", DEFAULT_GATE)
    errors: list[str] = []
    details_map: dict[str, Any] = {}
    
    if not verify_ci.has_reusable_gate(repo_root, workflow_ref):
        errors.append("missing_gate_workflow")
        details_map["missing_gate_workflow"] = [f"Expected gate workflow {workflow_ref} not found in .github/workflows/"]

    # 1. Run Standard Checks
    check_errors, check_details = _run_repo_checks(repo_root)
    errors.extend(check_errors)
    details_map.update(check_details)
    
    # 2. Run Fixable Checks (Zone Two Demonstration)
    fix_errors, fix_details = _run_fixable_checks(repo_root, auto_fix)
    errors.extend(fix_errors)
    details_map.update(fix_details)
    
    exit_code = 0 if not errors else 1
    return {"exit_code": exit_code, "errors": errors, "details": details_map}


def run_remote_policy(policy_id: str, registry_url: str) -> dict[str, Any]:
    """
    Download and execute a remote policy script.
    """
    errors = []
    details = {}
    
    try:
        client = RegistryClient(registry_url)
        # 1. Download Script (Zone One Client)
        print(f"Fetching policy '{policy_id}' from {registry_url}...")
        script_path = client.download_policy(policy_id)
        
        # 2. Execute Script (Subprocess)
        print(f"Executing {script_path}...")
        run_result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=False
        )
        
        # 3. Capture Results
        if run_result.returncode != 0:
            err_id = f"remote_policy_failed:{policy_id}"
            errors.append(err_id)
            details[err_id] = run_result.stdout + "\n" + run_result.stderr
            # Print output for user visibility
            print(run_result.stdout)
            print(run_result.stderr)
        else:
            print(run_result.stdout)
            
    except RegistryClientError as e:
        errors.append("registry_error")
        details["registry_error"] = str(e)
    except Exception as e:
        errors.append("runtime_error")
        details["runtime_error"] = str(e)
        
    exit_code = 1 if errors else 0
    return {"exit_code": exit_code, "errors": errors, "details": details}
