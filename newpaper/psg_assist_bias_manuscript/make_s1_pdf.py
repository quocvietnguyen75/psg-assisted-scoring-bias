"""Render Supplementary File S1 (the analysis plans) from Markdown to PDF with a headless Chromium browser.

Run from the repository root after make_supplementary_s1.py:
    BROWSER=<path to chrome or msedge> python newpaper/psg_assist_bias_manuscript/make_s1_pdf.py
Without BROWSER, the script looks for chrome, google-chrome, chromium or msedge on PATH. Another Markdown file can be
rendered the same way by passing SOURCE TARGET TITLE, for example the STARD checklist.
"""
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

FOLDER = Path("newpaper/psg_assist_bias_manuscript")
SOURCE = FOLDER / "supplementary_file_S1_analysis_plans.md"
TARGET = FOLDER / "supplementary_file_S1_analysis_plans.pdf"
TITLE = "Supplementary File S1: analysis plans"
CSS = """
@page { size: A4; margin: 2cm 2cm 2.2cm 2cm; }
body { font-family: Cambria, 'Times New Roman', serif; font-size: 10pt; line-height: 1.35; color: #000; }
h1 { font-size: 15pt; margin: 1.4em 0 0.5em; page-break-after: avoid; }
h2 { font-size: 12.5pt; margin: 1.2em 0 0.4em; page-break-after: avoid; }
h3, h4 { font-size: 11pt; margin: 1em 0 0.3em; page-break-after: avoid; }
p, li { orphans: 3; widows: 3; }
table { border-collapse: collapse; width: 100%; margin: 0.6em 0 1em; font-size: 8.5pt; page-break-inside: auto; }
th, td { border: 0.5pt solid #777; padding: 3px 5px; vertical-align: top; text-align: left; }
th { background: #eee; }
code { font-family: Consolas, 'Courier New', monospace; font-size: 8.5pt; word-break: break-all; }
pre { white-space: pre-wrap; background: #f5f5f5; padding: 6px; font-size: 8.5pt; }
hr { border: none; border-top: 0.75pt solid #999; margin: 1.6em 0; page-break-after: avoid; }
"""


def find_browser() -> str:
    candidate = os.environ.get("BROWSER")
    if candidate and Path(candidate).is_file():
        return candidate
    for name in ("chrome", "google-chrome", "chromium", "msedge"):
        found = shutil.which(name)
        if found:
            return found
    sys.exit("No Chromium browser found: set BROWSER to the path of chrome or msedge.")


LIST_ITEM = re.compile(r"^\s*([-*+]|\d+\.)\s")


def separate_lists(text: str) -> str:
    """Insert a blank line where a list starts right after a paragraph line, as CommonMark allows and
    python-markdown does not. The text itself is unchanged."""
    out, previous = [], ""
    for line in text.splitlines():
        if LIST_ITEM.match(line) and previous.strip() and not LIST_ITEM.match(previous) \
                and not previous.startswith(("#", "|", "    ")):
            out.append("")
        out.append(line)
        previous = line
    return "\n".join(out) + "\n"


def unlink_relative(body: str) -> str:
    """Repository-relative links do not resolve in a standalone PDF, so keep their text only."""
    return re.sub(r'<a href="(?!https?:)[^"]*">(.*?)</a>', r"\1", body)


def main(argv: list[str]) -> None:
    source, target, title = (Path(argv[0]), Path(argv[1]), argv[2]) if len(argv) == 3 else (SOURCE, TARGET, TITLE)
    body = unlink_relative(markdown.markdown(separate_lists(source.read_text(encoding="utf-8")),
                                            extensions=["tables", "fenced_code", "sane_lists"]))
    page = (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{html.escape(title)}</title>"
            f"<style>{CSS}</style></head><body>{body}</body></html>")
    with tempfile.TemporaryDirectory() as tmp:
        page_path = Path(tmp) / "page.html"
        page_path.write_text(page, encoding="utf-8")
        subprocess.run([find_browser(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--user-data-dir={Path(tmp) / 'profile'}", f"--print-to-pdf={target.resolve()}",
                        page_path.resolve().as_uri()], check=True, capture_output=True, timeout=180)
    print(target, target.stat().st_size, "bytes")


if __name__ == "__main__":
    main(sys.argv[1:])
