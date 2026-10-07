"""Four memory roles, real persistence, and a repeatable process-boundary demonstration.

Borrowed teaching design: Tim Warner's WARNERCO Schematica scratchpad, event log,
durable facts, and versioned procedures. This bounded reference app uses SQLite
and lexical retrieval, not embeddings. A shared local file proves a process boundary,
not a distributed database. Production replicas require a suitable shared service.

Examples:
  python memory_demo.py demo
  python memory_demo.py inspect --database ./data/incident.db
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

PROCEDURE = {"version": "1.0", "steps": ["Read incident facts", "Inspect the approved runbook", "Compare instances", "Request approval before changes"]}


def connect(path: Path) -> sqlite3.Connection:
    """Initialize repeatably; primary keys prevent duplicate seed data on later runs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=10)
    db.row_factory = sqlite3.Row
    db.executescript("""
    CREATE TABLE IF NOT EXISTS working(scope TEXT NOT NULL, topic TEXT NOT NULL, note TEXT NOT NULL, PRIMARY KEY(scope,topic));
    CREATE TABLE IF NOT EXISTS episodic(id INTEGER PRIMARY KEY, scope TEXT NOT NULL, occurred TEXT NOT NULL, summary TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS facts(id TEXT PRIMARY KEY, statement TEXT NOT NULL, source TEXT NOT NULL);
    """)
    db.execute("INSERT OR IGNORE INTO facts VALUES (?,?,?)", ("FACT-01", "Order API timeouts can follow exhausted connection pools.", "Fictional WARNERCO runbook v1"))
    db.commit()
    return db


def snapshot(path: Path, scope: str) -> dict:
    """Retrieve selected evidence explicitly; saving a record never inserts it into context."""
    with connect(path) as db:
        working = [dict(row) for row in db.execute("SELECT topic,note FROM working WHERE scope=?", (scope,))]
        events = [dict(row) for row in db.execute("SELECT occurred,summary FROM episodic WHERE scope=? ORDER BY id DESC LIMIT 3", (scope,))]
        facts = [dict(row) for row in db.execute("SELECT * FROM facts WHERE statement LIKE ?", ("%connection%",))]
    return {"scope":scope, "working":working, "episodic":events, "semantic":facts, "procedural":PROCEDURE, "retrieval":"Lexical lookup over durable facts; no embedding model"}


def write_note(path: Path, scope: str, note: str) -> None:
    """Persist a current observation and append its event atomically."""
    if not scope.strip() or not note.strip():
        raise ValueError("Scope and note must be nonempty")
    with connect(path) as db:
        db.execute("INSERT INTO working VALUES (?,?,?) ON CONFLICT(scope,topic) DO UPDATE SET note=excluded.note", (scope, "INC-1042", note))
        db.execute("INSERT INTO episodic(scope,occurred,summary) VALUES (?,?,?)", (scope, datetime.now(timezone.utc).isoformat(), "Observed: " + note))


def child(*args: str) -> str:
    """A new interpreter makes the process boundary observable, not simulated."""
    result = subprocess.run([sys.executable, str(Path(__file__).resolve()), *args], capture_output=True, text=True, timeout=15, check=True)
    return result.stdout.strip()


def demo() -> None:
    """Use an isolated temporary database so rehearsal never alters an existing session."""
    with tempfile.TemporaryDirectory(prefix="warnerco-memory-") as directory:
        path = str(Path(directory) / "incident.db")
        print("1. Process A writes process-local memory:", child("local-write"))
        print("2. Fresh process B reads process-local memory:", child("local-read"))
        print("3. Process A writes a durable note:", child("write", "--database", path, "--note", "Timeouts began after the deployment"))
        evidence = json.loads(child("inspect", "--database", path))
        assert evidence["working"][0]["note"] == "Timeouts began after the deployment"
        print("4. Fresh process B retrieves all four roles:")
        print(json.dumps(evidence, indent=2))
        other = json.loads(child("inspect", "--database", path, "--scope", "another-session"))
        assert other["working"] == [] and other["episodic"] == []
        print("PASS: the stored note survived a new process; another scope has no session notes.")
        print("Scope is an application filter, not authentication. Authorize the caller before selecting a scope.")


def main() -> None:
    """Provide small commands that can be inspected individually during a screencast."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["demo", "write", "inspect", "local-write", "local-read"])
    parser.add_argument("--database", type=Path, default=Path(__file__).parent / "data/incident.db")
    parser.add_argument("--scope", default="class-demo")
    parser.add_argument("--note", default="Timeouts began after the deployment")
    args = parser.parse_args()
    if args.action == "demo": demo()
    elif args.action == "write":
        write_note(args.database, args.scope, args.note)
        print("Committed note and event")
    elif args.action == "inspect": print(json.dumps(snapshot(args.database, args.scope), indent=2))
    elif args.action == "local-write":
        local = {"INC-1042": args.note}
        print(local["INC-1042"])
    else:
        local = {}
        print(local.get("INC-1042", "No note in this fresh process"))


if __name__ == "__main__":
    try: main()
    except (sqlite3.Error, OSError, ValueError, subprocess.SubprocessError) as exc:
        raise SystemExit(f"Memory demonstration failed: {exc}") from exc
