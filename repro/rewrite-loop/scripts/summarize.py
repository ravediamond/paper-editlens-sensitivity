"""summarize.py -> results.json: every number the notes and the paper quote."""
import sys, json, re, statistics as st, collections, random
sys.argv, a = sys.argv[:1], sys.argv[1:]
import wb
R = {}
# 1. before / after (word-weighted mean of paragraph scores, source rendered, citations stripped)
ba = {}
for p in ["register-reproducibility", "jepa-world-model", "reward-models-stopping-rule", "vla-edge-inference"]:
    inv = wb.inv["paper-"+p]["paras"]; texts = [wb.render(p, wb.para_src(p, i)) for i in range(len(inv))]
    sc = wb.score_texts(texts); w = [len(t.split()) for t in texts]
    base_w = [len(e["text"].split()) for e in inv]
    ba[p] = {"before": sum(e["base"]*x for e, x in zip(inv, base_w))/sum(base_w), "after": sum(s*x for s, x in zip(sc, w))/sum(w),
             "paragraphs": len(inv), "changed": sum(abs(s-e["base"]) > 0.02 for s, e in zip(sc, inv)),
             "worst_before": max(e["base"] for e in inv), "worst_after": max(sc)}
R["before_after"] = ba
R["transforms"] = json.load(open("exp_transforms.json"))["effects"]; R["inserts"] = json.load(open("exp_insert.json"))["effects"]
# 2. iteration log
rows = [json.loads(l) for l in open("iterlog.jsonl")]; g = collections.defaultdict(list)
for r in rows: g[(r["paper"], r["para"], r["round"])].append(r)
tot = low = 0; best = []
for v in g.values():
    c0 = [x for x in v if x["cand"] == 0][0]["score"]; cs = [x for x in v if x["cand"] > 0]
    for x in cs: tot += 1; low += x["score"] < c0 - 0.005
    ok = [x["score"]-c0 for x in cs if x["ph_ok"]]
    if ok: best.append(min(ok))
R["iteration"] = {"candidates": tot, "lower": low, "paragraph_rounds": len(best), "mean_best_delta": st.mean(best), "share_improved": sum(b < -0.005 for b in best)/len(best)}
# 3. word deletion
w = json.load(open("word_loo.json"))["rows"]; d = [r["delta"] for r in w]
R["word_deletion"] = {"n": len(d), "mean": st.mean(d), "max": max(d), "min": min(d), "share_abs_lt_0.01": sum(abs(x) < 0.01 for x in d)/len(d)}
# 4. lexicon validity (recomputed from lex.py output stored below)
json.dump(R, open("results.json", "w"), indent=1)
for p, v in ba.items(): print(f"{p:30s} {v['before']:.3f} -> {v['after']:.3f}  worst {v['worst_before']:.3f} -> {v['worst_after']:.3f}")
print(R["iteration"])
