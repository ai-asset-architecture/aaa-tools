import json
import os
import subprocess
from datetime import datetime


def run_check(python, runner, args):
    cmd = [python, runner] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout.strip()
    if not output:
        return {
            "pass": False,
            "details": ["no output"],
            "raw": result.stdout + result.stderr,
        }
    try:
        payload = json.loads(output.splitlines()[-1])
    except json.JSONDecodeError:
        return {
            "pass": False,
            "details": ["invalid JSON output"],
            "raw": output,
        }
    return payload


def main():
    workspace = os.environ.get("AAA_WORKSPACE", os.getcwd())
    evals_root = os.environ.get("EVALS_ROOT", os.path.join(workspace, "aaa-evals"))
    docs_root = os.environ.get("DOCS_ROOT", os.path.join(workspace, "aaa-tpl-docs"))

    runner = os.path.join(evals_root, "runner", "run_repo_checks.py")
    python = os.environ.get("PYTHON", "python3")

    repos = [
        (".github", os.path.join(workspace, ".github")),
        ("aaa-actions", os.path.join(workspace, "aaa-actions")),
        ("aaa-tools", os.path.join(workspace, "aaa-tools")),
        ("aaa-prompts", os.path.join(workspace, "aaa-prompts")),
        ("aaa-evals", os.path.join(workspace, "aaa-evals")),
        ("aaa-tpl-docs", os.path.join(workspace, "aaa-tpl-docs")),
        ("aaa-tpl-service", os.path.join(workspace, "aaa-tpl-service")),
        ("aaa-tpl-frontend", os.path.join(workspace, "aaa-tpl-frontend")),
        ("aaa-observability", os.path.join(workspace, "aaa-observability")),
    ]

    checks = []
    for name, path in repos:
        checks.append({"repo": name, "check": "readme", "args": ["--check", "readme", "--repo", path]})
        checks.append({"repo": name, "check": "workflow", "args": ["--check", "workflow", "--repo", path]})

    checks.append({
        "repo": "aaa-tools",
        "check": "skills",
        "args": ["--check", "skills", "--repo", os.path.join(workspace, "aaa-tools"), "--skills-root", "skills"],
    })
    checks.append({
        "repo": "aaa-prompts",
        "check": "prompt",
        "args": [
            "--check", "prompt",
            "--repo", os.path.join(workspace, "aaa-prompts"),
            "--schema-path", "prompt.schema.json",
            "--prompts-dir", "prompts",
        ],
    })

    results = []
    failed = False
    for check in checks:
        payload = run_check(python, runner, check["args"])
        results.append(payload)
        if not payload.get("pass", False):
            failed = True

    os.makedirs(os.path.join(docs_root, "reports"), exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    report_path = os.path.join(docs_root, "reports", f"governance_evals_report_{stamp}.md")

    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(f"# Governance Evals Report ({stamp})\n\n")
        handle.write("## Summary\n")
        handle.write("All governance eval checks passed.\n\n" if not failed else "Some governance eval checks failed.\n\n")
        handle.write("## Results\n")
        for payload in results:
            repo = payload.get("repo", "unknown")
            check = payload.get("check", "unknown")
            status = "PASS" if payload.get("pass") else "FAIL"
            details = payload.get("details", [])
            if details:
                handle.write(f"- `{repo}` {check}: {status} ({', '.join(details)})\n")
            else:
                handle.write(f"- `{repo}` {check}: {status}\n")

    print(report_path)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
