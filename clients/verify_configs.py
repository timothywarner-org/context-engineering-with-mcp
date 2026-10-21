"""Validate generated snippets by launching the named servers from an unrelated directory.

This checks configuration and protocol behavior, not a model host's interactive UI.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path
import tempfile
from mcp import Client, StdioServerParameters

ROOT = Path(__file__).resolve().parents[1]

def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)

async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=ROOT/"clients/generated")
    parser.add_argument("--python-only", action="store_true")
    args = parser.parse_args()
    expected = {"warnerco-incidents"} if args.python_only else {"warnerco-incidents","warnerco-memory"}
    canonical = None
    for name in ("vscode-mcp.json","claude-code.mcp.json","claude-desktop.json","copilot-mcp.json","inspector.json"):
        config = json.loads((args.directory/name).read_text(encoding="utf-8-sig"))
        entries = config["servers" if name == "vscode-mcp.json" else "mcpServers"]
        require(set(entries) == expected, name + ": wrong server names")
        normalized = {}
        for server_name, entry in entries.items():
            require(Path(entry["command"]).is_absolute(), name + ": executable must be absolute")
            require(Path(entry["args"][-1]).is_absolute(), name + ": script must be absolute")
            if name == "inspector.json":
                require(entry.get("protocolEra") == "modern", "Inspector era missing")
            else:
                require("protocolEra" not in entry and entry.get("type") == "stdio",
                        "Host schema or Inspector setting leak")
            normalized[server_name] = {key:value for key,value in entry.items() if key not in ("type","protocolEra")}
            if server_name == "warnerco-memory":
                require(Path(entry["env"]["WARNERCO_MEMORY_PATH"]).is_absolute(), "Memory path must be absolute")
        if canonical is None:
            canonical = normalized
        require(normalized == canonical, "Launch settings diverge between host snippets: " + name)
    require(canonical is not None, "No configs")
    # Avoid writes: call lookup/search only, using the actual generated launch entries.
    os.chdir(tempfile.gettempdir())
    for name, entry in canonical.items():
        server = StdioServerParameters(command=entry["command"],args=entry["args"],
            env={**os.environ, **entry.get("env",{})})
        async with Client(server, read_timeout_seconds=15) as client:
            tools = await client.list_tools()
            names = {tool.name for tool in tools.tools}
            require(names == ({"get_incident"} if name == "warnerco-incidents" else
                    {"memory_write","memory_search","memory_compress"}), "Wrong discovered tools")
            result = await client.call_tool("get_incident" if name == "warnerco-incidents" else "memory_search",
                {"incident_id":"INC-1042"} if name == "warnerco-incidents" else {"query":"MISSING-9876 unicorn"})
            require(not result.is_error, "Generated config tool call failed")
        print("PASS generated configuration: " + name)
    print("PASS five snippet formats agree; no installed host settings were changed.")

if __name__ == "__main__":
    asyncio.run(asyncio.wait_for(main(), timeout=60))
