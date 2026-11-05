#!/usr/bin/env python3
"""Controlled substitutions and insertions on host paragraphs, to see which kinds of content move the open EditLens score.
Hosts: human paragraphs scoring below 0.03 (60 to 250 words), human paragraphs scoring above 0.20 (up to 150 words), and our 62 paragraphs.
Needs `ws paper-polish serve`. Output: per host and transform the score change (no text).

    python3 trigger_battery.py HUMAN_TEXTS.json EXCLUDED.json OURS_PARAGRAPHS.json OUT.json"""
import hashlib, json, random, re, statistics as st, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/road-to-robotics/scripts"))
import paper_map as M  # noqa: E402
import paper_polish as PP  # noqa: E402

EVAL = r"\b(?:important|importantly|essential|crucial|paramount|challenging|powerful|novel|significant|significantly|simple|effective|effectively|robust|promising|extremely|highly|widely|state-of-the-art|critical|key)\b"
INS = {"prepend_motivation": ("pre", "This is an important and challenging problem."), "prepend_background": ("pre", "This problem has been widely studied in robotics."),
       "prepend_importantly": ("pre", "Importantly,"), "prepend_novelty": ("pre", "We propose a novel approach to this problem."),
       "append_importance": ("post", "This is important for the performance of the system."),
       "append_ai_phrase": ("post", "This approach plays a crucial role in leveraging the underlying structure of the data."),
       "append_specific": ("post", "We ran this on the Jetson Orin NX at 25 W with SmolVLA 450M and a batch size of 1."),
       "append_neutral_pointer": ("post", "Figure 3 shows the result for each of the five tasks.")}


def edits(t, other):
    out = {}
    for k, (w, s) in INS.items():
        out[k] = (s + " " + t) if w == "pre" else (t + " " + s)
    out["delete_evaluative_words"] = re.sub(r"\s{2,}", " ", re.sub(EVAL, "", t, flags=re.I))
    out["drop_numbers"] = re.sub(r"\s{2,}", " ", re.sub(r"\b\S*\d\S*\b", "", t))
    out["names_to_the_method"] = re.sub(r"\b(?:[A-Z]{2,}[a-z0-9\-]*|[A-Z][a-z]+[A-Z]\w*|\w*\d\w*)\b", "the method", t)
    ss = re.split(r"(?<=[.!?])\s+(?=[A-Z])", t)
    out["first_half"] = " ".join(ss[: max(1, len(ss) // 2)])
    out["append_other_specific_paragraph"] = t + " " + other
    return out


def main():
    a = sys.argv[1:]; H = json.loads(Path(a[0]).read_text()); ex = {(p, h) for p, h, _ in json.loads(Path(a[1]).read_text())}; ours = json.loads(Path(a[2]).read_text())
    H = [x for x in H if (x["paper"], hashlib.sha1(x["text"].encode()).hexdigest()[:12]) not in ex]
    rng = random.Random(3)
    low = [x["text"] for x in H if x["score"] < 0.03 and 60 <= x["words"] <= 250]; high = [x["text"] for x in H if x["score"] > 0.20 and x["words"] <= 150]
    rng.shuffle(low); rng.shuffle(high); hosts = [("human_low", t) for t in low[:120]] + [("human_high", t) for t in high[:100]] + [("ours", t) for t in ours]
    pool = [t for t in low if 60 <= len(t.split()) <= 120]
    texts, idx = [], []
    for g, t in hosts:
        texts.append(M.clean_text(t)); idx.append((g, t, "base"))
        for k, v in edits(t, rng.choice(pool)).items():
            texts.append(M.clean_text(v)); idx.append((g, t, k))
    sc = PP.score(texts, wait=3000); base = {}
    for (g, t, k), s in zip(idx, sc):
        if k == "base":
            base[(g, t)] = s
    res = {}
    for (g, t, k), s in zip(idx, sc):
        if k != "base":
            res.setdefault(g, {}).setdefault(k, []).append(s - base[(g, t)])
    rows = {"hosts": {g: sum(1 for x in hosts if x[0] == g) for g in {h[0] for h in hosts}}, "base_mean": {g: st.mean(v for (gg, _), v in base.items() if gg == g) for g in {h[0] for h in hosts}}, "raw": res}
    Path(a[3]).write_text(json.dumps(rows)); print(rows["hosts"], rows["base_mean"])


if __name__ == "__main__":
    main()
