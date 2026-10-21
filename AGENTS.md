# Course working home

**This repository is the single working home for the October 22, 2026 class.**
Start with `instructor/README.md` for teaching and the root `README.md` for learner practice.
Use `instructor/2026-10-pearson/current-runbook.md` for production status and review evidence.

- Preserve the 120-minute agenda, six polls, four activities, and all promised demos.
- Keep narration and demo behavior intact when repairing paths or packaging.
- Public teaching guides live in `instructor/`; runnable examples remain at the root.
- Publisher submissions, correspondence, raw receipts, and original snapshots live in
  `.local/pearson/2026-10-22/`. All `.local/` directories are ignored. Never force-add them.
- Preserve the submitted PPTX and PDFs byte for byte. Their expected hashes are in
  `instructor/2026-10-pearson/submitted-files.json`. A correction needs a new version.
- The former production repository is historical source. Don't create a second working
  copy of the demos or send Tim there for preparation or delivery.
- Run `python scripts/Test-CourseHome.py` and `python scripts/Test-PresenterRunbook.py`
  before handoff. On Tim's computer also run `python scripts/Test-CourseHome.py --local`.
- If the presenter server is running, verify the actual response with
  `python scripts/Test-PresenterRunbook.py --url http://127.0.0.1:8768/`.
- Record substantive failures, causes, preventive checks, and results in the existing
  current runbook. Artifact checks, live service behavior, platform checks, and measured
  delivery remain separate gates.
- Use PowerShell 7 first. Scripts need help, error handling, and comments explaining why.
  Keep secrets out of output, commands, screenshots, and Git. No em or en dashes.
