import sys, json
sys.argv, a = sys.argv[:1], sys.argv[1:]
import wb
sys.path.insert(0, "/home/jetson/workspace/road-to-robotics/scripts")
import paper_sentences as S
inv = json.load(open(wb.D/"baseline.json"))
rows = []
paras = [(r.replace("paper-",""), i, e["text"], e["base"]) for r, v in inv.items() for i, e in enumerate(v["paras"])
         if len(e["text"].split()) >= 40 and "figure and table" not in e["sec"]]
texts, meta = [], []
for k, (r, i, t, b) in enumerate(paras):
    ss = S.split_sentences(t)
    if len(ss) < 2: continue
    for j, s in enumerate(ss):
        texts.append(" ".join(x for m, x in enumerate(ss) if m != j)); meta.append((k, j, s, len(ss)))
sc = wb.score_texts(texts)
for (k, j, s, n), x in zip(meta, sc):
    r, i, t, b = paras[k]
    rows.append({"paper": r, "para": i, "sent": j, "n_sent": n, "sentence": s, "para_score": b, "without": x, "contribution": b - x})
json.dump(rows, open("loo_all.json", "w"))
print(len(rows), "sentences")
