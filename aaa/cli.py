import typer

app = typer.Typer(no_args_is_help=True)
sync_app = typer.Typer(no_args_is_help=True)


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
    """Sync skills to the specified target (stub)."""
    typer.echo(f"sync skills stub -> target={target}")


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
