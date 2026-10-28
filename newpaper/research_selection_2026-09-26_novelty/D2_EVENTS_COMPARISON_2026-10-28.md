# D2 re-implementation, extended to the event tasks: comparison with the study's values (28 October 2026)

Amendment 005, part D2, covered M1 (anchoring) and M2 (inflation) for sleep staging; that part was verified on
24 October ([D2_COMPARISON_2026-10-24.md](D2_COMPARISON_2026-10-24.md)). The second simulated review (26-27 October,
item R13) asked for an independent check of the event-level F1 matching, which carries 15 of the 20 primary units. The
corresponding author asked the D2 implementer to add M1 for the three event tasks from the protocol text. This
extension is outside the wording of amendment 005 D2. It verifies values that were already reported and changes no
reported quantity, so no amendment was written; the 0.001 rule of amendment 005 is reused as the criterion, as the
implementer's own notes state. Values within 0.001 of the study's are reported as verified.

## What was received

Duc Hoai Anh Nguyen (D.H.A.N.) pushed a second commit to the same public GitHub repository
(`hankleadngoo/PSG_manuscript_JSR_overleaf_2026-10-19`, commit `782eef5`, 27 October 2026, 23:23 UTC+07:00, "Add M1
verification for arousal, respiratory and limb events"). It adds 40 files under `d2_verification/` and extends its
`README_VI.md`; the manuscript files in the repository are unchanged. The new files and the updated README are copied
here as `d2_verification_dhan_events_2026-10-27/`:

- `event_m1.py`, the shared implementation (standard library only). It reuses `d2.py` from the staging part for reading
  the annotation files, the lights window and downloads; the `d2.py` it hashed (SHA-256 `2be342e3…`) is the copy
  already in `d2_verification_dhan_2026-10-22/`.
- `arousals/`, `respiratory/`, `limb/`: a wrapper `run.py`, six synthetic tests (labels and clipping, empty and touching
  intervals, greedy matching against a maximum-cardinality counter-example, tie recording, M1 with hand-computed
  answers, invalid input), a README and a report, and one run of 27 October 2026, 16:03 UTC, with `results_full.csv`,
  `results_3dp.csv`, `scorer_summary.csv` (60 expert-recording cells: both F1 values, M1, event counts, matched pairs,
  tie conflicts), `task_summary.csv` and `provenance.json`.
- `test_event_m1.py`, an end-to-end synthetic test over the three tasks; `download_events.py`; the 15-row summary
  `event_m1_results_3dp.csv`; an implementation note and a hand-over report in Vietnamese.

The folder holds aggregate values only; PSG-IPA is open data.

Provenance recorded by the implementation: PSG-IPA 1.0.0 annotation files for the three tasks (375 files) downloaded
from PhysioNet's public S3 mirror after the direct route timed out, every file matching the published SHA-256
manifest; window [lights off, lights on) from each task's own pre-fill file, events clipped to the window; labels
exactly those of the frozen configuration (EEG arousal; Obstructive apnea, Central apnea, Mixed apnea, Hypopnea, Central
hypopnea; Limb movement); event F1 with one-to-one matching, largest positive overlaps first, touching intervals not
matched, two empty lists F1 = 1, one empty list F1 = 0; M1 = mean over the 12 experts of F1(assisted, pre-fill) minus
F1(manual, pre-fill). Twenty-four tests passed before the real runs (5 staging, 18 event, 1 end-to-end). Python 3.12.6.

## Independence and AI assistance, as disclosed by the implementer

The same conditions as the staging part: implemented with the Codex coding assistant from protocol 001 as printed in
Supplementary File S1 (pages 3-4); the study's analysis code (`src/careport/`) was not in the package and is not public,
so it could not have been read; the implementer declares the AI assistance and that the assistant had seen manuscript
results beforehand, and does not call this a blind, human-only check; no formula or data handling was adjusted to match
the paper. What the assistant could have seen: the 19 October package, whose `generated/values.tex` holds, for each
event task, the mean M1, its interval, the largest and smallest per-recording M1 (three decimals) and the number of
experts with a positive M1; its Figure 2(a) showed the five per-recording values per task as dots, without numbers.
Table S15, which lists them numerically, was added on 27 October, after these runs.

## Comparison

Against `psg_assist_bias_001_report.json`, `tasks/<task>/M1_anchoring` (the frozen protocol 001 run of 29 September
2026), at full precision, by `compare_d2_events_2026-10-28.py` (kept here; it reads the frozen report and the received
CSV files).

| Task | Recording | M1 (study) | M1 (re-implementation) | Absolute difference |
|---|---|---|---|---|
| EEG arousals | SN1 | −0.002067 | −0.002067 | 0 |
| EEG arousals | SN2 | 0.162081 | 0.162081 | 0 |
| EEG arousals | SN3 | 0.072512 | 0.072512 | 0 |
| EEG arousals | SN4 | 0.022484 | 0.022484 | 0 |
| EEG arousals | SN5 | 0.074840 | 0.074840 | 0 |
| Respiratory events | SN1 | 0.097913 | 0.097913 | 0 |
| Respiratory events | SN2 | 0.108502 | 0.108502 | 0 |
| Respiratory events | SN3 | 0.037665 | 0.037665 | 0 |
| Respiratory events | SN4 | 0.194241 | 0.194241 | 2.8e-17 |
| Respiratory events | SN5 | 0.208161 | 0.208161 | 5.6e-17 |
| Limb movements | SN1 | 0.148641 | 0.148641 | 0 |
| Limb movements | SN2 | 0.117754 | 0.117754 | 0 |
| Limb movements | SN3 | 0.062687 | 0.062687 | 0 |
| Limb movements | SN4 | 0.054954 | 0.054954 | 0 |
| Limb movements | SN5 | 0.131565 | 0.131565 | 5.6e-17 |

Task means (study, re-implementation): arousals 0.065970 and 0.065970 (difference 1.4e-17); respiratory 0.129296 and
0.129296 (0); limb movements 0.103120 and 0.103120 (4.2e-17). The 36 per-expert means (12 experts, three tasks; the
entries of Table S16 for these tasks), computed from the received `scorer_summary.csv` files, equal the study's
`scorer_means` exactly. Positive recordings: 4 of 5 (arousals), 5 of 5, 5 of 5, as in the study.

All 15 per-recording values, the 3 task means and the 36 per-expert means agree within 5.6e-17, which is floating-point
rounding. **Verified** under the 0.001 rule. With the staging part, 35 per-recording values are verified.

## What the check does and does not test

- It exercises the event F1 matching written from the protocol text alone: the protocol's rule (one-to-one matching of
  overlapping events, largest overlaps first; touching intervals do not overlap; the empty-list conventions) sufficed to
  reproduce the values.
- The protocol does not fix the order among candidate pairs with equal overlap. Both implementations sort the candidate
  pairs by overlap and then by the index of the events in onset order, with the expert's scoring as the first list, so
  equal-overlap ties resolve the same way in both by construction. The implementation counted candidate-pair tie
  conflicts: 2 (arousals), 14 (respiratory events) and 749 (limb movements), over the 120 comparisons of each task. The
  agreement therefore does not test the tie convention; a different convention could change match counts where such
  ties occur. The supplement states this.
- Not re-implemented: the event consensus on the 0.1-second grid and everything downstream of it (the event-task
  Δauto, Δhuman, DiD and side-taking), M3 to M5, the audit emulation, the simulation and the stager comparisons. These
  rest on the analysis code's synthetic tests; D3 covers Cohen's kappa and the exact sign tests against scikit-learn
  and SciPy.

## Second half of D2

Unchanged: the clean re-run of the whole pipeline waits for the curated public repository built at submission. The
implementer's note says so.

## Repository status

On 28 October the repository was still public (it was cloned without credentials) and still holds the 19 October
package, including the suggested-reviewer list. The request to make it private stands.
