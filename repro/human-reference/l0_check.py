"""L0: recompute the human-reference statistics from expected/rows.json (one row per scored paragraph: paper, group, section type, words, score) and compare
with expected/summary.json. `python3 l0_check.py --write` regenerates summary.json from the rows. Standard library only."""
import collections, json, statistics as st, sys
from pathlib import Path

E = Path(__file__).resolve().parent / "expected"; MIN_PARAS = 8
TYPES = ["introduction", "related", "method", "results", "conclusion", "other"]


def p90(x):
    return sorted(x)[int(0.9 * (len(x) - 1))]


def wmean(rs):
    return sum(r["score"] * r["words"] for r in rs) / sum(r["words"] for r in rs)


def summarize(rows):
    by = collections.defaultdict(list)
    for r in rows:
        by[(r["group"], r["paper"])].append(r)
    hum = {p: v for (g, p), v in by.items() if g == "human" and len(v) >= MIN_PARAS}
    dropped = sorted(p for (g, p), v in by.items() if g == "human" and len(v) < MIN_PARAS)
    H = [r for v in hum.values() for r in v]; means = [wmean(v) for v in hum.values()]
    ours = {p: v for (g, p), v in by.items() if g == "ours"}; om = {p: wmean(v) for p, v in ours.items()}
    S = {"human_papers": len(hum), "dropped": dropped, "human_paragraphs": len(H), "paper_mean_median": st.median(means), "paper_mean_min": min(means),
         "paper_mean_max": max(means), "para_median": st.median(r["score"] for r in H), "share_gt_015": sum(r["score"] > 0.15 for r in H) / len(H),
         "share_gt_025": sum(r["score"] > 0.25 for r in H) / len(H), "ours_paragraphs": sum(len(v) for v in ours.values()), "ours_means": om,
         "ours_above_human_max": sum(m > max(means) for m in om.values()), "ours_above_median": sum(m > st.median(means) for m in om.values()),
         "ours_share_gt_015": sum(r["score"] > 0.15 for v in ours.values() for r in v) / sum(len(v) for v in ours.values()), "types": {}}
    for t in TYPES:
        x = [r["score"] for r in H if r["type"] == t]
        S["types"][t] = {"n": len(x), "median": st.median(x), "p90": p90(x), "share_gt_015": sum(v > 0.15 for v in x) / len(x)}
    return S


def main():
    rows = json.loads((E / "rows.json").read_text()); S = summarize(rows)
    if "--write" in sys.argv:
        (E / "summary.json").write_text(json.dumps(S, indent=1)); print("written"); return
    W = json.loads((E / "summary.json").read_text()); fails = 0

    def check(name, got, want, tol=1e-9):
        nonlocal fails
        ok = abs(got - want) <= tol; fails += not ok
        print(f"{'ok ' if ok else 'BAD'} {name}: {got:.4f} (expected {want:.4f})")
    for k in ["human_papers", "human_paragraphs", "paper_mean_median", "paper_mean_min", "paper_mean_max", "para_median", "share_gt_015", "share_gt_025",
              "ours_paragraphs", "ours_above_human_max", "ours_above_median", "ours_share_gt_015"]:
        check(k, S[k], W[k])
    for p, m in S["ours_means"].items():
        check(f"ours {p}", m, W["ours_means"][p])
    for t, d in S["types"].items():
        for k, v in d.items():
            check(f"{t} {k}", v, W["types"][t][k])
    assert S["dropped"] == W["dropped"], (S["dropped"], W["dropped"])
    print("L0 PASS" if not fails else f"L0 FAIL ({fails})")


if __name__ == "__main__":
    main()
