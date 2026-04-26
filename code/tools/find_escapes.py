"""Find remaining backslash-escape patterns in a file."""
import re
import sys
from collections import Counter

with open(sys.argv[1], encoding="utf-8") as f:
    s = f.read()
escapes = Counter(re.findall(r"\\(.)", s))
print("Remaining backslash-escape characters:")
for ch, n in escapes.most_common():
    print(f"  {ch!r}: {n}")
