#!/usr/bin/env python3
"""Match every version paragraph to a baseline paragraph of the same paper and tag the edit type (PROTOCOL §2).

    align.py            write expected/pairs.json
    align.py --check    print merges and new paragraphs for the owner to glance at

pairs.json: list of {"paper", "base_id", "ver_id", "ratio", "kind": "pair"|"new", "edit_type": "reword"|"content", "override": bool,
                     "words_base", "words_ver", "commit", "date"}"""
import difflib, re, sys
from collections import defaultdict
from common import *  # noqa: F401,F403

MIN_RATIO = 0.30
NUM = re.compile(r"\d[\d.,%]*")
NAME = re.compile(r"\b[A-Z][A-Za-z0-9-]{2,}\b")


def ratio(a, b):
    return difflib.SequenceMatcher(None, a.lower().split(), b.lower().split(), autojunk=False).ratio()


def edit_type(base, ver):
    nums = set(NUM.findall(ver)) - set(NUM.findall(base))
    names = set(NAME.findall(ver)) - set(NAME.findall(base))
    grow = (nwords(ver) - nwords(base)) / max(1, nwords(base))
    return "content" if nums or names or grow > 0.15 else "reword"


def main(check=False):
    V = load("versions.json") or sys.exit("run snapshot.py first")
    pairs, merges = [], defaultdict(list)
    for p, e in V.items():
        base = {b["id"]: b["text"] for b in e["baseline"]}
        best = {}
        for v in e["versions"]:
            cand = max(base, key=lambda k: ratio(base[k], v["text"]))
            best[v["id"]] = (cand, ratio(base[cand], v["text"]))
        # a baseline paragraph matched by several versions from the SAME commit is a split: keep the higher ratio
        by_commit_base = defaultdict(list)
        for v in e["versions"]:
            by_commit_base[(v["commit"], best[v["id"]][0])].append(v)
        demoted = set()
        for (c, bid), vs in by_commit_base.items():
            if len(vs) > 1:
                keep = max(vs, key=lambda v: best[v["id"]][1])
                for v in vs:
                    if v is not keep:
                        demoted.add(v["id"])
                merges[p].append((c, bid, [v["id"] for v in vs]))
        for v in e["versions"]:
            bid, r = best[v["id"]]
            new = r < MIN_RATIO or v["id"] in demoted
            et = v["override"] or edit_type(base[bid], v["text"])
            pairs.append({"paper": p, "base_id": bid, "ver_id": v["id"], "ratio": round(r, 3), "kind": "new" if new else "pair",
                          "edit_type": et, "override": v["override"] is not None, "words_base": nwords(base[bid]), "words_ver": v["words"],
                          "commit": v["commit"], "date": v["date"]})
    if check:
        for p, ms in merges.items():
            for c, bid, ids in ms:
                print(f"split/merge {p} {c} base {bid} <- {ids}")
        for q in pairs:
            if q["kind"] == "new":
                print(f"new {q['paper']} {q['commit']} {q['ver_id']} best ratio {q['ratio']}")
        n = sum(q["kind"] == "pair" for q in pairs)
        print(f"{n} pairs, {len(pairs) - n} new, {sum(q['edit_type'] == 'content' for q in pairs if q['kind'] == 'pair')} content / "
              f"{sum(q['edit_type'] == 'reword' for q in pairs if q['kind'] == 'pair')} reword")
        return
    dump("pairs.json", pairs)
    print(len(pairs), "rows")


if __name__ == "__main__":
    main("--check" in sys.argv)
