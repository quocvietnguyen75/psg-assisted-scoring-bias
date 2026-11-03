# Clean re-run of the whole pipeline (amendment 005, D2, second half), 29 October 2026

Amendment 005, part D2, second half: a person re-runs the whole pipeline from a clean copy of the repository on
freshly downloaded PSG-IPA files and confirms that `generated/values.tex` is reproduced exactly. The repository is
the curated snapshot built on 28 October ([PUBLIC_SNAPSHOT_2026-10-28.md](../psg_assist_bias_manuscript/PUBLIC_SNAPSHOT_2026-10-28.md)),
pushed by the corresponding author as the private repository `quocvietnguyen75/psg-assisted-scoring-bias` the same
day, with the implementer added as a collaborator.

## What was received

`task2810_sleep.zip` (4,356 bytes, SHA-256 `35ba14d6135384431b42381ded8e0da6ac941740614f325e1ceec8382ba69095`),
downloaded by the user from the team chat into the workspace root on 29 October 2026. Its five files are copied
unchanged to `d2_clean_rerun_dhan_2026-10-29/`: `a_compare.log` (tier A), `b_compare.log` (tier B),
`environment.json`, `yasa_pip_list.log` and `gssc_pip_list.log`. The environment file and the package listings name
folders on the implementer's own drive; they stay as received in this private repository and are left out of the
public snapshot, where this note stands for them.

## Who, and from what

Duc Hoai Anh Nguyen (D.H.A.N.), from a fresh clone of commit `1b36299` of the repository (the commit the
corresponding author pushed on 28 October; this workspace's copy is at that commit with a clean tree), on a freshly
downloaded PSG-IPA 1.0.0 with all 1,025 files verified against the published checksums, on Windows (10.0.22621)
with Python 3.11.9 and `PYTHONHASHSEED=0`, as the repository's README asks. Mode "all": tier A (standard library
only) and tier B (the two stager environments rebuilt from the pinned requirements: yasa 0.7.0, mne 1.13.2,
numpy 2.4.6, scipy 1.17.1, scikit-learn 1.9.1, lightgbm 4.7.0; gssc 0.0.9, torch 2.5.1+cpu; pandas 3.1.0 and
antropy 0.2.3 where the requirements pin 3.0.6 and 0.2.2).

## Results

Both tiers end with `RESULT: PASS` from `tools/compare_rerun.py`.

| File | Tier A | Tier B |
|---|---|---|
| `generated/values.tex` | identical (1,090 values) | identical (1,090 values) |
| Protocol 001 report | 31 leaves differ, at most 1.1e-16 | same |
| YASA report (M5) | copied (byte-identical) | regenerated: 7 leaves differ, at most 2.2e-16 |
| Exploratory ranking | copied (byte-identical) | regenerated: 1 leaf differs, 1.1e-16 |
| Amendment 002 report | 3 leaves differ, at most 5.6e-17 | same |
| Amendment 003 simulation and grid | 2 leaves differ, at most 1.1e-16; grid identical | same |
| Amendment 004 report | 6 leaves differ, at most 2.2e-16 | same |
| Amendment 005 report | 41 leaves differ, at most 2.2e-16 | same |
| Library cross-check | copied (byte-identical) | regenerated: byte-identical |
| YASA labels, 5,103 epochs | committed file used | regenerated: 0 epochs differ |
| GSSC labels, 5,103 epochs | committed file used | regenerated: 0 epochs differ |

## Verification on our side

- The "committed" SHA-256 values printed in his logs equal the normalised hashes of the files in the repository as
  built here (`values.tex`, the protocol 001 report, the YASA report, the cross-check, the grid and both label
  files), so the comparison was made against the same files that this workspace holds.
- The leaf differences are of the kind and size seen in the corresponding author's dry run of 28 October: all are
  sleep-stage kappa quantities, none exceeds 2.2e-16, and the cause is the order of the expected-agreement sum over
  the stage categories under Python's per-process hash randomisation (verified on 28 October by running protocol 001
  twice under different hash seeds). No reported value changes; `values.tex` is byte-identical after line-ending
  normalisation in both tiers.
- The two stager label files were regenerated epoch for epoch, including GSSC on the CPU, so amendments 004 and 005
  needed no second run.

## Conclusion

Amendment 005 D2, second half, is met: from a fresh copy of the repository and freshly downloaded data, every
generated value was reproduced exactly, and so were the stager labels. Reported on 29 October in the statement on
generative AI and in the Supplementary Methods (Software and verification). The repository stays private until
submission, when its URL fills the Data availability statement; the received logs stay in the private records.
