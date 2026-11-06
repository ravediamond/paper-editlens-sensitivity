# Human-edit dose–response of the open EditLens score (WS-166) — frozen before any number

Date: 2026-11-06. Status: bars **proposed, owner to confirm** before the first number (frozen-protocol step 3). Once confirmed, this file is committed with the message `WS-166: protocol frozen (before any number)` and any later change is a numbered deviation in §7.

## 1. Question

Same edit magnitude, opposite direction: does the open EditLens 3B score fall when a human edits an AI-drafted paragraph as much as it rises when an AI edits a human paragraph, or does the score track the last editor rather than the amount of editing?

Secondary, descriptive: at what human edit magnitude does half of the AI-drafted paragraphs fall below the human reference (paragraph p90 0.177, paper-mean median 0.071, `../human-reference/expected/summary.json`)?

## 2. Data

**Human direction (new rows).** The four paper repositories (`ravediamond/paper-register-reproducibility`, `paper-jepa-world-model`, `paper-reward-models-stopping-rule`, `paper-vla-edge-inference`), file `paper/DRAFT_4p.md` (the rendered text, numbers filled).

- *Baseline* of a paper = the text at the commit recorded in `expected/baseline.json` by `scripts/snapshot.py --freeze` (the HEAD of each repo at freeze time, i.e. the version after the 2026-11-05 loop rewrite and before any hand edit). These are the AI-drafted texts: drafted and rewritten by Claude Code, see `../rewrite-loop/RESULTS.md`.
- *Versions* = every later commit on the default branch (`main`) that changes `paper/DRAFT_4p.md`. A version of a paragraph is a distinct text; identical texts across commits count once. Versions are added by the owner editing by hand (phone or laptop), with no scorer open while editing. Commits produced by `ws paper-polish apply` after the freeze are excluded (`[polish]` in the message, or any commit whose author is not the owner).
- *Unit* = a paragraph of at least 40 words after citation stripping (`paper_map.strip_cites`), as in `../controlled-edits`. Headings, tables, figure captions, code blocks and block quotes are not paragraphs.
- *Alignment* (`scripts/align.py`): each version paragraph is matched to the baseline paragraph of the same paper with the highest word-level `difflib` ratio; a match below 0.30 is a *new paragraph* and is excluded from the curve (counted in `summary.json: new_paragraphs`). A baseline paragraph matched by two or more version paragraphs (a split) keeps the one with the higher ratio; the other becomes new. Two version paragraphs matched to one baseline paragraph by a merge are not separated; the merge is logged.
- *Edit type* (`scripts/align.py`, automatic): `content` when the version adds at least one numeric token absent from the baseline, or at least one capitalised name absent from the baseline, or grows by more than 15 % in words; otherwise `reword`. The owner may override with `[reword]` / `[content]` in the commit message, which applies to every paragraph that commit changed; the override is recorded as such.
- *Sample size*: the four drafts hold about 50 paragraphs of at least 40 words (13 in the register paper on 2026-11-06). The curve is reported when at least 40 baseline paragraphs have at least one version; a magnitude bin is evaluated when it holds at least 20 version rows from at least 10 baseline paragraphs on the human side and 20 rows on the AI side, otherwise it is `not proven`. Progress is printed by `scripts/analyze.py --progress`.

**AI direction (reference rows).** The `pangram/editlens_iclr` dataset, test split, AI-edited class, scored with the same 3B model through `scripts/ai_curve.py`. If the split carries the source text, magnitudes are recomputed with §3 so that both directions use one metric; if it carries only the authors' label, the label is used and the deviation is noted. Fallback if neither: 300 paragraphs from the 39 human reference papers (`../human-reference`, rule unchanged), edited once by `claude-sonnet-4-5` with the 31 test-split prompts of EditLens Table 8, one prompt per paragraph drawn with seed 0. The fallback is also run as a same-domain check if the dataset route works (exploratory, §8).

## 3. Metric

- *Magnitude* m between baseline x and version y, the two supervision metrics of EditLens as released in `pangramlabs/EditLens/scripts/scoring/` and vendored in `scripts/magnitude.py`: cosine distance with `Qwen/Qwen3-Embedding-0.6B` (their default) and soft n-grams with `all-MiniLM-L6-v2`, τ = 0.8, phrases of 6–12 words. Cosine is primary; soft n-grams is reported. Both run on the Orin in the `editlens` venv.
- *Score* s = `pangram/editlens_Llama-3.2-3B` through `ws paper-polish serve` (`paper_polish.score`), one paragraph per call, as in every other experiment here.
- *Outcome per paragraph version*: Δ = s(y) − s(x). Human direction x is AI-drafted, Δ expected ≤ 0. AI direction x is human, Δ expected ≥ 0.
- *Bins* of cosine magnitude, fixed now: [0.00, 0.03), [0.03, 0.06), [0.06, 0.10), [0.10, 0.15), [0.15, 1.00]. The 0.03 and 0.15 edges are EditLens's own thresholds for "edited" and "fully AI" (their Appendix C).
- *Aggregation*: per bin, mean Δ and mean |Δ| with a 95 % bootstrap CI, 2,000 resamples, seed 0, resampling unit = baseline paragraph (all its versions move together). Ratio R_bin = mean|Δ_human| / mean|Δ_AI|, CI by paired bootstrap of the two groups.
- *Descriptive curve*: for the human direction, the share of version paragraphs below 0.177 per bin, and the smallest bin where that share reaches 0.5.

## 4. Baselines and nulls

- *Identity null*: every baseline paragraph scored twice in separate server calls; the mean |difference| is the noise floor and is subtracted from nothing, only reported. A bin whose |Δ| CI contains the noise floor is read as no effect.
- *Length null*: Δ regressed on the word-count change (y − x) within each bin; if the slope's CI excludes 0, the per-bin result is also reported after removing the length effect (exploratory).
- *Same-set comparison*: human-direction bins are compared only with AI-direction bins of the same cosine range; no comparison across papers' means.

## 5. Bars (proposed, owner to confirm; source: chat 2026-11-06, Claude draft)

Evaluated per bin with the §2 sample sizes; a bin with fewer rows is `not proven`.

- **B1, magnitude-driven**: the score tracks the amount of editing if the 95 % CI of R_bin lies within [0.5, 2.0] in every evaluated bin. *Pass* if all evaluated bins; *fail* if any evaluated bin's CI lies entirely outside [0.5, 2.0]; *not proven* otherwise.
- **B2, last-editor**: the score tracks the last editor if, in at least two evaluated bins, the CI of R_bin lies entirely above 2.0 (small human edits collapse the score more than equal AI edits raise it). *Pass* / *fail* / *not proven* as above.
- **B3, robust to human polish**: in at least two evaluated bins the CI of R_bin lies entirely below 0.5. B2 and B3 cannot both pass; if neither passes and B1 fails, the result is reported as mixed with the per-bin table.
- **B4, reword vs content** (needs 20 rows from 10 paragraphs of each type in a bin): if the CI of mean Δ_content − mean Δ_reword excludes 0 in a bin, content and rewording are reported separately for the whole paper; otherwise together. No pass/fail; this decides the presentation.
- **Threshold for the production run** (not a bar on the result, a gate on spending): the production Pangram API is run once, on every baseline and version paragraph and on the AI-direction rows, only when (a) ≥ 40 baseline paragraphs have a version, (b) at least three bins are evaluable on the 3B model, (c) the identity null is below 0.01. Budget cap $25. Its results are analysed with exactly this §3–§5 and reported next to the 3B ones; the paper's headline uses the production numbers if they exist.

## 6. Checks before numbers

1. `scripts/snapshot.py --freeze` prints the four baseline commits and the paragraph count per paper (expected about 50 in total; `../controlled-edits` had 62 before the loop rewrite shortened the drafts).
2. `scripts/magnitude.py --selftest`: cosine(x, x) = 0 and soft-n-grams(x, x) = 0 exactly; cosine between two unrelated baseline paragraphs > 0.15; a hand-made edit (one synonym in a 60-word paragraph) gives cosine in (0, 0.03).
3. Two baseline paragraphs scored by hand through `ws paper-polish try` and compared with `scripts/score_versions.py` to 4 decimals.
4. `scripts/align.py --check` lists every merge and every new paragraph for the owner to glance at before the curve is read.
5. `scripts/ai_curve.py --columns` prints the dataset's columns; the route (§2, dataset / label / fallback) is written into `expected/ai_route.json` before any AI-direction score is computed.

## 7. Deviations

(none)

## 8. Exploratory, decided after data

- The length-adjusted per-bin results (§4).
- Soft-n-gram bins, if they disagree with cosine bins.
- Per-paper curves (four papers, too few per bin for bars).
- The same-domain fallback when the dataset route worked.
- Any threshold read from alphaXiv's display for the production model.
