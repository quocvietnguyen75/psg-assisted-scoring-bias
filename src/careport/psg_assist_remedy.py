"""Amendment 004 for the assisted-scoring bias study (PSG-IPA): remedy designs and two checks.

- A1: recompute Delta-human and M5 on epochs where both consensuses exist.
- A2: ask which side the assisted consensus takes where the two consensuses differ.
- A3: compare the pre-fill with the experts' own unassisted consensus, as judged by the assisted consensus.
- B1: emulate unassisted audit designs on the data, with exact finite-population precision.
- B2: evaluate the same designs in the calibrated amendment 003 model.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from statistics import NormalDist
from typing import Any, Mapping, Sequence

from careport.psg_assist_bias import (
    AnalysisError,
    _bin_counts,
    _coverage,
    _mean,
    _recordings,
    consensus_events,
    consensus_stages,
    event_f1,
    events_in_window,
    lights_window,
    read_annotations,
    sign_test,
    stage_agreement,
    stage_epochs,
    verify_checksums,
)
from careport.psg_assist_mechanisms import crossed_bootstrap_nan, stage_percent_agreement
from careport.psg_assist_simulation import Model, _alphas, _bisect, _correct, _prefill, abilities, difficulty_nodes

_NORMAL = NormalDist()


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------

def side_taking(auto: Sequence[Any], manual: Sequence[Any], assisted: Sequence[Any]) -> dict[str, Any]:
    """Among units where both consensuses exist and differ, the shares equal to the pre-fill's label."""
    changed = [(a, m, s) for a, m, s in zip(auto, manual, assisted)
               if a is not None and m is not None and s is not None and m != s]
    n = len(changed)
    if not n:
        return {"n_changed": 0, "n_assisted_equals": 0, "n_manual_equals": 0,
                "assisted_equals_prefill": None, "manual_equals_prefill": None, "difference": None}
    sa = sum(s == a for a, _, s in changed)
    ma = sum(m == a for a, m, _ in changed)
    return {"n_changed": n, "n_assisted_equals": sa, "n_manual_equals": ma,
            "assisted_equals_prefill": sa / n, "manual_equals_prefill": ma / n, "difference": (sa - ma) / n}


def _pop_var(values: Sequence[float]) -> float:
    """Finite-population variance with the N - 1 denominator."""
    n = len(values)
    if n < 2:
        return 0.0
    m = sum(values) / n
    return sum((v - m) ** 2 for v in values) / (n - 1)


def audit_precision(strata: Sequence[Sequence[tuple[float, float]]], fraction: float) -> dict[str, Any]:
    """Exact precision of the audit estimators under stratified simple random sampling.

    Each unit is (y, s): its value against the unassisted and against the assisted reference. D1 estimates
    the population mean of y from the audited units; D2 adds the audited mean of y - s to the known
    population mean of s. Both are unbiased; d0_bias is the bias of the population mean of s.
    """
    strata = [list(s) for s in strata if s]
    total = sum(len(s) for s in strata)
    target = sum(y for s in strata for y, _ in s) / total
    assisted = sum(x for s in strata for _, x in s) / total
    var1 = var2 = 0.0
    sizes = []
    for units in strata:
        big_n = len(units)
        n = min(big_n, max(2, round(fraction * big_n)))
        sizes.append(n)
        w = big_n / total
        factor = w * w * (1 - n / big_n) / n
        var1 += factor * _pop_var([y for y, _ in units])
        var2 += factor * _pop_var([y - x for y, x in units])
    return {"target": target, "assisted_mean": assisted, "d0_bias": assisted - target,
            "d1_se": math.sqrt(var1), "d2_se": math.sqrt(var2), "audited_per_stratum": sizes, "audited": sum(sizes)}


def joint_counts(pairs: Sequence[Sequence[Sequence[float]]]) -> list[list[float]]:
    """Joint distribution of (manual true-label count, assisted true-label count) over scorers.

    pairs[j] = [[P(M=T, S=T), P(M=T, S=C)], [P(M=C, S=T), P(M=C, S=C)]] for scorer j.
    """
    n = len(pairs)
    dist = [[0.0] * (n + 1) for _ in range(n + 1)]
    dist[0][0] = 1.0
    for k, q in enumerate(pairs):
        nxt = [[0.0] * (n + 1) for _ in range(n + 1)]
        for a in range(k + 1):
            for b in range(k + 1):
                d = dist[a][b]
                if d:
                    nxt[a + 1][b + 1] += d * q[0][0]
                    nxt[a + 1][b] += d * q[0][1]
                    nxt[a][b + 1] += d * q[1][0]
                    nxt[a][b] += d * q[1][1]
        dist = nxt
    return dist


def _session_pairs(model: Model, n: int, b: float | None, correct: bool) -> list[list[list[float]]]:
    """Per scorer: joint of (manual label true, assisted label true), given the epoch and the pre-fill."""
    z, al, c = abilities(n, model.spread), _alphas(model, n), model.consistency
    out = []
    for x, aj in zip(z, al):
        p = _correct(x, b)
        fresh = p + aj * (1 - p) if correct else p * (1 - aj)
        s_given_t = c * (1.0 if correct else 1 - aj) + (1 - c) * fresh
        s_given_c = c * (aj if correct else 0.0) + (1 - c) * fresh
        out.append([[p * s_given_t, p * (1 - s_given_t)], [(1 - p) * s_given_c, (1 - p) * (1 - s_given_c)]])
    return out


def _decide(count: int, n: int, m: int) -> bool | None:
    """Consensus from the number of true labels: True, False (competing label) or None (no consensus)."""
    return True if count >= m else False if n - count >= m else None


def competitor_ability(model: Model, advantage: float, bracket: Sequence[float]) -> float:
    """Ability of a competitor with the experts' error pattern whose true accuracy exceeds the pre-fill's by advantage."""
    nodes = difficulty_nodes(model)
    true_a = sum(w * _prefill(model, b) for w, b in nodes)
    root = _bisect(lambda d: sum(w * _correct(d, b) for w, b in nodes) - true_a - advantage, bracket[0], bracket[1])
    if root is None:
        raise AnalysisError(f"no competitor ability gives an advantage of {advantage}")
    return root


def design_moments(model: Model, n: int, majority: int, supermajority: int,
                   competitors: Sequence[float]) -> list[dict[str, Any]]:
    """Per-epoch moments of the audit designs (amendment 004, B2).

    Population: epochs where the unassisted n-scorer consensus exists. For the pre-fill, the competitor and
    their gap (competitor minus pre-fill), y is agreement with the unassisted consensus and s agreement with
    the assisted consensus (0 where it does not exist). D0 and D0s use the epochs where their assisted
    consensus exists.
    """
    nodes = difficulty_nodes(model)
    true_a = sum(w * _prefill(model, b) for w, b in nodes)
    table = []
    for w, b in nodes:
        a = _prefill(model, b)
        for correct, pst in ((True, a), (False, 1 - a)):
            dist = joint_counts(_session_pairs(model, n, b, correct))
            cells = []
            for km in range(n + 1):
                rm = _decide(km, n, majority)
                if rm is None:
                    continue
                for ks in range(n + 1):
                    if dist[km][ks]:
                        cells.append((dist[km][ks], rm, _decide(ks, n, majority), _decide(ks, n, supermajority)))
            table.append((w * pst, b, correct, cells))
    out = []
    for ability in competitors:
        sums = {q: dict.fromkeys(("w", "y", "yy", "s", "dd", "w0", "s0", "ss0", "w9", "s9", "ss9"), 0.0)
                for q in ("prefill", "competitor", "gap")}
        for base, b, correct, cells in table:
            pb = _correct(ability, b)
            for prob, rm, rs, r9 in cells:
                for b_true, pbx in ((True, pb), (False, 1 - pb)):
                    wt = base * prob * pbx
                    if not wt:
                        continue
                    ya, yb = float(correct == rm), float(b_true == rm)
                    sa = None if rs is None else float(correct == rs)
                    sb = None if rs is None else float(b_true == rs)
                    a9 = None if r9 is None else float(correct == r9)
                    b9 = None if r9 is None else float(b_true == r9)
                    values = {"prefill": (ya, sa, a9), "competitor": (yb, sb, b9),
                              "gap": (yb - ya, None if rs is None else sb - sa, None if r9 is None else b9 - a9)}
                    for q, (y, s, s9) in values.items():
                        acc = sums[q]
                        s_all = 0.0 if s is None else s
                        acc["w"] += wt
                        acc["y"] += wt * y
                        acc["yy"] += wt * y * y
                        acc["s"] += wt * s_all
                        acc["dd"] += wt * (y - s_all) ** 2
                        if s is not None:
                            acc["w0"] += wt
                            acc["s0"] += wt * s
                            acc["ss0"] += wt * s * s
                        if s9 is not None:
                            acc["w9"] += wt
                            acc["s9"] += wt * s9
                            acc["ss9"] += wt * s9 * s9
        result: dict[str, Any] = {"ability": ability,
                                  "true_advantage": sum(w * _correct(ability, b) for w, b in nodes) - true_a}
        for q, acc in sums.items():
            wtot = acc["w"]
            mean_y, mean_s = acc["y"] / wtot, acc["s"] / wtot
            mean0 = acc["s0"] / acc["w0"] if acc["w0"] else None
            mean9 = acc["s9"] / acc["w9"] if acc["w9"] else None
            result[q] = {
                "population_share": wtot,
                "mean_unassisted": mean_y,
                "var_unassisted": acc["yy"] / wtot - mean_y ** 2,
                "var_difference": acc["dd"] / wtot - (mean_y - mean_s) ** 2,
                "assisted_share": acc["w0"] / wtot,
                "mean_assisted": mean0,
                "var_assisted": acc["ss0"] / acc["w0"] - mean0 ** 2 if mean0 is not None else None,
                "supermajority_share": acc["w9"] / wtot,
                "mean_supermajority": mean9,
                "var_supermajority": acc["ss9"] / acc["w9"] - mean9 ** 2 if mean9 is not None else None,
            }
        result["population_share"] = result["gap"]["population_share"]
        out.append(result)
    return out


def _prob_positive(mean: float | None, var: float | None, n: float) -> float | None:
    if mean is None or var is None or n <= 0:
        return None
    sd = math.sqrt(max(var, 0.0) / n)
    if sd == 0:
        return 0.5 if mean == 0 else float(mean > 0)
    return _NORMAL.cdf(mean / sd)


def ranking_probabilities(q: Mapping[str, Any], n_epochs: int, fractions: Sequence[float]) -> dict[str, Any]:
    """P(a design's estimate of the gap, competitor minus pre-fill, is positive), normal approximation."""
    n_pop = n_epochs * q["population_share"]
    var_y, var_d = q["var_unassisted"], q["var_difference"]
    return {
        "D0": _prob_positive(q["mean_assisted"], q["var_assisted"], n_pop * q["assisted_share"]),
        "D0s": _prob_positive(q["mean_supermajority"], q["var_supermajority"], n_pop * q["supermajority_share"]),
        "D1": {f: _prob_positive(q["mean_unassisted"], var_y / f, n_pop) for f in fractions},
        "D2": {f: _prob_positive(q["mean_unassisted"], (var_y - var_d) + var_d / f, n_pop) for f in fractions},
    }


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

def _restricted(metric: Any, x: Mapping[int, Any], y: Mapping[int, Any], keys: Sequence[int]) -> float | None:
    if not keys:
        return None
    try:
        return metric({k: x[k] for k in keys}, {k: y[k] for k in keys})
    except AnalysisError:
        return None


def _diff(a: float | None, b: float | None) -> float | None:
    return None if a is None or b is None else a - b


def _load(root: Path, task: str, spec: Mapping[str, Any], c1: Mapping[str, Any], rec: int) -> dict[str, Any]:
    token, n_sc = spec["file_token"], int(c1["n_scorers"])
    ann = root / task / "Annotations"
    auto_rows = read_annotations(ann / "auto" / f"SN{rec}_{token}_auto.txt")
    window = lights_window(auto_rows, c1["window"]["start_label"], c1["window"]["end_label"])
    if spec["kind"] == "stages":
        ex = lambda rows: stage_epochs(rows, spec["labels"], spec["label_prefix"], window, c1["epoch_seconds"])
    else:
        ex = lambda rows: events_in_window(rows, spec["labels"], window)
    return {"window": window, "auto": ex(auto_rows),
            **{cond: [ex(read_annotations(ann / cond / f"SN{rec}_{token}_{cond}_scorer{s}.txt"))
                      for s in range(1, n_sc + 1)] for cond in ("manual", "semiauto")}}


def run_remedy(config4_path: Path, config1_path: Path, data_root: Path, stager_labels_path: Path,
               output_path: Path, verify: bool = True) -> dict[str, Any]:
    c4 = json.loads(Path(config4_path).read_text(encoding="utf-8"))
    c1 = json.loads(Path(config1_path).read_text(encoding="utf-8"))
    root = Path(data_root)
    repo = Path(config4_path).resolve().parents[2]
    if verify:
        verify_checksums(root, c1["dataset"]["checksum_file"], c1["dataset"]["expected_files"])
    n_sc = int(c1["n_scorers"])
    full, loo = int(c1["consensus_majority"]["full"]), int(c1["consensus_majority"]["leave_one_out"])
    sup, grid, boot = int(c4["supermajority"]), float(c1["event_grid_seconds"]), c4["bootstrap"]
    fractions = [float(f) for f in c4["audit_fractions"]]
    stager = {rec: {int(k): v for k, v in labels.items()}
              for rec, labels in json.loads(Path(stager_labels_path).read_text(encoding="utf-8")).items()}
    stage_task = c1["secondary_algorithm"]["task"]

    check = {"passed": True, "max_abs_difference": None}
    m5 = None
    if c4.get("stager_cache_check"):
        m5 = {r["recording"]: r for r in json.loads((repo / c4["stager_cache_check"]["m5_report"])
                                                    .read_text(encoding="utf-8"))["recordings"]}
    a1_human = {m: [[] for _ in range(n_sc)] for m in ("kappa", "percent")}
    a1_yasa: dict[str, list[dict[str, Any]]] = {"by_recording": []}
    a2: dict[str, Any] = {}
    a3: dict[str, Any] = {}
    b1_strata: dict[str, list[list[tuple[float, float]]]] = {"prefill": [], "yasa": [], "gap": []}
    b1_d0: dict[str, list[float]] = {"prefill": [], "yasa": [], "gap": []}
    b1_d0s: dict[str, list[float]] = {"prefill": [], "yasa": [], "gap": []}
    diffs = []
    for task, spec in c1["tasks"].items():
        a2[task], a3[task] = {"by_recording": []}, {"by_recording": []}
        for rec in _recordings(root, task, spec["file_token"]):
            d = _load(root, task, spec, c1, rec)
            name = f"SN{rec}"
            if spec["kind"] == "stages":
                auto, man, semi = d["auto"], d["manual"], d["semiauto"]
                cons_m, cons_s = consensus_stages(man, full), consensus_stages(semi, full)
                cons_s9 = consensus_stages(semi, sup)
                if task == stage_task:
                    yasa = stager[name]
                    if m5 is not None:
                        for key, cons in (("kappa_stager_vs_manual_consensus", cons_m),
                                          ("kappa_stager_vs_assisted_consensus", cons_s)):
                            diffs.append(abs(stage_agreement(yasa, cons) - m5[name][key]))
                    # A1: Delta-human and Delta-YASA on common support.
                    for s in range(n_sc):
                        lm = consensus_stages([x for i, x in enumerate(man) if i != s], loo)
                        ls = consensus_stages([x for i, x in enumerate(semi) if i != s], loo)
                        keys = sorted(k for k, v in man[s].items() if v is not None and k in lm and k in ls)
                        for metric, fn in (("kappa", stage_agreement), ("percent", stage_percent_agreement)):
                            a1_human[metric][s].append(_diff(_restricted(fn, man[s], ls, keys),
                                                             _restricted(fn, man[s], lm, keys)))
                    keys = sorted(k for k, v in yasa.items() if v is not None and k in cons_m and k in cons_s)
                    a1_yasa["by_recording"].append({
                        "recording": name, "epochs": len(keys),
                        **{metric: _diff(_restricted(fn, yasa, cons_s, keys), _restricted(fn, yasa, cons_m, keys))
                           for metric, fn in (("kappa", stage_agreement), ("percent", stage_percent_agreement))}})
                    # B1: audit emulation units.
                    units = {"prefill": [], "yasa": [], "gap": []}
                    for k in sorted(k for k, v in auto.items() if v is not None and yasa.get(k) is not None
                                    and k in cons_m):
                        ya, yy = float(auto[k] == cons_m[k]), float(yasa[k] == cons_m[k])
                        sa = float(auto[k] == cons_s[k]) if k in cons_s else 0.0
                        sy = float(yasa[k] == cons_s[k]) if k in cons_s else 0.0
                        units["prefill"].append((ya, sa))
                        units["yasa"].append((yy, sy))
                        units["gap"].append((ya - yy, sa - sy))
                        if k in cons_s:
                            b1_d0["prefill"].append(sa)
                            b1_d0["yasa"].append(sy)
                            b1_d0["gap"].append(sa - sy)
                        if k in cons_s9:
                            a9, y9 = float(auto[k] == cons_s9[k]), float(yasa[k] == cons_s9[k])
                            b1_d0s["prefill"].append(a9)
                            b1_d0s["yasa"].append(y9)
                            b1_d0s["gap"].append(a9 - y9)
                    for q in units:
                        b1_strata[q].append(units[q])
                keys = sorted(k for k, v in auto.items() if v is not None)
                side = side_taking([auto[k] for k in keys], [cons_m.get(k) for k in keys], [cons_s.get(k) for k in keys])
                common = [k for k in keys if k in cons_m and k in cons_s]
                closeness = {f"{metric}_{who}": _restricted(fn, ref, cons_s, common)
                             for metric, fn in (("kappa", stage_agreement), ("percent", stage_percent_agreement))
                             for who, ref in (("prefill", auto), ("manual_consensus", cons_m))}
                closeness["epochs"] = len(common)
                closeness["percent_matches_prefill"] = sum(auto[k] == cons_s[k] for k in common)
                closeness["percent_matches_manual_consensus"] = sum(cons_m[k] == cons_s[k] for k in common)
            else:
                window, auto_ev = d["window"], d["auto"]
                counts_m, counts_s = _bin_counts(d["manual"], grid, window), _bin_counts(d["semiauto"], grid, window)
                auto_bins = [bool(x) for x in _coverage(auto_ev, grid, window)]
                side = side_taking(auto_bins, [c >= full for c in counts_m], [c >= full for c in counts_s])
                ref = consensus_events(d["semiauto"], full, grid, window)
                closeness = {"f1_prefill": event_f1(ref, auto_ev),
                             "f1_manual_consensus": event_f1(ref, consensus_events(d["manual"], full, grid, window))}
            a2[task]["by_recording"].append({"recording": name, **side})
            a3[task]["by_recording"].append({"recording": name, **closeness})
    if diffs:
        check["max_abs_difference"] = max(diffs)
        check["passed"] = check["max_abs_difference"] <= float(c4["stager_cache_check"]["tolerance"])
        if not check["passed"]:
            raise AnalysisError(f"cached stager labels do not reproduce M5 (difference {check['max_abs_difference']})")

    # A1 summaries.
    a1 = {"delta_human": {m: {"mean": _mean([v for row in mat for v in row if v is not None]),
                              "ci95": crossed_bootstrap_nan(mat, boot["resamples"], boot["seed"]),
                              "n_cells": sum(v is not None for row in mat for v in row)}
                          for m, mat in a1_human.items()},
          "delta_yasa": {**a1_yasa, **{m: {"mean": _mean([r[m] for r in a1_yasa["by_recording"] if r[m] is not None]),
                                           "n_negative": sum(r[m] < 0 for r in a1_yasa["by_recording"] if r[m] is not None)}
                                       for m in ("kappa", "percent")}}}
    # A2 pooled per task and sign test over recording-task units.
    units = []
    for task, block in a2.items():
        rows = block["by_recording"]
        n = sum(r["n_changed"] for r in rows)
        sa, ma = sum(r["n_assisted_equals"] for r in rows), sum(r["n_manual_equals"] for r in rows)
        block["pooled"] = {"n_changed": n, "assisted_equals_prefill": sa / n if n else None,
                           "manual_equals_prefill": ma / n if n else None, "difference": (sa - ma) / n if n else None}
        units += [r["difference"] for r in rows if r["difference"] is not None]
    a2_out = {"tasks": a2, "sign_test": {"n_units": len(units), "n_positive": sum(u > 0 for u in units),
                                         "p": sign_test(units)}}
    # A3 counts of units where the pre-fill is closer to the assisted consensus.
    primary, percent_units = [], []
    for task, block in a3.items():
        for r in block["by_recording"]:
            if "f1_prefill" in r:
                primary.append(r["f1_prefill"] - r["f1_manual_consensus"])
            else:
                primary.append(_diff(r["kappa_prefill"], r["kappa_manual_consensus"]))
                percent_units.append(_diff(r["percent_prefill"], r["percent_manual_consensus"]))
        rows = block["by_recording"]
        if rows and "epochs" in rows[0]:
            n = sum(r["epochs"] for r in rows)
            block["pooled_percent"] = {"prefill": sum(r["percent_matches_prefill"] for r in rows) / n,
                                       "manual_consensus": sum(r["percent_matches_manual_consensus"] for r in rows) / n}
    primary = [u for u in primary if u is not None]
    a3_out = {"tasks": a3, "units_prefill_closer": {"n_units": len(primary), "n_positive": sum(u > 0 for u in primary),
                                                    "p": sign_test(primary)},
              "stage_units_prefill_closer_percent": sum(u > 0 for u in percent_units if u is not None)}
    # B1 audit emulation.
    b1: dict[str, Any] = {"population_epochs": sum(len(s) for s in b1_strata["prefill"]), "targets": {}}
    for q in ("prefill", "yasa", "gap"):
        audits = {f: audit_precision(b1_strata[q], f) for f in fractions}
        target = audits[fractions[0]]["target"]
        b1["targets"][q] = {
            "target": target,
            "D0": {"estimate": _mean(b1_d0[q]), "bias": _mean(b1_d0[q]) - target, "epochs": len(b1_d0[q])},
            "D0s": {"estimate": _mean(b1_d0s[q]), "bias": _mean(b1_d0s[q]) - target, "epochs": len(b1_d0s[q])},
            "audits": {str(f): {"audited": a["audited"], "d1_se": a["d1_se"], "d2_se": a["d2_se"],
                                "d1_halfwidth": 1.96 * a["d1_se"], "d2_halfwidth": 1.96 * a["d2_se"]}
                       for f, a in audits.items()},
        }
    gap = b1["targets"]["gap"]
    b1["smallest_f_D2_halfwidth_below_D0_gap_bias"] = next(
        (f for f in fractions if gap["audits"][str(f)]["d2_halfwidth"] < abs(gap["D0"]["bias"])), None)
    # B2 simulation.
    sim = c4["simulation"]
    params = json.loads((repo / sim["calibration_report"]).read_text(encoding="utf-8"))["calibration"]["model"]
    model = Model(**{**params, "alphas": tuple(params["alphas"]) if params.get("alphas") else None})
    advantages = [float(a) for a in sim["advantages"]]
    abilities_b = [competitor_ability(model, a, sim["ability_bracket"]) for a in advantages]
    moments = design_moments(model, int(sim["scorers"]), int(sim["majority"]), int(sim["supermajority"]), abilities_b)
    b2_rows = []
    for adv, mom in zip(advantages, moments):
        for n_epochs in sim["study_epochs"]:
            probs = ranking_probabilities(mom["gap"], int(n_epochs), fractions)
            b2_rows.append({"advantage": adv, "true_advantage": mom["true_advantage"], "study_epochs": n_epochs,
                            "P_competitor_ranked_above": {"D0": probs["D0"], "D0s": probs["D0s"],
                                                          **{f"D1_{f}": v for f, v in probs["D1"].items()},
                                                          **{f"D2_{f}": v for f, v in probs["D2"].items()}},
                            "expected_gap": {"D0": mom["gap"]["mean_assisted"], "D0s": mom["gap"]["mean_supermajority"],
                                             "unassisted": mom["gap"]["mean_unassisted"]}})
    b2 = {"model": params, "moments": moments, "rows": b2_rows}

    # Predictions.
    def row(adv: float, n_epochs: int) -> Mapping[str, Any]:
        return next(r for r in b2_rows if r["advantage"] == adv and r["study_epochs"] == n_epochs)

    big, small = max(sim["study_epochs"]), min(sim["study_epochs"])
    has_02 = 0.02 in advantages and 0.1 in fractions
    stage_pct = a3.get(stage_task, {}).get("pooled_percent")
    predictions = {
        "A1": {"supported": all(a1["delta_human"][m]["mean"] < 0 and a1["delta_yasa"][m]["mean"] < 0
                                for m in ("kappa", "percent"))},
        "A2": {"supported": all(b["pooled"]["difference"] is not None and b["pooled"]["difference"] > 0
                                for b in a2.values()) and a2_out["sign_test"]["p"] < 0.05},
        "A3": {"supported": stage_pct is not None and stage_pct["prefill"] >= stage_pct["manual_consensus"] - 0.01},
        "PB1": {"supported": b1["targets"]["prefill"]["D0"]["bias"] > 0 and b1["targets"]["gap"]["D0"]["bias"] > 0},
        "PB2": {"supported": all(b1["targets"][q]["audits"][str(f)]["d2_se"] < b1["targets"][q]["audits"][str(f)]["d1_se"]
                                 for q in b1["targets"] for f in fractions)
                and all(m[q]["var_difference"] < m[q]["var_unassisted"] for m in moments
                        for q in ("prefill", "competitor", "gap"))},
        "PB3": {"supported": has_02 and row(0.02, small)["P_competitor_ranked_above"]["D0"] < 0.05
                and row(0.02, big)["P_competitor_ranked_above"]["D0"] < 0.05
                and row(0.02, big)["P_competitor_ranked_above"]["D1_0.1"] > 0.8
                and row(0.02, big)["P_competitor_ranked_above"]["D2_0.1"] > 0.8},
        "PB4": {"supported": has_02 and row(0.02, big)["P_competitor_ranked_above"]["D0"]
                < row(0.02, big)["P_competitor_ranked_above"]["D0s"]
                < row(0.02, big)["P_competitor_ranked_above"]["D2_0.1"]},
    }
    report = {
        "protocol": c4["protocol"], "amendment": c4["amendment"], "frozen_at": c4["frozen_at"],
        "stager_cache_check": check,
        "A1_common_support": a1, "A2_side_taking": a2_out, "A3_closeness": a3_out,
        "B1_emulation": b1, "B2_simulation": b2, "predictions": predictions,
    }
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    return json.loads(output_path.read_text(encoding="utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=Path, required=True, help="amendment 004 config")
    parser.add_argument("--base-config", type=Path, required=True, help="protocol 001 config")
    parser.add_argument("--stager-labels", type=Path, required=True, help="cached YASA labels (outputs/)")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    env = json.loads(args.base_config.read_text(encoding="utf-8"))["data_root_env"]
    root = os.environ.get(env)
    if not root:
        print(f"Set {env} to the psg-ipa/1.0.0 folder.", file=sys.stderr)
        return 2
    report = run_remedy(args.config, args.base_config, Path(root), args.stager_labels, args.output)
    print(json.dumps({k: report[k] for k in ("stager_cache_check", "predictions")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
