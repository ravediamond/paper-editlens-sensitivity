# production-observations

Texts the owner pasted into the production Pangram detector (web page) on 2026-11-09, with the verdict he read off the page.
This is a log of observations, not a pre-registered experiment: no protocol was frozen, the texts were chosen as the day went,
and only verdict labels were noted (a percentage where the page showed one). The open 3B model was not run on these texts yet.

- `texts/` the seven texts of our own, verbatim (T1–T7). The dictated ones (T5–T7) were spoken from keyword outlines that the AI
  assistant wrote, so their order and some phrases come from the assistant.
- `expected/observations.json` one row per text (origin, words, verdict as reported), plus two external papers: for
  arXiv:2610.20563 only the section and opening words of each paragraph the owner saw flagged (no text copied); for the
  Mistral Large 4 report only the owner's note that it was not flagged.
- `expected/summary.json` the counts the paper uses; `l0_check.py` recomputes them and checks the word counts against `texts/`.

Next step (L1, not done): score T1–T7 and the arXiv:2610.20563 paragraphs with the open 3B model on the Orin, so the two detectors
can be compared on the same texts.
