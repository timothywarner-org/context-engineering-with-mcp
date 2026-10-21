"""Validate the actual saved Context Engineering presenter HTML.

Checks the 120-minute course structure, navigation, copy targets, command syntax,
embedded images, and optionally the served document identity. These are artifact
checks, not evidence of host execution, accessibility inspection, or Tim's rehearsal.

Examples:
    python scripts/Test-PresenterRunbook.py
    python scripts/Test-PresenterRunbook.py --url http://127.0.0.1:8768/
    python scripts/Test-PresenterRunbook.py --file path/to/guide.html --spoken-output spoken.txt

Requires Python 3, PowerShell 7 (pwsh), and Node.js on PATH. No third-party packages.
"""

from argparse import ArgumentParser
import base64
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from urllib.parse import urljoin
from urllib.request import urlopen


DEFAULT_FILE = (
    Path(__file__).resolve().parents[1]
    / "instructor/2026-10-pearson/Context-Engineering-All-Demos-v2.html"
)
ACTIVITIES = {
    "context-exercise": 1,
    "server-exercise": 2,
    "memory-exercise": 3,
    "governance": 4,
}


class Runbook(HTMLParser):
    """Collect semantic fields from the delivered HTML rather than a build script."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.links: list[str] = []
        self.copies: list[str] = []
        self.codes: dict[str, tuple[str, str]] = {}
        self.speech: list[str] = []
        self.scripts: list[str] = []
        self.images: list[tuple[str, str]] = []
        self.durations: list[int] = []
        self.rows: list[list[str]] = []
        self.polls: list[int] = []
        self.clocks: dict[str, str] = {}
        self.sections: list[str] = []
        self.row: list[str] | None = None
        self.cell: str | None = None
        self.code: tuple[str, str, str] | None = None
        self.say: str | None = None
        self.script: str | None = None
        self.clock: str | None = None
        self.next_poll_heading = False
        self.poll_heading: str | None = None

    def handle_starttag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.append(attrs["id"] or "")
        if tag == "a":
            self.links.append(attrs.get("href") or "")
        if "data-copy" in attrs:
            self.copies.append(attrs["data-copy"] or "")
        if "data-duration" in attrs:
            self.durations.append(int(attrs["data-duration"] or "0"))
        if tag == "section":
            self.sections.append(attrs.get("id") or "")
        if tag == "tr" and self.sections == ["schedule"]:
            self.row = []
        if tag == "td" and self.row is not None:
            self.cell = ""
        if tag == "code" and "id" in attrs:
            self.code = (attrs["id"] or "", attrs.get("data-language") or "", "")
        if "data-say" in attrs:
            self.say = ""
        if tag == "script":
            if attrs.get("src"):
                raise ValueError("The standalone guide must not depend on an external script.")
            self.script = ""
        if tag == "img":
            self.images.append((attrs.get("src") or "", attrs.get("alt") or ""))
        classes = (attrs.get("class") or "").split()
        if tag == "div" and "clock" in classes and self.sections:
            self.clock = ""
        if tag == "div" and "poll" in classes:
            self.next_poll_heading = True
        if tag == "strong" and self.next_poll_heading:
            self.poll_heading = ""
            self.next_poll_heading = False

    def handle_data(self, data: str) -> None:
        if self.cell is not None:
            self.cell += data
        if self.code is not None:
            name, language, text = self.code
            self.code = (name, language, text + data)
        if self.say is not None:
            self.say += data
        if self.script is not None:
            self.script += data
        if self.clock is not None:
            self.clock += data
        if self.poll_heading is not None:
            self.poll_heading += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self.cell is not None and self.row is not None:
            self.row.append(self.cell.strip())
            self.cell = None
        if tag == "tr" and self.row is not None:
            if self.row:
                self.rows.append(self.row)
            self.row = None
        if tag == "code" and self.code is not None:
            name, language, text = self.code
            self.codes[name] = (language, text)
            self.code = None
        if tag == "blockquote" and self.say is not None:
            self.speech.append(self.say.strip())
            self.say = None
        if tag == "script" and self.script is not None:
            self.scripts.append(self.script)
            self.script = None
        if tag == "strong" and self.poll_heading is not None:
            match = re.fullmatch(r"POLL ([1-6])", self.poll_heading.strip())
            require(match is not None, f"Unexpected poll heading: {self.poll_heading!r}")
            self.polls.append(int(match.group(1)))
            self.poll_heading = None
        if tag == "div" and self.clock is not None:
            self.clocks[self.sections[-1]] = self.clock.strip()
            self.clock = None
        if tag == "section" and self.sections:
            self.sections.pop()


def require(condition: bool, message: str) -> None:
    """Keep failures active even when Python runs with optimization enabled."""
    if not condition:
        raise ValueError(message)


def check_schedule(document: Runbook) -> None:
    """Read both clock and elapsed columns from the rendered schedule table."""
    require(len(document.rows) == 25, "Schedule must contain 25 actual HTML rows.")
    expected_start = 0
    clock_origin = None
    for index, row in enumerate(document.rows, 1):
        require(len(row) == 3, f"Schedule row {index} must contain three cells.")
        elapsed = re.fullmatch(r"(\d+)-(\d+)", row[1])
        wall = re.fullmatch(r"(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})", row[0])
        require(elapsed is not None and wall is not None, f"Malformed schedule row {index}.")
        start, end = map(int, elapsed.groups())
        hour1, minute1, hour2, minute2 = map(int, wall.groups())
        require(minute1 < 60 and minute2 < 60, f"Invalid clock minutes in row {index}.")
        wall_start, wall_end = hour1 * 60 + minute1, hour2 * 60 + minute2
        if clock_origin is None:
            clock_origin = wall_start
        require(start == expected_start and end > start, f"Schedule gap/overlap in row {index}.")
        require(
            (wall_start, wall_end) == (clock_origin + start, clock_origin + end),
            f"Clock and elapsed columns disagree in schedule row {index}.",
        )
        expected_start = end
    require(expected_start == 120, "The actual HTML schedule must end at elapsed minute 120.")
    require(document.polls == [1, 2, 3, 4, 5, 6], "Expected one poll block for each of polls 1-6.")
    for section, number in ACTIVITIES.items():
        require(
            re.search(rf"\bACTIVITY {number}\b", document.clocks.get(section, "")) is not None,
            f"Missing Activity {number} in the actual {section} section clock.",
        )
    require(
        len(document.durations) == 7
        and all(value > 0 for value in document.durations)
        and sum(document.durations) == 300,
        "The seven cloud beats must total 300 seconds.",
    )


def check_structure(document: Runbook, source: str) -> None:
    """Reject broken navigation and missing copy content before browser inspection."""
    duplicates = [name for name, count in Counter(document.ids).items() if count > 1]
    require(not duplicates, f"Duplicate IDs: {duplicates}")
    require("" not in document.ids, "An element has an empty ID.")
    for link in document.links:
        if link.startswith("#"):
            require(link[1:] in document.ids, f"Broken anchor: {link}")
    require(len(document.copies) == len(set(document.copies)), "Repeated copy target.")
    require(bool(document.copies), "No command copy controls found.")
    for target in document.copies:
        require(target in document.codes, f"Copy target is not a code block: {target}")
        require(bool(document.codes[target][1].strip()), f"Empty copy target: {target}")
    require(re.search("[\u2013\u2014]", source) is None, "Forbidden en/em dash in HTML.")
    require(bool(document.scripts), "No inline behavior script found.")
    # Only the screen label is a block; inline slide/time emphasis must keep flowing.
    require(
        re.search(r"\.screen\s*>\s*strong:first-child\s*\{[^}]*display\s*:\s*block", source) is not None,
        "The screen label needs its scoped block selector.",
    )
    require(
        re.search(r"\.screen\s+strong\s*\{[^}]*display\s*:\s*block", source) is None,
        "A broad screen emphasis selector would split inline slide/time cues.",
    )
    for image_source, alt in document.images:
        require(bool(alt.strip()), "An image needs descriptive alternative text.")
        # Browsers can silently sniff mislabeled captures, so check bytes as well as MIME.
        match = re.fullmatch(r"data:image/(png|jpeg);base64,([A-Za-z0-9+/=]+)", image_source)
        require(match is not None, "Image must be an embedded PNG or JPEG, not an external dependency.")
        pixels = base64.b64decode(match.group(2), validate=True)
        signature = b"\x89PNG\r\n\x1a\n" if match.group(1) == "png" else b"\xff\xd8\xff"
        require(
            pixels.startswith(signature),
            f"Embedded image bytes do not match declared image/{match.group(1)} MIME.",
        )


def check_syntax(document: Runbook) -> int:
    """Parse copied commands without running them; keep all temporary files isolated."""
    powershell = shutil.which("pwsh")
    node = shutil.which("node")
    require(powershell is not None, "PowerShell 7 (pwsh) is required on PATH.")
    require(node is not None, "Node.js is required on PATH.")
    commands = [(name, text) for name, (language, text) in document.codes.items() if language == "powershell"]
    with TemporaryDirectory(prefix="context-runbook-check-") as directory:
        temp = Path(directory)
        for index, (_, text) in enumerate(commands, 1):
            # Preserve CRLF from Windows checkouts; translating it again breaks backtick continuations.
            (temp / f"command-{index:02}.ps1").write_text(text, encoding="utf-8", newline="")
        parser = temp / "parse.ps1"
        # One parser process keeps a 26-command check fast without executing the demo commands.
        parser.write_text(
            """<# .SYNOPSIS
Parse the temporary presenter commands without executing them.
#>
param([Parameter(Mandatory)][string]$Directory)
$ErrorActionPreference = 'Stop'
$problems = @()
foreach ($script in Get-ChildItem -LiteralPath $Directory -Filter 'command-*.ps1') {
    $tokens = $null
    $parseErrors = $null
    [System.Management.Automation.Language.Parser]::ParseFile(
        $script.FullName, [ref]$tokens, [ref]$parseErrors) | Out-Null
    foreach ($problem in $parseErrors) {
        $problems += "$($script.Name): $($problem.Message)"
    }
}
if ($problems.Count) {
    $problems | Write-Output
    exit 1
}
""",
            encoding="utf-8",
        )
        result = subprocess.run(
            [powershell, "-NoProfile", "-File", str(parser), str(temp)],
            capture_output=True, text=True, timeout=30,
        )
        require(
            result.returncode == 0,
            "PowerShell syntax failed: " + (result.stdout + result.stderr).strip()
            + "\nCommand order: " + ", ".join(name for name, _ in commands),
        )
        for index, script in enumerate(document.scripts, 1):
            script_path = temp / f"inline-{index}.js"
            script_path.write_text(script, encoding="utf-8", newline="")
            result = subprocess.run(
                [node, "--check", str(script_path)], capture_output=True, text=True, timeout=30,
            )
            require(result.returncode == 0, "JavaScript syntax failed: " + result.stderr.strip())
    return len(commands)


def check_served(url: str, saved: bytes) -> None:
    """Check the exact document and the live-refresh revision, not just HTTP success."""
    with urlopen(url, timeout=10) as response:
        served = response.read()
    require(served == saved, "Served HTTP body differs from the selected file.")
    with urlopen(urljoin(url, "/__version"), timeout=10) as response:
        revision = json.load(response).get("revision")
    require(revision == hashlib.sha256(saved).hexdigest(), "Live-refresh revision differs from the file hash.")


def main() -> int:
    """Run the artifact gates and emit short, actionable diagnostics."""
    arguments = ArgumentParser(description=__doc__)
    arguments.add_argument("--file", type=Path, default=DEFAULT_FILE, help="Saved full-course HTML.")
    arguments.add_argument("--url", help="Optional live-refresh URL whose bytes and revision must match.")
    arguments.add_argument("--spoken-output", type=Path, help="Optional extracted SAY text for voice lint.")
    args = arguments.parse_args()
    try:
        saved = args.file.read_bytes()
        source = saved.decode("utf-8")
        document = Runbook()
        document.feed(source)
        document.close()
        check_schedule(document)
        check_structure(document, source)
        count = check_syntax(document)
        if args.url:
            check_served(args.url, saved)
        if args.spoken_output:
            args.spoken_output.write_text("\n\n".join(document.speech) + "\n", encoding="utf-8")
        print("PASS: actual HTML schedule has 25 contiguous windows, 120 minutes, six polls, four activities.")
        print(f"PASS: {len(document.ids)} unique IDs, {len(document.links)} links, {len(document.copies)} copy targets.")
        print(f"PASS: {count} PowerShell blocks, {len(document.scripts)} JavaScript block(s), seven cloud beats / 300 seconds.")
        print(f"PASS: {len(document.images)} embedded images with matching MIME and alt text; no forbidden dashes.")
        print(f"SHA256: {hashlib.sha256(saved).hexdigest()}")
        print("PASS: HTTP bytes and live-refresh revision match." if args.url else "HTTP identity: not requested.")
        if args.spoken_output:
            print(f"SAY text: {args.spoken_output.resolve()}")
        return 0
    except (OSError, ValueError, UnicodeError, subprocess.TimeoutExpired) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
