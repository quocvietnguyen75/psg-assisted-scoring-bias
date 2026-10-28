# How to settle the eight coding disagreements (D1 adjudication guide, 28 October 2026)

## Why you are doing this

Table S9 of the paper says, for 22 FDA-cleared PSG scoring programs, how each was validated: what the human
reference was, whether the reference scorers were blinded to the device's output, and whether they worked from
automatic pre-scoring. An AI coded this first and two co-authors checked it while seeing the AI's codes. Reviewers said
that is the assisted kind of check our own paper criticizes, so Tài and Hoài re-coded all 22 summaries without seeing
any code. In eight fields, spread over five summaries, one or both of them chose a different code from ours.

Our plan (amendment 005, part D1) says how such a disagreement is settled: a third author, who did not code, reads the
source and decides. That is you. Decide from the text only. Whatever you decide, I update the counts and the sentences;
nothing in the paper depends on the decisions going one way.

## What you need

- The five summaries, as PDF files cached in the workspace under `outputs/psg_assist_bias_validation_practice/pdf/`:
  `K120450.pdf`, `K153412.pdf`, `K221179.pdf`, `K223539.pdf`, `K142825.pdf`. "Page" below means the page counter of
  the PDF viewer, not the number printed on the page.
- This guide and about 30 minutes. Nothing else: you do not need the coders' sheets or our coding file.

## The one rule

Code only what the summary says. Each of the stricter codes (independent, daily practice, blinded, pre-scoring)
requires a sentence that says so, or an equivalent phrase. If that sentence is not there, choose the "not stated",
"not described" or "not said" code. Do not fill the gap with what sleep laboratories usually do, and do not read a
procedure into a results table. The point of our paper is that these summaries do not say.

## The three questions and their possible answers

These are the definitions the coders used, copied from the coding sheet.

**Question A. Reference: how was it produced?**

| Code | Definition |
|---|---|
| Independent experts | Experts scored the recordings for this validation, and the summary describes them as scoring independently (for example "independent", "separately", "blinded to each other"). |
| Consensus, independence not stated | The summary names a consensus or majority of several scorers (for example 2 of 3) but does not say that they scored independently. |
| Routine clinical scoring | The reference was the scoring made earlier in routine clinical care, not scoring done for the study. |
| Daily-practice panel | A panel scored for the study, but in their usual clinical way ("as done in their daily practice" or similar). |
| Another algorithm's output | The comparator was another algorithm's unedited output, not human scoring. |
| Not described | The summary reports performance against a reference without saying how it was produced. |

**Question B. Blinding to the device's output**

| Code | Definition |
|---|---|
| Explicit | The summary states that the reference scorers did not see, or had no access to, the device's output. |
| Implied by design | The summary says that the device was run separately from, or after, the human scoring, so the scorers could not have seen its output, without saying so in so many words. |
| Stated, object unspecified | The summary calls the scoring blind or blinded without saying to what. |
| Not stated | The summary says nothing about blinding, and nothing from which it follows. |
| Not applicable | The reference was an algorithm, so blinding of human scorers does not arise. |

**Question C. Did the reference scorers work from automatic pre-scoring (any software)?**

| Code | Definition |
|---|---|
| Not said | The summary does not say whether the reference scorers began from automatic scoring by any software, including their own laboratory's software. |
| Says they did | The summary says the reference scorers reviewed or edited automatic scoring. |
| Says they did not (any software) | The summary says the reference scorers scored without automatic pre-scoring of any kind. |
| Says they did not (only this device's output) | The summary says only that the scorers did not see or start from this device's output; other software is not mentioned. |
| Not applicable | There were no human reference scorers (for example, an algorithm reference). |

## The recipe for one item

1. Open the PDF at the page given and read the clinical or performance testing section once through.
2. Find the sentences quoted under "Find". They are the only sentences in the summary about the reference.
3. Answer the yes-or-no questions under "Ask". Use Ctrl+F with the listed words so that you do not miss a sentence
   elsewhere in the summary.
4. Take the code that your answers point to under "Decide". If you find a sentence that supports a third code, take
   that code and copy the sentence.
5. Write the decision on the item's answer line. Where you change our code, add the page and the words you relied on.

"Blind" after a coder's name means that coder had not checked that summary in the first round, so they had never
seen a code for it; "seen" means they had.

## Worked example: item 1, on the page you opened

K120450, page 5, Question A. The first sentence says the staging algorithms were validated "by comparison to sleep
staging made by manual observation by three raters who were either sleep technicians or physicians". The results
table is labelled "Epochs assigned by Expert Scoring" and has a "No-Consensus" row: the three raters' labels were
combined into one label per epoch, and epochs on which they did not agree were set aside. So the reference was a
consensus of several raters.

Now the two questions. Does any sentence say the raters scored in their daily or routine practice? Ctrl+F for
"daily", "routine", "practice": the only hit is "clinical testing", which names the validation study, not the way the
raters scored. Does any sentence say the raters scored independently, separately or blind to each other? Ctrl+F for
"independ", "separate", "blind": nothing. Both answers are no, so the code is "Consensus, independence not stated",
the code we have. The MICHELE table lower on the page reports the predicate device's own study and says nothing about
these raters.

## The eight items

### Item 1. K120450, Sleep Profiler (2012): Question A, reference

- **Open:** `K120450.pdf`, page 5.
- **Our code:** Consensus, independence not stated. Tài (seen) chose the same.
- **Hoài (blind):** Daily-practice panel, quoting the same sentence.
- **Find:** "comparison to sleep staging made by manual observation by three raters who were either sleep
  technicians or physicians"; the table's "No-Consensus" row.
- **Ask:** Does any sentence say the raters scored as in their daily or routine practice (Ctrl+F: daily, routine,
  practice)? Does any sentence say they scored independently (Ctrl+F: independ, separate, blind)?
- **Decide:** daily practice stated: Daily-practice panel. Independence stated: Independent experts. Neither:
  Consensus, independence not stated.
- **Answer:** 1: keep

### Item 2. K120450, Sleep Profiler (2012): Question B, blinding

- **Open:** `K120450.pdf`, page 5.
- **Our code:** Not stated. Tài (seen) chose the same.
- **Hoài (blind):** Implied by design, quoting "The positive and negative percent agreement obtained during clinical
  validation of the Sleep Profiler are similar to that obtained by the predicate device, MICHELE (K112102), which was
  validated using a different data set."
- **Find:** that sentence. It compares the results with the predicate's study; ask whether it says anything about
  when these raters scored relative to the device.
- **Ask:** Does any sentence say the raters did not see or had no access to the device's output (Ctrl+F: blind,
  access)? Does any sentence describe the order of events, such as the device run after the scoring, or the
  recordings scored before the study (Ctrl+F: prior, before, after, subsequent, previous, archived, retrospective)?
- **Decide:** no access stated: Explicit. Order described: Implied by design. Neither: Not stated.
- **Answer:** 2: keep

### Item 3. K153412, Sleep Profiler (2016): Question A, reference

- **Open:** `K153412.pdf`, pages 13 to 15.
- **Our code:** Consensus, independence not stated. Tài (seen) chose the same.
- **Hoài (blind):** Another algorithm's output, quoting "The Sleep Profiler software accuracy was clinically
  validated with signals acquired with the X8 System concurrent to polysomnography (PSG)", with the comment that two
  different programs were used.
- **Find:** page 13: "The results compared auto-detected staging and sleep disordered breathing (i.e., apnea-hypopnea
  index) to PSG results obtained by one rater per study." Page 14: "The results for the weighted majority agreement
  of three raters are presented in the cross-tabulation below". Page 15: "Differences between the two studies are
  the result of inter-rater variability in the application of the American Academy of Sleep Medicine scoring
  rules".
- **Ask:** Was the comparator produced by people (Ctrl+F: rater, technologist, physician, scorer, manual) or by a
  program with no human scoring? On these pages, is the X8 System the recording equipment or a scoring program? If
  the comparator was human scoring: does any sentence say the raters scored independently (Ctrl+F: independ,
  separate, blind)?
- **Decide:** no human scoring: Another algorithm's output. Human scoring, independence stated: Independent experts.
  Human scoring by a majority of raters, independence not stated: Consensus, independence not stated.
- **Answer:** 3: keep

### Item 4. K153412, Sleep Profiler (2016): Question B, blinding

- **Open:** `K153412.pdf`, page 13.
- **Our code:** Not stated. Tài (seen) chose the same.
- **Hoài (blind):** Implied by design, quoting "The results compared auto-detected staging and sleep disordered
  breathing (i.e., apnea-hypopnea index) to PSG results obtained by one rater per study."
- **Find:** that sentence and "signals acquired with the X8 System concurrent to polysomnography". "Concurrent"
  describes the recording of the signals at the same time as the PSG; ask whether any sentence says when the
  automatic staging was produced or whether the raters could see it.
- **Ask:** the same two questions as in item 2.
- **Decide:** no access stated: Explicit. Order described: Implied by design. Neither: Not stated.
- **Answer:** 4: ____

### Item 5. K153412, Sleep Profiler (2016): Question C, pre-scoring

- **Open:** `K153412.pdf`, pages 13 to 15.
- **Our code:** Not said. Tài (seen) chose the same.
- **Hoài (blind):** Not applicable, which follows from their item 3 (no human reference).
- **Ask:** This item follows item 3. If you decided in item 3 that there was no human reference, the code is Not
  applicable. Otherwise: does any sentence say the raters reviewed, edited or started from automatic scoring by any
  software (Ctrl+F: automatic, auto, software, algorithm, edit, review, pre-scor)?
- **Decide:** no human reference: Not applicable. Pre-scoring stated: Says they did. Neither: Not said.
- **Answer:** 5: keep

### Item 6. K221179, SomnoMetry (2022): Question A, reference. Both coders disagree with us

- **Open:** `K221179.pdf`, pages 7, 8 and 10.
- **Our code:** Routine clinical scoring. We read the archived clinical files as carrying the clinics' own earlier
  scoring. Hoài, who checked this summary in the first round, agreed then but noted that the text does not say when
  or by whom the reference was scored.
- **Tài (blind) and Hoài (seen):** Not described, quoting "AASM gold standard of manually scored PSG data". Tài's
  comment: how the reference scoring was produced, scorer independence, consensus, blinding and pre-scoring are not
  described.
- **Find:** page 7: "Study that utilized retrospective clinical data to demonstrate automatic scoring sleep study
  results." Page 8: "The clinical evaluation included a total of 201 polysomnography (PSG) files obtained from 2 AASM
  accredited Sleep Testing Facilities in California as the ground truths to validate the SomnoMetry AI/ML
  algorithms. An archived collection of retrospective diagnostic clinical PSG subject data was obtained from the 2
  AASM Accredited Sleep Testing Facilities and were verified to meet the specified disease spectrum, medical
  condition, medication, and demographic requirements." and "the performance of SomnoMetry is non-inferior compared
  to AASM gold standard of manually scored PSG data." Page 10: "In the retrospective diagnostic clinical study, the
  final study results and statistical analysis were reported for each endpoint."
- **Ask:** Does any sentence say who scored the reference, when, or how (Ctrl+F: scored, scorer, technologist,
  physician, annotat, manual)? If not: do you read "archived collection of retrospective diagnostic clinical PSG
  subject data ... as the ground truths", together with "manually scored PSG data", as a statement that the scores
  came with the clinics' files, made earlier in clinical care? Or do these words describe the recordings only and
  leave the scoring unexplained?
- **Decide:** scoring for the study described: the matching code (independent, consensus or daily practice). The
  scores came with the clinical files: Routine clinical scoring. Only the recordings are described: Not described.
- **Answer:** 6: not described

### Item 7. K223539, Dreem 3S (2023): Question A, reference

- **Open:** `K223539.pdf`, pages 8 and 9.
- **Our code:** Consensus, independence not stated. Tài (blind) chose the same.
- **Hoài (seen):** Independent experts, quoting "Confusion matrix comparing Dreem 3S and consensus of expert-scored
  PSG for all sleep epochs is summarized as percentages in the table below."
- **Find:** page 8: "comparing the performance of the Dreem device with expert-scored sleep stages from a cleared
  device". Page 9: the quoted sentence and the table header "Consensus from manual staging". The sentence "96.6%
  epochs per night of recording were determined to be acceptable for manual scoring and sleep staging by at least two
  out of three" is about EEG signal quality, not about how the reference was scored.
- **Ask:** Does any sentence describe the experts as scoring independently, separately or blinded to each other
  (Ctrl+F: independ, separate, blind)?
- **Decide:** yes: Independent experts. No: Consensus, independence not stated.
- **Answer:** 7: keep

### Item 8. K142825, Zmachine (2015): Question C, pre-scoring

- **Open:** `K142825.pdf`, page 7, and read the clinical testing section to its end.
- **Our code:** Not said. Tài (seen) chose the same.
- **Hoài (blind):** Says they did, quoting "Using the Rechtschaffen and Kales (R&K) visual sleep staging guidelines."
- **Find:** "The standard PSG channels were scored independently by two to four certified polysomnographic
  technologists, using the Rechtschaffen and Kales (R&K) visual sleep staging guidelines. The individual score files
  were then combined, on a 30-second epoch basis, using a majority voting rule, to generate a single score file per
  subject ('Human Scores')." The R&K guidelines are the 1968 manual scoring rules, a rulebook, not software.
- **Ask:** Does any sentence say the technologists reviewed, edited or started from automatic scoring by any software
  (Ctrl+F: automatic, auto, software, algorithm, computer, edit, review, pre-scor)?
- **Decide:** yes: Says they did. No: Not said.
- **Answer:** 8: keep

## Sending the answers

One line in the chat is enough, "keep" meaning our code:

```
1 keep, 2 keep, 3 keep, 4 keep, 5 keep, 6 not described, 7 keep, 8 keep
```

That line is an example of the format, not a suggestion. Where you change a code, add the page and the words you
relied on, for example "6 not described (p. 8: no sentence names a scorer or a scoring date)". I record your line
and the date in the D1 record as the adjudication, change the counts, tables and sentences that follow from it, fill
the four red placeholders about the blind coding, run the tests, rebuild the package and show you the new sentences
to approve.
