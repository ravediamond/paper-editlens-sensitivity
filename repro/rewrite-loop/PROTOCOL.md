# Rewrite loop (exploratory, 2026-11-05)

Not pre-registered. The task was to lower the paragraph scores of four papers (register-reproducibility, jepa-world-model, reward-models-stopping-rule, vla-edge-inference) without changing a number, a placeholder or a claim.

- **Loop.** For a paragraph: rank its sentences by leave-one-out contribution, write two to four candidate rewrites with the paper's placeholders kept, render and score them, keep the lowest candidate that preserves every placeholder, repeat for one to three rounds (`expected/iterlog.jsonl`: every scored candidate with round, score, placeholder check and text).
- **Rewrites** were written by an AI assistant (Claude Code) working in the author's repository. The author had not reviewed them paragraph by paragraph when the paper was written.
- **Content moves** in the register paper: one sentence moved to another paragraph and one that repeated another was dropped. No number, placeholder or verdict changed; `numbers.json` of each paper is unchanged and `make l0 paper` passes in each.
- **Outcome.** Per-paragraph scores before and after (`expected/before_after_rows.json`), the word-weighted mean per paper, and the loop statistics (candidates, share lower, share of rounds that improved, mean best drop).
- **Sources.** `sources/<paper>.orig.md` is the source before the rewrite, `<paper>.src.md` after. The after sources are the ones in the four paper repositories, apart from edits the author made to them later.
