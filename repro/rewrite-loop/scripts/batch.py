"""batch.py paper batch.json round : {para: [cand,...]} -> scores per paragraph; saves cands to cand_<paper>_<para>.json for ap2.py"""
import json, sys, re, time
sys.argv, args = sys.argv[:1], sys.argv[1:]
import wb
p, f, rnd = args
B = json.load(open(f))
log = open(wb.D/"iterlog.jsonl", "a")
for para, cands in B.items():
    i = int(para); cur = wb.para_src(p, i)
    allc = [cur] + cands
    sc = wb.score_texts([wb.render(p, c) for c in allc])
    json.dump(cands, open(wb.D/f"cand_{p}_{i}.json", "w"))
    res = []
    for k, (c, s) in enumerate(zip(allc, sc)):
        ok = sorted(re.findall(r"\{\{\w+\}\}", c)) == sorted(re.findall(r"\{\{\w+\}\}", cur))
        res.append(f"{'cur' if k==0 else 'c'+str(k)}={s:.3f}{'' if ok else '!PH'}")
        log.write(json.dumps({"paper": p, "para": i, "round": rnd, "cand": k, "score": s, "ph_ok": ok, "text": c, "t": time.time()}) + "\n")
    print(f"para {i:2d}: " + "  ".join(res))
