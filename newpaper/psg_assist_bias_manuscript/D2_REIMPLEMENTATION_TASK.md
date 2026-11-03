# Task D2: re-implement the primary staging measures without reading the study's code

**Status, 28 October 2026.** Part one is done. The staging measures (received 24 October) and, at the second simulated
review's request, the anchoring measure for the three event tasks (received 27 October) all agree with the study's
values to floating-point rounding; the manuscript reports this in the statement on generative AI and the Supplementary
Methods. Part two, the clean re-run, was done on 29 October from a fresh clone of the repository with freshly
downloaded data, in both tiers: every generated value and both stager label files were reproduced (RESULT: PASS).

This is part D2 of [amendment 005](../plan/PSG_ASSIST_BIAS_AMENDMENT_005_2026-10-12.md). Reviewers asked for a human
check of the analysis code, which an AI assistant wrote. The check counts only if the person doing it has **not read
the study's code** (`src/careport/`) or its result reports before sending their numbers.

## What to compute

Compute anchoring (M1) and inflation (M2) for the **sleep-staging task only**, for each of the five recordings
(SN1 to SN5), from the definitions in protocol 001. That protocol is in Supplementary File S1, under "Units and
windows", "Measures", and the two sets of operational clarifications. The main points are below, but the protocol text
decides.

- **Data.** PSG-IPA 1.0.0 from PhysioNet (https://doi.org/10.13026/ESX0-NW71), folder `Sleep_stages/Annotations/`:
  - the pre-fill `auto/SN<r>_SleepStages_auto.txt`;
  - 12 manual scorings `manual/SN<r>_SleepStages_manual_scorer<s>.txt`;
  - 12 assisted scorings `semiauto/SN<r>_SleepStages_semiauto_scorer<s>.txt`.
- **Window.** Only epochs whose midpoint lies between the "Lights off" and "Lights on" annotations of the pre-fill
  file. Epochs are 30 seconds long and aligned on the recording onset.
- **Labels.** W, N1, N2, N3 and R. Any other label means the epoch is unscored, and unscored epochs are dropped from
  each pairwise comparison.
- **Agreement.** Five-class Cohen's kappa.
- **Consensus.** An epoch takes the label chosen by at least 7 of the 12 experts and has no consensus otherwise.
  Leave-one-out consensuses of the other 11 experts need at least 6 of 11.
- **M1, anchoring.** For each expert, kappa(assisted, pre-fill) minus kappa(manual, pre-fill). Report the mean over
  the 12 experts for each recording.
- **M2, inflation.**
  - Δauto is kappa(pre-fill, assisted consensus) minus kappa(pre-fill, manual consensus).
  - Δhuman is the mean over experts of kappa(expert's manual scoring, the other 11 experts' assisted consensus) minus
    kappa(expert's manual scoring, the other 11 experts' manual consensus).
  - DiD is Δauto minus Δhuman.

  Report Δauto, Δhuman and DiD for each recording.

## What to send

A table of the five recordings with mean M1, Δauto, Δhuman and DiD (three decimals), your code, and one line saying
that you did not read the study's code or reports first. Send it to the corresponding author. The comparison with the
study's values is then reported in the paper: agreement within 0.001 counts as verified, and any larger difference is
investigated and reported with its cause.

Any language is fine. Python with pandas or plain loops, or R, will do. Expect about a day.

## Part two: a clean re-run (a different person, or the same one afterwards)

The repository is `psg-assisted-scoring-bias` on the corresponding author's GitHub account (private until
submission; you will be added as a collaborator). From a fresh clone and freshly downloaded PSG-IPA files:
1. download PSG-IPA 1.0.0 in full (about 2.6 GB) and set `PSG_IPA_ROOT` to the folder that holds `SHA256SUMS.txt`;
2. follow the repository's README, tier A: run protocol 001 and amendments 002 to 005 into `newpaper/rerun/`, copy
   the three environment-dependent reports, and build the values with
   `python -m careport.psg_assist_manuscript --reports newpaper/rerun --out newpaper/rerun/manuscript`;
3. if you can build the two pinned environments (`envs/`), also do tier B (the YASA and GSSC stagers and the
   library cross-check);
4. run `python tools/compare_rerun.py` and send its complete output, your Python version and operating system,
   and for tier B the `pip list` of each environment, to the corresponding author. `RESULT: PASS` means that
   `generated/values.tex` was reproduced exactly.
