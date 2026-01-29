from typing import Any, Dict, Optional, List

class InheritanceMerger:
    """
    Handles merging of governance rulesets with Inheritance strategy.
    Strategy: Deep Merge for Dictionaries, Atomic Replacement for Lists/Scalars.
    """
    
    def merge(self, parent: Optional[Dict[str, Any]], child: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge parent and child rulesets. 
        Child overrides parent.
        """
        if parent is None:
            return child if child is not None else {}
        if child is None:
            return parent
            
        return self._deep_merge(parent, child)

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursive deep merge implementation.
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Both are dicts -> Recurse
                result[key] = self._deep_merge(result[key], value)
            else:
                # Otherwise -> Overwrite (atomic replacement for lists, scalars, or type mismatches)
                result[key] = value
                
        return result
