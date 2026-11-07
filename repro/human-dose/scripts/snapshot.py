#!/usr/bin/env python3
"""Freeze the baselines and collect every later version of every paragraph of the four papers.

    snapshot.py --freeze        record HEAD of each paper repo as its baseline (expected/baseline.json); refuses to overwrite
    snapshot.py                 walk the default branch since the baseline; write expected/versions.json

versions.json: {paper: {"baseline": [{"id", "text", "words"}], "versions": [{"commit", "date", "subject", "override", "text", "words"}]}}
A version is a distinct paragraph text (sha) not present in the baseline; identical texts across commits count once (first commit kept).
Commits with `[polish]` in the subject, or whose author is not the owner, are skipped (PROTOCOL §2)."""
import sys
from common import *  # noqa: F401,F403

OWNER = "Ravindu Somawansa"


def freeze():
    if (EXP / "baseline.json").exists():
        sys.exit("baseline.json exists; the baseline is frozen (delete it by hand only before the first number)")
    base = {}
    for p in PAPERS:
        repo = REPOS / p
        pin = next((a.split("=", 1)[1] for a in sys.argv if a.startswith(f"--{p.split('paper-', 1)[-1]}=")), None)
        head = git(repo, "rev-parse", pin or "HEAD").strip()  # --<paper-suffix>=<commit> pins a baseline (CLARIFICATIONS.md C1)
        paras = paragraphs(show(repo, head))
        base[p] = {"commit": head, "date": git(repo, "log", "-1", "--format=%cI", head).strip(), "paragraphs": len(paras)}
        print(f"{p}: {head[:10]} {base[p]['date'][:10]} {len(paras)} paragraphs >= {MIN_WORDS} words")
    dump("baseline.json", base)
    print("total", sum(v["paragraphs"] for v in base.values()))


def collect():
    base = load("baseline.json") or sys.exit("run --freeze first")
    out = {}
    for p in PAPERS:
        repo, b = REPOS / p, base[p]["commit"]
        bparas = paragraphs(show(repo, b))
        seen = {sha(t) for t in bparas}
        entry = {"baseline": [{"id": sha(t), "text": t, "words": nwords(t)} for t in bparas], "versions": []}
        log = git(repo, "log", "--reverse", "--format=%H%x1f%cI%x1f%an%x1f%s", f"{b}..HEAD", "--", DRAFT).strip()
        for line in filter(None, log.split("\n")):
            commit, date, author, subject = line.split("\x1f")
            if "[polish]" in subject or author != OWNER:
                continue
            override = "reword" if "[reword]" in subject else "content" if "[content]" in subject else None
            for t in paragraphs(show(repo, commit)):
                h = sha(t)
                if h in seen:
                    continue
                seen.add(h)
                entry["versions"].append({"id": h, "commit": commit[:10], "date": date, "subject": subject, "override": override, "text": t, "words": nwords(t)})
        out[p] = entry
        print(f"{p}: {len(entry['baseline'])} baseline, {len(entry['versions'])} new paragraph texts")
    dump("versions.json", out)


if __name__ == "__main__":
    freeze() if "--freeze" in sys.argv else collect()
