import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

@dataclass
class Archetype:
    name: str
    description: str
    includes_packs: List[str]
    recommended_evals: List[str]

@dataclass
class Pack:
    name: str
    capabilities: List[str]

def _parse_archetypes_table(content: str) -> Dict[str, Any]:
    """Parse the Archetypes markdown table."""
    archetypes = {}
    
    # Regex to find the table rows under ## 1. Archetypes
    # Matches: | **Name** | Description | `pack1`, `pack2` | `eval1` |
    # Assumes standard GFM table format
    
    # 1. Isolate the section
    section_match = re.search(r"## .*Archetypes.*?(?:\|---|---).*?\n((?:\|.*\|\n)+)", content, re.DOTALL | re.IGNORECASE)
    if not section_match:
        return {}
    
    table_body = section_match.group(1)
    
    for line in table_body.strip().splitlines():
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 4:
            continue
            
        name_raw = parts[0] # **Backend Service**
        desc = parts[1]
        packs_raw = parts[2]
        evals_raw = parts[3]
        
        # Clean name: **Backend Service** -> backend-service (slugified for key)
        # But we want to keep Display Name too.
        display_name = name_raw.replace("*", "").strip()
        slug = display_name.lower().replace(" ", "-")
        
        # Parse Lists: `core-governance`, `api-standards`
        packs = [p.strip(" `") for p in packs_raw.split(",")]
        packs = [p for p in packs if p] # filter empty
        
        evals = [e.strip(" `") for e in evals_raw.split(",")]
        evals = [e for e in evals if e]
        
        archetypes[slug] = {
            "display_name": display_name,
            "description": desc,
            "inherited_packs": packs,
            "recommended_evals": evals
        }
        
    return archetypes

def _parse_packs_list(content: str) -> Dict[str, Any]:
    """Parse the Packs lists."""
    packs = {}
    
    # Find section "## 2. A la Carte Packs"
    section_match = re.search(r"## .*Packs.*?\n(.*?)(?=\n## |$)", content, re.DOTALL | re.IGNORECASE)
    if not section_match:
        return {}
        
    section_body = section_match.group(1)
    
    # Find h3 headers for packs: ### 🛡️ Agent Safety (`agent-safety`)
    pack_sections = re.split(r"(^### .*$)", section_body, flags=re.MULTILINE)
    
    current_pack_id = None
    
    for chunk in pack_sections:
        chunk = chunk.strip()
        if not chunk:
            continue
            
        # Check if header
        header_match = re.match(r"### .*`([^`]+)`.*", chunk)
        if header_match:
            current_pack_id = header_match.group(1)
            packs[current_pack_id] = {"capabilities": [], "source": ""} # Source hard to parse from MD unless structured, defaulting
            continue
            
        if current_pack_id and chunk.startswith("- ["):
            # Parse checkbox items: - [x] **Sandbox**: Prevents...
            for line in chunk.splitlines():
                cap_match = re.match(r"- \[[ xX]\].*?\*\*(.*?)\*\*: (.*)", line)
                if cap_match:
                    rule_name = cap_match.group(1)
                    desc = cap_match.group(2)
                    packs[current_pack_id]["capabilities"].append(f"{rule_name}: {desc}")
                else:
                    # Simple item
                    simple_match = re.match(r"- \[[ xX]\].*?(.*)", line)
                    if simple_match:
                         packs[current_pack_id]["capabilities"].append(simple_match.group(1).strip())
                         
        # Try to infer source if known convention or placeholder
        if current_pack_id:
             packs[current_pack_id]["source"] = f"github:ai-asset-architecture/aaa-packs//{current_pack_id}"

    return packs

def compile_menu(source_path: Path, output_path: Path) -> None:
    """Read markdown menu and write JSON registry."""
    if not source_path.exists():
        raise FileNotFoundError(f"Menu file not found: {source_path}")
        
    content = source_path.read_text(encoding="utf-8")
    
    archetypes = _parse_archetypes_table(content)
    packs = _parse_packs_list(content)
    
    registry = {
        "schema_version": "2.0",
        "min_cli_version": "1.5.0",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "comment": "Generated from AAA_MENU.md by aaa registry compile",
        "object_types": archetypes,
        "packs": packs
    }
    
    output_path.write_text(json.dumps(registry, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
