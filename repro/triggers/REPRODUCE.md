# Reproduce

## L0 (CPU, seconds)
```bash
python3 l0_check.py
```

## L1 (GPU, the gated model, about 40 minutes at 25 W)
`ws paper-polish serve` in road-to-robotics, then `python3 scripts/trigger_battery2.py <human texts json> ../human-reference/expected/excluded_back_matter.json ../controlled-edits/expected/paragraphs.json expected/battery2.json`. The human texts are re-extracted from the PDFs listed in `../human-reference/expected/selected.json` and are not stored here.

## L2
Not applicable.
