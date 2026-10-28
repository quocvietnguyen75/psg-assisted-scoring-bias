"""Compare Hoai's event-task M1 values with the frozen protocol 001 report.

Usage: python -X utf8 -I compare_d2_events.py <report.json> <d2_verification dir>
Prints aggregate differences only.
"""
import csv
import json
import os
import sys
from collections import defaultdict

report_path, d2_dir = sys.argv[1], sys.argv[2]
report = json.load(open(report_path, encoding="utf-8"))
TASKS = {"arousals": "EEG_arousals", "respiratory": "Resp_events", "limb": "Limb_movements"}
RECS = ["SN1", "SN2", "SN3", "SN4", "SN5"]

overall = 0.0
for folder, key in TASKS.items():
    runs = sorted(os.listdir(os.path.join(d2_dir, folder, "runs")))
    run = os.path.join(d2_dir, folder, "runs", runs[-1])
    t = report["tasks"][key]
    m1 = t["M1_anchoring"]
    rec_means = dict(zip(RECS, m1["recording_means"]))
    scorer_means = m1["scorer_means"]
    print(f"== {folder} -> {key}  (runs: {runs})")
    # per-recording
    theirs = {}
    for row in csv.DictReader(open(os.path.join(run, "results_full.csv"), encoding="utf-8")):
        theirs[row["recording"]] = float(row["M1"])
    worst = 0.0
    for r in RECS:
        d = abs(theirs[r] - rec_means[r])
        worst = max(worst, d)
        print(f"   {r}: ours {rec_means[r]:+.6f}  theirs {theirs[r]:+.6f}  |diff| {d:.1e}")
    # task mean
    tm = None
    for row in csv.DictReader(open(os.path.join(run, "task_summary.csv"), encoding="utf-8")):
        tm = float(row["mean_M1"])
        print(f"   task mean: ours {m1['mean']:+.6f} theirs {tm:+.6f} |diff| {abs(tm - m1['mean']):.1e}; "
              f"positive recordings {row['positive_recordings']}/{row['recordings']}, scorers {row['scorers']}")
        worst = max(worst, abs(tm - m1["mean"]))
    # per-scorer means (mean over recordings of M1 per scorer)
    per_scorer = defaultdict(list)
    ties_m = ties_a = 0
    n_cells = 0
    for row in csv.DictReader(open(os.path.join(run, "scorer_summary.csv"), encoding="utf-8")):
        per_scorer[int(row["scorer"])].append(float(row["M1"]))
        ties_m += int(row["manual_tie_conflicts"])
        ties_a += int(row["assisted_tie_conflicts"])
        n_cells += 1
    worst_s = 0.0
    for s in range(1, 13):
        vals = per_scorer[s]
        mean_s = sum(vals) / len(vals)
        d = abs(mean_s - scorer_means[s - 1])
        worst_s = max(worst_s, d)
    print(f"   per-expert means (12): largest |diff| {worst_s:.1e}; cells {n_cells}; "
          f"tie conflicts manual {ties_m}, assisted {ties_a}")
    worst = max(worst, worst_s)
    print(f"   largest |diff| in this task: {worst:.1e}")
    overall = max(overall, worst)
print(f"LARGEST ABSOLUTE DIFFERENCE OVER ALL CHECKS: {overall:.1e}")
