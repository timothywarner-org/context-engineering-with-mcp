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

- No implementation commit has been handed off yet. Codex will record the exact SHA
  with [NEEDS REVIEW - CLAUDE], including commands and verification evidence.

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
| P1 | Independent Linux/Windows adversarial verification of Codex changes | [TODO] | Read-only review after exact implementation SHA is handed off |
| P1 | Codex review of Claude branding, diagram and metadata | [IN PROGRESS - CODEX] | Read-only review of 42befa4 and repository metadata |
| P1 | Final teaching-clone sync and agreement on verified commit | [TODO] | Claude owns original teaching clone; both record evidence |

The peer agent is Claude. Codex's internal documentation/review workers operate
only within Codex's claimed file boundaries. They do not replace Claude's review.

## Assumptions

Assumptions and unverified dependencies are recorded here.

- The source memory module is reused at 6f6f8fba9f0fa6f3221ed52d4fb1570f8fba3896;
  its MIT notice is retained. No source-repository edits are needed.
- The first Python tool call remains independent of Node.js, a model account and Azure.
- Local verification currently uses Node 25.9.0 and locked Python dependencies.
  Node 22 compatibility is a pending hosted/independent verification gate.
- Current Claude Code is 2.1.306. Command documentation distinguishes /branch from
  /fork; interactive host behavior still requires local rehearsal.
- Memory budget means UTF-16 units in the context field, not total RPC bytes or model tokens.
- Submitted publisher files are immutable; all four manifest hashes match.
- The revised live clock moves the break to 8:55-9:00 Central. Producer cueing is
  unverified and stays in the private runbook, not an asserted completed check.
- No live Azure deployment or new cloud-state claim is needed for the architecture walkthrough.
- Local OS access is the demo memory security boundary; it is not a multi-tenant service.
- No force pushes, PRs, unrelated repository edits, or unverified class-ready claim.

## Codex

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
