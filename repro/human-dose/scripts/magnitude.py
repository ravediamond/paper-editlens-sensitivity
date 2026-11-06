#!/usr/bin/env python3
"""Edit magnitude between a baseline and a version paragraph: the two EditLens supervision metrics, as released in
pangramlabs/EditLens scripts/scoring/ (cosine_distance.py, soft_ngrams.py; CC BY-NC-SA 4.0), vendored here with the
same defaults (PROTOCOL §3).

    magnitude.py              write expected/magnitudes.json for every pair in pairs.json
    magnitude.py --selftest   PROTOCOL §6 check 2

Needs sentence-transformers in the `editlens` venv; Qwen/Qwen3-Embedding-0.6B (~1.2 GB) and all-MiniLM-L6-v2 are
downloaded once by sentence-transformers."""
import sys
import torch
from common import *  # noqa: F401,F403

COS_MODEL = "Qwen/Qwen3-Embedding-0.6B"
SNG_MODEL = "all-MiniLM-L6-v2"
_models = {}


def model(name):
    from sentence_transformers import SentenceTransformer
    if name not in _models:
        _models[name] = SentenceTransformer(name, model_kwargs={"dtype": "auto"})
    return _models[name]


def cosine_distance(a, b):
    e = model(COS_MODEL).encode([a, b], convert_to_tensor=True)
    e = torch.nn.functional.normalize(e, p=2, dim=1)
    return float(1.0 - (e[0] @ e[1]).item())


def phrases(text, lo=6, hi=12):
    w = text.split()
    lo = min(lo, len(w))
    return [" ".join(w[i:i + n]) for n in range(lo, hi + 1) for i in range(len(w) - n + 1)]


def soft_ngrams(src, edited, tau=0.8, lo=6, hi=12):
    ps, pe = phrases(src, lo, hi), phrases(edited, lo, hi)
    if not ps or not pe:
        return 1.0
    e = model(SNG_MODEL).encode(ps + pe, convert_to_tensor=True, batch_size=64)
    e = torch.nn.functional.normalize(e, p=2, dim=1)
    sim = e[:len(ps)] @ e[len(ps):].t()
    return 1.0 - float((sim >= tau).any(dim=0).sum().item()) / len(pe)


def selftest():
    V = load("versions.json") or sys.exit("run snapshot.py first")
    paras = [b["text"] for e in V.values() for b in e["baseline"]]
    x, y = paras[0], paras[-1]
    c0, s0 = cosine_distance(x, x), soft_ngrams(x, x)
    c1 = cosine_distance(x, y)
    w = x.split(); i = next(k for k, t in enumerate(w) if t.lower() in ("we", "the", "a", "on", "of"))
    w[i] = {"we": "the authors", "the": "this", "a": "one", "on": "upon", "of": "from"}[w[i].lower()]
    c2 = cosine_distance(x, " ".join(w))
    print(f"identity cosine {c0:.6f} sng {s0:.6f} (want 0, 0)")
    print(f"unrelated cosine {c1:.4f} (want > 0.15)")
    print(f"one-word edit cosine {c2:.4f} (want in (0, 0.03))")
    ok = c0 == 0.0 and s0 == 0.0 and c1 > 0.15 and 0 < c2 < 0.03
    print("SELFTEST PASS" if ok else "SELFTEST FAIL")


def main():
    V = load("versions.json"); P = load("pairs.json") or sys.exit("run align.py first")
    text = {b["id"]: b["text"] for e in V.values() for b in e["baseline"]}
    text.update({v["id"]: v["text"] for e in V.values() for v in e["versions"]})
    done = {(m["base_id"], m["ver_id"]): m for m in (load("magnitudes.json") or [])}
    out = []
    for q in P:
        if q["kind"] != "pair":
            continue
        key = (q["base_id"], q["ver_id"])
        if key in done:
            out.append(done[key]); continue
        x, y = text[q["base_id"]], text[q["ver_id"]]
        out.append({"base_id": q["base_id"], "ver_id": q["ver_id"], "cosine": round(cosine_distance(x, y), 5), "sng": round(soft_ngrams(x, y), 5)})
        print(q["paper"], q["ver_id"], out[-1]["cosine"], out[-1]["sng"])
    dump("magnitudes.json", out)


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
