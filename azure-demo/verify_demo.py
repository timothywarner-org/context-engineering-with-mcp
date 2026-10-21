"""Verify the actual backend routes and gateway decisions, without model calls.

Run with --local for a subprocess smoke test, or set WARNERCO_GATEWAY_URL,
WARNERCO_APIM_KEY, and WARNERCO_BACKEND_URL for the deployed gateway.
Only fictional incident data and sanitized results are written to the report.
"""

import argparse
import asyncio
from contextlib import ExitStack, contextmanager, redirect_stderr, redirect_stdout
from datetime import datetime, timezone
import json
import multiprocessing
import os
from pathlib import Path
import secrets
import socket
import sys
import time

# Reuse the HTTP client already pinned by the course's MCP SDK.
import httpx2 as httpx
from mcp import Client
from mcp.client.streamable_http import streamable_http_client


def serve_local(listener: socket.socket, key: str) -> None:
    """Run the real ASGI app on a socket already reserved by this test process."""
    # Spawn keeps the per-run credential out of the parent environment and other runs.
    os.environ["WARNERCO_BACKEND_KEY"] = key
    with open(os.devnull, "w") as sink, redirect_stdout(sink), redirect_stderr(sink):
        import uvicorn
        from server import app
        server = uvicorn.Server(uvicorn.Config(app, log_level="critical", access_log=False))
        server.run(sockets=[listener])


def stop_owned_process(process, timeout: float = 5) -> None:
    """Reap only this invocation's child, with bounded escalation if it stalls."""
    if process.is_alive():
        process.terminate()
    process.join(timeout)
    if process.is_alive():
        process.kill()
        process.join(timeout)
    if process.is_alive():
        raise RuntimeError("Local verification child did not stop after termination and kill")
    process.close()


@contextmanager
def local_backend():
    """Reserve a loopback port without a probe/rebind race and verify child startup."""
    key = secrets.token_hex(32)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        # Keep ownership of the OS-assigned socket throughout startup and verification.
        # Passing it through spawn works on Windows and Linux without racing a rebind.
        listener.bind(("127.0.0.1", 0))
        listener.listen(128)
        backend = f"http://127.0.0.1:{listener.getsockname()[1]}"
        process = multiprocessing.get_context("spawn").Process(
            target=serve_local, args=(listener, key), name="warnerco-local-verification"
        )
        process.start()
        try:
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                if not process.is_alive():
                    raise RuntimeError(f"Local verification child exited during startup ({process.exitcode})")
                try:
                    response = httpx.get(backend + "/health", timeout=0.5)
                    if (response.status_code == 200 and response.json() ==
                            {"status": "ok", "service": "warnerco-classroom"}):
                        break
                except (httpx.HTTPError, ValueError):
                    pass
                time.sleep(0.1)
            else:
                raise RuntimeError("Local verification child was not ready within 15 seconds")
            yield backend, key
        finally:
            stop_owned_process(process)


async def sdk_check(url: str, headers: dict):
    """Exercise SDK protocol negotiation and a real tool invocation through APIM."""
    async with httpx.AsyncClient(headers=headers, timeout=45) as http:
        # The SDK owns discovery and transport framing; credentials remain in memory.
        async with Client(
            streamable_http_client(url, http_client=http), read_timeout_seconds=45
        ) as client:
            tools = await client.list_tools()
            names = sorted(tool.name for tool in tools.tools)
            assert names == ["get_incident", "get_runbook", "request_rollback"]
            incident = await client.call_tool("get_incident", {"incident_id": "INC-1042"})
            assert not incident.is_error
            data = json.loads(incident.content[0].text)
            assert data["servedBy"] == "incidents" and data["owner"] == "Priya Patel"
            return {"protocol": client.protocol_version, "tools": names, "incident": data}


def call(url: str, method: str, params: dict, headers: dict | None = None):
    """Use a self-contained MCP request and retain status and routing evidence."""
    # The old protocol era is explicit so a native gateway's compatibility can be tested.
    response = httpx.post(
        url,
        headers={"Accept": "application/json, text/event-stream",
                 "MCP-Protocol-Version": "2025-06-18", **(headers or {})},
        json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
        timeout=45,
    )
    text = response.text
    if "data: " in text:
        text = next(line[6:] for line in text.splitlines() if line.startswith("data: "))
    try:
        body = json.loads(text)
    except json.JSONDecodeError:
        body = {"text": text[:300]}
    return {
        "status": response.status_code,
        "route": response.headers.get("x-warnerco-route"),
        "policy": response.headers.get("x-warnerco-policy"),
        "retryAfter": response.headers.get("retry-after"),
        "body": body,
    }


def structured(result):
    """Extract the SDK's structured tool result, keeping failures distinguishable."""
    rpc = result["body"].get("result", {})
    if rpc.get("isError"):
        raise AssertionError(f"Unexpected tool error: {rpc}")
    if "structuredContent" in rpc:
        return rpc["structuredContent"]
    return json.loads(rpc["content"][0]["text"])


def main():
    """Fail the run if any claimed route or enforcement outcome is unobserved."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    local_session = ExitStack()
    started = time.monotonic()
    report = {"verifiedAt": datetime.now(timezone.utc).isoformat(), "passed": False}
    try:
        if args.local:
            backend, key = local_session.enter_context(local_backend())
            headers = {"X-Warnerco-Backend-Key": key}
            report["direct_without_key"] = call(backend + "/catalog/mcp", "tools/list", {})
            assert report["direct_without_key"]["status"] == 401
            report["catalog"] = call(backend + "/catalog/mcp", "tools/list", {}, headers)
            assert {tool["name"] for tool in report["catalog"]["body"]["result"]["tools"]} == {
                "get_incident", "get_runbook", "request_rollback"
            }
            report["incident"] = call(backend + "/incidents/mcp", "tools/call", {
                "name": "get_incident", "arguments": {"incident_id": "INC-1042"}
            }, headers)
            assert structured(report["incident"])["servedBy"] == "incidents"
            assert structured(report["incident"])["owner"] == "Priya Patel"
            report["runbook"] = call(backend + "/runbooks/mcp", "tools/call", {
                "name": "get_runbook", "arguments": {}
            }, headers)
            assert structured(report["runbook"])["servedBy"] == "runbooks"
            report["wrong_route"] = call(backend + "/runbooks/mcp", "tools/call", {
                "name": "get_incident", "arguments": {"incident_id": "INC-1042"}
            }, headers)
            assert (report["wrong_route"]["body"].get("error") or
                    report["wrong_route"]["body"].get("result", {}).get("isError"))
            # Discovery exposes definitions, but it must never execute routed work or rollback.
            for label, method, name in (
                ("catalog_execution_denied", "tools/call", "get_incident"),
                ("rollback_fixture_denied", "tools/call", "request_rollback"),
                ("unknown_method_denied", "tools/execute", "get_incident"),
            ):
                report[label] = call(backend + "/catalog/mcp", method, {
                    "name": name, "arguments": {"incident_id": "INC-1042"}
                }, headers)
                assert (report[label]["body"].get("error") or
                        report[label]["body"].get("result", {}).get("isError"))
        else:
            gateway = os.environ["WARNERCO_GATEWAY_URL"]
            backend = os.environ["WARNERCO_BACKEND_URL"]
            headers = {"Ocp-Apim-Subscription-Key": os.environ["WARNERCO_APIM_KEY"]}
            report["gateway_without_key"] = call(gateway, "tools/list", {})
            assert report["gateway_without_key"]["status"] == 401
            report["direct_without_key"] = call(backend + "/incidents/mcp", "tools/call", {
                "name": "get_incident", "arguments": {"incident_id": "INC-1042"}
            })
            assert report["direct_without_key"]["status"] == 401
            report["catalog"] = call(gateway, "tools/list", {}, headers)
            assert report["catalog"]["status"] == 200
            assert {tool["name"] for tool in report["catalog"]["body"]["result"]["tools"]} == {
                "get_incident", "get_runbook", "request_rollback"
            }
            report["incident"] = call(gateway, "tools/call", {
                "name": "get_incident", "arguments": {"incident_id": "INC-1042"}
            }, headers)
            assert structured(report["incident"])["servedBy"] == "incidents"
            assert structured(report["incident"])["owner"] == "Priya Patel"
            assert report["incident"]["route"] == "incidents"
            report["sdk"] = asyncio.run(asyncio.wait_for(sdk_check(gateway, headers), timeout=90))
            report["spoofed_route"] = call(gateway, "tools/call", {
                "name": "get_incident", "arguments": {"incident_id": "INC-1042"}
            }, {**headers, "X-Warnerco-Route": "runbooks", "X-Warnerco-Backend-Key": "caller-value"})
            assert structured(report["spoofed_route"])["servedBy"] == "incidents"
            assert report["spoofed_route"]["route"] == "incidents"
            report["rollback_denied"] = call(gateway, "tools/call", {
                "name": "request_rollback", "arguments": {"incident_id": "INC-1042"}
            }, headers)
            assert report["rollback_denied"]["status"] == 403
            assert report["rollback_denied"]["policy"] == "tool-allowlist-denied"
            # Distributed counters are approximate. Require an observed 429, not an exact ordinal.
            for number in range(1, 13):
                result = call(gateway, "tools/call", {
                    "name": "get_runbook", "arguments": {}
                }, headers)
                report[f"runbook_{number}"] = result
                if result["status"] == 429:
                    assert number > 1, "Throttle window is still active. Wait 60 seconds before rerunning."
                    assert result["retryAfter"]
                    break
                assert structured(result)["servedBy"] == "runbooks"
                assert result["route"] == "runbooks"
                time.sleep(0.5)
            else:
                raise AssertionError("No runbook throttle observed within 12 calls")
            report["incident_after_throttle"] = call(gateway, "tools/call", {
                "name": "get_incident", "arguments": {"incident_id": "INC-1042"}
            }, headers)
            assert structured(report["incident_after_throttle"])["servedBy"] == "incidents"
        report["passed"] = True
        for name, result in report.items():
            if isinstance(result, dict):
                print(f"PASS {name}: HTTP {result.get('status', 'SDK')} "
                      f"route={result.get('route') or result.get('protocol') or '-'}")
    finally:
        local_session.close()
        # Preserve command evidence without turning a machine measurement into a presenter rehearsal.
        report["verificationSeconds"] = round(time.monotonic() - started, 2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
