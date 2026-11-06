# Reproduce

## L0 (CPU, seconds)
```bash
python3 l0_check.py
```
Passes with "no rows yet" until the first number exists.

## L1 (GPU, the gated model), on the Orin in the `editlens` venv
```bash
cd road-to-robotics && ws paper-polish serve            # loads pangram/editlens_Llama-3.2-3B (about a minute)
P=~/venvs/editlens/bin/python; S=repro/human-dose/scripts
$P $S/snapshot.py --freeze    # once: the four baseline commits (PROTOCOL §2); refuses to overwrite
$P $S/magnitude.py --selftest # §6 check 2
$P $S/ai_curve.py --columns   # §6 check 5: the dataset's columns, the route written before any AI score
$P $S/snapshot.py             # every later hand-edited version of every paragraph (rerun after each batch of edits)
$P $S/align.py --check        # merges and new paragraphs, for the owner to glance at
$P $S/align.py
$P $S/magnitude.py            # cosine (Qwen3-Embedding-0.6B) and soft n-grams (MiniLM) per pair; incremental
$P $S/score_versions.py       # 3B scores, baselines twice (identity null); incremental
$P $S/ai_curve.py             # 600 AI-direction rows from pangram/editlens_iclr (test), once
$P $S/analyze.py --progress   # coverage per bin; the bars need 40 covered paragraphs and 20 rows per bin
$P $S/analyze.py              # summary.json: bins, ratios, verdicts, the production-run gate
```
`magnitude.py` and `score_versions.py` keep what is already computed, so the loop is: edit by hand, commit, rerun the last six lines.

## L2 (the production Pangram API, ~$25 cap)
Only when `summary.json: gate.production_run_allowed` is true. Not written yet; it will score the same ids with the same analysis.
