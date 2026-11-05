# EditLens lexicon: words that go with lower and higher scores in the four papers

Built 2026-11-05 from `2026-11-05_rewrite/data/loo_all.json` (469 sentences of the four papers, original texts) and `word_loo.json` (2,042 word deletions in the 20 highest paragraphs). Scorer: `pangram/editlens_Llama-3.2-3B`, the open model. Read `2026-11-05_rewrite/RESULTS.md` first.

## How much to trust it

An effect here is the change in a paragraph's score when the sentence holding the word is removed, after taking out the linear effect of sentence length. A word is listed only if it occurs in at least 6 sentences of at least 3 of the 4 papers and its bootstrap 95 % CI excludes 0. With about 100 words tested, around 5 of 19 listed words could be chance.

- Held-out check: a lexicon built on three papers predicts the fourth paper's sentence effects with a correlation of 0.116, against 0.096 for the 95th percentile of shuffled labels. It is real and weak.
- The word-deletion source and the sentence source agree in sign for 48 of 80 words and correlate 0.47.
- It describes association in these four papers. A word-for-word swap was not tested. Do not replace a word if the meaning changes (rule 30), and do not treat a score as a target (rule 40).

Use it as a tie-breaker between synonyms and as a pointer: a word on the raising list in a high-scoring paragraph is a place to look for a more specific noun, a file, a paper or a number.

### Words in sentences that lower the paragraph score

| word | mean effect | sentences | 95 % CI | word-deletion check |
|---|---|---|---|---|
| table | -0.030 | 12 | -0.052 to -0.008 |  |
| takes | -0.025 | 6 | -0.049 to -0.001 |  |
| does | -0.025 | 9 | -0.044 to -0.005 |  |
| about | -0.022 | 9 | -0.046 to -0.004 |  |
| tested | -0.021 | 7 | -0.035 to -0.010 |  |
| passes | -0.017 | 7 | -0.035 to -0.002 |  |
| vla | -0.017 | 14 | -0.033 to -0.002 | -0.023 |
| not | -0.016 | 34 | -0.025 to -0.006 | -0.020 |
| more | -0.014 | 7 | -0.027 to -0.003 |  |
| task | -0.014 | 9 | -0.030 to -0.003 |  |
| by | -0.010 | 22 | -0.025 to -0.000 | -0.006 |

### Words in sentences that raise it

| word | mean effect | sentences | 95 % CI | word-deletion check |
|---|---|---|---|---|
| alone | +0.040 | 6 | +0.017 to +0.069 |  |
| ci | +0.040 | 10 | +0.011 to +0.073 |  |
| commanded | +0.030 | 9 | +0.001 to +0.056 |  |
| protocol | +0.027 | 8 | +0.005 to +0.057 | +0.031 |
| rule | +0.026 | 8 | +0.009 to +0.041 | +0.023 |
| come | +0.022 | 7 | +0.003 to +0.043 |  |
| committed | +0.020 | 10 | +0.002 to +0.040 | -0.007 |
| reports | +0.020 | 9 | +0.001 to +0.046 | +0.023 |

## What the two lists have in common

- Raising words are the vocabulary of a method talking about itself: protocol, rule, committed, reports, CI, alone, commanded, plus (below the strict cut, same sign in both sources) threshold, baseline, claims, papers, policy, register, rig, each, both, before. A sentence made of these says that a procedure was followed. Replace the label with the thing: the file (`PROTOCOL.md`, commit hash), the number, the paper's name, the model's name.
- Lowering words are plain function words and concrete task words: not, does, about, by, more, tested, passes, takes, task, table, VLA. Below the strict cut and the same in both sources: also, against, per, on, for, same, second, two, ten, ms, arXiv, AUROC, chunks, samples, imagined, progress. These are what a sentence about a measurement, a unit or a named method looks like.
- Single-paper words (repository, probes, cpp, ArmnetBench, DINOv2) lower too but are topic words of one paper, not a lexicon.

## Using it while writing

1. Draft in the plain forms: "we ran X on Y", the unit, the file name, the paper's name.
2. When a sentence is only about procedure ("the protocol committed the rule before the run"), write what was committed and where, once, and cut the rest.
3. Run the paragraph through the scorer (`2026-11-05_rewrite/tools/`, see rule 79); where a paragraph scores above 0.25, check its raising words and its list and semicolon sentences first, then the generic opener and closer.
