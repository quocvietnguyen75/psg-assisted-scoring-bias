# Assisted-scoring bias: results of amendment 004 (remedy and two checks)

Date: 29 September 2026.
- Pre-specification:
  [amendment 004](../plan/PSG_ASSIST_BIAS_AMENDMENT_004_2026-09-29.md),
  committed before the run.
- Aggregate output: [psg_assist_bias_004_report.json](psg_assist_bias_004_report.json).
- Code: `src/careport/psg_assist_remedy.py`, with 10 synthetic tests. The
  full suite passes (506 tests, 1 skipped).

The analysis ran once. YASA's per-epoch labels were regenerated for it
(kept outside Git). They reproduce the M5 kappas within 1 × 10⁻¹⁶.

## A2: the assisted consensus moves to the pre-fill (supported)

On units where the two consensuses exist and differ, the table shows which
consensus equals the pre-fill.

| Task | Units that differ | Assisted consensus = pre-fill | Manual consensus = pre-fill |
|---|---|---|---|
| Sleep stages | 171 epochs | 0.930 | 0.058 |
| EEG arousals | 23,176 bins | 0.788 | 0.212 |
| Respiratory events | 27,754 bins | 0.951 | 0.049 |
| Limb movements | 11,550 bins | 0.988 | 0.012 |

- **Consistency:** the difference was positive in all 20 recording-task
  units (exact sign test p = 1.9 × 10⁻⁶).
- **Benchmark:** if the two sessions were interchangeable, the two shares
  would be equal.
- **Spread:** arousals varied most, from 0.16 to 0.76 by recording.
- **Model:** the calibrated model predicted 0.93 for stages.

This is the study's most direct and least model-dependent result. Where
the reference changed between the unassisted and the assisted session, it
changed to the algorithm's answer, in 79% to 99% of units.

## A1: common support (supported, but weaker)

| Measure | All epochs in each consensus (protocol 001, M5) | Epochs in both consensuses |
|---|---|---|
| Δhuman, kappa | −0.016 | −0.010 (−0.024 to 0.002) |
| Δhuman, percent agreement | not computed | −0.007 (−0.015 to 0.001) |
| ΔYASA, kappa | −0.040 (4 of 5 recordings negative) | −0.027 (4 of 5 negative) |
| ΔYASA, percent agreement | not computed | −0.017 (4 of 5 negative) |

The inclusion effect accounted for roughly a third to two-fifths of the
earlier drops. What remains is still negative. For the human raters,
however, the interval now includes zero, so M2's human component is weaker
evidence than it first appeared. The primary M2 result was driven by the
pre-fill's gain, and it stands.

## A3: the pre-fill against the experts' own unassisted consensus (not supported)

Both are judged against the assisted consensus.
- **Stages:** pooled percent agreement over epochs with both consensuses
  was 0.947 for the pre-fill against 0.964 for the manual consensus. The
  prediction required the pre-fill to be at least 0.954. By recording, the
  pre-fill was closer in 3 of 5, by both kappa and percent agreement.
- **Events:** by F1 against the assisted-consensus events, the pre-fill
  was closer in 1 of 5 recordings for arousals, 2 of 5 for respiratory
  events and 0 of 5 for limb movements.
- **Overall:** 6 of 20 units (p = 0.12).

So the experts' own unassisted judgment stays the closer of the two. A3
was meant as a model-light check of the simulation's finding that the
pre-fill outscores a perfect competitor. It cannot settle that finding,
because the unassisted consensus is not an independent competitor: the
same experts' persistent tendencies carry over between the two sessions.

**Exploratory follow-up (not pre-specified).**
- **What consistency changes.** In the model, within-expert consistency
  (c) changes A2 and A3. It does not change the bias, handicap or
  break-even, which depend only on each session's own distribution.
- **The calibrated α cannot fit.** At α = 0.31, no value of c reproduces
  both A2 and A3.
- **A fitting configuration.** Weaken consensus-level anchoring to
  α = 0.22 and set c = 0.5. The model then reproduces:
  - side-taking: 0.926 against 0.930 observed;
  - the experts' agreement across sessions: 0.964 against 0.964;
  - Δauto: 0.046 against 0.045.
- **Consequences in that configuration.** The pre-fill's bias against 12
  assisted experts is +0.032 rather than +0.050. A competitor needs a true
  accuracy 7.6 points above the pre-fill's to tie, rather than being
  unable to tie at all.

The "outscores a perfect competitor" finding is therefore the upper end.
The robust statement is a handicap of several points.

## Part B: the remedy

**B1, emulation on PSG-IPA** (4,857 epochs; percent agreement against the
unassisted consensus):

| Quantity | Unassisted target | Assisted reference, D0 (bias) | 9-of-12 assisted, D0s (bias) |
|---|---|---|---|
| Pre-fill agreement | 0.899 | 0.947 (+0.049) | 0.975 (+0.077) |
| YASA agreement | 0.850 | 0.839 (−0.011) | 0.864 (+0.014) |
| Pre-fill minus YASA | 0.049 | 0.108 (+0.059) | 0.112 (+0.063) |

The assisted reference more than doubles the pre-fill's lead over an
independent algorithm. A stricter consensus makes this worse: it keeps
only the epochs experts agree on, where the pre-fill is nearly always right.

**95% half-widths** of the audit estimators (D1 audit alone, D2 the
difference estimator):

| Audit fraction | Audited epochs | Pre-fill, D1 / D2 | Pre-fill minus YASA, D1 / D2 |
|---|---|---|---|
| 1% | 49 | ±0.084 / ±0.056 | ±0.117 / ±0.089 |
| 2% | 97 | ±0.059 / ±0.039 | ±0.082 / ±0.063 |
| 5% | 243 | ±0.037 / ±0.025 | ±0.051 / ±0.039 |
| 10% | 486 | ±0.025 / ±0.017 | ±0.035 / ±0.027 |
| 20% | 972 | ±0.017 / ±0.011 | ±0.024 / ±0.018 |

- **Audit size needed.** From a 5% audit up, D2's half-width for the gap
  (±0.039) is smaller than the naive bias (0.059).
- **Gain from D2.** D2 narrows the intervals by 24% for the gap, 33% for
  the pre-fill and 38% for YASA. That is equivalent to auditing about 1.7
  to 2.6 times as many epochs.
- **Why D2 helps.** It works because the same experts' unassisted and
  assisted consensus agree on most epochs.

**B2, the calibrated model.** The table gives the probability that the
truly better competitor is ranked above the pre-fill (Δ is the true
advantage).

| Design | Δ = 0.02, 5,000 epochs | Δ = 0.02, 50,000 epochs | Δ = 0.05, 5,000 epochs | Δ = 0.05, 50,000 epochs |
|---|---|---|---|---|
| D0 assisted reference | 0.000 | 0.000 | 0.000 | 0.000 |
| D0s 9 of 12 | 0.000 | 0.000 | 0.000 | 0.000 |
| D1 5% audit | 0.732 | 0.975 | 0.945 | 1.000 |
| D1 10% audit | 0.809 | 0.997 | 0.988 | 1.000 |
| D2 10% audit | 0.811 | 0.997 | 0.983 | 1.000 |

- **Equal competitor.** When the competitor is exactly as accurate
  (Δ = 0), D0 and D0s rank the pre-fill first with probability 1.000. D1
  and D2 do so with probability 0.5.
- **Model epochs are independent.** Real, serially correlated epochs carry
  less information, so the audit probabilities are optimistic.
- **D2's gain is small in the model.** It assumes less consistency between
  sessions than the data show (see A3).

## Predictions

| Prediction | Result |
|---|---|
| A1 Δhuman and ΔYASA negative on common support (both metrics) | Supported: all four means negative. The human interval includes zero |
| A2 the assisted consensus sides with the pre-fill; sign test p < 0.05 | Supported: every task; 20 of 20, p = 1.9 × 10⁻⁶ |
| A3 stages: pre-fill no more than 0.01 below the manual consensus | **Not supported:** 0.947 against 0.964 |
| PB1 D0 overstates the pre-fill's agreement and its lead over YASA | Supported: +0.049 and +0.059 |
| PB2 D2's standard error below D1's everywhere, in the data and the model | **Not supported:** true in the data at every fraction and for every target. In the model the two are nearly equal, and D2 is slightly worse for a 5-point-better competitor |
| PB3 D0 < 0.05 for a 2-point-better competitor; a 10% audit > 0.8 at 50,000 epochs | Supported: 0.000; 0.997 |
| PB4 D0s between D0 and D2 | **Not supported:** D0s is as bad as D0 (0.000) |

## Reading

1. **Central model-light evidence.** Where the reference changed between
   sessions, it changed to the pre-fill (A2). Together with M1 and M2, this
   is the paper's core finding.
2. **Remedy.** Have the experts score a random 5-10% of epochs without the
   pre-fill, and combine that audit with the assisted reference by the
   difference estimator. In these data this removes the bias, with 95%
   intervals of about ±2-4 points. Do not rely on a stricter consensus; it
   increases the bias.
3. **Revisions to earlier claims:**
   - The simulation's "outscores a perfect competitor" finding is the upper
     end of a large handicap.
   - The human-rater drop in M2 is partly an inclusion effect.
   - The 9-of-12 consensus's small bias in the simulation (+0.017) applied
     only to the epochs it keeps. As a reference for all epochs, it inflates
     the pre-fill's agreement further.

**Limits.**
- An epoch-level audit assumes scoring software can hide the pre-fill on
  randomly chosen epochs. Interleaving may change how experts score them.
- The standard errors are conditional on these 5 recordings.
- The population of epochs with an unassisted consensus is treated as
  known.

**Next.**
- The review of reference standards in validation practice (workstream 5).
- Drafting, and a $0 venue.
- The ScoreCraft reply is still pending.
