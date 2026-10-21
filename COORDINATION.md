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

Status and file claims: please add here before overlapping edits.
Observed work: README banner, badges, architecture diagram, author section (42befa4).
Please preserve the Codex section when updating this file.

## Handoff

Pending: final public commit, direct main push, private instructor updates, and
synchronization of the teaching clone. Do not assume the isolated checkout has
updated local host configurations or the desktop launcher.
