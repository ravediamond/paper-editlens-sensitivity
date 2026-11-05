import sys, json, re, random, statistics as st
sys.argv, a = sys.argv[:1], sys.argv[1:]
import wb
sys.path.insert(0, "/home/jetson/workspace/road-to-robotics/scripts")
import paper_sentences as S
inv = json.load(open(wb.D/"inventory.json"))
paras = [(r.replace("paper-",""), i, e["text"]) for r, v in inv.items() for i, e in enumerate(v["paras"])
         if len(e["text"].split()) >= 40 and "figure and table" not in e["sec"]]
base = wb.score_texts([p[2] for p in paras])
rng = random.Random(7)
pool = {}
for r, i, t in paras: pool.setdefault(r, []).append(t)
def other_sentence(r, t):
    cands = [s for x in pool[r] if x != t for s in S.split_sentences(x) if 8 <= len(s.split()) <= 25 and not re.search(r"\d", s)]
    return rng.choice(cands) if cands else None
def semijoin(t):
    s = S.split_sentences(t); out = []; k = 0
    while k < len(s):
        if k + 1 < len(s) and k % 2 == 0:
            out.append(s[k].rstrip(".") + "; " + s[k+1][0].lower() + s[k+1][1:]); k += 2
        else: out.append(s[k]); k += 1
    return " ".join(out)
INS = {"append_generic_closer": "The result holds on this rig.", "append_advice": "Check the simple baseline first.",
       "append_verdict": "The row fails.", "append_contrast": "This is a limit of the setting, not of the method.",
       "append_we_ran": "We ran this on the Jetson Orin NX."}
T = {"semicolon_join_pairs": semijoin}
for n, s in INS.items(): T[n] = (lambda s: (lambda t: t + " " + s))(s)
texts, idx = [], []
for k, (r, i, t) in enumerate(paras):
    for n, f in T.items(): texts.append(f(t)); idx.append((k, n))
    o = other_sentence(r, t)
    if o: texts.append(t + " " + o); idx.append((k, "append_real_sentence_same_paper"))
sc = wb.score_texts(texts)
res = {}
for (k, n), s in zip(idx, sc): res.setdefault(n, []).append(s - base[k])
out = {}
for n, d in res.items():
    bs = sorted(sum(rng.choice(d) for _ in d)/len(d) for _ in range(2000))
    out[n] = {"n": len(d), "mean": st.mean(d), "ci": [bs[50], bs[1949]], "share_up": sum(x > 0.005 for x in d)/len(d)}
    print(f"{n:34s} n={len(d):2d} {st.mean(d):+.4f} [{bs[50]:+.4f},{bs[1949]:+.4f}] up={out[n]['share_up']:.2f}")
json.dump({"effects": out, "raw": res}, open("exp_insert.json", "w"))
