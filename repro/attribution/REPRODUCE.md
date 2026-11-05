# Reproduce

## L0 (CPU, under a minute)
```bash
python3 l0_check.py
```

## L1 (GPU, the gated model)
`scripts/loo_all.py` (about 470 scorings) and `scripts/words.py` (about 2,000 scorings, about 19 minutes at 25 W), run with the model server up and the paragraph inventory in place, as for `controlled-edits`. `scripts/mklex.py` then rebuilds `lexicon.json` and the tables on CPU.

## L2
Not applicable.
