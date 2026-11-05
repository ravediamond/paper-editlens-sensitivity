# human-reference

`l0_check.py` recomputes the section-type and paper-level means, medians and shares from `expected/rows.json`. The scores are L1: `scripts/score_pdfs.py` with the model server up, on PDFs that are not stored here (`expected/selected.json` lists the arXiv ids and dates).
