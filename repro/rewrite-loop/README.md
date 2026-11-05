# rewrite-loop

`l0_check.py` recomputes the loop statistics from `expected/iterlog.jsonl` and each paper's before and after mean from `expected/before_after_rows.json`. `RESULTS.md` is the write-up of 2026-11-05; `scripts/` holds the workbench used (`wb.py` and `batch.py` score and rank candidates, `tw.py` ports paragraphs to a tex twin, `reapply.py` replays rewrites onto a newer source). The reusable version is `ws paper-polish` in road-to-robotics.
