# Learner-facing MCP examples

This public repository speaks to learners. Start with README.md for the learning
route, prerequisites, commands, expected results, and conceptual boundaries.

- Keep examples runnable from one checkout. Preserve the fictional INC-1042 story.
- Explain MCP transport and capabilities separately from application context,
  retrieval, durable storage, and authorization decisions.
- Keep the first Python tool call independent of a model account, Node.js, and Azure.
- Use locked dependencies. Do not change versions as part of documentation cleanup.
- Keep instructor schedules, presenter guides, launchers, publisher submissions,
  production receipts, and private validation out of tracked files. The public
  instructor/README.md is only a short optional signpost.
- Local instructor convenience files live in ignored .local/instructor/;
  publisher originals remain in ignored .local/pearson/. Never force-add private
  files. Public builds and tests must work without either directory.
- Run python scripts/Test-CourseHome.py for public links and repository boundaries.
  Run relevant protocol, memory, client, or local HTTP checks when changing those
  examples. Public CI must not require a presenter machine or cloud account.
- Preserve submitted deck and PDF bytes. Local instructor validation checks their
  recorded hashes; never refresh a hash to excuse content drift.
- Use PowerShell 7 first. Scripts need help, error handling, and comments explaining
  why. Keep credentials out of outputs and Git. No em or en dashes.
