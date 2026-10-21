# Step-by-step demo tutorials

Follow these tutorials during class or practice afterward. Run one numbered step
at a time. Each exercise tells you what to do, what to look for, and why it matters.
You can read the explanation aloud while following the steps on another screen.

**One story throughout:** investigate fictional WARNERCO incident **INC-1042**,
owned by **Priya Patel**, involving Order API timeouts after a deployment.

**Our question:** what belongs in the assistant's next context, where does it come
from, and what is the assistant allowed to do?

## Choose your next tutorial

| Tutorial | What you will prove |
|---|---|
| [0. Prepare once](#0-prepare-once) | The examples run from your own checkout. |
| [1. Choose useful context](#1-choose-useful-context) | Relevant evidence and extra volume are different things. |
| [2. Retrieve evidence without a model](#2-retrieve-evidence-without-a-model) | An MCP client can retrieve incident facts and a procedure independently of AI. |
| [3. Inspect tools, resources, and prompts](#3-inspect-tools-resources-and-prompts) | Discovery, execution, reference material, and instructions are different. |
| [4. Carry memory across processes](#4-carry-memory-across-processes) | Saving, retrieving, and using information are separate steps. |
| [5. Use GitHub Copilot in VS Code](#5-use-github-copilot-in-vs-code) | The host can obtain evidence and use selected reference context. |
| [6. Use Claude Code](#6-use-claude-code) | Another host can call the same server. |
| [7. Use Claude Desktop](#7-use-claude-desktop) | A desktop host can launch the same local server. |
| [8. Choose tools and review access](#8-choose-tools-and-review-access) | Tool availability, model selection, approval, and authorization differ. |
| [9. Observe HTTP routing and gateway controls](#9-observe-http-routing-and-gateway-controls) | Local endpoint checks and live gateway enforcement prove different things. |
| [10. Explain the whole system](#10-explain-the-whole-system) | Context engineering connects all the exercises. |

The local Python and memory exercises need no model account, Node.js, or Azure.
Host exercises need the corresponding application and its required account/access.
Inspector and TypeScript additionally need Node.js 22.19 or later with npm.
Cloud deployment is optional and is not part of basic setup.

## 0. Prepare once

### Step 1: Open the checkout

Open PowerShell 7 in the repository root. All terminal commands below start there.
If you already have this checkout, do not clone another copy.

For a new checkout only:

```powershell
git clone https://github.com/timothywarner-org/context-engineering-with-mcp.git
if ($LASTEXITCODE) { throw 'Clone failed.' }
Set-Location -LiteralPath .\context-engineering-with-mcp
```

Run:

```powershell
Get-Location
Get-ChildItem -Name
```

**Look for:** the `python`, `memory`, `context`, and `clients` directories.
Your absolute checkout path need not match anybody else's.

### Step 2: Prepare the locked Python environment

Install [PowerShell 7](https://learn.microsoft.com/powershell/scripting/install/installing-powershell-on-windows),
[Git](https://git-scm.com/downloads), and [uv](https://docs.astral.sh/uv/getting-started/installation/)
if needed. Reopen your terminal after installation.

```powershell
# The lock and Python version match the course verification environment.
uv sync --project .\python --locked --python 3.12
if ($LASTEXITCODE) { throw 'Python setup failed.' }
```

**Explain:** "We're using the supplied dependency lock, not upgrading packages
while trying to learn the example."

### Step 3: Prepare Inspector and host snippets only if you need them

For Inspector or TypeScript, install [Node.js](https://nodejs.org/en/download)
22.19 or later with npm first.

Generate launch snippets for this checkout:

```powershell
.\clients\New-ClientConfigs.ps1
if (-not $?) { throw 'Configuration generation failed.' }
Get-ChildItem -LiteralPath .\clients\generated -Name
```

**Look for:** snippets for VS Code, Claude Code, Claude Desktop, and Inspector.
The [generator](clients/New-ClientConfigs.ps1) writes snippets; it does not install
them into your hosts. Merge only the `warnerco-incidents` entry, preserving other
servers and settings. Do not publish machine-specific generated configuration.

For every tutorial, success means observing the specified result, not merely
starting a process. If a command fails unexpectedly, stop that exercise and read
its error before continuing.

## 1. Choose useful context

**Question:** "Do we need more text, or better-selected evidence?"

### Step 1: Read the small incident brief

Open [the incident brief](context/incident-brief.txt).

**Look for:** the incident ID, owner, service, symptom, task, and approved procedure.

**Explain:** "Our task is to recommend the next investigation check. We need enough
evidence to support that recommendation, not every document the company owns."

### Step 2: Compare the large file

Open [the large context file](context/large-context.txt). Read its opening incident
summary, then scroll into the reference inventory.

**Look for:** the same useful incident information followed by unrelated records.

**Predict:** which records would change your next investigation check?

**Explain:** "The extra inventory adds volume without adding incident evidence.
This fixture illustrates selection; it doesn't prove that a particular model will
answer worse or cost a particular amount."

### Step 3: Optionally compare answers in a host

Use two fresh conversations with the same model and settings. Attach only the
large file in the first and only the brief in the second. In both, ask:

```text
Using only the attached incident information, recommend one next investigation
check for INC-1042. Separate observed facts, hypotheses, and missing information.
Do not change anything.
```

Inspect the answer's grounding, not just its fluency. Did it mistake "after a
deployment" for proof that the deployment caused the failure?

If the host exposes context/token usage, record the displayed measurements and
their labels. Do not call file sizes, word counts, or illustrative budgets measured
model tokens. Fresh chats reduce conversation carryover but do not guarantee the
host has no other instructions or context.

**Checkpoint:** explain which facts you would include and which material you would
leave out. A shorter file alone is not proof of better context.

## 2. Retrieve evidence without a model

**Question:** "Can we verify the evidence supply before involving an AI?"

### Step 1: Inspect the server's three capabilities

Open [the Python server](python/server.py).

| Find | Meaning |
|---|---|
| `@mcp.tool()` | `get_incident` looks up a record using an incident ID. |
| `@mcp.resource(...)` | The runbook is reference content addressed by an MCP URI. |
| `@mcp.prompt()` | The investigation prompt supplies reusable task instructions. |

**Explain:** "The incident is a fictional dictionary record. The runbook is a
short approved procedure. This server doesn't query a production ticket system."

The resource URI `warnerco://runbooks/order-api` is not a web address to visit.
The prompt does not execute an investigation. Requesting approval in its text
is not an authorization enforcement mechanism.

### Step 2: Run the client

Open [the small Python client](python/client.py), then run:

```powershell
uv run --locked --project .\python python .\python\client.py
if ($LASTEXITCODE) { throw 'Client demonstration failed.' }
```

Do not start the server in a second terminal. The client starts and stops its own
server subprocess over stdio.

### Step 3: Read the successful results

**Look for:**

- `Tools: get_incident`
- Owner `Priya Patel`, service `Order API`, status `Investigating`
- Symptom `Timeouts after a deployment`
- The runbook instruction to request approval before rollback

**Explain:** "We've retrieved current incident evidence and an approved procedure.
We still haven't established the cause of the timeouts."

### Step 4: Read the deliberate failure

**Look for:** `Unknown incident: is_error=True`.

The client requests `MISSING` deliberately. The Python server logs a `ValueError`
traceback to stderr; the SDK returns a tool-error result. The client expects that
result and finishes successfully.

**Explain:** "Unavailable evidence should remain unavailable. A failed lookup must
not become an invented incident or an empty success."

### Step 5: Identify what has not happened

The script lists a tool, calls it, reads a resource, and checks a tool error.
It does not invoke the investigation prompt, send information to a model, or use
the memory database.

**Checkpoint:** "MCP can deliver evidence without a language model. The application
still decides how that evidence enters model context."

### Optional: verify the TypeScript implementation too

Open [the TypeScript server](typescript/src/server.ts). Find the equivalent tool,
resource, and prompt. It is an alternative implementation, not a dependency of the
Python demonstration.

With Node.js and npm prepared:

```powershell
Push-Location .\typescript
try {
    npm ci
    if ($LASTEXITCODE) { throw 'TypeScript dependency installation failed.' }
    npm run build
    if ($LASTEXITCODE) { throw 'TypeScript build failed.' }
} finally { Pop-Location }

uv run --locked --project .\python python .\verify_protocol.py
if ($LASTEXITCODE) { throw 'Protocol verification failed.' }
```

**Look for:** `PASS Python` and `PASS TypeScript`. Each covers discovery, listing,
normalized incident lookup, resource reading, prompt retrieval, and an unknown-ID
tool error. The [verifier](verify_protocol.py) writes a fresh ignored report;
[reference evidence](evidence/protocol-evidence.json) is a dated reference, not your run.

## 3. Inspect tools, resources, and prompts

**Question:** "What exactly can a client discover and request?"

### Step 1: Open Inspector

Complete the Inspector preparation in tutorial 0, then run:

```powershell
npx --yes @modelcontextprotocol/inspector@2.9.0 --config .\clients\generated\inspector.json --server warnerco-incidents
```

Leave this terminal running while using Inspector. Open the local browser URL
printed by the launcher if it does not open automatically. Use its supplied
authentication flow; do not share launcher tokens or screenshots containing them.
Connect to the selected server if the browser asks you to connect.

**Look for:** a connected server and its capabilities. The generated Inspector
entry includes `protocolEra: "modern"` for this pinned release. Do not remove it.

### Step 2: Discover and call the tool

1. Open **Tools**, list tools if needed, and select `get_incident`.
2. Inspect its `incident_id` input and description.
3. Enter `INC-1042` and run the tool.
4. Read the actual returned incident record.
5. Try ` inc-1042 ` with surrounding spaces. It should return the same record.

**Explain:** "Discovery tells us what is available. Execution tells us whether this
request actually works. The server normalizes ordinary input."

### Step 3: Read the reference resource

1. Open **Resources** and list resources if needed.
2. Select `warnerco://runbooks/order-api` and read it.
3. Locate the approval-before-rollback instruction.

**Explain:** "We're retrieving selected reference material. Reading a runbook
doesn't perform its steps or grant permission to change a service."

### Step 4: Retrieve the prompt

1. Open **Prompts** and select `investigate_incident`.
2. Supply `INC-1042` for `incident_id` and get the prompt.
3. Find "Separate observed facts from hypotheses."

**Explain:** "The prompt frames how to investigate. It is not a stored finding,
and retrieving it does not run a model."

### Step 5: Test failure and finish

Return to **Tools**, call `get_incident` with `MISSING`, and inspect the error.
The error wording can differ between the Python and TypeScript implementations;
the important property is an explicit tool-error result.

Stop the Inspector launcher with **Ctrl+C** when finished.

If the browser workflow fails, these CLI calls exercise the same Python server:

```powershell
npx --yes @modelcontextprotocol/inspector@2.9.0 --cli --config .\clients\generated\inspector.json --server warnerco-incidents --method tools/call --tool-name get_incident --tool-arg incident_id=INC-1042 --format json
if ($LASTEXITCODE) { throw 'Inspector tool call failed.' }

npx --yes @modelcontextprotocol/inspector@2.9.0 --cli --config .\clients\generated\inspector.json --server warnerco-incidents --method resources/read --uri warnerco://runbooks/order-api --format json
if ($LASTEXITCODE) { throw 'Inspector resource read failed.' }
```

**Checkpoint:** identify a tool result, resource content, prompt instructions, and
a failure result without confusing one for another.

## 4. Carry memory across processes

**Question:** "When a process ends, what survives, and how do we get it back?"

No model, MCP connection, Node.js, or Azure is required. Use the locked Python
setup from tutorial 0. Open [the memory example](memory/memory_demo.py) if you want
to see the implementation, but you do not need to edit it.

### Step 1: Put an observation in a process-local variable

```powershell
uv run --locked --project .\python python .\memory\memory_demo.py local-write
if ($LASTEXITCODE) { throw 'Process-local write failed.' }
```

**Expected:**

```text
Timeouts began after the deployment
```

**Explain:** "This process put an observation in a dictionary. It printed the
observation, then exited. Predict what a new process will find."

### Step 2: Ask a fresh process for the observation

```powershell
uv run --locked --project .\python python .\memory\memory_demo.py local-read
if ($LASTEXITCODE) { throw 'Process-local read failed.' }
```

**Expected:**

```text
No note in this fresh process
```

**Explain:** "The new process has a new dictionary. Variables from the first
process did not survive its exit."

This demonstrates process-local state, not the behavior of an AI host's chat
history. The example deliberately uses separate dictionaries in separate processes.

### Step 3: Choose a fresh database for this practice run

Keep the **same PowerShell terminal** for steps 3 through 8 so `$memoryDb` remains
defined. Each Python command still starts a fresh Python process.

```powershell
# A unique temporary filename protects earlier practice databases.
$memoryDb = Join-Path ([System.IO.Path]::GetTempPath()) ("warnerco-memory-" + [guid]::NewGuid().ToString('N') + '.db')
```

### Step 4: Save the observation durably

```powershell
uv run --locked --project .\python python .\memory\memory_demo.py write --database $memoryDb --scope class-demo --note "Timeouts began after the deployment"
if ($LASTEXITCODE) { throw 'Durable write failed.' }
```

**Expected:** `Committed note and event`.

**Explain:** "This command saved a current working note and appended a timestamped
event in one database transaction. The writing Python process has now exited."

### Step 5: Retrieve from a new Python process

```powershell
uv run --locked --project .\python python .\memory\memory_demo.py inspect --database $memoryDb --scope class-demo
if ($LASTEXITCODE) { throw 'Durable read failed.' }
```

**Look for:** the observation under `working` and a timestamped entry under
`episodic`. Read the output one section at a time:

| Output section | Question it answers | How this example supplies it |
|---|---|---|
| `working` | What is our current note for this incident? | SQLite row selected by scope. |
| `episodic` | What was recorded, and when? | Up to three latest SQLite events for that scope. |
| `semantic` | What relevant background knowledge is available? | Seeded SQLite fact retrieved by a text match. |
| `procedural` | How should we proceed? | Version `1.0` procedure defined in Python code. |

**Explain:** "Working describes the note's purpose, not a requirement that it live
only in RAM. Our working note is durable here. The procedure is code-defined;
we have not stored all four roles as database tables."

The semantic fact says:

```text
Order API timeouts can follow exhausted connection pools.
```

Its source is `Fictional WARNERCO runbook v1`.

**Ask:** does that diagnose INC-1042?

**Answer:** no. It supplies background for a hypothesis, not evidence that the
connection pool is exhausted in this incident.

Retrieval is a SQL `LIKE` match for `connection`, not embeddings or a search
automatically generated from the current task. Initialization seeds this fictional
fact if it is absent, including when opening a fresh database.

### Step 6: See the difference between a current note and history

Save another known fictional incident fact:

```powershell
uv run --locked --project .\python python .\memory\memory_demo.py write --database $memoryDb --scope class-demo --note "Incident INC-1042 is assigned to Priya Patel"
if ($LASTEXITCODE) { throw 'Second durable write failed.' }

uv run --locked --project .\python python .\memory\memory_demo.py inspect --database $memoryDb --scope class-demo
if ($LASTEXITCODE) { throw 'Updated memory read failed.' }
```

**Look for:** one current working note containing the owner observation, and two
episodic events, newest first.

**Explain:** "The current note was replaced, not merged. The earlier observation
still exists in the event history. A scratchpad and an event log serve different
purposes."

### Step 7: Check a different scope

```powershell
uv run --locked --project .\python python .\memory\memory_demo.py inspect --database $memoryDb --scope another-session
if ($LASTEXITCODE) { throw 'Other-scope read failed.' }
```

**Look for:** empty `working` and `episodic` arrays. The shared semantic fact and
procedure still appear.

**Explain:** "Scope filters the session notes and events. It does not authenticate
the caller. This script lets us supply a scope; a production application must
authorize the identity-to-scope relationship."

### Step 8: Finish and remove only this practice database

**Explain:** "We proved that information survived Python process exits. We did
not prove distributed storage, automatic model memory, or production authorization."

```powershell
# Remove only the unique database created in step 3, after inspecting the results.
Remove-Item -LiteralPath $memoryDb -ErrorAction Stop
Remove-Variable memoryDb
```

### Step 9: Use the repeatable one-command version

For another run without manually managing a database:

```powershell
uv run --locked --project .\python python .\memory\memory_demo.py demo
if ($LASTEXITCODE) { throw 'Memory demonstration failed.' }
```

**Expected final lines:**

```text
PASS: the stored note survived a new process; another scope has no session notes.
Scope is an application filter, not authentication. Authorize the caller before selecting a scope.
```

This version creates an isolated temporary database, launches separate child
processes, checks its results, and removes the database afterward. Survival across
child-process exits does not mean survival after that deliberate cleanup.

### Step 10: Connect memory to context engineering

Look back at the four sections. Decide which information belongs in an assistant's
next investigation request.

**Explain:** "Storage answers: will it survive? Retrieval answers: can I get it
back? Context engineering answers: should I use it now?"

This script retrieves and prints a candidate collection of evidence. It does not
send it to a model, and it is not wired into the incident MCP server or client.
An application could retrieve memory directly or expose retrieval through MCP.
Either way, persistence alone does not put saved information into model context.

**If notes are missing:** check the database path and scope. Do not rerun step 3
midway: that chooses a new database. Do not use the standalone default database
and expect it to contain the temporary automatic demo's notes.

## 5. Use GitHub Copilot in VS Code

**Question:** "Can the host use verified evidence rather than just produce a
plausible answer?"

Host interfaces change. The current distinction between **Copilot** and **Local**
harnesses matters; a missing chat-input tool button does not necessarily indicate
a broken MCP server.

### Step 1: Connect the server in the correct configuration

If `warnerco-incidents` already works, keep that connection.

Otherwise, generate snippets using tutorial 0. For a VS Code-format MCP
configuration, merge the `warnerco-incidents` entry from
`clients/generated/vscode-mcp.json` into workspace `.vscode/mcp.json` under
`servers`. Preserve other settings and servers.

For a Copilot harness using portable MCP configuration, use the destination
selected by **MCP: Add Server** or **Chat: Open Customizations > MCP Servers**;
portable configuration uses `mcpServers`. The generated
`clients/generated/claude-code.mcp.json` contains the same launch command in that
wrapper. Merge the entry into the destination supported by your selected harness,
not blindly into every file.

Review the command and trust prompts. Use the
[current VS Code configuration guide](https://code.visualstudio.com/docs/agent-customization/mcp-servers)
if the destinations differ in your installation.

### Step 2: Find the tools controls

Open an agent-capable chat session.

- **Copilot harness:** press **Ctrl+Shift+P**, run **Chat: Open Customizations**,
  and open **Tools**. Search for `warnerco` and enable the incident tool/group.
  This selection persists in the active user profile. Record your original
  selections before changing them.
- **Local harness:** choose **Agent**, then **Configure Tools** in the chat input.
  Search for `warnerco` and enable the tool for the request.

The Copilot harness's built-in tools are read-only in that editor. Availability
and approval are separate controls. See
[current tool management](https://code.visualstudio.com/docs/agents/run/tools).

### Step 3: Require a real tool call

Start a fresh conversation and send:

```text
Use the warnerco-incidents MCP tool get_incident to look up INC-1042.
Report its owner, service, status, and symptom from the returned tool result.
Do not read repository files, change files, or perform a rollback.
```

Review any approval request before allowing it. Expand the actual tool call.

**Look for:** argument `incident_id: INC-1042`, owner Priya Patel, and the timeout
symptom in the returned result.

**Explain:** "The Python client chose fixed calls. Here, the host coordinates the
requests and makes the returned evidence available for the model's answer."

If the host answers without calling the tool, that is not a successful tool demo.
Use `#` tool completion if available to reference the discovered incident tool,
then repeat the bounded request.

### Step 4: Add the runbook as selected context

1. Run **MCP: Browse Resources** from the Command Palette.
2. Select the course server's `warnerco://runbooks/order-api` resource and read it.
3. Use **Add Context > MCP Resources** in Chat to attach the runbook.
4. Confirm the attachment appears, then send:

```text
Using the attached approved runbook and the INC-1042 tool result, list observed
facts, hypotheses, and missing information. Recommend one next check.
What requires approval? Do not change files or perform a rollback.
```

**Look for:** a recommendation grounded in the runbook, no assertion that temporal
correlation proves the cause, and the approval requirement.

### Step 5: Inspect the reusable prompt

Type `/` and select the discovered `investigate_incident` prompt. Supply `INC-1042`
when asked for the argument. Inspect the prepared request before sending it.
Prompt prefixes and picker labels can vary.

If resource or prompt controls are unavailable in your selected harness/version,
use Inspector for those capabilities and say which surface you actually tested.
Do not claim that a successful tool call verified resources or prompts.

**Checkpoint:** the tool supplied facts, the resource supplied reference context,
and the prompt framed the task. None automatically created durable memory.

## 6. Use Claude Code

**Question:** "Does a different host retrieve the same evidence?"

### Step 1: Merge the generated project configuration

Generate snippets using tutorial 0. Merge only `warnerco-incidents` from
`clients/generated/claude-code.mcp.json` into the repository-root `.mcp.json`
under `mcpServers`. Do not replace unrelated entries.

### Step 2: Start or restart Claude Code in this checkout

```powershell
claude
```

Inside Claude Code, run `/mcp`. Review project-server trust/approval requests and
confirm the course server is connected.

If Claude Code is not installed or signed in, complete the
[official setup and MCP guidance](https://code.claude.com/docs/en/mcp) first.
No additional Node.js package is needed by our Python server.

### Step 3: Ask for the incident

Send the same bounded tool request used in tutorial 5, step 3. Approve only the
read-only lookup you understand. Expand the tool invocation and inspect its input
and returned record.

**Look for:** Priya Patel, Order API, Investigating, and timeouts after deployment.
Claude Code may qualify the tool name with its server name.

### Step 4: Compare the host, not a different incident

**Explain:** "The host interface changed. The incident evidence and server did not.
A different launch or tool-loading sequence doesn't change our source of truth."

If this session visibly uses tool search before the incident call, inspect that
sequence. If it calls the tool directly, show that instead. One server does not
guarantee a tool-search step or a measurable token saving. Availability and
deferred tool-schema loading are different mechanisms.

**Checkpoint:** verify the actual call, not merely the final answer. Exit Claude
Code when finished; it manages its local server connection.

## 7. Use Claude Desktop

**Question:** "Can a desktop application obtain the same selected evidence?"

### Step 1: Open the local-server configuration

In Claude Desktop's application settings, open **Developer > Edit Config**.
On Windows, the configuration is normally at
`%APPDATA%\Claude\claude_desktop_config.json`.

Follow the [official local-server connection guide](https://modelcontextprotocol.io/docs/develop/connect-local-servers)
if your interface differs. Its filesystem example has different prerequisites;
our server uses the prepared Python environment.

### Step 2: Merge the course entry

Merge only `warnerco-incidents` from the generated
`clients/generated/claude-desktop.json` into `mcpServers`. Preserve other entries,
save valid JSON, then fully quit and reopen Desktop.

### Step 3: Confirm and call the tool

Confirm the local course server is available in Desktop's tools/integrations
controls. Send the same bounded request from tutorial 5, step 3.
Review any consent request, then inspect the tool activity and returned record.

**Look for:** the same owner and incident facts. If Desktop only produces a prose
answer without visible tool execution, do not count that as a verified connection.

### Step 4: Explain the boundary

**Explain:** "Desktop started a local subprocess. We didn't deploy the server to
a cloud or give it automatic memory. The host used a capability to retrieve
evidence for this request."

If the server fails to start, compare the configured absolute command and server
path with your newly generated snippet. Use tutorial 2 to check the server
independently of the host.

## 8. Choose tools and review access

**Question:** "Available, selected, approved, and authorized: are those the same?"

### Step 1: Reduce irrelevant tool availability

In the VS Code tools controls from tutorial 5, record the current selections.
Search for the course server. Temporarily deselect unrelated optional client-side
tool groups, leaving the incident tool available. Do not uninstall extensions or
edit unrelated server configurations.

Repeat the incident request in a fresh chat and inspect the tool call.

**Explain:** "We're reducing the available capability surface for this task.
We're not proving a token reduction, and enabling a tool does not mean it will
be called or that every call is authorized."

Restore your original selections afterward, especially for Copilot's persistent
profile-level controls.

### Step 2: Distinguish workflow guidance from capabilities

Compare the investigation prompt with the incident tool:

- The prompt tells the assistant how to approach the task.
- The tool lets the application retrieve incident evidence.
- A skill or other reusable workflow guidance is not automatically a new external
  capability, an authorization grant, or durable memory.

This is a comparison exercise, not a requirement to install or create a skill.

### Step 3: Review the authorization cases

Open [the request-review exercise](governance/request-review.json).
Before reading each decision, predict allow or deny:

| Case | What to notice | Expected decision |
|---|---|---|
| A | Audience is `different-resource`. | Deny: the token targets the wrong resource. |
| B | Scope is `profile.read`, not `incidents.read`. | Deny: required scope is absent. |
| C | Audience, scope, and incident permission appear suitable. | Only allow after remaining validation succeeds. |

### Step 4: Assign responsibilities

**Explain:** "The authorization server issues the token. A gateway and/or resource
server validates the token and applicable policy. The resource server or authorized
data layer must also enforce which incident this caller may access."

Case C still needs signature, issuer, expiry, and applicable policy validation.
A valid read scope is not permission to read every incident. A registry listing
is not authorization, and a prompt asking for approval is not an enforcement check.

**Checkpoint:** these are design cases, not requests against a real OAuth system.
The local stdio starters do not implement production identity enforcement.

## 9. Observe HTTP routing and gateway controls

**Question:** "What happens when capabilities sit behind an enforceable boundary?"

This optional supplement uses a separate HTTP server with three MCP endpoint
instances in one container. Unlike the stdio runbook resource, the HTTP example
also exposes a `get_runbook` tool. Do not treat the interfaces as identical.

### Step 1: Run the local HTTP checks

No Azure account or deployment is needed:

```powershell
uv run --locked --project .\python python .\azure-demo\verify_demo.py --local
if ($LASTEXITCODE) { throw 'Local HTTP verification failed.' }
```

The verifier starts and stops its own server on loopback port 8765. If that port is
in use, resolve the conflict with its owner rather than terminating an unknown process.

### Step 2: Interpret the local evidence

**Look for:** `PASS` lines for catalog discovery, incident and runbook execution,
wrong-route rejection, refused catalog execution, refused rollback fixture,
unknown-method rejection, and `direct_without_key: HTTP 401`.

Some refused MCP requests return an error inside HTTP 200. Inspect the MCP error
semantics too; HTTP status alone does not determine whether a tool succeeded.

**Explain:** "These checks prove backend endpoint behavior and backend-key
authentication locally. They do not run API Management, demonstrate its throttle,
or validate OAuth."

### Step 3: Read the gateway request path

Open [the supplement](azure-demo/README.md) and its request-path diagram.

| Request | Live gateway behavior to inspect |
|---|---|
| Discovery | Catalog endpoint lists the three tools. |
| `get_incident` | Result includes `servedBy: incidents`. |
| `get_runbook` | Result includes `servedBy: runbooks`. |
| `request_rollback` | Gateway denies the request with HTTP 403. |
| Repeated runbook calls | An observed HTTP 429 includes `Retry-After`. |
| Incident lookup after throttling | Incident route still succeeds. |

**Explain:** "The gateway decides whether the request may run and where it goes.
It does not decide which facts belong in the model's next context."

### Step 4: Observe a prepared live deployment, if available

Watch the live demonstration, or use the
[dated sanitized reference report](azure-demo/evidence/live-verification-2026-10-20.json).
Label reference evidence with its date; it is not proof of a new live run.

Only if you already have the documented deployment and permissions, run:

```powershell
# The script obtains credentials without printing them.
.\azure-demo\Test-Demo.ps1
if (-not $?) { throw 'Live gateway verification failed.' }
```

Do not run deployment commands just to complete this tutorial. Provisioning,
prerequisites, costs, and teardown boundaries are described in the
[supplement](azure-demo/README.md). Do not remove shared cloud resources.

Allow at least 60 seconds between full live runs. The configured limit is two
runbook calls per 60 seconds, but distributed counters are approximate. Prove
an observed 429, not a promise that a specific numbered request always fails.

### Step 5: State the security boundary accurately

Gateway and backend credentials are separate keys. This is not per-user OAuth,
Entra scope enforcement, or private networking. Never paste keys, access tokens,
private deployment receipts, or credential-bearing screenshots into chat or Git.
The rollback fixture is non-mutating and also refuses execution on the backend.

**Checkpoint:** discovery is not permission, and throttling one tool need not
block another.

## 10. Explain the whole system

Complete these statements in your own words:

1. **Context selection:** for this investigation, I need ___, but not ___.
2. **MCP:** I can retrieve ___ through a tool and ___ through a resource.
3. **Instructions:** the prompt tells the assistant to ___.
4. **Memory:** ___ survived a process exit because ___.
5. **Retrieval:** stored information becomes available when ___.
6. **Context assembly:** before supplying retrieved information to a model, I must ___.
7. **Authorization:** before permitting a request, the enforcing component must ___.

One possible summary:

> We selected incident facts and an approved procedure instead of unrelated
> inventory. MCP let a client request that evidence. The prompt framed the task.
> SQLite preserved observations across processes, and explicit retrieval brought
> them back. The application still has to choose what enters model context.
> Authorization must be enforced, not merely requested in prompt text.

The examples deliberately separate these responsibilities. There is no hidden
end-to-end model-and-memory pipeline in the starter client.

Return to the [learning route](README.md#learning-route) for the repository overview.
