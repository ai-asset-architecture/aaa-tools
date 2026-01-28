import os
import json
import datetime
import subprocess
from pathlib import Path
from typing import Any, Dict

def get_git_author() -> str:
    try:
        result = subprocess.run(
            ["git", "config", "user.name"], 
            capture_output=True, 
            text=True, 
            check=False
        )
        return result.stdout.strip() or "Unknown Author"
    except Exception:
        return "Unknown Author"

def init_milestone(milestone_id: str, workspace_root: Path) -> Dict[str, Any]:
    milestone_dir = workspace_root / "internal/development/milestones" / milestone_id
    
    # 1. Idempotency Check
    if milestone_dir.exists():
        return {
            "status": "skipped_or_warned",
            "message": f"Milestone directory {milestone_id} already exists."
        }
    
    try:
        # 2. Directory Creation
        milestone_dir.mkdir(parents=True)
        
        # 3. Template Copying & Context Injection
        template_path = workspace_root / "templates" / "PRD-template.md"
        target_path = milestone_dir / "PRD.md"
        
        if template_path.exists():
            content = template_path.read_text()
            
            # Inject context
            author = get_git_author()
            today = datetime.date.today().isoformat()
            
            content = content.replace("<AUTHOR>", author)
            content = content.replace("<DATE>", today)
            content = content.replace("<STATUS>", "Draft")
            
            target_path.write_text(content)
        
        # 4. Registration to index.json (SSOT)
        index_path = workspace_root / "internal" / "index.json"
        index_data = {"milestones": []}
        
        if index_path.exists():
            try:
                index_data = json.loads(index_path.read_text())
            except json.JSONDecodeError:
                pass
        else:
            index_path.parent.mkdir(parents=True, exist_ok=True)
            
        if milestone_id not in index_data.get("milestones", []):
            if "milestones" not in index_data:
                index_data["milestones"] = []
            index_data["milestones"].append(milestone_id)
            index_path.write_text(json.dumps(index_data, indent=2))
            
        return {
            "status": "success",
            "message": f"Milestone {milestone_id} initialized successfully."
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
