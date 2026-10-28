"""Amendment 002 analyses for the assisted-scoring bias study (PSG-IPA).

Secondary and descriptive: acceptance lift by pre-fill stage (R1), respiratory
event types (R2), dependence on manual ambiguity (R3), following of likely
pre-fill errors (R4), scorer consistency across tasks (R5) and robustness of
the protocol 001 conclusions to analysis choices (R6).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from careport.psg_assist_bias import (
    Interval,
    _analyse_task,
    _coverage,
    _mean,
    _recordings,
    event_f1,
    events_in_window,
    lights_window,
    read_annotations,
    sign_test,
    stage_epochs,
    verify_checksums,
)


def consensus_plurality(scorings: Sequence[Mapping[int, str | None]], _min_votes: int = 0) -> dict[int, str]:
    """Most frequent label per epoch; epochs with a tied top count are left out."""
    out = {}
    for k in sorted(set().union(*scorings)):
        votes: dict[str, int] = {}
        for s in scorings:
            label = s.get(k)
            if label is not None:
                votes[label] = votes.get(label, 0) + 1
        if votes:
            top = max(votes.values())
            winners = [lab for lab, c in votes.items() if c == top]
            if len(winners) == 1:
                out[k] = winners[0]
    return out


def stage_percent_agreement(x: Mapping[int, str | None], y: Mapping[int, str | None]) -> float:
    keys = [k for k in x.keys() & y.keys() if x[k] is not None and y[k] is not None]
    return sum(x[k] == y[k] for k in keys) / len(keys) if keys else float("nan")


def event_f1_iou(ref: Sequence[Interval], pred: Sequence[Interval], min_iou: float) -> float:
    """Event F1 with one-to-one matching that requires IoU >= min_iou (largest IoU first)."""
    if not ref and not pred:
        return 1.0
    pairs = []
    for i, (rs, re_) in enumerate(ref):
        for j, (ps, pe) in enumerate(pred):
            inter = min(re_, pe) - max(rs, ps)
            if inter > 0:
                iou = inter / (max(re_, pe) - min(rs, ps))
                if iou >= min_iou:
                    pairs.append((-iou, i, j))
    used_r, used_p = set(), set()
    for _, i, j in sorted(pairs):
        if i not in used_r and j not in used_p:
            used_r.add(i)
            used_p.add(j)
    tp = len(used_r)
    return 2 * tp / (2 * tp + (len(pred) - tp) + (len(ref) - tp))


def acceptance_lift_by_stage(auto: Mapping[int, str | None], manual: Mapping[int, str | None],
                             semi: Mapping[int, str | None], stages: Sequence[str]) -> dict[str, tuple[int, float | None]]:
    """Per pre-fill stage: (n epochs, P(semi = pre-fill) - P(manual = pre-fill))."""
    out = {}
    for x in stages:
        keys = [k for k, v in auto.items() if v == x and manual.get(k) is not None and semi.get(k) is not None]
        if not keys:
            out[x] = (0, None)
            continue
        out[x] = (len(keys), sum((semi[k] == x) - (manual[k] == x) for k in keys) / len(keys))
    return out


def _levels(manual: Sequence[Sequence[Any]]) -> list[int]:
    levels = []
    for unit in zip(*manual):
        counts: dict[Any, int] = {}
        for v in unit:
            counts[v] = counts.get(v, 0) + 1
        levels.append(max(counts.values()))
    return levels


def ambiguity_lift(auto: Sequence[Any], manual: Sequence[Sequence[Any]], semi: Sequence[Sequence[Any]],
                   bins: Sequence[Sequence[int]]) -> dict[str, dict[str, Any]]:
    """Acceptance lift per bin of manual agreement level (count of the most frequent manual label)."""
    levels = _levels(manual)
    out = {}
    for lo, hi in bins:
        idx = [i for i, lv in enumerate(levels) if lo <= lv <= hi]
        per_scorer = [sum((s[i] == auto[i]) - (m[i] == auto[i]) for i in idx) / len(idx) if idx else None
                      for m, s in zip(manual, semi)]
        vals = [v for v in per_scorer if v is not None]
        out[f"{lo}-{hi}"] = {"n_units": len(idx), "lift": _mean(vals) if vals else None, "per_scorer": per_scorer}
    return out


def error_following(auto: Sequence[Any], manual: Sequence[Sequence[Any]], semi: Sequence[Sequence[Any]],
                    strong: int) -> tuple[list[float | None], int]:
    """Where a strong manual consensus rejects the pre-fill: per scorer, P(semi = pre-fill) - P(manual = pre-fill)."""
    idx = []
    for i, unit in enumerate(zip(*manual)):
        counts: dict[Any, int] = {}
        for v in unit:
            counts[v] = counts.get(v, 0) + 1
        label, c = max(counts.items(), key=lambda kv: kv[1])
        if c >= strong and label != auto[i]:
            idx.append(i)
    if not idx:
        return [None] * len(manual), 0
    return [sum((s[i] == auto[i]) - (m[i] == auto[i]) for i in idx) / len(idx) for m, s in zip(manual, semi)], len(idx)


def spearman(x: Sequence[float], y: Sequence[float]) -> float:
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry = ranks(x), ranks(y)
    mx, my = _mean(rx), _mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def crossed_bootstrap_nan(matrix: Sequence[Sequence[float | None]], resamples: int, seed: int) -> tuple[float, float]:
    """95% interval of the mean of available cells, resampling rows and columns independently."""
    rng = random.Random(seed)
    rows, cols = len(matrix), len(matrix[0])
    stats = []
    for _ in range(resamples):
        r = [rng.randrange(rows) for _ in range(rows)]
        c = [rng.randrange(cols) for _ in range(cols)]
        vals = [matrix[i][j] for i in r for j in c if matrix[i][j] is not None]
        if vals:
            stats.append(sum(vals) / len(vals))
    stats.sort()
    return stats[int(0.025 * (len(stats) - 1))], stats[int(math.ceil(0.975 * (len(stats) - 1)))]


def _summary(matrix: list[list[float | None]], boot: Mapping[str, Any]) -> dict[str, Any]:
    vals = [v for row in matrix for v in row if v is not None]
    if not vals:
        return {"mean": None, "ci95": None, "n_cells": 0}
    return {"mean": _mean(vals), "ci95": crossed_bootstrap_nan(matrix, boot["resamples"], boot["seed"]), "n_cells": len(vals)}


def run_mechanisms(config2_path: Path, config1_path: Path, data_root: Path, output_path: Path,
                   verify: bool = True) -> dict[str, Any]:
    c2 = json.loads(Path(config2_path).read_text(encoding="utf-8"))
    c1 = json.loads(Path(config1_path).read_text(encoding="utf-8"))
    root = Path(data_root)
    if verify:
        verify_checksums(root, c1["dataset"]["checksum_file"], c1["dataset"]["expected_files"])
    n_sc, grid, epoch = int(c1["n_scorers"]), float(c1["event_grid_seconds"]), c1["epoch_seconds"]
    boot = c2["bootstrap"]
    r1 = {x: [[None] * 0 for _ in range(n_sc)] for x in c2["R1_stages"]}
    r2 = {t: [[] for _ in range(n_sc)] for t in c2["R2_types"]}
    r3, r4 = {}, {}
    for task, spec in c1["tasks"].items():
        token, kind = spec["file_token"], spec["kind"]
        ann = root / task / "Annotations"
        r3_cells = {f"{lo}-{hi}": [[] for _ in range(n_sc)] for lo, hi in c2["R3_bins"]}
        r3_units = {k: 0 for k in r3_cells}
        r4_cells, r4_units = [[] for _ in range(n_sc)], 0
        for rec in _recordings(root, task, token):
            auto_rows = read_annotations(ann / "auto" / f"SN{rec}_{token}_auto.txt")
            window = lights_window(auto_rows, c1["window"]["start_label"], c1["window"]["end_label"])
            rows = {cond: [read_annotations(ann / cond / f"SN{rec}_{token}_{cond}_scorer{s}.txt") for s in range(1, n_sc + 1)]
                    for cond in ("manual", "semiauto")}
            if kind == "stages":
                ex = lambda r: stage_epochs(r, spec["labels"], spec["label_prefix"], window, epoch)
                auto = ex(auto_rows)
                man = [ex(r) for r in rows["manual"]]
                semi = [ex(r) for r in rows["semiauto"]]
                for s in range(n_sc):
                    for x, (n, lift) in acceptance_lift_by_stage(auto, man[s], semi[s], c2["R1_stages"]).items():
                        r1[x][s].append(lift if n else None)
                keys = sorted(k for k, v in auto.items() if v is not None
                              and all(m.get(k) is not None for m in man) and all(x.get(k) is not None for x in semi))
                auto_seq = [auto[k] for k in keys]
                man_seqs = [[m[k] for k in keys] for m in man]
                semi_seqs = [[x[k] for k in keys] for x in semi]
            else:
                ex = lambda r: events_in_window(r, spec["labels"], window)
                auto_seq = _coverage(ex(auto_rows), grid, window)
                man_seqs = [_coverage(ex(r), grid, window) for r in rows["manual"]]
                semi_seqs = [_coverage(ex(r), grid, window) for r in rows["semiauto"]]
                if task == "Resp_events":
                    for t, labels in c2["R2_types"].items():
                        a_t = events_in_window(auto_rows, labels, window)
                        for s in range(n_sc):
                            r2[t][s].append(event_f1(events_in_window(rows["semiauto"][s], labels, window), a_t)
                                            - event_f1(events_in_window(rows["manual"][s], labels, window), a_t))
            amb = ambiguity_lift(auto_seq, man_seqs, semi_seqs, c2["R3_bins"])
            for key, v in amb.items():
                r3_units[key] += v["n_units"]
                for s in range(n_sc):
                    r3_cells[key][s].append(v["per_scorer"][s])
            per_scorer, n_units = error_following(auto_seq, man_seqs, semi_seqs, c2["R4_strong_consensus"])
            r4_units += n_units
            for s in range(n_sc):
                r4_cells[s].append(per_scorer[s])
        r3[task] = {key: {"n_units": r3_units[key], **_summary(r3_cells[key], boot)} for key in r3_cells}
        r4[task] = {"n_units": r4_units, **_summary(r4_cells, boot)}
    # R5 and R6: rerun protocol 001's task analysis (default hooks = R5 baseline; variants = R6).
    baseline = {task: _analyse_task(root, task, spec, c1) for task, spec in c1["tasks"].items()}
    tasks = list(baseline)
    r5 = {f"{a}|{b}": spearman(baseline[a]["M1_anchoring"]["scorer_means"], baseline[b]["M1_anchoring"]["scorer_means"])
          for i, a in enumerate(tasks) for b in tasks[i + 1:]}
    hooks = {
        "plurality_stages": dict(stage_consensus=consensus_plurality),
        "supermajority": {},
        "iou_0.2": dict(event_metric=lambda r, p: event_f1_iou(r, p, c2["R6_variants"]["iou_0.2"]["event_min_iou"])),
        "percent_agreement_stages": dict(stage_metric=stage_percent_agreement),
    }
    r6 = {}
    for name, variant in c2["R6_variants"].items():
        cfg = json.loads(json.dumps(c1))
        if "consensus_majority" in variant:
            cfg["consensus_majority"] = variant["consensus_majority"]
        res = {task: _analyse_task(root, task, spec, cfg, **hooks[name]) for task, spec in cfg["tasks"].items()}
        m1 = [v for t in res.values() for v in t["M1_anchoring"]["recording_means"]]
        did = [v for t in res.values() for v in t["M2_inflation"]["did_by_recording"]]
        r6[name] = {"M1_sign_test": {"n_units": len(m1), "n_positive": sum(v > 0 for v in m1), "p": sign_test(m1)},
                    "M2_sign_test": {"n_units": len(did), "n_positive": sum(v > 0 for v in did), "p": sign_test(did)},
                    "task_M1_mean": {t: v["M1_anchoring"]["mean"] for t, v in res.items()},
                    "task_DiD_mean": {t: v["M2_inflation"]["did_mean"] for t, v in res.items()}}
    report = {
        "protocol": c2["protocol"], "amendment": c2["amendment"], "frozen_at": c2["frozen_at"],
        "R1_lift_by_stage": {x: _summary(r1[x], boot) for x in r1},
        "R2_resp_types": {t: _summary(r2[t], boot) for t in r2},
        "R3_ambiguity": r3,
        "R4_error_following": r4,
        "R5_scorer_consistency_spearman": r5,
        "R6_robustness": r6,
        "baseline_check": {t: v["M1_anchoring"]["mean"] for t, v in baseline.items()},
    }
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    return json.loads(output_path.read_text(encoding="utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=Path, required=True, help="amendment 002 config")
    parser.add_argument("--base-config", type=Path, required=True, help="protocol 001 config")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    env = json.loads(args.base_config.read_text(encoding="utf-8"))["data_root_env"]
    root = os.environ.get(env)
    if not root:
        print(f"Set {env} to the psg-ipa/1.0.0 folder.", file=sys.stderr)
        return 2
    report = run_mechanisms(args.config, args.base_config, Path(root), args.output)
    print(json.dumps({k: report[k] for k in ("R1_lift_by_stage", "R2_resp_types", "R6_robustness")}, indent=1)[:4000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
