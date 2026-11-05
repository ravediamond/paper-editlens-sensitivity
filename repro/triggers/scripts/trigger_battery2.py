#!/usr/bin/env python3
"""Second trigger battery, on hosts that are not chosen by their score: 100 random human paragraphs (60 to 250 words, back matter excluded) and our 62 paragraphs.
Adds controls (a real sentence from another paragraph of the same text collection, at the end and at the start), position pairs (end against start),
separate name and digit edits, and a same-register concatenation against a concatenation with a specific technical human paragraph. Needs `ws paper-polish serve`.

    python3 trigger_battery2.py HUMAN_TEXTS.json EXCLUDED.json OURS_PARAGRAPHS.json OUT.json"""
import hashlib, json, random, re, statistics as st, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/road-to-robotics/scripts"))
import paper_map as M  # noqa: E402
import paper_polish as PP  # noqa: E402

EVAL = r"\b(?:important|importantly|essential|crucial|paramount|challenging|powerful|novel|significant|significantly|simple|effective|effectively|robust|promising|extremely|highly|widely|state-of-the-art|critical|key)\b"
AI = "This approach plays a crucial role in leveraging the underlying structure of the data."
PTR = "Figure 3 shows the result for each of the five tasks."
IMP = "This is important for the performance of the system."
MOT = "This is an important and challenging problem."


def sentences(t):
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", t) if s.strip()]


def edits(t, same, spec, peer):
    s = {"ctl_append_real_sentence": t + " " + same, "ctl_prepend_real_sentence": same + " " + t,
         "append_ai_phrase": t + " " + AI, "prepend_ai_phrase": AI + " " + t, "append_pointer": t + " " + PTR, "prepend_pointer": PTR + " " + t,
         "append_importance": t + " " + IMP, "prepend_motivation": MOT + " " + t,
         "names_only": re.sub(r"(?<=[a-z,;] )\b(?:[A-Z]{2,}[a-z\-]*|[A-Z][a-z]+[A-Z][A-Za-z]*)\b", "the method", t),
         "digits_only": re.sub(r"\s{2,}", " ", re.sub(r"\b\S*\d\S*\b", "", t)),
         "append_specific_paragraph": t + " " + spec, "prepend_specific_paragraph": spec + " " + t, "append_same_register_paragraph": t + " " + peer,
         "delete_evaluative_words": re.sub(r"\s{2,}", " ", re.sub(EVAL, "", t, flags=re.I))}
    return s


def main():
    a = sys.argv[1:]; H = json.loads(Path(a[0]).read_text()); ex = {(p, h) for p, h, _ in json.loads(Path(a[1]).read_text())}; ours = json.loads(Path(a[2]).read_text())
    H = [x for x in H if (x["paper"], hashlib.sha1(x["text"].encode()).hexdigest()[:12]) not in ex]; rng = random.Random(11)
    rand = [x["text"] for x in H if 60 <= x["words"] <= 250]; rng.shuffle(rand)
    spec = [x["text"] for x in H if x["score"] < 0.03 and 60 <= x["words"] <= 120]
    hosts = [("human_random", t) for t in rand[:100]] + [("ours", t) for t in ours]
    sent = {"human_random": [s for t in rand for s in sentences(t) if 8 <= len(s.split()) <= 25 and not re.search(r"\d", s)], "ours": [s for t in ours for s in sentences(t) if 8 <= len(s.split()) <= 25 and not re.search(r"\d", s)]}
    peers = {"human_random": rand[100:] or rand, "ours": ours}
    texts, idx = [], []
    for g, t in hosts:
        texts.append(M.clean_text(t)); idx.append((g, t, "base"))
        for k, v in edits(t, rng.choice(sent[g]), rng.choice(spec), rng.choice([p for p in peers[g] if p != t])).items():
            texts.append(M.clean_text(v)); idx.append((g, t, k))
    sc = []
    for i in range(0, len(texts), 250):
        sc += PP.score(texts[i:i + 250], wait=3000); print(i + 250, "of", len(texts), flush=True)
    base = {(g, t): s for (g, t, k), s in zip(idx, sc) if k == "base"}; res = {}
    for (g, t, k), s in zip(idx, sc):
        if k != "base":
            res.setdefault(g, {}).setdefault(k, []).append(s - base[(g, t)])
    out = {"hosts": {g: sum(1 for x in hosts if x[0] == g) for g in ("human_random", "ours")}, "base_mean": {g: st.mean(v for (gg, _), v in base.items() if gg == g) for g in ("human_random", "ours")},
           "base": {g: [v for (gg, _), v in base.items() if gg == g] for g in ("human_random", "ours")}, "raw": res}
    Path(a[3]).write_text(json.dumps(out)); print(out["hosts"], out["base_mean"])


if __name__ == "__main__":
    main()
