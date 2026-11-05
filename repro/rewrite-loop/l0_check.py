"""L0: recompute the rewrite-loop numbers (candidates, share improved, mean best drop) from expected/iterlog.jsonl and the paper means
from expected/before_after_rows.json (one row per paragraph: words and score before and after); compare with expected/results.json."""
import collections, json, statistics as st
from pathlib import Path

E = Path(__file__).resolve().parent / "expected"; fails = 0
R = json.loads((E / "results.json").read_text()); rows = [json.loads(l) for l in (E / "iterlog.jsonl").read_text().splitlines()]
BA = json.loads((E / "before_after_rows.json").read_text())


def check(name, got, want, tol=1e-6):
    global fails
    ok = abs(got - want) <= tol; fails += not ok
    print(f"{'ok ' if ok else 'BAD'} {name}: {got:.4f} (expected {want:.4f})")


g = collections.defaultdict(list)
for r in rows:
    g[(r["paper"], r["para"], r["round"])].append(r)
tot = low = 0; best = []
for v in g.values():
    c0 = [x for x in v if x["cand"] == 0][0]["score"]; cs = [x for x in v if x["cand"] > 0]
    for x in cs:
        tot += 1; low += x["score"] < c0 - 0.005
    ok = [x["score"] - c0 for x in cs if x["ph_ok"]]
    if ok:
        best.append(min(ok))
it = R["iteration"]
check("candidates", tot, it["candidates"]); check("lower", low, it["lower"]); check("paragraph rounds", len(best), it["paragraph_rounds"])
check("mean best delta", st.mean(best), it["mean_best_delta"]); check("share improved", sum(b < -0.005 for b in best) / len(best), it["share_improved"])
for p, rs in BA.items():
    b = sum(r["before"] * r["words_before"] for r in rs) / sum(r["words_before"] for r in rs)
    a = sum(r["after"] * r["words_after"] for r in rs) / sum(r["words_after"] for r in rs)
    check(f"{p} mean before", b, R["before_after"][p]["before"], 2e-3); check(f"{p} mean after", a, R["before_after"][p]["after"], 2e-3)
    check(f"{p} paragraphs", len(rs), R["before_after"][p]["paragraphs"])
print("L0 PASS" if not fails else f"L0 FAIL ({fails})")
