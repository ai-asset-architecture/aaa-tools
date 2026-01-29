import pytest
from aaa.engine.ruleset import InheritanceMerger

class TestInheritanceMerger:
    def test_deep_merge_simple_dict(self):
        """Test simple dictionary merging."""
        parent = {"a": 1, "b": 2}
        child = {"b": 3, "c": 4}
        merger = InheritanceMerger()
        result = merger.merge(parent, child)
        
        # Expect child to override b, preserve a, and add c
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_deep_merge_nested_dict(self):
        """Test valid nested dictionary merging."""
        parent = {
            "governance": {
                "threshold": 0.8,
                "mode": "strict"
            }
        }
        child = {
            "governance": {
                "threshold": 0.9
            }
        }
        merger = InheritanceMerger()
        result = merger.merge(parent, child)
        
        # Expect deep merge: threshold updated, mode preserved
        assert result == {
            "governance": {
                "threshold": 0.9,
                "mode": "strict"
            }
        }

    def test_list_behavior_replace(self):
        """Test that lists are replaced, not appended (Atomicity)."""
        parent = {"allowed_licenses": ["MIT"]}
        child = {"allowed_licenses": ["Apache-2.0"]}
        merger = InheritanceMerger()
        result = merger.merge(parent, child)
        
        # Expect atomic replacement
        assert result == {"allowed_licenses": ["Apache-2.0"]}

    def test_type_mismatch_override(self):
        """Test that type mismatch results in correct override."""
        parent = {"config": {"key": "value"}}
        child = {"config": "override_string"}
        merger = InheritanceMerger()
        result = merger.merge(parent, child)
        
        # Child scalar should overwrite parent dict
        assert result == {"config": "override_string"}

    def test_none_handling(self):
        """Test handling of None inputs."""
        merger = InheritanceMerger()
        
        # Parent None -> return Child
        assert merger.merge(None, {"a": 1}) == {"a": 1}
        
        # Child None -> return Parent
        assert merger.merge({"a": 1}, None) == {"a": 1}
        
        # Both None -> return empty dict
        assert merger.merge(None, None) == {}
