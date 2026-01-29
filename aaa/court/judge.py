import json
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.panel import Panel
from rich.markdown import Markdown
from aaa.court.schema import CaseFile, Ruling
from aaa.court.clerk import CourtClerk

console = Console()

class CourtJudge:
    def __init__(self, clerk: CourtClerk):
        self.clerk = clerk

    def conduct_session(self, case_id: str, human_id: str = "judge-001"):
        """Host an interactive court session."""
        case = self.clerk.get_case(case_id)
        if not case:
            console.print(f"[bold red]Case {case_id} not found![/bold red]")
            return

        self._display_docket(case)
        self._take_ruling(case, human_id)

    def _display_docket(self, case: CaseFile):
        console.clear()
        console.rule(f"[bold yellow]SUPREME COURT OF AI ASSETS[/bold yellow]")
        
        # Header
        console.print(f"Case ID: [cyan]{case.case_id}[/cyan]")
        console.print(f"Plaintiff: [green]{case.plaintiff}[/green]")
        console.print(f"Status: {case.status.value}")
        console.print(f"Submitted: {case.submitted_at}")
        
        console.rule("[bold]EVIDENCE & FACTS[/bold]")
        
        # Formatted Facts (JSON or Markdown)
        facts_json = json.dumps(case.facts, indent=2)
        syntax = Syntax(facts_json, "json", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Case Facts", expand=False))

    def _take_ruling(self, case: CaseFile, judge_id: str):
        console.rule("[bold]VERDICT[/bold]")
        console.print("How do you rule?")
        console.print("[green](y) Approve[/green]: Grant request as stated.")
        console.print("[red](n) Deny[/red]: Reject request.")
        console.print("[yellow](m) Modify[/yellow]: Approve with modifications.")
        console.print("[magenta](w) Waive[/magenta]: Grant special exemption (Rule Breaking).")

        choice = Prompt.ask("Enter verdict", choices=["y", "n", "m", "w"], default="y")

        ruling_map = {
            "y": Ruling.APPROVE,
            "n": Ruling.DENY,
            "m": Ruling.MODIFY,
            "w": Ruling.WAIVE
        }
        ruling = ruling_map[choice]
        
        reasoning = Prompt.ask("Enter judicial reasoning")
        
        # Confirm
        console.print(f"\n[bold]Preview Verdict[/bold]:")
        console.print(f"Ruling: {ruling.value}")
        console.print(f"Reasoning: {reasoning}")
        
        if Confirm.ask("Seal this verdict?", default=True):
            updated_case = self.clerk.apply_ruling(case.case_id, ruling, reasoning, judge_id)
            console.print(f"\n[bold green]Verdict Sealed.[/bold green] Case {updated_case.case_id} is now {updated_case.status.value}.")
        else:
            console.print("[yellow]Verdict discarded.[/yellow]")
