"""C5 runner (amendment 005): GSSC sleep staging as a second independent stager, labels only.

Needs the isolated GSSC environment (outputs/envs/gssc: gssc 0.0.9, torch 2.5.1 on the CPU, MNE); the
main analysis modules stay standard-library only. The channels are the M5 rule's EEG and EOG
(careport.psg_assist_bias.choose_channels), and the epochs follow the M5 window rule.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Iterable, Sequence

from careport.psg_assist_bias import stager_labels

GSSC_STAGES = {0: "W", 1: "N1", 2: "N2", 3: "N3", 4: "R"}


def gssc_stage_names(codes: Iterable[int]) -> list[str | None]:
    """GSSC's integer output (0 Wake, 1 N1, 2 N2, 3 N3, 4 REM) as the study's labels; anything else is unscored."""
    return [GSSC_STAGES.get(int(c)) for c in codes]


def gssc_stager(edf_path: Path, eeg: str, eog: str, emg: str) -> list[str | None]:
    """One label per 30-second epoch from the start of the recording (GSSC's own epoching, cut='back')."""
    import mne
    from gssc.infer import EEGInfer

    raw = mne.io.read_raw_edf(str(edf_path), include=[eeg, eog], preload=True, verbose="ERROR")
    stages, times = EEGInfer(use_cuda=False).mne_infer(raw, eeg=[eeg], eog=[eog], eeg_drop=True, eog_drop=True,
                                                       filter=True)
    if len(times) and float(times[0]) != 0.0:
        raise ValueError(f"GSSC epochs start at {times[0]} s, not at the recording start")
    return gssc_stage_names(stages)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", type=Path, required=True, help="protocol 001 config")
    parser.add_argument("--output", type=Path, required=True, help="per-epoch labels (kept out of Git)")
    args = parser.parse_args(argv)
    env = json.loads(args.config.read_text(encoding="utf-8"))["data_root_env"]
    root = os.environ.get(env)
    if not root:
        print(f"Set {env} to the psg-ipa/1.0.0 folder.", file=sys.stderr)
        return 2
    labels = stager_labels(args.config, Path(root), gssc_stager)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(labels) + "\n", encoding="utf-8")
    print({rec: len(v) for rec, v in labels.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
