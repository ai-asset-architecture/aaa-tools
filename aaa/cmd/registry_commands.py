import typer
from pathlib import Path
from typing import List, Optional
from aaa.registry.client import RegistryClient, RegistryClientError
from aaa.output_formatter import OutputFormatter, SemanticResult

app = typer.Typer()

# TODO: Inject this from global config in real app
DEFAULT_REGISTRY_PATH = Path("ai-asset-architecture-registry/registry_index.json")

@app.command("query")
def query_registry(
    terms: List[str] = typer.Argument(..., help="Keywords or phrases to search for capability"),
    registry: Path = typer.Option(DEFAULT_REGISTRY_PATH, help="Path to registry index"),
    format: str = typer.Option("human", help="Output format: human, json, llm")
):
    """
    Query the registry for packs with specific capabilities.
    """
    # formatter = OutputFormatter(format) # Unused in this initial version, using inline logic below
    
    try:
        client = RegistryClient(registry)
        results = client.query_capabilities(terms)
        
        if not results:
            typer.echo("No matching packs found.")
            raise typer.Exit(0)

        # Map to Semantic Result for LLM/JSON/Human output
        # For simplicity, just printing here, but ideally constructing SemanticResult
        
        if format == "human":
            typer.echo(f"Found {len(results)} matches:\n")
            for res in results:
                pack_id = res['pack_id']
                score = res['score']
                caps = ", ".join(res['matched_capabilities'])
                typer.echo(f"- {pack_id} (Score: {score})")
                typer.echo(f"  Matches: {caps}\n")
        
        elif format == "json":
            import json
            typer.echo(json.dumps(results, indent=2))
            
        elif format == "llm":
            typer.echo(f"### Registery Query Results\n")
            typer.echo(f"**Query**: {terms}\n")
            for res in results:
                typer.echo(f"- **{res['pack_id']}**")
                typer.echo(f"  - Relevance Score: {res['score']}")
                typer.echo(f"  - Capabilities: {res['matched_capabilities']}")

    except RegistryClientError as e:
        typer.echo(f"Registry Error: {e}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
