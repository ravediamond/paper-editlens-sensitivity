import json, re, random, statistics as st, collections
rows = json.load(open("loo_all.json"))
def toks(s): return set(w for w in re.findall(r"[a-z][a-z'-]+", s.lower()))
wc = [len(r["sentence"].split()) for r in rows]; y = [r["contribution"] for r in rows]
mw, my = st.mean(wc), st.mean(y)
b = sum((a-mw)*(c-my) for a, c in zip(wc, y))/sum((a-mw)**2 for a in wc); a0 = my - b*mw
for r, w in zip(rows, wc): r["resid"] = r["contribution"] - (a0 + b*w); r["toks"] = toks(r["sentence"])
print(f"{len(rows)} sentences; contribution mean {my:+.4f}; slope per word {b:+.5f}")
def lexicon(rs, minn):
    d = collections.defaultdict(list)
    for r in rs:
        for t in r["toks"]: d[t].append(r["resid"])
    return {t: (st.mean(v), len(v)) for t, v in d.items() if len(v) >= minn}
# leave-one-paper-out validation
papers = sorted({r["paper"] for r in rows}); corrs = []
def corr(a, b):
    ma, mb = st.mean(a), st.mean(b); da = sum((x-ma)**2 for x in a); db = sum((x-mb)**2 for x in b)
    return sum((x-ma)*(z-mb) for x, z in zip(a, b))/((da*db)**0.5) if da and db else 0
for p in papers:
    lx = lexicon([r for r in rows if r["paper"] != p], 4); te = [r for r in rows if r["paper"] == p]
    pred = [st.mean([lx[t][0] for t in r["toks"] if t in lx] or [0]) for r in te]
    c = corr(pred, [r["resid"] for r in te]); corrs.append(c); print(f"  held out {p:28s} n={len(te):3d} corr(pred, resid)={c:+.3f}")
print("mean held-out corr", round(st.mean(corrs), 3))
# permutation null for held-out correlation (shuffle labels in training)
rng = random.Random(1); null = []
for _ in range(100):
    sh = [r["resid"] for r in rows]; rng.shuffle(sh); rs = [dict(r, resid=s) for r, s in zip(rows, sh)]
    cs = []
    for p in papers:
        lx = lexicon([r for r in rs if r["paper"] != p], 4); te = [r for r in rows if r["paper"] == p]; tr = [r for r in rs if r["paper"] == p]
        pred = [st.mean([lx[t][0] for t in r["toks"] if t in lx] or [0]) for r in te]; cs.append(corr(pred, [r["resid"] for r in te]))
    null.append(st.mean(cs))
print("permutation null mean", round(st.mean(null), 3), "95th pct", round(sorted(null)[94], 3))
lx = lexicon(rows, 6)
# bootstrap CI for each word
d = collections.defaultdict(list)
for r in rows:
    for t in r["toks"]: d[t].append(r["resid"])
out = []
for t, (m, n) in lx.items():
    v = d[t]; bs = sorted(st.mean(rng.choice(v) for _ in v) for _ in range(500)); out.append((t, m, n, bs[12], bs[487], len({r["paper"] for r in rows if t in r["toks"]})))
out.sort(key=lambda x: x[1])
json.dump(out, open("lexicon_raw.json", "w"))
print("LOWER (negative = lowers the paragraph score)"); [print(f"  {t:16s} {m:+.3f} n={n:3d} CI[{lo:+.3f},{hi:+.3f}] papers={pp}") for t, m, n, lo, hi, pp in out[:30]]
print("RAISE"); [print(f"  {t:16s} {m:+.3f} n={n:3d} CI[{lo:+.3f},{hi:+.3f}] papers={pp}") for t, m, n, lo, hi, pp in out[-30:]]
