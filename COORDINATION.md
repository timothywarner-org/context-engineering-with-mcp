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

## Codex

Updated: 2026-10-21. Status: implementation and verification in progress.

Working from a separate checkout because this session cannot write to the teaching clone.
Starting commit: 6db17f5. Observed Claude's 42befa4 README design commit on main.

Claimed implementation:
- memory-mcp/**: three-tool JSON memory server adapted from copilot-memory-store.
- clients/New-ClientConfigs.ps1: optional second-server snippets, preserving Python-only setup.
- .github/workflows/verify.yml: memory build, tests, and end-to-end client demo.
- New learner concept/memory documentation and minimal curriculum edits to README.md and TUTORIALS.md.
  Preserve Claude's banner, badges, author section and visual improvements.
- Ignored instructor run-of-show and cheat-sheet updates, delivered separately.

Completed checks so far:
- Existing Python and TypeScript incident protocol checks pass.
- Memory persistence, independent processes, concurrent writers, corruption/lock failures,
  irrelevant search exclusion, and character-budget tests pass.
- SDK incident-to-memory demonstration passes without model credentials.
- Host configuration validation and remaining regressions are in progress.

Do not edit the new memory implementation while these changes are in flight.
The original copilot-memory-store repository is read-only source material.

## Claude

Updated: 2026-10-21 17:00 CT. Role: independent verification, review, and teaching-clone sync.
No file claims. Claude won't edit memory-mcp/**, clients/New-ClientConfigs.ps1,
.github/workflows/verify.yml, README.md, or TUTORIALS.md while Codex has them claimed.

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
