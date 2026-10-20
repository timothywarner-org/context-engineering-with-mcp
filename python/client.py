"""Call the WARNERCO server with the official MCP SDK, without a model or API key.

From the repository root: uv run --project python python python/client.py
The SDK starts and closes the existing server as a separate stdio process.
"""
import asyncio
from pathlib import Path
import sys

from mcp import Client, StdioServerParameters
from mcp.types import TextContent, TextResourceContents


async def main() -> None:
    """Discover a tool, retrieve incident evidence, and inspect a deliberate failure."""
    # Reuse this interpreter and an absolute path so another working directory is safe.
    server = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).resolve().with_name("server.py"))],
    )
    # The SDK owns discovery, protocol messages, and subprocess cleanup.
    async with Client(server, read_timeout_seconds=10) as client:
        print(f"Connected over stdio. Protocol: {client.protocol_version}")
        tools = await client.list_tools()
        print("Tools: " + ", ".join(tool.name for tool in tools.tools))

        incident = await client.call_tool("get_incident", {"incident_id": "INC-1042"})
        if incident.is_error:
            raise RuntimeError("The known incident returned a tool error")
        print("\nIncident result:")
        for block in incident.content:
            if isinstance(block, TextContent):
                print(block.text)

        runbook = await client.read_resource("warnerco://runbooks/order-api")
        print("\nApproved runbook:")
        for contents in runbook.contents:
            if isinstance(contents, TextResourceContents):
                print(contents.text)

        # A tool error is a returned result; a broken connection is a separate failure.
        missing = await client.call_tool("get_incident", {"incident_id": "MISSING"})
        if not missing.is_error:
            raise RuntimeError("The missing incident should return a tool error")
        print(f"\nUnknown incident: is_error={missing.is_error}")
        for block in missing.content:
            if isinstance(block, TextContent):
                print(block.text)


if __name__ == "__main__":
    try:
        # Bound the whole demonstration as well as individual requests during live delivery.
        asyncio.run(asyncio.wait_for(main(), timeout=30))
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        # SDK transport failures can arrive as exception groups at this CLI boundary.
        print(f"Client demo failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
