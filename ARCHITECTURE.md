# Architecture gallery

Open [ARCHITECTURE.html](ARCHITECTURE.html) for the offline, full-screen gallery.
Every diagram uses a 16:9 canvas, large text, and labeled blue, purple and amber
paths. Color is never the only way to distinguish a connection or outcome.

| View | Scalable artwork | 4K image | Main idea |
|---|---|---|---|
| 01. Host, clients and servers | [SVG](ARCHITECTURE-01-mcp.svg) | [PNG](ARCHITECTURE-01-mcp.png) | MCP exposes capabilities; the host assembles model context. |
| 02. Persistence and reuse | [SVG](ARCHITECTURE-02-memory.svg) | [PNG](ARCHITECTURE-02-memory.png) | A file survives the process; useful context must be retrieved and included again. |
| 03. Azure routing and access | [SVG](ARCHITECTURE-03-azure.svg) | [PNG](ARCHITECTURE-03-azure.png) | APIM routes to three endpoints in one Container Apps container. |

## Read the diagrams accurately

### 01. Host, clients and servers

The host owns model integration, context selection and connection permissions.
Each MCP client communicates with one server. The two incident starters are
alternative implementations, while memory is a separate server. The first
Python client demonstration invokes no model. The model in this diagram belongs
to the later host-driven workflow.

Tools, resources and prompts are distinct capabilities. The incident tool returns
facts, the runbook resource supplies reference material, and the prompt provides
task instructions. The memory server exposes three tools, with no resources or
prompts in this example. A successful connection alone supplies neither durable
memory nor permission to execute an action.

Implementation: [Python server](python/server.py), [TypeScript server](typescript/src/server.ts),
[model-free client](python/client.py), and [memory reference](memory-mcp/README.md).

### 02. Persistence and explicit reuse

The memory tools write and read a local JSON store. Both processes must resolve
the same absolute path. The standalone demonstration uses an isolated temporary
store by default and proves retrieval after the writer exits. It then prepares
a request file for explicit reuse in a new host conversation.

Search is deterministic keyword matching. Compression selects and truncates;
it does not produce an LLM summary. The budget counts UTF-16 units in the returned
context field, not model tokens or the full RPC response. Inspect truncation and
preserve important qualifications such as the rollback approval requirement.

Implementation: [memory demonstration](memory-mcp/demo.py) and
[memory behavior and limits](memory-mcp/README.md).

### 03. Azure routing and access

APIM authenticates the caller with an API subscription key. It forwards a
different credential to the backend. The request body selects the route, so a
caller-supplied routing hint cannot choose a different endpoint. `servedBy` in
the tool result identifies the executing endpoint; `X-Warnerco-Route` identifies
the gateway's route decision.

The runbook rate limit is approximate and distributed. The policy configures
two calls per 60 seconds; a particular numbered call is not guaranteed to fail.
Rollback is a non-mutating fixture that is refused at both gateway and server.
The diagram shows the implemented key-based demo. OAuth consent, per-user RBAC
and private networking are separate design extensions.

Implementation: [Azure supplement](azure-demo/README.md),
[gateway policy](azure-demo/policy.xml), and [server](azure-demo/server.py).

## Sources and icon attribution

- [MCP architecture specification, 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/architecture).
- [Microsoft Azure architecture icon terms](https://learn.microsoft.com/en-us/azure/architecture/icons/).
- [Official APIM SVG](https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/media/index/api-management.svg), source blob `7124f682bc67bbffab35f4b35e52c69d691cbafe`.
- [Official Container Apps SVG](https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/media/index/container-apps.svg), source blob `0cf1d6ac651c6b90ab57b1a7578667faac2b38cd`.

Microsoft owns the Azure product icons. Their use here is for architecture
documentation under Microsoft's icon terms. The supplied artwork is embedded
without cropping, rotation, recoloring or distortion, and is labeled with the
corresponding product name. The icons are not relicensed under this repository's
code license.

## Edit and rebuild

Run `python scripts/Build-Architecture.py` to regenerate the SVGs and HTML gallery.
The generator uses only Python's standard library. The included PNGs are rendered
at 3840 x 2160; re-export them from the SVGs after changing the artwork.
No diagram-generation dependencies are required to run the course examples.
