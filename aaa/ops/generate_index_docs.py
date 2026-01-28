import json
from pathlib import Path

def generate_internal_readme(workspace_root: Path):
    index_path = workspace_root / "internal" / "index.json"
    readme_path = workspace_root / "internal/development/README.md"
    
    if not index_path.exists():
        print(f"Index file not found: {index_path}")
        return
    
    try:
        data = json.loads(index_path.read_text())
    except Exception as e:
        print(f"Error reading index.json: {e}")
        return
    
    milestones = data.get("milestones", [])
    
    content = [
        "# AAA Internal Development Navigator",
        "",
        "> **Notice**: This document is auto-generated from `internal/index.json` (SSOT).",
        "",
        "## 🎯 Asset Catalogs",
        "",
        "| Asset Type | Catalog Guide | Source of Truth |",
        "|------------|---------------|-----------------|",
        "| **Runbooks** | [Runbook Catalog](../docs/references/runbook-catalog.md) | `aaa-tools/runbooks/` |",
        "| **Evals** | [Evals Catalog](../docs/references/evals-catalog.md) | `aaa-evals/evals/` |",
        "| **Templates** | [Templates Catalog](../docs/references/templates-catalog.md) | `aaa-tpl-docs/templates/` |",
        "| **Prompts** | [Prompts Catalog](../docs/references/prompts-catalog.md) | `aaa-prompts/prompts/` |",
        "| **Packs** | [Packs Catalog](../docs/references/packs-catalog.md) | `ai-asset-architecture-registry` |",
        "| **Checks** | [Checks Catalog](../docs/references/checks-catalog.md) | `aaa-tools/aaa/check_commands.py` |",
        "",
        "## 🏗️ Active Milestones",
        "",
        "| ID | Planning | Completion Report | Status |",
        "|----|----------|-------------------|--------|",
    ]
    
    for mid in milestones:
        # Check for standard paths
        plan_path = f"milestones/{mid}/PRD.md"
        report_path = f"../reports/milestones/{mid}_report.md" # Hypothetical standard
        
        content.append(f"| **{mid}** | [Plan]({plan_path}) | [Report]({report_path}) | Active |")
    
    content.append("")
    content.append("---")
    content.append("## 📜 Policies")
    content.append("- [Test Coverage Policy](./policies/test-coverage-policy.md)")
    content.append("")
    content.append(f"**Last Sync**: {Path.cwd()}") # Placeholder for real timestamp logic if needed
    
    readme_path.parent.mkdir(parents=True, exist_ok=True)
    readme_path.write_text("\n".join(content))
    print(f"Generated {readme_path}")

if __name__ == "__main__":
    # Test execution
    generate_internal_readme(Path.cwd().parent / "aaa-tpl-docs")
