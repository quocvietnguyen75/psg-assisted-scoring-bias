# Supplementary File S1: analysis plans

This file reproduces, verbatim, the protocol and the four amendments under which every analysis in the article was
run. Plan codes (M1, R3, A2, C1 and so on) are mapped to the names used in the article in Supplementary Table S1.

## Reading notes

The plans are reproduced exactly as they were written, so that their SHA-256 hashes below can be checked against the
study's repository. They therefore contain traces of the working environment:
- "The user" is the corresponding author, who approved the study's scope, the optional dependency YASA (protocol
  001) and amendment 005 before it was computed.
- Relative links point to other records in the study's repository: plans, configuration files and result reports.
  "Workstream" numbers and the candidate identifier in protocol 001 refer to the planning records of the topic
  selection that preceded the study.
- Local paths such as `data/psg-ipa/` and `outputs/` are folders on the analysis computer that held the downloaded
  dataset, per-epoch intermediate values and software environments. They are kept out of the repository, because only
  aggregate results are published.

## Provenance

All times are local (UTC+07:00). Protocol 001 and amendments 002 to 004 date from 29 September 2026, and amendment 005
from 12 October 2026. "Written" times come from time-stamped working logs of the analysis sessions; commit
identifiers and times come from the study's Git repository.

| Plan | Written | Analysis first run | Plan committed | Results committed |
|---|---|---|---|---|
| Protocol 001 (M1 to M4) | 09:31 | 10:24 | 4013337, 11:28, together with the results | 4013337, 11:28 |
| Protocol 001, operational details for M5 (YASA) | 11:30, after M1 to M4 were computed | 11:32 | 3dd1dcc, 11:33, together with the results | 3dd1dcc, 11:33 |
| Amendment 002 | 14:41 | 14:43 | 04c4710, 14:48, together with the results | 04c4710, 14:48 |
| Amendment 003 | 16:24 | 16:33 (stopped at calibration) | 89919eb, 16:36 | not applicable |
| Amendment 003, note 1 (folded difficulty) | 16:37 | 16:39 | 8641890, 16:39 | d304e24, 16:46 |
| Amendment 004 | 18:45 (edited until 18:50) | 18:53, after the plan was committed | dd06ba3, 18:53 | e1fb201, 18:59 |
| Amendment 005 | 15:15, approved by the corresponding author before commit | 15:51 | 67b794f, 15:31 | 7eb7f90, 15:55 |
| Amendment 005, operational clarifications | 15:40 | 15:51 | b73f79c, 15:41, with the tested code | 7eb7f90, 15:55 |
| Amendment 005, note 1 (GSSC settings) | 15:48, after an install check on synthetic signals | 15:51 | b97f0e5, 15:50 | 7eb7f90, 15:55 |

For amendments 003, 004 and 005 the repository shows each plan committed before its results. The protocol and
amendment 002 were committed in the same commits as their results, so for these the order rests on the working logs.
The first run under amendment 003 stopped at calibration, before any consequence was computed; note 1 records the
change made before the second run.

SHA-256 of each plan text as reproduced below (UTF-8, LF line endings):

- Protocol 001 (`PSG_ASSIST_BIAS_PROTOCOL_001_2026-09-29.md`): `69ab33f8b859b09c7ed3148cea5f7c06f9ff480421bf0e1f666cad3033b34298`
- Amendment 002 (first amendment) (`PSG_ASSIST_BIAS_AMENDMENT_002_2026-09-29.md`): `91aaff9acc3c49433b6a67f592d1c8367bc0b766fe1d3bc4806b9f0bc1e4445a`
- Amendment 003 (second amendment: simulation) (`PSG_ASSIST_BIAS_AMENDMENT_003_2026-09-29.md`): `73493ed4ce4561a2ec5202232bba2a499cb5b636b82dac9e4ed54ba6231e7011`
- Amendment 004 (third amendment: audit and independent-rater checks) (`PSG_ASSIST_BIAS_AMENDMENT_004_2026-09-29.md`): `45b4bded4947ac113dff3c8fe1e2b43b17bb40bc9f1b37dc9e5378917e2da942`
- Amendment 005 (fourth amendment: checks requested by a pre-submission review) (`PSG_ASSIST_BIAS_AMENDMENT_005_2026-10-12.md`): `1e82498854e6fe208f31dd81c6637e81de95fefaa162b7d4b12fee331d10e1a7`
- Amendment 006 (fifth amendment: derived quantities asked for by the round-2 review) (`PSG_ASSIST_BIAS_AMENDMENT_006_2026-10-27.md`): `ab239748d2d996a1d9d9580a426eb8913092ee0428bd05c5f5fb941b5b8e7d2b`


---

# Protocol 001

# Assisted-scoring bias in sleep-scoring references: protocol 001

Date: 29 September 2026. Candidate: `psg_assisted_scoring_incorporation_bias`
([novelty round](../research_selection_2026-09-26_novelty/CANDIDATES.md)).
Machine-readable version:
[config](../../config/preanalysis/psg_assist_bias_001_2026-09-29.json).
This protocol is frozen before any agreement, consensus or algorithm
statistic is computed. Any change needs a dated amendment.

## Question

When expert scorers edit an algorithm's pre-scoring (semi-automatic
scoring), do their labels move toward that algorithm? Does a reference
built from such labels inflate the algorithm's measured accuracy relative to
independent raters?

## Data

PSG-IPA 1.0.0 (PhysioNet, open, CC BY 4.0), held locally under
`data/psg-ipa/` (ignored by Git). It has four tasks (sleep stages, EEG
arousals, respiratory events, limb movements), five recordings per task and
12 expert scorers. Each scorer has a manual and a semi-automatic scoring
per recording, and each recording has one automatic pre-fill ("auto"): the
starting point of the semi-automatic scorings. Files carry context
annotations from other tasks, which are ignored.

**Integrity.** On 29 September, 1,012 of 1,025 files matched
`SHA256SUMS.txt`. The 13 missing files, including all five sleep-staging
pre-fills, are being re-fetched. The analysis runs only when all 1,025
files verify.

## Disclosure of what was seen before freezing

During format checks on 29 September the following were seen:
- the folder layout;
- the header and a few lines of five annotation files;
- label vocabularies and **total label counts per task and setting**,
  pooled over scorers and recordings.

The pooled counts showed, for example, more hypopneas in semi-automatic
than in manual respiratory scorings. No per-scorer, per-recording,
agreement, consensus or algorithm statistic was computed. The pooled counts
are not an outcome of this protocol and will not be reported as evidence.

## Units and windows

- **Analysis window.** Epochs and events between that recording's "Lights
  off" and "Lights on" annotations, taken from the auto pre-fill.
- **Sleep stages.** 30-second epochs aligned on the recording onset; labels
  W, N1, N2, N3, R. Epochs labelled "?" by any compared scoring are dropped
  from that comparison.
- **Events.**
  - EEG arousals: "EEG arousal".
  - Respiratory events: obstructive, central and mixed apnea, hypopnea and
    central hypopnea, pooled for the primary analysis. RERA is excluded.
  - Limb movements: "Limb movement".
  - Each task uses only its own labels.
- **Event agreement.** Event-level F1 with one-to-one matching: events match
  when their intervals overlap, pairing the largest overlaps first.
- **Stage agreement.** Five-class Cohen's kappa.
- **Consensus reference.** Majority vote of the 12 scorings in a condition
  (at least 7 of 12). For stages the vote is per epoch, with ties left
  unlabelled and excluded. For events it is on a 0.1-second grid, with
  contiguous majority segments forming consensus events.
  Leave-one-scorer-out consensus uses the other 11 (at least 6 of 11).

## Measures (all fixed in advance)

**M1 Anchoring (primary).** For each task, scorer s and recording r:

ΔA(s, r) = agreement(semi-automatic(s, r), auto(r)) − agreement(manual(s, r), auto(r))

A positive value means assisted labels sit closer to the algorithm.

**M2 Reference inflation (primary).** For each recording r:
- Δauto(r) = agreement(auto, semi-automatic consensus) − agreement(auto,
  manual consensus).
- Δhuman(r) = the mean over s of agreement(manual(s), semi-automatic
  consensus without s) − agreement(manual(s), manual consensus without s).
- **DiD(r) = Δauto(r) − Δhuman(r).**

Interpretation:
- If assistance only made labels more accurate, independent human raters
  should gain about as much as the algorithm (DiD near 0).
- If assisted references moved toward the algorithm, the algorithm gains
  while independent raters do not (DiD > 0).

**M3 Where the agreement gain comes from (secondary).** Compare the
inter-scorer agreement gain on epochs or events where auto agrees with the
manual consensus against those where it disagrees.

**M4 Clinical indices (secondary, descriptive).** Arousal index,
respiratory event index and limb-movement index per hour of sleep, using
the task's fixed context sleep stages. Report the auto pre-fill's index
error against manual-consensus and semi-automatic-consensus indices.

**M5 Independent algorithm (secondary, sleep stages only).** YASA
(open-source) staging evaluated against both consensus references, as a
second independent rater.

## Inference

With five recordings per task, recording-level inference is limited.
- **Primary tests.** Exact two-sided sign tests (α = 0.05) across the 20
  recording-task units:
  - M1, using the recording-level mean of ΔA over the 12 scorers;
  - M2, using DiD(r).
- **Effect sizes.** Per-task means with 95% crossed-bootstrap intervals
  (10,000 resamples of scorers and recordings, seed 20260929). These are
  descriptive, because five recordings give unstable intervals.
- All four tasks and all measures are reported whatever their direction.
  Per-task results are secondary.

## Decision rules

**Write up as a positive finding** if both primary sign tests are
significant in the positive direction and at least one task has a mean
ΔA of 0.05 or more (kappa or F1 units).

**Write up as a null or mixed finding** if the primary tests are not
significant and the per-task intervals rule out effects of 0.05 or more.
A precise null is still informative for validation practice.

**Otherwise,** report the result as inconclusive at this sample size and do
not claim either conclusion.

## Execution rules

- Code is written test-first on synthetic data. The real data are run once,
  computing all pre-specified quantities together.
- A bug fix after the first real run is recorded as a dated amendment with
  both outputs kept.
- Outputs contain aggregate statistics only. PSG-IPA is open,
  de-identified data, but no per-epoch labels are written to Git.

## Operational clarifications (29 September, before any run)

Fixed while writing the code, before any agreement was computed:
- **Window.** An epoch is in the window when its midpoint lies between
  lights-off and lights-on. Events are clipped to the window; events wholly
  outside it are dropped.
- **Event F1 edge cases.** Two empty event lists count as F1 = 1. One empty
  list and one non-empty list give F1 = 0.
- **M3 agreement.** Mean pairwise percent agreement among the 12 scorings of
  a condition: over epochs for stages, over 0.1-second bins (event versus no
  event) for events. The disagreement set is where the auto pre-fill's label
  differs from the manual consensus label (epochs, or bins with a manual
  consensus decision).
- **M4 sleep time.** Epochs labelled N1, N2, N3 or R in the auto pre-fill's
  context stages within the window. For the sleep-stage task, the M4
  indices do not apply.

## M5 operational clarifications (29 September, before YASA was run)

Fixed after M1-M4 were computed, before any YASA output existed:
- **Software.** YASA 0.7.0, installed in an isolated environment
  (`outputs/envs/yasa`), with default model and settings and no metadata
  (per-subject age and sex are not in the dataset).
- **Channels.**
  - EEG "EEG C4-M1"; SN1 has no C4-M1, so its only central channel, "EEG
    Cz-M1", is used there.
  - EOG "EOG E1-M2"; EMG "EMG chin".
- **Alignment.** YASA's 30-second epochs from the recording start align with
  the annotation epochs. Comparisons use the same window and consensus
  references as M2.
- **Reported quantities.** Per recording:
  - YASA's kappa against the manual and the assisted consensus;
  - Δyasa = kappa(YASA, assisted consensus) − kappa(YASA, manual consensus),
    shown next to Δauto and Δhuman from M2.
- **Reading, descriptive only.** A Δyasa near or below zero while Δauto is
  positive fits a pull toward the specific pre-fill. A Δyasa similar to
  Δauto fits a general improvement of the reference.

## Resources

CPU only for M1-M4; YASA staging for M5 on 5 recordings. Data are 2.75 GB
(open). YASA is approved by the user (26 September).


---

# Amendment 002 (first amendment)

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


---

# Amendment 003 (second amendment: simulation)

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


---

# Amendment 004 (third amendment: audit and independent-rater checks)

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


---

# Amendment 005 (fourth amendment: checks requested by a pre-submission review)

# Assisted-scoring bias: amendment 005 (checks requested by the pre-submission review)

Date: 12 October 2026. Follows
[amendment 004](PSG_ASSIST_BIAS_AMENDMENT_004_2026-09-29.md) and the
[pre-submission review of 11-12 October](../psg_assist_bias_manuscript/review_2026-10-11/).
Config: [psg_assist_bias_005](../../config/preanalysis/psg_assist_bias_005_2026-10-12.json).

This amendment is written before any analysis below is computed.
- **Seen:**
  - all results of protocol 001 and amendments 002-004, including the
    per-recording clinical-index values of M4 in the committed protocol 001
    report;
  - the five review cards, which quote those results.
- **Not seen:** every quantity defined in Parts C1-C6 below. No model output
  was computed for this amendment.

All analyses are **secondary**. They add no decision rule for the primary
result. Part E fixes, before any computation, how their results change three
secondary claims of the manuscript.

## Part C: analyses on PSG-IPA

**C1 Adoption of rejected labels without selecting on the scored expert (all
four tasks).**
- **Why.** Amendment 002's R4 selected units where at least 10 of the 12
  manual scorings, including the scored expert's own, rejected the pre-fill's
  label. Selecting on the expert's own manual label makes a positive lift
  partly expected from regression to the mean, even without anchoring (review:
  methodology W3, Devil's Advocate MJ2). For events, R4 used 0.1-second bins,
  so keeping the pre-fill's event edges counted as adoption (review: domain
  W3).
- **Stages.** For expert s and recording r, the units are epochs where:
  - the pre-fill is labelled;
  - at least 9 of the other 11 experts' manual labels differ from the
    pre-fill's label.

  The lift is P(assisted label of s = pre-fill) minus P(manual label of s =
  pre-fill) over those units. An epoch counts for s only if s labelled it in
  both sessions.
- **Events (event level, not bins).** The units are pre-fill events.
  - A manual scoring rejects a pre-fill event if none of its events overlaps
    it in time.
  - A unit qualifies for expert s if at least 9 of the other 11 experts'
    manual scorings reject it.
  - The lift for s is P(s's assisted scoring overlaps the pre-fill event)
    minus P(s's manual scoring overlaps it).
- **Comparison row.** R4's own rule (at least 10 of 12, the scored expert
  included), recomputed at event level for the event tasks. This separates
  the effect of bins from the effect of the selection rule.
- **Reported:**
  - the mean per task over experts and recordings, with a crossed-bootstrap
    95% interval;
  - the mean over experts per recording-task unit;
  - an exact two-sided sign test over the 20 units;
  - the number of units per task.
- **Why the rule removes regression to the mean.** Suppose there is no
  anchoring, so that each expert's two sessions are exchangeable given the
  unit, and suppose experts label independently given the unit. Then
  selecting on the other experts' labels leaves s's manual and assisted
  labels equally likely to match the pre-fill. The residual assumption
  (conditional independence within a session) is stated with the result.
- *Prediction:*
  - the lift is positive in every task;
  - the sign test gives p < 0.05;
  - the lift is smaller than R4 for stages (+0.241).

**C2 Negative control: movement toward an algorithm the experts never saw
(sleep staging).**
- **Why.** Assistance always came in the later session. A shift between
  sessions toward algorithm-like or more typical scoring would also move
  experts toward a stager they never saw; anchoring on the pre-fill would not
  (review: methodology W1).
- **Units.** Epochs where the pre-fill and YASA are both labelled and their
  labels differ.
- **Measures, for each expert and recording:**
  - toward YASA: P(assisted = YASA) minus P(manual = YASA);
  - toward the pre-fill on the same epochs: P(assisted = pre-fill) minus
    P(manual = pre-fill).
- **Side-taking toward YASA.** Among these epochs, take those where both
  consensuses exist and differ. The measure is the share where the assisted
  consensus equals YASA, minus the share where the manual consensus does.
- **Reported:** the mean over the 60 expert-recording cells with a
  crossed-bootstrap interval, and the per-recording values.
- **Second stager.** The same measures are computed with the second stager
  of C5, if C5 is done.
- *Prediction:*
  - movement toward YASA is not positive (mean at or below 0);
  - movement toward the pre-fill on the same epochs is positive.
- **Limit.** The control cannot detect a shift toward conventions of this
  centre that only the pre-fill encodes.

**C3 The pre-fill's own gain on common support (sleep staging).**
- **Why.** The inclusion effect that lowered the independent raters' change
  may also raise the pre-fill's gain, and amendment 004 restricted only
  Δhuman and ΔYASA (review: Devil's Advocate MJ4).
- **Units.** Epochs where both 12-expert consensuses exist and the pre-fill
  is labelled.
- **Measures, in kappa and percent agreement, per recording and as means:**
  - Δauto on these epochs;
  - the DiD on common support, Δauto minus amendment 004's common-support
    Δhuman;
  - the session-free contrast on common support, Δauto minus ΔYASA (and minus
    the C5 stager's change, if C5 is done).
- *Prediction:*
  - Δauto on common support is positive in all five recordings;
  - the session-free contrast is positive in at least four of five.

**C4 Audits of contiguous blocks (sleep staging).**
- **Why.** Amendment 004's audit sampled single epochs. In practice the
  pre-fill would be withheld for contiguous blocks, which costs precision
  (review: Journal-Fit W1, methodology W5, perspective W3, domain W11, Devil's
  Advocate MJ6).
- **Kept from amendment 004 part B1:** the population, the targets (the
  pre-fill's agreement, YASA's agreement and their gap) and the designs D0,
  D1 and D2.
- **Blocks.** Consecutive, non-overlapping blocks of 60 epochs (30 minutes),
  starting at lights off; the last block of a recording may be shorter. A
  block counts as long as it holds at least one population epoch.
- **Audit draw.** Stratified by recording. Within each recording, a simple
  random sample of blocks without replacement, with max(1, round(f × number
  of blocks)) blocks.
- **Fractions:** f = 0.05, 0.1, 0.2, 0.3 and 0.5. The realized share of
  epochs is reported for each.
- **Estimators.** D1 and D2 are expansion estimators of the population mean,
  using the known population size, so they are unbiased by construction. Their
  exact design variance is that of stratified simple random sampling of
  clusters, computed from all blocks.
- **Reported:** the 95% half-widths for the three targets, and the smallest f
  at which D2's half-width for the gap falls below D0's bias for the gap
  (amendment 004: +0.059).
- *Prediction:*
  - every half-width is larger than its epoch-sampling value at the nearest
    fraction;
  - the smallest f that meets the gap criterion is larger than under epoch
    sampling (0.05).
- **Not redone.** Part B2's ranking probabilities, which treat epochs as
  independent. The manuscript states that they are optimistic.

**C5 A second independent stager (sleep staging).**
- **Why.** The comparison with an independent algorithm rests on one stager
  and five recordings (review: Devil's Advocate MJ5, methodology W4).
- **Stager.** The Greifswald Sleep Stage Classifier, GSSC (Hanna and Flöel,
  2023). It was trained on NSRR cohorts, not on data from this centre.
  - It runs in a separate environment under `outputs/envs/` with its default
    pretrained model.
  - It uses the same EEG and EOG channels as YASA: C4-M1 (Cz-M1 for SN1) and
    E1-M2.
- **Operational details.** Channel mapping, resampling and the version are
  fixed in the config before GSSC is run on PSG-IPA. An install check on
  synthetic or non-PSG-IPA data comes first.
- **Measures:**
  - kappa against both consensuses, and ΔGSSC;
  - ΔGSSC on common support;
  - the pre-fill's lead over GSSC against each consensus;
  - the C2 negative control with GSSC's labels.
- *Prediction:*
  - mean ΔGSSC is negative;
  - the pre-fill's lead over GSSC is larger against the assisted consensus
    than against the manual consensus.
- **Fallback.** If GSSC cannot be installed or run on these channels, C5 is
  reported as not done, with the reason, and no other stager is substituted.

**C6 Event consensus with the rules' minimum durations (event tasks).**
- **Why.** Consensus events are built from 0.1-second bins with no minimum
  duration, so fragments shorter than the scoring rules allow enter the
  inflation measure (review: domain W4).
- **Variant.** Consensus events are formed as before. Those shorter than the
  rule's minimum are then dropped: 3 s for arousals, 10 s for respiratory
  events and 0.5 s for limb movements.
- **Reported:** M2 (Δauto, Δhuman and the DiD) for the three event tasks,
  per unit and per task, and a sign test over the 15 event units.
- *Prediction:*
  - the DiD stays positive in every event task's mean;
  - it is positive in at least 13 of the 15 event units.

## Part D: verification by people

These are checks of the work, not analyses of new quantities. Each is
reported in the manuscript with who did it and what it found.

**D1 Blind second coding of the FDA summaries.**
- **Who.** A co-author who has not seen the AI's codes or the checked codes
  for the summaries they code.
- **Task.** From each of the 22 summaries with performance data, code three
  fields with the existing definitions:
  - the reference type;
  - blinding to the device's output;
  - whether the summary says that the reference scorers worked from automatic
    pre-scoring by any software.
- **Coding sheet.** It lists the K number, the device and the summary's link,
  with blank fields and the definitions.
- **Reported:**
  - raw agreement and Cohen's kappa per field, against the reconciled coding;
  - every disagreement, resolved by a third author reading the source;
  - any resulting change to the manuscript's counts.
- The field-level agreement that the first check recorded (11 October) is
  reported as well.

**D2 Independent re-implementation and clean re-run.**
- **Re-implementation.** A person who has not read the analysis code
  re-implements, from the text of protocol 001 and its operational
  clarifications, M1 (anchoring) and M2 (inflation) for sleep staging. They
  report per-recording values.
  - Agreement within 0.001 of the reported values is reported as verified.
  - A larger discrepancy is investigated, and its cause and any correction are
    reported.
- **Clean re-run.** A person re-runs the whole pipeline from a clean copy of
  the repository on freshly downloaded PSG-IPA files and confirms that
  `generated/values.tex` is reproduced exactly.

**D3 Library cross-check.** On the real staging pairs, the study's kappa is
compared with scikit-learn's `cohen_kappa_score`, and its sign tests with
SciPy's `binomtest`. Both run in a separate environment.

## Part E: how the results change the text (fixed now)

- **Title and abstract.** Associational wording ("assisted references were
  closer to the assisting algorithm than the same experts' earlier unassisted
  references"), whatever the results. The estimand, agreement with the same
  experts' unassisted judgment, is stated in the abstract and Methods.
- **C1.** If the sign test gives p ≥ 0.05, or any task's mean lift is 0 or
  below:
  - the Discussion no longer presents the adoption of rejected labels as
    favouring anchoring over correction;
  - C1 replaces R4 in the main text.

  Otherwise C1's values replace R4's in the main text, with the residual
  assumption stated, and R4 moves to the supplement.
- **C2.**
  - If mean movement toward YASA is above 0 with an interval excluding 0, the
    manuscript says that experts also moved toward a stager they never saw,
    so the shift is not specific to the pre-fill.
  - Otherwise it reports the control as consistent with a shift specific to
    the pre-fill, within C2's stated limit.
- **C4.**
  - If some f in the grid meets the gap criterion, the abstract and the
    recommendation cite that block-audit share.
  - Otherwise they say that block audits of up to half the epochs did not
    reach the required precision in this dataset.
  - The epoch-level 5-10% figure leaves the abstract in either case.
- **C5.** If C5 is done, statements about an independent algorithm report
  both stagers, each with its per-recording range, and "more than doubled"
  is dropped.

## Operational clarifications (12 October, before any run)

These were fixed while the code (`careport.psg_assist_checks`) was written and tested on synthetic data. No PSG-IPA
quantity of this amendment had been computed.
- **C1, stages.**
  - Another expert's manual label counts as rejecting only if it is present and differs from the pre-fill's label.
  - Each recording-task unit's value is the mean over the experts who have qualifying epochs.
  - The task summary is amendment 002's: the mean of the available expert-by-recording cells, with a
    crossed-bootstrap interval (2,000 resamples, seed 20261012).
- **C1, events.**
  - The pre-fill's events are taken after clipping to the window.
  - "Overlaps" means an intersection of positive length with any event of the scoring.
- **C2.**
  - Units are epochs where the pre-fill and the stager both give a label and the labels differ.
  - An expert contributes an epoch only if they labelled it in both sessions.
- **C3.**
  - Δhuman on common support is recomputed per recording as amendment 004 computed A1 (mean over experts).
  - The session-free contrast is computed on the joint common support: epochs where the pre-fill and the stager
    are both labelled and both consensuses exist.
- **C4.**
  - The population and the units are amendment 004's B1.
  - Blocks are counted from the first in-window epoch of the pre-fill.
  - The number of blocks drawn uses Python's `round` (half to even), as B1 did, with at least one block and at most
    all of them.
  - D0's bias for the gap is recomputed as in B1, so it should reproduce +0.059.
- **C6.**
  - Only the consensus events, full and leave-one-out, are filtered; the scorings and the pre-fill are not.
  - Each unit's DiD is Δauto minus the mean Δhuman, and the sign test runs over the 15 event units.
- **YASA labels.** They are regenerated with the M5 code into `outputs/psg_assist_bias_005/`.
- **GSSC.** Its operational details are fixed in a further dated note after the install check.

## Note 1, 12 October 2026: GSSC operational details (after the install check, before any PSG-IPA run)

- **Environment.** `outputs/envs/gssc` with Python 3.11.9, gssc 0.0.9 (pip), MNE 1.13.2 and PyTorch 2.5.1 on the
  CPU. PyTorch 2.6 and later refuse to load GSSC's saved networks (`torch.load` defaults to `weights_only=True`), so
  PyTorch is pinned to the last earlier release instead of changing how the networks load.
- **Call** (`careport.psg_assist_bias_gssc`):
  - the EDF is read with `mne.io.read_raw_edf(include=[EEG, EOG], preload=True)`;
  - inference uses `EEGInfer(use_cuda=False).mne_infer(raw, eeg=[EEG], eog=[EOG], eeg_drop=True, eog_drop=True,
    filter=True)`.

  These are the package's default networks and settings. GSSC filters to 0.3-30 Hz, resamples to 2,560 samples
  per 30-second epoch, and drops a trailing partial epoch.
- **Channels.** The M5 rule's EEG and EOG: C4-M1 (Cz-M1 for SN1) and E1-M2.
- **Labels.** Codes 0-4 become W, N1, N2, N3 and R. Epoch i starts 30·i s after the recording start; the run
  stops if GSSC's first epoch does not start at 0 s. Epochs then follow the M5 window rule, as YASA's do.
- **Install check (synthetic noise, not PSG-IPA).** On 10 minutes of noise in one EEG and one EOG channel, GSSC
  ran on the CPU and returned 19 epochs starting at 0 s, all Wake, identical on a second run. Its networks are
  set to evaluation mode, so inference is deterministic.

## Execution and reporting

- Every analysis is reported whatever its direction, and failed predictions
  are stated as such.
- The code is written test-first on synthetic data, and the real data are run
  once. Any later fix gets a dated note, and both outputs are kept.
- **YASA labels.** They are regenerated with the M5 code and must reproduce
  the M5 kappas within 10⁻⁹, or the run stops.
- **What goes to Git.** Aggregate outputs only. YASA and GSSC labels, and all
  per-epoch values, stay in the ignored `outputs/`.
- **New environments.** GSSC (with PyTorch for the CPU) and the scikit-learn
  and SciPy cross-check each run in their own environment under
  `outputs/envs/`.


---

# Amendment 006 (fifth amendment: derived quantities asked for by the round-2 review)

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
