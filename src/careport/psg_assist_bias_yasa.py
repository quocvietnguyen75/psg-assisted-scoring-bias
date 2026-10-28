"""M5 runner: YASA sleep staging as an independent rater (protocol 001).

Needs the isolated YASA environment (outputs/envs/yasa); the main analysis
module stays standard-library only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Sequence

from careport.psg_assist_bias import run_m5, stager_labels


def yasa_stager(edf_path: Path, eeg: str, eog: str, emg: str) -> list[str]:
    import mne
    import yasa

    raw = mne.io.read_raw_edf(str(edf_path), include=[eeg, eog, emg], preload=True, verbose="ERROR")
    hypno = yasa.SleepStaging(raw, eeg_name=eeg, eog_name=eog, emg_name=emg).predict()
    return list(hypno.hypno) if hasattr(hypno, "hypno") else list(hypno)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache", action="store_true",
                        help="write YASA's per-epoch labels (kept out of Git) instead of running M5")
    parser.add_argument("--ranking", type=Path,
                        help="also write the exploratory ranking rows (pre-fill and YASA kappas per recording)")
    args = parser.parse_args(argv)
    env = json.loads(args.config.read_text(encoding="utf-8"))["data_root_env"]
    root = os.environ.get(env)
    if not root:
        print(f"Set {env} to the psg-ipa/1.0.0 folder.", file=sys.stderr)
        return 2
    if args.cache:
        labels = stager_labels(args.config, Path(root), yasa_stager)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(labels) + "\n", encoding="utf-8")
        print({rec: len(v) for rec, v in labels.items()})
        return 0
    report = run_m5(args.config, Path(root), args.output, stager=yasa_stager, ranking_path=args.ranking)
    print(json.dumps({k: v for k, v in report.items() if k != "recordings"}, indent=1))
    for rec in report["recordings"]:
        print(rec["recording"], rec["channels"][0], {k: round(v, 3) for k, v in rec.items() if isinstance(v, float)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
