# Reproduce

## L0 (CPU, seconds)
```bash
python3 l0_check.py
```

## L1 (GPU, the gated model)
Each score in `iterlog.jsonl` and `before_after_rows.json` is one EditLens scoring of the text stored next to it. To rescore: `ws paper-polish serve`, then score the stored texts with `scripts/rows.py` (paper rows) or `scripts/batch.py` (candidates). Scores vary in the third decimal between runs on different hardware; the L0 tolerances account for the stored rounding only.

## L2
Not applicable.
