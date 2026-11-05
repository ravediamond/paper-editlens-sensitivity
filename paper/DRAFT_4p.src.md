# What moves an open AI-edit detector on technical prose: edits to four robotics papers, tested one at a time

*Ravindu Somawansa, Shisso Robotics, Paris. Draft, not submitted. Every number is a placeholder filled from `numbers.json` by `make_paper.py`, and `numbers.json` names the file each value comes from. The drafts under test and the rewrites were produced with an AI assistant (Claude Code).*

## Abstract

Reading a score table suggests what to change in a text to lower its AI-edit score. We tested five such suggestions as controlled edits and three of them did not hold. We scored {{n_paras}} paragraphs from four of our robotics papers with Pangram's open EditLens model. Joining two sentences with a semicolon raised the score of {{semi_up}} % of the paragraphs, by {{semi}} on average. Appending a short verdict sentence lowered it by {{verdict_abs}}, although verdict words had looked like a cause of high scores. Shuffling the sentences, changing "we" to "I" and appending a sentence of the same paper did nothing. Rewriting paragraphs against the sentence-level scores lowered the four paper means from {{reg_b}}, {{jepa_b}}, {{rew_b}} and {{vla_b}} to {{reg_a}}, {{jepa_a}}, {{rew_a}} and {{vla_a}}. Pre-2022 human papers score {{hum1}} to {{hum3}}, so none of the four reached that range.

## 1 Introduction

Our four papers pass the slopscore and lmscan checks of the repository, and alphaXiv, which runs Pangram's detector, still flags them as AI-written. We wanted to know what in the text the detector reacts to, so that we could write the next paper without it.

We first read a table of {{n_sent}} sentences from the four papers and compared the score contribution of each sentence with its features. Semicolons, contrast framing, advice, verdict words and colon set-ups went with higher scores, and "we", short sentences and citations went with lower ones. From this table we wrote rule 78 of the writing rules in road-to-robotics. A feature that goes with a high score can travel with something else, such as a long list of numbers. This paper changes one feature at a time and scores the result.

EditLens [@thai2025editlens] takes a text and regresses how much an AI edited it, as a score between 0 and 1. Its authors trained it on pairs of a source text and an AI-edited version of it, from reviews, news, stories and web articles, edited with prompts such as "make it more descriptive" and "fix any mistakes". Our texts are experimental robotics papers, so we did not expect the same features to matter. The controlled edits below test that.

## 2 Setup

The scorer is `pangram/editlens_Llama-3.2-3B`, the open model, on a Jetson Orin NX at 25 W. The production detector that flagged the papers is a different and stronger model, and we did not run it. The model is licensed for non-commercial use and we used it on our own four papers only.

The texts are the rendered drafts of four papers: a register of re-tested robot-learning claims, a JEPA world model on a low-cost arm, reward models and a stopping rule, and chunking tricks for a VLA on an edge GPU. Citations are stripped and the model lower-cases its input. Paragraphs of at least 40 words are scored on their own, since shorter ones are noisy. There are {{n_paras}} of them, in {{n_sent}} sentences. As a human reference we scored three robot-learning papers from before November 2022. Their paper means are {{hum1}}, {{hum2}} and {{hum3}}.

An edit changes one thing in every paragraph that contains it, and we report the mean change in the paragraph score with a 95 % bootstrap interval over paragraphs. An edit that changes only case and spacing gives exactly {{null_edit}}, because the model normalizes both. We removed semicolons and colons from the texts before this test, so for these two we could only test adding them.

## 3 Results

### 3.1 Controlled edits

Table 1: Controlled edits on the original paragraphs. A positive change means the edited paragraph scores higher, which is worse for us.

| edit | paragraphs changed | change in score (95 % CI) |
|---|---|---|
| join sentence pairs with a semicolon | {{n_paras}} | {{semi}} ({{semi_lo}} to {{semi_hi}}) |
| append a generic closer, "The result holds on this rig." | {{n_paras}} | {{closer}} ({{closer_lo}} to {{closer_hi}}) |
| append a contrast closer, "a limit of the setting, not of the method" | {{n_paras}} | {{contrast}} ({{contrast_lo}} to {{contrast_hi}}) |
| append advice, "Check the simple baseline first." | {{n_paras}} | {{advice}} ({{advice_lo}} to {{advice_hi}}) |
| append a verdict, "The row fails." | {{n_paras}} | {{verdict}} ({{verdict_lo}} to {{verdict_hi}}) |
| append a sentence about the rig, "We ran this on the Jetson Orin NX." | {{n_paras}} | {{weran}} ({{weran_lo}} to {{weran_hi}}) |
| append a real sentence from another paragraph of the same paper | {{n_paras}} | {{realsent}} ({{realsent_lo}} to {{realsent_hi}}) |
| change "we" and "our" to "I" and "my" | {{we_to_i_n}} | {{we_to_i}} ({{we_to_i_lo}} to {{we_to_i_hi}}) |
| shuffle the sentences of a paragraph | {{n_paras}} | {{shuffle_a}} ({{shuffle_a_lo}} to {{shuffle_a_hi}}) |
| drop the parentheticals | {{parens_n}} | {{parens}} ({{parens_lo}} to {{parens_hi}}) |
| split at ", and" and ", but" | {{split_and_n}} | {{split_and}} ({{split_and_lo}} to {{split_and_hi}}) |
| replace every number with "many" | {{mask_num_n}} | {{mask_num}} ({{mask_num_lo}} to {{mask_num_hi}}) |
| keep only the first half of the sentences | {{n_paras}} | {{first_half}} ({{first_half_lo}} to {{first_half_hi}}) |

The semicolon and the two closers raise the score, and the verdict sentence lowers it. Advice, the sentence about the rig, a real sentence of the same paper and the pronoun change do nothing, so adding length or changing the pronoun does not move the score. Shuffling does nothing either. Dropping the parentheticals, splitting at "and" and "but", and masking numbers lower the score. Keeping half of a paragraph lowers it most.

### 3.2 What the earlier table got right

Table 2: The sentence-level correlations we first used as rules, against the controlled edit of the same feature.

| feature | correlation table | controlled edit |
|---|---|---|
| semicolons | {{c_semi}} | {{semi}}, holds |
| contrast framing | {{c_contrast}} | {{contrast}}, holds and is smaller |
| advice or imperatives | {{c_advice}} | {{advice}}, does not hold |
| verdict words | {{c_verdict}} | {{verdict}}, reversed |
| "we" or "our" doing something | {{c_we}} | {{we_to_i}}, does not hold |

Two of five features held. The verdict result is the one we did not expect. In the papers a verdict word sits in sentences that also carry a number, a bar and a citation, which may be what raised the score in the table. We did not test that. A verdict sentence appended on its own does not raise it.

### 3.3 The rewrite loop

We rewrote paragraphs from the highest-scoring sentences down. Each round scored a few candidate rewrites with the placeholders of the paper filled in, and kept the lowest one that preserved every number and claim. In the register paper one sentence moved to another paragraph and one that repeated another was dropped. There were {{n_cand}} candidates in {{n_rounds}} paragraph-rounds. {{n_lower}} of the candidates scored lower than the text they replaced, and the best candidate of a round improved the paragraph in {{share_impr}} % of the rounds, by {{mean_best}} on average.

Table 3: Word-weighted mean paragraph score before and after the rewrite.

| paper | paragraphs | mean before | mean after |
|---|---|---|---|
| register of re-tested claims | {{reg_p}} | {{reg_b}} | {{reg_a}} |
| JEPA world model | {{jepa_p}} | {{jepa_b}} | {{jepa_a}} |
| reward models and a stopping rule | {{rew_p}} | {{rew_b}} | {{rew_a}} |
| chunking tricks on an edge GPU | {{vla_p}} | {{vla_b}} | {{vla_a}} |

The largest single drops came from three changes, listed in Table 4. Merging sentences into longer ones with "so" or "which means" raised a limitations paragraph from {{merge_b}} to {{merge_a}} in the first variant, and the other two variants did the same. Paragraphs made of numbers, bars and verdicts stayed above the human range whatever we did.

Table 4: The three largest drops in one paragraph, by the change that caused them.

| change | paragraph | before | after |
|---|---|---|---|
| name the works in place of "papers propose several uses" | JEPA introduction | {{jepa_intro_b}} | {{jepa_intro_a}} |
| split one list sentence into plain statements | register, cold reruns | {{cold_b}} | {{cold_a}} |
| open with the AUROC example and give the class letter after it | register, classes B and C | {{classes_b}} | {{classes_a}} |

### 3.4 A lexicon of words

We also tried to turn the sentence scores into a list of words. A lexicon built on three papers predicts the sentence effects of the fourth with a correlation of {{lex_held}}, and the 95th percentile of shuffled labels is {{lex_null}}. Deleting single words in the {{wd_paras}} highest paragraphs ({{wd_n}} deletions) agrees in sign with the sentence source for {{lex_same}} of {{lex_words}} words. Only {{lex_listed}} words pass our strict test. Words that name a method for talking about itself (protocol, rule, committed, reports, CI) go with higher scores, and plain task words and units go with lower ones. The effect of one word is small, since the mean deletion changes a paragraph by {{wd_mean}} and the largest by {{wd_max}}. The list is a tie-breaker between synonyms.

## 4 Limitations

The model is the open 3B one, and the detector that flagged the papers is another. We did not run the production model, so none of these effects is shown to carry over to it. Running it on the four papers costs about {{pass_cost}} dollars for each full pass at the listed API rate, and we did not spend it.

We drafted the four papers with Claude Code, and Claude Code wrote the rewrites in this paper too. The author has not yet read the rewrites paragraph by paragraph. The open EditLens model scores a paragraph low when it sees little AI editing in it. We do not read the score as who wrote the paragraph.

Table 1 changes one feature per edit. A real rewrite changes several at once. We have not run the test that applies the rewrite moves of Section 3.3 one at a time to the same paragraphs. That test would show whether their effects add up. All {{n_paras}} paragraphs come from the four papers of one author, on one SO-101 arm and one Jetson Orin NX. The five appended sentences are our own examples, and other wording could behave differently.

## 5 Related work

EditLens [@thai2025editlens] introduces the continuous score and reports binary and ternary detection results, and we use its open 3B model. Its authors state that the model has a non-zero error rate and can cause harm when used to accuse someone. The AI Polish study [@saha2025polish], which EditLens evaluates on, shows that binary detectors flag lightly polished text as AI. Work on paraphrasers and humanizers [@krishna2023paraphrase; @cheng2025adversarial; @masrour2025damage] studies how they degrade the detection of AI text. We read only the descriptions of these in the EditLens paper and not the works themselves. We start from human-directed drafts of technical prose and ask which edits move an open model's score, and we report the edits that did nothing.

## 6 Conclusion

Of the five features we had read off a correlation table, a semicolon and a contrast closer raised the score, and the other three did not, so test a suspected feature as an edit before it becomes a writing rule. In our rewrites, paragraphs with named things and plain "we ran X on Y" sentences scored lower than paragraphs of procedure words, and result paragraphs stayed above the human range.

## References

- Thai, K., Emi, B., Masrour, E., Iyyer, M. EditLens: Quantifying the Extent of AI Editing in Text. arXiv:2510.03154, 2025.
- Saha, S., Feizi, S. Almost AI, Almost Human: The Challenge of Detecting AI-Polished Writing. arXiv:2502.15666, 2025.
- Krishna, K., Song, Y., Karpinska, M., Wieting, J., Iyyer, M. Paraphrasing Evades Detectors of AI-Generated Text, but Retrieval is an Effective Defense. arXiv:2303.13408, 2023.
- Cheng, Y., Sadasivan, V. S., Saberi, M., Saha, S., Feizi, S. Adversarial Paraphrasing: A Universal Attack for Humanizing AI-Generated Text. arXiv:2506.07001, 2025.
- Masrour, E., Emi, B., Spero, M. DAMAGE: Detecting Adversarially Modified AI-Generated Text. arXiv:2501.03437, 2025.
