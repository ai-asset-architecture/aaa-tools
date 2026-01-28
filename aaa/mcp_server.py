try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    # Fallback for environments without mcp-sdk
    class FastMCP:
        def __init__(self, name: str):
            self.name = name
        def tool(self):
            def decorator(func):
                return func
            return decorator
        def run(self):
            print(f"MCP Server {self.name} is not available: mcp-sdk-python not installed.")

from pathlib import Path
from . import check_commands
from . import output_formatter

mcp = FastMCP("AAA Governance Server")

@mcp.tool()
def aaa_check(path: str = ".") -> str:
    """
    Run AAA governance checks for the specified repository path.
    Returns LLM-optimized semantic diagnostic information.
    """
    repo_path = Path(path).resolve()
    raw_result = check_commands.run_blocking_check(repo_path)
    semantic_result = output_formatter.enrich_result("check", raw_result)
    formatter = output_formatter.get_formatter("llm")
    return formatter.format(semantic_result)

@mcp.tool()
def aaa_audit(path: str = ".") -> str:
    """
    Generate a governance audit report for the specified repository path.
    """
    from . import audit_commands
    repo_path = Path(path).resolve()
    raw_result = audit_commands.run_local_audit(repo_path)
    semantic_result = output_formatter.enrich_result("audit", raw_result)
    formatter = output_formatter.get_formatter("llm")
    return formatter.format(semantic_result)

if __name__ == "__main__":
    mcp.run()
