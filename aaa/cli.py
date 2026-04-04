import argparse
import json
import shutil
import sys
from importlib import metadata
from pathlib import Path
from typing import Optional

try:
    import typer
except Exception:  # pragma: no cover - fallback when typer isn't available
    typer = None

from . import check_commands
from . import output_formatter
from . import audit_commands
from . import init_commands
from . import pack_commands
from . import package_commands
from . import bootstrap_commands
from . import governance_commands
from . import runbook_registry
from . import runbook_runtime
from .utils import version_check
from . import outdated as outdated_commands
from . import outdated as outdated_commands
from .action_registry import RuntimeSecurityError
from .cmd import registry_commands

if typer:
    app = typer.Typer(no_args_is_help=True)
    sync_app = typer.Typer(no_args_is_help=True)
else:
    app = None
    sync_app = None

REPO_ROOT = Path(__file__).resolve().parents[1]


def _copy_tree(src: Path, dest: Path):
    if not src.exists():
        return
    if src.is_dir():
        shutil.copytree(src, dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".DS_Store"))
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def _sync_sources(sources, dest_root: Path):
    dest_root.mkdir(parents=True, exist_ok=True)
    for source in sources:
        if not source.exists():
            continue
        for item in source.iterdir():
            if item.name.startswith("."):
                continue
            _copy_tree(item, dest_root / item.name)


def _version_callback(value: bool):
    if value:
        typer.echo(f"aaa-tools {metadata.version('aaa-tools')}")
        raise typer.Exit()


def _parse_inputs(values: list[str] | None) -> dict[str, str]:
    result: dict[str, str] = {}
    if not values:
        return result
    for item in values:
        if "=" not in item:
            result[item] = ""
            continue
        key, value = item.split("=", 1)
        result[key] = value
    return result


def run_runbook_impl(
    spec: str | None,
    inputs: list[str] | None = None,
    json_output: bool = False,
    runbook_file: str | None = None,
    output_format: str = "human",
) -> int:
    def _format_error_details(details: object) -> list[str]:
        if details is None:
            return []
        if isinstance(details, list):
            return [str(item) for item in details]
        if isinstance(details, dict):
            return [f"{key}={json.dumps(value, ensure_ascii=True)}" for key, value in details.items()]
        return [str(details)]

    try:
        if runbook_file:
            path = Path(runbook_file)
            payload = runbook_registry.load_runbook_file(path)
        else:
            if not spec:
                raise runbook_registry.RunbookError("runbook spec is required")
            path, payload = runbook_registry.resolve_runbook(spec, REPO_ROOT)
        result = runbook_runtime.execute_runbook(payload, _parse_inputs(inputs))
        response = {"status": "ok", "result": result}
        exit_code = 0
    except runbook_registry.RunbookError as exc:
        response = {"status": "error", "error_code": "RUNBOOK_ERROR", "message": str(exc), "details": {}}
        exit_code = 2
        path = None
    except RuntimeSecurityError as exc:
        response = {"status": "error", "error_code": exc.code, "message": exc.message, "details": exc.details}
        exit_code = 2
        path = None
    except runbook_runtime.RunbookExecutionError as exc:
        response = {"status": "error", "error_code": "RUNTIME_ERROR", "message": str(exc), "details": exc.details}
        exit_code = 1
        path = None
    except Exception as exc:
        response = {"status": "error", "error_code": "RUNTIME_ERROR", "message": str(exc), "details": {}}
        exit_code = 1
        path = None

    raw_result = {
        "exit_code": exit_code,
        "errors": [response["error_code"]] if response.get("status") == "error" else [],
        "details": {response["error_code"]: _format_error_details(response.get("details"))} if response.get("status") == "error" else {},
        "response": response,
        "path": path,
    }
    
    # Handle backward compatibility with --json
    actual_format = "json" if json_output else output_format
    
    semantic_result = output_formatter.enrich_result("runbook", raw_result)
    formatter = output_formatter.get_formatter(actual_format)
    
    output = formatter.format(semantic_result)
    if typer:
        typer.echo(output)
    else:
        print(output)
        
    return exit_code
    return exit_code


if typer:
    @app.callback()
    def main(
        version: bool = typer.Option(False, "--version", help="Show version.", is_eager=True, callback=_version_callback)
    ):
        """AAA tools CLI."""
        version_check.schedule_update_hint()
        return


if typer:
    @app.command()
    def version():
        """Show version."""
        typer.echo(f"aaa-tools {metadata.version('aaa-tools')}")


if typer:
    run_typer = typer.Typer(no_args_is_help=True)
    governance_typer = typer.Typer(no_args_is_help=True)
    ops_typer = typer.Typer(no_args_is_help=True)
    ops_typer = typer.Typer(no_args_is_help=True)
    pack_typer = typer.Typer(no_args_is_help=True)
    package_typer = typer.Typer(no_args_is_help=True)
    bootstrap_typer = typer.Typer(no_args_is_help=True)
    registry_typer = registry_commands.app
    from .cmd import lock_commands
    lock_typer = lock_commands.app
    from .cmd import observability_commands
    observability_typer = observability_commands.app

    @run_typer.command("runbook")
    def run_runbook(
        spec: str | None = typer.Argument(None),
        inputs: list[str] | None = typer.Option(None, "--input"),
        json_output: bool = typer.Option(False, "--json", help="Output JSON result (Legacy)"),
        output_format: str = typer.Option("human", "--format", help="human|json|llm"),
        runbook_file: Path | None = typer.Option(None, "--runbook-file", help="Runbook JSON file"),
    ):
        """Run a runbook by id@version."""
        exit_code = run_runbook_impl(
            spec,
            inputs,
            json_output=json_output,
            runbook_file=str(runbook_file) if runbook_file else None,
            output_format=output_format,
        )
        if exit_code:
            raise typer.Exit(code=exit_code)

    @governance_typer.command("update-index")
    def governance_update_index(
        target_dir: Path = typer.Option(..., "--target-dir", help="Directory to scan"),
        pattern: str = typer.Option("*.md", "--pattern", help="Glob pattern for files"),
        readme_template: str = typer.Option(..., "--template", help="README template"),
        index_output: str = typer.Option("index.json", "--index-output", help="Index filename"),
        metadata_field: list[str] | None = typer.Option(None, "--metadata-field", help="Frontmatter keys to include"),
        include_frontmatter: bool = typer.Option(True, "--include-frontmatter/--no-include-frontmatter"),
        sort_by: str = typer.Option("filename", "--sort-by", help="filename/last_modified/frontmatter:<key>"),
        hash_algo: str = typer.Option("sha256", "--hash-algo", help="sha256/sha1"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Render without writing files"),
    ):
        """Generate README.md and index.json for a directory."""
        payload = governance_commands.update_index_cli(
            target_dir=str(target_dir),
            pattern=pattern,
            readme_template=readme_template,
            index_output=index_output,
            metadata_fields=metadata_field,
            include_frontmatter=include_frontmatter,
            sort_by=sort_by,
            hash_algo=hash_algo,
            dry_run=dry_run,
        )
        typer.echo(json.dumps(payload, indent=2))

    @governance_typer.command("validate-tool-command-adoption")
    def governance_validate_tool_command_adoption(
        bundle: Path = typer.Option(..., "--bundle", help="Path to tool-command adoption bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate tool-command adoption bundle against runtime binding registry."""
        payload = governance_commands.validate_tool_command_adoption_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("validate-multi-repo-worktree-identity")
    def governance_validate_multi_repo_worktree_identity(
        bundle: Path = typer.Option(..., "--bundle", help="Path to multi-repo worktree identity bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate multi-repo worktree identity bundle against runtime guard rules."""
        payload = governance_commands.validate_multi_repo_worktree_identity_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("validate-context-runtime-preflight")
    def governance_validate_context_runtime_preflight(
        bundle: Path = typer.Option(..., "--bundle", help="Path to context runtime preflight bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate context runtime preflight bundle against anti-contamination law."""
        payload = governance_commands.validate_context_runtime_preflight_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("validate-session-readiness-state")
    def governance_validate_session_readiness_state(
        bundle: Path = typer.Option(..., "--bundle", help="Path to session readiness state bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate session readiness state bundle against readiness gating semantics."""
        payload = governance_commands.validate_session_readiness_state_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("readiness-inspect")
    def governance_readiness_inspect(
        bundle: Path = typer.Option(..., "--bundle", help="Path to readiness-inspect adoption bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate readiness-inspect runtime adoption bundle across capability/target/truth/readiness chain."""
        payload = governance_commands.readiness_inspect_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("repo-check")
    def governance_repo_check(
        bundle: Path = typer.Option(..., "--bundle", help="Path to repo-check adoption bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate repo-check runtime adoption bundle across shared governance law."""
        payload = governance_commands.repo_check_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("shared-command-dispatch")
    def governance_shared_command_dispatch(
        dispatch_bundle: Path = typer.Option(..., "--dispatch-bundle", help="Path to shared dispatch bundle JSON"),
        command_bundle: Path = typer.Option(..., "--command-bundle", help="Path to command bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Route readiness-inspect or repo-check through a shared command dispatch runtime."""
        payload = governance_commands.shared_command_dispatch_cli(
            dispatch_bundle=str(dispatch_bundle),
            command_bundle=str(command_bundle),
        )
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("result-evidence-promotion-gate")
    def governance_result_evidence_promotion_gate(
        bundle: Path = typer.Option(..., "--bundle", help="Path to result/evidence promotion gate bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate result artifact eligibility and evidence promotion gate runtime bundle."""
        payload = governance_commands.result_evidence_promotion_gate_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("session-context-snapshot")
    def governance_session_context_snapshot(
        bundle: Path = typer.Option(..., "--bundle", help="Path to session context snapshot bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate session context snapshot runtime bundle against snapshot/reload/replay boundaries."""
        payload = governance_commands.session_context_snapshot_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("query-orchestration")
    def governance_query_orchestration(
        bundle: Path = typer.Option(..., "--bundle", help="Path to query orchestration runtime bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate query orchestration runtime bundle against dispatch/result/snapshot boundaries."""
        payload = governance_commands.query_orchestration_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("permission-gate")
    def governance_permission_gate(
        bundle: Path = typer.Option(..., "--bundle", help="Path to permission gate runtime bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate permission and authorization runtime gate bundle against authority execution boundaries."""
        payload = governance_commands.permission_gate_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("event-stream")
    def governance_event_stream(
        bundle: Path = typer.Option(..., "--bundle", help="Path to tool progress and runtime event stream bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate tool progress and runtime event stream bundle against signal/evidence boundaries."""
        payload = governance_commands.event_stream_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("session-persistence")
    def governance_session_persistence(
        bundle: Path = typer.Option(..., "--bundle", help="Path to session persistence and transcript compaction bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate session persistence and transcript compaction bundle against replay and truth boundaries."""
        payload = governance_commands.session_persistence_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("runtime-control")
    def governance_runtime_control(
        bundle: Path = typer.Option(..., "--bundle", help="Path to runtime budget/retry/recovery bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate runtime budget, retry, and recovery control bundle against shared control boundaries."""
        payload = governance_commands.runtime_control_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("result-normalization")
    def governance_result_normalization(
        bundle: Path = typer.Option(..., "--bundle", help="Path to structured output normalization bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate structured output and result normalization bundle against shared normalization boundaries."""
        payload = governance_commands.result_normalization_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("workflow-runtime")
    def governance_workflow_runtime(
        bundle: Path = typer.Option(..., "--bundle", help="Path to workflow and runbook orchestration runtime bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate workflow and runbook orchestration runtime bundle against step/gate boundaries."""
        payload = governance_commands.workflow_runtime_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("delegation-lifecycle")
    def governance_delegation_lifecycle(
        bundle: Path = typer.Option(..., "--bundle", help="Path to agent delegation and task lifecycle runtime bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate delegation lifecycle runtime bundle against handoff and verification boundaries."""
        payload = governance_commands.delegation_lifecycle_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("extension-runtime")
    def governance_extension_runtime(
        bundle: Path = typer.Option(..., "--bundle", help="Path to skill and plugin extension runtime bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate skill and plugin extension runtime bundle against load/register/trust boundaries."""
        payload = governance_commands.extension_runtime_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("composition-root")
    def governance_composition_root(
        bundle: Path = typer.Option(..., "--bundle", help="Path to runtime composition root bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate runtime composition root bundle against mandatory core closeout assembly boundaries."""
        payload = governance_commands.composition_root_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("offering-package-selection-runtime-baseline")
    def governance_offering_package_selection_runtime_baseline(
        bundle: Path = typer.Option(
            ...,
            "--bundle",
            help="Path to offering package selection runtime baseline bundle JSON",
        ),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate package selection enum/artifact bundle without leaking into resolution or gate semantics."""
        payload = governance_commands.offering_package_selection_runtime_baseline_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("offering-package-definition-resolution")
    def governance_offering_package_definition_resolution(
        bundle: Path = typer.Option(
            ...,
            "--bundle",
            help="Path to offering package definition resolution bundle JSON",
        ),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate pre-topology offering package definition resolution bundle."""
        payload = governance_commands.offering_package_definition_resolution_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("offering-package-prerequisite-gate")
    def governance_offering_package_prerequisite_gate(
        bundle: Path = typer.Option(
            ...,
            "--bundle",
            help="Path to offering package prerequisite gate bundle JSON",
        ),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate pre-topology offering package prerequisite gate bundle."""
        payload = governance_commands.offering_package_prerequisite_gate_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("offering-package-materialization-and-bootstrap-mapping")
    def governance_offering_package_materialization_and_bootstrap_mapping(
        bundle: Path = typer.Option(
            ...,
            "--bundle",
            help="Path to offering package materialization and bootstrap mapping bundle JSON",
        ),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate pre-topology offering package materialization/bootstrap mapping bundle."""
        payload = governance_commands.offering_package_materialization_and_bootstrap_mapping_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("offering-package-status-and-evidence-runtime")
    def governance_offering_package_status_and_evidence_runtime(
        bundle: Path = typer.Option(
            ...,
            "--bundle",
            help="Path to offering package status and evidence runtime bundle JSON",
        ),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate offering package status/evidence bundle against pre-topology layered status boundaries."""
        payload = governance_commands.offering_package_status_and_evidence_runtime_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("package-machine-interface-read-boundary")
    def governance_package_machine_interface_read_boundary(
        bundle: Path = typer.Option(
            ...,
            "--bundle",
            help="Path to package machine interface read boundary bundle JSON",
        ),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate package machine-readable read boundary bundle against read-only/non-orchestration boundaries."""
        payload = governance_commands.package_machine_interface_read_boundary_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("offering-package-composition-and-closeout")
    def governance_offering_package_composition_and_closeout(
        bundle: Path = typer.Option(
            ...,
            "--bundle",
            help="Path to offering package composition and closeout bundle JSON",
        ),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate offering package runtime core closeout bundle against consumed-stage and no-rejudgment boundaries."""
        payload = governance_commands.offering_package_composition_and_closeout_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("topology-aware-init-plan-validation")
    def governance_topology_aware_init_plan_validation(
        bundle: Path = typer.Option(..., "--bundle", help="Path to topology-aware init plan validation bundle JSON"),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate topology-aware init plan validation bundle against declared/planned structure boundaries."""
        payload = governance_commands.topology_aware_init_plan_validation_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("topology-aware-offering-package-definition-resolution")
    def governance_topology_aware_offering_package_definition_resolution(
        bundle: Path = typer.Option(
            ...,
            "--bundle",
            help="Path to topology-aware offering package definition resolution bundle JSON",
        ),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate topology-aware offering package definition resolution bundle against mother-draft boundaries."""
        payload = governance_commands.topology_aware_offering_package_definition_resolution_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("topology-aware-prerequisite-gate")
    def governance_topology_aware_prerequisite_gate(
        bundle: Path = typer.Option(
            ...,
            "--bundle",
            help="Path to topology-aware prerequisite gate bundle JSON",
        ),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate topology-aware prerequisite gate bundle against pre-adoption gate boundaries."""
        payload = governance_commands.topology_aware_prerequisite_gate_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("topology-aware-materialization-and-bootstrap-mapping")
    def governance_topology_aware_materialization_and_bootstrap_mapping(
        bundle: Path = typer.Option(
            ...,
            "--bundle",
            help="Path to topology-aware materialization and bootstrap mapping bundle JSON",
        ),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate topology-aware materialization/bootstrap mapping bundle against placement boundaries."""
        payload = governance_commands.topology_aware_materialization_and_bootstrap_mapping_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("topology-aware-package-status-and-repo-checks")
    def governance_topology_aware_package_status_and_repo_checks(
        bundle: Path = typer.Option(
            ...,
            "--bundle",
            help="Path to topology-aware package status and repo checks bundle JSON",
        ),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate topology-aware package status/repo-check bundle against topology compliance boundaries."""
        payload = governance_commands.topology_aware_package_status_and_repo_checks_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("github-governance-topology-contract-baseline")
    def governance_github_governance_topology_contract_baseline(
        bundle: Path = typer.Option(
            ...,
            "--bundle",
            help="Path to github governance topology contract baseline bundle JSON",
        ),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate topology contract baseline bundle against hybrid authority and dedicated-only rejection boundaries."""
        payload = governance_commands.github_governance_topology_contract_baseline_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @governance_typer.command("github-governance-topology-composition-and-closeout")
    def governance_github_governance_topology_composition_and_closeout(
        bundle: Path = typer.Option(
            ...,
            "--bundle",
            help="Path to github governance topology composition and closeout bundle JSON",
        ),
        output_format: str = typer.Option("human", "--format", help="human|json"),
    ):
        """Validate topology support closeout bundle against consumed-stage and no-rejudgment boundaries."""
        payload = governance_commands.github_governance_topology_composition_and_closeout_cli(bundle=str(bundle))
        if output_format == "json":
            typer.echo(json.dumps(payload, indent=2, ensure_ascii=True))
        else:
            typer.echo(f"status={payload['status']} valid={payload['valid']}")
            for error in payload["errors"]:
                typer.echo(f"{error['code']}: {error['message']}")
        if not payload["valid"]:
            raise typer.Exit(code=2)

    @ops_typer.command("render-dashboard")
    def ops_render_dashboard(
        input_path: Path = typer.Option(..., "--input", help="Input JSON file"),
        md_out: Path = typer.Option(..., "--md-out", help="Markdown output path"),
        html_out: Path = typer.Option(..., "--html-out", help="HTML output path"),
        threshold: float = typer.Option(0.8, "--threshold", help="Compliance threshold"),
        drift_threshold: float = typer.Option(0.05, "--drift-threshold", help="Drift rate threshold"),
        health_threshold: float = typer.Option(0.9, "--health-threshold", help="Repo health threshold"),
    ):
        """Render governance dashboard outputs."""
        from aaa.ops.render_dashboard import render_dashboard

        compliance_rate, metrics = render_dashboard(
            str(input_path),
            str(md_out),
            str(html_out),
            {
                "compliance": threshold,
                "drift": drift_threshold,
                "health": health_threshold,
            },
        )
        drift_rate = metrics.get("drift_rate", 0.0)
        repo_health = metrics.get("repo_health", 1.0)
        if compliance_rate < threshold or drift_rate > drift_threshold or repo_health < health_threshold:
            raise typer.Exit(code=1)

    @pack_typer.command("list")
    def pack_list():
        """List installed packs for the current repo."""
        payload = pack_commands.list_packs(Path.cwd())
        typer.echo(json.dumps(payload, ensure_ascii=True))

    @package_typer.command("select")
    def package_select(
        level: str = typer.Option(..., "--level", help="lite|core|full"),
        output_format: str = typer.Option("human", "--format", help="human|json|llm"),
    ):
        """Select a public package level without leaking into resolution or activation semantics."""
        try:
            payload = package_commands.select(level)
        except ValueError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=2)
        typer.echo(package_commands.render_payload(payload, output_format))

    @package_typer.command("resolve")
    def package_resolve(
        level: str = typer.Option(..., "--level", help="lite|core|full"),
        topology_mode: str = typer.Option("repo_local", "--topology-mode", help="dedicated_repo|repo_local|hybrid"),
        output_format: str = typer.Option("human", "--format", help="human|json|llm"),
    ):
        """Resolve a public package definition through topology-aware package truth."""
        try:
            payload = package_commands.resolve(level, topology_mode)
        except ValueError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=2)
        typer.echo(package_commands.render_payload(payload, output_format))

    @package_typer.command("status")
    def package_status(
        level: str = typer.Option(..., "--level", help="lite|core|full"),
        topology_mode: str = typer.Option("repo_local", "--topology-mode", help="dedicated_repo|repo_local|hybrid"),
        workspace: Path = typer.Option(Path.cwd(), "--workspace", help="Workspace root to inspect"),
        output_format: str = typer.Option("human", "--format", help="human|json|llm"),
    ):
        """Discover package status through pre-topology package status plus topology-aware adjudication."""
        try:
            payload = package_commands.status(level, topology_mode, workspace)
        except (ValueError, FileNotFoundError) as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=2)
        typer.echo(package_commands.render_payload(payload, output_format))

    @bootstrap_typer.command("supported-path")
    def bootstrap_supported_path(
        level: str = typer.Option(..., "--level", help="lite|core|full"),
        topology_mode: str = typer.Option("repo_local", "--topology-mode", help="dedicated_repo|repo_local|hybrid"),
        output_format: str = typer.Option("human", "--format", help="human|json|llm"),
    ):
        """Show the one canonical public bootstrap path without inventing a second environment-profile path."""
        try:
            payload = bootstrap_commands.supported_path(level, topology_mode)
        except ValueError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=2)
        typer.echo(bootstrap_commands.render_payload(payload, output_format))

    @app.command("audit")
    def audit(
        local: bool = typer.Option(False, "--local", help="Audit current repo"),
        remote: Optional[str] = typer.Option(None, "--remote", help="Remote repo URL"),
        output: Optional[Path] = typer.Option(None, "--output", help="Output JSON path"),
        output_format: str = typer.Option("human", "--format", help="human|json|llm"),
    ):
        """Generate governance audit report."""
        if local:
            payload = audit_commands.run_local_audit(Path.cwd())
        elif remote:
            payload = audit_commands.run_remote_audit(remote)
        else:
            raise typer.Exit(code=2)

        # v1.8 Observability Integration (Metrics + Ledger)
        try:
            from .observability.custom_metrics import MetricStore
            store = MetricStore()
            # Extract compliance score (assumption: payload has 'stats' or similar)
            # For v1.7 audit payload, let's assume raw_result has 'compliance_score'
            # If not, we calculate it or just log success for now
            score = payload.get("stats", {}).get("compliance_score", 0.0)
            store.record("audit_compliance", score, tags={"scope": "local" if local else "remote"})
        except Exception:
            pass # Fail open if observability DB is locked/failed
        
        # If output file is specified, always write JSON there (standard behavior)
        if output:
            output.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
            typer.echo(f"Audit report written to {output}")
            
        # Also print to stdout using the specified format
        semantic_result = output_formatter.enrich_result("audit", payload)
        formatter = output_formatter.get_formatter(output_format)
        typer.echo(formatter.format(semantic_result))


def sync_skills(target: str = "codex"):
    """Sync skills to the specified target."""
    if target not in {"codex", "agent"}:
        raise ValueError("target must be codex or agent")
    skills_root = REPO_ROOT / "skills"
    sources = [skills_root / "common", skills_root / target]
    dest_root = Path.cwd() / (".codex/skills" if target == "codex" else ".agent/skills")
    _sync_sources(sources, dest_root)
    if typer:
        typer.echo(f"sync skills -> {dest_root}")
    else:
        print(f"sync skills -> {dest_root}")


def sync_workflows(target: str = "agent"):
    """Sync workflows to the specified target."""
    if target != "agent":
        raise ValueError("target must be agent")
    workflows_root = REPO_ROOT / "workflows" / "agent"
    dest_root = Path.cwd() / ".agent/workflows"
    _sync_sources([workflows_root], dest_root)
    if typer:
        typer.echo(f"sync workflows -> {dest_root}")
    else:
        print(f"sync workflows -> {dest_root}")


def sync_operate_maintain_workflow(force_index: bool = False):
    """Sync operate_maintain_workflow_v2 capability scaffold to current repo."""
    capability_root = REPO_ROOT / "workflows" / "operate_maintain_workflow_v2"
    if not capability_root.exists():
        raise ValueError(f"capability scaffold not found: {capability_root}")

    copied: list[str] = []
    skipped: list[str] = []
    for src in capability_root.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(capability_root)
        dest = Path.cwd() / rel
        is_index_file = rel.as_posix() in {
            "aaa-tpl-docs/ops/index/version_index.md",
            "aaa-tpl-docs/ops/index/workflow_index.md",
        }
        if is_index_file and dest.exists() and not force_index:
            skipped.append(rel.as_posix())
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        copied.append(rel.as_posix())

    msg = {
        "capability": "operate_maintain_workflow_v2",
        "source": str(capability_root),
        "copied": copied,
        "skipped": skipped,
        "force_index": force_index,
    }
    if typer:
        typer.echo(json.dumps(msg, ensure_ascii=True))
    else:
        print(json.dumps(msg, ensure_ascii=True))


if typer:
    @app.command()
    def lint():
        """Lint workspace (stub)."""
        typer.echo("lint stub")

    @app.command("check")
    def check(
        mode: str = typer.Option("blocking", "--mode", help="blocking"),
        output_format: str = typer.Option("human", "--format", help="human|json|llm"),
        remote: Optional[str] = typer.Option(None, "--remote", help="Remote Policy ID to run"),
        registry: str = typer.Option("file:///Users/imac/Documents/Code/AI-Lotto/AAA_WORKSPACE/aaa-policies", "--registry", help="Registry URL"),
        auto_fix: bool = typer.Option(False, "--auto-fix", help="Attempt to automatically fix violations"),
    ):
        """Run governance checks (local or remote)."""
        print(f"DEBUG: CLI check called. Mode={mode}, AutoFix={auto_fix}")
        if remote:
            # Remote Mode
            raw_result = check_commands.run_remote_policy(remote, registry)
        elif mode == "blocking":
            # Normal Blocking Mode
            raw_result = check_commands.run_blocking_check(Path.cwd(), auto_fix=auto_fix)
        else:
            raise typer.Exit(code=2)
        semantic_result = output_formatter.enrich_result("check", raw_result)
        
        formatter = output_formatter.get_formatter(output_format)
        typer.echo(formatter.format(semantic_result))
        
        if semantic_result.exit_code:
            raise typer.Exit(code=semantic_result.exit_code)


if typer:
    @app.command("eval")
    def eval_run(suite: str = typer.Argument("smoke")):
        """Run eval suite (stub)."""
        typer.echo(f"eval stub -> suite={suite}")


if typer:
    @app.command("outdated")
    def outdated(json_output: bool = typer.Option(False, "--json", help="Output JSON report")):
        """Report outdated AAA components."""
        report = outdated_commands.build_outdated_report(Path.cwd())
        if json_output:
            typer.echo(json.dumps(report, ensure_ascii=True, indent=2))
            return
        typer.echo(outdated_commands.render_outdated_report(report))


if typer:
    from .cmd import registry_commands
    from .cmd import court_commands

    sync_typer = typer.Typer(no_args_is_help=True)
    sync_typer.command("skills")(sync_skills)
    sync_typer.command("workflows")(sync_workflows)
    sync_typer.command("operate-maintain-workflow")(sync_operate_maintain_workflow)
    app.add_typer(sync_typer, name="sync")
    app.add_typer(init_commands.init_app, name="init")
    app.add_typer(run_typer, name="run")
    app.add_typer(governance_typer, name="governance")
    app.add_typer(ops_typer, name="ops")
    app.add_typer(ops_typer, name="ops")
    app.add_typer(ops_typer, name="ops")
    app.add_typer(ops_typer, name="ops")
    app.add_typer(pack_typer, name="pack")
    app.add_typer(package_typer, name="package")
    app.add_typer(bootstrap_typer, name="bootstrap")
    app.add_typer(registry_typer, name="registry")
    app.add_typer(lock_typer, name="lock")
    app.add_typer(observability_typer, name="observe")
    app.add_typer(court_commands.app, name="court", help="Supreme Court Interface (v1.9)")
    
    # v2.0 Agent OS
    from .cmd import os_commands
    app.add_typer(os_commands.app, name="os", help="Agent OS Kernel (v2.0)")
    app.add_typer(os_commands.trust_app, name="trust", help="Global Trust Network")
    app.add_typer(os_commands.cert_app, name="cert", help="Enterprise Certification")


def _run_fallback() -> int:
    parser = argparse.ArgumentParser(prog="aaa", description="AAA tools CLI (fallback)")
    parser.add_argument("--version", action="store_true", help="Show version")
    subparsers = parser.add_subparsers(dest="command")

    sync_parser = subparsers.add_parser("sync")
    sync_sub = sync_parser.add_subparsers(dest="sync_command")
    sync_skills_parser = sync_sub.add_parser("skills")
    sync_skills_parser.add_argument("--target", default="codex")
    sync_workflows_parser = sync_sub.add_parser("workflows")
    sync_workflows_parser.add_argument("--target", default="agent")
    sync_omw_parser = sync_sub.add_parser("operate-maintain-workflow")
    sync_omw_parser.add_argument("--force-index", action="store_true")

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--plan")
    init_parser.add_argument("--mode", default="pr")
    init_parser.add_argument("--preset")
    init_parser.add_argument("--jsonl", action="store_true")
    init_parser.add_argument("--log-dir")
    init_parser.add_argument("--dry-run", action="store_true")
    init_sub = init_parser.add_subparsers(dest="init_command")

    validate_parser = init_sub.add_parser("validate-plan")
    validate_parser.add_argument("--plan", required=True)
    validate_parser.add_argument("--schema", default=str(REPO_ROOT / "specs" / "plan.schema.json"))
    validate_parser.add_argument("--jsonl", action="store_true")
    validate_parser.add_argument("--log-dir")

    ops_parser = subparsers.add_parser("ops")
    ops_sub = ops_parser.add_subparsers(dest="ops_command")
    render_parser = ops_sub.add_parser("render-dashboard")
    render_parser.add_argument("--input", required=True)
    render_parser.add_argument("--md-out", required=True)
    render_parser.add_argument("--html-out", required=True)
    render_parser.add_argument("--threshold", type=float, default=0.8)
    render_parser.add_argument("--drift-threshold", type=float, default=0.05)
    render_parser.add_argument("--health-threshold", type=float, default=0.9)

    ensure_parser = init_sub.add_parser("ensure-repos")
    ensure_parser.add_argument("--org", required=True)
    ensure_parser.add_argument("--from-plan", required=True)
    ensure_parser.add_argument("--preset")
    ensure_parser.add_argument("--jsonl", action="store_true")
    ensure_parser.add_argument("--log-dir")
    ensure_parser.add_argument("--dry-run", action="store_true")

    apply_parser = init_sub.add_parser("apply-templates")
    apply_parser.add_argument("--org", required=True)
    apply_parser.add_argument("--from-plan", required=True)
    apply_parser.add_argument("--preset")
    apply_parser.add_argument("--aaa-tag", required=True)
    apply_parser.add_argument("--jsonl", action="store_true")
    apply_parser.add_argument("--log-dir")
    apply_parser.add_argument("--dry-run", action="store_true")

    protect_parser = init_sub.add_parser("protect")
    protect_parser.add_argument("--org", required=True)
    protect_parser.add_argument("--from-plan", required=True)
    protect_parser.add_argument("--preset")
    protect_parser.add_argument("--jsonl", action="store_true")
    protect_parser.add_argument("--log-dir")
    protect_parser.add_argument("--dry-run", action="store_true")

    verify_parser = init_sub.add_parser("verify-ci")
    verify_parser.add_argument("--org", required=True)
    verify_parser.add_argument("--from-plan", required=True)
    verify_parser.add_argument("--preset")
    verify_parser.add_argument("--jsonl", action="store_true")
    verify_parser.add_argument("--log-dir")
    verify_parser.add_argument("--dry-run", action="store_true")

    open_prs_parser = init_sub.add_parser("open-prs")
    open_prs_parser.add_argument("--org", required=True)
    open_prs_parser.add_argument("--from-plan", required=True)
    open_prs_parser.add_argument("--preset")
    open_prs_parser.add_argument("--jsonl", action="store_true")
    open_prs_parser.add_argument("--log-dir")
    open_prs_parser.add_argument("--dry-run", action="store_true")

    repo_checks_parser = init_sub.add_parser("repo-checks")
    repo_checks_parser.add_argument("--org", required=True)
    repo_checks_parser.add_argument("--from-plan", required=True)
    repo_checks_parser.add_argument("--preset")
    repo_checks_parser.add_argument("--suite", required=True)
    repo_checks_parser.add_argument("--jsonl", action="store_true")
    repo_checks_parser.add_argument("--log-dir")
    repo_checks_parser.add_argument("--dry-run", action="store_true")

    enterprise_parser = init_sub.add_parser("enterprise")
    enterprise_parser.add_argument("--repo-type", required=True)
    enterprise_parser.add_argument("--plan-ref", default="enterprise")

    run_parser = subparsers.add_parser("run")
    run_sub = run_parser.add_subparsers(dest="run_command")
    runbook_parser = run_sub.add_parser("runbook")
    runbook_parser.add_argument("spec", nargs="?")
    runbook_parser.add_argument("--input", action="append")
    runbook_parser.add_argument("--json", action="store_true", help="Output JSON result (Legacy)")
    runbook_parser.add_argument("--format", dest="output_format", default="human", help="human|json|llm")
    runbook_parser.add_argument("--runbook-file")

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--mode", default="blocking")
    check_parser.add_argument("--format", dest="output_format", default="human", help="human|json|llm")
    check_parser.add_argument("--remote", help="Remote Policy ID")
    check_parser.add_argument("--registry", default="file:///Users/imac/Documents/Code/AI-Lotto/AAA_WORKSPACE/aaa-policies")
    check_parser.add_argument("--auto-fix", action="store_true")

    governance_parser = subparsers.add_parser("governance")
    governance_sub = governance_parser.add_subparsers(dest="governance_command")
    update_index_parser = governance_sub.add_parser("update-index")
    update_index_parser.add_argument("--target-dir", required=True)
    update_index_parser.add_argument("--pattern", default="*.md")
    update_index_parser.add_argument("--template", required=True)
    update_index_parser.add_argument("--index-output", default="index.json")
    update_index_parser.add_argument("--metadata-field", action="append")
    update_index_parser.add_argument("--include-frontmatter", action="store_true")
    update_index_parser.add_argument("--no-include-frontmatter", action="store_true")
    update_index_parser.add_argument("--sort-by", default="filename")
    update_index_parser.add_argument("--hash-algo", default="sha256")
    update_index_parser.add_argument("--dry-run", action="store_true")

    pack_parser = subparsers.add_parser("pack")
    pack_sub = pack_parser.add_subparsers(dest="pack_command")
    pack_sub.add_parser("list")

    audit_parser = subparsers.add_parser("audit")
    audit_parser.add_argument("--local", action="store_true")
    audit_parser.add_argument("--remote", help="Remote repo URL")
    audit_parser.add_argument("--output", help="Output JSON path")
    audit_parser.add_argument("--format", dest="output_format", default="human", help="human|json|llm")

    outdated_parser = subparsers.add_parser("outdated")
    outdated_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()
    if args.version:
        print("aaa-tools 1.5.0")
        return 0

    version_check.schedule_update_hint()

    if args.command == "sync":
        if args.sync_command == "skills":
            sync_skills(args.target)
            return 0
        if args.sync_command == "workflows":
            sync_workflows(args.target)
            return 0
        if args.sync_command == "operate-maintain-workflow":
            sync_operate_maintain_workflow(args.force_index)
            return 0
        parser.error("sync requires a subcommand")

    if args.command == "init":
        if args.init_command is None and args.plan:
            init_commands.run_plan(
                plan=Path(args.plan),
                mode=args.mode,
                preset=args.preset,
                jsonl=args.jsonl,
                log_dir=Path(args.log_dir) if args.log_dir else None,
                dry_run=args.dry_run,
            )
            return 0
        if args.init_command == "validate-plan":
            init_commands.validate_plan(
                plan=Path(args.plan),
                schema=Path(args.schema),
                jsonl=args.jsonl,
                log_dir=Path(args.log_dir) if args.log_dir else None,
            )
            return 0
        if args.init_command == "ensure-repos":
            init_commands.ensure_repos(
                org=args.org,
                from_plan=Path(args.from_plan),
                preset=args.preset,
                jsonl=args.jsonl,
                log_dir=Path(args.log_dir) if args.log_dir else None,
                dry_run=args.dry_run,
            )
            return 0
        if args.init_command == "apply-templates":
            init_commands.apply_templates(
                org=args.org,
                from_plan=Path(args.from_plan),
                preset=args.preset,
                aaa_tag=args.aaa_tag,
                jsonl=args.jsonl,
                log_dir=Path(args.log_dir) if args.log_dir else None,
                dry_run=args.dry_run,
            )
            return 0
        if args.init_command == "protect":
            init_commands.protect(
                org=args.org,
                from_plan=Path(args.from_plan),
                preset=args.preset,
                jsonl=args.jsonl,
                log_dir=Path(args.log_dir) if args.log_dir else None,
                dry_run=args.dry_run,
            )
            return 0
        if args.init_command == "verify-ci":
            init_commands.verify_ci(
                org=args.org,
                from_plan=Path(args.from_plan),
                preset=args.preset,
                jsonl=args.jsonl,
                log_dir=Path(args.log_dir) if args.log_dir else None,
                dry_run=args.dry_run,
            )
            return 0
        if args.init_command == "open-prs":
            init_commands.open_prs(
                org=args.org,
                from_plan=Path(args.from_plan),
                preset=args.preset,
                jsonl=args.jsonl,
                log_dir=Path(args.log_dir) if args.log_dir else None,
                dry_run=args.dry_run,
            )
            return 0
        if args.init_command == "repo-checks":
            init_commands.repo_checks(
                org=args.org,
                from_plan=Path(args.from_plan),
                preset=args.preset,
                suite=args.suite,
                jsonl=args.jsonl,
                log_dir=Path(args.log_dir) if args.log_dir else None,
                dry_run=args.dry_run,
            )
            return 0
        if args.init_command == "enterprise":
            init_commands.enterprise(
                repo_type=args.repo_type,
                plan_ref=args.plan_ref,
            )
            return 0

    if args.command == "governance":
        if args.governance_command == "update-index":
            include_frontmatter = True
            if args.no_include_frontmatter:
                include_frontmatter = False
            payload = governance_commands.update_index_cli(
                target_dir=args.target_dir,
                pattern=args.pattern,
                readme_template=args.template,
                index_output=args.index_output,
                metadata_fields=args.metadata_field,
                include_frontmatter=include_frontmatter,
                sort_by=args.sort_by,
                hash_algo=args.hash_algo,
                dry_run=args.dry_run,
            )
            print(json.dumps(payload, indent=2))
            return 0

    if args.command == "pack":
        if args.pack_command == "list":
            payload = pack_commands.list_packs(Path.cwd())
            print(json.dumps(payload, ensure_ascii=True))
            return 0

    if args.command == "audit":
        if args.local:
            payload = audit_commands.run_local_audit(Path.cwd())
        elif args.remote:
            payload = audit_commands.run_remote_audit(args.remote)
        else:
            return 2
        if args.output:
            Path(args.output).write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
        
        semantic_result = output_formatter.enrich_result("audit", payload)
        formatter = output_formatter.get_formatter(args.output_format)
        print(formatter.format(semantic_result))
        return 0

    if args.command == "ops":
        if args.ops_command == "render-dashboard":
            from aaa.ops.render_dashboard import render_dashboard

            compliance_rate, metrics = render_dashboard(
                args.input,
                args.md_out,
                args.html_out,
                {
                    "compliance": args.threshold,
                    "drift": args.drift_threshold,
                    "health": args.health_threshold,
                },
            )
            drift_rate = metrics.get("drift_rate", 0.0)
            repo_health = metrics.get("repo_health", 1.0)
            if compliance_rate < args.threshold or drift_rate > args.drift_threshold or repo_health < args.health_threshold:
                return 1
            return 0

    if args.command == "run":
        if args.run_command == "runbook":
            exit_code = run_runbook_impl(
                args.spec,
                args.input,
                json_output=args.json,
                runbook_file=args.runbook_file,
                output_format=args.output_format,
            )
            return exit_code
        parser.error("init requires a subcommand")

    if args.command == "check":
        if args.remote:
             raw_result = check_commands.run_remote_policy(args.remote, args.registry)
        elif args.mode == "blocking":
             raw_result = check_commands.run_blocking_check(Path.cwd(), auto_fix=args.auto_fix)
        else:
            return 2
            
        semantic_result = output_formatter.enrich_result("check", raw_result)
        formatter = output_formatter.get_formatter(args.output_format)
        print(formatter.format(semantic_result))
        return semantic_result.exit_code

    if args.command == "outdated":
        report = outdated_commands.build_outdated_report(Path.cwd())
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
            return 0
        print(outdated_commands.render_outdated_report(report))
        return 0

    if args.command == "run":
        if args.run_command == "runbook":
            try:
                path, payload = runbook_registry.resolve_runbook(args.spec, REPO_ROOT)
            except runbook_registry.RunbookError as exc:
                print(f"runbook error: {exc}")
                return 2
            print(f"runbook resolved: {path}")
            print(f"runbook id: {payload.get('metadata', {}).get('id')}")
            print(f"runbook version: {payload.get('metadata', {}).get('version')}")
            return 0
        parser.error("run requires a subcommand")

    parser.print_help()
    return 1


if __name__ == "__main__":
    if typer:
        app()
    else:
        sys.exit(_run_fallback())
