"""Assemble Supplementary File S1: the dated analysis plans, verbatim, with their provenance.

Run from the repository root:  python newpaper/psg_assist_bias_manuscript/make_supplementary_s1.py
"""
import hashlib
import subprocess
from pathlib import Path

PLANS = [
    ("Protocol 001", "newpaper/plan/PSG_ASSIST_BIAS_PROTOCOL_001_2026-09-29.md"),
    ("Amendment 002 (first amendment)", "newpaper/plan/PSG_ASSIST_BIAS_AMENDMENT_002_2026-09-29.md"),
    ("Amendment 003 (second amendment: simulation)", "newpaper/plan/PSG_ASSIST_BIAS_AMENDMENT_003_2026-09-29.md"),
    ("Amendment 004 (third amendment: audit and independent-rater checks)",
     "newpaper/plan/PSG_ASSIST_BIAS_AMENDMENT_004_2026-09-29.md"),
    ("Amendment 005 (fourth amendment: checks requested by a pre-submission review)",
     "newpaper/plan/PSG_ASSIST_BIAS_AMENDMENT_005_2026-10-12.md"),
    ("Amendment 006 (fifth amendment: derived quantities asked for by the round-2 review)",
     "newpaper/plan/PSG_ASSIST_BIAS_AMENDMENT_006_2026-10-27.md"),
]

HEADER = """# Supplementary File S1: analysis plans

This file reproduces, verbatim, the protocol and the five amendments under which every analysis in the article was
run or, for the fifth, reported. Plan codes (M1, R3, A2, C1 and so on) are mapped to the names used in the article in
Supplementary Table S1.

## Reading notes

The plans are reproduced exactly as they were written, so that their SHA-256 hashes below can be checked against the
study's repository. They therefore contain traces of the working environment:
- "The user" is the corresponding author, who approved the study's scope, the optional dependency YASA (protocol
  001) and amendments 005 and 006 before they were computed.
- Amendment 006 adds derived quantities and reporting only (no new analysis). Its section A names "the C4 grid (1%,
  2%, 5%, 10%, 20%, 50%)", which lists amendment 004's B1 block fractions; the C4 grid of amendment 005 is 5%, 10%,
  20%, 30% and 50%, and Supplementary Table S14 follows C4. The amendment's text is reproduced as written.
- Relative links point to other records in the study's repository: plans, configuration files and result reports.
  "Workstream" numbers and the candidate identifier in protocol 001 refer to the planning records of the topic
  selection that preceded the study.
- Local paths such as `data/psg-ipa/` and `outputs/` are folders on the analysis computer that held the downloaded
  dataset, per-epoch intermediate values and software environments. They are kept out of the repository, because only
  aggregate results are published.

## Provenance

All times are local (UTC+07:00). Protocol 001 and amendments 002 to 004 date from 29 September 2026, amendment 005
from 12 October 2026 and amendment 006 from 27 October 2026. "Written" times come from time-stamped working logs of the
analysis sessions; commit identifiers and times come from the study's Git repository.

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
| Amendment 006 (derived quantities and reporting only) | 27 October, before 12:11, as a draft awaiting approval; approved by the corresponding author at about 13:00 | computed after the approval (derived from the committed reports and the frozen model; no analysis re-run) | 7c323c1, 12:11 (draft); c8350d2, 13:04 (approved text) | c8350d2, 13:04, together with the derived values |

For amendments 003, 004 and 005 the repository shows each plan committed before its results, and amendment 006's draft
was committed before its approval and its derived values. The protocol and
amendment 002 were committed in the same commits as their results, so for these the order rests on the working logs.
The first run under amendment 003 stopped at calibration, before any consequence was computed; note 1 records the
change made before the second run.

SHA-256 of each plan text as reproduced below (UTF-8, LF line endings):

"""


def git_text(path: str) -> str:
    return subprocess.run(["git", "show", f"HEAD:{path}"], capture_output=True, check=True).stdout.decode("utf-8")


def main() -> None:
    parts, hashes = [], []
    for title, path in PLANS:
        text = git_text(path).replace("\r\n", "\n")
        hashes.append(f"- {title} (`{Path(path).name}`): `{hashlib.sha256(text.encode('utf-8')).hexdigest()}`")
        parts.append(f"\n\n---\n\n# {title}\n\n{text.strip()}\n")
    out = Path("newpaper/psg_assist_bias_manuscript/supplementary_file_S1_analysis_plans.md")
    out.write_text(HEADER + "\n".join(hashes) + "\n" + "".join(parts), encoding="utf-8", newline="\n")
    print(out, sum(len(p.split()) for p in parts), "words of plan text")


if __name__ == "__main__":
    main()
