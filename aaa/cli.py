import argparse
import shutil
import sys
from pathlib import Path

try:
    import typer
except Exception:  # pragma: no cover - fallback when typer isn't available
    typer = None

from . import init_commands

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
        typer.echo("aaa-tools 0.1.0")
        raise typer.Exit()


if typer:
    @app.callback()
    def main(
        version: bool = typer.Option(False, "--version", help="Show version.", is_eager=True, callback=_version_callback)
    ):
        """AAA tools CLI."""
        return


if typer:
    @app.command()
    def version():
        """Show version."""
        typer.echo("aaa-tools 0.1.0")


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


if typer:
    @app.command()
    def lint():
        """Lint workspace (stub)."""
        typer.echo("lint stub")


if typer:
    @app.command("eval")
    def eval_run(suite: str = typer.Argument("smoke")):
        """Run eval suite (stub)."""
        typer.echo(f"eval stub -> suite={suite}")


if typer:
    sync_typer = typer.Typer(no_args_is_help=True)
    sync_typer.command("skills")(sync_skills)
    sync_typer.command("workflows")(sync_workflows)
    app.add_typer(sync_typer, name="sync")
    app.add_typer(init_commands.init_app, name="init")


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

    init_parser = subparsers.add_parser("init")
    init_sub = init_parser.add_subparsers(dest="init_command")

    validate_parser = init_sub.add_parser("validate-plan")
    validate_parser.add_argument("--plan", required=True)
    validate_parser.add_argument("--schema", default=str(REPO_ROOT / "specs" / "plan.schema.json"))
    validate_parser.add_argument("--jsonl", action="store_true")
    validate_parser.add_argument("--log-dir")

    ensure_parser = init_sub.add_parser("ensure-repos")
    ensure_parser.add_argument("--org", required=True)
    ensure_parser.add_argument("--from-plan", required=True)
    ensure_parser.add_argument("--jsonl", action="store_true")
    ensure_parser.add_argument("--log-dir")
    ensure_parser.add_argument("--dry-run", action="store_true")

    apply_parser = init_sub.add_parser("apply-templates")
    apply_parser.add_argument("--org", required=True)
    apply_parser.add_argument("--from-plan", required=True)
    apply_parser.add_argument("--aaa-tag", required=True)
    apply_parser.add_argument("--jsonl", action="store_true")
    apply_parser.add_argument("--log-dir")
    apply_parser.add_argument("--dry-run", action="store_true")

    protect_parser = init_sub.add_parser("protect")
    protect_parser.add_argument("--org", required=True)
    protect_parser.add_argument("--from-plan", required=True)
    protect_parser.add_argument("--jsonl", action="store_true")
    protect_parser.add_argument("--log-dir")
    protect_parser.add_argument("--dry-run", action="store_true")

    verify_parser = init_sub.add_parser("verify-ci")
    verify_parser.add_argument("--org", required=True)
    verify_parser.add_argument("--from-plan", required=True)
    verify_parser.add_argument("--jsonl", action="store_true")
    verify_parser.add_argument("--log-dir")
    verify_parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()
    if args.version:
        print("aaa-tools 0.1.0")
        return 0

    if args.command == "sync":
        if args.sync_command == "skills":
            sync_skills(args.target)
            return 0
        if args.sync_command == "workflows":
            sync_workflows(args.target)
            return 0
        parser.error("sync requires a subcommand")

    if args.command == "init":
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
                jsonl=args.jsonl,
                log_dir=Path(args.log_dir) if args.log_dir else None,
                dry_run=args.dry_run,
            )
            return 0
        if args.init_command == "apply-templates":
            init_commands.apply_templates(
                org=args.org,
                from_plan=Path(args.from_plan),
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
                jsonl=args.jsonl,
                log_dir=Path(args.log_dir) if args.log_dir else None,
                dry_run=args.dry_run,
            )
            return 0
        if args.init_command == "verify-ci":
            init_commands.verify_ci(
                org=args.org,
                from_plan=Path(args.from_plan),
                jsonl=args.jsonl,
                log_dir=Path(args.log_dir) if args.log_dir else None,
                dry_run=args.dry_run,
            )
            return 0
        parser.error("init requires a subcommand")

    parser.print_help()
    return 1


if __name__ == "__main__":
    if typer:
        app()
    else:
        sys.exit(_run_fallback())
