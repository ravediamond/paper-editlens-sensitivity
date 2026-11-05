import json, re, random, statistics as st, collections
rows = json.load(open("loo_all.json")); wd = json.load(open("word_loo.json"))["rows"]
def toks(s): return set(re.findall(r"[a-z][a-z'-]+", s.lower()))
wc = [len(r["sentence"].split()) for r in rows]; y = [r["contribution"] for r in rows]
mw, my = st.mean(wc), st.mean(y); b = sum((a-mw)*(c-my) for a, c in zip(wc, y))/sum((a-mw)**2 for a in wc); a0 = my-b*mw
for r, w in zip(rows, wc): r["resid"] = r["contribution"]-(a0+b*w); r["toks"] = toks(r["sentence"])
def lexicon(rs, minn):
    d = collections.defaultdict(list)
    for r in rs:
        for t in r["toks"]: d[t].append(r["resid"])
    return {t: (st.mean(v), len(v)) for t, v in d.items() if len(v) >= minn}
def corr(a, b):
    ma, mb = st.mean(a), st.mean(b); da = sum((x-ma)**2 for x in a); db = sum((x-mb)**2 for x in b)
    return sum((x-ma)*(z-mb) for x, z in zip(a, b))/((da*db)**0.5) if da and db else 0
papers = sorted({r["paper"] for r in rows})
def heldout(rs):
    cs = []
    for p in papers:
        lx = lexicon([r for r in rs if r["paper"] != p], 4); te = [r for r in rows if r["paper"] == p]; tr = {id(x): x for x in rs}
        pred = [st.mean([lx[t][0] for t in r["toks"] if t in lx] or [0]) for r in te]; cs.append(corr(pred, [r["resid"] for r in te]))
    return st.mean(cs)
ho = heldout(rows); rng = random.Random(1); null = []
for _ in range(200):
    sh = [r["resid"] for r in rows]; rng.shuffle(sh); null.append(heldout([dict(r, resid=s) for r, s in zip(rows, sh)]))
null.sort()
# word deletion lexicon, mean-centred
m = st.mean(r["delta"] for r in wd); dd = collections.defaultdict(list)
for r in wd:
    t = re.sub(r"[^a-z'-]", "", r["word"].lower())
    if t: dd[t].append(r["delta"]-m)
wl = {t: (st.mean(v), len(v)) for t, v in dd.items() if len(v) >= 4}
d = collections.defaultdict(list); pp = collections.defaultdict(set)
for r in rows:
    for t in r["toks"]: d[t].append(r["resid"]); pp[t].add(r["paper"])
out = []
for t, v in d.items():
    if len(v) < 6 or len(pp[t]) < 3: continue
    bs = sorted(st.mean(rng.choice(v) for _ in v) for _ in range(500)); lo, hi = bs[12], bs[487]
    out.append((t, st.mean(v), len(v), lo, hi, wl.get(t)))
low = sorted([x for x in out if x[4] < 0], key=lambda x: x[1]); high = sorted([x for x in out if x[3] > 0], key=lambda x: -x[1])
both = [(t, a, wl[t][0]) for t, a, *_ in out if t in wl]
agree = sum((a > 0) == (b2 > 0) for _, a, b2 in both)
ma, mb = st.mean(a for _, a, _ in both), st.mean(b2 for _, _, b2 in both)
cc = sum((a-ma)*(b2-mb) for _, a, b2 in both)/((sum((a-ma)**2 for _, a, _ in both)*sum((b2-mb)**2 for _, _, b2 in both))**0.5)
res = {"sentences": len(rows), "heldout_corr": ho, "null_mean": st.mean(null), "null_p95": null[int(0.95*len(null))], "two_source_words": len(both), "two_source_same_sign": agree, "two_source_corr": cc}
json.dump({"validity": res, "lower": [(t, a, n, lo, hi) for t, a, n, lo, hi, _ in low], "raise": [(t, a, n, lo, hi) for t, a, n, lo, hi, _ in high]}, open("lexicon.json", "w"), indent=1)
def tab(xs): return "\n".join(f"| {t} | {a:+.3f} | {n} | {lo:+.3f} to {hi:+.3f} | " + (f"{w[0]:+.3f}" if w else "") + " |" for t, a, n, lo, hi, w in xs)
print(json.dumps(res, indent=1)); print("LOW", len(low), "HIGH", len(high))
open("lexicon_tables.md", "w").write("### Words in sentences that lower the paragraph score\n\n| word | mean effect | sentences | 95 % CI | word-deletion check |\n|---|---|---|---|---|\n" + tab(low) +
  "\n\n### Words in sentences that raise it\n\n| word | mean effect | sentences | 95 % CI | word-deletion check |\n|---|---|---|---|---|\n" + tab(high) + "\n")
