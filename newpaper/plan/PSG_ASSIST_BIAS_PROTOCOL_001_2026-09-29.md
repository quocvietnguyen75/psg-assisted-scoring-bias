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
