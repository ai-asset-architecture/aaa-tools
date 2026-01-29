import unittest

from aaa import action_registry


class TestActionRegistry(unittest.TestCase):
    def test_registry_executes_handler(self):
        registry = action_registry.ActionRegistry()
        registry.register("notify", lambda args: {"ok": True}, scopes=["notify:send"])
        result = registry.execute("notify", {"message": "hi"}, allowed_scopes=["notify:send"])
        self.assertEqual(result, {"ok": True})

    def test_registry_blocks_missing_scope(self):
        registry = action_registry.ActionRegistry()
        registry.register("fs_write", lambda args: {"ok": True}, scopes=["fs:write"])
        with self.assertRaises(action_registry.RuntimeSecurityError):
            registry.execute("fs_write", {"path": "/tmp/a"}, allowed_scopes=[])


if __name__ == "__main__":
    unittest.main()
