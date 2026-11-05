#!/usr/bin/env python3
"""Per-paragraph style features of the human reference papers and of our four PDFs, joined to the stored EditLens scores by (paper, sha1) so no text is stored.

    python3 style_features.py HUMAN_DIR ../expected/rows.json ../expected/style_rows.json --ours PDF ...
"""
import hashlib, json, re, statistics as st, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_pdfs as S  # noqa: E402
M = S.M

RX = {"cite": r"\[\d+(?:[,–\-]\s*\d+)*\]|\([A-Z][A-Za-z\-]+(?: et al\.)?,? \d{4}\)", "figtab": r"\b(?:Fig\.|Figure|Table|Tab\.|Sec\.|Section)\s*\d+",
      "we": r"\b(?:we|our|us|We|Our|I)\b", "passive": r"\b(?:is|are|was|were|be|been|being)\s+\w+(?:ed|en)\b",
      "hedge": r"\b(?:may|might|could|seem|seems|appear|appears|likely|possibly|potentially|suggest|suggests|perhaps|tend|tends)\b",
      "contrast": r"\b(?:however|but|while|whereas|although|though|instead|rather|unlike)\b", "connective": r"\b(?:therefore|thus|hence|consequently|moreover|furthermore|additionally|also|in addition)\b",
      "digit_tok": r"\b\S*\d\S*\b", "paren": r"\(", "colon": r":", "semi": r";", "comma": r",", "dash": r"[—–]|--"}


def feats(t):
    w = t.split(); n = len(w) or 1
    sents = [x for x in re.split(r"(?<=[.!?])\s+(?=[A-Z])", t) if x.strip()]
    sl = [len(x.split()) for x in sents] or [n]
    f = {"words": n, "sentences": len(sl), "sent_mean": st.mean(sl), "sent_sd": st.pstdev(sl), "sent_max": max(sl)}
    for k, rx in RX.items():
        f[k + "_per100"] = 100 * len(re.findall(rx, t)) / n
    caps = sum(1 for s in sents for x in s.split()[1:] if re.match(r"[A-Z][a-z]+$", x))
    f["cap_mid_per100"] = 100 * caps / n; f["word_len"] = st.mean(len(re.sub(r"\W", "", x)) for x in w); f["ttr"] = len({x.lower() for x in w}) / n
    f["long_per100"] = 100 * sum(len(re.sub(r"\W", "", x)) >= 10 for x in w) / n
    f["starts_we"] = float(bool(re.match(r"(We|Our|I)\b", t))); f["starts_the"] = float(bool(re.match(r"(The|This|These|Our)\b", t)))
    f["starts_in"] = float(bool(re.match(r"(In|For|To|On|At|When|If)\b", t)))
    return f


def main():
    a = sys.argv[1:]; hdir, rows_f, out = Path(a[0]), a[1], a[2]; ours = a[a.index("--ours") + 1:] if "--ours" in a else []
    sc = {(r["paper"], r["sha1"]): r for r in json.loads(Path(rows_f).read_text())}; res = []
    jobs = [(f, "human", re.sub(r"v\d+$", "", f.stem)) for f in sorted(hdir.glob("pdfs/*.pdf"))] + [(Path(f), "ours", Path(f).parents[1].name) for f in ours]
    for f, g, pid in jobs:
        for s in S.sections(f):
            for p in s["paras"]:
                if M.words(p["text"]) < 40:
                    continue
                h = hashlib.sha1(p["text"].encode()).hexdigest()[:12]; r = sc.get((pid, h))
                if r:
                    res.append({"paper": pid, "group": g, "sha1": h, "type": r["type"], "score": r["score"], **feats(p["text"])})
    Path(out).write_text(json.dumps(res)); print(len(res), "paragraphs with features")


if __name__ == "__main__":
    main()
