"""repro/additivity L0: recompute the summary of PROTOCOL.md from expected/additivity.json and check the hunks (standard library, numpy, scipy)."""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "scripts"))
from summarize import summary  # noqa: E402

P = json.loads((HERE / "expected/additivity.json").read_text())
stored = json.loads((HERE / "expected/additivity_summary.json").read_text())
got = summary(P)
fails = 0


def check(name, cond):
    global fails
    fails += not cond; print(("ok  " if cond else "BAD ") + name)


check("summary recomputed from the per-hunk scores equals the stored summary", json.dumps(got, sort_keys=True) == json.dumps(stored, sort_keys=True))
check("26 changed paragraphs, 46 hunks", (len(P), sum(len(p["hunks"]) for p in P)) == (26, 46))
check("every paragraph has at least one hunk and D = after - before, S = sum of the hunk effects",
      all(p["hunks"] and abs(p["D"] - (p["after"] - p["before"])) < 1e-3 and abs(p["S"] - sum(h["d"] for h in p["hunks"])) < 1e-3 for p in P))
check("every hunk's removed sentences are sentences of the original and its added ones sentences of the rewrite",
      all(all(s in p["before_text"] for s in h["removed"]) and all(s in p["after_text"] for s in h["added"]) for p in P for h in p["hunks"]))
print("L0 PASS" if not fails else "L0 FAIL"); sys.exit(1 if fails else 0)
