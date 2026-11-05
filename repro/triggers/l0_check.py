"""L0: recompute the mean change of every edit of the second trigger battery (expected/battery2.json, hosts not chosen by their score) from the stored
per-host deltas, and the host base means from the stored host scores. Bootstrap CIs are not stored here: the paper's CIs are recomputed with the seed below.
Standard library only."""
import json, random, statistics as st
from pathlib import Path

E = Path(__file__).resolve().parent / "expected"; B = json.loads((E / "battery2.json").read_text()); S = json.loads((E / "trigger_summary.json").read_text()); fails = 0


def check(name, got, want, tol=1e-9):
    global fails
    ok = abs(got - want) <= tol; fails += not ok
    print(f"{'ok ' if ok else 'BAD'} {name}: {got:.4f} (expected {want:.4f})")


for g in ("human_random", "ours"):
    check(f"{g} hosts", len(B["base"][g]), S["hosts"][g]); check(f"{g} base mean", st.mean(B["base"][g]), S["base_mean"][g])
    for k, d in B["raw"][g].items():
        check(f"{g} {k} mean", st.mean(d), S["effects"][g][k]["mean"])
        rng = random.Random(0); bs = sorted(st.mean(rng.choice(d) for _ in d) for _ in range(1000))
        check(f"{g} {k} CI low", bs[25], S["effects"][g][k]["ci"][0]); check(f"{g} {k} CI high", bs[974], S["effects"][g][k]["ci"][1])
print("L0 PASS" if not fails else f"L0 FAIL ({fails})")
