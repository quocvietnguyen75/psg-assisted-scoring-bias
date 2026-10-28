# Assisted-scoring bias: amendment 002 (mechanism and robustness)

Date: 29 September 2026. Amends
[protocol 001](PSG_ASSIST_BIAS_PROTOCOL_001_2026-09-29.md), whose primary
and pre-specified secondary results (M1-M5) are already reported in
[results 001](../research_selection_2026-09-26_novelty/PSG_ASSIST_BIAS_RESULTS_001_2026-09-29.md).
Config: [psg_assist_bias_002](../../config/preanalysis/psg_assist_bias_002_2026-09-29.json).

This amendment is written before any of the analyses below is computed.
Protocol 001's primary results were seen, as were the M3 splitting pattern,
the M4 indices and the M5 YASA results. Nothing else was seen. All
analyses here are **secondary and descriptive**. They add no new decision
rule and do not change the primary conclusion.

## Why

To support a full paper: where the pull toward the pre-fill arises, whether
experts adopt likely pre-fill errors, and whether the primary conclusions
depend on analysis choices.

## Analyses and predictions (stated before computing)

**R1 Acceptance lift by pre-fill stage (sleep stages).** For each scorer,
recording and pre-fill stage X:

lift = P(assisted label = pre-fill | pre-fill = X) − P(manual label = pre-fill | pre-fill = X)

Only epochs in the window where both scorings are labelled count.
*Prediction:* the largest lift for N1, the least reliable stage.

**R2 Respiratory event type.** The M1 anchoring measure computed separately
for apneas (obstructive, central, mixed) and hypopneas (hypopnea, central
hypopnea), filtering every scoring to that type. *Prediction:* larger for
hypopneas.

**R3 Dependence on ambiguity.**
- Agreement level of each unit among the 12 *manual* scorings: epochs for
  stages; 0.1-second bins, scored as event or no event, for event tasks.
- Level = the count of the most frequent label, in four bins: 12
  (unanimous), 10-11, 8-9, and 7 or less.
- Per bin, the mean over scorers of [1(assisted = pre-fill) − 1(manual =
  pre-fill)].
- *Prediction:* the lift grows as manual agreement falls.

**R4 Following likely pre-fill errors.**
- Units where a strong manual consensus (10 or more of 12) disagrees with
  the pre-fill.
- For each scorer, the share of such units where the assisted scoring
  equals the pre-fill, minus the share where the manual scoring does.
- *Prediction:* positive. Experts adopt pre-fill labels that the manual
  consensus rejected.
- A strong manual consensus is a proxy for truth, not truth.

**R5 Scorer consistency across tasks.**
- Per-scorer mean M1 effect in each task, and Spearman correlations between
  tasks across the 12 scorers (6 task pairs).
- *Assumption:* the file indices scorer1-scorer12 denote the same person in
  every task. The source paper states that the same 12 experts scored all
  tasks, but the dataset does not confirm the index mapping.
- *Prediction:* weakly positive. Descriptive only.

**R6 Robustness of the primary conclusions.** Recompute the
recording-level M1 and M2 units and both exact sign tests under:
- (a) a plurality stage consensus (the most frequent label, with ties
  excluded; leave-one-out the same);
- (b) a supermajority consensus of 9 of 12 (9 of 11 leave-one-out), for all
  tasks;
- (c) event matching requiring IoU of 0.2 or more instead of any overlap;
- (d) percent agreement instead of kappa for stages.

*Prediction:* both primary sign tests stay significant and positive under
every variant.

## Inference and reporting

- Means with 95% crossed-bootstrap intervals over scorers and recordings:
  2,000 resamples, seed 20260930.
- R6 reports exact sign tests.
- Every analysis is reported whatever its direction. Results that contradict
  a prediction are stated as such.
- The code is test-first. The real data are run once; later bug fixes get a
  dated note with both outputs kept.
