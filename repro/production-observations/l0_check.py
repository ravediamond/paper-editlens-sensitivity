#!/usr/bin/env python3
"""L0: recompute expected/summary.json from expected/observations.json and the stored texts (word counts from texts/).
The verdicts are as the owner read them off the production detector's web page; they cannot be recomputed here. Standard library only."""
import json, sys
from pathlib import Path

H = Path(__file__).resolve().parent; E = H / "expected"


def summarize(o):
    rows = o["rows"]
    for r in rows:
        w = len((H / r["file"]).read_text().split())
        assert w == r["words"], f"{r['id']}: {w} words in file, {r['words']} in row"
    fl = o["external"][0]["flagged_paragraphs"]
    return dict(date="2026-11-09", detector="Pangram production detector, web page",
                own_texts=len(rows), own_flagged=sum(r["cls"] == "flagged" for r in rows), own_human=sum(r["cls"] == "human" for r in rows),
                dictated=sum(r["dictated"] for r in rows), dictated_flagged=sum(r["dictated"] and r["cls"] == "flagged" for r in rows),
                longest_dictated_words=max(r["words"] for r in rows if r["dictated"]),
                human_segment_words=[r["words"] for r in rows if r["cls"] == "human"][0],
                ext_flagged_paragraphs=len(fl), ext_case_study_flagged=sum(p["case_study"] for p in fl))


s = summarize(json.loads((E / "observations.json").read_text()))
if "--write" in sys.argv:
    (E / "summary.json").write_text(json.dumps(s, indent=1) + "\n")
ok = s == json.loads((E / "summary.json").read_text())
for k, v in s.items():
    print(("ok  " if ok else "??  ") + f"{k}: {v}")
print("L0 PASS" if ok else "L0 FAIL")
