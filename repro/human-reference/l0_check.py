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


def excluded():
    return {(p, h) for p, h, _ in json.loads((E / "excluded_back_matter.json").read_text())}


def summarize(rows):
    by = collections.defaultdict(list)
    ex = excluded()
    nex = collections.Counter()
    for r in rows:
        if (r["paper"], r["sha1"]) in ex:
            nex[r["group"]] += 1
            continue
        by[(r["group"], r["paper"])].append(r)
    hum = {p: v for (g, p), v in by.items() if g == "human" and len(v) >= MIN_PARAS}
    dropped = sorted(p for (g, p), v in by.items() if g == "human" and len(v) < MIN_PARAS)
    H = [r for v in hum.values() for r in v]; means = [wmean(v) for v in hum.values()]
    ours = {p: v for (g, p), v in by.items() if g == "ours"}; om = {p: wmean(v) for p, v in ours.items()}
    S = {"human_papers": len(hum), "dropped": dropped, "human_paragraphs": len(H), "paper_mean_median": st.median(means), "paper_mean_min": min(means),
         "paper_mean_max": max(means), "para_median": st.median(r["score"] for r in H), "share_gt_015": sum(r["score"] > 0.15 for r in H) / len(H),
         "share_gt_025": sum(r["score"] > 0.25 for r in H) / len(H), "excluded_human": nex["human"], "excluded_ours": nex["ours"], "ours_paragraphs": sum(len(v) for v in ours.values()), "ours_means": om,
         "ours_above_human_max": sum(m > max(means) for m in om.values()), "ours_above_median": sum(m > st.median(means) for m in om.values()),
         "ours_share_gt_015": sum(r["score"] > 0.15 for v in ours.values() for r in v) / sum(len(v) for v in ours.values()), "types": {}}
    for t in TYPES:
        x = [r["score"] for r in H if r["type"] == t]
        S["types"][t] = {"n": len(x), "median": st.median(x), "p90": p90(x), "share_gt_015": sum(v > 0.15 for v in x) / len(x)}
    return S


def rank(x):
    o = sorted(range(len(x)), key=lambda i: x[i]); r = [0] * len(x)
    for k, i in enumerate(o):
        r[i] = k
    return r


def corr(a, b):
    ma, mb = st.mean(a), st.mean(b); da = sum((x - ma) ** 2 for x in a); db = sum((x - mb) ** 2 for x in b)
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (da * db) ** 0.5 if da and db else 0


def style_summary():
    ex = excluded(); R = [r for r in json.loads((E / "style_rows.json").read_text()) if (r["paper"], r["sha1"]) not in ex]
    H = [r for r in R if r["group"] == "human" and r["paper"] not in DROPPED]; O = [r for r in R if r["group"] == "ours"]
    lo = [r for r in H if r["score"] < 0.05]; hi = [r for r in H if r["score"] > 0.15]; sc = [r["score"] for r in H]; out = {"n_human": len(H), "n_low": len(lo), "n_high": len(hi), "n_ours": len(O), "features": {}}
    for k in [k for k in H[0] if k not in ("paper", "group", "sha1", "type", "score")]:
        out["features"][k] = {"spearman": corr(rank([r[k] for r in H]), rank(sc)), "low": st.mean(r[k] for r in lo), "high": st.mean(r[k] for r in hi), "ours": st.mean(r[k] for r in O)}
    T = [json.loads(l) for l in (E / "style_trials.jsonl").read_text().splitlines()]; by = collections.defaultdict(list)
    for t in T:
        by[(t["paper"], t["para"])].append(t)
    d = []
    for v in by.values():
        cur = [x for x in v if x["cand"] == 0][0]["score"]; d += [x["score"] - cur for x in v if x["cand"] > 0]
    best = [min(x["score"] for x in v if x["cand"] > 0) - [x for x in v if x["cand"] == 0][0]["score"] for v in by.values()]
    out["trials"] = {"paragraphs": len(by), "candidates": len(d), "lower": sum(x < -0.005 for x in d), "higher": sum(x > 0.005 for x in d), "paragraphs_best_lower": sum(b < -0.005 for b in best), "mean_change": st.mean(d)}
    return out


DROPPED = ["2002.12360"]


def main():
    rows = json.loads((E / "rows.json").read_text()); S = summarize(rows); Y = style_summary()
    if "--write" in sys.argv:
        (E / "summary.json").write_text(json.dumps(S, indent=1)); (E / "style_summary.json").write_text(json.dumps(Y, indent=1)); print("written"); return
    W = json.loads((E / "summary.json").read_text()); fails = 0

    def check(name, got, want, tol=1e-9):
        nonlocal fails
        ok = abs(got - want) <= tol; fails += not ok
        print(f"{'ok ' if ok else 'BAD'} {name}: {got:.4f} (expected {want:.4f})")
    for k in ["human_papers", "human_paragraphs", "excluded_human", "excluded_ours", "paper_mean_median", "paper_mean_min", "paper_mean_max", "para_median", "share_gt_015", "share_gt_025",
              "excluded_human", "excluded_ours", "ours_paragraphs", "ours_above_human_max", "ours_above_median", "ours_share_gt_015"]:
        check(k, S[k], W[k])
    for p, m in S["ours_means"].items():
        check(f"ours {p}", m, W["ours_means"][p])
    for t, d in S["types"].items():
        for k, v in d.items():
            check(f"{t} {k}", v, W["types"][t][k])
    assert S["dropped"] == W["dropped"], (S["dropped"], W["dropped"])
    Z = json.loads((E / "style_summary.json").read_text())
    for k in ["n_human", "n_low", "n_high", "n_ours"]:
        check("style " + k, Y[k], Z[k])
    for f, d in Y["features"].items():
        for k, v in d.items():
            check(f"style {f} {k}", v, Z["features"][f][k], 1e-9)
    for k, v in Y["trials"].items():
        check("trials " + k, v, Z["trials"][k], 1e-9)
    print("L0 PASS" if not fails else f"L0 FAIL ({fails})")


if __name__ == "__main__":
    main()
