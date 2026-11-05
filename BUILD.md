# Build (2026-11-05)

Assembled by hand from road-to-robotics `journal/papers/ai-map/2026-11-05_rewrite/` and `journal/papers/editlens-influence/` at road-to-robotics `5bf8b8fecd`, plus the layout (Makefile, style, CI, `md2tex.py`) of paper-reward-models-stopping-rule. No raw data is stored here beyond the paragraph texts of the author's four papers.

- L0: every `repro/*/l0_check.py` passes (`make l0`).
- `make check` regenerates the paper from `repro/*/expected/` and fails on any difference.
- `paper/make_paper.py`: every number in `numbers.json` has an anchor inside `repro/` or names the road-to-robotics file it was read from (the five correlations of the earlier table and the three human reference means are read, not recomputed).
