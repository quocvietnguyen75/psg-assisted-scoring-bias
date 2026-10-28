# Assisted-scoring bias: results of the amendment 003 simulation

Date: 29 September 2026.
- Pre-specification: [amendment 003](../plan/PSG_ASSIST_BIAS_AMENDMENT_003_2026-09-29.md),
  including note 1.
- Outputs: [psg_assist_bias_003_simulation.json](psg_assist_bias_003_simulation.json)
  (calibration, validation, checks, summaries) and
  [psg_assist_bias_003_grid.csv](psg_assist_bias_003_grid.csv) (all 810 grid
  cells).
- Code: `src/careport/psg_assist_simulation.py`, with 16 synthetic tests.
  The full suite passes (496 tests, 1 skipped).

All quantities are percent agreement for sleep staging. They are exact
large-sample expectations under a two-label latent-class model in which
experts edit the pre-fill. The model's truth is what a very large panel of
unassisted experts would converge to (note 1).

## Run history and checks

- **First run.** It stopped at calibration because of label switching:
  the unconstrained difficulty fit made experts more often wrong than right
  on about half of the epochs. Note 1 records the cause and the change,
  which was committed before the repeat run's output was seen.
- **Repeat run.** It ran once and completed.
- **Monte Carlo check (pre-specified).** The study's own estimators were
  applied to 400,000 simulated epochs. The largest difference from the
  analytic values over all 23 calibration and validation targets was
  0.001, against a tolerance of 0.015.
- **Additional check (not pre-specified).** Against simulated epochs with
  known truth, reference accuracy and the pre-fill's bias agreed with the
  analytic values within 0.001. This held for 1, 12 and 25 scorers and for
  both consensus rules.

## Calibration

Pooled over the 5,103 epochs where the pre-fill and all 24 scorings are
labelled:

| Target | Observed | Fitted |
|---|---|---|
| C1 share of epochs at manual agreement 12 / 10-11 / 8-9 / 7 or less | 0.509 / 0.248 / 0.135 / 0.108 | 0.511 / 0.250 / 0.146 / 0.094 |
| C2 pairwise manual agreement | 0.821 | 0.830 |
| C3 experts' manual agreement with the pre-fill | 0.831 | 0.831 |
| C4 pooled M1 | 0.052 | used to set α |

- **Difficulty.** 8.5% of epochs are clear. The rest have a folded normal
  difficulty (μ −0.06, σ 3.91).
- **C2 misfit.** C2 is fitted 0.009 too high: 10.6% of epochs have three
  or four distinct manual labels, which two labels cannot represent.
- **Pre-fill accuracy.** The pre-fill is about as accurate as an average
  expert: true accuracy 0.882 against 0.880 (δ_A = 0.03).
- **Anchoring strength.** α = C4/(1 − C3) = 0.31. In assisted mode, experts
  switched to the pre-fill on 31% of the epochs where they would otherwise
  have disagreed with it.
- **Per-scorer anchoring.** The scorer-specific values (S4) range from 0.02
  to 0.71. Three experts switched on more than half of their disagreements
  (0.51, 0.69 and 0.71). The rest were at 0.39 or less, and five were at
  0.11 or less.

## Validation (P1 supported)

These targets were not used in fitting.

| Target | Model | Observed |
|---|---|---|
| V1 Δauto | +0.065 | +0.045 |
| V2 Δhuman | −0.011 | −0.012 |
| V3 DiD | +0.076 | +0.057 |
| V4 M3, where the pre-fill agrees with the manual consensus: manual → assisted | 0.869 → 0.897 | 0.872 → 0.915 |
| V4 M3, where it disagrees | 0.636 → 0.529 | 0.590 → 0.526 |
| V5 R3 lift at agreement 12 / 10-11 / 8-9 / 7 or less | −0.006 / +0.069 / +0.145 / +0.177 | −0.007 / +0.065 / +0.146 / +0.179 |
| V6 R4 lift | +0.332 | +0.228 (amendment 002 interval 0.139 to 0.371) |
| V7 share of epochs that are R4 units | 0.043 | 0.028 |
| V8 pre-fill agreement with the manual consensus | 0.886 | 0.899 |
| V9 change for a human-level independent algorithm | −0.013 | negative (YASA, kappa) |
| V10 growth of the pre-fill's lead | +0.078 | positive (kappa) |

- **Signs.** Every sign is reproduced.
- **Close fits.** The only fitted anchoring quantity is α, taken from M1.
  With it, the model reproduces:
  - the R3 dose-response within 0.004 in every bin;
  - Δhuman within 0.001.
- **Misfits.** The model overpredicts:
  - Δauto, by 0.020;
  - the R4 lift, by 0.10 (still within the amendment 002 interval);
  - the R4 share: 0.043 against 0.028.

  So the real pre-fill makes fewer errors on epochs that experts find
  clear than an expert-level pre-fill would. Experts may also resist the
  pre-fill more when they disagree strongly. In the model, 99% of R4 units
  are pre-fill errors.
- **M3 misfit.** The disagreement-region misfit (0.636 against 0.590) is
  again the two-label limit.

## Consequences at the calibrated point

The pre-fill's true accuracy is 0.882, and the competitor is as accurate as
an average expert. The bias is measured minus true accuracy on the epochs
the reference includes. The handicap is the bias favouring the pre-fill
over that competitor.

| Reference | Reference accuracy | Pre-fill measured accuracy (bias) | Handicap |
|---|---|---|---|
| 1 expert, manual | 0.880 | 0.831 (−0.051) | −0.001 |
| 1 expert, assisted | 0.881 | 0.883 (+0.001) | +0.050 |
| 3 experts, manual | 0.920 | 0.857 (−0.026) | −0.001 |
| 3 experts, assisted | 0.912 | 0.915 (+0.033) | +0.063 |
| 5 experts, manual | 0.936 | 0.865 (−0.017) | −0.001 |
| 5 experts, assisted | 0.922 | 0.926 (+0.044) | +0.068 |
| 12 experts, manual | 0.970 | 0.886 (−0.005) | −0.000 |
| 12 experts, assisted | 0.944 | 0.951 (+0.050) | +0.064 |
| 25 experts, manual | 0.970 | 0.878 (−0.004) | −0.000 |
| 25 experts, assisted | 0.935 | 0.944 (+0.062) | +0.079 |
| 12 experts, 9-of-12 consensus, manual (84% of epochs) | 0.996 | 0.926 (−0.001) | −0.000 |
| 12 experts, 9-of-12 consensus, assisted (86% of epochs) | 0.983 | 0.985 (+0.017) | +0.020 |

1. **More assisted scorers make the bias worse.** Against manual
   references, the pre-fill's bias shrinks toward zero as experts are
   added. Against assisted references, it grows from +0.001 with one
   expert to +0.062 with 25. Adding assisted experts also lowers the
   reference's own accuracy, from 0.944 with 12 to 0.935 with 25, because a
   larger assisted majority locks in the pre-fill's errors on ambiguous
   epochs.
2. **The pre-fill outscores a perfect algorithm.** A perfect algorithm's
   measured accuracy equals the reference's accuracy. With 12 assisted
   experts that is 0.944, below the pre-fill's 0.951. So no competitor,
   however accurate, can tie the pre-fill.
   - **Grid:** the break-even advantage is undefined in 508 of the 720
     cells with α > 0.
   - **Scorer-specific anchoring (S4):** a competitor needs a true accuracy
     11 points above the pre-fill's (about 0.99) to tie.
3. **Assistance can make the reference worse.** Here the pre-fill is only
   expert-level, and the 12-expert assisted reference is 2.6 points less
   accurate than the manual one (0.944 against 0.970).
4. **A stricter consensus reduces the bias but does not remove it.** With
   9 of 12 votes required, the bias is +0.017, and 14% of epochs are
   excluded.
5. **Fairness.** Manual references are almost exactly fair between the
   pre-fill and an equally accurate competitor. The handicap is at most
   0.001 in size.

## Predictions

| Prediction | Result |
|---|---|
| P1 all validation signs reproduced | Supported |
| P2 with 12 experts, the assisted bias is positive and exceeds the manual bias | Supported: +0.050 against −0.005 |
| P3 the assisted bias is larger with 25 experts than with 1, and positive | Supported: +0.062 against +0.001 |
| P4 in every majority cell with α > 0, the assisted handicap exceeds the manual one; with 12 experts it is positive | Supported: 360 of 360 cells; +0.064 |
| P5 the signatures keep their sign at every δ_A, while the assisted reference is worse at δ_A = −1 and better at δ_A = 3 | **Not supported** |

**Why P5 failed.** The accuracy part held. With 12 experts, the assisted
reference's accuracy minus the manual reference's was −0.064 at δ_A = −1 and
+0.021 at δ_A = 3. The signature part failed:
- **Always positive:** M1 and Δauto, at every pre-fill ability.
- **Δhuman turns positive** at δ_A of 1.5 or more, which is exactly where
  the assisted reference becomes more accurate. Under note 1's convention
  there are no epochs where experts are mostly wrong. So an independent
  expert gains agreement whenever the reference moves toward the truth.
  The prediction had implicitly relied on such epochs.
- **The independent algorithm's change** depends on the panel:
  - With an even panel and ties excluded, it stayed negative even when the
    reference improved. The assisted panel reaches a consensus on more
    hard epochs, where every rater agrees less. Call this the inclusion
    effect.
  - With odd panels (3, 5, 25), it turned positive once the assisted
    reference was clearly more accurate.

**Reading.**
- M1 and Δauto cannot reveal whether an assisted reference got better or
  worse.
- Δhuman and M5 can, but only when computed on epochs included in both
  consensuses. The empirical versions used consensus rules that exclude
  epochs, so the inclusion effect may explain part of their negative sign.
- In the calibrated model, the pre-fill is expert-level, the assisted
  reference is less accurate, and the model reproduces the observed
  Δhuman.

## Sensitivity analyses

| Analysis | Refit | Bias with 12 assisted experts | Handicap | All validation signs |
|---|---|---|---|---|
| Base | | +0.050 | +0.064 | yes |
| S1 scorer ability spread τ = 0.5 | clear 0.039, σ 4.33, δ_A −0.05 | +0.052 | +0.067 | yes |
| S2 intra-rater consistency c = 0.5 | none needed | +0.050 | +0.064 | yes |
| S3 idiosyncratic pre-fill errors | ε = 0: the base model already exceeds the observed R4 share | +0.050 | +0.064 | yes |
| S4 scorer-specific anchoring (0.02-0.71) | none needed | +0.044 | +0.056 | yes |

Every sensitivity analysis keeps the P2-P4 conclusions. S2 brings the
unanimous-bin R3 lift to 0.000 and the R4 lift to 0.305.

## Interpretation and limits

**Supported (under the model).** When experts edit an expert-level
pre-fill, the resulting reference credits the pre-fill with about 5 points
more accuracy than it has with 12 experts, and 6 points with 25. It also
scores the pre-fill above any competitor, including a perfect one. More
experts make this worse, not better. A 9-of-12 consensus reduces the bias
but does not remove it.

**A check that depends little on the model.** The observed Δauto is 0.045.
The model gives a manual-reference bias near zero with 12 experts (−0.005).
Together these imply that the pre-fill's measured accuracy against the
assisted reference exceeds its true accuracy by about 4 points. The model's
own figure is 5.

**Limits.**
- The model has two labels, and experts are conditionally independent
  given the epoch's difficulty.
- The truth is defined as the large unassisted panel, so the model cannot
  represent experts who are all systematically wrong.
- The model overpredicts Δauto and R4, so its bias figures are more likely
  high than low.
- It covers one dataset, one task and one pre-fill algorithm.
- It has no stage-specific or recording-level structure.
- Event tasks were not simulated.

## Update after amendment 004 (29 September)

See [results 004](PSG_ASSIST_BIAS_RESULTS_004_REMEDY_2026-09-29.md).
- **Finding 2 is the upper end.** A model-light check (A3) could not
  confirm it. The model also overstates consensus-level anchoring.
  - An exploratory configuration (α = 0.22, within-expert consistency 0.5)
    reproduces the observed side-taking, the experts' agreement across
    sessions and Δauto.
  - In that configuration, the bias with 12 assisted experts is +0.032,
    and a competitor needs a 7.6-point advantage to tie.
- **Finding 4 concerns only the epochs the stricter consensus keeps.**
  Against all epochs, the 9-of-12 assisted reference inflates the
  pre-fill's agreement more than the majority reference does (+0.077
  against +0.049 in the data). In the model it does not restore the correct
  ranking.
- **Findings 1, 3 and 5 stand.**

## Next

1. **Workstream 4, the remedy**, under a dated amendment 004 (done; see
   results 004). Include two
   checks the simulation motivates:
   - Δhuman and M5 recomputed on epochs included in both consensuses, to
     remove the inclusion effect;
   - whether the assisted consensus sides with the pre-fill or with the
     manual consensus where they differ. This is a model-light check of
     finding 2.
2. **Drafting.**
