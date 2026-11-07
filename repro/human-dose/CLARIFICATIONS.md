# Clarifications to PROTOCOL.md (WS-166), written before any number

Date: 2026-11-07. Basis: owner-delegated to agent recommendation 2026-11-07 (owner, chat: for bars, opinions and decisions the agent's recommendation is taken). These clarify how an ambiguous sentence is read. They change no threshold, bin edge, sample-size rule or bar in PROTOCOL.md. Where two readings were possible the one that can only make a verdict stricter (fail or not proven rather than pass) was taken. The readback list of 29 was not kept verbatim in the item notes; this file is the written record of the readings, grouped by section.

## Baselines
C1. Baseline of each paper = the last commit touching `paper/DRAFT_4p.md` at or before 2026-11-06 15:17 Paris (protocol commit time), verified from git log: register 781586d (12:24), jepa 6559e84 (10:31), reward-models 7389b94 (09:47), vla 1a2d28b (09:44). Frozen with `snapshot.py --freeze --register-reproducibility=781586d --jepa-world-model=6559e84 --reward-models-stopping-rule=7389b94 --vla-edge-inference=1a2d28b`; the script gained that pin option (no other change). "HEAD at freeze time" in §2 is read as these pins.
C2. Later commits that touch DRAFT_4p.md (reward-models 98c5897 2026-11-07, vla 5788165 2026-11-07, and any other authored by the owner after the baseline) count as versions, since all are authored under the owner's name; the owner may exclude one by saying it is not a hand edit, before the curve is read.
C3. A paragraph that reverts to its baseline text is not a version (identical to baseline, counted once as baseline).

## Data and alignment (§2)
C4. "Paragraph of at least 40 words" is judged on the baseline text for coverage; a version of a baseline paragraph is kept even if it falls below 40 words.
C5. "Default branch" = `main` in all four repos.
C6. Exclusion by author: author name must equal Ravindu Somawansa exactly; any other author is excluded.
C7. A version text is kept once, at the first commit that introduced it (the script's rule); later intermediate texts of the same paragraph each count as separate versions if distinct.
C8. Match ratio exactly 0.30 counts as matched (new only if < 0.30).
C9. Merges: the merged paragraph is aligned to its best baseline paragraph only; the merge is logged and the paragraph is flagged; the owner may drop flagged rows before the curve is read (stricter: dropping never adds rows).
C10. The edit-type rule: "grows by more than 15 %" is strictly greater than 0.15 in word count; a capitalised name is a capitalised token not at sentence start; any one condition suffices. A `[reword]`/`[content]` override applies to every paragraph that commit changed and is reported as an override.
C11. Sample-size rule: "20 rows from 10 paragraphs" means at least 20 rows and at least 10 distinct baseline paragraphs, both on the human side; AI side at least 20 rows. Below that, the bin is `not proven`.
C12. "At least 40 baseline paragraphs have at least one version" counts distinct baseline paragraphs with at least one aligned non-new version.
C13. AI direction: if the dataset carries source text, magnitudes are recomputed with §3 (preferred); otherwise the label is used and noted. A fallback route stops for the owner (needs a go).

## Metric and aggregation (§3)
C14. Bin edges are half-open on the right, [lo, hi), except the last bin which is [0.15, 1.00] closed; a magnitude exactly on an edge goes to the upper bin. A magnitude above 1.00 (possible for cosine distance) goes to the last bin.
C15. Mean Δ and mean |Δ| per bin are means over rows (version paragraphs); the paragraph is the bootstrap resampling unit (all its versions move together).
C16. R_bin CI: the human and AI groups are resampled independently (the groups share no unit), percentile 2.5/97.5, 2,000 resamples, RNG seed 0 re-seeded at the start of each bin. "Paired" in §3 is read as "both groups resampled in the same replicate".
C17. AI-direction resampling unit = the AI row (each AI row is its own paragraph unless the dataset gives a document id, in which case the id).
C18. Share below 0.177 in the descriptive curve uses the version's score s(y) (not Δ), strictly below; the "half" bin is the smallest bin where the share is at least 0.5.
C19. Cosine is the primary magnitude and defines all bars; soft-n-gram results are descriptive and never rescue a bar.

## Nulls (§4)
C20. Identity null = mean over baseline paragraphs of |s_call1 − s_call2|; a bin's |Δ| CI "contains the noise floor" when its lower bound is at or below that value, and the bin is then read as no effect.
C21. Length-adjusted results are exploratory (§8) and never change a verdict.

## Bars (§5)
C22. B1 precedence: if one evaluated bin's R CI lies entirely outside [0.5, 2.0] B1 is `fail`, even if other bins are within (fail beats not proven; stricter reading). `Pass` needs every evaluated bin inside; otherwise `not proven`.
C23. B1 with zero evaluated bins is `not proven`.
C24. B2 passes if in at least two evaluated bins the R CI lies entirely above 2.0 (lower bound > 2.0, strict). It is `fail` only if no bin can reach it: at least all evaluated bins have a CI with lower bound at or below 2.0 and at least three bins are evaluated; otherwise `not proven`.
C25. B3 is read the same way, mirrored (upper bound < 0.5, strict; fail with at least three evaluated bins none of which qualifies and fewer than two could still).
C26. B2 and B3 both reaching their pass condition is reported as a protocol inconsistency, not as two passes.
C27. "Mixed" is reported when neither B2 nor B3 passes and B1 fails, with the per-bin table.
C28. B4: "CI of mean Δ_content − mean Δ_reword excludes 0" uses the same bootstrap (paragraph as unit); if the bin has fewer than 20 rows from 10 paragraphs of each type it is `not proven` for that bin and content and rewording are reported together.
C29. Production gate (a)–(c) are all required; (b) counts evaluated bins as defined in C11; (c) the identity null must be strictly below 0.01. If the gate cannot open that is stated and nothing is spent.
