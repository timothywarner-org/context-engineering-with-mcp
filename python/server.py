"""WARNERCO incident lookup on the official MCP Python SDK.

Run with uv run python server.py. All incident data is a fictional teaching fixture.
The small interface lets the learner verify the protocol independently of a model.
"""
import sys
from mcp.server import MCPServer  # docs form; mcp.server.mcpserver also works

mcp = MCPServer(name="warnerco-incidents", version="1.0.0")
INCIDENTS = {"INC-1042": {"id": "INC-1042", "owner": "Priya Patel", "service": "Order API", "status": "Investigating", "symptom": "Timeouts after a deployment"}}


@mcp.tool()
def get_incident(incident_id: str) -> dict:
    """Look up a WARNERCO incident by ID. This operation is read-only."""
    # Normalizing once makes ordinary user input tolerant without hiding missing records.
    key = incident_id.strip().upper()
    if key not in INCIDENTS:
        raise ValueError(f"Unknown incident: {key}")
    return INCIDENTS[key].copy()


@mcp.resource("warnerco://runbooks/order-api")
def order_api_runbook() -> str:
    """Return the approved investigation procedure as URI-addressed context."""
    return "Confirm the deployment time; inspect request failures; compare healthy and failing instances; request approval before rollback."


@mcp.prompt()
def investigate_incident(incident_id: str = "INC-1042") -> str:
    """Prepare an evidence-first investigation request for the user to invoke."""
    return f"Investigate {incident_id}. Read the incident and order-api runbook. Separate observed facts from hypotheses. Recommend the next check; request approval before changes."


if __name__ == "__main__":
    try:
        # Protocol bytes own stdout; diagnostics belong on stderr.
        print("WARNERCO incident server listening on stdio", file=sys.stderr)
        mcp.run()
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print(f"Server stopped: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
