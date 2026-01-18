import shutil
from pathlib import Path

import typer

app = typer.Typer(no_args_is_help=True)
sync_app = typer.Typer(no_args_is_help=True)
workflows_app = typer.Typer(no_args_is_help=True)

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


@app.callback()
def main(version: bool = typer.Option(False, "--version", help="Show version.", is_eager=True, callback=_version_callback)):
    """AAA tools CLI."""
    return


@app.command()
def version():
    """Show version."""
    typer.echo("aaa-tools 0.1.0")


@sync_app.command("skills")
def sync_skills(target: str = typer.Option("codex", help="codex|agent")):
    """Sync skills to the specified target."""
    if target not in {"codex", "agent"}:
        raise typer.BadParameter("target must be codex or agent")
    skills_root = REPO_ROOT / "skills"
    sources = [skills_root / "common", skills_root / target]
    dest_root = Path.cwd() / (".codex/skills" if target == "codex" else ".agent/skills")
    _sync_sources(sources, dest_root)
    typer.echo(f"sync skills -> {dest_root}")


@sync_app.command("workflows")
def sync_workflows(target: str = typer.Option("agent", help="agent")):
    """Sync workflows to the specified target."""
    if target != "agent":
        raise typer.BadParameter("target must be agent")
    workflows_root = REPO_ROOT / "workflows" / "agent"
    dest_root = Path.cwd() / ".agent/workflows"
    _sync_sources([workflows_root], dest_root)
    typer.echo(f"sync workflows -> {dest_root}")


@app.command()
def lint():
    """Lint workspace (stub)."""
    typer.echo("lint stub")


@app.command("eval")
def eval_run(suite: str = typer.Argument("smoke")):
    """Run eval suite (stub)."""
    typer.echo(f"eval stub -> suite={suite}")


app.add_typer(sync_app, name="sync")


if __name__ == "__main__":
    app()
