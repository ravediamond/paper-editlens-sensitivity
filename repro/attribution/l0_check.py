"""L0: recompute the word-deletion statistics from expected/word_loo.json and the lexicon validity (held-out correlation, permutation ceiling,
agreement between the two sources) from expected/loo_all.json; compare with expected/word_deletion.json and expected/lexicon.json."""
import collections, json, random, re, statistics as st
from pathlib import Path

E = Path(__file__).resolve().parent / "expected"; fails = 0
rows = json.loads((E / "loo_all.json").read_text()); wd = json.loads((E / "word_loo.json").read_text())["rows"]
WD = json.loads((E / "word_deletion.json").read_text()); LX = json.loads((E / "lexicon.json").read_text())["validity"]


def check(name, got, want, tol=1e-6):
    global fails
    ok = abs(got - want) <= tol; fails += not ok
    print(f"{'ok ' if ok else 'BAD'} {name}: {got:.4f} (expected {want:.4f})")


d = [r["delta"] for r in wd]
check("word deletions", len(d), WD["n"]); check("mean deletion", st.mean(d), WD["mean"]); check("max deletion", max(d), WD["max"])
check("share |d|<0.01", sum(abs(x) < 0.01 for x in d) / len(d), WD["share_abs_lt_0.01"])


def toks(s):
    return set(re.findall(r"[a-z][a-z'-]+", s.lower()))


wc = [len(r["sentence"].split()) for r in rows]; y = [r["contribution"] for r in rows]; mw, my = st.mean(wc), st.mean(y)
b = sum((a - mw) * (c - my) for a, c in zip(wc, y)) / sum((a - mw) ** 2 for a in wc); a0 = my - b * mw
for r, w in zip(rows, wc):
    r["resid"] = r["contribution"] - (a0 + b * w); r["toks"] = toks(r["sentence"])


def lexicon(rs, minn):
    dd = collections.defaultdict(list)
    for r in rs:
        for t in r["toks"]:
            dd[t].append(r["resid"])
    return {t: (st.mean(v), len(v)) for t, v in dd.items() if len(v) >= minn}


def corr(a, b2):
    ma, mb = st.mean(a), st.mean(b2); da = sum((x - ma) ** 2 for x in a); db = sum((x - mb) ** 2 for x in b2)
    return sum((x - ma) * (z - mb) for x, z in zip(a, b2)) / ((da * db) ** 0.5) if da and db else 0


papers = sorted({r["paper"] for r in rows})


def heldout(rs):
    cs = []
    for p in papers:
        lx = lexicon([r for r in rs if r["paper"] != p], 4); te = [r for r in rows if r["paper"] == p]
        pred = [st.mean([lx[t][0] for t in r["toks"] if t in lx] or [0]) for r in te]; cs.append(corr(pred, [r["resid"] for r in te]))
    return st.mean(cs)


check("sentences", len(rows), LX["sentences"]); check("held-out correlation", heldout(rows), LX["heldout_corr"])
rng = random.Random(1); null = []
for _ in range(200):
    sh = [r["resid"] for r in rows]; rng.shuffle(sh); null.append(heldout([dict(r, resid=s) for r, s in zip(rows, sh)]))
null.sort(); check("permutation mean", st.mean(null), LX["null_mean"]); check("permutation 95th percentile", null[int(0.95 * len(null))], LX["null_p95"])
print("L0 PASS" if not fails else f"L0 FAIL ({fails})")
