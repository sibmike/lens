"""Mechanical cleanup pass for the LENS pre-print papers.

Strips Google-Docs export artifacts and removes all <<NOTE: ...>> editorial
markers in place. Run on a copy of the paper, not the original.

Usage:
    /c/Users/mikea/anaconda3/python.exe code/tools/cleanup_paper.py paperN_v2.md
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def strip_escapes(text: str) -> str:
    # Order matters: do specific multi-char escapes before single-char.
    # Escaped equals, hash, ampersand, brackets, period, asterisk, underscore.
    text = re.sub(r"\\([=#&\[\]\.\*_<>~+\-!()])", r"\1", text)
    # Escaped backslashes that survived as `\\`
    text = text.replace("\\\\", "\\")
    return text


def strip_notes(text: str) -> str:
    # <<NOTE: ...>> -- can span lines, can be wrapped in escaped angle brackets.
    # The escapes have already been stripped by strip_escapes(), so by the time
    # this runs, all NOTEs look like literal `<<NOTE: ...>>`.
    text = re.sub(r"<<NOTE:.*?>>", "", text, flags=re.DOTALL)
    # Clean up double-spaces and orphaned space-before-period left by removals.
    text = re.sub(r"  +", " ", text)
    text = re.sub(r" \n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def fix_headings(text: str) -> str:
    # `## **0\. Notation...**` -> `## 0. Notation...`
    # The escape on the period is already gone after strip_escapes.
    # Now just strip bold markers from headings.
    def fix_one(match: re.Match) -> str:
        hashes = match.group(1)
        title = match.group(2)
        # Remove leading/trailing **
        title = re.sub(r"^\*\*(.+)\*\*$", r"\1", title.strip())
        return f"{hashes} {title}"

    text = re.sub(r"^(#+)\s+(.+)$", fix_one, text, flags=re.M)
    return text


def normalize_smart_quotes(text: str) -> str:
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("‘", "'").replace("’", "'")
    return text


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Usage: cleanup_paper.py <path-to-paper.md>")
    path = Path(sys.argv[1])
    if not path.is_file():
        sys.exit(f"Not a file: {path}")
    raw = path.read_text(encoding="utf-8")

    cleaned = raw
    cleaned = strip_escapes(cleaned)
    cleaned = strip_notes(cleaned)
    cleaned = fix_headings(cleaned)
    cleaned = normalize_smart_quotes(cleaned)

    path.write_text(cleaned, encoding="utf-8")
    print(f"Cleaned {path}")
    print(f"  Before: {len(raw):>7d} chars, {raw.count(chr(10)):>5d} lines")
    print(f"  After:  {len(cleaned):>7d} chars, {cleaned.count(chr(10)):>5d} lines")
    print(f"  Removed: {len(raw) - len(cleaned)} chars")


if __name__ == "__main__":
    main()
