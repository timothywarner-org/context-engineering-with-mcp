"""WARNERCO incident lookup on the official MCP Python SDK.

Run with uv run python server.py. All incident data is a fictional teaching fixture.
The small interface lets the learner verify the protocol independently of a model.
"""
import sys
from typing import Annotated

from mcp.server import MCPServer
from mcp.types import ToolAnnotations
from pydantic import Field

mcp = MCPServer(name="warnerco-incidents", version="1.0.0")
INCIDENTS = {"INC-1042": {"id": "INC-1042", "owner": "Priya Patel", "service": "Order API", "status": "Investigating", "symptom": "Timeouts after a deployment"}}


# Field metadata reaches MCP discovery, so Inspector shows guidance beside the input.
IncidentId = Annotated[
    str,
    Field(
        description="Fictional incident ID. Try INC-1042.",
        examples=["INC-1042"],
    ),
]


# These hints describe this fixture; they do not replace a host's authorization checks.
@mcp.tool(
    title="Incident facts: look up INC-1042",
    annotations=ToolAnnotations(
        readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False
    ),
)
def get_incident(incident_id: IncidentId) -> dict:
    """Retrieve incident facts that the assistant can use as evidence.

    Try incident_id="INC-1042" in Inspector. Expect Priya Patel, Order API,
    Investigating, and Timeouts after a deployment. Try "MISSING" to see an
    explicit tool error instead of invented facts. Input ignores case and spaces.

    This read-only lookup uses fictional data held in this process. It does not
    query a live ticketing system, retrieve memory, or perform a rollback.
    """
    # Normalizing once makes ordinary user input tolerant without hiding missing records.
    key = incident_id.strip().upper()
    if key not in INCIDENTS:
        raise ValueError(f"Unknown incident: {key}")
    return INCIDENTS[key].copy()


@mcp.resource(
    "warnerco://runbooks/order-api",
    title="Order API runbook: investigation procedure",
    mime_type="text/plain",
)
def order_api_runbook() -> str:
    """Read reference context for investigating the fictional Order API incident.

    In Inspector, read warnerco://runbooks/order-api; no arguments are needed.
    Pair it with incident INC-1042. Expect a procedure ending with a requirement
    to request approval before rollback. This is guidance, not evidence that any
    check or rollback has occurred. The host chooses whether to include it in
    the assistant's next context; reading it does not create persistent memory.
    """
    return "Confirm the deployment time; inspect request failures; compare healthy and failing instances; request approval before rollback."


@mcp.prompt(title="Investigate an incident using evidence")
def investigate_incident(incident_id: IncidentId = "INC-1042") -> str:
    """Prepare an investigation request with an explicit evidence boundary.

    Try incident_id="INC-1042" in Inspector, or omit it to use that default.
    Expect a user message asking for incident facts, the Order API runbook,
    facts-versus-hypotheses separation, and approval before changes.

    Getting this prompt only returns instructions. It does not call the tool,
    read the resource, retrieve stored observations, or assemble a context packet.
    """
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
