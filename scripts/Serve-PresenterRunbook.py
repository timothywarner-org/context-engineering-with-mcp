"""Serve one presenter HTML file with live revision checks on localhost.

Usage:
  python scripts/Serve-PresenterRunbook.py --file path/to/runbook.html --port 8768

Only the selected document and its revision endpoint are exposed. This avoids
serving instructor research, repository configuration, or adjacent credentials.
Stop the foreground server with Ctrl+C. No third-party packages are required.
"""
from __future__ import annotations

import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit


def main() -> None:
    """Validate the document before binding a loopback-only development server."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, type=Path)
    parser.add_argument("--port", default=8768, type=int)
    args = parser.parse_args()
    document = args.file.resolve(strict=True)
    if document.suffix.lower() != ".html" or not document.is_file():
        parser.error("--file must identify an existing HTML document")
    if not 1024 <= args.port <= 65535:
        parser.error("--port must be between 1024 and 65535")

    class Handler(BaseHTTPRequestHandler):
        """Read from disk per request so saved edits become visible immediately."""

        def do_GET(self) -> None:
            route = unquote(urlsplit(self.path).path)
            if route not in ("/", "/" + document.name, "/__version"):
                self.send_error(404, "Only the presenter document is served")
                return
            try:
                payload = document.read_bytes()
                if route == "/__version":
                    payload = json.dumps({
                        "revision": hashlib.sha256(payload).hexdigest()
                    }).encode("utf-8")
                    content_type = "application/json; charset=utf-8"
                else:
                    content_type = "text/html; charset=utf-8"
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(payload)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.end_headers()
                self.wfile.write(payload)
            except (BrokenPipeError, ConnectionResetError):
                # Browser reloads can close the previous request mid-response.
                pass
            except OSError:
                self.send_error(503, "The presenter document is temporarily unavailable")

        def log_message(self, format: str, *values: object) -> None:
            # Revision polling is routine; only failed requests merit a log entry.
            if len(values) > 1 and str(values[1]) != "200":
                super().log_message(format, *values)

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Presenter runbook: http://127.0.0.1:{args.port}/", flush=True)
    print(f"Document: {document}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Presenter server stopped.", flush=True)
    finally:
        server.server_close()


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Presenter server failed: {exc}") from exc
