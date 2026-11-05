import sys, json, re
sys.argv, a = sys.argv[:1], sys.argv[1:]
import wb
p = "jepa-world-model"
L = open(wb.D/"work"/f"{p}.src.md").read().split("\n")
blocks, cur, in_code = [], [], False
for n, l in enumerate(L, 1):
    if l.strip().startswith("```"):
        in_code = not in_code
    if in_code or l.strip().startswith("```") or not l.strip():
        if cur: blocks.append(cur); cur = []
        continue
    cur.append((n, l))
if cur: blocks.append(cur)
paras = []
sec = ""
for b in blocks:
    first = b[0][1]
    if first.startswith("#"):
        sec = first.lstrip("# ").strip(); 
        b = b[1:]
        if not b: continue
        first = b[0][1]
    if first.startswith(("|", "!", "<", "$$")): continue
    txt = wb.render(p, "\n".join(x[1] for x in b))
    if len(txt.split()) < 40: continue
    paras.append({"sec": sec, "l0": b[0][0], "l1": b[-1][0], "text": txt})
sc = wb.score_texts([x["text"] for x in paras])
for x, s in zip(paras, sc): x["base"] = s
wb.inv["paper-"+p]["paras"] = paras
json.dump(wb.inv, open(wb.D/"baseline.json", "w"), indent=1)
tw = sum(len(x["text"].split()) for x in paras)
print(len(paras), "paras", tw, "words", "mean", sum(x["base"]*len(x["text"].split()) for x in paras)/tw)
