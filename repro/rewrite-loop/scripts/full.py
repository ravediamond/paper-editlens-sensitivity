import sys, json
sys.argv, a = sys.argv[:1], sys.argv[1:]
import wb
p = a[0]; inv = wb.inv["paper-"+p]["paras"]
texts = [wb.render(p, wb.para_src(p, i)) for i in range(len(inv))]
sc = wb.score_texts(texts)
w = [len(t.split()) for t in texts]
base = sum(e["base"]*len(e["text"].split()) for e in inv)/sum(len(e["text"].split()) for e in inv)
now = sum(s*x for s, x in zip(sc, w))/sum(w)
print(f"{p}: baseline {base:.3f} -> now {now:.3f}  (words {sum(len(e['text'].split()) for e in inv)} -> {sum(w)})")
for i,(e,s) in enumerate(zip(inv,sc)):
    if abs(s-e['base'])>0.02: print(f"  para {i:2d} {e['base']:.3f} -> {s:.3f}")
