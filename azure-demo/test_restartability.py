"""Check repeatable local verification without taking another application's port.

Run: uv run --locked --project python python azure-demo/test_restartability.py
No cloud requests, model calls, or generated host configuration changes are made.
"""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

from verify_demo import local_backend


def exit_before_ready(listener, key):
    """Simulate a child failing before it can accept a health request."""
    raise SystemExit(23)


class RestartabilityTests(unittest.TestCase):
    """Exercise process and socket ownership rather than merely checking helper calls."""

    def test_parallel_runs_with_old_port_occupied(self):
        """A busy former fixed port must not affect concurrent independent checks."""
        with socket.socket() as unrelated, tempfile.TemporaryDirectory() as directory:
            try:
                unrelated.bind(("127.0.0.1", 8765))
                unrelated.listen()
            except OSError:
                # An existing application is equally valid contention; leave it alone.
                pass

            def run(number):
                output = Path(directory) / f"result-{number}.json"
                result = subprocess.run(
                    [sys.executable, str(Path(__file__).with_name("verify_demo.py")),
                     "--local", "--output", str(output)],
                    capture_output=True, text=True, timeout=45,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue(json.loads(output.read_text())["passed"])

            with ThreadPoolExecutor(max_workers=2) as executor:
                list(executor.map(run, (1, 2)))
            if unrelated.getsockname()[1] == 8765:
                # Our unrelated listener must still belong to us after both child exits.
                with socket.create_connection(("127.0.0.1", 8765), timeout=1):
                    pass

    def test_repeated_starts_release_owned_listener(self):
        """Each context exits with its child reaped and listening socket closed."""
        for _ in range(2):
            with local_backend() as (backend, _key):
                port = urlsplit(backend).port
                with socket.create_connection(("127.0.0.1", port), timeout=1):
                    pass
            with socket.socket() as probe:
                probe.settimeout(1)
                self.assertNotEqual(probe.connect_ex(("127.0.0.1", port)), 0)

    def test_startup_failure_is_explicit(self):
        """An exited child cannot be mistaken for a ready unrelated service."""
        with patch("verify_demo.serve_local", exit_before_ready):
            with self.assertRaisesRegex(RuntimeError, "exited during startup.*23"):
                with local_backend():
                    self.fail("A failed child must not yield a backend")


if __name__ == "__main__":
    unittest.main()
