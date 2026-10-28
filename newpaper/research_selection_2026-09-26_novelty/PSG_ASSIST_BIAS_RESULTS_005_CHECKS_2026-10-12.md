# Assisted-scoring bias: results of amendment 005 (checks requested by the pre-submission review)

Date: 12 October 2026.

**Plan and record.**
- [Amendment 005](../plan/PSG_ASSIST_BIAS_AMENDMENT_005_2026-10-12.md), committed in 67b794f (15:31) before anything in it
  was computed. Its operational clarifications came with the code in b73f79c (15:41), and note 1 (GSSC's settings)
  in b97f0e5 (15:50).
- Reports: [psg_assist_bias_005_report.json](psg_assist_bias_005_report.json) and
  [psg_assist_bias_005_crosscheck.json](psg_assist_bias_005_crosscheck.json).
- The real data were run once (15:51), with the checksums of all 1,025 files verified.

**Stager labels.**
- YASA's labels were regenerated with the M5 code. They are identical to amendment 004's cache and reproduce the M5
  kappas within 1.1 × 10⁻¹⁶.
- GSSC 0.0.9 (PyTorch 2.5.1 on the CPU) labelled the same 5,103 in-window epochs of the five staging recordings.
- Both label files stay in `outputs/`.

## Summary

Every check that bears on the paper's claims went in the paper's direction.
- **C1.** The adoption of rejected labels survives selection on the other experts only (19 of 19 nonzero units).
  For stages it shrinks from +0.24 to +0.17, as predicted.
- **C2.** On epochs where an algorithm the experts never saw disagreed with the pre-fill, the experts moved away
  from that algorithm's label and toward the pre-fill's. This held for YASA and for GSSC.
- **C5.** With GSSC as the comparator, the pre-fill and GSSC were roughly level against the manual consensus but
  the pre-fill led in all five recordings against the assisted consensus.
- **C4.** Audits of 30-minute blocks need about 10% of the blocks, against 5% of single epochs, to resolve the
  bias of the assisted reference.
- **Failed prediction.** C4's prediction failed as worded (see C4).

## C1 Adoption of rejected labels without selecting on the scored expert

Units qualify when at least 9 of the other 11 experts' manual labels reject the pre-fill's label. Events are counted
at event level. The lift is P(assisted label = pre-fill) minus P(manual label = pre-fill), for the scored expert.

| Task | C1 lift (95% interval) | Expert-unit pairs | Cells | R4 rule at event level (≥10 of 12, scorer included) | Amendment 002's R4 |
|---|---|---|---|---|---|
| Sleep stages | +0.169 (+0.074 to +0.279) | 3,096 | 60 | — | +0.241 |
| EEG arousals | +0.269 (+0.160 to +0.390) | 432 | 60 | +0.303 | bins |
| Respiratory events | +0.231 (+0.120 to +0.351) | 1,248 | 60 | +0.258 | bins |
| Limb movements | +0.374 (+0.103 to +0.647) | 399 | 52 | +0.499 | bins |

- **Units.** Positive in 19 of 20 recording-task units. The twentieth, limb movements SN4, is exactly 0. The exact
  sign test over the 19 nonzero units gives p = 3.8 × 10⁻⁶.
- **Event level.** Counted per event rather than per bin, the R4 rule gives lifts close to C1's.
- **What changed and what did not.** Removing the selection on the scored expert lowered the stage lift by about a
  third, but the lift stayed clearly positive in every task.
- **Assumption.** C1 relies on experts labelling independently, given the unit, within a session.
- **Prediction C1** (positive in every task, p < 0.05, stage lift below R4's): **supported**.

## C2 Negative control: movement toward an algorithm the experts never saw (sleep stages)

These are epochs where the stager and the pre-fill both give a label and the labels differ. Values are means over
the 60 expert-recording cells.

| Stager | Epochs where it differs from the pre-fill | Toward the stager (95% interval) | Toward the pre-fill (95% interval) | Side-taking toward the stager (assisted / manual consensus) |
|---|---|---|---|---|
| YASA | 1,052 | −0.135 (−0.206 to −0.076) | +0.162 (+0.101 to +0.233) | 0.00 / 0.93 of 122 changed epochs |
| GSSC | 794 | −0.156 (−0.242 to −0.086) | +0.183 (+0.113 to +0.268) | 0.00 / 0.96 of 100 changed epochs |

- **Every recording.** Movement toward the stager was negative and movement toward the pre-fill positive in each
  recording:
  - toward YASA, −0.095 to −0.168, against +0.138 to +0.184 toward the pre-fill;
  - toward GSSC, −0.104 to −0.234, against +0.139 to +0.234.
- **Side-taking.** Take the epochs where the stager and the pre-fill disagreed and the two consensuses differed.
  There, the assisted consensus never took the stager's label, while the manual consensus did in 93% (YASA) and 96%
  (GSSC) of epochs.
- **Interpretation.** The shift between sessions went toward the algorithm the experts were shown, not toward
  algorithm-like or more typical scoring.
- **Limit.** C2 cannot detect a shift toward conventions of this centre that only the pre-fill encodes.
- **Prediction C2** (movement toward YASA at or below 0; toward the pre-fill above 0): **supported**.

## C3 The pre-fill's own gain on common support (sleep stages)

| Recording | Δauto, kappa (percent) | Δhuman, kappa | Session-free contrast vs YASA, kappa | vs GSSC, kappa |
|---|---|---|---|---|
| SN1 | +0.043 (+0.030) | −0.004 | +0.033 | +0.023 |
| SN2 | +0.076 (+0.053) | −0.006 | +0.103 | +0.114 |
| SN3 | +0.032 (+0.022) | −0.010 | +0.054 | +0.038 |
| SN4 | +0.046 (+0.033) | −0.009 | +0.087 | +0.063 |
| SN5 | +0.074 (+0.030) | −0.020 | +0.129 | +0.128 |
| Mean | +0.054 (+0.034) | — | +0.081 | +0.073 |

- **Size.** On common support, the pre-fill's gain is smaller than in protocol 001 (+0.075 kappa), but it is positive
  in every recording. The DiD on common support averages +0.064 kappa.
- **Session-free contrast.** It needs no human baseline, and it is positive in 5 of 5 recordings for both stagers.
  In percent agreement the means are +0.051 (YASA) and +0.045 (GSSC).
- **Prediction C3** (Δauto positive in all five; contrast positive in at least four): **supported**.

## C5 GSSC as a second independent stager

| Recording | GSSC kappa vs manual / assisted consensus | ΔGSSC | Pre-fill's lead over GSSC vs manual / assisted consensus |
|---|---|---|---|
| SN1 | 0.818 / 0.830 | +0.012 | −0.029 / +0.020 |
| SN2 | 0.758 / 0.701 | −0.057 | +0.058 / +0.218 |
| SN3 | 0.865 / 0.847 | −0.018 | −0.011 / +0.063 |
| SN4 | 0.841 / 0.821 | −0.020 | +0.062 / +0.145 |
| SN5 | 0.865 / 0.802 | −0.063 | −0.024 / +0.128 |

- **Change against the assisted reference.** Mean ΔGSSC is −0.029, negative in 4 of 5 recordings, as for YASA
  (−0.040, 4 of 5).
- **Ranking.** Against the manual consensus, GSSC was ahead of the pre-fill in 3 of 5 recordings, with a mean lead
  for the pre-fill of +0.011. Against the assisted consensus, the pre-fill led in all 5, with a mean lead of +0.115.
- **For comparison, YASA.** Its leads were −0.024 to +0.107 against the manual consensus and +0.029 to +0.259
  against the assisted consensus.
- **Prediction C5** (mean ΔGSSC negative; lead larger against the assisted consensus): **supported**.

## C4 Audits of contiguous 30-minute blocks (sleep stages)

There are 4,857 population epochs in 87 blocks. D0's bias for the gap, recomputed, is +0.059 (amendment 004:
+0.059).

| f (blocks) | Expected share of epochs | D2 95% half-width: pre-fill / YASA / gap | Epoch sampling, D2 for the gap (amendment 004) |
|---|---|---|---|
| 0.05 (5 of 87) | 0.058 | 0.035 / 0.041 / 0.062 | 0.039 |
| 0.10 (10) | 0.116 | 0.024 / 0.028 / **0.045** | 0.027 |
| 0.20 (18) | 0.206 | 0.016 / 0.019 / 0.030 | 0.018 |
| 0.30 (25) | 0.287 | 0.013 / 0.015 / 0.024 | — |
| 0.50 (44) | 0.507 | 0.008 / 0.010 / 0.015 | — |

- **Headline.** The smallest f at which D2's half-width for the gap falls below the assisted reference's bias is
  0.10: 10 of 87 blocks, about 12% of the epochs. Under epoch sampling it was 0.05.
- **D1 alone.** It needs more: its half-width for the gap is 0.080 at f = 0.10 and 0.056 at f = 0.20.
- **Prediction C4: not supported as worded.**
  - *What was predicted.* Every block half-width is larger than its epoch-sampling value at the nearest fraction,
    and the smallest qualifying f exceeds 0.05.
  - *Second part.* It holds (0.10).
  - *First part, like-for-like fractions.* At 0.05, 0.10 and 0.20, every block half-width is larger, as expected.
  - *First part, where it fails.* For f = 0.30 and 0.50, the nearest epoch fraction in amendment 004's grid is
    0.20. At f = 0.50 the block half-widths (0.008, 0.010, 0.015) are smaller than the epoch-sampling values at
    0.20 (0.011, 0.012, 0.018).
  - *Why.* The prediction compared different fractions there. It is reported as failed and not reinterpreted.

## C6 Inflation with the rules' minimum event durations

Consensus events shorter than 3 s (arousals), 10 s (respiratory events) or 0.5 s (limb movements) were dropped.

| Task | DiD per recording | Mean |
|---|---|---|
| EEG arousals | +0.023, +0.151, +0.063, +0.086, +0.089 | +0.082 |
| Respiratory events | +0.097, +0.191, +0.043, +0.394, +0.312 | +0.207 |
| Limb movements | +0.087, +0.040, +0.015, +0.020, +0.110 | +0.054 |

Positive in 15 of 15 event units (exact sign test p = 6.1 × 10⁻⁵).

**Prediction C6** (positive in every task's mean; at least 13 of 15 units): **supported**.

## D3 Library cross-check

These ran in a separate environment with scikit-learn 1.9.1 and SciPy 1.17.1.
- **Kappa.** Over all 130 staging comparisons with the pre-fill (each manual and assisted scoring and both
  consensuses, five recordings), the study's kappa matched scikit-learn's `cohen_kappa_score` within 2.2 × 10⁻¹⁶.
- **Sign tests.** The exact two-sided sign tests matched SciPy's `binomtest` exactly (difference 0):
  - anchoring, 19 of 20;
  - inflation, 20 of 20;
  - side-taking, 20 of 20;
  - C1, 19 of 19 nonzero;
  - C6, 15 of 15.

## Part E: the text rules, applied

- **C1.** Sign test p < 0.05 and every task's mean is above 0. The rejected-label argument stays, with C1's values
  in the main text and R4 in the supplement. The residual assumption is stated.
- **C2.** Movement toward YASA is below 0, with an interval below 0. The manuscript reports the control as
  consistent with a shift specific to the pre-fill, within C2's limit.
- **C4.** The abstract and the recommendation cite block audits of about 10% of 30-minute blocks (about 12% of the
  epochs). The epoch-level 5-10% figure leaves the abstract.
- **C5.** Statements about an independent algorithm report both stagers with their per-recording values, and "more
  than doubled" is dropped.
- **Title and abstract.** These use associational wording, whatever the results, and state the estimand.

## Still to come

- **D1** (blind second coding of the FDA summaries): by the corresponding author and two teammates.
- **D2** (re-implementation by a person who has not read the code, and a clean re-run): to be assigned.
