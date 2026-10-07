# Context Engineering with MCP

Tim Warner | Pearson Enterprise Live Training | October 22, 2026

**Two ways to take part.** If you set up the tools listed on the registration page, follow along hands-on with the commands below. If you didn't, you lose nothing: Tim drives every demo on screen, and the polls, chat, and worksheet carry the activities. Everything below also works as follow-up practice after class.

## What is in this repository

- `python/`: official MCP Python SDK 2.3.0 starter, pinned with `uv.lock`.
- `typescript/`: official TypeScript SDK server 2.3.1 starter, pinned with `package-lock.json`.
- `memory/memory_demo.py`: working, episodic, semantic, and procedural memory example.
- `clients/New-ClientConfigs.ps1`: portable configuration generator for three hosts and Inspector.
- `context/`: small and large fictional incident files for the context audit.
- `governance/request-review.json`: remote authorization and gateway decision exercise.
- Slides, participant worksheet, and links PDF: in the Resources widget for your Pearson session.
- `evidence/`: saved verification results from October 7, 2026.

## Optional preparation

Use PowerShell 7, Python 3.11 or later with `uv`, and Node.js 22.19 or later with npm. Live attendees can skip this and still complete every activity. A host account is needed only to repeat the host demonstrations later. No Azure subscription is needed for the supplied local exercises.

Clone the repository with `git clone https://github.com/timothywarner-org/context-engineering-with-mcp.git`, then open a terminal at its root:

```powershell
# Locked dependencies make the demonstration reproducible.
uv sync --project .\python --locked
Push-Location .\typescript
try { npm ci; if ($LASTEXITCODE) { throw 'npm ci failed' }; npm run build; if ($LASTEXITCODE) { throw 'Build failed' } }
finally { Pop-Location }

# Verify both languages using real protocol requests and explicit failure cases.
uv run --project .\python python .\verify_protocol.py

# Use a fresh temporary database so repeated practice can't alter earlier work.
uv run --project .\python python .\memory\memory_demo.py demo

# Generate absolute launch paths for wherever you cloned the repository.
.\clients\New-ClientConfigs.ps1
```

Expect six protocol checks per language: discovery, tool listing, normalized incident lookup, resource read, prompt retrieval, and an unknown-ID tool error. The known incident is `INC-1042`; its owner is `Priya Patel`. All business data is fictional.

## Inspect the server

```powershell
# Pin Inspector to the version verified with this release.
npx --yes @modelcontextprotocol/inspector@2.9.0 --cli --config clients/generated/inspector.json --server warnerco-incidents --protocol-era modern --method tools/call --tool-name get_incident --tool-arg incident_id=INC-1042 --format json

# Read the resource separately: discovery alone isn't functional verification.
npx --yes @modelcontextprotocol/inspector@2.9.0 --cli --config clients/generated/inspector.json --server warnerco-incidents --protocol-era modern --method resources/read --uri warnerco://runbooks/order-api --format json

# Start the graphical Inspector when you want to explore the same exchange.
npx --yes @modelcontextprotocol/inspector@2.9.0 --config clients/generated/inspector.json --server warnerco-incidents
```

Keep the server's stdout reserved for protocol messages. Diagnostics go to stderr. If a server appears idle when launched directly, it's waiting for protocol input.

## Connect a host

Generate snippets first. Merge only `warnerco-incidents` into your existing configuration; don't replace unrelated server settings.

| Host | Supplied snippet | Placement |
|---|---|---|
| GitHub Copilot in VS Code | `clients/generated/vscode-mcp.json` | Workspace `.vscode/mcp.json`, using `servers` |
| Claude Code | `clients/generated/claude-code.mcp.json` | Project `.mcp.json`, using `mcpServers` |
| Claude Desktop | `clients/generated/claude-desktop.json` | Desktop configuration described in the official local-server guide, using `mcpServers` |

Restart or reload the connection as required by the current host. Review its consent request. Confirm `get_incident` is available, then request the owner and symptom for `INC-1042`. Check the actual result, not the model's assurance that it connected. The generated command launches were verified; GUI behavior, account permissions, and host protocol support require a local check. See the first-party links PDF for current host documentation.

## Understand the memory demonstration

The example starts separate Python processes. A process-local value is lost. A note and event written to SQLite survive the next process. It then retrieves a durable fact and a versioned procedure, and verifies that a different scope sees no working notes or events.

SQLite proves a local process boundary. It isn't a distributed storage demonstration. Retrieval is lexical, not embeddings. Scope is a filter, not authorization. Production replicas require a suitable shared service, authorized identity-to-scope binding, concurrent-write behavior, retention, and a retrieval strategy that fits the workload.

The memory roles adapt the teaching design of [WARNERCO Schematica](https://github.com/timothywarner-org/context-engineering/tree/main/src/warnerco/backend). That larger reference uses additional dependencies and a vector-backed knowledge store. This repository deliberately keeps the demonstration inspectable.

## Context audit and governance practice

Use `context/incident-brief.txt` and `context/large-context.txt` to compare what your host includes. Record only counters the host actually exposes. File bytes and word counts aren't model token measurements. The worksheet provides an explicitly illustrative budget when no reliable counter is available.

Use `governance/request-review.json` to locate token, scope, and data-access decisions. It's a design exercise. The local stdio starters don't implement remote OAuth, gateway deployment, or production identity enforcement.

## Protocol and verification boundary

The starters target the July 28, 2026 specification. Current-protocol `server/discover` and the five other checks passed for both languages on October 7, 2026. The TypeScript starter uses the official `serveStdio` entry point so the SDK chooses the protocol era. Don't replace it with a hand-written dispatcher.

No result in this repository claims a completed three-host GUI rehearsal, a live Azure OAuth test, or a Pearson event-platform upload. Re-run the examples after dependency or host changes. Keep tokens and private data out of screenshots and teaching fixtures.

## Troubleshooting

- Command not found: install the optional prerequisite, reopen your terminal, and regenerate configuration snippets.
- TypeScript module not found: run `npm ci` and `npm run build` inside `typescript`.
- Discovery returns Method not found: inspect SDK version, protocol era, and the server entry point. Compare with the supplied files.
- Tool is listed but fails: inspect arguments and the returned error; use `INC-1042` for the known success case.
- No notes returned: verify the database path and scope. Storing a note doesn't automatically place it in model context.

License: MIT. See `NOTICE.md` for teaching-source attribution.
