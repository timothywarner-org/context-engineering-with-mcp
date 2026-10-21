"""Verify real stdio RPC traffic against both starters, including current-protocol discovery.

This process-level check is independent of any AI host, account, or model response.
It deliberately checks both success and failure paths before the example is taught.
"""
from __future__ import annotations
import json
import time
from pathlib import Path
import subprocess
import sys
import queue
import threading

ROOT = Path(__file__).parent.resolve()
META = {"io.modelcontextprotocol/protocolVersion":"2026-07-28", "io.modelcontextprotocol/clientCapabilities":{}, "io.modelcontextprotocol/clientInfo":{"name":"course-verification","version":"1.0"}}


def check(name: str, command: list[str]) -> dict:
    """Read complete RPC results and report only instructional evidence, never environment data."""
    calls = [
        ("server/discover", {}),
        ("tools/list", {}),
        ("tools/call", {"name":"get_incident","arguments":{"incident_id":" inc-1042 "}}),
        ("resources/read", {"uri":"warnerco://runbooks/order-api"}),
        ("prompts/get", {"name":"investigate_incident","arguments":{"incident_id":"INC-1042"}}),
        ("tools/call", {"name":"get_incident","arguments":{"incident_id":"MISSING"}}),
    ]
    requests = [json.dumps({"jsonrpc":"2.0","id":i,"method":method,"params":{**params,"_meta":META}}) for i,(method,params) in enumerate(calls,1)]
    # Keep stdin open until each reply arrives; EOF may cancel in-flight SDK tasks.
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=ROOT, bufsize=1)
    inbox: queue.Queue[str | None] = queue.Queue()
    def read_stdout() -> None:
        try:
            for line in process.stdout: inbox.put(line)
        finally:
            inbox.put(None)
    def read_stderr() -> None:
        # Drain diagnostics to avoid a full pipe without retaining arbitrary server output.
        for _ in process.stderr: pass
    readers = [threading.Thread(target=reader, daemon=True) for reader in (read_stdout, read_stderr)]
    for reader in readers: reader.start()
    results = {}
    try:
        for expected_id,request in enumerate(requests,1):
            process.stdin.write(request+"\n")
            process.stdin.flush()
            deadline = time.monotonic() + 20
            while expected_id not in results:
                # Notifications must not extend a missing response's deadline indefinitely.
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise RuntimeError(f"{name}: timed out waiting for reply {expected_id}.")
                try: line = inbox.get(timeout=remaining)
                except queue.Empty as exc: raise RuntimeError(f"{name}: timed out waiting for reply {expected_id}.") from exc
                if line is None:
                    raise RuntimeError(f"{name}: server closed stdout before reply {expected_id}.")
                message = json.loads(line)
                if "id" in message: results[message["id"]] = message
    finally:
        # EOF gives the owned server a graceful exit; escalation never targets other processes.
        try:
            process.stdin.close()
        except (BrokenPipeError, OSError):
            pass
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
        finally:
            for reader in readers: reader.join(timeout=3)
            process.stdout.close()
            process.stderr.close()
    if len(results) != len(calls): raise AssertionError(f"{name}: expected {len(calls)} results, got {results}")
    for i in range(1,6):
        if "error" in results[i]: raise AssertionError(f"{name} {calls[i-1][0]}: {results[i]}")
    assert "2026-07-28" in json.dumps(results[1]), results[1]
    assert "get_incident" in json.dumps(results[2]), results[2]
    assert "Priya Patel" in json.dumps(results[3]), results[3]
    assert "request approval before rollback" in json.dumps(results[4]), results[4]
    assert "Separate observed facts from hypotheses" in json.dumps(results[5]), results[5]
    assert results[6].get("result",{}).get("isError") is True, results[6]
    return {"language":name,"protocol":"2026-07-28","checks":len(calls),"result":"PASS","responses":results}


def main() -> None:
    """Exercise shipped files, not test-only copies of the implementation."""
    # Reuse the activated locked environment, avoiding a wrapper that can orphan its child.
    commands = [("Python", [sys.executable,str(ROOT/"python/server.py")]),("TypeScript",["node",str(ROOT/"typescript/dist/server.js")])]
    reports = [check(name,command) for name,command in commands]
    path=ROOT/"protocol-evidence.json"
    path.write_text(json.dumps(reports,indent=2),encoding="utf-8")
    for report in reports: print(f"PASS {report['language']}: discovery, list, normalized lookup, resource, prompt, unknown-ID error")


if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt:
        raise SystemExit(130)
    except (OSError, ValueError, RuntimeError, AssertionError, subprocess.SubprocessError) as exc:
        raise SystemExit(f"Protocol verification failed: {exc}") from exc
