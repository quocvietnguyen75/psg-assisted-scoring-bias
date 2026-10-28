"""Compare a clean re-run with the committed reports and manuscript values (amendment 005, D2 part two).

Usage, from the repository root:
    python tools/compare_rerun.py [--rerun newpaper/rerun] [--tolerance 1e-9]

The committed reports are read from newpaper/research_selection_2026-09-26_novelty and the committed values from
newpaper/psg_assist_bias_manuscript/generated/values.tex. The re-run's reports are read from --rerun and its values
from --rerun/manuscript/generated/values.tex. Line endings are normalised before hashing and comparing. The
top-level "frozen_at" field of each JSON report is the plan's freeze date copied from the configuration, not a run
time, so a re-run can reproduce a report byte for byte; the field is ignored in the comparison all the same.

values.tex must be identical. Numeric leaves of the reports may differ by up to --tolerance (default 1e-9, the
study's own cache-check tolerance): Python randomises string hashes per process, which changes the order in which
the kappa computation sums over the stage categories, so sleep-stage kappa quantities differ between processes at
the last floating-point bit (about 1e-16), never in a reported value. The script prints a SHA-256 of every
normalised file, the differing keys of values.tex if any, and for each report whether it is identical apart from
that field, equal within the tolerance (with the number of such leaves and the largest difference), or different.
Stager label files regenerated under --rerun/labels are compared epoch by epoch with the committed ones in outputs/.
Files absent from the re-run are listed as "not re-run" and do not fail the comparison. Exit code 0 (RESULT: PASS)
when values.tex is identical and every re-run report is within tolerance; 1 otherwise. Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMITTED = ROOT / "newpaper" / "research_selection_2026-09-26_novelty"
VALUES = ROOT / "newpaper" / "psg_assist_bias_manuscript" / "generated" / "values.tex"
REPORTS = [
    "psg_assist_bias_001_report.json", "psg_assist_bias_001_m5_yasa.json",
    "psg_assist_bias_001_exploratory_ranking.json", "psg_assist_bias_002_report.json",
    "psg_assist_bias_003_simulation.json", "psg_assist_bias_004_report.json", "psg_assist_bias_005_report.json",
    "psg_assist_bias_005_crosscheck.json",
]
GRID = "psg_assist_bias_003_grid.csv"
LABELS = {"yasa_labels.json": ROOT / "outputs" / "psg_assist_bias_005" / "yasa_labels.json",
          "gssc_labels.json": ROOT / "outputs" / "psg_assist_bias_005" / "gssc_labels.json"}
VALUE_LINE = re.compile(r"^\\expandafter\\def\\csname val@([^\\]+)\\endcsname\{(.*)\}$")


def normalised(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_values(text: str) -> dict[str, str]:
    out = {}
    for line in text.splitlines():
        m = VALUE_LINE.match(line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def differences(a, b, path="", out=None):
    """Differing leaves between two JSON values, as (path, a, b)."""
    out = [] if out is None else out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append((f"{path}/{k}", a.get(k, "<absent>"), b.get(k, "<absent>")))
            else:
                differences(a[k], b[k], f"{path}/{k}", out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((f"{path}/len", len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)):
            differences(x, y, f"{path}[{i}]", out)
    elif a != b and not (isinstance(a, float) and isinstance(b, float) and a != a and b != b):
        out.append((path, a, b))
    return out


def is_number(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def compare_json(name: str, committed: Path, rerun: Path, tolerance: float) -> bool:
    ca, cb = normalised(committed), normalised(rerun)
    a, b = json.loads(ca), json.loads(cb)
    for d in (a, b):
        if isinstance(d, dict):
            d.pop("frozen_at", None)
    diffs = differences(a, b)
    within = [(p, x, y) for p, x, y in diffs if is_number(x) and is_number(y) and abs(x - y) <= tolerance]
    beyond = [d for d in diffs if d not in within]
    if ca == cb:
        status = "byte-identical to the committed file"
    elif not diffs:
        status = "identical apart from the frozen_at field"
    elif not beyond:
        status = (f"equal within tolerance: {len(within)} leaves differ by at most "
                  f"{max(abs(x - y) for _, x, y in within):.3e}")
    else:
        status = f"DIFFERENT: {len(beyond)} leaves beyond tolerance ({len(within)} within)"
    print(f"{name}: {status}")
    print(f"    committed {digest(ca)}\n    re-run    {digest(cb)}")
    for p, x, y in beyond[:20]:
        print(f"    {p}: committed {x!r}, re-run {y!r}")
    if len(beyond) > 20:
        print(f"    ... {len(beyond) - 20} more")
    return not beyond


def compare_labels(name: str, committed: Path, rerun: Path) -> bool:
    a, b = json.loads(normalised(committed)), json.loads(normalised(rerun))
    total = differing = 0
    for rec in sorted(set(a) | set(b)):
        ea, eb = a.get(rec, {}), b.get(rec, {})
        keys = set(ea) | set(eb)
        total += len(keys)
        differing += sum(ea.get(k) != eb.get(k) for k in keys)
    print(f"{name}: {differing} of {total} epochs differ")
    print(f"    committed {digest(normalised(committed))}\n    re-run    {digest(normalised(rerun))}")
    return differing == 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rerun", type=Path, default=ROOT / "newpaper" / "rerun")
    parser.add_argument("--tolerance", type=float, default=1e-9)
    args = parser.parse_args(argv)
    rerun = args.rerun if args.rerun.is_absolute() else ROOT / args.rerun
    ok = True

    rerun_values = rerun / "manuscript" / "generated" / "values.tex"
    if rerun_values.is_file():
        ca, cb = normalised(VALUES), normalised(rerun_values)
        va, vb = parse_values(ca), parse_values(cb)
        if ca == cb:
            print(f"values.tex: IDENTICAL ({len(va)} values)")
        else:
            keys = sorted(k for k in set(va) | set(vb) if va.get(k) != vb.get(k))
            print(f"values.tex: DIFFERENT, {len(keys)} of {len(set(va) | set(vb))} keys differ")
            for k in keys[:40]:
                print(f"    {k}: committed {va.get(k, '<absent>')}, re-run {vb.get(k, '<absent>')}")
            ok = False
        print(f"    committed {digest(ca)}\n    re-run    {digest(cb)}")
    else:
        print(f"values.tex: not found at {rerun_values} (build it with careport.psg_assist_manuscript --reports ... --out ...)")
        ok = False

    for name in REPORTS:
        path = rerun / name
        if name == "psg_assist_bias_003_simulation.json" and not path.is_file() and (rerun / "sim" / "simulation.json").is_file():
            path = rerun / "sim" / "simulation.json"
        if not path.is_file():
            print(f"{name}: not re-run")
            continue
        ok = compare_json(name, COMMITTED / name, path, args.tolerance) and ok
    grid = rerun / GRID
    if not grid.is_file() and (rerun / "sim" / "grid.csv").is_file():
        grid = rerun / "sim" / "grid.csv"
    if grid.is_file():
        ca, cb = normalised(COMMITTED / GRID), normalised(grid)
        print(f"{GRID}: {'identical' if ca == cb else 'DIFFERENT'}\n    committed {digest(ca)}\n    re-run    {digest(cb)}")
        ok = (ca == cb) and ok
    else:
        print(f"{GRID}: not re-run")

    for name, committed in LABELS.items():
        path = rerun / "labels" / name
        if path.is_file():
            ok = compare_labels(name, committed, path) and ok
        else:
            print(f"{name}: not re-run (the committed file in outputs/ was used)")

    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
