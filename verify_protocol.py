"""Verify real stdio RPC traffic against both starters, including current-protocol discovery.

This process-level check is independent of any AI host, account, or model response.
It deliberately checks both success and failure paths before the example is taught.
"""
from __future__ import annotations
import json
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
    inbox: queue.Queue[str] = queue.Queue()
    diagnostics: list[str] = []
    def read_stdout() -> None:
        for line in process.stdout: inbox.put(line)
    def read_stderr() -> None:
        for line in process.stderr: diagnostics.append(line)
    threading.Thread(target=read_stdout,daemon=True).start()
    threading.Thread(target=read_stderr,daemon=True).start()
    results = {}
    try:
        for expected_id,request in enumerate(requests,1):
            process.stdin.write(request+"\n")
            process.stdin.flush()
            while expected_id not in results:
                try: message = json.loads(inbox.get(timeout=20))
                except queue.Empty as exc: raise RuntimeError(f"{name}: timed out waiting for reply {expected_id}. {''.join(diagnostics)[-800:]}") from exc
                if "id" in message: results[message["id"]] = message
    finally:
        process.stdin.close()
        try: process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=3)
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
    commands = [("Python", ["uv","run","--project",str(ROOT/"python"),"python",str(ROOT/"python/server.py")]),("TypeScript",["node",str(ROOT/"typescript/dist/server.js")])]
    reports = [check(name,command) for name,command in commands]
    path=ROOT/"protocol-evidence.json"
    path.write_text(json.dumps(reports,indent=2),encoding="utf-8")
    for report in reports: print(f"PASS {report['language']}: discovery, list, normalized lookup, resource, prompt, unknown-ID error")


if __name__ == "__main__":
    try: main()
    except (OSError, ValueError, RuntimeError, AssertionError, subprocess.SubprocessError) as exc:
        raise SystemExit(f"Protocol verification failed: {exc}") from exc
