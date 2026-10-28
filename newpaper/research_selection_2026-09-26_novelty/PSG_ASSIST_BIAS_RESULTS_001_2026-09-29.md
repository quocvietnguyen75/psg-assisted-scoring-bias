# Assisted-scoring bias: results of protocol 001

Date: 29 September 2026. Protocol:
[PSG_ASSIST_BIAS_PROTOCOL_001](../plan/PSG_ASSIST_BIAS_PROTOCOL_001_2026-09-29.md);
aggregate output: [psg_assist_bias_001_report.json](psg_assist_bias_001_report.json).
It was run once, after all 1,025 PSG-IPA files verified against PhysioNet's
checksums. Code: `src/careport/psg_assist_bias.py` (15 synthetic tests;
full suite 467 passed, 1 skipped).

## Primary results (frozen decision: positive)

| Measure | Units positive | Exact sign test |
|---|---|---|
| M1 anchoring: semi-automatic scorings closer to the pre-fill than the same expert's manual scoring | 19 of 20 recording-task units | p = 4.0 × 10⁻⁵ |
| M2 inflation: pre-fill's gain against the assisted consensus minus independent human raters' gain | 20 of 20 | p = 1.9 × 10⁻⁶ |

## Per-task effects (kappa for stages, event F1 otherwise)

Intervals are crossed-bootstrap 95% intervals; the protocol treats them as
descriptive because each task has only five recordings.

| Task | M1 mean ΔA (95% CI) | Scorers positive | Pre-fill gain Δauto (range over 5) | Human gain Δhuman (range) | M2 DiD (95% CI) |
|---|---|---|---|---|---|
| Sleep stages | 0.081 (0.038 to 0.129) | 11/12 | +0.056 to +0.102 | −0.022 to −0.011 | 0.091 (0.072 to 0.112) |
| EEG arousals | 0.066 (0.011 to 0.133) | 10/12 | +0.018 to +0.155 | −0.043 to +0.004 | 0.089 (0.042 to 0.145) |
| Respiratory events | 0.129 (0.059 to 0.207) | 11/12 | +0.034 to +0.255 | −0.132 to −0.012 | 0.178 (0.066 to 0.300) |
| Limb movements | 0.103 (0.066 to 0.144) | 12/12 | +0.015 to +0.094 | −0.016 to +0.001 | 0.054 (0.023 to 0.089) |

Against the assisted consensus, the pre-fill's agreement rose in every
recording. Independent human raters' agreement with that consensus fell or
stayed flat.

## Secondary results

**M3, where agreement changes.** Mean pairwise agreement among the 12
scorers, manual then assisted:

| Task | Where pre-fill agrees with manual consensus | Where it disagrees |
|---|---|---|
| Sleep stages | 0.868 → 0.916 | 0.593 → 0.528 |
| EEG arousals | 0.977 → 0.983 | 0.647 → 0.604 |
| Respiratory events | 0.977 → 0.988 | 0.769 → 0.676 |
| Limb movements | 0.987 → 0.997 | 0.590 → 0.728 |

In three tasks, assistance raised agreement only where the algorithm
already matched the human consensus. Where it disagreed, agreement fell:
some experts followed the algorithm and others did not. Limb movements
converged in both regions.

**M4, clinical indices (descriptive, mixed).** The pre-fill's index error
against the assisted consensus was smaller than against the manual
consensus in 4 of 5 respiratory recordings and 3 of 5 limb recordings, but
larger in 5 of 5 arousal recordings. There, assisted scorers added
arousals beyond the pre-fill. Event-level agreement shifted toward the
algorithm more consistently than event counts.

**M5, YASA as an independent algorithm (sleep stages).** Run once, after
its channel rule was fixed in the protocol:
[psg_assist_bias_001_m5_yasa.json](psg_assist_bias_001_m5_yasa.json).
YASA 0.7.0, default model; C4-M1 EEG (Cz-M1 for SN1), E1-M2 EOG, chin EMG.

| Recording | YASA kappa vs manual consensus | vs assisted consensus | Δyasa | Δauto | Δhuman |
|---|---|---|---|---|---|
| SN1 (Cz-M1) | 0.812 | 0.821 | +0.009 | +0.062 | −0.012 |
| SN2 | 0.709 | 0.667 | −0.042 | +0.102 | −0.014 |
| SN3 | 0.753 | 0.706 | −0.047 | +0.056 | −0.022 |
| SN4 | 0.795 | 0.739 | −0.056 | +0.064 | −0.011 |
| SN5 | 0.736 | 0.671 | −0.065 | +0.090 | −0.020 |
| Mean | | | −0.040 | +0.075 | −0.016 |

Against the assisted reference, the independent algorithm lost agreement
in 4 of 5 recordings, like the independent human raters, while the
pre-fill gained in all 5. Under the reading fixed before the run, this fits
a pull toward the specific assisting algorithm rather than a general
improvement of the reference.

**Exploratory (not pre-specified): ranking of two algorithms.**
[psg_assist_bias_001_exploratory_ranking.json](psg_assist_bias_001_exploratory_ranking.json).
- Against the manual consensus, the pre-fill leads YASA by 0.079 kappa on
  average (0.840 vs 0.761), and YASA leads on SN1.
- Against the assisted consensus, the lead grows to 0.194 (0.915 vs 0.721),
  and SN1 flips to the pre-fill.
- The assisted reference puts the pre-fill at 0.915 kappa, above the
  dataset's reported manual inter-scorer kappa of 0.76 (source paper).

## Amendment 002: mechanism and robustness (secondary, descriptive)

Written before computing: [amendment 002](../plan/PSG_ASSIST_BIAS_AMENDMENT_002_2026-09-29.md).
Run once; aggregate output: [psg_assist_bias_002_report.json](psg_assist_bias_002_report.json).
Code: `src/careport/psg_assist_mechanisms.py`, with 9 synthetic tests; the
full suite passes (480 tests, 1 skipped). The refactored protocol 001
analysis reproduces the published M1 means exactly in the re-run.
Intervals are crossed-bootstrap 95% intervals (2,000 resamples). **Every
prediction was supported.**

**R1, acceptance lift by pre-fill stage** (P(assisted = pre-fill) −
P(manual = pre-fill)):
- N1 +0.173 (0.098 to 0.254), the largest, as predicted;
- N3 +0.095 (0.051 to 0.148);
- R +0.054 (0.016 to 0.098);
- N2 +0.040 (−0.021 to 0.111);
- W +0.029 (0.001 to 0.078).

**R2, respiratory event types** (F1 anchoring):
- hypopneas +0.234 (0.156 to 0.309);
- apneas +0.056 (−0.108 to 0.202).

Larger for hypopneas, as predicted.

**R3, dependence on ambiguity.** Lift by the number of the 12 manual
scorers sharing the most frequent label:

| Task | 12 (unanimous) | 10-11 | 8-9 | 7 or less |
|---|---|---|---|---|
| Sleep stages | −0.005 (−0.016 to 0.002) | +0.068 (0.024 to 0.119) | +0.149 (0.081 to 0.225) | +0.191 (0.104 to 0.292) |
| EEG arousals | −0.002 (−0.003 to −0.001) | +0.062 (0.026 to 0.094) | +0.124 (0.064 to 0.173) | +0.182 (0.106 to 0.243) |
| Respiratory events | +0.003 (0.000 to 0.006) | +0.111 (0.071 to 0.150) | +0.216 (0.145 to 0.288) | +0.240 (0.129 to 0.359) |
| Limb movements | +0.000 (−0.000 to 0.000) | +0.126 (0.087 to 0.164) | +0.273 (0.214 to 0.327) | +0.345 (0.278 to 0.409) |

The lift is essentially zero where experts agree unanimously, and rises
monotonically with ambiguity in all four tasks, as predicted. Event units
are 0.1-second bins.

**R4, following likely pre-fill errors.** On units where at least 10 of 12
manual scorers rejected the pre-fill's label, assisted scorings adopted
that label more often than the same experts' manual scorings did:

| Task | Difference (95% CI) | Units |
|---|---|---|
| Sleep stages | +0.241 (0.139 to 0.371) | 145 epochs |
| EEG arousals | +0.281 (0.188 to 0.380) | 13,645 bins |
| Respiratory events | +0.283 (0.186 to 0.385) | 33,751 bins |
| Limb movements | +0.514 (0.404 to 0.611) | 2,869 bins |

As predicted. A strong manual consensus is a proxy for truth, not truth.

**R5, scorer consistency.** Spearman correlations of per-scorer anchoring
across tasks were +0.29 to +0.55 in all 6 pairs: the same experts tend to
anchor more, as predicted. This assumes the scorer indices denote the same
person in every task.

**R6, robustness.** Both primary sign tests stay positive and significant
under every variant:

| Variant | M1 | M2 (DiD) | Task DiD range |
|---|---|---|---|
| Plurality stage consensus | 19/20, p = 4.0 × 10⁻⁵ | 20/20, p = 1.9 × 10⁻⁶ | +0.054 to +0.178 |
| Supermajority 9/12 | 19/20 | 19/20, p = 4.0 × 10⁻⁵ | +0.046 to +0.114 |
| IoU ≥ 0.2 event matching | 19/20 | 19/20 | +0.059 to +0.178 |
| Percent agreement for stages | 19/20 | 20/20 | +0.054 to +0.178 |

**Reading.** Assistance leaves unambiguous units untouched and concentrates
its pull where experts disagree: N1, hypopneas and contested bins. There,
experts in assisted mode accept pre-fill labels that most of their manual
peers rejected. This fits the M3 splitting pattern (some experts follow the
algorithm, others do not). It is harder to reconcile with a uniform gain in
accuracy.

## Interpretation and limits

- **Supported claim.** References built by editing an algorithm's
  pre-scoring systematically favour that algorithm relative to independent
  human raters. The DiD is 0.05-0.18 kappa or F1 units across four clinical
  scoring tasks.
- **Not shown.** Whether assisted references are further from the truth.
  If the algorithm were more accurate than the experts, moving toward it
  could be improvement. The M3 splitting pattern (less agreement where the
  algorithm disagrees) argues against simple convergence on the truth, but
  does not prove it. M5 adds an independent algorithm, which lost
  agreement against the assisted reference just as the human raters did.
  That is harder to reconcile with "the reference got better", though an
  algorithm that makes different errors from the pre-fill could still lose
  agreement against a truly better reference.
- **Design limits.**
  - Five recordings per task, one centre, 12 scorers and one algorithm
    family (the dataset authors' own).
  - **Fixed order.** The source paper (PMC9522290, Methods) states that
    scoring used "first a purely manual (visual), followed by a
    semi-automatic scoring approach", with "at least 4 months of
    separation", blind to earlier scorings. Its authors note "randomized
    order would have probably been a better choice". A drift in scoring
    habits over those months is therefore an alternative explanation for
    part of M1. A generic drift would not, however, reproduce the
    pre-fill's specific epoch- and event-level decisions, which is what M1
    and M2 measure. The write-up must state this limitation.
  - Pooled label counts were seen before freezing, as the protocol
    discloses.
- **Update, 29 September (amendment 003 simulation;
  [results](PSG_ASSIST_BIAS_RESULTS_003_SIMULATION_2026-09-29.md)).**
  - **Reproduced:** a model calibrated to the staging data, in which experts
    switch to the pre-fill on 31% of their disagreements, reproduces the R3
    dose-response and Δhuman.
  - **Bias:** under that model, the 12-expert assisted reference credits the
    expert-level pre-fill with about 5 points of accuracy it does not have.
    It scores the pre-fill above even a perfect competitor, and more
    assisted experts make this worse.
  - **Qualification of M2 and M5:** their human component and M5 can be
    pushed negative by an inclusion effect. Assisted panels reach a
    consensus on more hard epochs. On their own, these negative signs are
    therefore weak evidence that the reference moved away from the truth.
- **Next.** All pre-specified measures (M1-M5), amendment 002 and the
  amendment 003 simulation are complete, and the source paper's scoring
  schedule has been checked. The remaining workstreams and their order are
  tracked in the [state note](../plan/RESEARCH_SELECTION_STATE.md).
