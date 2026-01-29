import typer
from rich.console import Console
from pathlib import Path
from aaa.os.kernel import AgentKernel
from aaa.trust.verifier import TrustVerifier

app = typer.Typer(no_args_is_help=True)
console = Console()

@app.command("boot")
def boot_kernel():
    """Initialize the Agent OS Kernel."""
    kernel = AgentKernel(Path.cwd())
    status = kernel.boot()
    
    console.print("[bold green]Agent OS Kernel Booted.[/bold green]")
    console.print_json(data=status)

@app.command("status")
def system_status():
    """Show OS Status."""
    boot_kernel()

# Trust Sub-commands
trust_app = typer.Typer(no_args_is_help=True)
app.add_typer(trust_app, name="trust")

@trust_app.command("verify")
def verify_trust(repo_url: str, signature: str):
    """Verify a remote repository signature."""
    verifier = TrustVerifier(Path.cwd())
    if verifier.verify_repo(repo_url, signature):
        console.print(f"[green]TRUST VERIFIED[/green]: {repo_url}")
    else:
        console.print(f"[red]TRUST FAILED[/red]: {repo_url}")

# Cert Sub-commands
cert_app = typer.Typer(no_args_is_help=True)
app.add_typer(cert_app, name="cert")

@cert_app.command("status")
def cert_status():
    """Check Enterprise Certification Status."""
    verifier = TrustVerifier(Path.cwd())
    status = verifier.get_certification_status(Path.cwd())
    console.print_json(data=status)
