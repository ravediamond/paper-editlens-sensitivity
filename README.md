# What moves an open AI-edit detector on technical prose

Controlled edits, one feature at a time, scored with Pangram's open EditLens 3B model on four robotics papers. A correlation table of 469 sentences suggested five features (semicolons, contrast framing, advice, verdict words, "we"); as controlled edits on 62 paragraphs two held, one reversed and two did nothing. The repository also holds the paragraph-by-paragraph rewrite of the four papers that followed, with the scores of every candidate.

The scorer is the open model, not the production Pangram detector, and the texts were drafted and rewritten with an AI assistant. A low score is a pointer to paragraphs to reread. It does not say who wrote a paragraph.

## What is here

- `paper/`: the draft (markdown and LaTeX sources, `make_paper.py`, `numbers.json` with every number's anchor, the built `main.pdf`).
- `repro/controlled-edits/`: the 62 paragraphs, the per-paragraph score change of every edit, the L0 check.
- `repro/additivity/`: the rewrites split into sentence-level hunks, each applied alone and scored, the summary, the L0 check.
- `repro/rewrite-loop/`: every scored candidate rewrite (`iterlog.jsonl`), the per-paragraph scores of the four papers before and after, the original and final paper sources, the L0 check, `RESULTS.md`.
- `repro/attribution/`: sentence leave-one-out and word-deletion scores, the lexicon, the L0 check, `EDITLENS_LEXICON.md`.
- `repro/human-reference/`: 39 human robot-learning papers from before November 2022 (the first 40 results of an arXiv query, rule fixed before scoring), scored by section with the same PDF extractor as our own four PDFs; arXiv ids, scores and hashes, no text; the L0 check.
- `PROVENANCE.md`: where every file was copied from.

## Reproduce

- **L0** (CPU, seconds to a minute): `make l0`. Recomputes every mean, share and the lexicon validity from the stored rows.
- **Paper**: `make paper` regenerates `numbers.json`, `main.tex` and `DRAFT_4p.md` from `repro/*/expected/` and fails on any difference. `make pdf` builds `main.pdf` with tectonic. `make check` runs all three.
- **L1** (GPU, the gated model): the per-paragraph scores themselves. Each experiment's `REPRODUCE.md` gives the command. It needs `pangram/editlens_Llama-3.2-3B` (CC BY-NC-SA 4.0, non-commercial, access granted per account) on `meta-llama/Llama-3.2-3B`.

## Licence and use

The model is licensed for non-commercial use and was run on the author's own four papers only. Nothing here is a service or an authorship test.
