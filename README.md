# Context Engineering with MCP

Tim Warner | Pearson Enterprise Live Training | October 22, 2026

**Start here. This is the canonical learner and demo repository for this session.**
Use this same checkout during the demonstration and for practice afterward. You
don't need another course repository to complete the examples.

**Attending live?** Tim runs every demo on screen. Participate through predictions,
polls, chat, and the worksheet; installing tools is optional. Get the slide PDF,
participant worksheet, and links PDF from your Pearson session's **Resources** widget.

**Practicing afterward?** Start with [your first successful tool call](#optional-preparation),
then follow the learning route below. The first example needs no model account,
API key, Node.js installation, or Azure subscription.

## Learning route

Follow one fictional incident, **INC-1042**, from a context problem through tool use,
durable memory, and access decisions. All business data is fictional.

| Step | Open or run | What you should be able to explain |
|---|---|---|
| 1. Choose useful context | [Context audit](#context-audit-and-governance-practice) | What the assistant needs, what adds noise, and which measurements are real. |
| 2. Call a tool and read a resource | [Python client](#call-the-server-from-python) | How a client gets incident data and a runbook, including a deliberate failure. |
| 3. Inspect the exchange | [MCP Inspector](#inspect-the-server) | The difference between discovering a capability and successfully using it. |
| 4. Connect your preferred host | [Host configuration](#connect-a-host) | How a host launches the same server and obtains consent. One host is enough for practice. |
| 5. Carry context across processes | [Memory demonstration](#understand-the-memory-demonstration) | What survives a process exit and why storage alone doesn't supply model context. |
| 6. Decide who may do what | [Governance exercise](#context-audit-and-governance-practice) | Where token, scope, and data-access decisions belong. |
| Optional extension | [Azure gateway demonstration](#explore-the-azure-gateway-demonstration) | How routing, denial, and throttling affect real requests. |

## What is in this repository

- `python/`: official MCP Python SDK 2.3.0 starter, pinned with `uv.lock`.
- `python/client.py`: small SDK client that calls the existing server without a model or API key.
- `typescript/`: official TypeScript SDK server 2.3.1 starter, pinned with `package-lock.json`.
- `memory/memory_demo.py`: working, episodic, semantic, and procedural memory example.
- `clients/New-ClientConfigs.ps1`: portable configuration generator for three hosts and Inspector.
- `context/`: small and large fictional incident files for the context audit.
- `governance/request-review.json`: remote authorization and gateway decision exercise.
- [`azure-demo/`](azure-demo/README.md): the optional Azure Container Apps and API Management supplement, with tool-specific routes, denial, and throttling.
- Slides, participant worksheet, and links PDF: in the Resources widget for your Pearson session.
- `evidence/`: dated reference results; [GitHub Actions](https://github.com/timothywarner-org/context-engineering-with-mcp/actions/workflows/verify.yml) checks the current code on Windows and Linux.

## Optional preparation

### Your first successful tool call

Use **PowerShell 7**, **Git**, and **uv**. The locked project supports Python 3.11 or
later; the commands below select Python 3.12, matching the verification workflow.
uv can obtain that interpreter if it isn't installed.

If you already have this repository, open a terminal in that checkout and skip the
clone. Otherwise, run:

```powershell
# Clone once so every exercise uses the same working copy.
git clone https://github.com/timothywarner-org/context-engineering-with-mcp.git
if ($LASTEXITCODE) { throw 'Clone failed; resolve the error before continuing.' }
Set-Location -LiteralPath .\context-engineering-with-mcp
```

From the repository root:

```powershell
# Use the lock file and the same Python version as the course verification workflow.
uv sync --project .\python --locked --python 3.12
if ($LASTEXITCODE) { throw 'Python setup failed; resolve the error before continuing.' }

# This client starts and stops its own server; no separate terminal or model is needed.
uv run --locked --project .\python python .\python\client.py
if ($LASTEXITCODE) { throw 'Client demo failed; see Troubleshooting below.' }
```

**Look for:** tool `get_incident`, owner **Priya Patel**, a timeout after deployment,
the runbook's instruction to request approval before rollback, and a final
`is_error=True` for the deliberately missing incident. That last result is expected.
[The client explanation](#call-the-server-from-python) separates this expected tool
error from a failed demo.

### Add tools only for the next exercise

| Exercise | Additional preparation |
|---|---|
| Memory or local HTTP checks | None beyond the locked Python setup above. |
| Inspector | Node.js 22.19 or later with npm; generate the client snippets below. |
| TypeScript implementation and full regression checks | Node.js 22.19 or later with npm; install and build below. |
| Host integration | A supported host and its required account/access; generate snippets and review consent. |
| Azure deployment | Optional. Read the supplement's prerequisites and cost/cleanup instructions first. |

For Inspector or a host, generate configuration for **your** checkout path:

```powershell
# Generated absolute paths prevent the host from launching a different checkout.
.\clients\New-ClientConfigs.ps1
if (-not $?) { throw 'Configuration generation failed.' }
```

For the TypeScript example and the full Python/TypeScript regression checks:

```powershell
# Keep the TypeScript installation local and reproducible.
Push-Location .\typescript
try {
    npm ci
    if ($LASTEXITCODE) { throw 'TypeScript dependency installation failed.' }
    npm run build
    if ($LASTEXITCODE) { throw 'TypeScript build failed.' }
} finally { Pop-Location }

# Both implementations must return meaningful success and failure results.
uv run --locked --project .\python python .\verify_protocol.py
if ($LASTEXITCODE) { throw 'Protocol verification failed.' }
```

Expect six protocol checks per language: discovery, tool listing, normalized incident lookup, resource read, prompt retrieval, and an unknown-ID tool error. The known incident is `INC-1042`; its owner is `Priya Patel`. All business data is fictional.

## Call the server from Python

After installing the locked Python dependencies, run this from the repository root:

```powershell
# The SDK manages the stdio subprocess, including discovery and cleanup.
uv run --locked --project .\python python .\python\client.py
```

The client lists `get_incident`, calls it with `INC-1042`, reads the approved runbook,
and requests `MISSING` to show an explicit tool error. Expect Priya Patel, the timeout
symptom, the instruction to request approval before rollback, and `is_error=True`
for the missing incident. All business data is fictional.

The existing server raises `ValueError` for a missing incident. The SDK logs that
exception to stderr and returns `Error executing tool get_incident` to the client.
The traceback is server diagnostics; `is_error=True` is the returned tool result.

An MCP client can make these requests without a language model. The script uses
`Client` and `StdioServerParameters` from the same pinned official `mcp` package as
the server. It starts `python/server.py` with its own Python interpreter and an
absolute path, then closes the connection and server on exit. No separate server
terminal, new package, or credential is required. Requests have a ten-second timeout,
and the complete demonstration has a thirty-second timeout. Unexpected failures
exit with a nonzero status; the deliberate missing-incident result is part of a
successful demonstration.

Use this small client to learn the SDK calls. Keep `verify_protocol.py` for the full
Python/TypeScript regression checks, including normalization and prompt retrieval.
See the [official SDK client guide](https://py.sdk.modelcontextprotocol.io/client/).

## Inspect the server

```powershell
# Pin Inspector to the version verified with this release.
npx --yes @modelcontextprotocol/inspector@2.9.0 --cli --config clients/generated/inspector.json --server warnerco-incidents --method tools/call --tool-name get_incident --tool-arg incident_id=INC-1042 --format json

# Read the resource separately: discovery alone isn't functional verification.
npx --yes @modelcontextprotocol/inspector@2.9.0 --cli --config clients/generated/inspector.json --server warnerco-incidents --method resources/read --uri warnerco://runbooks/order-api --format json

# Start the graphical Inspector when you want to explore the same exchange.
npx --yes @modelcontextprotocol/inspector@2.9.0 --config clients/generated/inspector.json --server warnerco-incidents
```

Keep the server's stdout reserved for protocol messages. Diagnostics go to stderr. If a server appears idle when launched directly, it's waiting for protocol input.

The generator selects `protocolEra: "modern"` inside the Inspector server entry.
Both the graphical and command-line Inspector use that saved selection.
This setting is specific to Inspector and isn't added to the other host snippets.

## Connect a host

Generate snippets first. Merge only `warnerco-incidents` into your existing configuration; don't replace unrelated server settings.

| Host | Supplied snippet | Placement |
|---|---|---|
| GitHub Copilot in VS Code | `clients/generated/vscode-mcp.json` | Workspace `.vscode/mcp.json`, using `servers` |
| Claude Code | `clients/generated/claude-code.mcp.json` | Project `.mcp.json`, using `mcpServers` |
| Claude Desktop | `clients/generated/claude-desktop.json` | Desktop configuration described in the official local-server guide, using `mcpServers` |

Restart or reload the connection as required by the current host. Review its consent request. Confirm `get_incident` is available, then request the owner and symptom for `INC-1042`. Check the actual result, not the model's assurance that it connected. The generated command launches were verified; GUI behavior, account permissions, and host protocol support require a local check. See the first-party links PDF for current host documentation.

## Understand the memory demonstration

From the same repository root:

```powershell
# A temporary database makes this repeatable without altering prior practice.
uv run --locked --project .\python python .\memory\memory_demo.py demo
if ($LASTEXITCODE) { throw 'Memory demonstration failed.' }
```

The example starts separate Python processes. A process-local value is lost. A note and event written to SQLite survive the next process. It then retrieves a durable fact and a versioned procedure, and verifies that a different scope sees no working notes or events.

SQLite proves a local process boundary. It isn't a distributed storage demonstration. Retrieval is lexical, not embeddings. Scope is a filter, not authorization. Production replicas require a suitable shared service, authorized identity-to-scope binding, concurrent-write behavior, retention, and a retrieval strategy that fits the workload.

The memory roles adapt the teaching design of WARNERCO Schematica. The complete
local exercise is here; the optional architectural reference is listed under
[Further reading](#further-reading).

## Context audit and governance practice

Use `context/incident-brief.txt` and `context/large-context.txt` to compare what your host includes. Record only counters the host actually exposes. File bytes and word counts aren't model token measurements. The worksheet provides an explicitly illustrative budget when no reliable counter is available.

Use `governance/request-review.json` to locate token, scope, and data-access decisions. It's a design exercise. The local stdio starters don't implement remote OAuth, gateway deployment, or production identity enforcement.

## Explore the Azure gateway demonstration

The [ACA/APIM supplement](azure-demo/README.md) runs the same fictional incident
behind a real gateway. It routes incident and runbook tools to separate endpoints
in one container, denies the rollback fixture, and limits runbook calls while
incident lookup remains available.

Run the HTTP server checks locally with the course's locked dependencies:

```powershell
# Verify endpoint behavior without Azure credentials or a model account.
uv run --locked --project .\python python .\azure-demo\verify_demo.py --local
```

The supplement includes deployment and live verification scripts for an existing
Azure environment, plus a [dated, sanitized live report](azure-demo/evidence/live-verification-2026-10-20.json).
Its authentication uses separate gateway and backend keys. OAuth consent,
per-user authorization, and private networking remain design extensions.
Attendees can watch the hosted demonstration without creating Azure resources.

## Protocol and verification boundary

The starters target the July 28, 2026 specification. Current-protocol `server/discover` and the five other checks passed for both languages on October 7, 2026. The TypeScript starter uses the official `serveStdio` entry point so the SDK chooses the protocol era. Don't replace it with a hand-written dispatcher.

No result in this repository claims a completed three-host GUI rehearsal, a live Azure OAuth test, or a Pearson event-platform upload. Re-run the examples after dependency or host changes. Keep tokens and private data out of screenshots and teaching fixtures.

## Further reading

[WARNERCO Schematica](https://github.com/timothywarner-org/context-engineering/tree/main/src/warnerco/backend)
is the larger architectural reference behind the memory exercise. It has different
dependencies and a vector-backed knowledge store. **It is optional reading, not a
second setup route for this session.** Keep this repository as your working copy.

## Troubleshooting

- **Wrong folder:** run `Get-Location`. The repository root contains `python`, `typescript`, `memory`, and `clients`. All commands on this page start there.
- **Need installation instructions:** use the official [PowerShell](https://learn.microsoft.com/powershell/scripting/install/installing-powershell-on-windows), [Git](https://git-scm.com/downloads), [uv](https://docs.astral.sh/uv/getting-started/installation/), and [Node.js](https://nodejs.org/en/download) guides. Install only what your chosen exercise needs.
- Command not found: install the optional prerequisite, reopen your terminal, and regenerate configuration snippets.
- TypeScript module not found: run `npm ci` and `npm run build` inside `typescript`.
- Discovery returns Method not found: inspect SDK version, protocol era, and the server entry point. Compare with the supplied files.
- Tool is listed but fails: inspect arguments and the returned error; use `INC-1042` for the known success case.
- No notes returned: verify the database path and scope. Storing a note doesn't automatically place it in model context.

License: MIT. See `NOTICE.md` for teaching-source attribution.
