"""Serve the course incident through independently routed MCP endpoints.

Run with the existing locked course environment. All records are fictional.
Three SDK servers share one container so the routing lesson stays inexpensive.
"""

from contextlib import AsyncExitStack, asynccontextmanager
import hmac
import os

from mcp.server import MCPServer
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
import uvicorn


def create_server(route: str) -> MCPServer:
    """Keep discovery separate from the endpoints permitted to execute a tool."""
    server = MCPServer(name="warnerco-classroom", version="1.0.0")

    if route in ("catalog", "incidents"):
        @server.tool()
        def get_incident(incident_id: str) -> dict:
            """Read the owner and symptom of a fictional WARNERCO incident."""
            # Returning the executing route makes backend selection observable.
            if route != "incidents":
                raise ValueError("Incident execution requires the incidents route")
            if incident_id.strip().upper() != "INC-1042":
                raise ValueError("Unknown incident")
            return {
                "id": "INC-1042",
                "owner": "Priya Patel",
                "service": "Order API",
                "symptom": "Timeouts after a deployment",
                "servedBy": "incidents",
            }

    if route in ("catalog", "runbooks"):
        @server.tool()
        def get_runbook(service: str = "Order API") -> dict:
            """Read the approved investigation steps for a fictional service."""
            if route != "runbooks":
                raise ValueError("Runbook execution requires the runbooks route")
            if service.casefold() != "order api":
                raise ValueError("Unknown service")
            return {
                "service": "Order API",
                "steps": [
                    "Confirm the deployment time",
                    "Inspect request failures",
                    "Compare healthy and failing instances",
                    "Request approval before rollback",
                ],
                "servedBy": "runbooks",
            }

    if route == "catalog":
        @server.tool()
        def request_rollback(incident_id: str) -> dict:
            """Teaching fixture for an operation the gateway must deny."""
            # This fixture cannot change a system, even if the gateway is misconfigured.
            raise ValueError("Rollback is disabled in the teaching server")

    return server


servers = {name: create_server(name) for name in ("catalog", "incidents", "runbooks")}
http_apps = {
    name: server.streamable_http_app(
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
        host="0.0.0.0",
    )
    for name, server in servers.items()
}


@asynccontextmanager
async def lifespan(app):
    """Start all SDK transport managers when the outer ASGI application starts."""
    async with AsyncExitStack() as stack:
        for server in servers.values():
            await stack.enter_async_context(server.session_manager.run())
        yield


async def health(request):
    """Expose only process health to Container Apps probes."""
    return JSONResponse({"status": "ok", "service": "warnerco-classroom"})


class BackendKeyMiddleware:
    """Require the gateway's independent credential on every MCP backend path."""

    def __init__(self, app):
        self.app = app
        self.key = os.environ.get("WARNERCO_BACKEND_KEY", "")
        if len(self.key) < 32:
            raise RuntimeError("WARNERCO_BACKEND_KEY must contain at least 32 characters")

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"] != "/health":
            headers = dict(scope.get("headers", []))
            candidate = headers.get(b"x-warnerco-backend-key", b"")
            if not hmac.compare_digest(candidate, self.key.encode()):
                await JSONResponse(
                    {"error": "Gateway backend credential required"}, status_code=401
                )(scope, receive, send)
                return
        await self.app(scope, receive, send)


app = BackendKeyMiddleware(
    Starlette(
        lifespan=lifespan,
        routes=[Route("/health", health)]
        + [Mount(f"/{name}", application) for name, application in http_apps.items()],
    )
)


if __name__ == "__main__":
    # ACA terminates TLS; only the container's internal listener uses plain HTTP.
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
