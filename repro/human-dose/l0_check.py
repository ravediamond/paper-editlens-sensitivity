"""L0: recompute every per-bin mean of expected/summary.json from the stored rows (pairs.json, magnitudes.json, scores.json, ai_rows.json)
and compare; check the bar verdicts follow from the stored ratio CIs. Prints "L0 PASS (no rows yet)" while the experiment has no data,
so `make l0` passes before the first number. Standard library only."""
import json, statistics as st, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
from common import BINS, bin_of  # noqa: E402

E = Path(__file__).resolve().parent / "expected"; fails = 0
if not (E / "summary.json").exists():
    print("L0 PASS (no rows yet: the protocol is frozen, no number exists)"); sys.exit(0)
S = json.loads((E / "summary.json").read_text())
P = json.loads((E / "pairs.json").read_text()); M = {(m["base_id"], m["ver_id"]): m for m in json.loads((E / "magnitudes.json").read_text())}
SC = json.loads((E / "scores.json").read_text())
A = json.loads((E / ("ai_rows_fallback.json" if S["ai_source"] == "fallback" else "ai_rows.json")).read_text())


def check(name, got, want, tol=1e-6):
    global fails
    ok = abs(got - want) <= tol; fails += not ok
    print(f"{'ok ' if ok else 'BAD'} {name}: {got:.4f} (expected {want:.4f})")


H = [{"cosine": M[(q["base_id"], q["ver_id"])]["cosine"], "delta": round(SC[q["ver_id"]]["s"] - SC[q["base_id"]]["s"], 4)}
     for q in P if q["kind"] == "pair" and (q["base_id"], q["ver_id"]) in M and q["ver_id"] in SC]
for b in range(len(BINS)):
    for name, rows, stored in (("human", H, S["human_bins"][str(b)]), ("ai", A, S["ai_bins"][str(b)])):
        rs = [r["delta"] for r in rows if bin_of(r["cosine"]) == b]
        check(f"{name} bin {b} n", len(rs), stored["n"])
        if rs:
            check(f"{name} bin {b} mean", st.mean(rs), stored["mean"], 5e-5); check(f"{name} bin {b} |mean|", st.mean(map(abs, rs)), stored["abs_mean"], 5e-5)
            lo, hi = stored["mean_ci"]; check(f"{name} bin {b} mean inside CI", float(lo - 1e-9 <= st.mean(rs) <= hi + 1e-9), 1.0)
ev = {b: r for b, r in S["ratio"].items() if r}
inside = all(0.5 <= r["ci"][0] and r["ci"][1] <= 2.0 for r in ev.values()); outside = any(r["ci"][1] < 0.5 or r["ci"][0] > 2.0 for r in ev.values())
want = "not proven" if not ev else "pass" if inside else "fail" if outside else "not proven"
check("B1 follows from ratio CIs", float(S["verdicts"]["B1_magnitude_driven"] == want), 1.0)
print("L0 PASS" if not fails else f"L0 FAIL ({fails})")
