# Controlled edits (exploratory, 2026-11-05)

Not pre-registered: no bar was committed before the run, and the results are descriptive. The question came after a correlation table (sentence-level scores of 311 sentences, WRITING_RULES.md section K of road-to-robotics) had suggested five features.

- **Texts.** The 62 paragraphs of at least 40 words in the rendered drafts of four papers as they stood before the rewrite (`expected/paragraphs.json`), citations stripped.
- **Scorer.** `pangram/editlens_Llama-3.2-3B`, raw score in [0, 1], each paragraph as a text of its own; the model lower-cases and collapses spaces.
- **Edits** (`scripts/exp.py`, `scripts/exp2.py`): case and spacing (a null), shuffle, reverse, first sentence last, drop first or last sentence, first half only, drop parentheticals, split at ", and" and ", but", mask numbers, "we" to "I", join sentence pairs with a semicolon, and appending one fixed sentence (generic closer, advice, verdict, contrast, "We ran this on the Jetson Orin NX.") or a real sentence from another paragraph of the same paper.
- **Outcome.** Score of the edited paragraph minus the score of the original, per paragraph (`expected/exp_transforms.json`, `exp_insert.json`, key `raw`). Mean over paragraphs with a 95 % bootstrap CI (2,000 resamples); for edits that change only some paragraphs the mean over the paragraphs the edit changes (`subset_effects.json`).
- **Known limit.** Semicolons and colons had been removed from the texts before the run, so only adding them could be tested. The appended sentences are examples chosen by the author.
