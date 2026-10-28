# Assisted-scoring bias: amendment 003 (simulation of reference bias)

Date: 29 September 2026. Amends
[protocol 001](PSG_ASSIST_BIAS_PROTOCOL_001_2026-09-29.md) and follows
[amendment 002](PSG_ASSIST_BIAS_AMENDMENT_002_2026-09-29.md).
Config: [psg_assist_bias_003](../../config/preanalysis/psg_assist_bias_003_2026-09-29.json).

This amendment is written before any simulation output or any of the new
pooled aggregates below is computed.
- **Seen:** all protocol 001 and amendment 002 results, including the R3
  bin sizes and lifts, R4, the per-scorer kappa M1 means, and the
  percent-agreement M1 (0.054) and DiD (0.059) for stages.
- **Not seen:** the pooled percent-agreement aggregates C2-C4, the
  per-scorer values C3_j and C4_j, V1-V8, and every simulation output.
- Rough hand calculations during design used only the seen values.

The simulation is **secondary and descriptive**. It adds no decision rule.

## Why

The PSG-IPA data show that assisted references move toward the pre-fill,
but the truth is unknown. So they cannot show:
- how far the algorithm's measured accuracy departs from its true accuracy;
- whether the assisted reference misranks algorithms;
- whether more scorers or a stricter consensus fix it.

A simulation with a known truth can, provided that a simple model of the
scoring process reproduces the data's signatures.

## Model

A two-label latent-class model for 30-second epochs (sleep staging):
- **Labels.** Each epoch has a true label and one competing label, and every
  rater gives one of the two. Most staging disagreements are between two
  adjacent stages.
- **Difficulty.** With probability w an epoch is clear: every human and the
  independent algorithm are correct, and the pre-fill is correct with
  probability 1 − ε. Otherwise the epoch has difficulty b ~ Normal(μ, σ²).
- **Rater accuracy on the other epochs.** Raters are independent given the
  epoch. The probability of being correct is:
  - human j: logistic(τ z_j − b), where z_j is the normal quantile at
    (j − ½)/n;
  - pre-fill A: (1 − ε) logistic(δ_A − b);
  - independent algorithm B: logistic(δ_B − b).
- **Manual scoring.** Human j is correct with the probability above.
- **Assisted scoring.** Human j forms a judgment. With probability c it
  repeats their manual label; otherwise it is a new draw with the same
  accuracy. If the judgment matches the pre-fill, they keep it. Otherwise
  they switch to the pre-fill with probability α, the anchoring strength.
- **Reference.** n scorings, and the consensus is the label with at least m
  votes. Epochs where neither label reaches m are excluded. Majority:
  m = ⌊n/2⌋ + 1. Supermajority: m = ⌈3n/4⌉.
- **Base model:** τ = 0, c = 0, ε = 0 and δ_B = 0, so B is as accurate as the
  average human.

**Computation.**
- All quantities use percent agreement. They are exact large-sample
  expectations, computed by numerical integration over difficulty: 400
  quantile nodes plus the clear share.
- **Monte Carlo check.** The study's own estimator code (`pairwise_agreement`,
  `ambiguity_lift`, `error_following` and the consensus rule) is applied to
  400,000 epochs simulated at the calibrated point. The analytic and
  simulated values must agree within 0.015 for every calibration and
  validation target. Otherwise the run stops.

**Two analytical consequences, recorded before running:**
- The model gives M1 = α(1 − P(manual label = pre-fill)) exactly. So α is
  estimated from the data without the rest of the model:
  α = C4/(1 − C3), per scorer or pooled.
- An assisted scorer gives the pre-fill label with probability at least α
  on every epoch. So for α > 0.5, a large assisted majority converges to the
  pre-fill on every epoch.

## Calibration (PSG-IPA sleep staging)

The targets are pooled over the 5,103 epochs where the pre-fill and all 24
scorings are labelled (the R3 set), in percent agreement:
- **C1:** the shares of epochs at manual agreement levels 12, 10-11, 8-9
  and 7 or less. Amendment 002 counted 2,599, 1,263, 689 and 552.
- **C2:** mean pairwise agreement among the 12 manual scorings.
- **C3:** mean over scorers of manual agreement with the pre-fill; C3_j per
  scorer.
- **C4:** mean over scorers of assisted minus manual agreement with the
  pre-fill (a pooled M1); C4_j per scorer.

**Fit.**
1. Fit w, μ and σ by least squares on the first three C1 shares and C2,
   with equal weights. Nelder-Mead starts from w = 0.4, μ = −2, σ = 1.5, with
   one restart from the best point. The mean human ability is the origin.
2. Fit δ_A by bisection to C3.
3. Set α = C4/(1 − C3).

## Validation (targets not used in fitting)

The calibrated model predicts each target, and the run compares the
prediction with the pooled empirical value:
- **V1 Δauto:** pre-fill agreement with the 12-scorer assisted consensus
  (7 or more votes), minus its agreement with the manual consensus.
- **V2 Δhuman:** mean over scorers of manual agreement with the other 11
  scorers' assisted consensus (6 or more), minus agreement with their
  manual consensus.
- **V3 DiD** = V1 − V2.
- **V4 M3:** pairwise agreement among the manual and among the assisted
  scorings on epochs with a manual consensus, split by whether the pre-fill
  equals it (four values).
- **V5 R3:** lift in each of the four agreement bins.
- **V6 R4:** lift. **V7:** the share of epochs that are R4 units.
- **V8:** pre-fill agreement with the manual consensus.
- **V9 and V10, signs only**, because the observed values are kappa:
  - V9: the change in a human-level independent algorithm's agreement from
    the manual to the assisted consensus. Observed with YASA: negative.
  - V10: the growth of the pre-fill's lead over that algorithm. Observed:
    positive.

For R3 and R4, the amendment 002 intervals are shown as approximate
yardsticks. They are intervals for cell means, not for pooled values.

## Sensitivity analyses

Each one refits the calibration where needed, then repeats the validation
and the calibrated-point summaries:
- **S1:** scorer ability spread τ = 0.5.
- **S2:** intra-rater consistency c = 0.5.
- **S3:** idiosyncratic pre-fill errors. ε is fitted, together with δ_A,
  to the observed V7 share, searching ε in [0, 0.1]. If the base model
  already reaches that share, ε = 0.
- **S4:** scorer-specific anchoring α_j = C4_j/(1 − C3_j), clipped to
  [0, 1]. Run with 12 scorers only.

## Consequence grid (base model, calibrated difficulty)

The grid crosses:
- α in {0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8}, plus the calibrated α;
- δ_A in {−1, −0.5, 0, 0.5, 1, 1.5, 2, 3}, plus the calibrated δ_A;
- n in {1, 3, 5, 12, 25} scorers;
- majority and supermajority consensus.

For the manual and the assisted reference of each cell, the run reports:
- the share of epochs included, and the reference's accuracy against the
  truth;
- the measured and true accuracy of A and of a human-level B on the
  included epochs, and A's bias (measured − true);
- the **handicap**, h = (measured A − measured B) − (true A − true B), which
  is positive when the reference favours A;
- the **break-even advantage**: how much more accurate than A (true
  accuracy, all epochs) a competitor with the humans' error pattern must be
  to tie A's measured accuracy.

Each cell also reports its observable signatures: M1, Δauto, Δhuman
(leave-one-out, n ≥ 3) and B's agreement change.

## Predictions (stated before running)

- **P1:** The calibrated base model reproduces the sign of every validation
  target. For V4, the direction of change in both regions. For V5, a lift
  within ±0.01 in the unanimous bin that increases across the bins. No
  prediction is made about magnitudes; each is reported.
- **P2:** At the calibrated point with 12 scorers and majority consensus,
  A's measured accuracy against the assisted reference exceeds its true
  accuracy. That bias also exceeds A's bias against the manual reference.
- **P3:** More scorers do not remove the bias. At the calibrated point
  (majority), A's bias against the assisted reference is larger with 25
  scorers than with 1, and positive with 25.
- **P4:** For every α > 0 under majority consensus, the assisted
  reference's handicap exceeds the manual reference's (h_s > h_m), because
  assistance shifts the comparison toward A. At the calibrated point with
  12 scorers, h_s > 0.
- **P5 (identifiability):** At the calibrated α with 12 scorers (majority):
  - M1 > 0, Δauto > 0, Δhuman < 0 and a negative change for B hold at every
    δ_A in the grid;
  - the assisted reference is less accurate than the manual reference at
    δ_A = −1, and more accurate at δ_A = 3.

  The observed signatures therefore cannot tell whether an assisted
  reference is closer to the truth.

## Reporting and limits

- All grid cells go to a CSV. Each prediction is reported as supported or
  not, whatever its direction.
- The model is a deliberate simplification:
  - two labels per epoch;
  - conditional independence given difficulty;
  - one anchoring strength in the base model;
  - no recording-level structure.
- The calibration uses one dataset, one task and one pre-fill algorithm.
- The code is test-first, and the run is done once. Any later bug fix gets
  a dated note, and both outputs are kept.

## Note 1, 29 September 2026: first run stopped at calibration

**What happened.** The first run (code as in commit 89919eb) stopped at
step 2 of the base calibration: the pre-fill ability was not bracketed. It
produced no simulation output, validation or grid.

**Values seen while diagnosing.** The run's own calibration inputs and base
fit were recomputed:
- Pooled over 5,103 epochs:
  - C1 shares: 0.509, 0.248, 0.135 and 0.108;
  - C2 0.821, C3 0.831, C4 0.052.
- Fitted difficulty: clear share 0.085, μ −0.06, σ 3.91 (loss 2.1 × 10⁻⁴).
  C2 was fitted at 0.830.
- Under that fit:
  - mean expert accuracy was 0.547;
  - the experts' agreement with the pre-fill peaked at 0.830 near δ_A = 0,
    just below C3, and fell for larger δ_A.

**Cause.** In a two-label model, the manual agreement statistics do not
change when an epoch's expert accuracy p is replaced by 1 − p. So the
manual targets cannot tell whether the experts are mostly right or mostly
wrong on an epoch. The unconstrained normal difficulty used this freedom:
it made experts more often wrong than right on about half of the epochs.
This is the label-switching problem of latent-class models.

**Change, made before re-running.** Adopt the standard latent-class
convention that raters are better than chance.
- On every epoch, the true label is the one the experts give more often.
- Difficulty is b = −|x| with x ~ Normal(μ, σ²), a folded normal, so expert
  accuracy is at least one half everywhere. μ and −μ give the same model.
- The folded family reaches the same manual agreement statistics as the
  failed fit, so C1 and C2 fit as before.
- The simulation's truth is therefore what a very large panel of unassisted
  experts would converge to.
- Everything else is unchanged, including the predictions.

**Also seen (descriptive).**
- 543 epochs (10.6%) had 3 or 4 distinct manual labels, which a two-label
  model cannot represent. This is why C2 was fitted at 0.830 against 0.821
  observed.
- The pre-fill was one of the manual plurality labels on 88.8% of epochs.

The code change is test-first, and the run is repeated once. The first
run's error is recorded here. Its log stays outside Git because it
contains machine paths.
