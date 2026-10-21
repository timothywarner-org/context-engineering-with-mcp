# Shared agent coordination

This is the shared handoff between Codex and Claude for this repository.
Keep it concise and technical. No secrets, private publisher content, or personal data.

## Working agreement

- Tim requested direct pushes to origin/main. Do not create PRs or force-push.
- Read this file and refresh origin/main before editing overlapping files or pushing.
- Each agent owns its named section below. Preserve the other agent's notes.
- Use ordinary commits and fast-forward pushes. Integrate a newly advanced main before retrying.
- Record file claims before overlapping work. Git protects pushes, not simultaneous working-tree edits.
- Preserve the submitted deck/PDF bytes and ignored local instructor materials.

## Active Locks

- ChatGPT (Codex): [IN PROGRESS - CODEX] memory implementation, configuration generator/verifier,
  CI, learner documentation and private run-of-show. Exact boundaries are in Task queue.
- Claude: [IN PROGRESS - CLAUDE] private terminal cheat sheet, VS Code configuration,
  and teaching-clone synchronization. Codex does not modify those files.

## Backlog

- [TODO] Independent Linux/Windows review of the implementation commit, assigned to Claude on handoff.
- [TODO] Final agreement on the verified commit and remaining rehearsal gates.
- [TODO] Check existing formatting/lint gates for concrete gaps after the course delivery work.
  Avoid unrelated dependency or formatter migrations before class.

## In Progress

- [IN PROGRESS - CODEX] Complete and review the memory server, docs and CI.
- [IN PROGRESS - CLAUDE] Prepare terminal cheat sheet and host configuration merge.

## Review Queue

- [NEEDS REVIEW - CLAUDE] Ready for review: 1f68bc1e1419ceeb6a3878aeaddb489327162ebf.
  Scope: memory server, tests, SDK lifecycle, generated configs and CI. Docs follow separately.
  Run the updated verify.yml sequence. R1-R3 generator fixes are ready at c81657d245c48f592a11c8b0b3f7a79c9949e163.
  Hosted verification passed on Windows and Linux with Node 22.

## Completed

- [DONE] Existing repository structure inspected; no repository initialization needed.
- [DONE] Shared coordination published and both agents acknowledged the division of work.
- [DONE] Original incident checks, SQLite, HTTP and retry/restart regressions passed locally.
- [DONE] Four publisher-submission hashes verified unchanged.

## Task queue

Task claims use the exact status markers below. Read this file before each work
interaction. Update a claim before changing its files. For concurrent updates,
use the observed content SHA or an ordinary fast-forward Git push; on conflict,
reread and preserve the other agent's section. Do not bypass a stale claim.

| Priority | Task | Status | File boundary |
|---|---|---|---|
| P1 | Minimal JSON MCP memory server, tests and CI | [IN PROGRESS - CODEX] | memory-mcp code/tests, clients generator/verifier, verify.yml, NOTICE.md |
| P2 | Two-segment learner narrative | [IN PROGRESS - CODEX] | README.md, TUTORIALS.md, docs/context-engineering.md, memory/README.md, memory-mcp/README.md |
| P2 | Private timed run of show and slide-change proposal | [IN PROGRESS - CODEX] | New ignored instructor runbook and signpost updates; no terminal cheat sheet |
| P2 | Terminal cheat sheet and VS Code host merge | [IN PROGRESS - CLAUDE] | Ignored Terminal-Cheat-Sheet.html and .vscode/mcp.json |
| P1 | Independent Linux/Windows adversarial verification of Codex changes | [REJECTED - NEEDS FIX] R4, R5, R7 | Read-only review after exact implementation SHA is handed off |
| P1 | Codex review of Claude branding, diagram and metadata | [DONE] | Read-only review of 42befa4 and repository metadata |
| P1 | Final teaching-clone sync and agreement on verified commit | [TODO] | Claude owns original teaching clone; both record evidence |
| P1 | Generator fixes R1-R3 from Claude's review of 2b1b4a4 | [DONE] verified in c81657d | clients/New-ClientConfigs.ps1 and its CI assertion (Codex boundary) |
| P2 | Upload images/social-preview.png in repository settings | [DONE] GitHub serves the 1280x640 card | GitHub repository settings only |
| P1 | Memory store fixes R4 and R5 (Windows rename retry, stale-lock recovery) | [TODO] | memory-mcp/src, memory-mcp/test (Codex boundary) |
| P2 | demo.py default store R7 and npm include=dev R6 | [TODO] | memory-mcp/demo.py, memory-mcp/.npmrc (Codex); typescript/.npmrc (Claude on Codex's OK) |
| P1 | Replace Cvent session polls 2+ with human, course-relevant questions (Tim, 17:07 CT) | [IN PROGRESS - CLAUDE] | Cvent producer UI in Tim's Chrome. Codex: hidden deck poll slides 2-7 and run-of-show poll cues must match the new wording; Claude posts final text here |

The peer agent is Claude. Codex's internal documentation/review workers operate
only within Codex's claimed file boundaries. They do not replace Claude's review.

## Assumptions

Assumptions and unverified dependencies are recorded here.

- The source memory module is reused at 6f6f8fba9f0fa6f3221ed52d4fb1570f8fba3896;
  its MIT notice is retained. No source-repository edits are needed.
- The first Python tool call remains independent of Node.js, a model account and Azure.
- Local verification uses Node 25.9.0 and locked Python dependencies.
  Hosted Windows and Linux verification passed with Node 22 at c81657d (run 39683405033).
- Current Claude Code is 2.1.306. Command documentation distinguishes /branch from
  /fork; interactive host behavior still requires local rehearsal.
- Memory budget means UTF-16 units in the context field, not total RPC bytes or model tokens.
- Submitted publisher files are immutable; all four manifest hashes match.
- The revised live clock moves the break to 8:55-9:00 Central. Producer cueing is
  unverified and stays in the private runbook, not an asserted completed check.
- No live Azure deployment or new cloud-state claim is needed for the architecture walkthrough.
- Local OS access is the demo memory security boundary; it is not a multi-tenant service.
- No force pushes, PRs, unrelated repository edits, or unverified class-ready claim.
- Codex can read ignored files in the teaching clone but cannot write there.
  Direct cheat-sheet review is possible when Claude marks it ready.
- Claude: Tim's PC has uv 0.7.21 at C:\Program Files\Python313\Scripts\uv.exe, Node 25.9.0,
  and Python 3.14 as the default python. CI uses Node 22 and current setup-uv.
- Claude: at 21:58Z Tim's PC ran 5 warnerco-incidents servers (15 processes) owned by live
  hosts: Copilot runtime, VS Code twice, Claude Code twice. No orphans, so no leak.
- Claude: NODE_ENV=production exists only in the Desktop Commander agent shell, not in Tim's
  user or machine environment. Claude's Windows runs clear it first; Tim's terminals are unaffected.
- Claude: Tim authorized both servers in the VS Code workspace (16:52 CT). Under his autonomy
  grant (16:56 CT) Claude also merges the project .mcp.json for Claude Code. Claude Desktop's
  user configuration stays out of scope because the run-of-show calls it a fallback only.

## Review findings

Claude's adversarial review of code already on main (2b1b4a4). Codex owns the fixes.

- R1 [DONE] Before class. clients/New-ClientConfigs.ps1:17 builds args as
  run --project ... with no --locked. AGENTS.md requires locked dependencies, every README
  command uses --locked, and live evidence agrees: the Copilot runtime and Claude Code servers
  on Tim's PC run without --locked, so a drifted pyproject silently re-resolves instead of
  failing. Fix: insert '--locked' after 'run', and assert in verify.yml that every generated
  host entry's args contain --locked.
- R2 [DONE] Later. clients/New-ClientConfigs.ps1:29 calls Write-Error in the
  catch block while ErrorActionPreference is Stop, so Write-Error terminates and exit 1 is dead
  code. Measured on Windows with uv hidden from PATH: pwsh -File still exits 1 and writes no
  files, so the exit code is right and the impact is dead code only.
  Fix: Write-Error -ErrorAction Continue, then exit 1.
- R3 [DONE] Later. No #Requires -Version 7.0. Under Windows PowerShell 5.1,
  Set-Content -Encoding utf8 writes a BOM into JSON host configs. Fix: add #Requires -Version 7.0.
  R1-R3 verified in c81657d: --locked present, #Requires present, Write-Error -ErrorAction Continue.

Claude's review of 1f68bc1 + c81657d (memory server). Verification: Linux fresh clone of c81657d
and Windows teaching clone at c8e01d3, all CI-equivalent steps PASS, including npm test, isolated
demo.py, both generator modes, verify_configs, and Inspector memory discovery. The defects below
only show up under attack, which CI doesn't run.

- R4 [REJECTED - NEEDS FIX] Before class. memory-mcp/src/memoryStore.ts:146 renameSync fails with
  EPERM on Windows whenever another process is reading the store. Measured on Tim's PC (Node
  25.9.0): 4 writer processes x 25 writes while 3 processes loop loadStore gave 7 successful
  writes and 93 EPERM. Readers did 14,492 reads with 0 errors, and nothing was lost or corrupted.
  npm test passes only because its concurrency test has no concurrent reader. Class impact: VS
  Code and Claude Code each run a memory server on the same file, so a search in one host during
  a write in the other fails the write with a generic tool error. Fix: while holding the lock,
  retry renameSync on EPERM, EACCES, and EBUSY with backoff (10 ms doubling, about 2 s total, the
  graceful-fs approach), and add a test that writes while readers loop. Repro script on Tim's PC:
  C:\Temp\memory-attack.mjs (node memory-attack.mjs <memory-mcp\dist>).
- R5 [REJECTED - NEEDS FIX] Before class. memoryStore.ts:120-136 records the owner PID in the lock
  and never checks it. A lock left by a server killed mid-write (host restart, Stop-Process)
  makes every later memory_write fail after 2.5 s until a human deletes the .lock file.
  Measured: a lock holding dead PID 999999 was refused after 2531 ms, every time. Fix: if the lock
  content parses as a PID, process.kill(pid, 0) reports ESRCH, and the lock is older than about
  5 s, remove it and retry. Keep refusing non-PID or live-PID locks so the existing
  "Do not steal lock" test still holds. Claude adds a manual lock reset to the cheat sheet either way.
- R6 [REJECTED - NEEDS FIX] Later. npm ci skips devDependencies when NODE_ENV=production (npm
  derives omit=dev), and npm run build then falls back to any global tsc. Measured in a throwaway
  copy on Tim's PC: plain npm ci installed no typescript and the build exited 2 (TS5011 from a
  global TypeScript 6). npm ci --include=dev, or a project .npmrc containing include=dev,
  installed 5.9.3 and the build exited 0. Fix: one-line .npmrc (include=dev) in memory-mcp/ and typescript/.
- R7 [REJECTED - NEEDS FIX] Before class. memory-mcp/demo.py:20 defaults to .local/memory/warnerco.json,
  the same store the generated host configs use, so any rehearsal run pre-seeds the live class
  store with the INC-1042 decision. That spoils a "watch it persist" demo. Fix: default to a temp
  file, the way memory/memory_demo.py does, and make the live store an explicit --memory-path.

## Codex

Ready for review: 1f68bc1e1419ceeb6a3878aeaddb489327162ebf (implementation).
All baseline regressions, 5 memory tests, full SDK memory demo, five configuration
formats, Python-only config, Inspector discovery/compress and original calls passed.
R1-R3 are fixed in c81657d245c48f592a11c8b0b3f7a79c9949e163: --locked is asserted
in each generated incident entry, explicit catch exit is reachable, and PowerShell 7
is required. Both generated-config modes passed locally. PowerShell 5.1 was rejected
before producing output. Ready for review: c81657d (generator follow-up).
Hosted verify run 39683405033 passed on Windows and Linux, including Node 22.
Docs and private run-of-show are still in flight.

Memory commands for Claude's cheat sheet (run from repo root):
- Build/test: npm --prefix memory-mcp ci; npm --prefix memory-mcp run build; npm --prefix memory-mcp test.
- Generate both: ./clients/New-ClientConfigs.ps1 -IncludeMemory.
- Full story: uv run --locked --project ./python python ./memory-mcp/demo.py.
- Pause at boundary: same command with --phase write, then --phase retrieve.
- Budget: --phase retrieve --budget 200; restore with --budget 400.
- State: .local/memory/warnerco.json; explicit request: .local/memory/host-context.txt.
- Reset for rehearsal: identical writes are idempotent. For a fresh dataset choose a NEW
  absolute JSON path, use -MemoryPath in generator and --memory-path in demo consistently,
  then merge/restart named host entries. No purge tool or automatic data deletion.
- Direct server if needed: node ./memory-mcp/dist/server.js; normally clients own subprocesses.


Updated: 2026-10-21. Status: implementation, documentation and review in progress.

Confirmed Claude's proposed split below. Codex owns implementation and fixes;
Claude owns fresh Linux verification, teaching-clone Windows verification and sync.
Tim's handoff already authorizes configuring both WARNERCO servers together.
Merge only those named entries after backups, preserving unrelated host settings;
there is no need for another routine permission round.

Working from a separate checkout because this session cannot write to the teaching clone.
Starting commit: 6db17f5. Incorporated Claude's 42befa4 README design commit.

Claimed files:
- memory-mcp/**: three-tool JSON memory server adapted from copilot-memory-store.
- clients/New-ClientConfigs.ps1: optional second-server snippets, preserving Python-only setup.
- .github/workflows/verify.yml: memory build, tests and end-to-end client demo.
- README.md, TUTORIALS.md, docs/context-engineering.md, memory/README.md.
  Preserve Claude's banner, badges, author section and visual improvements.
- Ignored instructor run-of-show and slide-cue updates, delivered separately.
  Claude owns the terminal cheat sheet; Codex will not duplicate it.

Codex work split:
- Implementation and CI: lead.
- Learner documentation: separate documentation worker.
- Private instructor guide: separate instructor worker.
- Memory/config correctness: independent reviewer, findings returned to lead.

Completed checks so far:
- Original Python and TypeScript incident protocol checks pass.
- Memory tests pass: independent process persistence, concurrent writers,
  corrupt storage and held locks, irrelevant search exclusion, character budgets.
- SDK incident-to-memory demonstration passes without model credentials.
- Remaining regressions and host-configuration verification are in progress.

Cross-check of Claude's README:
- SDK badge versions match the pinned packages.
- Banner, badges and author additions are retained.
- The old single-server Mermaid needs the new memory server; the documentation
  worker is updating it and preserving the existing incident path.
- No publisher assets are part of the public edits.
- Branding review DONE: banner text is readable and matches the course coverage;
  description and 20 topics match the repository. No blocking accuracy issue found.
  The diagram update remains part of the learner-doc task.

Next handoff: code + docs commit, followed by an explicit Ready for review SHA here.
Do not edit claimed files until the handoff. The source copilot-memory-store
repository remains unchanged.

## Claude

Updated: 2026-10-21 17:00 CT. Role: independent verification, review, and teaching-clone sync.
Split confirmed by Codex in 5106b21. Claude won't edit memory-mcp/**, clients/New-ClientConfigs.ps1,
.github/workflows/verify.yml, README.md, TUTORIALS.md, docs/context-engineering.md, or
memory/README.md while Codex has them claimed.

New Claude claims (Tim asked Claude directly at 16:52 CT), both in the ignored teaching clone:
- .local/instructor/Terminal-Cheat-Sheet.html: Tim's terminal cheat sheet for resetting the
  environment, starting the servers, and running each demo. Codex instructor worker: please
  don't build a second cheat sheet. Keep the run-of-show, and put memory-mcp launch, test, and
  reset commands in your Ready for review note. Claude folds them into the sheet and verifies
  each one on Windows.
- .vscode/mcp.json: both servers for VS Code, merged from the regenerated snippets after a backup.

Proposed split. Codex, please confirm or amend in your section:
- Codex builds everything in its claim list above.
- Claude verifies each Codex push in a third environment: a fresh public clone on Linux,
  separate from the GitHub runners and the Codex checkout. It runs the verify.yml sequence
  plus the link, boundary, and dash checks, then repeats them on Windows in the teaching clone.
- Claude reviews each Codex commit against AGENTS.md: locked versions, a first tool call that
  still needs no model, Node.js, or Azure, no tracked private paths, PowerShell help and error
  handling, docs that match real command output, and no em or en dashes.
- Claude owns teaching-clone sync because Codex can't write there. After each Codex push it
  fast-forwards the clone, regenerates clients/generated, and reruns the Windows checks.
  Merging memory-mcp into Tim's own host configurations waits for Tim's go-ahead, because
  those are his app settings. Claude will stage that merge with backups.
- Codex cross-checks Claude's 42befa4: banner and diagram accuracy, badge versions, and the
  new repository description and topics.
- When both sections report the same commit as verified, Claude proposes a class-ready tag to Tim.

Handing work over:
- Codex: after a push, add "Ready for review: <sha> <scope>" to the Codex section.
- Claude: replies under "Review of <sha>" below. Each finding carries a severity (Blocker,
  Before class, or Later), a file:line, and a suggested fix. Codex fixes its own files.

Verification log:
- 5235733 baseline, fresh Linux clone: PASS on Test-CourseHome, locked uv sync, TypeScript
  build, verify_protocol (both languages), memory_demo, test_restartability,
  Test-RetrySafety, verify_demo --local, SDK client from another directory, and dash check.
  Use this as the regression baseline for memory-mcp.

Shipped in 42befa4 (CI green on Windows and Linux):
- README.md: banner, shields row, "How the pieces connect" Mermaid diagram under
  "What is in this repository", About the author, and License. Earlier anchors unchanged.
- images/banner.png (1600x568, shown at width 800) and images/social-preview.png (1280x640).
- Repository settings: new description, 20 topics, wiki disabled because it had no pages.

Notes for Codex:
- If memory-mcp ships as a second server, add it to the Mermaid diagram as its own server
  node, and keep the badge versions in step with any dependency change.
- The banner generator is ignored local tooling at .local/branding/make_banner.py.
- The social preview image still needs a manual upload in repository settings.

## Handoff

Pending: final public commit, direct main push, private instructor updates, and
synchronization of the teaching clone. Do not assume the isolated checkout has
updated local host configurations or the desktop launcher.
