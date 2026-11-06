# Additivity of the rewrite moves

The 26 paragraphs the rewrite loop changed, each rewrite split into sentence-level hunks, each hunk applied alone to the original and scored with the open EditLens model. `PROTOCOL.md` is the protocol (committed before any score), `scripts/additivity.py` runs it (needs the scorer server of the working repository), `scripts/summarize.py` computes the statistics, `expected/additivity.json` holds every hunk and score and `expected/additivity_summary.json` the summary the paper reads. `l0_check.py` recomputes the summary.
