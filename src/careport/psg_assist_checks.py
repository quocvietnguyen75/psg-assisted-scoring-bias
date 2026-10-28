"""Amendment 005 for the assisted-scoring bias study (PSG-IPA): checks requested by the pre-submission review.

- C1: adoption of rejected labels, selecting units on the other experts' manual labels only (events at event level).
- C2: negative control: movement toward an independent stager that no expert saw (sleep staging).
- C3: the pre-fill's own gain, and the session-free contrast, on common support (sleep staging).
- C4: unassisted audits of contiguous 30-minute blocks, with exact precision (sleep staging).
- C5: a second independent stager (GSSC), when its labels are supplied.
- C6: inflation (M2) for the event tasks with consensus events shorter than the rules' minimum dropped.

The plan is newpaper/plan/PSG_ASSIST_BIAS_AMENDMENT_005_2026-10-12.md.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from bisect import bisect_left
from pathlib import Path
from typing import Any, Mapping, Sequence

from careport.psg_assist_bias import (
    AnalysisError,
    Interval,
    _coverage,
    _mean,
    _recordings,
    _segments,
    consensus_stages,
    event_f1,
    sign_test,
    stage_agreement,
    verify_checksums,
)
from careport.psg_assist_mechanisms import _summary, crossed_bootstrap_nan, stage_percent_agreement
from careport.psg_assist_remedy import _diff, _load, _restricted, side_taking

STAGE_METRICS = (("kappa", stage_agreement), ("percent", stage_percent_agreement))


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------

def rejected_label_lift(auto: Mapping[int, str | None], manual: Sequence[Mapping[int, str | None]],
                        semi: Sequence[Mapping[int, str | None]], min_other_rejecting: int) -> list[tuple[int, float | None]]:
    """C1 for stages. Per scorer s: (units, lift) over epochs where the pre-fill is labelled, s labelled the epoch in
    both sessions, and at least min_other_rejecting of the other scorers' manual labels differ from the pre-fill's.

    The lift is P(assisted label of s = pre-fill) - P(manual label of s = pre-fill). Selection never uses s's labels,
    so exchangeable sessions give no lift in expectation (no regression to the mean)."""
    out = []
    for s in range(len(manual)):
        diffs = []
        for k, a in auto.items():
            if a is None or manual[s].get(k) is None or semi[s].get(k) is None:
                continue
            rejecting = sum(1 for j, m in enumerate(manual) if j != s and m.get(k) is not None and m[k] != a)
            if rejecting >= min_other_rejecting:
                diffs.append((semi[s][k] == a) - (manual[s][k] == a))
        out.append((len(diffs), sum(diffs) / len(diffs) if diffs else None))
    return out


def overlaps(event: Interval, events: Sequence[Interval]) -> bool:
    """True when some event intersects the given one over a positive length (touching is not overlapping)."""
    return any(min(event[1], e) - max(event[0], s) > 0 for s, e in events)


class _Union:
    """Disjoint, sorted union of one scoring's events, for fast overlap queries."""

    def __init__(self, events: Sequence[Interval]):
        merged: list[list[float]] = []
        for s, e in sorted(events):
            if merged and s <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], e)
            else:
                merged.append([s, e])
        self.starts = [m[0] for m in merged]
        self.ends = [m[1] for m in merged]

    def overlaps(self, event: Interval) -> bool:
        i = bisect_left(self.starts, event[1]) - 1
        return i >= 0 and self.ends[i] > event[0]


def event_rejection_lift(auto: Sequence[Interval], manual: Sequence[Sequence[Interval]],
                         semi: Sequence[Sequence[Interval]], min_rejecting: int,
                         include_self: bool) -> list[tuple[int, float | None]]:
    """C1 for events, at event level. A manual scoring rejects a pre-fill event if none of its events overlaps it.

    Per scorer s, units are pre-fill events rejected by at least min_rejecting manual scorings: the other scorers only
    (include_self False, C1's rule) or all scorers (True, amendment 002's R4 rule). The lift is P(s's assisted scoring
    overlaps the event) - P(s's manual scoring overlaps it)."""
    man_u, semi_u = [_Union(m) for m in manual], [_Union(x) for x in semi]
    accepted = [[u.overlaps(e) for u in man_u] for e in auto]
    out = []
    for s in range(len(manual)):
        diffs = []
        for e, acc in zip(auto, accepted):
            rejecting = sum(not a for a in acc) - (0 if include_self else (not acc[s]))
            if rejecting >= min_rejecting:
                diffs.append(semi_u[s].overlaps(e) - acc[s])
        out.append((len(diffs), sum(diffs) / len(diffs) if diffs else None))
    return out


def movement_toward(target: Mapping[int, str | None], manual: Mapping[int, str | None],
                    semi: Mapping[int, str | None], keys: Sequence[int]) -> tuple[int, float | None]:
    """C2: over the given epochs where all three are labelled, P(assisted = target) - P(manual = target)."""
    diffs = [(semi[k] == target[k]) - (manual[k] == target[k]) for k in keys
             if target.get(k) is not None and manual.get(k) is not None and semi.get(k) is not None]
    return len(diffs), (sum(diffs) / len(diffs) if diffs else None)


def epoch_blocks(keys: Sequence[int], block_epochs: int, first_epoch: int) -> dict[int, list[int]]:
    """C4: consecutive, non-overlapping blocks of block_epochs epochs counted from first_epoch (lights off)."""
    blocks: dict[int, list[int]] = {}
    for k in sorted(keys):
        blocks.setdefault((k - first_epoch) // block_epochs, []).append(k)
    return blocks


def _pop_var(values: Sequence[float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    m = sum(values) / n
    return sum((v - m) ** 2 for v in values) / (n - 1)


def block_audit_precision(strata: Sequence[Sequence[Sequence[tuple[float, float]]]], fraction: float) -> dict[str, Any]:
    """C4: exact precision of the audit estimators when whole blocks are audited.

    strata[h] is a list of blocks, each a list of units (y, s): the unit's value against the unassisted and against the
    assisted reference. Within each stratum, max(1, round(fraction * blocks)) blocks are drawn by simple random sampling
    without replacement. D1 expands the audited block totals of y to the population mean; D2 adds the expanded totals
    of y - s to the known population mean of s. Both are unbiased; the variances are exact for this design."""
    strata = [[list(b) for b in s if b] for s in strata]
    strata = [s for s in strata if s]
    total = sum(len(b) for s in strata for b in s)
    target = sum(y for s in strata for b in s for y, _ in b) / total
    assisted = sum(x for s in strata for b in s for _, x in b) / total
    var1 = var2 = 0.0
    sizes, share = [], 0.0
    for blocks in strata:
        big_b = len(blocks)
        n = min(big_b, max(1, round(fraction * big_b)))
        sizes.append(n)
        share += (n / big_b) * sum(len(b) for b in blocks) / total
        factor = big_b * big_b * (1 - n / big_b) / n
        var1 += factor * _pop_var([sum(y for y, _ in b) for b in blocks])
        var2 += factor * _pop_var([sum(y - x for y, x in b) for b in blocks])
    return {"target": target, "assisted_mean": assisted, "d0_bias": assisted - target,
            "d1_se": math.sqrt(var1) / total, "d2_se": math.sqrt(var2) / total,
            "blocks_per_stratum": [len(s) for s in strata], "audited_blocks_per_stratum": sizes,
            "expected_share": share}


def drop_short(events: Sequence[Interval], min_seconds: float) -> list[Interval]:
    """C6: keep events lasting at least min_seconds."""
    return [(s, e) for s, e in events if e - s >= min_seconds - 1e-9]


def m2_event_min_duration(auto: Sequence[Interval], manual: Sequence[Sequence[Interval]],
                          semi: Sequence[Sequence[Interval]], full: int, loo: int, grid: float, window: Interval,
                          min_seconds: float) -> tuple[float, list[float]]:
    """C6: protocol 001's M2 for one event recording, with consensus events shorter than min_seconds dropped.

    Returns (delta_auto, [delta_human per scorer]). Only the consensus events (full and leave-one-out) are filtered;
    the scorings and the pre-fill are unchanged."""
    cover = {c: [_coverage(ev, grid, window) for ev in sc] for c, sc in (("manual", manual), ("semi", semi))}
    counts = {c: [sum(col) for col in zip(*cover[c])] for c in cover}
    cons = {c: drop_short(_segments([n >= full for n in counts[c]], grid, window), min_seconds) for c in counts}
    loo_cons = lambda c, s: drop_short(_segments([n - x >= loo for n, x in zip(counts[c], cover[c][s])], grid, window),
                                       min_seconds)
    delta_auto = event_f1(cons["semi"], auto) - event_f1(cons["manual"], auto)
    delta_human = [event_f1(manual[s], loo_cons("semi", s)) - event_f1(manual[s], loo_cons("manual", s))
                   for s in range(len(manual))]
    return delta_auto, delta_human


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

def _load_labels(path: Path | None) -> dict[str, dict[int, str | None]] | None:
    if path is None:
        return None
    return {rec: {int(k): v for k, v in labels.items()}
            for rec, labels in json.loads(Path(path).read_text(encoding="utf-8")).items()}


def _cells_summary(cells: list[list[float | None]], boot: Mapping[str, Any]) -> dict[str, Any]:
    """Mean of available scorer-by-recording cells with a crossed-bootstrap interval (amendment 002's summary)."""
    return _summary(cells, {"resamples": boot["resamples"], "seed": boot["seed"]})


def _stager_block(stager: Mapping[int, str | None], auto: Mapping[int, str | None], man: Sequence[Mapping[int, Any]],
                  semi: Sequence[Mapping[int, Any]], cons_m: Mapping[int, str], cons_s: Mapping[int, str]) -> dict[str, Any]:
    """C2, C3 and C5 quantities for one stager on one recording."""
    differ = sorted(k for k, a in auto.items() if a is not None and stager.get(k) is not None and stager[k] != a)
    toward_stager = [movement_toward(stager, man[s], semi[s], differ) for s in range(len(man))]
    toward_prefill = [movement_toward(auto, man[s], semi[s], differ) for s in range(len(man))]
    side = side_taking([stager[k] for k in differ], [cons_m.get(k) for k in differ], [cons_s.get(k) for k in differ])
    cs_stager = sorted(k for k, v in stager.items() if v is not None and k in cons_m and k in cons_s)
    joint = sorted(k for k in cs_stager if auto.get(k) is not None)
    out: dict[str, Any] = {
        "differ_epochs": len(differ),
        "toward_stager": [m for _, m in toward_stager], "toward_prefill": [m for _, m in toward_prefill],
        "side_taking_toward_stager": side,
        "kappa_vs_manual_consensus": stage_agreement(stager, cons_m),
        "kappa_vs_assisted_consensus": stage_agreement(stager, cons_s),
        "common_support_epochs": len(cs_stager), "joint_common_support_epochs": len(joint),
    }
    out["delta"] = out["kappa_vs_assisted_consensus"] - out["kappa_vs_manual_consensus"]
    out["lead_of_prefill_vs_manual"] = stage_agreement(auto, cons_m) - out["kappa_vs_manual_consensus"]
    out["lead_of_prefill_vs_assisted"] = stage_agreement(auto, cons_s) - out["kappa_vs_assisted_consensus"]
    for metric, fn in STAGE_METRICS:
        out[f"delta_common_support_{metric}"] = _diff(_restricted(fn, stager, cons_s, cs_stager),
                                                      _restricted(fn, stager, cons_m, cs_stager))
        # Session-free contrast on the joint common support (pre-fill and stager labelled, both consensuses exist).
        d_auto = _diff(_restricted(fn, auto, cons_s, joint), _restricted(fn, auto, cons_m, joint))
        d_stager = _diff(_restricted(fn, stager, cons_s, joint), _restricted(fn, stager, cons_m, joint))
        out[f"session_free_contrast_{metric}"] = _diff(d_auto, d_stager)
    return out


def _stager_summary(per_rec: Sequence[Mapping[str, Any]], boot: Mapping[str, Any]) -> dict[str, Any]:
    n_sc = len(per_rec[0]["toward_stager"])
    cells = lambda key: [[r[key][s] for r in per_rec] for s in range(n_sc)]
    out = {
        "toward_stager": _cells_summary(cells("toward_stager"), boot),
        "toward_prefill": _cells_summary(cells("toward_prefill"), boot),
        "toward_stager_by_recording": [_mean([v for v in r["toward_stager"] if v is not None]) for r in per_rec],
        "toward_prefill_by_recording": [_mean([v for v in r["toward_prefill"] if v is not None]) for r in per_rec],
        "mean_delta": _mean([r["delta"] for r in per_rec]),
        "n_delta_negative": sum(r["delta"] < 0 for r in per_rec),
    }
    sides = [r["side_taking_toward_stager"] for r in per_rec]
    n = sum(x["n_changed"] for x in sides)
    out["side_taking_toward_stager_pooled"] = {
        "n_changed": n,
        "assisted_equals_stager": sum(x["n_assisted_equals"] for x in sides) / n if n else None,
        "manual_equals_stager": sum(x["n_manual_equals"] for x in sides) / n if n else None,
    }
    for metric, _ in STAGE_METRICS:
        vals = [r[f"session_free_contrast_{metric}"] for r in per_rec]
        out[f"session_free_contrast_{metric}"] = {"by_recording": vals, "mean": _mean([v for v in vals if v is not None]),
                                                  "n_positive": sum(v is not None and v > 0 for v in vals)}
        dvals = [r[f"delta_common_support_{metric}"] for r in per_rec]
        out[f"delta_common_support_{metric}"] = {"by_recording": dvals, "mean": _mean([v for v in dvals if v is not None])}
    return out


def run_checks(config5_path: Path, config1_path: Path, data_root: Path, yasa_labels_path: Path, output_path: Path,
               gssc_labels_path: Path | None = None, verify: bool = True) -> dict[str, Any]:
    c5 = json.loads(Path(config5_path).read_text(encoding="utf-8"))
    c1 = json.loads(Path(config1_path).read_text(encoding="utf-8"))
    root, repo = Path(data_root), Path(config5_path).resolve().parents[2]
    if verify:
        verify_checksums(root, c1["dataset"]["checksum_file"], c1["dataset"]["expected_files"])
    n_sc, epoch = int(c1["n_scorers"]), c1["epoch_seconds"]
    full, loo = int(c1["consensus_majority"]["full"]), int(c1["consensus_majority"]["leave_one_out"])
    grid, boot = float(c1["event_grid_seconds"]), c5["bootstrap"]
    rule = c5["c1_rejected_label_adoption"]
    min_other, cmp_rule = int(rule["min_other_rejecting"]), rule["comparison_rule"]
    blocks_cfg, min_dur = c5["c4_block_audit"], c5["c6_event_min_duration_s"]
    stagers = {"yasa": _load_labels(yasa_labels_path), "gssc": _load_labels(gssc_labels_path)}
    stage_task = c1["secondary_algorithm"]["task"]
    m5 = {r["recording"]: r for r in json.loads((repo / c5["stager_cache_check"]["m5_report"])
                                                .read_text(encoding="utf-8"))["recordings"]}
    m5_diffs: list[float] = []

    c1_out: dict[str, Any] = {}
    unit_lifts: list[float] = []
    stager_recs: dict[str, list[dict[str, Any]]] = {"yasa": [], "gssc": []}
    c3_recs: list[dict[str, Any]] = []
    c4_units: dict[str, list[list[list[tuple[float, float]]]]] = {"prefill": [], "yasa": [], "gap": []}
    d0_gap: list[float] = []
    c6_out: dict[str, Any] = {}
    c6_units: list[float] = []
    for task, spec in c1["tasks"].items():
        cells = [[] for _ in range(n_sc)]
        cmp_cells = [[] for _ in range(n_sc)]
        pairs, cmp_pairs, by_rec, c6_rec = 0, 0, [], []
        for rec in _recordings(root, task, spec["file_token"]):
            d = _load(root, task, spec, c1, rec)
            name, auto, man, semi = f"SN{rec}", d["auto"], d["manual"], d["semiauto"]
            if spec["kind"] == "stages":
                lifts = rejected_label_lift(auto, man, semi, min_other)
                cmp_lifts = None
            else:
                lifts = event_rejection_lift(auto, man, semi, min_other, include_self=False)
                cmp_lifts = event_rejection_lift(auto, man, semi, int(cmp_rule["min_rejecting_including_scored"]),
                                                 include_self=True)
                dauto, dhuman = m2_event_min_duration(auto, man, semi, full, loo, grid, d["window"], float(min_dur[task]))
                c6_rec.append({"recording": name, "delta_auto": dauto, "delta_human": _mean(dhuman),
                               "did": dauto - _mean(dhuman)})
                c6_units.append(dauto - _mean(dhuman))
            for s, (n, lift) in enumerate(lifts):
                cells[s].append(lift)
                pairs += n
            if cmp_lifts is not None:
                for s, (n, lift) in enumerate(cmp_lifts):
                    cmp_cells[s].append(lift)
                    cmp_pairs += n
            vals = [lift for _, lift in lifts if lift is not None]
            unit = _mean(vals) if vals else None
            by_rec.append({"recording": name, "mean_lift": unit, "scorer_unit_pairs": sum(n for n, _ in lifts)})
            if unit is not None:
                unit_lifts.append(unit)
            if task == stage_task:
                cons_m, cons_s = consensus_stages(man, full), consensus_stages(semi, full)
                for key, cons in (("kappa_stager_vs_manual_consensus", cons_m),
                                  ("kappa_stager_vs_assisted_consensus", cons_s)):
                    m5_diffs.append(abs(stage_agreement(stagers["yasa"][name], cons) - m5[name][key]))
                for sname, labels in stagers.items():
                    if labels is not None:
                        stager_recs[sname].append({"recording": name, **_stager_block(labels[name], auto, man, semi,
                                                                                      cons_m, cons_s)})
                # C3: the pre-fill's own gain and the human change on common support.
                cs = sorted(k for k, a in auto.items() if a is not None and k in cons_m and k in cons_s)
                human = {m: [] for m, _ in STAGE_METRICS}
                for s in range(n_sc):
                    lm = consensus_stages([x for i, x in enumerate(man) if i != s], loo)
                    ls = consensus_stages([x for i, x in enumerate(semi) if i != s], loo)
                    keys = sorted(k for k, v in man[s].items() if v is not None and k in lm and k in ls)
                    for metric, fn in STAGE_METRICS:
                        human[metric].append(_diff(_restricted(fn, man[s], ls, keys), _restricted(fn, man[s], lm, keys)))
                row: dict[str, Any] = {"recording": name, "epochs": len(cs)}
                for metric, fn in STAGE_METRICS:
                    dauto = _diff(_restricted(fn, auto, cons_s, cs), _restricted(fn, auto, cons_m, cs))
                    dh = _mean([v for v in human[metric] if v is not None])
                    row[f"delta_auto_{metric}"], row[f"delta_human_{metric}"] = dauto, dh
                    row[f"did_{metric}"] = _diff(dauto, dh)
                c3_recs.append(row)
                # C4: block audit units, population as amendment 004's B1.
                yasa = stagers["yasa"][name]
                pop = sorted(k for k, a in auto.items() if a is not None and yasa.get(k) is not None and k in cons_m)
                units = {}
                for k in pop:
                    ya, yy = float(auto[k] == cons_m[k]), float(yasa[k] == cons_m[k])
                    sa = float(auto[k] == cons_s[k]) if k in cons_s else 0.0
                    sy = float(yasa[k] == cons_s[k]) if k in cons_s else 0.0
                    units[k] = {"prefill": (ya, sa), "yasa": (yy, sy), "gap": (ya - yy, sa - sy)}
                    if k in cons_s:
                        d0_gap.append(sa - sy)
                blocks = epoch_blocks(pop, int(blocks_cfg["block_epochs"]), min(auto))
                for q in c4_units:
                    c4_units[q].append([[units[k][q] for k in ks] for ks in blocks.values()])
        c1_out[task] = {"loo_rule": {**_cells_summary(cells, boot), "scorer_unit_pairs": pairs},
                        "by_recording": by_rec}
        if spec["kind"] == "events":
            c1_out[task]["r4_rule_event_level"] = {**_cells_summary(cmp_cells, boot), "scorer_unit_pairs": cmp_pairs}
            c6_out[task] = {"min_duration_s": float(min_dur[task]), "by_recording": c6_rec,
                            "did_mean": _mean([r["did"] for r in c6_rec])}
    check = {"max_abs_difference": max(m5_diffs), "tolerance": float(c5["stager_cache_check"]["tolerance"])}
    check["passed"] = check["max_abs_difference"] <= check["tolerance"]
    if not check["passed"]:
        raise AnalysisError(f"YASA labels do not reproduce M5 (difference {check['max_abs_difference']})")

    c1_report = {"tasks": c1_out, "sign_test": {"n_units": len(unit_lifts),
                                                "n_positive": sum(u > 0 for u in unit_lifts), "p": sign_test(unit_lifts)}}
    stagers_out = {s: {"by_recording": recs, **_stager_summary(recs, boot)} for s, recs in stager_recs.items() if recs}
    c3_report: dict[str, Any] = {"by_recording": c3_recs}
    for metric, _ in STAGE_METRICS:
        da = [r[f"delta_auto_{metric}"] for r in c3_recs]
        c3_report[metric] = {"delta_auto_mean": _mean(da), "n_delta_auto_positive": sum(v > 0 for v in da),
                             "did_mean": _mean([r[f"did_{metric}"] for r in c3_recs])}
    c4: dict[str, Any] = {"population_epochs": sum(len(b) for s in c4_units["prefill"] for b in s), "targets": {}}
    fractions = [float(f) for f in blocks_cfg["audit_fractions"]]
    for q in c4_units:
        audits = {f: block_audit_precision(c4_units[q], f) for f in fractions}
        c4["targets"][q] = {"target": audits[fractions[0]]["target"], "audits": {
            str(f): {"expected_share": a["expected_share"], "audited_blocks": sum(a["audited_blocks_per_stratum"]),
                     "blocks": sum(a["blocks_per_stratum"]), "d1_halfwidth": 1.96 * a["d1_se"],
                     "d2_halfwidth": 1.96 * a["d2_se"]} for f, a in audits.items()}}
    gap_bias = _mean(d0_gap) - c4["targets"]["gap"]["target"]
    c4["d0_gap_bias"] = gap_bias
    c4["smallest_f_D2_halfwidth_below_D0_gap_bias"] = next(
        (f for f in fractions if c4["targets"]["gap"]["audits"][str(f)]["d2_halfwidth"] < abs(gap_bias)), None)
    c6_report = {"tasks": c6_out, "sign_test": {"n_units": len(c6_units), "n_positive": sum(u > 0 for u in c6_units),
                                                "p": sign_test(c6_units)}}

    # Predictions (amendment 005, Part C) and the text rules of Part E.
    reports = "newpaper/research_selection_2026-09-26_novelty/"
    r4 = json.loads((repo / c5.get("r4_report", reports + "psg_assist_bias_002_report.json"))
                    .read_text(encoding="utf-8"))["R4_error_following"]
    b1 = json.loads((repo / c5.get("b1_report", reports + "psg_assist_bias_004_report.json"))
                    .read_text(encoding="utf-8"))["B1_emulation"]
    epoch_fracs = sorted(float(f) for f in b1["targets"]["gap"]["audits"])
    nearest = lambda f: min(epoch_fracs, key=lambda e: abs(e - f))
    task_means = {t: v["loo_rule"]["mean"] for t, v in c1_out.items()}
    yasa_sum = stagers_out["yasa"]
    predictions: dict[str, Any] = {
        "C1": {"supported": all(m is not None and m > 0 for m in task_means.values()) and c1_report["sign_test"]["p"] < 0.05
               and task_means[stage_task] < r4[stage_task]["mean"],
               "stage_r4_mean": r4[stage_task]["mean"]},
        "C2": {"supported": yasa_sum["toward_stager"]["mean"] <= 0 < yasa_sum["toward_prefill"]["mean"]},
        "C3": {"supported": c3_report["kappa"]["n_delta_auto_positive"] == len(c3_recs)
               and yasa_sum["session_free_contrast_kappa"]["n_positive"] >= len(c3_recs) - 1},
        "C4": {"supported": all(c4["targets"][q]["audits"][str(f)]["d2_halfwidth"]
                                > b1["targets"][q]["audits"][str(nearest(f))]["d2_halfwidth"]
                                for q in c4["targets"] for f in fractions)
               and (c4["smallest_f_D2_halfwidth_below_D0_gap_bias"] is None
                    or c4["smallest_f_D2_halfwidth_below_D0_gap_bias"] > float(b1["smallest_f_D2_halfwidth_below_D0_gap_bias"]))},
        "C6": {"supported": all(v["did_mean"] > 0 for v in c6_out.values()) and c6_report["sign_test"]["n_positive"] >= 13},
    }
    if "gssc" in stagers_out:
        g = stagers_out["gssc"]
        predictions["C5"] = {"supported": g["mean_delta"] < 0 and _mean([r["lead_of_prefill_vs_assisted"] for r in g["by_recording"]])
                             > _mean([r["lead_of_prefill_vs_manual"] for r in g["by_recording"]])}
    else:
        predictions["C5"] = {"supported": None, "note": "GSSC labels not supplied"}
    ci = yasa_sum["toward_stager"]["ci95"]
    text_rules = {
        "C1_keep_rejected_label_argument": c1_report["sign_test"]["p"] < 0.05
        and all(m is not None and m > 0 for m in task_means.values()),
        "C2_shift_not_specific_to_prefill": yasa_sum["toward_stager"]["mean"] > 0 and ci is not None and ci[0] > 0,
        "C4_block_audit_share": c4["smallest_f_D2_halfwidth_below_D0_gap_bias"],
    }
    report = {"protocol": c5["protocol"], "amendment": c5["amendment"], "frozen_at": c5["frozen_at"],
              "stager_cache_check": check, "C1_rejected_label_adoption": c1_report,
              "C2_C5_independent_stagers": stagers_out, "C3_common_support": c3_report, "C4_block_audit": c4,
              "C6_event_min_duration": c6_report, "predictions": predictions, "text_rules": text_rules}
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    return json.loads(output_path.read_text(encoding="utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=Path, required=True, help="amendment 005 config")
    parser.add_argument("--base-config", type=Path, required=True, help="protocol 001 config")
    parser.add_argument("--yasa-labels", type=Path, required=True, help="regenerated YASA labels (outputs/)")
    parser.add_argument("--gssc-labels", type=Path, help="GSSC labels (outputs/), if C5 was done")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    env = json.loads(args.base_config.read_text(encoding="utf-8"))["data_root_env"]
    root = os.environ.get(env)
    if not root:
        print(f"Set {env} to the psg-ipa/1.0.0 folder.", file=sys.stderr)
        return 2
    report = run_checks(args.config, args.base_config, Path(root), args.yasa_labels, args.output, args.gssc_labels)
    print(json.dumps({k: report[k] for k in ("stager_cache_check", "predictions", "text_rules")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
