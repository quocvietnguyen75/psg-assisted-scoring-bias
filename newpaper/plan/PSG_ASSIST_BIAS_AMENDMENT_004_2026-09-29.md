# Assisted-scoring bias: amendment 004 (remedy and two checks)

Date: 29 September 2026. Follows
[amendment 003](PSG_ASSIST_BIAS_AMENDMENT_003_2026-09-29.md) and its
[results](../research_selection_2026-09-26_novelty/PSG_ASSIST_BIAS_RESULTS_003_SIMULATION_2026-09-29.md).
Config: [psg_assist_bias_004](../../config/preanalysis/psg_assist_bias_004_2026-09-29.json).

This amendment is written before any analysis below is computed on the
real data.
- **Seen:** all results of protocol 001 and amendments 002 and 003,
  including M5 and the exploratory ranking. Before writing, the
  model-based values quoted in the predictions were computed from the
  amendment 003 model. That is model output only.
- **Not seen:** every quantity defined below on PSG-IPA.

**YASA labels.** YASA's per-epoch labels were not kept by the M5 run. They
are regenerated with the same code and channels. YASA is deterministic, so
the regenerated labels must reproduce the M5 kappas within 10⁻⁹, or the run
stops. The labels stay outside Git.

All analyses are **secondary**. They add no decision rule.

## Part A: two checks motivated by the simulation

**A1 Common support (sleep stages).** Assisted panels reach a consensus on
more hard epochs, and this alone can lower any independent rater's
agreement (the inclusion effect). A1 recomputes two measures on epochs where
both consensuses exist:
- **Δhuman:** for each scorer and recording, manual agreement with the
  other 11 scorers' assisted consensus minus agreement with their manual
  consensus (6 or more votes each). Only epochs where both leave-one-out
  consensuses exist count.
- **ΔYASA (M5):** YASA's agreement with the 12-scorer assisted consensus
  minus agreement with the manual consensus (7 or more votes each). Only
  epochs where both consensuses exist count.

Metrics are kappa (protocol 001's metric) and percent agreement.
- Δhuman: mean over the 60 scorer-recording cells, with a crossed-bootstrap
  interval.
- ΔYASA: per recording, and the mean.

*Prediction:* both stay negative on common support, in both metrics. For a
human-level independent algorithm, the calibrated model gives −0.009 on
common support, against −0.013 without that restriction.

**A2 Which side the assisted consensus takes (all four tasks).**
- **Units:** those where both consensuses exist and differ. For stages,
  these are epochs. For events, they are 0.1-second bins where the
  consensus event status differs.
- **Measure:** the share of those units where the assisted consensus
  equals the pre-fill, minus the share where the manual consensus does.
  - If the two sessions were exchangeable (no anchoring, and any drift
    unrelated to the pre-fill), the two shares would be equal.
  - For events the two shares sum to one. For stages, both consensuses can
    differ from the pre-fill.
- **Test:** the difference per recording-task unit, and an exact sign test
  over the 20 units, as in protocol 001.
- *Prediction:*
  - the difference is positive in every task, pooled over recordings;
  - the sign test gives p < 0.05.
- *Model values for stages.* Among changed epochs, the share moving toward
  the pre-fill is 0.93 in the calibrated model. It is 0.97 with
  intra-rater consistency 0.5, and exactly 0.5 without anchoring.

**A3 The pre-fill against the experts' own unassisted consensus.** Both are
judged against the assisted consensus.
- **Stages:** kappa and percent agreement on epochs where both consensuses
  exist and the pre-fill is labelled.
- **Events:** F1 against the assisted-consensus events.
- **Reported:** results per recording, and the count of the 20
  recording-task units where the pre-fill is closer.
- *Prediction, stages only:* the pre-fill's percent agreement with the
  assisted consensus is not lower than the manual consensus's by more than
  0.01. For reference, the model values (pre-fill against manual
  consensus) are:
  - calibrated model: 0.952 against 0.943;
  - with intra-rater consistency 0.5: 0.951 against 0.951;
  - without anchoring: 0.894 against 0.964.
- No prediction is made for the event tasks.

## Part B: the remedy (workstream 4)

The question is how much unassisted scoring removes the bias.

**Setting.** A validation study scores every epoch with assistance. The
same experts also score a random audit fraction f of epochs without the
pre-fill.

**Designs compared** (percent agreement, sleep stages):
- **D0:** the assisted consensus (7 of 12) alone.
- **D0s:** the assisted consensus with a 9-of-12 supermajority, on the
  epochs that reach it.
- **D1:** the audit alone. Agreement with the unassisted consensus on the
  audited epochs.
- **D2:** the audit combined with the assisted consensus by a difference
  (prediction-powered) estimator. The estimate is:
  - the mean agreement with the assisted consensus over all epochs;
  - plus the mean, over audited epochs, of agreement with the unassisted
    consensus minus agreement with the assisted consensus.

**Target:** agreement with the unassisted consensus, on all epochs where
it exists.
- **Why the unassisted consensus alone.** Whether the assisted consensus
  exists depends on the pre-fill. Conditioning on it would select epochs by
  the pre-fill's correctness and bias even the audit estimators. This was
  noticed while writing the tests, before any computation.
- **D2's assisted term** counts agreement as 0 where the assisted consensus
  does not exist. Any fixed rule keeps D2 unbiased.
- **D0 and D0s** use the epochs where their own assisted consensus exists,
  which is what a study relying on them would report.
- **Known population.** The emulation treats the set of epochs with an
  unassisted consensus as known. In a real audit it is known only for
  audited epochs, so this slightly flatters D2.

**Audit fractions:** f = 0.01, 0.02, 0.05, 0.1 and 0.2.

**B1 Emulation on PSG-IPA.**
- **Population:** epochs where the pre-fill and YASA are labelled and the
  unassisted consensus exists.
- **Targets:** the pre-fill's agreement, YASA's agreement, and the
  pre-fill-minus-YASA gap.
- **Audit draw:** stratified simple random sampling within recordings,
  with proportional allocation.
- **Precision:** bias and standard error come from exact finite-population
  formulas for this design. D1 and D2 are unbiased by construction.
  RMSE and 95% half-widths are reported.
- **Headline figure:** the smallest f at which D2's 95% half-width for the
  gap falls below D0's bias for the gap.

**B2 Simulation (the calibrated amendment 003 model).**
- 12 experts, with the same population and designs as B1.
- **Competitor:** it has the experts' error pattern, and its true accuracy
  exceeds the pre-fill's by Δ = 0, 0.01, 0.02 or 0.05.
- **Study sizes:** 5,000 and 50,000 epochs, about 5 and 50 recordings.
  Epochs are treated as independent. This overstates how much information
  real, serially correlated epochs carry.
- **Output:** for each design and f, the probability of ranking the
  competitor above the pre-fill. It uses a normal approximation built on
  the model's exact per-epoch means, variances and covariances. For Δ = 0,
  the output is the probability of ranking the pre-fill above an equally
  accurate competitor.

**Predictions (stated before running).**
- **PB1:** In the data, D0 overstates the pre-fill's agreement with the
  unassisted consensus. It also overstates the pre-fill-minus-YASA gap.
- **PB2:** D2's standard error is below D1's at every f. This holds for the
  pre-fill, for YASA (or the competitor) and for the gap, in both the data
  and the model.
- **PB3:** In the model, take a competitor that is truly 2 points more
  accurate than the pre-fill:
  - D0 ranks it above the pre-fill with probability below 0.05, at both
    study sizes;
  - D1 and D2 with a 10% audit do so with probability above 0.8 at 50,000
    epochs.
- **PB4:** For that competitor at 50,000 epochs, D0s's probability lies
  between D0's and D2's (10% audit).

## Reporting

- Every analysis is reported whatever its direction. Predictions that fail
  are stated as such.
- The code is test-first, and the real data are run once. Any later fix
  gets a dated note, and both outputs are kept.
- Aggregate outputs only go to Git. Regenerated YASA labels and all
  per-epoch values stay in the ignored `outputs/`.
