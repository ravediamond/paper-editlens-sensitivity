# Reproduce

## L0 (CPU, seconds)
```bash
python3 l0_check.py
```

## L1 (GPU, the gated model)
Needs `pangram/editlens_Llama-3.2-3B` (access granted to the account) and `meta-llama/Llama-3.2-3B`, in a venv with torch, transformers and peft. In road-to-robotics: `ws paper-polish serve`, then run `scripts/exp.py` and `scripts/exp2.py` from a scratch folder holding the paragraph inventory (`inventory.json`, the original rendered paragraphs) and the workbench modules (`scripts/wb.py`, `score.py`, `server.py`, all in this folder). The scripts are the originals used on 2026-11-05 and expect that scratch layout; they are kept for the record and for the method, not as a one-command rerun. About 1,300 scorings, about ten minutes at 25 W.

## L2
Not applicable.
