# EditLens rewrite of the four papers, 2026-11-05: what was done and what it showed

Scorer: `pangram/editlens_Llama-3.2-3B` on the Orin (the open 3B model, not the production detector alphaXiv runs), raw score in [0, 1], one paragraph per scoring. Every number below is in `data/results.json` or the files named next to it; the tools that produced them are in `tools/`. The scorer is licensed CC BY-NC-SA 4.0 and was used on the four papers only.

What a score means here: EditLens estimates how much AI editing a text holds. It does not say who wrote a text. These papers were drafted and rewritten with an AI assistant, so a low score does not make them human-written, and the open 3B model is weaker than the production one. Pre-2022 human robot-learning papers score 0.053, 0.055 and 0.095 as paper means.

## 1. Result

| paper | paragraphs | mean before | mean after | worst paragraph before | after |
|---|---|---|---|---|---|
| register-reproducibility | 23 | 0.211 | 0.153 | 0.296 | 0.218 |
| jepa-world-model | 22 | 0.176 | 0.160 | 0.315 | 0.257 |
| reward-models-stopping-rule | 21 | 0.202 | 0.189 | 0.301 (a caption, not edited) | 0.301 |
| vla-edge-inference | 18 | 0.233 | 0.207 | 0.309 | 0.298 |

Word-weighted mean of the paragraph scores of the rendered text with citations stripped (`tools/summarize.py`). None of the four reached the human range (0.05 to 0.10). Number-dense paragraphs (results, related work, setup) stall at 0.15 to 0.20.

Placeholders and `numbers.json` are unchanged in all four repos; `make l0 paper` passes after staging; `ws prose-check` passes; PDFs are rebuilt. Nothing is committed.

## 2. The rewrite loop

90 candidate rewrites in 50 paragraph-rounds (`data/iterlog.jsonl`). 50 of the 90 scored below the current text (by more than 0.005). The best candidate of a round improved the paragraph in 64 % of the rounds, by 0.032 on average. One candidate dropped a placeholder (a confidence interval) and was rejected.

Moves that lowered a paragraph, with the largest cases:

| move | case | before | after |
|---|---|---|---|
| name the specific works instead of the field | jepa introduction (ContactGuard, HWM, H-JEPA named) | 0.315 | 0.164 |
| open from the concrete case, class letter after it | register classes B and C | 0.253 | 0.145 |
| split a list sentence into plain statements | register cold reruns ("a larger GPU, a private checkpoint, the arm, or a step the write-up leaves out") | 0.253 | 0.139 |
| move a generic sentence to where it belongs or drop a duplicate | register "papers were chosen for one stack" moved; limitations lost two sentences | 0.273 / 0.275 | 0.150 / 0.158 |
| "we ran / we measured" plus the named thing | vla Euler steps; vla power modes; reward data paragraph | 0.271; 0.292; 0.211 | 0.156; 0.206; 0.154 |
| put the interval in its own sentence | reward truncation paragraph | 0.285 | 0.212 |

Moves that did not work: merging sentences into longer ones with "so" or "which means" (register limitations, 0.275 to 0.360 to 0.366 in three variants); adding a contrast sentence to a short paragraph (0.214 to 0.338); naming the tricks in the vla introduction (0.270 to 0.281 and 0.314); restating numbers first in a conclusion (0.218 to 0.28).

## 3. Controlled edits on 62 paragraphs (original texts, `data/exp_transforms.json`, `data/exp_insert.json`)

Change in the paragraph score, mean over paragraphs, 95 % bootstrap CI.

| edit | n changed | effect |
|---|---|---|
| upper-case and double spaces (null) | 62 | 0.000 exactly (the model lower-cases and collapses spaces) |
| shuffle or reverse the sentences | 62 | means within ±0.004, CIs contain 0 (about ±0.012) |
| "we/our" to "I/my" | 52 | +0.001 (−0.004 to +0.006) |
| append a real sentence from another paragraph of the same paper | 62 | +0.003 (−0.005 to +0.011): length alone does nothing |
| keep only the first half of the sentences | 62 | −0.029 (−0.044 to −0.015) |
| drop the parentheticals | 27 | −0.018 (−0.033 to −0.005) |
| split at ", and" and ", but" | 28 | −0.014 (−0.020 to −0.007) |
| mask every number with "many" | 55 | −0.021 (−0.030 to −0.012) |
| join sentence pairs with a semicolon | 62 | +0.047 (+0.039 to +0.056), 92 % of paragraphs rise |
| append "The result holds on this rig." (generic closer) | 62 | +0.017 (+0.012 to +0.022) |
| append "This is a limit of the setting, not of the method." (contrast) | 62 | +0.011 (+0.006 to +0.017) |
| append "Check the simple baseline first." (advice) | 62 | +0.001 (−0.004 to +0.005) |
| append "We ran this on the Jetson Orin NX." | 62 | −0.001 (−0.007 to +0.005) |
| append "The row fails." (verdict) | 62 | −0.015 (−0.020 to −0.011) |

The baseline texts already had their semicolons and colons removed (rule 78, earlier the same day), so the reverse test (adding semicolons) is the only one that could be run.

Correlational claims of rule 78 against these controlled tests:

| feature (rule 78, 311 sentences) | correlational | controlled |
|---|---|---|
| semicolons | +0.028 | +0.047, confirmed |
| contrast framing | +0.029 | +0.011, confirmed, smaller |
| advice or imperatives | +0.021 | +0.001, not confirmed |
| verdict words | +0.020 | −0.015, reversed |
| "we/our" doing something | −0.020 | −0.001 to +0.001, not confirmed |

## 4. Word-level and sentence-level attributions

- Word deletion on the 20 highest paragraphs, 2,042 deletions (`data/word_loo.json`): the mean deletion changes the score by +0.013 (every word adds a little), 39 % of deletions move it by less than 0.01, the largest single deletion by 0.157. No single word carries a paragraph.
- Sentence leave-one-out on 469 sentences (`data/loo_all.json`): sentence length does not predict its contribution (slope −0.00015 per word). The sentences that push a paragraph up are mostly generic statements about the field or the register ("Each paper reports the use that worked on its own robot and data", +0.097; "The register file lists the papers scheduled next", +0.106), list sentences, and sentences that carry an interval ("Length observed up to that cut gives 0.851 within policy (CI 0.829–0.873; Fig. 2)", +0.166).

## 5. The lexicon

`../EDITLENS_LEXICON.md`. A lexicon built on three papers and tested on the fourth correlates 0.116 with the held-out sentence effects, against a permutation ceiling of 0.096 (95th percentile): it is real and weak. The word-deletion source agrees in sign for 48 of 80 words (correlation 0.47). Use it as a tie-breaker between synonyms, not as a target.

## 6. What the numbers say about writing

1. Specific naming and plain "we ran X on Y" sentences lower a paragraph; generic framing, list sentences, semicolons, generic closers and contrast closers raise it.
2. Rhythm, order and pronouns do nothing, which is why the earlier rule about varying sentence length was dropped.
3. A paragraph made of results (numbers, intervals, verdicts) has a floor around 0.15. Going lower needs content only the author has (a decision and its reason, a thing that went wrong), which a rewrite cannot add; rule 4 forbids inventing it.
