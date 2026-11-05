import json, re, random, statistics as st
ex = json.load(open("exp_transforms.json")); inv = json.load(open("inventory.json"))
paras = ex["paras"]; texts = []
for r, i, b in paras: texts.append(inv["paper-"+r]["paras"][i]["text"])
# subset effects: only paragraphs the transform actually changes
has = {"semicolons_to_periods": lambda t: ";" in t, "colons_to_periods": lambda t: re.search(r"[a-z\)]: [a-z]", t) is not None,
       "drop_parentheticals": lambda t: re.search(r"\([^()]*\)", t) is not None, "split_at_and_but": lambda t: re.search(r", (and|but) ", t) is not None,
       "numbers_masked": lambda t: re.search(r"\d", t) is not None, "we_to_I": lambda t: re.search(r"\b[Ww]e\b|\b[Oo]ur\b", t) is not None}
rng = random.Random(0)
def ci(d):
    bs = sorted(sum(rng.choice(d) for _ in d)/len(d) for _ in range(2000)); return bs[50], bs[1949]
sub = {}
for name, f in has.items():
    d = [x for x, t in zip(ex["raw"][name], texts) if f(t)]
    sub[name] = {"n": len(d), "mean": st.mean(d), "ci": ci(d)}
    print(f"{name:24s} affected n={len(d):2d} mean {st.mean(d):+.4f} CI [{ci(d)[0]:+.4f},{ci(d)[1]:+.4f}]")
json.dump(sub, open("subset_effects.json","w"), indent=1)
# length: correlation of base score with word count and sentence count
import math
wc = [len(t.split()) for t in texts]; bs = [b for _, _, b in paras]
def corr(a, b):
    ma, mb = st.mean(a), st.mean(b); return sum((x-ma)*(y-mb) for x, y in zip(a, b))/math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
print("corr(score, words)", round(corr(bs, wc), 3), "n", len(bs))
# word-level deletion
w = json.load(open("word_loo.json")); d = [r["delta"] for r in w["rows"]]
print("word deletions", len(d), "mean", round(st.mean(d), 4), "max", round(max(d), 3), "min", round(min(d), 3),
      "share |d|<0.01", round(sum(abs(x) < 0.01 for x in d)/len(d), 3), "share >0.03", round(sum(x > 0.03 for x in d)/len(d), 4))
# iteration log
rows = [json.loads(l) for l in open("iterlog.jsonl")]
print("logged candidates", len(rows), "paragraph-rounds", len({(r["paper"], r["para"], r["round"]) for r in rows}))
