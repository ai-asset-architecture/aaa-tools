import typer
import json
import sys
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from aaa.court.clerk import CourtClerk
from aaa.court.judge import CourtJudge
from aaa.court.schema import CaseFile

app = typer.Typer(no_args_is_help=True)
console = Console()

@app.command("file")
def file_case(
    facts: str = typer.Argument(..., help="JSON string or path to JSON file containing facts"),
    plaintiff: str = typer.Option("CLI-User", help="Name of the plaintiff agent")
):
    """File a new case with the Supreme Court."""
    clerk = CourtClerk()
    
    # Parse facts
    try:
        if Path(facts).exists():
            data = json.loads(Path(facts).read_text())
        else:
            data = json.loads(facts)
    except json.JSONDecodeError:
        console.print("[bold red]Error: Invalid JSON facts.[/bold red]")
        raise typer.Exit(code=1)
    
    case_id = clerk.file_case(plaintiff, data)
    console.print(f"[green]Case Filed Successfully.[/green] ID: [bold cyan]{case_id}[/bold cyan]")
    console.print("Wait for adjudication.")

@app.command("docket")
def view_docket():
    """List pending cases."""
    clerk = CourtClerk()
    cases = clerk.list_pending_cases()
    
    if not cases:
        console.print("[yellow]No pending cases.[/yellow]")
        return
        
    table = Table(title="Supreme Court Docket")
    table.add_column("ID", style="cyan")
    table.add_column("Plaintiff", style="green")
    table.add_column("Submitted", style="dim")
    table.add_column("Preview")
    
    for case in cases:
        # Preview facts
        preview = json.dumps(case.facts)[:50] + "..."
        table.add_row(case.case_id[:8], case.plaintiff, str(case.submitted_at), preview)
        
    console.print(table)

@app.command("rule")
def rule_case(
    case_id: str = typer.Argument(..., help="Case ID (or prefix)"),
    judge_handle: str = typer.Option("Honorable-User", help="Judge ID")
):
    """Open interactive session to rule on a case."""
    clerk = CourtClerk()
    
    # Support partial ID lookup logic could go here, but strict for now
    # Actually, let's support prefix matching if simple
    target_id = case_id
    if len(case_id) < 36:
        # Simple prefix match
        matches = [c for c in clerk.list_pending_cases() if c.case_id.startswith(case_id)]
        if len(matches) == 1:
            target_id = matches[0].case_id
        elif len(matches) > 1:
            console.print(f"[red]Ambiguous ID prefix '{case_id}'. Matches found: {len(matches)}[/red]")
            return
        # If 0 matches, let get_case fail gracefully in judge
    
    judge = CourtJudge(clerk)
    judge.conduct_session(target_id, human_id=judge_handle)
