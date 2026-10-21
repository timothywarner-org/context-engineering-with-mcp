# Learner-facing MCP examples

This public repository speaks to learners. Start with README.md for the learning
route, prerequisites, commands, expected results, and conceptual boundaries.

- Keep examples runnable from one checkout. Preserve the fictional INC-1042 story.
- Explain MCP transport and capabilities separately from application context,
  retrieval, durable storage, and authorization decisions.
- Keep the first Python tool call independent of a model account, Node.js, and Azure.
- Use locked dependencies. Do not change versions as part of documentation cleanup.
- Keep personal working material, schedules, drafts, receipts, and credentials out
  of tracked files. That material lives in the ignored .local/ folder. Never
  force-add ignored files. Public builds and tests must work without .local/.
- Treat everything under .local/ as the author's originals: don't modify, re-export,
  or re-hash those files unless the author asks.
- Run python scripts/Test-CourseHome.py for public links and repository boundaries.
  Run relevant protocol, memory, client, or local HTTP checks when changing those
  examples. Public CI must not require a particular machine or cloud account.
- Use PowerShell 7 first. Scripts need help, error handling, and comments explaining
  why. Keep credentials out of outputs and Git. No em or en dashes.
