import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional
import re

try:
    import typer
    _HAS_TYPER = True
except Exception:  # pragma: no cover - fallback when typer isn't available
    _HAS_TYPER = False

    class _TyperExit(SystemExit):
        pass

    class _TyperShim:
        Exit = _TyperExit
        @staticmethod
        def Option(default=None, *_args, **_kwargs):
            return default

    typer = _TyperShim()
try:
    from jsonschema import Draft202012Validator
except Exception:  # pragma: no cover - fallback when jsonschema isn't available
    Draft202012Validator = None

from .jsonl import emit_jsonl
from . import verify_ci as verify_ci_module


if _HAS_TYPER:
    init_app = typer.Typer(no_args_is_help=True)
else:
    class _NoOpApp:
        def command(self, *_args, **_kwargs):
            def decorator(func):
                return func

            return decorator
        def callback(self, *_args, **_kwargs):
            def decorator(func):
                return func

            return decorator

    init_app = _NoOpApp()


ERROR_GENERAL = 1
ERROR_INVALID_ARGUMENT = 10
ERROR_PLAN_VALIDATION_FAILED = 11
ERROR_ENV_PRECHECK_FAILED = 12
ERROR_PERMISSION_DENIED = 13
ERROR_ORG_NOT_FOUND = 20
ERROR_REPO_CREATE_FAILED = 21
ERROR_REPO_INACCESSIBLE = 22
ERROR_REPO_CLONE_FAILED = 23
ERROR_GIT_PUSH_FAILED = 24
ERROR_PR_CREATE_FAILED = 25
ERROR_TEMPLATE_SOURCE_NOT_FOUND = 30
ERROR_TEMPLATE_APPLY_FAILED = 31
ERROR_SYNC_WORKFLOWS_FAILED = 32
ERROR_SYNC_SKILLS_FAILED = 33
ERROR_BRANCH_PROTECTION_FAILED = 40
ERROR_REQUIRED_CHECKS_MISMATCH = 41
ERROR_CI_CHECKS_MISSING = 42
ERROR_CI_CHECKS_FAILED = 43
ERROR_REPO_CHECKS_FAILED = 44


REPO_ROOT = Path(__file__).resolve().parents[1]
_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass
class CommandResult:
    code: int
    stdout: str
    stderr: str


def _run_command(cmd: list[str], cwd: Optional[Path] = None, input_data: Optional[str] = None) -> CommandResult:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        input=input_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return CommandResult(code=proc.returncode, stdout=proc.stdout.strip(), stderr=proc.stderr.strip())


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_checks_manifest() -> Optional[dict[str, Any]]:
    manifest_path = Path(
        os.environ.get("AAA_CHECKS_MANIFEST", REPO_ROOT.parent / "aaa-actions" / "checks.manifest.json")
    )
    if manifest_path.is_file():
        return verify_ci_module.load_checks_manifest(manifest_path)
    return None


def _repo_type_from_plan(repo: dict[str, Any]) -> str:
    value = repo.get("repo_type") or repo.get("type") or "all"
    repo_type = str(value).strip()
    return repo_type if repo_type else "all"


def _upsert_repo_type_index(target_dir: Path, repo_type: str) -> None:
    if not repo_type:
        return
    index_path = target_dir / "index.json"
    payload: dict[str, Any] = {}
    if index_path.exists():
        try:
            payload = json.loads(index_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
    if not isinstance(payload, dict):
        payload = {}
    payload["repo_type"] = repo_type
    index_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _schema_error_hint(error: Exception, instance: Any) -> str:
    try:
        if isinstance(instance, list) and "required_checks" in list(error.path):
            missing = sorted({"lint", "test", "eval"} - set(instance))
            if missing:
                return f"required_checks missing: {', '.join(missing)}"
    except Exception:
        return "schema validation failed"
    return "schema validation failed"


def _first_validation_error(validator: Draft202012Validator, instance: dict[str, Any]) -> Optional[dict[str, Any]]:
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    if not errors:
        return None
    error = errors[0]
    json_path = "/".join(str(p) for p in error.absolute_path)
    schema_path = "/".join(str(p) for p in error.absolute_schema_path)
    hint = _schema_error_hint(error, error.instance)
    return {
        "message": error.message,
        "json_path": json_path,
        "schema_path": schema_path,
        "hint": hint,
    }


def _resolve_repo_full_name(org: str, repo_name: str) -> str:
    if "/" in repo_name:
        return repo_name
    return f"{org}/{repo_name}"


def _gh_repo_view(full_name: str) -> Optional[dict[str, Any]]:
    result = _run_command(["gh", "repo", "view", full_name, "--json", "url,defaultBranchRef,visibility"])
    if result.code == 0:
        return json.loads(result.stdout or "{}")
    return None


def _gh_repo_exists(full_name: str) -> bool:
    result = _run_command(["gh", "repo", "view", full_name])
    return result.code == 0


def _copy_tree(src: Path, dest: Path) -> None:
    if not src.exists():
        return
    if src.is_dir():
        shutil.copytree(src, dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git", ".DS_Store"))
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def _clear_worktree(path: Path) -> None:
    for item in path.iterdir():
        if item.name == ".git":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def _plan_from_file(plan_path: Path) -> dict[str, Any]:
    return _load_json(plan_path)


def _fallback_validate_plan(plan: dict[str, Any]) -> Optional[dict[str, Any]]:
    required_top = ["plan_version", "aaa", "target", "repos", "steps", "reporting"]
    for key in required_top:
        if key not in plan:
            return {
                "message": f"missing required field: {key}",
                "json_path": key,
                "schema_path": f"required/{key}",
                "hint": "add required field",
            }
    if plan.get("plan_version") != "0.1":
        return {
            "message": "invalid plan_version",
            "json_path": "plan_version",
            "schema_path": "plan_version",
            "hint": "plan_version must be 0.1",
        }
    target = plan.get("target", {})
    project_slug = target.get("project_slug", "")
    if not project_slug or not _SLUG_RE.match(project_slug):
        return {
            "message": "invalid project_slug",
            "json_path": "target/project_slug",
            "schema_path": "target/project_slug",
            "hint": "project_slug must be kebab-case",
        }
    repos = plan.get("repos", [])
    if not isinstance(repos, list) or not repos:
        return {
            "message": "repos must be a non-empty array",
            "json_path": "repos",
            "schema_path": "repos",
            "hint": "add at least one repo",
        }
    for idx, repo in enumerate(repos):
        checks = repo.get("required_checks", [])
        missing = _missing_required_checks(checks)
        if missing:
            return {
                "message": "required_checks missing required entries",
                "json_path": f"repos/{idx}/required_checks",
                "schema_path": "repos/required_checks",
                "hint": f"required_checks missing: {', '.join(missing)}",
            }
    steps = plan.get("steps", [])
    if not isinstance(steps, list) or not steps:
        return {
            "message": "steps must be a non-empty array",
            "json_path": "steps",
            "schema_path": "steps",
            "hint": "add at least one step",
        }
    return None


def _validate_plan(plan: dict[str, Any], schema_path: Path) -> Optional[dict[str, Any]]:
    if Draft202012Validator is None:
        return _fallback_validate_plan(plan)
    schema = _load_json(schema_path)
    validator = Draft202012Validator(schema)
    return _first_validation_error(validator, plan)


def _emit_error_and_exit(
    jsonl: bool,
    command: str,
    step_id: str,
    code: int,
    message: str,
    data: Optional[dict[str, Any]] = None,
) -> None:
    emit_jsonl(
        jsonl,
        event="error",
        status="error",
        command=command,
        step_id=step_id,
        code=code,
        message=message,
        data=data,
    )
    raise typer.Exit(code)


def _default_branch_from_plan(plan: dict[str, Any]) -> str:
    return plan.get("target", {}).get("default_branch", "main")


def _required_checks_from_plan(repo: dict[str, Any]) -> list[str]:
    checks = repo.get("required_checks") or []
    return [str(check) for check in checks]


def _aaa_version_from_plan(plan: dict[str, Any]) -> str:
    return plan.get("aaa", {}).get("version_tag", "v0.1.0")


def _project_slug_from_plan(plan: dict[str, Any]) -> str:
    return plan.get("target", {}).get("project_slug", "project")


def _missing_required_checks(checks: Iterable[str]) -> list[str]:
    return sorted({"lint", "test", "eval"} - set(checks))


def _write_log(log_dir: Optional[Path], name: str, content: str) -> None:
    if not log_dir:
        return
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / name).write_text(content + "\n", encoding="utf-8")


def _rfc3339_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _tool_version(name: str) -> str:
    if not shutil.which(name):
        return "missing"
    result = _run_command([name, "--version"])
    return result.stdout.splitlines()[0] if result.stdout else "unknown"


def _python_version() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def _require_tool(name: str, jsonl: bool, command: str, step_id: str, dry_run: bool = False) -> bool:
    if dry_run:
        return True
    if shutil.which(name):
        return True
    _emit_error_and_exit(
        jsonl,
        command,
        step_id,
        ERROR_ENV_PRECHECK_FAILED,
        f"{name} not found in PATH",
        {"tool": name},
    )
    return False


class _Cwd:
    def __init__(self, path: Path):
        self.path = path
        self.original = Path.cwd()

    def __enter__(self):
        os.chdir(self.path)
        return self

    def __exit__(self, exc_type, exc, tb):
        os.chdir(self.original)


class _ReportBuilder:
    def __init__(self, plan: dict[str, Any], plan_path: Path, mode: str, workspace_dir: Path, dry_run: bool):
        self.plan = plan
        self.plan_path = plan_path
        self.mode = mode
        self.workspace_dir = workspace_dir
        self.dry_run = dry_run
        self.steps: list[dict[str, Any]] = []
        self.repos: list[dict[str, Any]] = []
        self._init_repos()

    def _init_repos(self) -> None:
        for repo in self.plan.get("repos", []):
            self.repos.append(
                {
                    "name": repo.get("name", ""),
                    "type": repo.get("type", "other"),
                    "status": "exists",
                    "url": "",
                    "default_branch": self.plan.get("target", {}).get("default_branch", "main"),
                    "template_applied": False,
                    "template_source": "",
                    "workflows_synced": False,
                    "skills_synced": False,
                    "pr_url": "",
                    "notes": "",
                }
            )

    def mark_repo(self, repo_name: str, **updates: Any) -> None:
        for repo in self.repos:
            if repo["name"] == repo_name:
                repo.update(updates)
                return

    def add_step(self, step_id: str, status: str, started_at: str, ended_at: str, commands: Optional[list[str]] = None):
        payload = {
            "id": step_id,
            "status": status,
            "started_at": started_at,
            "ended_at": ended_at,
        }
        if commands is not None:
            payload["commands"] = commands
        self.steps.append(payload)

    def build(self, status: str, prs_created: int, next_actions: list[str]) -> dict[str, Any]:
        aaa = self.plan.get("aaa", {})
        target = self.plan.get("target", {})
        required_checks = []
        if self.plan.get("repos"):
            required_checks = _required_checks_from_plan(self.plan["repos"][0])
        branch_applied = status == "pass" and not self.dry_run
        ci_overall = "pass" if status == "pass" and not self.dry_run else "partial"
        report = {
            "metadata": {
                "report_version": "0.1",
                "generated_at": _rfc3339_now(),
                "aaa_org": aaa.get("org", ""),
                "aaa_version_tag": aaa.get("version_tag", ""),
                "target_org": target.get("org", ""),
                "project_slug": target.get("project_slug", ""),
                "mode": self.mode,
                "visibility": target.get("visibility", "private"),
                "default_branch": target.get("default_branch", "main"),
            },
            "inputs": {
                "plan_path": str(self.plan_path),
                "plan_version": self.plan.get("plan_version", ""),
                "tools": {
                    "gh": _tool_version("gh"),
                    "git": _tool_version("git"),
                    "python": _python_version(),
                    "aaa": "aaa-tools 0.1.0",
                },
                "network_access": {
                    "enabled": True,
                    "allowed_endpoints": ["github.com", "api.github.com"],
                    "external_downloads": False,
                    "external_download_sources": [],
                },
            },
            "repos": self.repos,
            "steps": self.steps,
            "branch_protection": {
                "baseline_applied": branch_applied,
                "required_checks": required_checks,
                "settings": {
                    "require_pr_reviews": True,
                    "required_approvals": 1,
                    "require_status_checks": True,
                    "dismiss_stale_approvals": True,
                    "prevent_force_push": True,
                    "require_linear_history": True,
                },
                "per_repo": [
                    {"repo": repo["name"], "applied": branch_applied, "missing_permissions": False, "notes": ""}
                    for repo in self.repos
                ],
            },
            "ci": {
                "required_checks": required_checks,
                "per_repo": [
                    {
                        "repo": repo["name"],
                        "checks": [
                            {"name": check, "status": "skipped", "details_url": ""}
                            for check in required_checks
                        ],
                        "overall": ci_overall,
                    }
                    for repo in self.repos
                ],
            },
            "summary": {
                "status": "partial" if self.dry_run else status,
                "repos_total": len(self.repos),
                "repos_ok": len(self.repos) if status == "pass" and not self.dry_run else 0,
                "prs_created": prs_created,
                "next_actions": next_actions,
            },
        }
        return report


@init_app.command("validate-plan")
def validate_plan(
    plan: Path = typer.Option(..., "--plan", exists=False, readable=False),
    schema: Path = typer.Option(REPO_ROOT / "specs" / "plan.schema.json", "--schema"),
    jsonl: bool = typer.Option(False, "--jsonl"),
    log_dir: Optional[Path] = typer.Option(None, "--log-dir"),
):
    command = "aaa init validate-plan"
    step_id = "validate_plan"
    emit_jsonl(jsonl, event="start", status="start", command=command, step_id=step_id)

    if not plan.exists():
        _emit_error_and_exit(jsonl, command, step_id, ERROR_INVALID_ARGUMENT, "plan not found", {"path": str(plan)})

    if not schema.exists():
        _emit_error_and_exit(jsonl, command, step_id, ERROR_INVALID_ARGUMENT, "schema not found", {"path": str(schema)})

    try:
        plan_data = _plan_from_file(plan)
    except json.JSONDecodeError as exc:
        _emit_error_and_exit(
            jsonl,
            command,
            step_id,
            ERROR_INVALID_ARGUMENT,
            "plan json parse failed",
            {"error": str(exc)},
        )

    try:
        error = _validate_plan(plan_data, schema)
    except Exception as exc:
        _emit_error_and_exit(
            jsonl,
            command,
            step_id,
            ERROR_PLAN_VALIDATION_FAILED,
            "plan validation crashed",
            {"error": str(exc)},
        )

    if error:
        _write_log(log_dir, "stderr.log", error.get("message", "schema validation failed"))
        _emit_error_and_exit(
            jsonl,
            command,
            step_id,
            ERROR_PLAN_VALIDATION_FAILED,
            "plan validation failed",
            error,
        )

    emit_jsonl(
        jsonl,
        event="result",
        status="ok",
        command=command,
        step_id=step_id,
        data={"plan": str(plan), "schema": str(schema)},
    )


@init_app.callback(invoke_without_command=True)
def run_plan(
    plan: Optional[Path] = typer.Option(None, "--plan"),
    mode: str = typer.Option("pr", "--mode"),
    jsonl: bool = typer.Option(False, "--jsonl"),
    log_dir: Optional[Path] = typer.Option(None, "--log-dir"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    if plan is None:
        return
    command = "aaa init"
    step_id = "run_plan"
    emit_jsonl(jsonl, event="start", status="start", command=command, step_id=step_id)

    if not plan.exists():
        _emit_error_and_exit(
            jsonl,
            command,
            step_id,
            ERROR_INVALID_ARGUMENT,
            "plan not found",
            {"path": str(plan)},
        )

    schema_path = REPO_ROOT / "specs" / "plan.schema.json"
    plan_data = _plan_from_file(plan)
    error = _validate_plan(plan_data, schema_path)
    if error:
        _emit_error_and_exit(
            jsonl,
            command,
            step_id,
            ERROR_PLAN_VALIDATION_FAILED,
            "plan validation failed",
            error,
        )

    org = plan_data.get("target", {}).get("org")
    if not org:
        _emit_error_and_exit(
            jsonl,
            command,
            step_id,
            ERROR_INVALID_ARGUMENT,
            "target org missing",
        )

    steps = plan_data.get("steps", [])
    workspace_dir = Path(os.environ.get("WORKSPACE_DIR", Path.cwd()))
    if not workspace_dir.exists():
        _emit_error_and_exit(
            jsonl,
            command,
            step_id,
            ERROR_INVALID_ARGUMENT,
            "WORKSPACE_DIR not found",
            {"path": str(workspace_dir)},
        )

    report_builder = _ReportBuilder(plan_data, plan, mode, workspace_dir, dry_run=dry_run)
    prs_created = 0
    next_actions: list[str] = []

    try:
        for step in steps:
            step_id_value = step.get("id")
            started_at = _rfc3339_now()

            if step_id_value == "preflight":
                _require_tool("gh", jsonl, command, step_id, dry_run=dry_run)
                _require_tool("git", jsonl, command, step_id, dry_run=dry_run)
                emit_jsonl(
                    jsonl,
                    event="result",
                    status="ok" if not dry_run else "noop",
                    command=command,
                    step_id="preflight",
                    data={"status": "checked"},
                )
                report_builder.add_step(
                    "preflight",
                    "pass",
                    started_at,
                    _rfc3339_now(),
                    step.get("commands"),
                )
                continue

            if step_id_value == "ensure_repos":
                ensure_repos(org=org, from_plan=plan, jsonl=jsonl, log_dir=log_dir, dry_run=dry_run)
                report_builder.add_step(
                    "ensure_repos",
                    "pass",
                    started_at,
                    _rfc3339_now(),
                    step.get("commands"),
                )
            elif step_id_value == "apply_templates":
                aaa_tag = _aaa_version_from_plan(plan_data)
                apply_templates(
                    org=org,
                    from_plan=plan,
                    aaa_tag=aaa_tag,
                    jsonl=jsonl,
                    log_dir=log_dir,
                    dry_run=dry_run,
                )
                report_builder.add_step(
                    "apply_templates",
                    "pass",
                    started_at,
                    _rfc3339_now(),
                    step.get("commands"),
                )
            elif step_id_value == "sync_assets":
                if dry_run:
                    emit_jsonl(
                        jsonl,
                        event="result",
                        status="noop",
                        command=command,
                        step_id="sync_assets",
                        data={"status": "dry_run"},
                    )
                else:
                    with _Cwd(workspace_dir):
                        from .cli import sync_skills, sync_workflows

                        sync_skills(target="codex")
                        sync_skills(target="agent")
                        sync_workflows(target="agent")
                    for repo in report_builder.repos:
                        repo["workflows_synced"] = True
                        repo["skills_synced"] = True
                report_builder.add_step(
                    "sync_assets",
                    "pass",
                    started_at,
                    _rfc3339_now(),
                    step.get("commands"),
                )
            elif step_id_value == "branch_protection":
                protect(org=org, from_plan=plan, jsonl=jsonl, log_dir=log_dir, dry_run=dry_run)
                report_builder.add_step(
                    "branch_protection",
                    "pass",
                    started_at,
                    _rfc3339_now(),
                    step.get("commands"),
                )
            elif step_id_value == "open_prs":
                if mode == "pr":
                    open_prs(org=org, from_plan=plan, jsonl=jsonl, log_dir=log_dir, dry_run=dry_run)
                    if not dry_run:
                        prs_created += len(report_builder.repos)
                report_builder.add_step(
                    "open_prs",
                    "pass" if mode == "pr" else "skipped",
                    started_at,
                    _rfc3339_now(),
                    step.get("commands"),
                )
            elif step_id_value == "ci_verify":
                verify_ci(org=org, from_plan=plan, jsonl=jsonl, log_dir=log_dir, dry_run=dry_run)
                report_builder.add_step(
                    "ci_verify",
                    "pass",
                    started_at,
                    _rfc3339_now(),
                    step.get("commands"),
                )
            elif step_id_value == "repo_evals":
                repo_checks(org=org, from_plan=plan, suite="governance", jsonl=jsonl, log_dir=log_dir, dry_run=dry_run)
                report_builder.add_step(
                    "repo_evals",
                    "pass",
                    started_at,
                    _rfc3339_now(),
                    step.get("commands"),
                )
            else:
                report_builder.add_step(
                    step_id_value or "unknown",
                    "skipped",
                    started_at,
                    _rfc3339_now(),
                    step.get("commands"),
                )
    except SystemExit:
        report = report_builder.build("fail", prs_created, next_actions)
        report_path = log_dir / "aaa-init-report.json" if log_dir else workspace_dir / "aaa-init-report.json"
        report_path.write_text(json.dumps(report, ensure_ascii=True, indent=2), encoding="utf-8")
        emit_jsonl(
            jsonl,
            event="result",
            status="error",
            command=command,
            step_id=step_id,
            data={"report_path": str(report_path)},
        )
        raise

    report = report_builder.build("pass", prs_created, next_actions)
    report_path = log_dir / "aaa-init-report.json" if log_dir else workspace_dir / "aaa-init-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=True, indent=2), encoding="utf-8")
    emit_jsonl(
        jsonl,
        event="result",
        status="ok",
        command=command,
        step_id=step_id,
        data={"status": "completed", "report_path": str(report_path)},
    )


@init_app.command("ensure-repos")
def ensure_repos(
    org: str = typer.Option(..., "--org"),
    from_plan: Path = typer.Option(..., "--from-plan"),
    jsonl: bool = typer.Option(False, "--jsonl"),
    log_dir: Optional[Path] = typer.Option(None, "--log-dir"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    command = "aaa init ensure-repos"
    step_id = "ensure_repos"
    emit_jsonl(jsonl, event="start", status="start", command=command, step_id=step_id)

    if not from_plan.exists():
        _emit_error_and_exit(
            jsonl,
            command,
            step_id,
            ERROR_INVALID_ARGUMENT,
            "plan not found",
            {"path": str(from_plan)},
        )

    plan = _plan_from_file(from_plan)
    visibility = plan.get("target", {}).get("visibility", "private")
    repos = plan.get("repos", [])

    for repo in repos:
        repo_name = str(repo.get("name", "")).strip()
        if not repo_name:
            _emit_error_and_exit(
                jsonl,
                command,
                step_id,
                ERROR_INVALID_ARGUMENT,
                "repo name missing in plan",
            )
        full_name = _resolve_repo_full_name(org, repo_name)

        if dry_run:
            emit_jsonl(
                jsonl,
                event="result",
                status="noop",
                command=command,
                step_id=step_id,
                data={"repo": full_name, "status": "would_check"},
            )
            continue

        _require_tool("gh", jsonl, command, step_id, dry_run=False)
        view_result = _run_command(["gh", "repo", "view", full_name, "--json", "url,defaultBranchRef,visibility"])
        if view_result.code == 0:
            data = json.loads(view_result.stdout or "{}")
            emit_jsonl(
                jsonl,
                event="result",
                status="ok",
                command=command,
                step_id=step_id,
                data={
                    "repo": full_name,
                    "status": "exists",
                    "url": data.get("url"),
                    "visibility": data.get("visibility"),
                    "default_branch": (data.get("defaultBranchRef") or {}).get("name"),
                },
            )
            continue

        if "403" in view_result.stderr or "forbidden" in view_result.stderr.lower():
            _emit_error_and_exit(
                jsonl,
                command,
                step_id,
                ERROR_PERMISSION_DENIED,
                "permission denied",
                {"repo": full_name, "details": view_result.stderr},
            )

        create_cmd = [
            "gh",
            "repo",
            "create",
            full_name,
            "--description",
            repo.get("description", ""),
            "--confirm",
        ]
        create_cmd.append("--private" if visibility == "private" else "--public")
        create_result = _run_command(create_cmd)
        if create_result.code != 0:
            _write_log(log_dir, "stderr.log", create_result.stderr)
            _emit_error_and_exit(
                jsonl,
                command,
                step_id,
                ERROR_REPO_CREATE_FAILED,
                "repo create failed",
                {"repo": full_name, "details": create_result.stderr},
            )

        data = _gh_repo_view(full_name) or {}
        emit_jsonl(
            jsonl,
            event="result",
            status="ok",
            command=command,
            step_id=step_id,
            data={
                "repo": full_name,
                "status": "created",
                "url": data.get("url"),
                "visibility": data.get("visibility"),
                "default_branch": (data.get("defaultBranchRef") or {}).get("name"),
            },
        )


@init_app.command("apply-templates")
def apply_templates(
    org: str = typer.Option(..., "--org"),
    from_plan: Path = typer.Option(..., "--from-plan"),
    aaa_tag: str = typer.Option(..., "--aaa-tag"),
    jsonl: bool = typer.Option(False, "--jsonl"),
    log_dir: Optional[Path] = typer.Option(None, "--log-dir"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    command = "aaa init apply-templates"
    step_id = "apply_templates"
    emit_jsonl(jsonl, event="start", status="start", command=command, step_id=step_id)

    if not from_plan.exists():
        _emit_error_and_exit(
            jsonl,
            command,
            step_id,
            ERROR_INVALID_ARGUMENT,
            "plan not found",
            {"path": str(from_plan)},
        )

    plan = _plan_from_file(from_plan)
    aaa_org = plan.get("aaa", {}).get("org", "ai-asset-architecture")
    project_slug = plan.get("target", {}).get("project_slug", "project")
    repos = plan.get("repos", [])
    temp_root = REPO_ROOT / ".aaa-tmp"
    temp_root.mkdir(parents=True, exist_ok=True)

    for repo in repos:
        repo_name = str(repo.get("name", "")).strip()
        template = str(repo.get("template", "")).strip()
        if not repo_name or not template:
            _emit_error_and_exit(
                jsonl,
                command,
                step_id,
                ERROR_INVALID_ARGUMENT,
                "repo name or template missing in plan",
            )
        full_name = _resolve_repo_full_name(org, repo_name)
        template_full = f"{aaa_org}/{template}"
        template_dir = temp_root / f"template-{template}"
        target_dir = temp_root / f"target-{repo_name}"

        if template_dir.exists():
            shutil.rmtree(template_dir)
        if target_dir.exists():
            shutil.rmtree(target_dir)

        if dry_run:
            emit_jsonl(
                jsonl,
                event="result",
                status="noop",
                command=command,
                step_id=step_id,
                data={"repo": full_name, "status": "would_apply", "template_source": f"{template_full}@{aaa_tag}"},
            )
            continue

        _require_tool("git", jsonl, command, step_id, dry_run=False)
        _require_tool("gh", jsonl, command, step_id, dry_run=False)
        template_clone = _run_command(
            ["git", "clone", "--depth", "1", "--branch", aaa_tag, f"https://github.com/{template_full}.git", str(template_dir)]
        )
        if template_clone.code != 0:
            _write_log(log_dir, "stderr.log", template_clone.stderr)
            _emit_error_and_exit(
                jsonl,
                command,
                step_id,
                ERROR_TEMPLATE_SOURCE_NOT_FOUND,
                "template clone failed",
                {"template": template_full, "details": template_clone.stderr},
            )

        target_clone = _run_command(["gh", "repo", "clone", full_name, str(target_dir)])
        if target_clone.code != 0:
            _write_log(log_dir, "stderr.log", target_clone.stderr)
            _emit_error_and_exit(
                jsonl,
                command,
                step_id,
                ERROR_REPO_CLONE_FAILED,
                "repo clone failed",
                {"repo": full_name, "details": target_clone.stderr},
            )

        branch_name = f"bootstrap/{project_slug}/{aaa_tag}"
        _run_command(["git", "checkout", "-b", branch_name], cwd=target_dir)
        _clear_worktree(target_dir)
        for item in template_dir.iterdir():
            if item.name == ".git":
                continue
            _copy_tree(item, target_dir / item.name)
        _upsert_repo_type_index(target_dir, _repo_type_from_plan(repo))

        status_result = _run_command(["git", "status", "--porcelain"], cwd=target_dir)
        if not status_result.stdout.strip():
            commit_result = _run_command(
                [
                    "git",
                    "commit",
                    "--allow-empty",
                    "-m",
                    f"chore: apply aaa template {template}@{aaa_tag} (noop)",
                ],
                cwd=target_dir,
            )
            if commit_result.code != 0:
                _write_log(log_dir, "stderr.log", commit_result.stderr)
                _emit_error_and_exit(
                    jsonl,
                    command,
                    step_id,
                    ERROR_TEMPLATE_APPLY_FAILED,
                    "template apply failed",
                    {"repo": full_name, "details": commit_result.stderr},
                )

            push_result = _run_command(["git", "push", "-u", "origin", branch_name], cwd=target_dir)
            if push_result.code != 0:
                _write_log(log_dir, "stderr.log", push_result.stderr)
                _emit_error_and_exit(
                    jsonl,
                    command,
                    step_id,
                    ERROR_GIT_PUSH_FAILED,
                    "git push failed",
                    {"repo": full_name, "details": push_result.stderr},
                )

            emit_jsonl(
                jsonl,
                event="result",
                status="ok",
                command=command,
                step_id=step_id,
                data={
                    "repo": full_name,
                    "branch": branch_name,
                    "template_source": f"{template_full}@{aaa_tag}",
                    "status": "noop",
                    "forced": True,
                },
            )
            continue

        _run_command(["git", "add", "."], cwd=target_dir)
        commit_result = _run_command(
            ["git", "commit", "-m", f"chore: apply aaa template {template}@{aaa_tag}"], cwd=target_dir
        )
        if commit_result.code != 0:
            _write_log(log_dir, "stderr.log", commit_result.stderr)
            _emit_error_and_exit(
                jsonl,
                command,
                step_id,
                ERROR_TEMPLATE_APPLY_FAILED,
                "template apply failed",
                {"repo": full_name, "details": commit_result.stderr},
            )

        push_result = _run_command(["git", "push", "-u", "origin", branch_name], cwd=target_dir)
        if push_result.code != 0:
            _write_log(log_dir, "stderr.log", push_result.stderr)
            _emit_error_and_exit(
                jsonl,
                command,
                step_id,
                ERROR_GIT_PUSH_FAILED,
                "git push failed",
                {"repo": full_name, "details": push_result.stderr},
            )

        emit_jsonl(
            jsonl,
            event="result",
            status="ok",
            command=command,
            step_id=step_id,
            data={
                "repo": full_name,
                "branch": branch_name,
                "template_source": f"{template_full}@{aaa_tag}",
            },
        )


@init_app.command("protect")
def protect(
    org: str = typer.Option(..., "--org"),
    from_plan: Path = typer.Option(..., "--from-plan"),
    jsonl: bool = typer.Option(False, "--jsonl"),
    log_dir: Optional[Path] = typer.Option(None, "--log-dir"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    command = "aaa init protect"
    step_id = "branch_protection"
    emit_jsonl(jsonl, event="start", status="start", command=command, step_id=step_id)

    if not from_plan.exists():
        _emit_error_and_exit(
            jsonl,
            command,
            step_id,
            ERROR_INVALID_ARGUMENT,
            "plan not found",
            {"path": str(from_plan)},
        )

    plan = _plan_from_file(from_plan)
    default_branch = _default_branch_from_plan(plan)
    repos = plan.get("repos", [])
    manifest = _load_checks_manifest()

    for repo in repos:
        repo_name = str(repo.get("name", "")).strip()
        if not repo_name:
            _emit_error_and_exit(
                jsonl,
                command,
                step_id,
                ERROR_INVALID_ARGUMENT,
                "repo name missing in plan",
            )
        full_name = _resolve_repo_full_name(org, repo_name)
        repo_type = _repo_type_from_plan(repo)
        if manifest:
            checks = [
                item["name"]
                for item in manifest.get("checks", [])
                if "all" in set(item.get("applies_to", [])) or repo_type in set(item.get("applies_to", []))
            ]
        else:
            checks = _required_checks_from_plan(repo)
            missing = _missing_required_checks(checks)
            if missing:
                _emit_error_and_exit(
                    jsonl,
                    command,
                    step_id,
                    ERROR_REQUIRED_CHECKS_MISMATCH,
                    "required checks mismatch",
                    {"repo": full_name, "missing": missing},
                )
        settings = {
            "required_status_checks": {"strict": True, "contexts": checks},
            "enforce_admins": {"enabled": True},
            "required_pull_request_reviews": {"required_approving_review_count": 1},
            "restrictions": None,
            "required_linear_history": {"enabled": True},
            "allow_force_pushes": {"enabled": False},
            "allow_deletions": {"enabled": False},
        }

        if dry_run:
            emit_jsonl(
                jsonl,
                event="result",
                status="noop",
                command=command,
                step_id=step_id,
                data={"repo": full_name, "status": "would_apply", "required_checks": checks},
            )
            continue

        _require_tool("gh", jsonl, command, step_id, dry_run=False)
        api_result = _run_command(
            [
                "gh",
                "api",
                f"repos/{full_name}/branches/{default_branch}/protection",
                "--method",
                "PUT",
                "--input",
                "-",
            ],
            input_data=json.dumps(settings),
        )
        if api_result.code != 0:
            _write_log(log_dir, "stderr.log", api_result.stderr)
            _emit_error_and_exit(
                jsonl,
                command,
                step_id,
                ERROR_BRANCH_PROTECTION_FAILED,
                "branch protection apply failed",
                {"repo": full_name, "details": api_result.stderr},
            )

        emit_jsonl(
            jsonl,
            event="result",
            status="ok",
            command=command,
            step_id=step_id,
            data={"repo": full_name, "required_checks": checks, "status": "applied"},
        )


@init_app.command("verify-ci")
def verify_ci(
    org: str = typer.Option(..., "--org"),
    from_plan: Path = typer.Option(..., "--from-plan"),
    jsonl: bool = typer.Option(False, "--jsonl"),
    log_dir: Optional[Path] = typer.Option(None, "--log-dir"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    command = "aaa init verify-ci"
    step_id = "ci_verify"
    emit_jsonl(jsonl, event="start", status="start", command=command, step_id=step_id)

    if not from_plan.exists():
        _emit_error_and_exit(
            jsonl,
            command,
            step_id,
            ERROR_INVALID_ARGUMENT,
            "plan not found",
            {"path": str(from_plan)},
        )

    plan = _plan_from_file(from_plan)
    default_branch = _default_branch_from_plan(plan)
    repos = plan.get("repos", [])
    manifest = _load_checks_manifest()

    if dry_run:
        emit_jsonl(
            jsonl,
            event="result",
            status="noop",
            command=command,
            step_id=step_id,
            data={"status": "dry_run"},
        )
        return

    for repo in repos:
        repo_name = str(repo.get("name", "")).strip()
        if not repo_name:
            _emit_error_and_exit(
                jsonl,
                command,
                step_id,
                ERROR_INVALID_ARGUMENT,
                "repo name missing in plan",
            )
        full_name = _resolve_repo_full_name(org, repo_name)
        repo_type = _repo_type_from_plan(repo)
        if manifest:
            checks = [
                item["name"]
                for item in manifest.get("checks", [])
                if "all" in set(item.get("applies_to", [])) or repo_type in set(item.get("applies_to", []))
            ]
        else:
            checks = _required_checks_from_plan(repo)
            missing = _missing_required_checks(checks)
            if missing:
                _emit_error_and_exit(
                    jsonl,
                    command,
                    step_id,
                    ERROR_REQUIRED_CHECKS_MISMATCH,
                    "required checks mismatch",
                    {"repo": full_name, "missing": missing},
                )

        _require_tool("gh", jsonl, command, step_id, dry_run=False)
        api_result = _run_command(["gh", "api", f"repos/{full_name}/commits/{default_branch}/check-runs"])
        if api_result.code != 0:
            _write_log(log_dir, "stderr.log", api_result.stderr)
            _emit_error_and_exit(
                jsonl,
                command,
                step_id,
                ERROR_CI_CHECKS_MISSING,
                "failed to fetch check runs",
                {"repo": full_name, "details": api_result.stderr},
            )

        payload = json.loads(api_result.stdout or "{}")
        check_runs = payload.get("check_runs", [])
        status_map = {check.get("name"): check.get("conclusion") for check in check_runs}
        missing = [name for name in checks if name not in status_map]
        failed = [name for name in checks if status_map.get(name) not in {"success", "neutral"}]

        if missing:
            _emit_error_and_exit(
                jsonl,
                command,
                step_id,
                ERROR_CI_CHECKS_MISSING,
                "required checks missing",
                {"repo": full_name, "missing": missing},
            )

        if failed:
            _emit_error_and_exit(
                jsonl,
                command,
                step_id,
                ERROR_CI_CHECKS_FAILED,
                "required checks failed",
                {"repo": full_name, "failed": failed},
            )

        emit_jsonl(
            jsonl,
            event="result",
            status="ok",
            command=command,
            step_id=step_id,
            data={"repo": full_name, "checks": checks, "status": "pass"},
        )


@init_app.command("open-prs")
def open_prs(
    org: str = typer.Option(..., "--org"),
    from_plan: Path = typer.Option(..., "--from-plan"),
    jsonl: bool = typer.Option(False, "--jsonl"),
    log_dir: Optional[Path] = typer.Option(None, "--log-dir"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    command = "aaa init open-prs"
    step_id = "open_prs"
    emit_jsonl(jsonl, event="start", status="start", command=command, step_id=step_id)

    if not from_plan.exists():
        _emit_error_and_exit(
            jsonl,
            command,
            step_id,
            ERROR_INVALID_ARGUMENT,
            "plan not found",
            {"path": str(from_plan)},
        )

    plan = _plan_from_file(from_plan)
    default_branch = _default_branch_from_plan(plan)
    aaa_tag = _aaa_version_from_plan(plan)
    project_slug = _project_slug_from_plan(plan)
    repos = plan.get("repos", [])

    for repo in repos:
        repo_name = str(repo.get("name", "")).strip()
        if not repo_name:
            _emit_error_and_exit(
                jsonl,
                command,
                step_id,
                ERROR_INVALID_ARGUMENT,
                "repo name missing in plan",
            )
        full_name = _resolve_repo_full_name(org, repo_name)
        branch_name = f"bootstrap/{project_slug}/{aaa_tag}"
        head = f"{org}:{branch_name}"

        if dry_run:
            emit_jsonl(
                jsonl,
                event="result",
                status="noop",
                command=command,
                step_id=step_id,
                data={"repo": full_name, "status": "would_create", "head": branch_name},
            )
            continue

        _require_tool("gh", jsonl, command, step_id, dry_run=False)
        list_result = _run_command(
            ["gh", "api", f"repos/{full_name}/pulls", "--field", "state=open", "--field", f"head={head}"]
        )
        if list_result.code == 0 and list_result.stdout:
            existing = json.loads(list_result.stdout)
            if existing:
                pr_url = existing[0].get("html_url") or existing[0].get("url")
                emit_jsonl(
                    jsonl,
                    event="result",
                    status="noop",
                    command=command,
                    step_id=step_id,
                    data={"repo": full_name, "pr_url": pr_url, "status": "exists"},
                )
                continue

        pr_create = _run_command(
            [
                "gh",
                "pr",
                "create",
                "--repo",
                full_name,
                "--title",
                f"chore: apply aaa templates ({aaa_tag})",
                "--body",
                "Automated bootstrap update from aaa templates.",
                "--base",
                default_branch,
                "--head",
                branch_name,
            ]
        )
        if pr_create.code != 0:
            _write_log(log_dir, "stderr.log", pr_create.stderr)
            _emit_error_and_exit(
                jsonl,
                command,
                step_id,
                ERROR_PR_CREATE_FAILED,
                "pr create failed",
                {"repo": full_name, "details": pr_create.stderr},
            )

        pr_url = pr_create.stdout.strip()
        emit_jsonl(
            jsonl,
            event="result",
            status="ok",
            command=command,
            step_id=step_id,
            data={"repo": full_name, "pr_url": pr_url, "status": "created"},
        )


@init_app.command("repo-checks")
def repo_checks(
    org: str = typer.Option(..., "--org"),
    from_plan: Path = typer.Option(..., "--from-plan"),
    suite: str = typer.Option(..., "--suite"),
    jsonl: bool = typer.Option(False, "--jsonl"),
    log_dir: Optional[Path] = typer.Option(None, "--log-dir"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    command = "aaa init repo-checks"
    step_id = "repo_evals"
    emit_jsonl(jsonl, event="start", status="start", command=command, step_id=step_id)

    if not from_plan.exists():
        _emit_error_and_exit(
            jsonl,
            command,
            step_id,
            ERROR_INVALID_ARGUMENT,
            "plan not found",
            {"path": str(from_plan)},
        )

    if suite != "governance":
        _emit_error_and_exit(
            jsonl,
            command,
            step_id,
            ERROR_INVALID_ARGUMENT,
            "unsupported suite",
            {"suite": suite},
        )

    plan = _plan_from_file(from_plan)
    repos = plan.get("repos", [])
    workspace_dir = Path(os.environ.get("WORKSPACE_DIR", Path.cwd()))
    evals_root = Path(os.environ.get("AAA_EVALS_ROOT", REPO_ROOT.parent / "aaa-evals"))
    runner = evals_root / "runner" / "run_repo_checks.py"

    if not runner.exists():
        _emit_error_and_exit(
            jsonl,
            command,
            step_id,
            ERROR_REPO_CHECKS_FAILED,
            "runner not found",
            {"path": str(runner)},
        )

    checks = ["readme", "workflow", "skills", "prompt"]
    failed = []

    for repo in repos:
        repo_name = str(repo.get("name", "")).strip()
        if not repo_name:
            _emit_error_and_exit(
                jsonl,
                command,
                step_id,
                ERROR_INVALID_ARGUMENT,
                "repo name missing in plan",
            )
        repo_dir_name = repo_name.split("/")[-1]
        repo_path = workspace_dir / repo_dir_name
        if dry_run:
            emit_jsonl(
                jsonl,
                event="result",
                status="noop",
                command=command,
                step_id=step_id,
                data={"repo": repo_name, "status": "dry_run"},
            )
            continue

        if not repo_path.exists():
            failed.append({"repo": repo_name, "check": "repo_path", "message": "repo path missing"})
            continue

        repo_results = []
        for check in checks:
            run_result = _run_command(
                ["python3", str(runner), "--check", check, "--repo", str(repo_path)]
            )
            try:
                payload = json.loads(run_result.stdout) if run_result.stdout else {}
            except json.JSONDecodeError:
                payload = {"pass": False, "details": [run_result.stderr or "invalid output"]}

            repo_results.append(
                {"id": check, "status": "pass" if payload.get("pass") else "fail", "message": payload.get("details")}
            )
            if not payload.get("pass"):
                failed.append({"repo": repo_name, "check": check, "message": payload.get("details")})

        emit_jsonl(
            jsonl,
            event="result",
            status="ok",
            command=command,
            step_id=step_id,
            data={"repo": repo_name, "suite": suite, "checks": repo_results},
        )

    if failed:
        _write_log(log_dir, "stderr.log", json.dumps(failed))
        _emit_error_and_exit(
            jsonl,
            command,
            step_id,
            ERROR_REPO_CHECKS_FAILED,
            "repo checks failed",
            {"failures": failed},
        )
