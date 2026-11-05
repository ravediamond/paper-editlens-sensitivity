"""L0: recompute the mean change of every controlled edit from the stored per-paragraph deltas (expected/exp_transforms.json, exp_insert.json),
the changed-paragraph subsets from the paragraph texts (expected/paragraphs.json), and compare with the stored effects. Bootstrap CIs are
read, and checked only to contain the recomputed mean. Standard library only."""
import json, re, statistics as st
from pathlib import Path

E = Path(__file__).resolve().parent / "expected"; fails = 0
T = json.loads((E / "exp_transforms.json").read_text()); I = json.loads((E / "exp_insert.json").read_text())
S = json.loads((E / "subset_effects.json").read_text()); texts = json.loads((E / "paragraphs.json").read_text())


def check(name, got, want, tol=1e-6):
    global fails
    ok = abs(got - want) <= tol; fails += not ok
    print(f"{'ok ' if ok else 'BAD'} {name}: {got:.4f} (expected {want:.4f})")


assert len(texts) == len(T["paras"]) == 62
for n, d in T["raw"].items():
    check(f"transform {n} mean", st.mean(d), T["effects"][n]["mean_delta"])
    lo, hi = T["effects"][n]["ci"]; check(f"transform {n} mean inside CI", float(lo - 1e-9 <= st.mean(d) <= hi + 1e-9), 1.0)
for n, d in I["raw"].items():
    check(f"insert {n} mean", st.mean(d), I["effects"][n]["mean"])
    check(f"insert {n} share up", sum(x > 0.005 for x in d) / len(d), I["effects"][n]["share_up"])
    lo, hi = I["effects"][n]["ci"]; check(f"insert {n} mean inside CI", float(lo - 1e-9 <= st.mean(d) <= hi + 1e-9), 1.0)
has = {"semicolons_to_periods": lambda t: ";" in t, "colons_to_periods": lambda t: re.search(r"[a-z\)]: [a-z]", t) is not None,
       "drop_parentheticals": lambda t: re.search(r"\([^()]*\)", t) is not None, "split_at_and_but": lambda t: re.search(r", (and|but) ", t) is not None,
       "numbers_masked": lambda t: re.search(r"\d", t) is not None, "we_to_I": lambda t: re.search(r"\b[Ww]e\b|\b[Oo]ur\b", t) is not None}
for n, f in has.items():
    d = [x for x, t in zip(T["raw"][n], texts) if f(t)]
    check(f"subset {n} n", len(d), S[n]["n"]); check(f"subset {n} mean", st.mean(d), S[n]["mean"])
print("L0 PASS" if not fails else f"L0 FAIL ({fails})")
