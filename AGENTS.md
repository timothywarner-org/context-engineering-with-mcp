# Learner-facing MCP examples

This public repository teaches context engineering through a fictional WARNERCO
incident, **INC-1042**. Start with `README.md` for the learning route and
`TUTORIALS.md` for the step-by-step exercises. Use `docs/context-engineering.md`
for the distinction between instructions, retrieved context, skills, subagents,
conversation history, and durable records.

## Project map

- `python/` contains the locked Python MCP incident server and model-free SDK
  client. The client starts and stops its own stdio server subprocess.
- `typescript/` contains the separate TypeScript MCP starter server.
- `memory-mcp/` contains the second stdio MCP server, implemented in TypeScript.
  It exposes `memory_write`, `memory_search`, and `memory_compress`, backed by
  local JSON storage under ignored `.local/`.
- `memory/` is an optional Python SQLite exercise. It is not an MCP server and
  does not share records with `memory-mcp/`.
- `azure-demo/` is an optional API Management and Azure Container Apps extension.
  Its local verification does not require cloud access; deployment uses existing
  Azure infrastructure.
- `clients/New-ClientConfigs.ps1` generates host and Inspector snippets for the
  current checkout. Generated paths can be machine-specific.

## Teaching and repository boundaries

- Keep examples runnable from one checkout and preserve the fictional INC-1042
  story. Keep business data fictional.
- Explain MCP transport and capabilities separately from context selection,
  retrieval, durable storage, tool availability, approval, and authorization.
- Keep the first Python tool call independent of a model account, Node.js, and
  Azure.
- Use locked dependencies. Do not change dependency versions during documentation
  cleanup or routine fixes.
- Preserve installed host settings when generating or documenting MCP config.
  Never publish machine-specific generated configuration.
- Keep personal working material, schedules, drafts, receipts, credentials, and
  deployment state out of tracked files. Store local material under ignored
  `.local/`; never force-add it. Public builds and tests must work without it.
- Treat everything under `.local/` as the author's original material. Do not
  modify, re-export, or re-hash it unless explicitly requested.

## Changes and verification

- Use PowerShell 7 from the repository root for learner commands. Prefer
  paste-ready single-line commands for ad hoc terminal guidance.
- Run `python scripts/Test-CourseHome.py` after documentation changes. It checks
  public links and repository boundaries, plus compact table separators in
  `memory-mcp/README.md`.
- Run the relevant locked build, test, demo, or local HTTP check when changing an
  example. Use `.github/workflows/verify.yml` as the CI inventory; CI must not
  require a particular machine, `.local/` data, or a cloud account for public
  checks.
- Distinguish failures caused by existing worktree changes from failures caused
  by the current edit. Do not revert or overwrite unrelated user changes.
- PowerShell scripts need comment-based help, error handling, and comments that
  explain non-obvious decisions. Keep credentials out of output and Git.
- Use ASCII by default. Do not use em dashes or en dashes.
