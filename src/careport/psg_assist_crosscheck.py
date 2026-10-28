"""Library cross-check (amendment 005, part D3): the study's kappa and sign tests against reference implementations.

The comparison functions take the reference implementations as arguments, so this module stays standard-library
only. main() supplies scikit-learn's cohen_kappa_score and SciPy's binomtest, and runs in a separate environment
that has them (outputs/envs/yasa).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from careport.psg_assist_bias import cohen_kappa, sign_test
from careport.psg_assist_remedy import _load
from careport.psg_assist_bias import _recordings, consensus_stages


def compare_kappa(pairs: Sequence[tuple[Sequence[str], Sequence[str]]],
                  reference: Callable[[Sequence[str], Sequence[str]], float]) -> dict[str, Any]:
    """Largest absolute difference between the study's Cohen's kappa and a reference over label-sequence pairs."""
    diffs = [abs(cohen_kappa(a, b) - float(reference(a, b))) for a, b in pairs]
    return {"pairs": len(diffs), "max_abs_difference": max(diffs) if diffs else None}


def compare_sign_tests(units: Mapping[str, Sequence[float]],
                       reference: Callable[[int, int], float]) -> dict[str, Any]:
    """The study's exact two-sided sign test against a reference binomial test, reference(k positive, n nonzero)."""
    tests = {}
    for name, values in units.items():
        nonzero = [v for v in values if v != 0]
        k, n = sum(v > 0 for v in nonzero), len(nonzero)
        p_study, p_ref = sign_test(values), float(reference(k, n))
        tests[name] = {"n": n, "k": k, "p_study": p_study, "p_reference": p_ref, "abs_difference": abs(p_study - p_ref)}
    return {"tests": tests, "max_abs_difference": max(t["abs_difference"] for t in tests.values())}


def stage_pairs(config1_path: Path, data_root: Path) -> list[tuple[list[str], list[str]]]:
    """Every staging comparison the primary analysis makes against the pre-fill, on the epochs it uses."""
    c1 = json.loads(Path(config1_path).read_text(encoding="utf-8"))
    task = c1["secondary_algorithm"]["task"]
    spec, full = c1["tasks"][task], int(c1["consensus_majority"]["full"])
    pairs = []
    for rec in _recordings(Path(data_root), task, spec["file_token"]):
        d = _load(Path(data_root), task, spec, c1, rec)
        auto = d["auto"]
        others = d["manual"] + d["semiauto"] + [consensus_stages(d["manual"], full), consensus_stages(d["semiauto"], full)]
        for other in others:
            keys = sorted(k for k in auto.keys() & other.keys() if auto[k] is not None and other[k] is not None)
            pairs.append(([other[k] for k in keys], [auto[k] for k in keys]))
    return pairs


def report_units(repo: Path) -> dict[str, list[float]]:
    """The recording-task unit values behind the sign tests reported in the manuscript and amendment 005."""
    base = repo / "newpaper/research_selection_2026-09-26_novelty"
    r1 = json.loads((base / "psg_assist_bias_001_report.json").read_text(encoding="utf-8"))
    r4 = json.loads((base / "psg_assist_bias_004_report.json").read_text(encoding="utf-8"))
    r5 = json.loads((base / "psg_assist_bias_005_report.json").read_text(encoding="utf-8"))
    return {
        "M1_anchoring": [v for t in r1["tasks"].values() for v in t["M1_anchoring"]["recording_means"]],
        "M2_inflation": [v for t in r1["tasks"].values() for v in t["M2_inflation"]["did_by_recording"]],
        "A2_side_taking": [r["difference"] for t in r4["A2_side_taking"]["tasks"].values() for r in t["by_recording"]
                           if r["difference"] is not None],
        "C1_rejected_labels": [r["mean_lift"] for t in r5["C1_rejected_label_adoption"]["tasks"].values()
                               for r in t["by_recording"] if r["mean_lift"] is not None],
        "C6_min_duration": [r["did"] for t in r5["C6_event_min_duration"]["tasks"].values() for r in t["by_recording"]],
    }


def main(argv: Sequence[str] | None = None) -> int:
    from scipy import __version__ as scipy_version
    from scipy.stats import binomtest
    from sklearn import __version__ as sklearn_version
    from sklearn.metrics import cohen_kappa_score

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-config", type=Path, required=True, help="protocol 001 config")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    env = json.loads(args.base_config.read_text(encoding="utf-8"))["data_root_env"]
    root = os.environ.get(env)
    if not root:
        print(f"Set {env} to the psg-ipa/1.0.0 folder.", file=sys.stderr)
        return 2
    repo = args.base_config.resolve().parents[2]
    report = {
        "references": {"scikit-learn": sklearn_version, "scipy": scipy_version},
        "kappa": compare_kappa(stage_pairs(args.base_config, Path(root)), cohen_kappa_score),
        "sign_tests": compare_sign_tests(report_units(repo), lambda k, n: binomtest(k, n, 0.5).pvalue),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"kappa": report["kappa"], "sign_tests_max": report["sign_tests"]["max_abs_difference"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
