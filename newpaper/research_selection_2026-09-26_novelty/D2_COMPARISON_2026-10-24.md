# D2 re-implementation: comparison with the study's values (24 October 2026)

Amendment 005, part D2, first half: an independent re-implementation of M1 (anchoring) and M2 (inflation) for
sleep staging, from the text of protocol 001, by someone who had not read the analysis code. Values within 0.001 of
the study's are reported as verified.

## What was received

Duc Hoai Anh Nguyen (D.H.A.N.) sent a GitHub repository on 24 October 2026 (`hankleadngoo/PSG_manuscript_JSR_overleaf_2026-10-19`,
single commit of 23 October 2026, 17:21 UTC) containing the 19 October Overleaf package and a folder
`d2_verification/`: `d2.py` (standard library only), `test_d2.py` (five synthetic tests, including 50 random kappa
pairs against scikit-learn and a fixture with known M1, Δauto, Δhuman and DiD), `README_VI.md`, `REPORT_VI.md`, and two
runs of 22 October 2026 with `results_full.csv`, `results_3dp.csv`, `scorer_summary.csv` and `provenance.json`.
The folder is copied here as `d2_verification_dhan_2026-10-22/`. It contains aggregate values only; PSG-IPA is open data.

Provenance recorded by the implementation: PSG-IPA 1.0.0 downloaded from PhysioNet, all 125 staging annotation files
matching the published SHA-256 sums; window `lights_off <= epoch midpoint < lights_on` from the pre-fill file; 5,103
epochs in the windows (SN1 896, SN2 725, SN3 1,635, SN4 961, SN5 886); no unscored epochs in the windows; consensus
7 of 12 and leave-one-out 6 of 11; no epoch midpoint on a window boundary. Both runs gave identical values.

## Independence and AI assistance, as disclosed by the implementer

The analysis code (`src/careport/`) was not in the package and is not public, so the implementation could not have
read it. The implementer's own disclosure (REPORT_VI.md, translated): the implementation was done with the help of the
Codex coding assistant from the protocol text and the PSG-IPA annotations; the code did not read or use the study's
analysis code; in the conversation before the implementation the assistant had seen some result tables of the
manuscript; the implementer therefore declares the AI assistance and that exposure and does not call this a blind,
human-only check; no formula or data handling was adjusted to match the paper.

Two notes on our side. The task sheet asked for someone who had not read the result reports, but it was delivered
inside a package that contained the manuscript PDF, so that condition could not be met by anyone working from the
package. Amendment 005 asks for a person who has not read the analysis code; it does not exclude coding assistance.
The manuscript must describe the check as it was done: an independent re-implementation from the protocol text,
without access to the code, by a co-author using a different AI coding assistant, with synthetic tests against
scikit-learn.

## Comparison

Against `psg_assist_bias_001_report.json`, `tasks/Sleep_stages/recordings` (the frozen protocol 001 run of
29 September 2026), full precision.

| Recording | M1 (mean over 12 experts) | Δauto | Δhuman | DiD | Largest absolute difference |
|---|---|---|---|---|---|
| SN1 | 0.095 | 0.062 | −0.012 | 0.074 | 2.8e-17 |
| SN2 | 0.112 | 0.102 | −0.014 | 0.117 | 2.2e-16 |
| SN3 | 0.065 | 0.056 | −0.022 | 0.078 | 1.1e-16 |
| SN4 | 0.055 | 0.064 | −0.011 | 0.074 | 1.5e-16 |
| SN5 | 0.078 | 0.090 | −0.020 | 0.110 | 0 |

All 20 values agree within 2.3e-16, which is floating-point rounding. **Verified** under the 0.001 rule.

## Second half of D2

The clean re-run of the whole pipeline from a fresh copy of the repository waits for the curated public repository
that is built at submission; the Overleaf package does not contain the pipeline. The implementer noted this
correctly.

## Observation from the implementation's provenance

`semiauto/SN1_SleepStages_semiauto_scorer4.txt` has the same SHA-256 as `auto/SN1_SleepStages_auto.txt`: for SN1,
scorer 4's assisted staging is byte-identical to the pre-fill. Confirmed on the local copy; no other assisted
staging file is identical to its pre-fill. This fact is not yet mentioned in the manuscript's data description.
Any analysis that excludes or singles out this unit needs a dated amendment first.

## Extension to the event tasks (28 October 2026)

At the second simulated review's request, the implementer added M1 for the three event tasks; all 15 per-recording
values and the 36 per-expert means agree within 5.6e-17. See
[D2_EVENTS_COMPARISON_2026-10-28.md](D2_EVENTS_COMPARISON_2026-10-28.md) and `d2_verification_dhan_events_2026-10-27/`.
