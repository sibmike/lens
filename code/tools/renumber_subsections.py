"""Renumber `### A. Title` -> `### N.1 Title` per parent `## N. ...` section."""
import re
import sys
from pathlib import Path

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

path = Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

current_section = None  # e.g. "3"
counter = 0

out = []
for line in lines:
    m_h2 = re.match(r"^## (\d+)\. ", line)
    if m_h2:
        current_section = m_h2.group(1)
        counter = 0
        out.append(line)
        continue
    m_h3 = re.match(r"^### ([A-Z])\. (.+)$", line)
    if m_h3 and current_section:
        idx = LETTERS.index(m_h3.group(1)) + 1
        title = m_h3.group(2)
        out.append(f"### {current_section}.{idx} {title}\n")
        counter += 1
        continue
    out.append(line)

path.write_text("".join(out), encoding="utf-8")
print(f"Renumbered subsections in {path}")
