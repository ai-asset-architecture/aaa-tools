import typer
from pathlib import Path
from typing import Optional
from aaa.compiler.menu_v2 import compile_menu
from aaa.jsonl import emit_jsonl

app = typer.Typer(no_args_is_help=True)

@app.command("compile")
def compile_registry(
    source: Path = typer.Option(..., "--source", help="Path to AAA_MENU.md"),
    output: Optional[Path] = typer.Option(None, "--output", help="Output path (defaults to registry_index.v2.json next to source)"),
    jsonl: bool = typer.Option(False, "--jsonl"),
):
    """Compile a Markdown Menu into a JSON Registry."""
    command = "aaa registry compile"
    step_id = "compile_menu"
    emit_jsonl(jsonl, event="start", status="start", command=command, step_id=step_id)
    
    if not source.exists():
        msg = f"Source file not found: {source}"
        emit_jsonl(jsonl, event="error", status="error", command=command, step_id=step_id, message=msg)
        raise typer.Exit(1)
        
    if output is None:
        output = source.parent / "registry_index.v2.json"
        
    try:
        compile_menu(source, output)
        emit_jsonl(jsonl, event="result", status="ok", command=command, step_id=step_id, data={"output": str(output)})
        if not jsonl:
            print(f"✅ Registry compiled to: {output}")
    except Exception as e:
        emit_jsonl(jsonl, event="error", status="error", command=command, step_id=step_id, message=str(e))
        raise typer.Exit(1)
