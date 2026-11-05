# Changelog

- 2026-11-05: repository created. Draft of the paper, three experiments with their L0 checks.
- 2026-11-05: two paragraphs (limitations, introduction) rewritten with `ws paper-polish` (mean 0.198 to 0.181); `polish/` holds the baseline and every scored candidate.
- 2026-11-05: human reference added (repro/human-reference): 39 pre-2022 robot-learning papers scored by section with the open model through the same PDF extractor as our four PDFs. Paper means have a median of 0.085 (0.041 to 0.130); human results paragraphs have a median of 0.046. Section 3.5 and the abstract updated.
- 2026-11-05: style trial (section 3.6): style features of human and our paragraphs, and seven paragraphs of two of our papers rewritten toward the human style. 5 of 7 paragraphs not lowered; mean change +0.020. The four papers are unchanged by this trial.
- 2026-11-05: abstract, introduction and conclusion updated with the human reference and the style trial; conclusion paragraph polished with ws paper-polish.
- 2026-11-05: correction of the human reference. Reference lists and acknowledgements kept as prose by the extractor (116 human paragraphs, 7 of ours) are excluded after inspection of the highest scores; human paper-mean median 0.085 to 0.071, all four of our papers now above the highest human paper.
- 2026-11-05: section 3.7 and repro/triggers: single edits on hosts not chosen by score, with a real-sentence control. Language-model-style sentences and generic openers raise the score, our digits raise it, a figure pointer lowers it, a long specific technical paragraph lowers it most; single evaluative words hardly matter; the gradient attribution is diffuse. The first battery (hosts chosen by score) is kept and explained.
