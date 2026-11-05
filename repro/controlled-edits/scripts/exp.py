import sys, json, re, random
sys.argv, a = sys.argv[:1], sys.argv[1:]
import wb
sys.path.insert(0, "/home/jetson/workspace/road-to-robotics/scripts")
import paper_sentences as S
inv = json.load(open(wb.D/"baseline.json"))
paras = []
for r, v in inv.items():
    for i, e in enumerate(v["paras"]):
        if len(e["text"].split()) >= 40 and "figure and table" not in e["sec"]:
            paras.append((r.replace("paper-",""), i, e["text"], e["base"]))
print(len(paras), "paragraphs >= 40 words")
def cap(s): return re.sub(r"(\.\s+)([a-z])", lambda m: m.group(1)+m.group(2).upper(), s)
def semi(t): return cap(t.replace("; ", ". "))
def colon(t): return cap(re.sub(r"(?<=[a-z\)]): (?=[a-z])", ". ", t))
def paren(t): return re.sub(r"\s*\([^()]*\)", "", t)
def andsplit(t): return cap(re.sub(r", (and|but) ", ". ", t))
def num(t): return re.sub(r"\d+(?:[.,]\d+)*", lambda m: "many", t)
def rev(t): return " ".join(S.split_sentences(t)[::-1])
def shuf(seed):
    def f(t):
        s = S.split_sentences(t); random.Random(seed).shuffle(s); return " ".join(s)
    return f
def first2end(t):
    s = S.split_sentences(t); return " ".join(s[1:]+s[:1])
def dropl(t): s = S.split_sentences(t); return " ".join(s[:-1])
def dropf(t): s = S.split_sentences(t); return " ".join(s[1:])
def half(t): s = S.split_sentences(t); return " ".join(s[:max(1,len(s)//2)])
def toI(t):
    t = re.sub(r"\bWe\b", "I", t); t = re.sub(r"\bwe\b", "I", t); t = re.sub(r"\bour\b", "my", t); return re.sub(r"\bOur\b", "My", t)
def nowe(t): return re.sub(r"\b(We|we) ", "", t)
def ws(t): return "  ".join(t.split(" ")).upper()
T = {"null_upper_ws": ws, "semicolons_to_periods": semi, "colons_to_periods": colon, "drop_parentheticals": paren,
     "split_at_and_but": andsplit, "numbers_masked": num, "reverse_order": rev, "shuffle_a": shuf(1), "shuffle_b": shuf(2), "shuffle_c": shuf(3),
     "first_sentence_last": first2end, "drop_last_sentence": dropl, "drop_first_sentence": dropf, "first_half_only": half, "we_to_I": toI}
texts, idx = [], []
for k, (r, i, t, b) in enumerate(paras):
    for name, f in T.items():
        texts.append(f(t)); idx.append((k, name))
base = wb.score_texts([p[2] for p in paras])
sc = wb.score_texts(texts)
res = {}
for (k, name), s in zip(idx, sc):
    res.setdefault(name, []).append(s - base[k])
rng = random.Random(0)
out = {}
for name, d in res.items():
    m = sum(d)/len(d)
    bs = sorted(sum(rng.choice(d) for _ in d)/len(d) for _ in range(2000))
    out[name] = {"mean_delta": m, "ci": [bs[50], bs[1949]], "n": len(d), "share_down": sum(x < -0.005 for x in d)/len(d)}
    print(f"{name:24s} {m:+.3f} [{bs[50]:+.3f},{bs[1949]:+.3f}] n={len(d)} down={out[name]['share_down']:.2f}")
json.dump({"base_check": sum(base)/len(base), "effects": out, "raw": {n: res[n] for n in res},
           "paras": [(r, i, b) for r, i, t, b in paras]}, open("exp_transforms.json", "w"))
