# D1 blind second coding of the FDA summaries (26 October 2026)

Amendment 005, part D1: co-authors who had not seen the AI's codes or the checked codes for the summaries they code
re-code three fields of the 22 summaries with performance data (reference type, blinding to the device's output,
automatic pre-scoring), from the definitions in the coding sheet. Reported: raw agreement and Cohen's kappa per field
against the reconciled coding (`DEVICES.csv`), every disagreement, resolved by a third author reading the source,
and any resulting change to the manuscript's counts.

Status on 28 October: adjudicated. The corresponding author (Q.V.N.), who did not code, read the source pages with the
[step-by-step guide](D1_ADJUDICATION_GUIDE_2026-10-28.md) and wrote a decision on each item's answer line (chat message
of 28 October: "Finished the verification. I filled in the .md file. I agree."). The decisions are recorded under each
item below and applied: one code changed (`DEVICES.csv`, K221179); the generated values, Tables S9, S17 and S18, the
tests and the manuscript follow (see "Effect on the manuscript" below). Both coders were final on 26 October (coder 2's
exposure answer was clarified in chat at 11:37, below).

## Files received

Downloaded by the user from the team chat into the workspace root. Hashes are SHA-256 of the files as received. "Saved" is
the workbook's own last-modified property (UTC).

| As received | Size | SHA-256 | Saved by, at | Stored here as |
|---|---|---|---|---|
| `BLIND_FDA_CODING_2026-10-12.xlsx` (P.T.D., first return) | 20,374 B | `5a45a66c…49add2c` | Duong Phuc Tai, 2026-10-21 16:04 | not stored; differs from the corrected file in one cell |
| `BLIND_FDA_CODING_2026-10-12taiduongfix.xlsx` (P.T.D., corrected) | 20,375 B | `235eb66c…c56e7ef9` | Duong Phuc Tai, 2026-10-24 04:31 | `BLIND_FDA_CODING_PTD_2026-10-24.xlsx` |
| `BLIND_FDA_CODING_ANDH.xlsx` (D.H.A.N.) | 20,850 B | `965ea1e5…2eb34defe6f4` | Nguyen Duc Hoai Anh, 2026-10-25 16:24 | `BLIND_FDA_CODING_ANDH_2026-10-26.xlsx` |

Full hashes, in the table's order: `5a45a66cf1fad48315aff2d0b7dde447b0165ef592190fbe73b0b703c49add2c`,
`235eb66cae963a15215f4e5b9b0f9eb0cf2edff20d79f0ca35a6da84c56e7ef9`,
`965ea1e59a972301aa3c5154a7eb5dc31cb9e53cf7a6d11069a72eb34defe6f4`.

P.T.D.'s two files differ only in cell `Code!K7`, the blinding quote for K162627: "scoring-blind" in the first
return, "scoring-bind" in the corrected one. The printed summary reads "scoring-bind" (a typo in the FDA document,
confirmed on a rendering of PDF page 5), so the corrected quote is verbatim. P.T.D. made the correction after we
flagged the one quote that did not match the PDF text.

The workbook properties carry both coders' full names and university ID-like numbers. They stay in the private
repository; the curated public snapshot must clear these properties or leave the sheets out.

## Coders and prior exposure

Each summary had been checked in the first round (October 2026, `FDA_CODING_CHECK_COMPLETED.xlsx`,
`FDA_CODING_RECONCILIATION.md`) by one of the two coders, who then saw the AI's codes for those summaries:
P.T.D. rows 1-12 of the first-round sheet (K120450 to K192469; the reconciliation note dates this 8 October, the
sheet's own date cells read 2026-10-08 for row 1 and 2026-08-10 for rows 2-12, and P.T.D. recalled 11 October in
chat), D.H.A.N. rows 13-25 (K202142 to K253390). In the blind sheet, rows 1-10 are the ten of P.T.D.'s summaries
with performance data (K120450, K142825, K153412, K153353, K162140, K162627, K163617, K173366, K182227, K192469) and
rows 11-22 are the twelve of D.H.A.N.'s (K202142, K210034, K221179, K223922, K223539, K233438, K241960, K250058,
K252330, K250851, K253668, K253390).

- **Coder 1, P.T.D.** Coder tab: initials DPT, started 2026-10-20, "seen earlier coding: No", no K numbers. The "No"
  is superseded by P.T.D.'s answer in chat on 24 October: they had checked K120450 to K192469 in the first round, and
  they coded this sheet by hand without an AI assistant. Rows 1-10 are therefore counted as previously seen and rows
  11-22 as blind.
- **Coder 2, D.H.A.N.** Coder tab: initials ANDH, started 2026-10-26, "seen earlier coding: No", K numbers: "all".
  Asked about the contradiction on 26 October, D.H.A.N. answered in chat (11:37) that they had read the K-number cell
  as asking how many summaries they had checked and wrote "all" because they re-coded all of them; that before and
  during coding they opened none of Table S9 of the package's supplement, the first-round sheet or another coder's
  file; and that they coded by hand. The "No" does not cover the first round itself: D.H.A.N. had checked rows 13-25
  of the first-round sheet against the AI's codes, so rows 11-22 of the blind sheet count as previously seen and rows
  1-10 as blind, as in the tables below. D.H.A.N. also held the 19 October Overleaf package, whose `supplement.pdf`
  contains Table S9, and disclosed for D2 that the Codex assistant had seen some result tables; their answer covers
  the table. The file was saved on 25 October 16:24 UTC; the stated start date of 26 October is read as the date it
  was sent.

Both coders were told not to send their file until every coder had finished. P.T.D.'s file reached the user on
21 October, before D.H.A.N. had finished; D.H.A.N. states that they opened no other coder's file.

## Agreement with the reconciled coding

Unweighted Cohen's kappa over the category sets of the coding sheet (6, 5 and 5 categories). Computed by
a one-off session script (not kept; the manuscript module now reproduces the comparison from
`D1_BLIND_CODES_2026-10-26.csv`, see below), mapping the sheet's labels to the `DEVICES.csv` codes.

| Field | Coder | All 22 | Blind rows | Previously seen rows |
|---|---|---|---|---|
| Reference type | P.T.D. | 21/22, kappa 0.937 | 11/12, kappa 0.892 (rows 11-22) | 10/10, kappa 1.000 (rows 1-10) |
| Reference type | D.H.A.N. | 18/22, kappa 0.747 | 8/10, kappa 0.672 (rows 1-10) | 10/12, kappa 0.780 (rows 11-22) |
| Blinding | P.T.D. | 22/22, kappa 1.000 | 12/12, kappa 1.000 | 10/10, kappa 1.000 |
| Blinding | D.H.A.N. | 20/22, kappa 0.853 | 8/10, kappa 0.643 | 12/12, kappa 1.000 |
| Pre-scoring | P.T.D. | 22/22, kappa 1.000 | 12/12, kappa 1.000 | 10/10, kappa 1.000 |
| Pre-scoring | D.H.A.N. | 20/22, kappa 0.636 | 8/10, kappa 0.000 | 12/12, kappa 1.000 |

Kappa is unstable where the reconciled column is nearly constant: the pre-scoring field is "not said" in 20 of 22
summaries, so 20/22 agreement gives kappa 0.636, and on rows 1-10, where every reconciled value is "not said", any
agreement short of 10/10 gives kappa 0 exactly. Raw agreement is the informative number for that field.

Between the two coders (all 22 rows): reference type 19/22, kappa 0.810; blinding 20/22, kappa 0.853; pre-scoring
20/22, kappa 0.636. Taking, for each summary, the code of the coder who was blind for it gives 19/22, 20/22 and 20/22
against the reconciled coding; this mixes two coders into one series and is not the amendment's measure.

The first round's field-level agreement (89 of 100 fields agreed, 5 partly, 6 disagreed; four corrections) is
already reported in the Supplementary Methods.

## Disagreements: adjudication packet

Eight fields in five summaries. For each: the reconciled code with its recorded quote, each coder's code with their
quote, the source passage, and the definitions of the two categories from the coding sheet. Page numbers are PDF
pages of the cached summaries in `outputs/psg_assist_bias_validation_practice/pdf/`. "Effect" is what would change
if the coder's code were upheld (keys of `generated/values.tex`; current values: routine 4, consensus 4, notdesc 2,
daily 1, indep 10, algo 1, unclear 7, blind-none 13, blind-implied 5, prescoring-reported 0).
Decisions are the adjudicator's to record below each item.

### 1. K120450, Sleep Profiler (2012): reference type

- Reconciled: **Consensus, independence not stated**. Quote: "comparison to sleep staging made by manual observation
  by three raters who were either sleep technicians or physicians"; note: the results table has a No-Consensus row;
  how the consensus was formed and whether the raters scored independently are not described. P.T.D. (seen): same.
- D.H.A.N. (blind): **Daily-practice panel**, quoting the same sentence (p. 5), no comment.
- Source, p. 5: "The Sleep Profiler software has been the subject of clinical testing which validates the sleep
  staging algorithms by comparison to sleep staging made by manual observation by three raters who were either sleep
  technicians or physicians. There were 44 subjects." The table's row labels include "Expert Scoring" and
  "No-Consensus". No other sentence in the summary describes the raters.
- Definitions: Consensus, independence not stated: "names a consensus or majority of several scorers but does not say
  that they scored independently". Daily-practice panel: "A panel scored for the study, but in their usual clinical
  way ('as done in their daily practice' or similar)".
- Effect: consensus 4 to 3, daily 1 to 2, unclear 7 to 8; Table S9 row; the Results sentence on reference types.
- Decision: **keep** (Q.V.N., 28 October 2026; guide answer line "1: keep").

### 2. K120450, Sleep Profiler (2012): blinding

- Reconciled: **Not stated**. P.T.D. (seen): same.
- D.H.A.N. (blind): **Implied by design**, quote (p. 5): "The positive and negative percent agreement obtained during
  clinical validation of the Sleep Profiler are similar to that obtained by the predicate device, MICHELE (K112102),
  which was validated using a different data set."
- Source: the quoted sentence compares results with the predicate's validation. The summary does not say when the
  device was run relative to the manual scoring.
- Definitions: Implied by design: "the device was run separately from, or after, the human scoring, so the scorers
  could not have seen its output, without saying so in so many words". Not stated: "says nothing about blinding, and
  nothing from which it follows".
- Effect: blind-none 13 to 12, blind-implied 5 to 6; Table S9 row; the Results sentence on blinding.
- Decision: **keep** (Q.V.N., 28 October 2026; guide answer line "2: keep").

### 3. K153412, Sleep Profiler (2016): reference type

- Reconciled: **Consensus, independence not stated**. Quote (p. 14): "the weighted majority agreement of three
  raters"; note: independence of the raters not described. P.T.D. (seen): same.
- D.H.A.N. (blind): **Another algorithm's output**, quote (p. 13): "The Sleep Profiler software accuracy was
  clinically validated with signals acquired with the X8 System concurrent to polysomnography (PSG)"; comment: "Since
  using a different software to validation and evaluation, so the architecture of 2 softwares make they can not
  affect each others".
- Source, p. 13: "The results compared auto-detected staging and sleep disordered breathing (i.e., apnea-hypopnea
  index) to PSG results obtained by one rater per study." P. 14: "The results for the weighted majority agreement of
  three raters are presented in the cross-tabulation below" (the staging cross-tabulation, 31,361 epochs). P. 15:
  "Differences between the two studies are the result of inter-rater variability in the application of the American
  Academy of Sleep Medicine scoring rules".
- Definitions: Another algorithm's output: "The comparator was another algorithm's unedited output, not human
  scoring". Consensus, independence not stated: as above.
- Effect: consensus 4 to 3, algo 1 to 2; Table S9 row; the Results sentence on reference types.
- Decision: **keep** (Q.V.N., 28 October 2026; guide answer line "3: keep").

### 4. K153412, Sleep Profiler (2016): blinding

- Reconciled: **Not stated**. P.T.D. (seen): same.
- D.H.A.N. (blind): **Implied by design**, quote (p. 13): "The results compared auto-detected staging and sleep
  disordered breathing (i.e., apnea-hypopnea index) to PSG results obtained by one rater per study."
- Source: as in item 3. The summary says the device signals were acquired concurrently with PSG; it does not say when
  the automatic staging was run or whether the raters could see it.
- Definitions: as in item 2.
- Effect: blind-none 13 to 12, blind-implied 5 to 6; Table S9 row.
- Decision: **keep** (Q.V.N., 28 October 2026). The guide's answer line for item 4 was left blank; the decision rests on
  the adjudicator's chat message of 28 October ("I agree") to the recommendations, which read keep for item 4. To be
  confirmed explicitly by the adjudicator; if reversed, the blinding counts move (not stated 13 to 12, implied by
  design 5 to 6) and the Results sentence on blinding changes.

### 5. K153412, Sleep Profiler (2016): pre-scoring

- Reconciled: **Not said**. P.T.D. (seen): same.
- D.H.A.N. (blind): **Not applicable**, same quote as item 3; follows from their coding of the reference as an
  algorithm.
- Definitions: Not applicable: "There were no human reference scorers (for example, an algorithm reference)". Not
  said: "does not say whether the reference scorers began from automatic scoring by any software".
- Effect: no count and no table changes (Table S9 does not show this field); `DEVICES.csv` only.
- Decision: **keep** (Q.V.N., 28 October 2026; guide answer line "5: keep").

### 6. K221179, SomnoMetry (2022): reference type. Both coders disagree.

- Reconciled: **Routine clinical scoring**. Quote: "201 polysomnography (PSG) files obtained from 2 AASM accredited
  Sleep Testing Facilities ... as the ground truths"; rule: "existing clinical scoring (procedure not reported)"; note:
  archived diagnostic clinical PSG from two AASM-accredited facilities; who scored them and how is not reported, nor
  whether automatic pre-scoring was used; 167 subjects in the staging table. The first-round checker (D.H.A.N.) agreed
  with this code and noted that the text does not say when or by whom the reference was scored.
- P.T.D. (blind): **Not described**, quote: "p. 8 (printed p. 5 of 8): 'AASM gold standard of manually scored PSG
  data.'"; comment: "Reference identified as manually scored PSG data from two AASM-accredited facilities. How
  reference scoring was produced, scorer independence, consensus, blinding, and use of automatic pre-scoring are not
  described."
- D.H.A.N. (seen): **Not described**, quote (p. 8): "SomnoMetry is non-inferior compared to AASM gold standard of
  manually scored PSG data."
- Source, p. 7: "Study that utilized retrospective clinical data to demonstrate automatic scoring sleep study
  results." P. 8, "Retrospective Clinical Performance Testing - Clinical Evaluation": "The clinical evaluation
  included a total of 201 polysomnography (PSG) files obtained from 2 AASM accredited Sleep Testing Facilities in
  California as the ground truths to validate the SomnoMetry AI/ML algorithms. An archived collection of
  retrospective diagnostic clinical PSG subject data was obtained from the 2 AASM Accredited Sleep Testing Facilities
  and were verified to meet the specified disease spectrum, medical condition, medication, and demographic
  requirements." ... "Table 2 confusion matrix with conditional probabilities shows that the performance of
  SomnoMetry is non-inferior compared to AASM gold standard of manually scored PSG data." P. 10: "In the
  retrospective diagnostic clinical study, the final study results and statistical analysis were reported for each
  endpoint." No sentence names scorers, a scoring procedure or a scoring date.
- Definitions: Routine clinical scoring: "The reference was the scoring made earlier in routine clinical care, not
  scoring done for the study". Not described: "The summary reports performance against a reference without saying
  how it was produced".
- Effect: routine 4 to 3, notdesc 2 to 3; unclear stays 7 (it sums routine, daily-practice and not described), so the
  Discussion's count is unchanged; the Results sentence and the Table S9 row change; `FDA_CODING_RECONCILIATION.md`
  lists K221179 among the routine-care summaries (a record, left as written, with this adjudication as the later
  word).
- Decision: **Not described** (Q.V.N., 28 October 2026; guide answer line "6: not described"). Applied to
  `DEVICES.csv`: `reference_type` not_described, `reference_rule` cleared, the quote extended with "non-inferior
  compared to AASM gold standard of manually scored PSG data" (both coders' quote), notes updated. Counts: routine
  clinical scoring 4 to 3, not described 2 to 3, unclear 7 unchanged; the amendment 006 D count of coded passages
  containing "manual" rises from 9 to 10, because K221179's coded passage now carries that sentence.

### 7. K223539, Dreem 3S (2023): reference type

- Reconciled: **Consensus, independence not stated**. Quote: "consensus of expert-scored PSG"; note: independence of
  the scorers not described; the 2-of-3 rule in the summary concerns EEG quality, not the staging reference.
  P.T.D. (blind): same.
- D.H.A.N. (seen): **Independent experts**, quote (p. 9): "Confusion matrix comparing Dreem 3S and consensus of
  expert-scored PSG for all sleep epochs is summarized as percentages in the table below."
- Source, p. 8: "comparing the performance of the Dreem device with expert-scored sleep stages from a cleared
  device"; p. 9: "Consensus from manual staging" (table header); "96.6% epochs per night of recording were determined
  to be acceptable for manual scoring and sleep staging by at least two out of three" (EEG quality study). A search
  of the summary for "independent", "separately" and "blind" finds nothing.
- Definitions: Independent experts: "Experts scored the recordings for this validation, and the summary describes
  them as scoring independently (for example 'independent', 'separately', 'blinded to each other')". Consensus,
  independence not stated: as above.
- Effect: consensus 4 to 3, indep 10 to 11 (indep-three unchanged: scorer count not stated); Table S9 row; the
  Results and Discussion sentences on the most common reference.
- Decision: **keep** (Q.V.N., 28 October 2026; guide answer line "7: keep").

### 8. K142825, Zmachine (2015): pre-scoring

- Reconciled: **Not said**. P.T.D. (seen): same.
- D.H.A.N. (blind): **Says they did**, quote (p. 7): "Using the Rechtschaffen and Kales (R&K) visual sleep staging
  guidelines."
- Source, p. 7: "The standard PSG channels were scored independently by two to four certified polysomnographic
  technologists, using the Rechtschaffen and Kales (R&K) visual sleep staging guidelines. The individual score files
  were then combined, on a 30-second epoch basis, using a majority voting rule, to generate a single score file per
  subject ('Human Scores')." No sentence mentions automatic scoring by any software before the technologists scored.
- Definitions: Says they did: "The summary says the reference scorers reviewed or edited automatic scoring". Not
  said: as above.
- Effect: prescoring-reported 0 to 1, and the statement that no summary reported whether reference scorers had worked
  from automatic pre-scoring (Results, Discussion, Supplementary Methods, and the amendment's keyword search) would no
  longer hold.
- Decision: **keep** (Q.V.N., 28 October 2026; guide answer line "8: keep"). The statement that no summary reported
  pre-scoring stands.

## Quote verification against the cached PDFs

- P.T.D.: 34 quoted passages, all found verbatim on the stated PDF page (after the K162627 correction). The remaining
  cells read "Nothing found" where the code was "Not stated" or "Not said", as the template asks.
- D.H.A.N.: 37 quoted passages, all located in the stated summary: 21 verbatim on the stated page; 11 verbatim after
  whitespace normalisation (line breaks from copying); 1 on the page before the stated one (K153353, blinding quote,
  PDF page 11, stated 12); 4 not verbatim for identifiable reasons: the K162627 reference and blinding quotes write
  "scoring-blind" for the printed "scoring-bind" (the same correction P.T.D. made at first), the K223922 reference
  quote spans PDF pages 10-11 and carries the running header "510(k) Summary 8" mid-sentence, and the K210034
  reference quote is cut at a line break. 29 blinding and pre-scoring cells hold "None" or a bare page reference
  instead of the template's "nothing found"; all belong to codes "Not stated", "Not said" or "Not applicable".

## Effect on the manuscript (applied 28 October 2026)

1. `DEVICES.csv`: K221179 changed as in item 6, after the pinned test counts had been changed first (fda-notdesc 3,
   fda-manual-ref 10; the tests failed, then passed). The two coders' codes were exported from the two workbooks to
   [D1_BLIND_CODES_2026-10-26.csv](D1_BLIND_CODES_2026-10-26.csv) (66 rows: 22 summaries times 3 fields, with the
   first-round code and each coder's code and exposure) by `d1_export_codes_2026-10-28.py`. The manuscript module
   computes every reported agreement, kappa and count from that file and the current `DEVICES.csv` (values `d1-*`,
   Tables S17 and S18), so no number is typed; `tests/test_psg_assist_manuscript.py` pins the values of the agreement
   table above.
2. The red placeholders are replaced: the AI statement; Methods (the sentence after the first check); Results
   (agreement 18 to 22 of 22 per field, kappa 0.636 to 1.000; the 8 disagreements; 1 code changed) and the
   Supplementary Methods paragraph (coders, exposure, agreement by exposure, inter-coder agreement, the adjudication
   and its count changes). The Limitations say the blind second coders were authors, blind to the codes but not to
   the hypothesis. The main text stays at 4,990 words with headings after cuts elsewhere.
3. The amendment's keyword-search statement and the "no summary reported pre-scoring" sentences stand.

## Open items

- D.H.A.N.: the GitHub repository that held the D2 package was still public on 28 October; the request to make it
  private stands.
- User: confirm item 4 explicitly (its answer line in the guide is blank; see its decision line above).
- Before any public snapshot: clear the workbook properties (the coders' names and ID-like numbers) or leave the
  sheets out.
