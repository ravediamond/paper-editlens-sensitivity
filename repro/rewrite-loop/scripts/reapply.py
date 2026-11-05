"""reapply.py <paper-name> <source file in the repo> : replay my paragraph rewrites (orig -> final) onto the repo's current source."""
import sys, re
from pathlib import Path
name, srcname = sys.argv[1], sys.argv[2]
W = Path("work"); repo = Path.home()/f"scratch/paper-repos/paper-{name}/paper"
def paras(t):
    out, cur = [], []
    for l in t.split("\n") + [""]:
        if l.strip(): cur.append(l)
        elif cur: out.append("\n".join(cur)); cur = []
    return out
po, pn = paras((W/f"{name}.orig.md").read_text()), paras((W/f"{name}.src.md").read_text())
assert len(po) == len(pn), (len(po), len(pn))
up = (repo/srcname).read_text(); n = 0
for a, b in zip(po, pn):
    if a == b: continue
    assert up.count(a) == 1, f"upstream paragraph not found exactly once: {a[:70]!r} ({up.count(a)})"
    up = up.replace(a, b); n += 1
(repo/srcname).write_text(up); print(name, "paragraphs replayed:", n)
