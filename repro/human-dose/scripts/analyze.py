#!/usr/bin/env python3
"""The curve, the bars and the production-run gate (PROTOCOL §3–§5), from the stored rows only (CPU, seconds).

    analyze.py              write expected/summary.json and print the per-bin table
    analyze.py --progress   how many baseline paragraphs have a version, per bin counts, which bins are evaluable

Human rows: pairs.json (kind == pair) + magnitudes.json + scores.json. AI rows: ai_rows.json (or ai_rows_fallback.json with --fallback).
Bootstrap: 2,000 resamples, seed 0, unit = baseline paragraph (human side) / row (AI side)."""
import random, statistics as st, sys
from collections import defaultdict
from common import *  # noqa: F401,F403

B, SEED = 2000, 0
HUMAN_P90, HUMAN_MED = 0.177, 0.071  # ../human-reference/expected/summary.json: para p90 of 'other' type rounded; paper-mean median


def boot(groups, f, b=B, seed=SEED):
    """groups: list of lists (one per resampling unit). f(flat list) -> statistic."""
    rng = random.Random(seed); n = len(groups)
    vals = []
    for _ in range(b):
        s = [x for g in (groups[rng.randrange(n)] for _ in range(n)) for x in g]
        vals.append(f(s))
    vals.sort()
    return vals[int(0.025 * b)], vals[int(0.975 * b) - 1]


def human_rows():
    P, M, S = load("pairs.json") or [], {(m["base_id"], m["ver_id"]): m for m in (load("magnitudes.json") or [])}, load("scores.json") or {}
    rows = []
    for q in P:
        if q["kind"] != "pair" or (q["base_id"], q["ver_id"]) not in M or q["ver_id"] not in S:
            continue
        m = M[(q["base_id"], q["ver_id"])]
        rows.append({**q, "cosine": m["cosine"], "sng": m["sng"], "delta": round(S[q["ver_id"]]["s"] - S[q["base_id"]]["s"], 4),
                     "s_ver": S[q["ver_id"]]["s"], "s_base": S[q["base_id"]]["s"], "dw": q["words_ver"] - q["words_base"]})
    return rows


def per_bin(rows, unit_key):
    out = {}
    for b in range(len(BINS)):
        rs = [r for r in rows if bin_of(r["cosine"]) == b]
        units = defaultdict(list)
        for r in rs:
            units[r[unit_key]].append(r["delta"])
        g = list(units.values())
        if not rs:
            out[b] = {"n": 0}; continue
        mean = st.mean(r["delta"] for r in rs); amean = st.mean(abs(r["delta"]) for r in rs)
        out[b] = {"n": len(rs), "units": len(g), "mean": round(mean, 4), "mean_ci": [round(v, 4) for v in boot(g, st.mean)],
                  "abs_mean": round(amean, 4), "abs_ci": [round(v, 4) for v in boot(g, lambda s: st.mean(map(abs, s)))],
                  "share_below_p90": round(sum(r.get("s_ver", 1) < HUMAN_P90 for r in rs) / len(rs), 3)}
    return out


def ratio_ci(hrows, arows, b):
    hu = defaultdict(list); au = defaultdict(list)
    for r in hrows:
        if bin_of(r["cosine"]) == b: hu[r["base_id"]].append(abs(r["delta"]))
    for r in arows:
        if bin_of(r["cosine"]) == b: au[r["idx"]].append(abs(r["delta"]))
    H, A = list(hu.values()), list(au.values())
    if sum(map(len, H)) < 20 or len(H) < 10 or sum(map(len, A)) < 20:
        return None
    rng = random.Random(SEED); vals = []
    for _ in range(B):
        h = [x for g in (H[rng.randrange(len(H))] for _ in range(len(H))) for x in g]
        a = [x for g in (A[rng.randrange(len(A))] for _ in range(len(A))) for x in g]
        vals.append(st.mean(h) / max(1e-6, st.mean(a)))
    vals.sort()
    return {"R": round(st.mean(x for g in H for x in g) / max(1e-6, st.mean(x for g in A for x in g)), 3), "ci": [round(vals[int(0.025 * B)], 3), round(vals[int(0.975 * B) - 1], 3)], "n_h": len(H), "n_a": len(A)}


def main(progress=False, fallback=False):
    H = human_rows(); A = load("ai_rows_fallback.json" if fallback else "ai_rows.json") or []
    S = load("scores.json") or {}; V = load("versions.json") or {}
    base_ids = {b["id"] for e in V.values() for b in e["baseline"]}
    nulls = [abs(S[i]["s"] - S[i]["s2"]) for i in base_ids if i in S and "s2" in S[i]]
    hb, ab = per_bin(H, "base_id"), per_bin(A, "idx")
    covered = len({r["base_id"] for r in H})
    print(f"baseline paragraphs with a version: {covered} (need 40); human rows {len(H)}; AI rows {len(A)}; identity null mean {st.mean(nulls) if nulls else None}")
    print("bin        human n  mean dΔ         |Δ|      <p90   | AI n   mean Δ      |Δ|     | R [ci]")
    R, verdict = {}, {}
    for b, (lo, hi) in enumerate(BINS):
        h, a = hb[b], ab[b]
        r = ratio_ci(H, A, b); R[b] = r
        print(f"[{lo:.2f},{hi:.2f}) {h.get('n', 0):4d} {h.get('mean', ''):>8} {h.get('abs_mean', ''):>8} {h.get('share_below_p90', ''):>6} | {a.get('n', 0):4d} {a.get('mean', ''):>8} {a.get('abs_mean', ''):>8} | {r}")
    if progress:
        return
    ev = {b: r for b, r in R.items() if r}
    inside = all(0.5 <= r["ci"][0] and r["ci"][1] <= 2.0 for r in ev.values())
    outside = any(r["ci"][1] < 0.5 or r["ci"][0] > 2.0 for r in ev.values())
    above = sum(r["ci"][0] > 2.0 for r in ev.values()); below = sum(r["ci"][1] < 0.5 for r in ev.values())
    verdict["B1_magnitude_driven"] = "not proven" if not ev else "pass" if inside else "fail" if outside else "not proven"
    verdict["B2_last_editor"] = "pass" if above >= 2 else "fail" if len(ev) >= 2 and above == 0 else "not proven"
    verdict["B3_robust_to_polish"] = "pass" if below >= 2 else "fail" if len(ev) >= 2 and below == 0 else "not proven"
    # B4 reword vs content
    b4 = {}
    for b in range(len(BINS)):
        c = [r for r in H if bin_of(r["cosine"]) == b and r["edit_type"] == "content"]; w = [r for r in H if bin_of(r["cosine"]) == b and r["edit_type"] == "reword"]
        if len(c) >= 20 and len(w) >= 20 and len({r["base_id"] for r in c}) >= 10 and len({r["base_id"] for r in w}) >= 10:
            d = st.mean(r["delta"] for r in c) - st.mean(r["delta"] for r in w)
            rng = random.Random(SEED); vals = []
            for _ in range(B):
                vals.append(st.mean(rng.choice(c)["delta"] for _ in c) - st.mean(rng.choice(w)["delta"] for _ in w))
            vals.sort(); b4[b] = {"diff": round(d, 4), "ci": [round(vals[int(0.025 * B)], 4), round(vals[int(0.975 * B) - 1], 4)], "separate": vals[int(0.025 * B)] > 0 or vals[int(0.975 * B) - 1] < 0}
    verdict["B4_report_separately"] = any(v["separate"] for v in b4.values()) if b4 else "not proven"
    half = next((f"[{BINS[b][0]:.2f},{BINS[b][1]:.2f})" for b in range(len(BINS)) if hb[b].get("share_below_p90", 0) >= 0.5 and hb[b].get("n", 0) >= 20), None)
    gate = {"covered": covered, "evaluable_bins": len(ev), "identity_null": round(st.mean(nulls), 5) if nulls else None,
            "production_run_allowed": covered >= 40 and len(ev) >= 3 and bool(nulls) and st.mean(nulls) < 0.01}
    out = {"human_bins": hb, "ai_bins": ab, "ratio": R, "verdicts": verdict, "B4": b4, "first_bin_half_below_p90": half, "gate": gate,
           "ai_source": "fallback" if fallback else "dataset", "human_p90": HUMAN_P90, "human_paper_median": HUMAN_MED}
    dump("summary.json", out)
    print(verdict, "half below p90 first at", half, "production gate", gate)


if __name__ == "__main__":
    main("--progress" in sys.argv, "--fallback" in sys.argv)
