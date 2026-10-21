# Teach from this folder

**Working home: `C:\github\context-engineering-with-mcp`.**
Open this folder in VS Code for preparation, teaching, and learner demonstrations.

1. Open the [complete presenter walkthrough](2026-10-pearson/Context-Engineering-All-Demos-v2.html).
2. Open the [submitted deck](../.local/pearson/2026-10-22/handoff-v2/Context-Engineering-with-MCP-v2.pptx).
   This is Tim's local, unchanged Pearson submission. It isn't included in a public clone.
3. Use the [current runbook](2026-10-pearson/current-runbook.md) for the submitted file list,
   preparation, remaining delivery checks, and consolidation evidence.

The class is **Thursday, October 22, 8:00-10:00 a.m. Central**, with speaker check-in
at **7:30 a.m.** Tim operates the demos; attendees need no installation or credentials.

## Open the presenter browser

From the repository root in PowerShell 7:

```powershell
# Resolve the teaching file from this checkout and verify the served bytes before opening it.
.\instructor\Start-Presenter.ps1
```

The launcher serves the full guide at <http://127.0.0.1:8768/> with automatic refresh.
Only that HTML and its revision endpoint are served. The guide also opens directly
as an offline file. The [ACA/APIM guide](2026-10-pearson/ACA-APIM-Presenter-Quick-Start-v2.html)
is a focused reference for the cloud segment; the complete walkthrough governs the class.

## What belongs where

| Material | Location | Git status |
|---|---|---|
| Presenter walkthrough and current runbook | `instructor/2026-10-pearson/` | Public |
| Demos and fixtures | `python/`, `typescript/`, `memory/`, `context/`, `governance/`, `azure-demo/` | Public |
| Submitted deck and three PDFs | `.local/pearson/2026-10-22/handoff-v2/` | Ignored, local only |
| Publisher correspondence and raw rehearsal records | `.local/pearson/2026-10-22/` | Ignored, local only |
| Gateway deployment bindings and credentials | `azure-demo/.local/` | Ignored, local only |
| Generated host configurations | `clients/generated/` | Ignored, generated for this checkout |

The [submission hashes](2026-10-pearson/submitted-files.json) identify the exact four
files sent October 7. Learners get the PDFs through Pearson's Resources widget.
The private migration ledger is `.local/consolidation-2026-10-21/preservation.json`.
The source production repository remains a historical backup, with a redirect here.
The copied authoring scripts under the local archive are historical build inputs,
not an alternate demo setup or a promise of a portable rebuild.

## Verify this home

```powershell
# Require local publisher files and compare their hashes as well as public links and paths.
python .\scripts\Test-CourseHome.py --local
if ($LASTEXITCODE) { throw 'Course-home verification failed.' }

# Validate the actual saved guide and the exact document currently served to the browser.
python .\scripts\Test-PresenterRunbook.py --url http://127.0.0.1:8768/
if ($LASTEXITCODE) { throw 'Presenter verification failed.' }
```

Without `--local`, the course-home check runs on a fresh public clone and explicitly
skips private files and generated host configuration. Demo execution checks remain
in the root README and GitHub Actions. Passing these checks doesn't establish
Pearson platform readiness or Tim's measured delivery time.
