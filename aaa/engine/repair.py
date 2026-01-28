import ast
import shutil
from pathlib import Path
from typing import Callable, Optional, Tuple

class FixResult:
    def __init__(self, success: bool, changed: bool, message: str):
        self.success = success
        self.changed = changed
        self.message = message

class AutoFixEngine:
    """
    Zone Zero Component: Safely applies fixes to files with Circuit Breaker logic.
    Target Coverage: 100%
    """
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries

    def apply_fix(self, file_path: Path, fixer: Callable[[str], str]) -> FixResult:
        """
        Apply a fix function to a file with rollback protection.
        
        Args:
            file_path: Path to the file to fix.
            fixer: A function that takes file content (str) and returns fixed content (str).
            
        Returns:
            FixResult indicating success/failure and change status.
        """
        if not file_path.exists():
            return FixResult(False, False, f"File not found: {file_path}")

        original_content = file_path.read_text(encoding='utf-8')
        
        # 1. Circuit Breaker Loop
        for attempt in range(1, self.max_retries + 1):
            try:
                # 2. Apply Fix
                new_content = fixer(original_content)
                
                if new_content == original_content:
                    return FixResult(True, False, "No changes needed")
                
                # 3. Write Candidate
                file_path.write_text(new_content, encoding='utf-8')
                
                # 4. Stability Check
                if self._check_stability(file_path):
                    return FixResult(True, True, "Fix applied and verified")
                else:
                    # Unstable, rollback
                    file_path.write_text(original_content, encoding='utf-8')
                    if attempt == self.max_retries:
                         return FixResult(False, False, "Fix introduced syntax errors (Rollback applied)")
                         
            except Exception as e:
                # Runtime error during fix, rollback
                file_path.write_text(original_content, encoding='utf-8')
                return FixResult(False, False, f"Exception during fix: {str(e)}")
                
        return FixResult(False, False, "Max retries exceeded")

    def _check_stability(self, file_path: Path) -> bool:
        """
        Verify file stability (e.g., syntax check for Python).
        """
        if file_path.suffix == '.py':
            try:
                ast.parse(file_path.read_text(encoding='utf-8'))
                return True
            except SyntaxError:
                return False
        # For non-code files, assume stable if written successfully
        return True
