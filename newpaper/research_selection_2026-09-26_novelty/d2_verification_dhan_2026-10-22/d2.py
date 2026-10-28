"""D2 staging reimplementation from protocol 001; no study-code imports."""
from __future__ import annotations

import argparse
import csv
import hashlib
from http.client import HTTPException
import json
import math
import platform
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

STAGES = ('W', 'N1', 'N2', 'N3', 'R')
BASE = 'https://physionet.org/files/psg-ipa/1.0.0/'


def fetch_bytes(url):
    """Retry transient transport errors without accepting partial responses."""
    for attempt in range(4):
        try:
            with urlopen(url, timeout=60) as response:
                return response.read()
        except (OSError, HTTPException):
            if attempt == 3:
                raise
            time.sleep(attempt + 1)


def filenames():
    for r in range(1, 6):
        yield f'Sleep_stages/Annotations/auto/SN{r}_SleepStages_auto.txt'
        for setting in ('manual', 'semiauto'):
            for s in range(1, 13):
                yield f'Sleep_stages/Annotations/{setting}/SN{r}_SleepStages_{setting}_scorer{s}.txt'


def download(root: Path):
    """Fetch only required annotations, validating each against upstream SHA256SUMS."""
    root.mkdir(parents=True, exist_ok=True)
    manifest = fetch_bytes(BASE + 'SHA256SUMS.txt')
    expected = {}
    for line in manifest.decode().splitlines():
        digest, name = line.split(maxsplit=1)
        expected[name.lstrip('*').removeprefix('./')] = digest

    def fetch(name):
        target = root / name
        digest = expected[name]
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == digest:
            return
        content = fetch_bytes(BASE + name)
        if hashlib.sha256(content).hexdigest() != digest:
            raise ValueError(f'Checksum mismatch: {name}')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(fetch, filenames()))
    (root / 'SHA256SUMS.txt').write_bytes(manifest)
    print('Downloaded and SHA-256 verified all 125 required annotation files.')


def read_annotations(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        rows = csv.DictReader(stream, skipinitialspace=True)
        if not {'Recording onset', 'Duration', 'Annotation'} <= set(rows.fieldnames or []):
            raise ValueError(f'Unexpected annotation header: {path}')
        return [(float(row['Recording onset']), float(row['Duration']),
                 row['Annotation'].strip()) for row in rows]


def lights_window(rows):
    off = [t for t, _, label in rows if label.casefold() == 'lights off']
    on = [t for t, _, label in rows if label.casefold() == 'lights on']
    if len(off) != 1 or len(on) != 1 or off[0] >= on[0]:
        raise ValueError('Expected exactly one ordered lights-off/on pair.')
    return off[0], on[0]


def epoch_labels(rows, epochs):
    """Project stage intervals onto recording-aligned epoch midpoints.

    Annotation intervals are half-open. Unknown stage labels remain unscored.
    Other-task/context annotations are ignored. Overlapping stage intervals fail.
    """
    intervals = sorted((t, t + duration, label.removeprefix('Sleep stage '))
                       for t, duration, label in rows if label.startswith('Sleep stage '))
    previous_end = -math.inf
    for start, end, _ in intervals:
        if end <= start or start < previous_end - 1e-7:
            raise ValueError('Invalid or overlapping stage intervals.')
        previous_end = end
    result = []
    index = 0
    for epoch in epochs:
        midpoint = epoch * 30 + 15
        while index < len(intervals) and intervals[index][1] <= midpoint:
            index += 1
        label = None
        if index < len(intervals):
            start, end, candidate = intervals[index]
            if start <= midpoint < end and candidate in STAGES:
                label = candidate
        result.append(label)
    return result


def kappa(left, right):
    if len(left) != len(right):
        raise ValueError('Pairwise sequences must have equal length.')
    pairs = [(a, b) for a, b in zip(left, right) if a in STAGES and b in STAGES]
    n = len(pairs)
    if not n:
        raise ValueError('No jointly scored epochs for kappa.')
    observed = sum(a == b for a, b in pairs) / n
    expected = sum(sum(a == label for a, _ in pairs) *
                   sum(b == label for _, b in pairs) for label in STAGES) / n**2
    if math.isclose(expected, 1.0, abs_tol=1e-15):
        raise ValueError('Kappa undefined: expected agreement equals one.')
    return (observed - expected) / (1 - expected)


def consensus(scorings, threshold):
    if not scorings or len({len(row) for row in scorings}) != 1:
        raise ValueError('Consensus requires nonempty equal-length scorings.')
    if threshold <= len(scorings) / 2:
        raise ValueError('This implementation requires a strict majority threshold.')
    output = []
    for votes in zip(*scorings):
        output.append(next((label for label in STAGES if votes.count(label) >= threshold), None))
    return output


def measures(auto, manual, assisted):
    if len(manual) != 12 or len(assisted) != 12:
        raise ValueError('Exactly 12 matched scorers are required.')
    cm, cs = consensus(manual, 7), consensus(assisted, 7)
    per_scorer = []
    for s in range(12):
        m_other = consensus(manual[:s] + manual[s + 1:], 6)
        s_other = consensus(assisted[:s] + assisted[s + 1:], 6)
        per_scorer.append({
            'scorer': s + 1,
            'M1': kappa(assisted[s], auto) - kappa(manual[s], auto),
            'delta_human': kappa(manual[s], s_other) - kappa(manual[s], m_other),
        })
    m1 = sum(row['M1'] for row in per_scorer) / 12
    da = kappa(auto, cs) - kappa(auto, cm)
    dh = sum(row['delta_human'] for row in per_scorer) / 12
    return {'M1': m1, 'delta_auto': da, 'delta_human': dh, 'DiD': da - dh}, per_scorer, cm, cs


def analyze(root: Path, output: Path):
    # Never overwrite a previous run: retain outputs if a later correction is needed.
    if output.exists():
        raise FileExistsError(f'Choose a new output folder; already exists: {output}')
    manifest = {}
    for line in (root / 'SHA256SUMS.txt').read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        manifest[name.lstrip('*').removeprefix('./')] = digest
    hashes = {}
    for name in filenames():
        digest = hashlib.sha256((root / name).read_bytes()).hexdigest()
        if digest != manifest[name]:
            raise ValueError(f'Input checksum mismatch: {name}')
        hashes[name] = digest
    results, details, quality = [], [], []
    for r in range(1, 6):
        record = f'SN{r}'
        base = root / 'Sleep_stages' / 'Annotations'
        auto_rows = read_annotations(base / 'auto' / f'{record}_SleepStages_auto.txt')
        off, on = lights_window(auto_rows)
        # Half-open lights window; explicitly record this boundary convention.
        epochs = [i for i in range(max(0, math.ceil(on / 30))) if off <= 30 * i + 15 < on]
        auto = epoch_labels(auto_rows, epochs)
        conditions = {}
        for setting in ('manual', 'semiauto'):
            conditions[setting] = [epoch_labels(read_annotations(
                base / setting / f'{record}_SleepStages_{setting}_scorer{s}.txt'), epochs)
                for s in range(1, 13)]
        stats, scorers, cm, cs = measures(auto, conditions['manual'], conditions['semiauto'])
        results.append({'recording': record, **stats})
        details.extend({'recording': record, **row} for row in scorers)
        quality.append({'recording': record, 'lights_off': off, 'lights_on': on,
                        'epochs_in_window': len(epochs), 'auto_unscored': auto.count(None),
                        'manual_unscored_per_scorer': [x.count(None) for x in conditions['manual']],
                        'assisted_unscored_per_scorer': [x.count(None) for x in conditions['semiauto']],
                        'manual_consensus_epochs': len(cm) - cm.count(None),
                        'assisted_consensus_epochs': len(cs) - cs.count(None),
                        'midpoints_exactly_on_boundary': sum(30*i+15 in (off,on) for i in range(math.ceil(on/30)+1))})
    output.mkdir(parents=True)
    for filename, rows, rounded in [('results_full.csv', results, False),
                                    ('results_3dp.csv', results, True),
                                    ('scorer_summary.csv', details, False)]:
        with (output / filename).open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            for row in rows:
                writer.writerow({key: f'{value:.3f}' if rounded and isinstance(value, float) else value
                                 for key, value in row.items()})
    metadata = {'created_utc': datetime.now(timezone.utc).isoformat(),
                'python': platform.python_version(), 'dataset': 'PSG-IPA 1.0.0',
                'source': BASE, 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'protocol_pdf_sha256': hashlib.sha256((Path(__file__).resolve().parents[1] /
                    'submission/supplementary_file_S1_analysis_plans.pdf').read_bytes()).hexdigest(),
                'window_convention': 'lights_off <= epoch midpoint < lights_on',
                'quality': quality, 'input_sha256': hashes,
                'disclosure': 'AI-assisted reimplementation. Assistant previously viewed manuscript results; '
                              'not a blind human-only verification. No original analysis code read or imported.'}
    (output / 'provenance.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print(f'Analysis complete: {output / "results_3dp.csv"}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['download', 'analyze'])
    parser.add_argument('--data-root', type=Path, default=Path(__file__).parent / 'data' / 'psg-ipa' / '1.0.0')
    parser.add_argument('--output', type=Path, default=Path(__file__).parent / 'runs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    args = parser.parse_args()
    if args.command == 'download':
        download(args.data_root)
    else:
        analyze(args.data_root, args.output)


if __name__ == '__main__':
    main()
