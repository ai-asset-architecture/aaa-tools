import typer
import time
import sqlite3
import json
from rich.console import Console
from rich.table import Table
from aaa.observability.custom_metrics import MetricStore
from aaa.observability.ledger import RiskLedger

app = typer.Typer(no_args_is_help=True)
console = Console()

@app.command("trends")
def show_trends(
    metric: str = typer.Argument(..., help="Metric name to visualize"),
    days: int = typer.Option(7, "--days", "-d", help="Number of days to look back")
):
    """Visualize metric trends (ASCII Chart)."""
    store = MetricStore()
    cutoff = time.time() - (days * 24 * 3600)
    
    conn = sqlite3.connect(store.db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp, value FROM metrics WHERE metric_name = ? AND timestamp > ? ORDER BY timestamp ASC",
        (metric, cutoff)
    )
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        console.print(f"[yellow]No data found for metric '{metric}' in last {days} days.[/yellow]")
        return
        
    console.print(f"[bold blue]Trend for {metric} ({days} days)[/bold blue]")
    
    # Simple ASCII Sparkline logic
    values = [r[1] for r in rows]
    min_v, max_v = min(values), max(values)
    
    # Draw Table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Time", style="dim")
    table.add_column("Value")
    table.add_column("Bar")
    
    for ts, val in rows:
        local_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))
        
        # ASCII Bar
        if max_v == min_v:
            bar = "█" * 10
        else:
            percent = (val - min_v) / (max_v - min_v)
            bar_len = int(percent * 20)
            bar = "█" * bar_len
        
        table.add_row(local_time, str(val), bar)
        
    console.print(table)

@app.command("ledger")
def show_ledger(limit: int = typer.Option(10, "--limit", "-n", help="Number of events to show")):
    """Show Risk Ledger events."""
    ledger = RiskLedger()
    
    conn = sqlite3.connect(ledger.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, event_type, severity, description, actor, hash FROM ledger ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    table = Table(title="Risk Ledger (Tamper-Evident log)", show_header=True)
    table.add_column("Time", style="dim")
    table.add_column("Type", style="cyan")
    table.add_column("Sev", style="red")
    table.add_column("Description")
    table.add_column("Actor")
    table.add_column("Hash (Partial)", style="dim")
    
    for ts, evt, sev, desc, actor, h_val in rows:
        local_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))
        table.add_row(local_time, evt, sev, desc, actor, h_val[:8]+"...")
        
    console.print(table)
