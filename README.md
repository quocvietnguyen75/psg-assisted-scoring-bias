# Assisted-scoring bias in sleep-scoring references: code, records and manuscript

Analysis code, dated analysis plans, aggregate results and the manuscript source of the study *Bias toward the assisting algorithm in polysomnography reference standards built from edited automatic pre-scoring* (Quoc Viet Nguyen, Duc Hoai Anh Nguyen, Phuc Tai Duong, Dzung Van Dinh, Nam S. Vo, Zengchang Qin; manuscript prepared for the *Journal of Sleep Research*, 2026; preprint link to be added).

The data are **PSG-IPA 1.0.0** (PhysioNet, CC BY 4.0: https://doi.org/10.13026/ESX0-NW71). This repository does not
redistribute them. Every number in the manuscript is generated from the aggregate reports in this repository by the
code in this repository; nothing is typed by hand.

## Layout

| Path | Content |
|---|---|
| `src/careport/psg_assist_*.py` | The analysis code (standard library only, except the two stager runners and the library cross-check, which need the environments below) |
| `tests/test_psg_assist_*.py` | Synthetic unit tests of every module |
| `config/preanalysis/psg_assist_bias_00*.json` | The frozen configuration of the protocol and each amendment |
| `newpaper/plan/PSG_ASSIST_BIAS_*.md` | Protocol 001 and amendments 002 to 006, as written before each analysis |
| `newpaper/research_selection_2026-09-26_novelty/` | The committed aggregate reports (JSON and CSV), the results notes, and the records of the independent re-implementation (D2) |
| `newpaper/psg_assist_bias_validation_practice_2026-09-29/` | The review of FDA 510(k) summaries: coding (`DEVICES.csv`), the blind second coding (`D1_*`), reconciliation and search records |
| `newpaper/psg_assist_bias_litreview_2026-09-29/` | The literature review behind the Introduction and Discussion |
| `newpaper/psg_assist_bias_manuscript/` | `main.tex`, `supplement.tex`, `references.bib`, the generated values, tables and figures, the build script, Supplementary File S1 and the STARD checklist |
| `outputs/psg_assist_bias_005/` | The per-epoch labels of the two independent stagers (YASA, GSSC) on the five staging recordings, as used by amendments 004 and 005 |
| `envs/` | Pinned requirements for the stager environments |
| `tools/compare_rerun.py` | Compares a re-run with the committed reports and values |
| `PROVENANCE.md` | Source commit of this snapshot and the private materials left out |

## Reproducing the results

The pipeline is deterministic (fixed seeds, standard-library arithmetic), so a re-run should reproduce the manuscript
values byte for byte after line-ending normalisation and the committed reports to the last floating-point bit (their
`frozen_at` field is the plan's freeze date, not a run time; see "On determinism" below for the one source of
last-bit differences). Two tiers: tier A needs Python only; tier B adds the stager environments.

### 1. Data

Download PSG-IPA 1.0.0 in full (about 2.6 GB; the analysis verifies all 1,025 files against `SHA256SUMS.txt`
before it runs), for example

```
wget -r -N -c -np https://physionet.org/files/psg-ipa/1.0.0/
```

or from PhysioNet's public mirror `https://physionet-open.s3.amazonaws.com/psg-ipa/1.0.0/`. Point the environment
variable `PSG_IPA_ROOT` at the folder that holds `SHA256SUMS.txt`.

### 2. Tier A: the analyses (Python 3.10 or newer, standard library; matplotlib for the figures)

PowerShell, from the repository root (bash: `export PSG_IPA_ROOT=...`, `export PYTHONPATH=src`, `mkdir -p`, `cp`):

```powershell
$env:PSG_IPA_ROOT = 'D:/data/psg-ipa/1.0.0'
$env:PYTHONPATH = 'src'
$c1 = 'config/preanalysis/psg_assist_bias_001_2026-09-29.json'
New-Item -ItemType Directory -Force newpaper/rerun/sim | Out-Null

python -m careport.psg_assist_bias --config $c1 --output newpaper/rerun/psg_assist_bias_001_report.json
python -m careport.psg_assist_mechanisms --config config/preanalysis/psg_assist_bias_002_2026-09-29.json --base-config $c1 --output newpaper/rerun/psg_assist_bias_002_report.json
python -m careport.psg_assist_simulation --config config/preanalysis/psg_assist_bias_003_2026-09-29.json --base-config $c1 --output-dir newpaper/rerun/sim
Copy-Item newpaper/rerun/sim/simulation.json newpaper/rerun/psg_assist_bias_003_simulation.json
Copy-Item newpaper/rerun/sim/grid.csv newpaper/rerun/psg_assist_bias_003_grid.csv
python -m careport.psg_assist_remedy --config config/preanalysis/psg_assist_bias_004_2026-09-29.json --base-config $c1 --stager-labels outputs/psg_assist_bias_005/yasa_labels.json --output newpaper/rerun/psg_assist_bias_004_report.json
python -m careport.psg_assist_checks --config config/preanalysis/psg_assist_bias_005_2026-10-12.json --base-config $c1 --yasa-labels outputs/psg_assist_bias_005/yasa_labels.json --gssc-labels outputs/psg_assist_bias_005/gssc_labels.json --output newpaper/rerun/psg_assist_bias_005_report.json
```

Three reports need the environments of tier B (the YASA report, the exploratory ranking and the library
cross-check). In tier A, copy the committed ones so that the manuscript values can be built:

```powershell
Copy-Item newpaper/research_selection_2026-09-26_novelty/psg_assist_bias_001_m5_yasa.json, newpaper/research_selection_2026-09-26_novelty/psg_assist_bias_001_exploratory_ranking.json, newpaper/research_selection_2026-09-26_novelty/psg_assist_bias_005_crosscheck.json newpaper/rerun/
```

Then build the manuscript values from the re-run and compare:

```powershell
python -m pip install matplotlib
python -m careport.psg_assist_manuscript --reports newpaper/rerun --out newpaper/rerun/manuscript
python tools/compare_rerun.py
```

`compare_rerun.py` prints a SHA-256 of every file, says whether `values.tex` is identical and whether each report is
byte-identical, identical apart from its `frozen_at` field, or equal within a tolerance, and ends with
`RESULT: PASS` or `RESULT: FAIL`.

On determinism: Python randomises the hash of strings in every process, which changes the order in which the kappa
computation sums over the stage categories, so sleep-stage kappa quantities in the reports differ between processes at
the last floating-point bit (about 1e-16), never in any reported value. The comparison therefore treats numeric
differences up to 1e-9 (the study's own cache-check tolerance) as a match and still requires `values.tex` to be
identical. Setting `PYTHONHASHSEED=0` before the commands makes runs bitwise reproducible among themselves.

### 3. Tier B: the stagers and the library cross-check

The stagers read the five staging EDF recordings. Create the two environments with Python 3.11 and the pinned
versions in `envs/` (the scikit-learn and SciPy version strings are printed in the supplement, so other versions
make `values.tex` differ in those two strings):

```powershell
python -m venv envs/yasa
envs/yasa/Scripts/python -m pip install -r envs/yasa-requirements.txt
python -m venv envs/gssc
envs/gssc/Scripts/python -m pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu
envs/gssc/Scripts/python -m pip install -r envs/gssc-requirements.txt
```

Then, with `PSG_IPA_ROOT` and `PYTHONPATH` set as above:

```powershell
envs/yasa/Scripts/python -m careport.psg_assist_bias_yasa --config $c1 --output newpaper/rerun/psg_assist_bias_001_m5_yasa.json --ranking newpaper/rerun/psg_assist_bias_001_exploratory_ranking.json
envs/yasa/Scripts/python -m careport.psg_assist_bias_yasa --config $c1 --output newpaper/rerun/labels/yasa_labels.json --cache
envs/yasa/Scripts/python -m careport.psg_assist_crosscheck --base-config $c1 --output newpaper/rerun/psg_assist_bias_005_crosscheck.json
envs/gssc/Scripts/python -m careport.psg_assist_bias_gssc --config $c1 --output newpaper/rerun/labels/gssc_labels.json
```

If the regenerated label files are identical to the committed ones (the comparison script says so), amendments
004 and 005 need no second run; otherwise run them again with the regenerated files and report the differences.
Rebuild the values and run the comparison as in tier A.

### 4. The manuscript PDFs

`newpaper/psg_assist_bias_manuscript/build.ps1` regenerates the values, tables and figures from the committed
reports and builds `supplement.pdf` and `main.pdf` with pdfLaTeX and BibTeX (MiKTeX or TeX Live). `main.tex`
reads the supplementary table numbers from `generated/supplement_refs.tex`, which the build writes from
`supplement.aux`, so the supplement is built first.

## Unit tests

```powershell
$env:PYTHONPATH = 'src'
python -m unittest discover -s tests -v
```

The tests are synthetic and need no data.

## The clean re-run of amendment 005, part D2

The study's plan asks a person who did not write the code to re-run the whole pipeline from a fresh copy of this
repository on freshly downloaded PSG-IPA files and to confirm that `generated/values.tex` is reproduced exactly.
To do it: clone this repository into a new folder, follow tier A (and tier B if the environments can be built),
and send back the complete output of `tools/compare_rerun.py`, the Python version, the operating system, and for
tier B the output of `pip list` in each environment. The manuscript reports the result in the statement on
generative AI and in the Supplementary Methods.

## Provenance and licence

`PROVENANCE.md` names the private-repository commit this snapshot was built from and the materials left out
(submission documents, internal planning notes, the simulated pre-submission reviews, and the two blind coders'
workbooks, whose document properties carry personal identifiers; their SHA-256 are in the D1 record). The code and
documents here are released under the MIT License (`LICENSE`). PSG-IPA is distributed by PhysioNet under CC BY 4.0;
cite Alvarez-Estevez D. PSG-IPA: a polysomnographic inter-scorer performance assessment database (version 1.0.0).
PhysioNet, 2026, doi:10.13026/ESX0-NW71, and Goldberger AL et al. PhysioBank, PhysioToolkit, and PhysioNet.
Circulation 2000;101(23):e215-e220.
