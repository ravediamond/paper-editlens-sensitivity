"""repro/additivity: apply the hunks of each rewrite one at a time to the original paragraph and score them
(PROTOCOL.md). Needs the scorer server of the working repository (`ws paper-polish serve`).

    python3 repro/additivity/scripts/additivity.py   (from the repository root)
"""
import difflib
import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/jetson/workspace/road-to-robotics/scripts")
import paper_polish as PP  # noqa: E402
import paper_sentences as S  # noqa: E402

HERE = Path(__file__).resolve().parent
ROWS = HERE.parents[1] / "rewrite-loop/expected/before_after_rows.json"
OUT = HERE.parent / "expected/additivity.json"

rows = [dict(r, paper=p) for p, v in json.loads(ROWS.read_text()).items() for r in v if r["before_text"] != r["after_text"]]
paras, texts = [], []
for r in rows:
    a, b = S.split_sentences(r["before_text"]), S.split_sentences(r["after_text"])
    ops = [o for o in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes() if o[0] != "equal"]
    hunks = []
    for tag, i1, i2, j1, j2 in ops:
        kind = "delete" if j1 == j2 else "insert" if i1 == i2 else "replace"
        variant = " ".join(a[:i1] + b[j1:j2] + a[i2:])
        hunks.append({"type": kind, "removed": a[i1:i2], "added": b[j1:j2], "variant": variant})
    paras.append({"paper": r["paper"], "para": r["para"], "sec": r["sec"], "before_text": r["before_text"], "after_text": r["after_text"], "hunks": hunks})
    texts += [r["before_text"], r["after_text"]] + [h["variant"] for h in hunks]
sc = PP.score(texts)
k = 0
for p in paras:
    p["before"], p["after"] = sc[k], sc[k + 1]; k += 2
    for h in p["hunks"]:
        h["score"] = sc[k]; h["d"] = round(h["score"] - p["before"], 4); k += 1
    p["D"] = round(p["after"] - p["before"], 4); p["S"] = round(sum(h["d"] for h in p["hunks"]), 4)
OUT.write_text(json.dumps(paras, indent=1))
print(len(paras), "paragraphs,", sum(len(p["hunks"]) for p in paras), "hunks")
