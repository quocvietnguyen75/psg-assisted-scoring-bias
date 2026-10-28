# Assisted-scoring bias: amendment 006 (derived quantities asked for by the round-2 review)

Date: 27 October 2026. Status: **approved by the corresponding author on 27 October 2026** ("Right. Proceed with the
updates", in reply to the list of decisions that named this amendment); computed after that approval. Protocol 001 and amendments 002 to 005 stay in force; this amendment adds reporting only. No new
data are processed, no measure is redefined and no decision rule changes. Every quantity here is derived from the
committed reports and the frozen model of amendment 003, is labelled post hoc in the text, and is reported whatever
its value.

## Why

The round-2 panel of 26 October 2026 (`newpaper/psg_assist_bias_manuscript/review_2026-10-26/`) asked for four
quantities that the records do not yet hold in the form the text needs. The fidelity check of the same day found
nothing wrong with the reported numbers; these additions concern how the audit remedy, the exploratory model
configuration and the census coding rule are presented.

## A. Audit half-widths an auditor could compute from the sample (methodology seat, W3)

C4 and B1 report 95% half-widths from exact design-based standard errors with the within-stratum variances taken
from the whole population and the large-sample multiplier 1.96. An audit of f of the blocks would estimate the
within-stratum variance from its own blocks and use a t multiplier with the design's degrees of freedom.

- For each block fraction f in the C4 grid (1%, 2%, 5%, 10%, 20%, 50%) and each target (the gap, the pre-fill,
  YASA): the same standard error as C4 multiplied by t(0.975, df) with df = audited blocks minus the number of
  strata (five recordings), when df is at least 1; "not estimable" otherwise (one block per stratum).
- The smallest f at which the gap's D2 half-width under the t multiplier falls below the D0 bias of the assisted
  reference (the criterion of amendment 005 C4), or "none in the grid".
- Reported in Table S14 beside the known-variance values, and in the text: the 10% figure stays as the
  known-variance best case, and the recommendation names the fraction (or the number of blocks) that meets the
  criterion under the t multiplier, if any.
- This is a multiplier on existing standard errors, not a re-sampling; the standard error itself still uses the
  population variances, which the text says.

## B. The exploratory model configuration's anchoring value and validation row (Devil's Advocate, M3)

The configuration (alpha 0.22, consistency 0.5) examined after the independent-rater checks is reported with its
side-taking, agreement and bias values but without the primary anchoring measure. Compute, from the frozen model
of amendment 003 with that configuration: M1 (anchoring), the V1 to V8 validation targets as in Table S5, and the
assisted-reference bias with 1, 12 and 25 experts (majority rule). Report them in the Supplementary Methods next to
the calibrated configuration's values. The main-text statements that adding experts does not remove the bias and
that no competitor could tie at the calibrated strength are kept only if they hold in both configurations;
otherwise they move to the supplement with the caveat.

## C. The model's two crossovers (Devil's Advocate, M4)

From the existing identifiability grid of amendment 003 (no new computation): the pre-fill offset and true accuracy
at which the assisted reference first becomes more accurate than the manual one, and those at which Delta_human
first turns positive, with 12 experts and the majority rule; and on which side of each the observed Delta_human
(stages, all epochs and common support) falls. Reported in the Supplementary Methods.

## D. The census coding rule for "manually scored" references (Devil's Advocate, M7)

State in the Methods the rule already applied: a reference described only as manually scored was not counted as a
statement about pre-scoring by any software, because manual scoring can be done in software that pre-scores.
Count, from the coded passages in `DEVICES.csv` (the `reference_rule` and `quote` fields of the 22 clearances with
performance data), the number of summaries whose reference description uses the word "manual" or "manually", and
report it in the Results beside the statement that no summary said whether the scorers worked from pre-scoring.
The count is a generated value with a unit test; the keyword search of the first check is not repeated.

## E. Reading-only additions (no computation; listed for completeness)

- Delta_auto's sign in each of the 20 units (from the committed report 001), reported as the inflation evidence
  that has no session-matched baseline, with the DiD kept as the pre-specified primary and its session-matched
  interpretation stated in the Results (methodology seat, W2).
- The share of sleep-staging epochs on which the two consensuses differ (A2's 171 changed epochs over the
  common-support epochs of C3), and the failed prediction A3 with its values, in the main text (methodology seat,
  W6).
- The common-support DiD for stages (C3, already generated as a value), in the Results.

## Execution and reporting

Tests before code for every new generated value (the project's rule); the generator reads the committed reports and
the frozen model only; the build regenerates the tables; the response document of the round-2 review maps each item
to its sentence. Any discrepancy between a value here and the text is reported, not adjusted.
