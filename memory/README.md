# Optional SQLite memory exercise

Run commands from the repository root. This Python-only comparison is separate from
the [three-tool MCP memory lifecycle](../memory-mcp/README.md). Its scope filter is
not authorization; its database does not share records with the JSON MCP store.

## Carry memory across processes

**Question:** "When a process ends, what survives, and how do we get it back?"

No model, MCP connection, Node.js, or Azure is required. Use the locked Python
setup from tutorial 0. Open [the memory example](memory_demo.py) if you want
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


Return to the [learner tutorials](../TUTORIALS.md).
