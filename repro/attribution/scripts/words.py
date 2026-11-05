import sys, json, re, time, collections
sys.argv, a = sys.argv[:1], sys.argv[1:]
import wb
inv = json.load(open(wb.D/"baseline.json"))
paras = sorted([(r.replace("paper-",""), i, e["text"], e["base"]) for r, v in inv.items() for i, e in enumerate(v["paras"])
         if len(e["text"].split()) >= 40 and "figure and table" not in e["sec"]], key=lambda x: -x[3])[:20]
base = wb.score_texts([p[2] for p in paras])
t0 = time.time()
rows = []  # (paper, para, word_index, word, delta = base - score_without)
CH = 400
jobs = []
for k, (r, i, t, b) in enumerate(paras):
    toks = t.split(" ")
    for j, w in enumerate(toks):
        jobs.append((k, j, w, " ".join(toks[:j] + toks[j+1:])))
print(len(jobs), "word deletions", flush=True)
sc = []
for s in range(0, len(jobs), CH):
    sc += wb.score_texts([x[3] for x in jobs[s:s+CH]])
    json.dump(sc, open("word_loo_partial.json", "w"))
    print(s, time.time()-t0, flush=True)
for (k, j, w, _), s in zip(jobs, sc):
    rows.append({"k": k, "j": j, "word": w, "delta": base[k] - s})
json.dump({"paras": [(r, i, b) for r, i, t, b in paras], "base": base, "rows": rows}, open("word_loo.json", "w"))
agg = collections.defaultdict(list)
for x in rows:
    agg[re.sub(r"[^\w€$%.-]", "", x["word"].lower()).strip(".")].append(x["delta"])
tab = [(w, sum(d)/len(d), len(d)) for w, d in agg.items() if len(d) >= 10 and w]
tab.sort(key=lambda x: -x[1])
print("TOP raise"); [print(f"  {w:14s} {m:+.4f} n={n}") for w, m, n in tab[:25]]
print("TOP lower"); [print(f"  {w:14s} {m:+.4f} n={n}") for w, m, n in tab[-25:]]
