"""Regression checks for retry-safe memory writes and owned stdio process cleanup.

Run with: uv run --locked --project python python scripts/Test-RetrySafety.py
Uses temporary databases and disposable child processes; never touches live hosts.
"""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import importlib.util
from pathlib import Path
import queue
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    """Load the shipped modules so regression tests exercise their real cleanup."""
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


memory = load("course_memory", "memory/memory_demo.py")
protocol = load("course_protocol", "verify_protocol.py")


class RetrySafety(unittest.TestCase):
    """Repeated writes preserve transitions, and failures leave no owned server."""
    def test_concurrent_retries_and_atomic_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "incident.db"
            with closing(memory.connect(database)):
                pass
            with ThreadPoolExecutor(max_workers=6) as workers:
                list(workers.map(lambda _: memory.write_note(database, "session", "Timeouts"), range(12)))
            self.assertEqual(len(memory.snapshot(database, "session")["episodic"]), 1)
            memory.write_note(database, "session", "Recovery")
            memory.write_note(database, "session", "Timeouts")
            self.assertEqual(len(memory.snapshot(database, "session")["episodic"]), 3)
            with closing(sqlite3.connect(database)) as db:
                db.execute("CREATE TRIGGER reject_event BEFORE INSERT ON episodic BEGIN SELECT RAISE(ABORT, 'fixture'); END")
                db.commit()
            with self.assertRaises(sqlite3.IntegrityError):
                memory.write_note(database, "session", "Uncommitted")
            self.assertEqual(memory.snapshot(database, "session")["working"][0]["note"], "Timeouts")
            self.assertEqual(memory.snapshot(database, "other")["episodic"], [])
            # Windows refuses this deletion if an application connection remains open.
            database.unlink()

    def check_owned_exit(self, source, expected, interrupt=False):
        children = []
        original = subprocess.Popen
        def start(*args, **kwargs):
            child = original(*args, **kwargs)
            children.append(child)
            return child
        with patch.object(protocol.subprocess, "Popen", side_effect=start):
            if interrupt:
                with patch.object(queue.Queue, "get", side_effect=KeyboardInterrupt):
                    with self.assertRaises(expected):
                        protocol.check("fixture", [sys.executable, "-u", "-c", source])
            else:
                with self.assertRaises(expected):
                    protocol.check("fixture", [sys.executable, "-u", "-c", source])
        self.assertEqual(len(children), 1)
        self.assertIsNotNone(children[0].poll())
        self.assertTrue(all(stream.closed for stream in (children[0].stdin, children[0].stdout, children[0].stderr)))

    def test_malformed_response_cleanup(self):
        self.check_owned_exit("import sys,time; sys.stdin.readline(); print('invalid', flush=True); time.sleep(30)", ValueError)

    def test_early_eof_cleanup(self):
        self.check_owned_exit("import sys; sys.stdin.readline()", RuntimeError)

    def test_keyboard_interrupt_cleanup(self):
        self.check_owned_exit("import time; time.sleep(30)", KeyboardInterrupt, interrupt=True)


if __name__ == "__main__":
    unittest.main()
