# Pearson delivery: October 22, 2026

**Start here for Thursday's delivery.** This runbook supersedes the September planning
snapshots for this booking. It preserves the files already sent to Pearson.

**Complete presenter walkthrough:** open
[Context-Engineering-All-Demos-v2.html](Context-Engineering-All-Demos-v2.html).
This is the dark, responsive, standalone guide for the entire class: every demo,
all three hosts, six polls, four activities, and the full 120-minute clock.
It includes large text, anchored contents, copyable commands, selected spoken cues,
and clearly dated fallback evidence.

**Live-refresh tab:** <http://127.0.0.1:8768/>. Saved HTML edits refresh automatically.
The restart command is in the guide's final section. The helper serves only the
selected HTML and revision endpoint on loopback; adjacent instructor files and
the Azure deployment's private folder are not exposed.

## Confirmed booking

| Field | Value |
| --- | --- |
| Course | Context Engineering with MCP |
| Publisher and platform | Pearson Enterprise Live Training, Cvent |
| Date | Thursday, October 22, 2026 |
| Speaker check-in | 7:30 a.m. America/Chicago |
| Teaching | 8:00-10:00 a.m. America/Chicago, 6:00-8:00 a.m. Pacific |
| Editorial contact | Laura Lewin |
| Platform support | livetraining@pearson.com |
| Learner code | <https://github.com/timothywarner-org/context-engineering-with-mcp> |
| Speaker room | Use the original October 14 Pearson speaker invitation |

Booking sources: Pearson's September 25 confirmation and October 14 speaker invitation.
The October 7 sent email identifies the exact submitted files below.

Tim operates every demonstration. Participants can follow along if prepared, or use the
polls, chat, and worksheet without installing anything during class. Use **WARNERCO**,
incident **INC-1042**, and owner **Priya Patel** throughout.

## Submitted package (instructor-local files)

- [Deck v2](../../.local/pearson/2026-10-22/handoff-v2/Context-Engineering-with-MCP-v2.pptx)
- [Slide PDF v2](../../.local/pearson/2026-10-22/handoff-v2/Context-Engineering-with-MCP-v2.pdf)
- [Participant worksheet v2](../../.local/pearson/2026-10-22/handoff-v2/Participant-Worksheet-v2.pdf)
- [Resources and references v3](../../.local/pearson/2026-10-22/handoff-v2/Resources-and-References-v3.pdf)
- [October 20 presenter route and corrections](../../.local/pearson/2026-10-22/audit-2026-10-20/presenter-route-2026-10-20.txt)
- [October 18 say-track, retained for history](../../.local/pearson/2026-10-22/audit-2026-10-18/say-track-2026-10-18.txt)
- [Technical update and sources](../../.local/pearson/2026-10-22/audit-2026-10-18/technical-update.md)

The deck has 35 live slides and six hidden producer poll slides. Its live notes cover
exactly 120 minutes. Hidden slides aren't additional teaching time. The live slide PDF
has 35 pages. Keep shipped versions unchanged. Any correction gets a new filename and
an explicit producer handoff.

Use the full-course HTML and October 20 route addendum for the current screen sequence,
physical slide numbers, host calls, and ACA/APIM substitution. They incorporate the October 18
API Management and tool-search corrections. The shipped deck notes retain their October 7
wording; the current presenter route supersedes their demo cues without replacing that artifact.

## Clock on Thursday

| Central time | Offset | Delivery |
| --- | --- | --- |
| 8:00 | 0 | Welcome, context selection, incident, context audit |
| 8:25 | 25 | MCP roles, primitives, code, stateless protocol, verification |
| 8:55 | 55 | Q&A |
| 9:00 | 60 | Five-minute break. Display **9:05 a.m. Central** as the return time |
| 9:05 | 65 | Memory roles, process boundary, retrieval, tier triage |
| 9:30 | 90 | Host wiring, governance, tool exposure, skills |
| 9:50 | 110 | Transfer reflection, final poll, wrap-up and Q&A |
| 10:00 | 120 | Finish |

The shipped notes put the context demonstration at minutes 14-21, protocol and Inspector
at 39-51, memory at 73-83, and the host demonstration at 93-99. Producer poll offsets are
5, 21, 51, 83, 104, and 110 minutes. Confirm cueing with the producer.

## Server demonstration: 8:39-8:51 a.m. Central

**October 19 presenter update:** use this sequence on the existing **Demo: Build, run,
and inspect** slide. It replaces the long explanation of the raw-protocol verification
script with a small SDK client. The slide, twelve-minute window, following poll, and
120-minute agenda stay unchanged. The submitted deck and PDFs retain their original bytes.

Open VS Code and a PowerShell terminal at
`C:\github\context-engineering-with-mcp`. Install dependencies during prep.

| Central time | Offset | Action |
| --- | --- | --- |
| 8:39-8:41 | 39-41 | Open `python/server.py` beside `typescript/src/server.ts`. Identify the same incident tool, runbook resource, and investigation prompt in both implementations |
| 8:41-8:44 | 41-44 | Open `python/client.py`, run the command below, and inspect the tool result, resource, and deliberate error |
| 8:44-8:45 | 44-45 | Run the existing protocol verifier. Show both PASS lines, including normalization and prompt retrieval |
| 8:45-8:51 | 45-51 | Use Inspector to list tools, call the known incident, read the resource, get the prompt, and call the missing incident. Move to poll 3 at 8:51 |

1. In `python/client.py`, point to `Client`, `StdioServerParameters`, and `async with`.
   The SDK launches the server, discovers the protocol, and closes the subprocess.
2. Run:

   ```powershell
   # Reuse the locked SDK; the client starts the existing server itself.
   uv run --project .\python python .\python\client.py
   ```

3. Show `Tools: get_incident`, Priya Patel and the timeout symptom, then the approved
   runbook's rollback-approval instruction. These are responses from the server.
4. Show `Unknown incident: is_error=True` and `Error executing tool get_incident`.
   The tool returned an explicit failure result and the client finished normally.
   The existing server also logs its `ValueError` traceback to stderr. Distinguish
   those server diagnostics from the error result returned to the client.

**Say:** "An MCP client can call our server without a language model. I'm running the
client in this terminal, and you can see the incident facts and the approved runbook
come back from the server. The SDK handles the connection and the protocol messages.
Now look at the missing incident. The server returns an explicit tool error, so our
code can handle that result. Later, we'll connect this same server to the AI hosts
and inspect the calls they make."

5. Run the full verifier without walking through its subprocess and threading code:

   ```powershell
   # Keep both language implementations and the additional cases covered.
   uv run --project .\python python .\verify_protocol.py
   ```

6. Start Inspector and continue the existing manual checks:

   ```powershell
   # Use the rehearsed Inspector release and generated local launch configuration.
   npx --yes @modelcontextprotocol/inspector@2.9.0 --config clients/generated/inspector.json --server warnerco-incidents
   ```

**Recovery:** if the small client fails, keep the source visible and use the full
verifier or Inspector to demonstrate the same server behavior. Explain that the
client failed; a process launch alone doesn't prove its calls worked. Keep the
90-second troubleshooting limit and the 8:51 poll transition. This sequence has no
model inference, API key, or learner setup requirement. Its time allocation is a
rehearsal target, not a measured full delivery.

## October 20: working ACA and APIM example

**Focused five-minute reference:** open
[ACA-APIM-Presenter-Quick-Start-v2.html](ACA-APIM-Presenter-Quick-Start-v2.html)
for the standalone large-text guide, copyable commands, timed screen actions,
spoken cues, and embedded captured fallback. It opens directly in a browser.

**Tim requested the smaller INC-1042 class server.** It is deployed in Azure Container
Apps behind the existing API Management instance, with a separate classroom API.
The live check passed discovery, incident/runbook routing, rollback denial, a
runbook-specific throttle, incident success after throttling, and direct-backend
authentication. The official Python SDK negotiated MCP **2026-07-28** through APIM.

Open the [presenter walkthrough](file:///C:/github/context-engineering-with-mcp/azure-demo/README.md)
beside the [gateway policy](file:///C:/github/context-engineering-with-mcp/azure-demo/policy.xml).
Run from any PowerShell 7 terminal after signing in to the deployment's Azure tenant:

```powershell
# The wrapper retrieves the API-scoped key without displaying credentials.
& 'C:\github\context-engineering-with-mcp\azure-demo\Test-Demo.ps1'
```

Allow at least 60 seconds between runs. The gateway's distributed rate limiter is
approximate; show the observed 429 rather than promising an exact rejected call number.
The resulting report is
`C:\github\context-engineering-with-mcp\azure-demo\.local\live-verification.json`.

**Rehearsal target:** use the five-minute walkthrough at **9:39-9:44 Central**,
after the promised host demo and before poll 5. The October 20 full-course guide
makes this substitution explicit: host calls occupy 9:33-9:38, tool exposure uses
9:38-9:39, and the OAuth distinction continues through the gateway close, poll 5,
and the governance exercise. Skills, all host examples, and every poll remain.
No teaching time is added. Rehearse the whole 9:30-9:50 segment to measure the fit.

This example uses API subscription-key authentication and a separate backend
credential. It does **not** demonstrate OAuth consent, Entra scopes, per-user RBAC,
or private networking. Those distinctions remain part of the original design discussion.
No learner Azure account, local execution, or installation is required.

## Before the rehearsal

Use this same checkout for preparation and live commands. The root README contains the
locked setup and Inspector commands. The former development scaffold isn't a demo dependency.

- [x] Install the locked Python dependencies and run `npm ci` plus `npm run build`.
      Completed in the named learner checkout on October 19.
- [x] Run `uv run --project .\python python .\python\client.py`. The known incident,
      approved resource, and deliberate missing-incident error passed on October 19.
- [x] Run `uv run --project .\python python .\verify_protocol.py`. Both languages passed
      discovery, tool listing, normalized lookup, resource, prompt, and unknown-ID checks
      on October 19.
- [ ] Rehearse the client segment within 8:41-8:44 and the full server demo within 8:39-8:51.
- [x] Run `uv run --project .\python python .\memory\memory_demo.py demo` with a fresh
      temporary database. Process-local loss, durable retrieval, and scope-filter
      separation passed October 20.
- [x] Run `.\clients\New-ClientConfigs.ps1`. Regenerated October 20.
- [x] Merge the named server into each host configuration, preserving unrelated settings.
      All three configurations are installed and their actual tool calls passed October 20.
- [x] Execute `get_incident` in VS Code Copilot, Claude Code, and Claude Desktop.
      Each returned INC-1042, Priya Patel, Order API, Investigating, and the timeout symptom.
- [x] Observe Claude Code `/context` before loading, after the small fixture, after the
      complete large fixture, and after `/clear`: 784, 2.7k, 31.3k, and 904 of 1m tokens.
      These are dated host estimates, not billing counts or a demonstrated overflow.
- [x] Capture labeled fallback evidence for every host, context, Inspector, and the gateway.
      The full-course HTML embeds the evidence so its core content works offline.
- [x] Complete the Inspector GUI sequence using the corrected modern configuration:
      known incident, normalized input, resource, prompt, and deliberate missing incident.
- [x] Compare deferred tool search enabled and disabled using actual Claude Code calls.
      Both return the same incident; the guide shows the different loading sequences.

The SQLite example proves a **same-host process boundary**. It doesn't prove a distributed
storage service or authorization. The submitted OAuth/gateway exercise remains a design
review on paper. The October 20 supplemental example above now proves live routing
and policy enforcement with key authentication; it does not prove the OAuth design.
These limits remain visible in the submitted materials.

## Platform and producer check

- [ ] Complete the scheduled Pearson platform test Wednesday, October 21,
      10:30-11:00 a.m. Central, as confirmed in Tim's calendar on October 19.
- [ ] Confirm Pearson loaded deck v2 and the six polls, including answer keys.
- [ ] Confirm the Resources widget has slide PDF v2, worksheet v2, references v3,
      and the public learner repository URL.
- [ ] Test the selected camera, microphone, and shared window in Chrome.
- [ ] Check the shared terminal and code at the resolution attendees receive.
- [ ] Confirm speaker verification email access and the waiting-room procedure.
- [ ] Use a natural, blurred, or Pearson-approved virtual background.
- [ ] Keep the camera on throughout, as required by the speaker invitation.

## Recovery and pacing

After 90 seconds of troubleshooting, switch to a labeled capture and continue the same
teaching point. Startup silence only means a stdio process may be waiting for input.
Prove behavior with the known tool result, resource read, and failure case.

Protect all promised host examples. A working host can keep the session moving, but it
doesn't verify the other hosts. Show a labeled capture for any host that fails live.

Cloud-backed host inference and Cvent need network access. Local protocol and SQLite
checks can run offline only after their dependencies are installed. Keep captured context
readings and local demo results ready if the network fails.

Shorten repeated explanation and typing before cutting a required concept or activity.
Keep the five-minute break and final handoff. Rehearse from the current full-course HTML
and its physical slide cues, and record actual elapsed times before calling delivery ready.

## Evidence and preservation

The **October 20** rehearsal record reports successful tool calls in all three hosts,
the Inspector sequence, context readings, selective tool loading, and the deployed
gateway checks. The walkthrough retains the dated native captures. Original receipts
and the complete prior production log are preserved in the ignored
[local archive](../../.local/pearson/2026-10-22/archive/current-runbook.md).
These observations aren't a new rehearsal on the consolidation date.

The selected [tool-loading comparison](evidence/claude-tool-loading-comparison.json)
is public teaching evidence. Session/tool-use identifiers and account cost fields
are omitted; the original record remains in the local archive.

The [submission manifest](submitted-files.json) fixes the SHA-256 of the four files
sent October 7. They stay under `.local/pearson/2026-10-22/handoff-v2/` and outside Git.
Participants receive the PDFs through Pearson's Resources widget.

**Remaining human gates:** measured delivery, especially the 9:30-9:50 block,
and Pearson's platform, camera, microphone, poll, and resource checks. Exact native
200% browser zoom and print-preview checks weren't recorded in the October 20 audit.

## October 21 consolidation review

**Failure:** teaching required two repositories, while old scaffold documentation
still looked current. **Cause:** publishing learner code separately left presenter
commands, evidence paths, and the running HTML server anchored to the production repo.

**Correction:** the reusable walkthrough, runbook, and serving/validation tools now
live in this checkout. The submitted files, publisher correspondence, original
source snapshots, and raw rehearsal records are preserved under ignored `.local/`.
The former repository is retained as historical source with a redirect.

**Preventive check:** `scripts/Test-CourseHome.py` rejects obsolete checkout paths,
broken public links, and tracked private files. Its `--local` check also requires
the private package, verifies submitted hashes, and resolves demo/configuration paths.
`scripts/Test-PresenterRunbook.py` validates the delivered HTML and can compare the
served bytes and revision. Both run in the repository's verification workflow.

**Local validation, October 21:** 175 links/anchors and 34 displayed demo paths
resolve in the consolidated checkout. All four submitted file hashes match, and
all 52 private preservation copies match the migration ledger. Seven generated
and installed host configurations point to this checkout's server. Twenty external
URLs returned HTTP 200, following redirects where present.

The SDK client (including its intended missing-incident error), Python and TypeScript
protocol checks, memory process-boundary example, and local HTTP server checks passed.
No new cloud deployment or host-model inference was required for this consolidation.
Original October 20 live evidence remains dated evidence.

The actual HTML retains the same 23 spoken passages, 25 agenda windows totaling
120 minutes, six polls, four activities, and eight original screenshot payloads.
Voice lint reports zero errors and warnings. The HTML validator passes all anchors,
31 copy targets, 26 PowerShell blocks, JavaScript syntax, and image MIME checks.
Negative fixtures for an old checkout, missing file, and missing anchor were rejected.

The existing loopback listener was explicitly identified and replaced with the new
checkout's server. HTTP response bytes and revision match the new saved HTML.
Private, adjacent, and traversal requests returned 404. Repeating the launcher reused
the verified listener. Browser inspection showed the single working home, live-refresh
connection, working schedule navigation, enlarged 140% text, and copy-success feedback.
The browser clipboard read API returned empty text, so this run doesn't claim a new
clipboard round trip. Native 200% zoom and print preview remain separate checks.

Staged files passed the privacy check and a credential-pattern inspection. The eight
native screenshots were visually inspected before publication. Publisher assets and
raw source records aren't included in the public change. The GitHub verification
workflow now runs both course-home and presenter checks on Windows and Linux.
