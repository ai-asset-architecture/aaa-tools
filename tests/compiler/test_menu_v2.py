import json
from pathlib import Path
from aaa.compiler.menu_v2 import _parse_archetypes_table, _parse_packs_list

SAMPLE_MENU = """
# AAA Menu

## 1. Archetypes
| **Name** | Description | Includes Packs | Recommended Evals |
| :--- | :--- | :--- | :--- |
| **Backend Service** | API Service | `core-governance`, `api-standards` | `lint-openapi` |
| **Shared Library** | Lib | `core-governance` | |

## 2. A la Carte Packs

### 🛡️ Agent Safety (`agent-safety`)
- [x] **Sandbox**: Filesystem sandbox
- [ ] **Network**: No internet

### 🏛️ Core Governance (`core-governance`)
- [x] Readme
"""

def test_parse_archetypes():
    archetypes = _parse_archetypes_table(SAMPLE_MENU)
    assert "backend-service" in archetypes
    assert archetypes["backend-service"]["display_name"] == "Backend Service"
    assert "api-standards" in archetypes["backend-service"]["inherited_packs"]
    assert "lint-openapi" in archetypes["backend-service"]["recommended_evals"]
    
    assert "shared-library" in archetypes
    assert archetypes["shared-library"]["inherited_packs"] == ["core-governance"]
    assert archetypes["shared-library"]["recommended_evals"] == []

def test_parse_packs():
    packs = _parse_packs_list(SAMPLE_MENU)
    assert "agent-safety" in packs
    assert "Sandbox: Filesystem sandbox" in packs["agent-safety"]["capabilities"]
    assert "Network: No internet" not in packs["agent-safety"]["capabilities"] # Unchecked
    assert "core-governance" in packs
    assert "Readme" in packs["core-governance"]["capabilities"]
