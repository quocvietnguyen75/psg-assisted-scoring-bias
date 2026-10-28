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
