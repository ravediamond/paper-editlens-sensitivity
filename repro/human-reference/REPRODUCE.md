# Reproduce

## L0 (CPU, seconds)
```bash
python3 l0_check.py
```

## L1 (GPU, the gated model, about 15 minutes at 25 W)
Fetch the PDFs listed in `expected/selected.json` from arxiv.org into a folder `pdfs/`, run `ws paper-polish serve` in road-to-robotics, then
```bash
python3 scripts/score_pdfs.py <folder holding pdfs/> expected/rows.json --ours <four main.pdf paths>
```
arXiv may serve a newer version than the one fetched on 2026-11-05; the ids in `selected.json` carry the version that was fetched.

## L2
Not applicable.
