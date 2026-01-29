import typer
from pathlib import Path
from typing import Optional

from aaa.engine.locking import LockManager

app = typer.Typer(no_args_is_help=True)

def get_lock_manager() -> LockManager:
    # Locate workspace root (simplistic assumption for now: CWD or parent-traversal)
    # In AAA toolkit, it's safer to use a utility, but for now assuming CWD.
    return LockManager(Path.cwd())

@app.command("acquire")
def acquire_lock(
    path: str = typer.Argument(..., help="Relative path to file"),
    owner: str = typer.Option(..., "--owner", help="Identity of the lock owner (e.g. agent-id)"),
    ttl: int = typer.Option(5, "--ttl", help="Time-to-live in minutes")
):
    """Acquire a lock on a file."""
    mgr = get_lock_manager()
    success = mgr.acquire(path, owner, ttl_minutes=ttl)
    if success:
        typer.echo(f"✅ Locked: {path} (Owner: {owner}, TTL: {ttl}m)")
    else:
        typer.echo(f"❌ Failed to lock: {path} (Already locked)")
        raise typer.Exit(code=1)

@app.command("release")
def release_lock(
    path: str = typer.Argument(..., help="Relative path to file"),
    owner: str = typer.Option(..., "--owner", help="Identity of the lock owner")
):
    """Release a lock."""
    mgr = get_lock_manager()
    success = mgr.release(path, owner)
    if success:
        typer.echo(f"🔓 Released: {path}")
    else:
        typer.echo(f"❌ Failed to release: {path} (Not locked or wrong owner)")
        raise typer.Exit(code=1)

@app.command("check")
def check_lock(path: str = typer.Argument(..., help="Relative path to file")):
    """Check lock status."""
    mgr = get_lock_manager()
    info = mgr.check_lock(path)
    if info:
        typer.echo(f"🔒 Locked by {info.owner} (Expires: {info.expires_at})")
        raise typer.Exit(code=1) # Exit 1 to indicate "Locked" to scripts
    else:
        typer.echo(f"🟢 Free: {path}")

@app.command("clear")
def clear_locks(force: bool = typer.Option(False, "--force", help="Force clear all locks")):
    """Clear all locks (Emergency)."""
    if not force:
        typer.confirm("Are you sure you want to clear ALL locks?", abort=True)
    
    mgr = get_lock_manager()
    mgr.clear_all()
    typer.echo("🧹 All locks cleared.")
