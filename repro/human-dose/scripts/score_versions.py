#!/usr/bin/env python3
"""Score every baseline and version paragraph with the open EditLens 3B model through `ws paper-polish serve`
(paper_polish.score, one paragraph per text). Baselines are scored twice (identity null, PROTOCOL §4).

    score_versions.py           write expected/scores.json: {id: {"s": score, "s2": second score (baselines only)}}
Already-scored ids are kept; only new ones go to the model."""
import sys
from common import *  # noqa: F401,F403
import paper_polish as PP  # noqa: E402


def main():
    V = load("versions.json") or sys.exit("run snapshot.py first")
    S = load("scores.json") or {}
    base = {b["id"]: b["text"] for e in V.values() for b in e["baseline"]}
    vers = {v["id"]: v["text"] for e in V.values() for v in e["versions"]}
    todo = [(i, t) for i, t in base.items() if i not in S] + [(i, t) for i, t in vers.items() if i not in S]
    for k in range(0, len(todo), 16):
        chunk = todo[k:k + 16]
        for (i, _), s in zip(chunk, PP.score([t for _, t in chunk])):
            S[i] = {"s": s}
        print(f"{min(k + 16, len(todo))}/{len(todo)}")
    redo = [(i, t) for i, t in base.items() if "s2" not in S[i]]
    for k in range(0, len(redo), 16):
        chunk = redo[k:k + 16]
        for (i, _), s in zip(chunk, PP.score([t for _, t in chunk])):
            S[i]["s2"] = s
    dump("scores.json", S)
    nulls = [abs(S[i]["s"] - S[i]["s2"]) for i in base]
    print(f"scored {len(S)}; identity null mean |diff| {sum(nulls) / len(nulls):.5f} max {max(nulls):.5f}")


if __name__ == "__main__":
    main()
