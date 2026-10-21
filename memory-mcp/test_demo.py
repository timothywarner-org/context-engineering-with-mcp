"""Safety regressions for rehearsal data-path selection; no host store is touched."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("memory_demo", Path(__file__).with_name("demo.py"))
demo = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(demo)

class DemoPathTests(unittest.TestCase):
    def test_default_runs_share_temporary_store_and_never_host_store(self):
        calls = []
        def capture(command, **kwargs):
            path = Path(command[command.index("--memory-path") + 1])
            self.assertTrue(path.is_absolute())
            self.assertTrue(path.parent.is_dir())
            calls.append(path)
        with patch.object(demo.sys, "argv", ["demo.py"]), patch.object(demo.subprocess, "run", capture):
            demo.main()
            demo.main()
        self.assertEqual(calls[0], calls[1])
        self.assertEqual(calls[2], calls[3])
        self.assertNotEqual(calls[0], calls[2])
        for path in calls:
            self.assertNotEqual(path, demo.ROOT / ".local/memory/warnerco.json")
            self.assertFalse(path.parent.exists())

    def test_split_phase_requires_path_before_launching_anything(self):
        for phase in ("write", "retrieve"):
            with self.subTest(phase=phase), patch.object(demo.sys, "argv", ["demo.py", "--phase", phase]):
                with patch.object(demo.subprocess, "run") as launch, self.assertRaises(SystemExit):
                    demo.main()
                launch.assert_not_called()

    def test_explicit_store_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Path(directory) / "chosen.json"
            store.write_text("sentinel", encoding="utf-8")
            with patch.object(demo.sys, "argv", ["demo.py", "--memory-path", str(store)]):
                with patch.object(demo.subprocess, "run") as launch:
                    demo.main()
            self.assertEqual(launch.call_count, 2)
            for call in launch.call_args_list:
                command = call.args[0]
                self.assertEqual(command[command.index("--memory-path") + 1], str(store))
            self.assertEqual(store.read_text(encoding="utf-8"), "sentinel")

if __name__ == "__main__":
    unittest.main()
