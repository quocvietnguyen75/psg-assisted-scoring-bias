"""Assisted-scoring bias in sleep-scoring references (PSG-IPA), protocol 001.

Measures whether semi-automatic scorings move toward the automatic pre-fill
(M1), whether a reference built from them inflates the pre-fill's measured
accuracy relative to independent human raters (M2), where agreement gains
arise (M3) and how clinical indices shift (M4). The protocol is
newpaper/plan/PSG_ASSIST_BIAS_PROTOCOL_001_2026-09-29.md.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import random
import re
import sys
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

Interval = tuple[float, float]
SLEEP_LABELS = ("N1", "N2", "N3", "R")


class AnalysisError(ValueError):
    """Raised when inputs are missing, malformed or fail verification."""


@dataclass(frozen=True)
class Annotation:
    onset: float
    duration: float
    label: str


def parse_annotation_lines(lines: Iterable[str]) -> list[Annotation]:
    rows = list(csv.reader(lines, skipinitialspace=True))
    if not rows or [c.strip() for c in rows[0][:5]] != ["Date", "Time", "Recording onset", "Duration", "Annotation"]:
        raise AnalysisError("unexpected annotation header")
    out = []
    for row in rows[1:]:
        if len(row) < 5 or not row[2].strip():
            continue
        out.append(Annotation(float(row[2]), float(row[3] or 0.0), row[4].strip()))
    return out


def read_annotations(path: Path) -> list[Annotation]:
    if not path.is_file():
        raise AnalysisError(f"missing annotation file: {path.name}")
    with open(path, encoding="utf-8", errors="replace", newline="") as fh:
        return parse_annotation_lines(fh)


def lights_window(rows: Sequence[Annotation], start_label: str, end_label: str) -> Interval:
    starts = [a.onset for a in rows if a.label == start_label]
    ends = [a.onset for a in rows if a.label == end_label]
    if len(starts) != 1 or len(ends) != 1 or ends[0] <= starts[0]:
        raise AnalysisError("expected exactly one lights-off before one lights-on")
    return starts[0], ends[0]


def stage_epochs(rows: Sequence[Annotation], labels: Sequence[str], prefix: str,
                 window: Interval, epoch_seconds: float) -> dict[int, str | None]:
    """Epoch index -> stage label (None when unscored), for epochs whose midpoint is in the window."""
    epochs: dict[int, str | None] = {}
    for a in rows:
        if not a.label.startswith(prefix) or abs(a.duration - epoch_seconds) > 1e-6:
            continue
        mid = a.onset + epoch_seconds / 2
        if not window[0] <= mid <= window[1]:
            continue
        stage = a.label[len(prefix):].strip()
        epochs[int(round(a.onset / epoch_seconds))] = stage if stage in labels else None
    return epochs


def events_in_window(rows: Sequence[Annotation], labels: Sequence[str], window: Interval) -> list[Interval]:
    out = []
    for a in rows:
        if a.label not in labels:
            continue
        start, end = max(a.onset, window[0]), min(a.onset + a.duration, window[1])
        if end > start:
            out.append((start, end))
    return sorted(out)


def cohen_kappa(a: Sequence[str], b: Sequence[str]) -> float:
    if len(a) != len(b) or not a:
        raise AnalysisError("kappa needs two equal, non-empty label sequences")
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    cats = set(a) | set(b)
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    if pe >= 1.0:
        return 1.0 if po >= 1.0 else 0.0
    return (po - pe) / (1 - pe)


def stage_agreement(x: Mapping[int, str | None], y: Mapping[int, str | None]) -> float:
    keys = sorted(k for k in x.keys() & y.keys() if x[k] is not None and y[k] is not None)
    return cohen_kappa([x[k] for k in keys], [y[k] for k in keys])


def match_events(ref: Sequence[Interval], pred: Sequence[Interval]) -> tuple[int, int, int]:
    """One-to-one matching of overlapping events, largest overlaps first; returns (tp, fp, fn)."""
    pairs = []
    for i, (rs, re_) in enumerate(ref):
        for j, (ps, pe) in enumerate(pred):
            overlap = min(re_, pe) - max(rs, ps)
            if overlap > 0:
                pairs.append((-overlap, i, j))
    used_r, used_p = set(), set()
    for _, i, j in sorted(pairs):
        if i not in used_r and j not in used_p:
            used_r.add(i)
            used_p.add(j)
    tp = len(used_r)
    return tp, len(pred) - tp, len(ref) - tp


def event_f1(ref: Sequence[Interval], pred: Sequence[Interval]) -> float:
    if not ref and not pred:
        return 1.0
    tp, fp, fn = match_events(ref, pred)
    return 2 * tp / (2 * tp + fp + fn)


def consensus_stages(scorings: Sequence[Mapping[int, str | None]], min_votes: int) -> dict[int, str]:
    out = {}
    for k in sorted(set().union(*scorings)):
        votes: dict[str, int] = {}
        for s in scorings:
            label = s.get(k)
            if label is not None:
                votes[label] = votes.get(label, 0) + 1
        if votes:
            label, count = max(votes.items(), key=lambda kv: kv[1])
            if count >= min_votes:
                out[k] = label
    return out


def _coverage(events: Sequence[Interval], grid: float, window: Interval) -> list[int]:
    """1 for grid bins touched by any event of one scoring, else 0."""
    n = int(math.ceil((window[1] - window[0]) / grid - 1e-9))
    diff = [0] * (n + 1)
    for start, end in events:
        a = max(0, int(math.floor((start - window[0]) / grid + 1e-9)))
        b = min(n, int(math.ceil((end - window[0]) / grid - 1e-9)))
        if b > a:
            diff[a] += 1
            diff[b] -= 1
    out, running = [0] * n, 0
    for i in range(n):
        running += diff[i]
        out[i] = 1 if running > 0 else 0
    return out


def _bin_counts(scorings: Sequence[Sequence[Interval]], grid: float, window: Interval) -> list[int]:
    return [sum(col) for col in zip(*(_coverage(ev, grid, window) for ev in scorings))]


def _segments(flags: Sequence[bool], grid: float, window: Interval) -> list[Interval]:
    out, start = [], None
    for i, flag in enumerate(list(flags) + [False]):
        if flag and start is None:
            start = i
        elif not flag and start is not None:
            out.append((window[0] + start * grid, window[0] + i * grid))
            start = None
    return out


def consensus_events(scorings: Sequence[Sequence[Interval]], min_votes: int, grid: float,
                     window: Interval) -> list[Interval]:
    counts = _bin_counts(scorings, grid, window)
    return _segments([c >= min_votes for c in counts], grid, window)


def pairwise_agreement(sequences: Sequence[Sequence[Any]]) -> float:
    """Pooled fraction of agreeing scorer pairs over units (all sequences equally long)."""
    agree = total = 0
    for unit in zip(*sequences):
        for x, y in combinations(unit, 2):
            agree += x == y
            total += 1
    return agree / total if total else float("nan")


def sign_test(values: Sequence[float]) -> float:
    nonzero = [v for v in values if v != 0]
    n, k = len(nonzero), sum(v > 0 for v in nonzero)
    if n == 0:
        return 1.0
    lower = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    upper = sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n
    return min(1.0, 2 * min(lower, upper))


def crossed_bootstrap(matrix: Sequence[Sequence[float]], resamples: int, seed: int) -> tuple[float, float]:
    """95% percentile interval of the grand mean, resampling rows and columns independently."""
    rng = random.Random(seed)
    rows, cols = len(matrix), len(matrix[0])
    stats = []
    for _ in range(resamples):
        r = [rng.randrange(rows) for _ in range(rows)]
        c = [rng.randrange(cols) for _ in range(cols)]
        stats.append(sum(matrix[i][j] for i in r for j in c) / (rows * cols))
    stats.sort()
    return stats[int(0.025 * (resamples - 1))], stats[int(math.ceil(0.975 * (resamples - 1)))]


def verify_checksums(root: Path, checksum_file: str, expected: int | None) -> int:
    listed = {}
    for text in (root / checksum_file).read_text(encoding="utf-8").splitlines():
        parts = text.strip().split(maxsplit=1)
        if len(parts) == 2:
            listed[parts[1].lstrip("*")] = parts[0]
    if expected is not None and len(listed) != expected:
        raise AnalysisError(f"checksum list has {len(listed)} files, expected {expected}")
    for rel, digest in listed.items():
        path = root / rel
        if not path.is_file():
            raise AnalysisError(f"missing file: {rel}")
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for block in iter(lambda: fh.read(1 << 20), b""):
                h.update(block)
        if h.hexdigest() != digest:
            raise AnalysisError(f"checksum mismatch: {rel}")
    return len(listed)


def _recordings(root: Path, task: str, token: str) -> list[int]:
    found = sorted(int(m.group(1)) for p in (root / task / "Annotations" / "auto").glob(f"SN*_{token}_auto.txt")
                   if (m := re.match(r"SN(\d+)_", p.name)))
    if not found:
        raise AnalysisError(f"{task}: no automatic pre-fill files")
    return found


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def _binary_bins(events: Sequence[Interval], grid: float, window: Interval) -> list[bool]:
    return [c > 0 for c in _bin_counts([events], grid, window)]


def _analyse_task(root: Path, task: str, spec: Mapping[str, Any], config: Mapping[str, Any],
                  stage_metric: Any = None, event_metric: Any = None, stage_consensus: Any = None) -> dict[str, Any]:
    """Protocol 001 analysis of one task. The optional hooks exist for amendment 002 robustness variants;
    the defaults reproduce protocol 001 exactly."""
    stage_metric = stage_metric or stage_agreement
    event_metric = event_metric or event_f1
    stage_consensus = stage_consensus or consensus_stages
    token, kind = spec["file_token"], spec["kind"]
    n_sc = int(config["n_scorers"])
    full, loo = config["consensus_majority"]["full"], config["consensus_majority"]["leave_one_out"]
    grid = float(config["event_grid_seconds"])
    ann = root / task / "Annotations"
    boot = config["inference"]
    m1_matrix, did_matrix, recs_out = [], [], []
    m3_acc: dict[str, list[float]] = {"agree_manual": [], "agree_semi": [], "disagree_manual": [], "disagree_semi": []}
    m4 = []
    recordings = _recordings(root, task, token)
    for rec in recordings:
        auto_rows = read_annotations(ann / "auto" / f"SN{rec}_{token}_auto.txt")
        window = lights_window(auto_rows, config["window"]["start_label"], config["window"]["end_label"])
        paths = {cond: [ann / cond / f"SN{rec}_{token}_{cond}_scorer{s}.txt" for s in range(1, n_sc + 1)]
                 for cond in ("manual", "semiauto")}
        if kind == "stages":
            extract = lambda rows: stage_epochs(rows, spec["labels"], spec["label_prefix"], window,
                                                config["epoch_seconds"])
            agree = stage_metric
            consensus = stage_consensus
        else:
            extract = lambda rows: events_in_window(rows, spec["labels"], window)
            agree = event_metric
            consensus = lambda sc, k: consensus_events(sc, k, grid, window)
        auto = extract(auto_rows)
        scorings = {cond: [extract(read_annotations(p)) for p in ps] for cond, ps in paths.items()}
        # M1: anchoring toward the pre-fill, per scorer.
        delta_a = [agree(scorings["semiauto"][s], auto) - agree(scorings["manual"][s], auto) for s in range(n_sc)]
        # M2: inflation of the pre-fill versus independent human raters.
        if kind == "events":
            # Per-scoring grid coverage computed once; leave-one-out counts are full counts minus one scoring.
            cover = {cond: [_coverage(ev, grid, window) for ev in scorings[cond]] for cond in scorings}
            counts = {cond: [sum(col) for col in zip(*cover[cond])] for cond in cover}
            cons = {cond: _segments([c >= full for c in counts[cond]], grid, window) for cond in counts}
            loo_cons_of = lambda cond, s: _segments(
                [c - x >= loo for c, x in zip(counts[cond], cover[cond][s])], grid, window)
        else:
            cons = {cond: consensus(scorings[cond], full) for cond in scorings}
            loo_cons_of = lambda cond, s: consensus([x for i, x in enumerate(scorings[cond]) if i != s], loo)
        delta_auto = agree(cons["semiauto"], auto) - agree(cons["manual"], auto) if kind == "events" else \
            stage_metric(auto, cons["semiauto"]) - stage_metric(auto, cons["manual"])
        delta_human = [agree(scorings["manual"][s], loo_cons_of("semiauto", s))
                       - agree(scorings["manual"][s], loo_cons_of("manual", s)) for s in range(n_sc)]
        m1_matrix.append(delta_a)
        did_matrix.append([delta_auto - d for d in delta_human])
        recs_out.append({"recording": f"SN{rec}", "mean_delta_a": _mean(delta_a), "delta_auto": delta_auto,
                         "delta_human": _mean(delta_human), "did": delta_auto - _mean(delta_human)})
        # M3: where inter-scorer agreement gains arise.
        if kind == "stages":
            keys = sorted(k for k in cons["manual"] if auto.get(k) is not None
                          and all(sc.get(k) is not None for c in scorings for sc in scorings[c]))
            split = {"agree": [k for k in keys if auto[k] == cons["manual"][k]],
                     "disagree": [k for k in keys if auto[k] != cons["manual"][k]]}
            for part, ks in split.items():
                for cond, name in (("manual", "manual"), ("semiauto", "semi")):
                    if ks:
                        m3_acc[f"{part}_{name}"].append(pairwise_agreement([[sc[k] for k in ks] for sc in scorings[cond]]))
        else:
            auto_bins = _binary_bins(auto, grid, window)
            for part in ("agree", "disagree"):
                for cond, name in (("manual", "manual"), ("semiauto", "semi")):
                    agree_pairs = total_pairs = 0
                    for i, k in enumerate(counts["manual"]):
                        decision = True if k >= full else False if n_sc - k >= full else None
                        if decision is None or (auto_bins[i] == decision) != (part == "agree"):
                            continue
                        e = counts[cond][i]
                        agree_pairs += math.comb(e, 2) + math.comb(n_sc - e, 2)
                        total_pairs += math.comb(n_sc, 2)
                    if total_pairs:
                        m3_acc[f"{part}_{name}"].append(agree_pairs / total_pairs)
            # M4: clinical indices per hour of sleep from the pre-fill's context stages.
            context = stage_epochs(auto_rows, SLEEP_LABELS + ("W",), "Sleep stage ", window, config["epoch_seconds"])
            hours = sum(1 for v in context.values() if v in SLEEP_LABELS) * config["epoch_seconds"] / 3600
            if hours > 0:
                idx = {"auto": len(auto) / hours, "manual_consensus": len(cons["manual"]) / hours,
                       "semi_consensus": len(cons["semiauto"]) / hours}
                m4.append({"recording": f"SN{rec}", **{k: round(v, 3) for k, v in idx.items()},
                           "auto_error_vs_manual": round(abs(idx["auto"] - idx["manual_consensus"]), 3),
                           "auto_error_vs_semi": round(abs(idx["auto"] - idx["semi_consensus"]), 3)})
    m1_t = [list(col) for col in zip(*m1_matrix)]
    did_t = [list(col) for col in zip(*did_matrix)]
    result = {
        "kind": kind,
        "n_recordings": len(recordings),
        "M1_anchoring": {
            "mean": _mean([v for row in m1_matrix for v in row]),
            "recording_means": [r["mean_delta_a"] for r in recs_out],
            "scorer_means": [_mean(col) for col in m1_t],
            "ci95": crossed_bootstrap(m1_t, boot["bootstrap_resamples"], boot["bootstrap_seed"]),
        },
        "M2_inflation": {
            "delta_auto_by_recording": [r["delta_auto"] for r in recs_out],
            "delta_human_by_recording": [r["delta_human"] for r in recs_out],
            "did_by_recording": [r["did"] for r in recs_out],
            "did_mean": _mean([r["did"] for r in recs_out]),
            "did_ci95": crossed_bootstrap(did_t, boot["bootstrap_resamples"], boot["bootstrap_seed"]),
        },
        "M3_agreement_gain": {k: (_mean(v) if v else None) for k, v in m3_acc.items()},
        "recordings": recs_out,
    }
    if kind == "events":
        result["M4_indices"] = m4
    return result


def run(config_path: Path, data_root: Path, output_path: Path, verify: bool = True) -> dict[str, Any]:
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    root = Path(data_root)
    verified = verify_checksums(root, config["dataset"]["checksum_file"], config["dataset"]["expected_files"]) \
        if verify else None
    tasks = {task: _analyse_task(root, task, spec, config) for task, spec in config["tasks"].items()}
    m1_units = [v for t in tasks.values() for v in t["M1_anchoring"]["recording_means"]]
    did_units = [v for t in tasks.values() for v in t["M2_inflation"]["did_by_recording"]]
    alpha, material = config["inference"]["sign_test_alpha"], config["decision"]["material_effect"]
    p1, p2 = sign_test(m1_units), sign_test(did_units)
    positive = (p1 < alpha and p2 < alpha and sum(v > 0 for v in m1_units) > len(m1_units) / 2
                and sum(v > 0 for v in did_units) > len(did_units) / 2
                and any(t["M1_anchoring"]["mean"] >= material for t in tasks.values()))
    null = (p1 >= alpha and p2 >= alpha
            and all(t["M1_anchoring"]["ci95"][1] < material and t["M2_inflation"]["did_ci95"][1] < material
                    for t in tasks.values()))
    report = {
        "protocol": config["protocol"],
        "version": config["version"],
        "frozen_at": config["frozen_at"],
        "files_verified": verified,
        "tasks": tasks,
        "primary": {
            "M1_sign_test": {"n_units": len(m1_units), "n_positive": sum(v > 0 for v in m1_units), "p": p1},
            "M2_sign_test": {"n_units": len(did_units), "n_positive": sum(v > 0 for v in did_units), "p": p2},
            "decision": "positive" if positive else "null" if null else "inconclusive",
        },
    }
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    return json.loads(output_path.read_text(encoding="utf-8"))


STAGE_NAMES = {"W": "W", "WAKE": "W", "N1": "N1", "N2": "N2", "N3": "N3", "R": "R", "REM": "R"}


def normalize_stage_labels(labels: Iterable[Any]) -> list[str | None]:
    """Map stager output (e.g. YASA's WAKE/REM) to W/N1/N2/N3/R; anything else is unscored."""
    return [STAGE_NAMES.get(str(x).strip().upper()) for x in labels]


def choose_channels(labels: Sequence[str]) -> tuple[str, str, str]:
    """Protocol 001 M5 rule: C4-M1, else Cz-M1; left EOG E1-M2; chin EMG."""
    eeg = next((c for c in ("EEG C4-M1", "EEG Cz-M1") if c in labels), None)
    eog = "EOG E1-M2" if "EOG E1-M2" in labels else None
    emg = "EMG chin" if "EMG chin" in labels else None
    if eeg is None or eog is None or emg is None:
        raise AnalysisError("recording lacks the channels required for M5")
    return eeg, eog, emg


def edf_labels(path: Path) -> list[str]:
    """Signal labels from an EDF header (standard library only)."""
    with open(path, "rb") as fh:
        head = fh.read(256)
        ns = int(head[252:256].decode("ascii").strip())
        block = fh.read(ns * 16)
    return [block[i * 16:(i + 1) * 16].decode("ascii", errors="replace").strip() for i in range(ns)]


def _stager_epochs(labels: Sequence[str | None], window: Interval, epoch: float) -> dict[int, str | None]:
    """Stager output on the 30-second epochs whose midpoint lies in the analysis window (M5 rule)."""
    return {i: lab for i, lab in enumerate(labels) if window[0] <= i * epoch + epoch / 2 <= window[1]}


def stager_labels(config_path: Path, data_root: Path, stager: Any,
                  channel_reader: Any = edf_labels) -> dict[str, dict[int, str | None]]:
    """Per recording, the stager's labels as M5 used them (for analyses that need per-epoch output)."""
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    root = Path(data_root)
    task = config["secondary_algorithm"]["task"]
    token, epoch = config["tasks"][task]["file_token"], config["epoch_seconds"]
    out = {}
    for rec in _recordings(root, task, token):
        auto_rows = read_annotations(root / task / "Annotations" / "auto" / f"SN{rec}_{token}_auto.txt")
        window = lights_window(auto_rows, config["window"]["start_label"], config["window"]["end_label"])
        edf = root / task / "PSG" / f"SN{rec}_{token}.edf"
        labels = normalize_stage_labels(stager(edf, *choose_channels(channel_reader(edf))))
        out[f"SN{rec}"] = _stager_epochs(labels, window, epoch)
    return out


def run_m5(config_path: Path, data_root: Path, output_path: Path, stager: Any,
           channel_reader: Any = edf_labels, verify: bool = True,
           ranking_path: Path | None = None) -> dict[str, Any]:
    """M5: an independent stager scored against the manual and the assisted consensus.

    With ranking_path, also writes the exploratory ranking rows (the pre-fill's and the stager's kappa against each
    consensus, per recording) computed in the same pass; the M5 report itself is unchanged."""
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    root = Path(data_root)
    if verify:
        verify_checksums(root, config["dataset"]["checksum_file"], config["dataset"]["expected_files"])
    task = config["secondary_algorithm"]["task"]
    spec = config["tasks"][task]
    token, n_sc, epoch = spec["file_token"], int(config["n_scorers"]), config["epoch_seconds"]
    full, loo = config["consensus_majority"]["full"], config["consensus_majority"]["leave_one_out"]
    ann = root / task / "Annotations"
    recs, ranking_rows = [], []
    for rec in _recordings(root, task, token):
        auto_rows = read_annotations(ann / "auto" / f"SN{rec}_{token}_auto.txt")
        window = lights_window(auto_rows, config["window"]["start_label"], config["window"]["end_label"])
        extract = lambda rows: stage_epochs(rows, spec["labels"], spec["label_prefix"], window, epoch)
        auto = extract(auto_rows)
        scorings = {cond: [extract(read_annotations(ann / cond / f"SN{rec}_{token}_{cond}_scorer{s}.txt"))
                           for s in range(1, n_sc + 1)] for cond in ("manual", "semiauto")}
        cons = {cond: consensus_stages(scorings[cond], full) for cond in scorings}
        edf = root / task / "PSG" / f"SN{rec}_{token}.edf"
        channels = choose_channels(channel_reader(edf))
        stager_epochs = _stager_epochs(normalize_stage_labels(stager(edf, *channels)), window, epoch)
        k_manual = stage_agreement(stager_epochs, cons["manual"])
        k_semi = stage_agreement(stager_epochs, cons["semiauto"])
        k_auto_manual, k_auto_semi = stage_agreement(auto, cons["manual"]), stage_agreement(auto, cons["semiauto"])
        delta_auto = k_auto_semi - k_auto_manual
        delta_human = _mean([
            stage_agreement(scorings["manual"][s], consensus_stages([x for i, x in enumerate(scorings["semiauto"]) if i != s], loo))
            - stage_agreement(scorings["manual"][s], consensus_stages([x for i, x in enumerate(scorings["manual"]) if i != s], loo))
            for s in range(n_sc)])
        recs.append({"recording": f"SN{rec}", "channels": list(channels),
                     "kappa_stager_vs_manual_consensus": k_manual, "kappa_stager_vs_assisted_consensus": k_semi,
                     "delta_yasa": k_semi - k_manual, "delta_auto": delta_auto, "delta_human": delta_human})
        ranking_rows.append({"recording": f"SN{rec}", "prefill_vs_manual": k_auto_manual, "yasa_vs_manual": k_manual,
                             "prefill_vs_assisted": k_auto_semi, "yasa_vs_assisted": k_semi})
    report = {
        "protocol": config["protocol"], "version": config["version"], "measure": "M5",
        "stager": config["secondary_algorithm"]["name"], "task": task, "recordings": recs,
        "n_delta_yasa_positive": sum(r["delta_yasa"] > 0 for r in recs),
        "mean_delta_yasa": _mean([r["delta_yasa"] for r in recs]),
        "mean_delta_auto": _mean([r["delta_auto"] for r in recs]),
        "mean_delta_human": _mean([r["delta_human"] for r in recs]),
    }
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    if ranking_path is not None:
        ranking_path = Path(ranking_path)
        ranking_path.parent.mkdir(parents=True, exist_ok=True)
        ranking_path.write_text(json.dumps({"label": "exploratory, not pre-specified", "rows": ranking_rows}, indent=1),
                                encoding="utf-8")
    return json.loads(output_path.read_text(encoding="utf-8"))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    config = json.loads(args.config.read_text(encoding="utf-8"))
    root = os.environ.get(config["data_root_env"])
    if not root:
        print(f"Set {config['data_root_env']} to the psg-ipa/1.0.0 folder.", file=sys.stderr)
        return 2
    report = run(args.config, Path(root), args.output)
    print(json.dumps(report["primary"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
