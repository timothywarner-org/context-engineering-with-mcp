"""Check learner documentation links and the public repository boundary.

Run ``python scripts/Test-CourseHome.py`` from any working directory.
Only tracked public files are required. No instructor installation, publisher
assets, host account, generated configuration, or cloud access is needed.
"""
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    """Keep validation active when Python optimization is enabled."""
    if not condition:
        raise ValueError(message)


class Document(HTMLParser):
    """Collect explicit anchors and HTML links, including those in Markdown."""
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.add(attributes["id"])
        if tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
        if tag == "img" and attributes.get("src"):
            self.links.append(attributes["src"])


def read_document(path: Path) -> tuple[list[str], set[str]]:
    """Resolve Markdown headings and links without treating code as navigation."""
    source = path.read_text(encoding="utf-8-sig")
    source = re.sub(r"^```[^\n]*\n.*?^```\s*$", "", source, flags=re.MULTILINE | re.DOTALL)
    parsed = Document()
    parsed.feed(source)
    if path.suffix.lower() in (".md", ".markdown"):
        # Destinations with spaces use angle brackets; optional titles are separate.
        links = re.findall(r"!?\[[^\]]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\s*\)", source)
        parsed.links.extend(value.strip("<>") for value in links)
        references = dict(re.findall(r"^\s*\[([^\]]+)\]:\s*<?([^\s>]+)>?", source, flags=re.MULTILINE))
        parsed.links.extend(references.values())
        duplicates: dict[str, int] = {}
        for title in re.findall(r"^#{1,6}\s+(.+?)(?:\s+#+)?\s*$", source, flags=re.MULTILINE):
            title = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", title)
            slug = re.sub(r"[^\w\s-]", "", unescape(title).lower()).replace(" ", "-")
            count = duplicates.get(slug, 0)
            duplicates[slug] = count + 1
            parsed.ids.add(f"{slug}-{count}" if count else slug)
    return parsed.links, parsed.ids


def tracked_paths() -> list[str]:
    """Use the index so an accidental private addition fails before publication."""
    result = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"],
                            check=True, capture_output=True)
    return [value for value in result.stdout.decode("utf-8").split("\0") if value]


def check_privacy(paths: list[str]) -> None:
    """Reject instructor operations and credentials without reading their contents."""
    for name in paths:
        parts = Path(name).parts
        require(".local" not in parts and "correspondence" not in parts,
                f"Private path is tracked: {name}")
        require(not re.search(r"(^|/)\.env(?:\.|$)|\.(pem|key)$", name, re.IGNORECASE),
                f"Credential file is tracked: {name}")
        require(not name.startswith("instructor/"),
                f"Instructor operations must remain local: {name}")
        require(not re.search(r"(?:Presenter|InstructorHome|ClassEnvironment)|submitted-files\.json", name),
                f"Instructor operations must remain local: {name}")
        require(not re.search(r"(?:Context-Engineering-with-MCP|Participant-Worksheet|Resources-and-References)-v\d+\.(?:pptx|pdf)$", name),
                f"Publisher submission is tracked: {name}")
    for name in (".local/instructor/private.txt", "azure-demo/.local/deployment.json",
                 "clients/generated/inspector.json", "COORDINATION.md"):
        ignored = subprocess.run(["git", "-C", str(ROOT), "check-ignore", "--quiet", "--no-index", "--", name])
        require(ignored.returncode == 0, f"Private/generated path is not ignored: {name}")


def check_documents(paths: list[str]) -> tuple[int, int]:
    """Require learner navigation to work in a fresh public clone."""
    documents = [ROOT / name for name in paths if Path(name).suffix.lower() in (".md", ".markdown", ".html")]
    links_checked = 0
    for source in documents:
        require(source.is_file(), f"Tracked document is missing: {source.relative_to(ROOT)}")
        for value in read_document(source)[0]:
            url = urlsplit(unescape(value))
            if url.scheme in ("http", "https", "mailto", "data"):
                continue
            require(not url.scheme and not url.netloc,
                    f"Machine-specific or unsupported link in {source.relative_to(ROOT)}: {value}")
            target = (source.parent / unquote(url.path)).resolve() if url.path else source
            require(target.is_relative_to(ROOT), f"Link leaves repository: {value}")
            require(".local" not in target.relative_to(ROOT).parts,
                    f"Public navigation depends on private material: {value}")
            require(target.exists(), f"Broken link in {source.relative_to(ROOT)}: {value}")
            # An ignored local file must not conceal a missing file in a learner clone.
            relative = target.relative_to(ROOT).as_posix()
            require(relative in paths or (target.is_dir() and any(name.startswith(relative + "/") for name in paths)),
                    f"Link depends on an untracked file: {value}")
            if url.fragment and target.suffix.lower() in (".md", ".markdown", ".html"):
                require(unquote(url.fragment) in read_document(target)[1],
                        f"Broken anchor in {source.relative_to(ROOT)}: {value}")
            links_checked += 1
    return len(documents), links_checked


def check_compact_markdown_tables() -> int:
    """Enforce MD060 compact separator spacing in the memory server README."""
    relative_path = Path("memory-mcp/README.md")
    lines = (ROOT / relative_path).read_text(encoding="utf-8-sig").splitlines()
    separator_count = 0
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = stripped[1:-1].split("|")
        if not cells or not all(re.fullmatch(r"\s*:?-+:?\s*", cell) for cell in cells):
            continue
        separator_count += 1
        require(
            all(cell.startswith(" ") and cell.endswith(" ") for cell in cells),
            f"MD060 compact table spacing violation in {relative_path}:{line_number}",
        )
    require(separator_count > 0, f"No Markdown table separators found in {relative_path}")
    return separator_count


def main() -> int:
    """Keep public checks independent from the instructor's local environment."""
    try:
        paths = tracked_paths()
        check_privacy(paths)
        documents, links = check_documents(paths)
        table_separators = check_compact_markdown_tables()
        print(f"PASS: {documents} public documents and {links} local links/anchors checked.")
        print(f"PASS: {table_separators} compact Markdown table separators checked.")
        print(f"PASS: {len(paths)} tracked paths respect the public/private boundary.")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
