# What moves an open AI-edit detector on technical prose: controlled edits, one feature at a time

*Ravindu Somawansa, Shisso Robotics, Paris. Draft, not submitted. Every number is a placeholder filled from `numbers.json` by `make_paper.py`, and `numbers.json` names the file each value comes from. The drafts under test and the rewrites were produced with an AI assistant (Claude Code).*

## Abstract

A correlation table of sentence scores suggests what to change in a text to lower its AI-edit score. We tested its five suggestions as controlled edits on 62 paragraphs of four of our robotics papers, scored with Pangram's open EditLens model, and three did not hold. Joining two sentences with a semicolon raised the score of 92 % of the paragraphs, by +0.047 on average, but an appended verdict sentence lowered it. Rewriting paragraphs against their sentence-level scores moved the four paper means from 0.211, 0.176, 0.202 and 0.233 to 0.153, 0.160, 0.189 and 0.207. In 39 human robot-learning papers from before November 2022 the paper means have a median of 0.071, and 4 of our four papers still score above all of them. Style features that go with low scores in the human papers did not lower the score of 5 of 7 paragraphs when we added them.

## 1 Introduction

Our four papers pass the slopscore and lmscan checks of the repository, and alphaXiv, which runs Pangram's detector, still flags them as AI-written. We wanted to know what in the text the detector reacts to, so that we could write the next paper without it.

We first read a table of 469 sentences from the four papers and compared the score contribution of each sentence with its features. Semicolons, contrast framing, advice, verdict words and colon set-ups went with higher scores, and "we", short sentences and citations went with lower ones. From this table we wrote rule 78 of the writing rules in road-to-robotics. A feature that goes with a high score can travel with something else, such as a long list of numbers. This paper changes one feature at a time and scores the result.

EditLens (Thai et al. 2025) takes a text and regresses how much an AI edited it, as a score between 0 and 1. Its authors trained it on pairs of a source text and an AI-edited version of it, from reviews, news, stories and web articles, edited with prompts such as "make it more descriptive" and "fix any mistakes". Our texts are experimental robotics papers, so we did not expect the same features to matter. The controlled edits below test that.

A score also needs a scale. We therefore scored 39 human robot-learning papers from before November 2022 in the same way, and we tried to write our paragraphs in the style that those papers suggest.

## 2 Setup

The scorer is `pangram/editlens_Llama-3.2-3B`, the open model, on a Jetson Orin NX at 25 W. The production detector that flagged the papers is a different and stronger model, and we did not run it. The model is licensed for non-commercial use and we used it on our own four papers only.

The texts are the rendered drafts of four papers: a register of re-tested robot-learning claims, a JEPA world model on a low-cost arm, reward models and a stopping rule, and chunking tricks for a VLA on an edge GPU. Citations are stripped and the model lower-cases its input. Paragraphs of at least 40 words are scored on their own, since shorter ones are noisy. There are 62 of them, in 469 sentences. As a human reference we took the first 40 results of an arXiv query for robot-learning papers submitted from 2018 to 2021 (the rule is in `repro/human-reference/PROTOCOL.md`) and read their PDFs with the same extractor we used on our own four built PDFs. 1 paper had too few scoreable paragraphs and was dropped. Reference lists and acknowledgements that the extractor had kept as prose (116 paragraphs, found after the first scoring because they were among the highest scores) were excluded, which leaves 39 papers and 1,365 paragraphs.

An edit changes one thing in every paragraph that contains it, and we report the mean change in the paragraph score with a 95 % bootstrap interval over paragraphs. An edit that changes only case and spacing gives exactly 0.000, because the model normalizes both. We removed semicolons and colons from the texts before this test, so for these two we could only test adding them.

## 3 Results

### 3.1 Controlled edits

Table 1: Controlled edits on the original paragraphs. A positive change means the edited paragraph scores higher, which is worse for us.

| edit | paragraphs changed | change in score (95 % CI) |
|---|---|---|
| join sentence pairs with a semicolon | 62 | +0.047 (+0.039 to +0.056) |
| append a generic closer, "The result holds on this rig." | 62 | +0.017 (+0.012 to +0.022) |
| append a contrast closer, "a limit of the setting, not of the method" | 62 | +0.011 (+0.006 to +0.017) |
| append advice, "Check the simple baseline first." | 62 | +0.001 (−0.004 to +0.005) |
| append a verdict, "The row fails." | 62 | −0.015 (−0.020 to −0.011) |
| append a sentence about the rig, "We ran this on the Jetson Orin NX." | 62 | −0.001 (−0.007 to +0.004) |
| append a real sentence from another paragraph of the same paper | 62 | +0.003 (−0.005 to +0.011) |
| change "we" and "our" to "I" and "my" | 52 | +0.001 (−0.004 to +0.006) |
| shuffle the sentences of a paragraph | 62 | +0.000 (−0.012 to +0.012) |
| drop the parentheticals | 27 | −0.018 (−0.033 to −0.005) |
| split at ", and" and ", but" | 28 | −0.014 (−0.020 to −0.007) |
| replace every number with "many" | 55 | −0.021 (−0.030 to −0.012) |
| keep only the first half of the sentences | 62 | −0.029 (−0.044 to −0.015) |

The semicolon and the two closers raise the score, and the verdict sentence lowers it. Advice, the sentence about the rig, a real sentence of the same paper and the pronoun change do nothing, so adding length or changing the pronoun does not move the score. Shuffling does nothing either. Dropping the parentheticals, splitting at "and" and "but", and masking numbers lower the score. Keeping half of a paragraph lowers it most.

### 3.2 What the earlier table got right

Table 2: The sentence-level correlations we first used as rules, against the controlled edit of the same feature.

| feature | correlation table | controlled edit |
|---|---|---|
| semicolons | +0.028 | +0.047, holds |
| contrast framing | +0.029 | +0.011, holds and is smaller |
| advice or imperatives | +0.021 | +0.001, does not hold |
| verdict words | +0.020 | −0.015, reversed |
| "we" or "our" doing something | −0.020 | +0.001, does not hold |

Two of five features held. The verdict result is the one we did not expect. In the papers a verdict word sits in sentences that also carry a number, a bar and a citation, which may be what raised the score in the table. We did not test that. A verdict sentence appended on its own does not raise it.

### 3.3 The rewrite loop

We rewrote paragraphs from the highest-scoring sentences down. Each round scored a few candidate rewrites with the placeholders of the paper filled in, and kept the lowest one that preserved every number and claim. In the register paper one sentence moved to another paragraph and one that repeated another was dropped. There were 90 candidates in 50 paragraph-rounds. 50 of the candidates scored lower than the text they replaced, and the best candidate of a round improved the paragraph in 64 % of the rounds, by 0.032 on average.

Table 3: Word-weighted mean paragraph score before and after the rewrite.

| paper | paragraphs | mean before | mean after |
|---|---|---|---|
| register of re-tested claims | 23 | 0.211 | 0.153 |
| JEPA world model | 22 | 0.176 | 0.160 |
| reward models and a stopping rule | 21 | 0.202 | 0.189 |
| chunking tricks on an edge GPU | 18 | 0.233 | 0.207 |

The largest single drops came from three changes, listed in Table 4. Merging sentences into longer ones with "so" or "which means" raised a limitations paragraph from 0.275 to 0.365 in the first variant, and the other two variants did the same. Paragraphs made of numbers, bars and verdicts stayed above the median of human results paragraphs (0.045) whatever we did.

Table 4: The three largest drops in one paragraph, by the change that caused them.

| change | paragraph | before | after |
|---|---|---|---|
| name the works in place of "papers propose several uses" | JEPA introduction | 0.315 | 0.164 |
| split one list sentence into plain statements | register, cold reruns | 0.253 | 0.139 |
| open with the AUROC example and give the class letter after it | register, classes B and C | 0.253 | 0.145 |

A rewrite changes several sentences at once, so we asked whether the changes add up. For the 26 paragraphs the loop changed, we split each rewrite into its sentence-level hunks and applied every hunk alone to the original paragraph (46 hunks, `repro/additivity`). 14 paragraphs have two or more hunks, and in them the hunk effects sum to −0.067 on average against −0.063 for the whole rewrite. The two agree across paragraphs with a correlation of 0.94 (Spearman 0.86), and the mean gap is +0.010 per paragraph. In every one of these paragraphs the hunk with the largest effect has the sign of the whole rewrite. Nearly all hunks are reworded sentences (45 of 46), so this shows that sentence-level changes add up, and it does not separate the named moves, such as naming the works or splitting a list.

### 3.4 A lexicon of words

We also tried to turn the sentence scores into a list of words. A lexicon built on three papers predicts the sentence effects of the fourth with a correlation of 0.116, and the 95th percentile of shuffled labels is 0.096. Deleting single words in the 20 highest paragraphs (2,042 deletions) agrees in sign with the sentence source for 48 of 80 words. Only 19 words pass our strict test. Words that name a method for talking about itself (protocol, rule, committed, reports, CI) go with higher scores, and plain task words and units go with lower ones. The effect of one word is small, since the mean deletion changes a paragraph by +0.013 and the largest by 0.157. The list is a tie-breaker between synonyms.

### 3.5 A human reference

Table 5 gives the paragraph scores of the 39 human papers by the type of section. The paper means run from 0.033 to 0.123 with a median of 0.071. The median paragraph scores 0.063, 15 % of the paragraphs score above 0.15, and 5 % score above 0.25. Results paragraphs have a median of 0.045, so a results paragraph at 0.15, the level where ours stopped, is high for a human one.

Table 5: Paragraph scores of the human reference papers by section type, read from the PDFs. Section types come from the headings and are rough.

| section type | paragraphs | median | 90th percentile |
|---|---|---|---|
| introduction | 167 | 0.053 | 0.177 |
| related work | 114 | 0.063 | 0.153 |
| method | 133 | 0.073 | 0.174 |
| results | 140 | 0.045 | 0.169 |
| conclusion | 82 | 0.043 | 0.116 |
| other or not recognised | 689 | 0.069 | 0.187 |

Read the same way, our four built PDFs have paper means of 0.182, 0.130, 0.145 and 0.138, and 56 % of their 50 scoreable paragraphs score above 0.15. All four lie above the human median, and 4 of the 4 lie above the highest human paper.

### 3.6 Writing in the style of the human papers

Our papers score above the human ones, so we measured style features of the human paragraphs and of ours (Table 6) and looked for the ones that go with a low score. The rank correlations are weak, at most 0.30 in absolute value. The largest gaps between our paragraphs and the human ones are the numeric tokens, the passive constructions, and the contrast and connective words. Our paragraphs have 8.56 numeric tokens per 100 words where the human paragraphs below 0.05 have 4.29.

Table 6: Style features of the human paragraphs by score, and of ours, read from the PDFs. Counts are per 100 words except the last row. Low is the 542 human paragraphs below 0.05 and high the 211 above 0.15.

| feature | rank correlation with score | low | high | ours |
|---|---|---|---|---|
| numeric tokens | −0.12 | 4.29 | 3.66 | 8.56 |
| passive constructions | −0.12 | 1.12 | 0.89 | 0.40 |
| contrast words | −0.10 | 0.36 | 0.35 | 0.08 |
| connective words | −0.13 | 0.29 | 0.12 | 0.21 |
| commas | +0.09 | 5.16 | 5.99 | 4.35 |
| words per paragraph | −0.28 | 199 | 125 | 137 |

We rewrote 7 paragraphs of two of our papers in that direction, in our own words and with every number kept, joining clauses with contrast and connective words and using the passive for procedures. Of the 8 candidates, 5 scored higher than the paragraph they replaced and 2 lower, and the mean change was +0.020. No candidate lowered 5 of the 7 paragraphs. The related-work paragraph of the register paper rose from 0.194 to 0.280. The features that go with low scores across human paragraphs did not lower ours when we added them, which is the same gap between a correlation and an edit as in Section 3.2.

### 3.7 What the model reacts to

The first battery of edits used the highest and lowest paragraphs as hosts and misled us, because at the ends of the score any edit seems to move a paragraph toward the middle. The second battery uses 100 random human paragraphs and our 62, with a control that appends or prepends a real sentence from another paragraph. The control moves a human paragraph by −0.025 when appended and −0.014 when prepended, and ours by +0.002 and +0.005.

Table 7: Single edits on hosts not chosen by their score. Mean change in the paragraph score with a 95 % bootstrap CI. The base mean is 0.201 for ours and 0.080 for the human paragraphs.

| edit | ours | human, random |
|---|---|---|
| language-model-style sentence appended | +0.038 (+0.028 to +0.049) | +0.013 (−0.000 to +0.024) |
| language-model-style sentence prepended | +0.024 (+0.014 to +0.035) | +0.034 (+0.027 to +0.042) |
| generic opener on an important and challenging problem | +0.015 (+0.009 to +0.022) | +0.009 (+0.006 to +0.013) |
| generic sentence on importance appended | −0.004 (−0.010 to +0.003) | −0.024 (−0.035 to −0.015) |
| neutral figure pointer appended | −0.041 (−0.047 to −0.034) | −0.037 (−0.049 to −0.027) |
| neutral figure pointer prepended | −0.059 (−0.070 to −0.049) | −0.023 (−0.028 to −0.018) |
| long specific technical paragraph appended | −0.167 (−0.185 to −0.150) | −0.062 (−0.076 to −0.050) |
| long specific technical paragraph prepended | −0.138 (−0.153 to −0.122) | −0.042 (−0.051 to −0.034) |
| paragraph of the same register appended | −0.006 (−0.022 to +0.009) | −0.026 (−0.041 to −0.012) |
| names replaced by "the method" | +0.003 (−0.005 to +0.011) | −0.006 (−0.009 to −0.003) |
| digits dropped | −0.042 (−0.057 to −0.030) | +0.003 (−0.003 to +0.010) |
| evaluative words deleted | +0.000 (+0.000 to +0.000) | −0.005 (−0.007 to −0.003) |
| control: real sentence appended | +0.002 (−0.005 to +0.009) | −0.025 (−0.037 to −0.015) |
| control: real sentence prepended | +0.005 (−0.005 to +0.014) | −0.014 (−0.020 to −0.010) |

A sentence in the style of a language model raises the score in either position, by +0.038 appended and +0.024 prepended to ours. A generic opener about an important and challenging problem raises ours by +0.015. Digits are the clearest feature of our own text. Dropping them moves our paragraphs by −0.042, replacing names with "the method" does nothing (+0.003), and the human paragraphs are not sensitive to digits (+0.003). A neutral figure pointer moves ours by −0.041. A long, specific technical paragraph from a human paper moves ours most, by −0.167 appended and −0.138 prepended, and a paragraph of the same register does not (−0.006). Single evaluative words hardly matter. Deleting them from human paragraphs moves the score by −0.005, and an appended sentence on importance by −0.024.

The gradient of the score with respect to the input shows no single trigger word. In 9 example paragraphs the top tenth of the words holds 34 % to 70 % of the positive attribution. The score looks like a measure of how much of a paragraph is generic exposition against specific technical detail, since a run of specifics dilutes it and generic framing or language-model phrasing adds to it. We tested this reading only with these edits.

## 4 Limitations

The model is the open 3B one, and the detector that flagged the papers is another. We did not run the production model, so none of these effects is shown to carry over to it. Running it on the four papers costs about 3.2 dollars for each full pass at the listed API rate, and we did not spend it.

We drafted the four papers with Claude Code, and Claude Code wrote the rewrites in this paper too. The author has not yet read the rewrites paragraph by paragraph. The open EditLens model scores a paragraph low when it sees little AI editing in it. We do not read the score as who wrote the paragraph.

Table 1 changes one feature per edit. A real rewrite changes several at once. We applied the sentence-level hunks of the rewrites one at a time (Section 3.3), but nearly all of them are reworded sentences, so we did not separate the named moves. All 62 paragraphs come from the four papers of one author, on one SO-101 arm and one Jetson Orin NX. The five appended sentences are our own examples, and other wording could behave differently. The human reference is the first 40 results of one query, not a sample of the field, and its section types are rough because many headings were not recognised. Our own four PDFs give only 50 scoreable paragraphs, so their section types are not compared. The trigger edits use one language-model-style sentence and one figure pointer that we wrote, so they show that these sentences move the score and not that every such sentence does. The style trial is 7 paragraphs from two papers, one round, with features we chose, so it shows that these edits did not help in that sample and does not rule them out.

## 5 Related work

EditLens (Thai et al. 2025) introduces the continuous score and reports binary and ternary detection results, and we use its open 3B model. Its authors state that the model has a non-zero error rate and can cause harm when used to accuse someone. The AI Polish study (Saha and Feizi 2025), which EditLens evaluates on, shows that binary detectors flag lightly polished text as AI. Work on paraphrasers and humanizers (Krishna et al. 2023; Cheng et al. 2025; Masrour et al. 2025) studies how they degrade the detection of AI text. We read only the descriptions of these in the EditLens paper and not the works themselves. We start from human-directed drafts of technical prose and ask which edits move an open model's score, and we report the edits that did nothing.

## 6 Conclusion

> **Conclusion.** Of the five features we had read off a correlation table, a semicolon and a contrast closer raised the score and the other three did not. A suspected feature should therefore be tested as an edit before it becomes a writing rule. Our four papers score above the human median, and our result paragraphs stayed above the median of human results paragraphs. Adding the style features of the human papers did not lower our scores. In our rewrites, paragraphs with named things and plain "we ran X on Y" sentences scored lower than paragraphs of procedure words. Adding long specific technical text lowered the score most, and generic framing and language-model phrasing raised it. We have not tested whether the rest of the gap is content that only the author can add, such as the reasons for a decision.

## References

- Thai, K., Emi, B., Masrour, E., Iyyer, M. EditLens: Quantifying the Extent of AI Editing in Text. arXiv:2510.03154, 2025.
- Saha, S., Feizi, S. Almost AI, Almost Human: The Challenge of Detecting AI-Polished Writing. arXiv:2502.15666, 2025.
- Krishna, K., Song, Y., Karpinska, M., Wieting, J., Iyyer, M. Paraphrasing Evades Detectors of AI-Generated Text, but Retrieval is an Effective Defense. arXiv:2303.13408, 2023.
- Cheng, Y., Sadasivan, V. S., Saberi, M., Saha, S., Feizi, S. Adversarial Paraphrasing: A Universal Attack for Humanizing AI-Generated Text. arXiv:2506.07001, 2025.
- Masrour, E., Emi, B., Spero, M. DAMAGE: Detecting Adversarially Modified AI-Generated Text. arXiv:2501.03437, 2025.
