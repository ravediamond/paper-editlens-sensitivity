# Attribution and lexicon (exploratory, 2026-11-05)

Not pre-registered.

- **Sentence leave-one-out** (`scripts/loo_all.py`): for each sentence of every paragraph of 40 words or more with at least two sentences (469 sentences of the original texts), the paragraph score minus the score of the paragraph without that sentence (`expected/loo_all.json`).
- **Word deletion** (`scripts/words.py`): the same for every single word of the 20 highest paragraphs (2,042 deletions, `expected/word_loo.json`).
- **Lexicon** (`scripts/mklex.py`): the sentence contribution after removing its linear dependence on sentence length, averaged over the sentences that contain each word; a word is listed if it occurs in at least 6 sentences of at least 3 papers and its 95 % bootstrap CI excludes 0. Validity: leave-one-paper-out correlation of the lexicon's prediction with the held-out sentence effects, against the 95th percentile of 200 shuffled-label runs; agreement in sign with the word-deletion source.
- **Known limit.** About 100 words were tested, so around 5 of the 19 listed words could be chance. The lexicon describes association in four papers and was not tested by swapping words.
