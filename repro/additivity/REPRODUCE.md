# Reproduce

## L0
```bash
python3 l0_check.py
```

## L1
`scripts/additivity.py` scores the 46 hunk variants and the 52 original and rewritten paragraphs again. It needs `pangram/editlens_Llama-3.2-3B` (CC BY-NC-SA 4.0, non-commercial, research use) behind the scorer server of the working repository (`ws paper-polish serve`), and takes a few minutes on an Orin NX.
