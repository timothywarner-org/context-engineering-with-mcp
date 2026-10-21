"""Verify the consolidated course's links, demo paths, and privacy boundary.

Usage:
    python scripts/Test-CourseHome.py
    python scripts/Test-CourseHome.py --local

The default works on public clones. --local additionally requires Tim's private
submission and installed/generated host configurations without printing secrets.
This validates artifacts and paths; it doesn't run Azure or host inference.
"""
from argparse import ArgumentParser
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
TEACHING = ROOT / "instructor/2026-10-pearson"
CANONICAL = "C:/github/context-engineering-with-mcp"
DOCUMENTS = [ROOT / "README.md", ROOT / "AGENTS.md", ROOT / "instructor/README.md",
             TEACHING / "current-runbook.md",
             TEACHING / "Context-Engineering-All-Demos-v2.html",
             TEACHING / "ACA-APIM-Presenter-Quick-Start-v2.html"]


def require(condition: bool, message: str) -> None:
    """Keep checks active even if Python optimization disables assertions."""
    if not condition:
        raise ValueError(message)


class Document(HTMLParser):
    """Read navigation and displayed text without scanning embedded image data."""
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()
        self.text = []
        self.hidden = False

    def handle_starttag(self, tag, attrs) -> None:
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.add(attributes["id"])
        if tag == "a":
            self.links.append(attributes.get("href", ""))
        if tag in ("script", "style"):
            self.hidden = True

    def handle_endtag(self, tag) -> None:
        if tag in ("script", "style"):
            self.hidden = False

    def handle_data(self, text) -> None:
        if not self.hidden:
            self.text.append(text)


def read_document(path: Path) -> tuple[list[str], set[str], str]:
    """Collect Markdown headings with GitHub-style anchors and ordinary links."""
    source = path.read_text(encoding="utf-8-sig")
    if path.suffix == ".html":
        parsed = Document()
        parsed.feed(source)
        return parsed.links, parsed.ids, "\n".join(parsed.text)
    links = re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", source)
    headings = re.findall(r"^#{1,6}\s+(.+)$", source, flags=re.MULTILINE)
    ids = {re.sub(r"[^\w\s-]", "", title.lower()).replace(" ", "-") for title in headings}
    return links, ids, source


def local_path(value: str, source: Path) -> tuple[Path, str] | None:
    """Map Tim's named checkout into any CI checkout without creating aliases."""
    url = urlsplit(unescape(value))
    if url.scheme in ("http", "https", "mailto"):
        return None
    require(url.scheme in ("", "file"), f"Unexpected link scheme in {source.name}")
    target = unquote(url.path)
    if url.scheme == "file":
        normalized = target.lstrip("/").replace("\\", "/")
        require(normalized == CANONICAL or normalized.startswith(CANONICAL + "/"),
                f"File link leaves the course home: {value}")
        path = ROOT / normalized[len(CANONICAL):].lstrip("/")
    else:
        path = source.parent / target if target else source
    path = path.resolve()
    require(path.is_relative_to(ROOT), f"Link escapes the course home: {value}")
    return path, unquote(url.fragment)


def is_local_only(path: Path) -> bool:
    """Separate intentional private/generated dependencies from missing public files."""
    relative = path.relative_to(ROOT).as_posix()
    return ".local" in path.parts or relative.startswith("clients/generated/") or relative in (
        ".mcp.json", ".vscode/mcp.json")


def check_documents(local: bool) -> tuple[int, int, int]:
    """Resolve actual file targets and command paths, not just link labels."""
    link_count = path_count = skipped = 0
    for source in DOCUMENTS:
        links, _, visible = read_document(source)
        require(not re.search(r"C:[/\\]github[/\\]context-eng-2\b", visible, re.IGNORECASE),
                f"Obsolete working path in {source.relative_to(ROOT)}")
        require("Instructor clone" not in visible and "Runnable learner clone" not in visible,
                f"Split-clone directions remain in {source.name}")
        for value in links:
            resolved = local_path(value, source)
            if resolved is None:
                continue
            target, fragment = resolved
            if is_local_only(target) and not local:
                skipped += 1
                continue
            require(target.exists(), f"Broken link in {source.name}: {value}")
            if fragment and target.suffix in (".md", ".html"):
                require(fragment in read_document(target)[1], f"Broken anchor in {source.name}: {value}")
            link_count += 1
        # Literal paths in copied PowerShell commands must point inside this same home.
        for value in set(re.findall(r"C:\\github\\context-engineering-with-mcp(?:\\[A-Za-z0-9_.-]+)*", visible)):
            target = ROOT / value.replace("\\", "/")[len(CANONICAL):].lstrip("/")
            if is_local_only(target) and not local:
                skipped += 1
                continue
            require(target.exists(), f"Missing displayed/command path in {source.name}: {value}")
            path_count += 1
    return link_count, path_count, skipped


def check_privacy() -> int:
    """Inspect the index and ignore rules without reading credential contents."""
    result = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"],
                            check=True, capture_output=True)
    paths = [value for value in result.stdout.decode("utf-8").split("\0") if value]
    manifest = json.loads((TEACHING / "submitted-files.json").read_text(encoding="utf-8"))
    submitted_names = {Path(item["path"]).name for item in manifest["files"]}
    for name in paths:
        parts = Path(name).parts
        require(".local" not in parts and "correspondence" not in parts,
                f"Private path is tracked: {name}")
        require(not re.search(r"(^|/)\.env(?:\.|$)|\.(pem|key)$", name),
                f"Credential file is tracked: {name}")
        # A misplaced copy must not publish Pearson's submitted assets under another folder.
        require(Path(name).name not in submitted_names, f"Publisher submission is tracked: {name}")
    probes = [".local/pearson/2026-10-22/handoff-v2/Context-Engineering-with-MCP-v2.pptx",
              "azure-demo/.local/deployment.json", "clients/generated/inspector.json"]
    for name in probes:
        ignored = subprocess.run(["git", "-C", str(ROOT), "check-ignore", "--quiet", "--no-index", "--", name])
        require(ignored.returncode == 0, f"Private/generated path isn't ignored: {name}")
    return len(paths)


def check_submissions() -> int:
    """Require the exact submitted bytes; never refresh a hash to excuse drift."""
    manifest = json.loads((TEACHING / "submitted-files.json").read_text(encoding="utf-8"))
    for item in manifest["files"]:
        path = (ROOT / item["path"]).resolve()
        require(path.is_relative_to(ROOT / ".local"), "Submission manifest path leaves private storage")
        require(path.is_file(), f"Submitted file is missing: {path.name}")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"],
                f"Submitted file has changed: {path.name}")
    return len(manifest["files"])


def check_host_paths() -> int:
    """Inspect only the course server's configuration, leaving other servers alone."""
    configs = [(ROOT / "clients/generated" / name, key) for name, key in (
        ("vscode-mcp.json", "servers"), ("claude-code.mcp.json", "mcpServers"),
        ("claude-desktop.json", "mcpServers"), ("inspector.json", "mcpServers"))]
    configs += [(ROOT / ".vscode/mcp.json", "servers"), (ROOT / ".mcp.json", "mcpServers")]
    appdata = os.environ.get("APPDATA")
    require(bool(appdata), "--local host verification requires Tim's Windows APPDATA")
    configs.append((Path(appdata) / "Claude/claude_desktop_config.json", "mcpServers"))
    expected = (ROOT / "python/server.py").resolve()
    for path, key in configs:
        config = json.loads(path.read_text(encoding="utf-8-sig"))
        entry = config[key]["warnerco-incidents"]
        args = entry.get("args", [])
        require(any(Path(value).resolve() == expected for value in args if isinstance(value, str)),
                f"Course server uses another checkout: {path.name}")
        if path.name == "inspector.json":
            require(entry.get("protocolEra") == "modern", "Inspector must select the modern protocol")
    return len(configs)


def main() -> int:
    """Report artifact checks separately from unexecuted live demonstrations."""
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--local", action="store_true", help="Require private files and installed host paths.")
    args = parser.parse_args()
    try:
        links, paths, skipped = check_documents(args.local)
        tracked = check_privacy()
        print(f"PASS: {links} local links/anchors and {paths} displayed demo paths resolve in one checkout.")
        print(f"PASS: {tracked} tracked paths checked; private and generated locations are ignored.")
        if args.local:
            print(f"PASS: {check_submissions()} submitted files retain their original SHA-256.")
            print(f"PASS: {check_host_paths()} generated/installed course-server configurations use this checkout.")
        else:
            print(f"LOCAL ONLY: {skipped} private/generated references intentionally skipped; use --local on Tim's computer.")
        return 0
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
