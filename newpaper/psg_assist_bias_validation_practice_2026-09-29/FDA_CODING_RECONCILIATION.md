# FDA coding check: reconciliation (11 October 2026)

Two authors checked the AI-assisted coding in [DEVICES.csv](DEVICES.csv) against the 25 summary PDFs, using
[FDA_CODING_CHECK.xlsx](FDA_CODING_CHECK.xlsx):
- Phuc Tai Duong (PTD), rows 1-12 (K120450 to K192469), on 8 October 2026;
- Duc Hoai Anh Nguyen (DHAN), rows 13-25 (K202142 to K253390), undated, returned on 11 October 2026.

The returned sheet is kept unchanged as [FDA_CODING_CHECK_COMPLETED.xlsx](FDA_CODING_CHECK_COMPLETED.xlsx). Before
DEVICES.csv was changed, the agent reread the cited passage of every disagreement and comment in the cached PDFs.
Every correction was confirmed. Page numbers are PDF pages; the summaries' printed page numbers are lower.

## Corrections that change counts in the manuscript

| 510(k) | Field | Was | Now | Evidence | Raised by |
|---|---|---|---|---|---|
| K242094 (Dreem 3S, 2024) | performance data; reference | yes; not described | no; no new performance data | p. 8: "No bench testing, animal testing, or clinical testing was performed to support this submission". The clearance adds a predetermined change control plan, and its performance is as reported for K223539. The 284 recordings on p. 9 set non-inferiority margins for future updates. | DHAN |
| K223922 (SOMNUM, 2023) | reference; scorers; rule | not described; none; none | consensus, independence not stated; 3; 2 of 3 | pp. 10-11: "the scoring of three technologists using 2/3 majority rule". The original quote came from the comparison table on p. 9, which missed this passage. | DHAN |
| K192469 (Nox Sleep System, 2019) | blinding to the device's output | not stated | implied by design | p. 15: the study exported "the reported indices/events from the pre-existing manual scoring and then [ran] the automatic scoring algorithm ... on the same clinical data". This meets the definition of "implied by design". | PTD |

Effect on the manuscript:
- 22 clearances have performance data (was 23).
- References: a consensus of experts not described as independent in 4 (was 3); not described in 2 (was 4).
- References that were routine scoring, a daily-practice panel or not described: 7 of 22 (was 9 of 23).
- Blinding: implied by design in 5 (was 4); not addressed in 13 (was 15).
- Unchanged: 10 independent-expert references (8 with three scorers), 4 routine, 1 daily-practice panel, 1 algorithm
  reference; 1 explicit and 2 unspecified blinding statements, 1 not applicable.

## Corrections to Table S9 or notes only

| 510(k) | Change | Evidence | Raised by |
|---|---|---|---|
| K120450 | Scorers: none to 3. Rule: "expert scoring consensus" to "consensus (rule not described)". New quote. | p. 5: "manual observation by three raters who were either sleep technicians or physicians". The phrase "Expert Scoring Consensus" does not appear as such; the table has an "Expert Scoring" header and a "No-Consensus" row. | PTD |
| K202142 | Note: five studies (four on Somnolyzer, one on CReSS), not four | p. 8 | DHAN |
| K210034 | Note: nine RPSGTs from three laboratories, three per subject | p. 12 | DHAN |
| K221179 | Rule: "existing clinical scoring (procedure not reported)". Note: 167 subjects in the staging table. | p. 8 | DHAN |
| K223539 | Note: the summary's 2-of-3 rule concerns EEG quality, not the staging reference | p. 9 | DHAN |
| K233438 | Rule: "2 of 3; epochs without a majority excluded" (86,983 included, 2,289 excluded) | p. 9 | DHAN |
| K241960, K252330 | Note: the same manual scoring served for the device and its comparators | p. 12; pp. 13-14 | DHAN |
| K253668 | Rule: "2 of 3; epochs without a majority excluded" (3,282). Note: the heart-rate reference is outside this review. | pp. 14-16 | DHAN |
| K253390 | Rule: "2 of 3; metrics on consensus epochs". Note: the blinding statement applies to the STAGES study; the second study (48 recordings) does not mention blinding. | pp. 15, 22 | DHAN |

The Table S9 label for `expert_consensus_details_limited` is now "Consensus, independence not stated", because
K223922 states its rule.

## Automatic pre-scoring (new column `prescoring_reported`)

For every summary, the checkers recorded whether it said that the reference scorers had started from automatic
scoring by any software.
- 23 summaries: "Not said" (coded `not said`, or `not applicable` where there is no performance data).
- K253390: "Says they did not". The checker limited this to the STAGES study and to SOMNUM's output: "it does not
  exclude automatic pre-scoring by other software". Coded `device output only`.
- K250851 (Hypnos): "says they did not". Its reference is EnsoSleep's unedited output, so there are no human reference
  scorers. Coded `not applicable`.

So no summary said whether its reference scorers worked from automatic pre-scoring by any software. The generated
value `fda-prescoring-reported` (0) counts statements of either kind among the clearances with performance data. The
manuscript now says "by any software" (abstract, Methods, Results, Discussion and the cover letter) and reports the
SOMNUM statement separately.

## Comments that needed no change

- K210034, K223539, K250058: the checker confirmed the codes and warned against over-reading them.
- K241960, K252330, K221179: the checker confirmed the routine-care code and added sample details, which the
  manuscript does not report.
- The "partly agree" marks on scorers and rule (K221179, K233438, K241960, K252330, K253668) are resolved by the rule
  changes above.
- Edits outside the checker columns do not affect the coding: the header "Summary PDF" and its link text were
  shortened, and the date 8 October was stored as 10 August.

## Consistency of the blinding code

"Implied by design" requires the summary to say that the device was run separately from, or after, the human scoring.
K192469 says so. The other routine-care summaries (K221179, K241960, K252330) do not say when the device was run, so
they stay "not stated", as their checker agreed.
